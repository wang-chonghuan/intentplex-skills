#!/usr/bin/env python3
"""
Release one commit across every deployable service on Render, then prove it.

    export RENDER_API_KEY=...            # or: eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
    python3 release.py                   # release HEAD
    python3 release.py --commit <sha>
    python3 release.py --dry-run         # show what would be deployed, touch nothing
    python3 release.py --only trovestep  # restrict to services whose name contains this

Exits non-zero unless **every** targeted service ends up `live` on the target
commit. That exit code is the whole point: the failure this guards against is a
release where ten services updated and one did not, which no human verifies
exhaustively by hand and which looks exactly like success.

## Why this asks the platform instead of being told

Nothing here knows what the project is made of. It does not know how many
services there are, which are cron jobs, or that a web service exists at all.
Everything is derived from the API at the moment of acting, so adding a
background worker or a second web service changes nothing in this file.

That is deliberate, and it comes from a real failure: an earlier version of the
release procedure carried a hardcoded list of service types, and anything not on
that list would have been skipped in silence.

## The Render facts this encodes

Three, all observed rather than assumed, all of which produce a *silent partial
release* if you get them wrong:

1. **Datastores appear in the services listing and have no `type` field.** A
   Postgres entry deserializes as `{'environment', 'postgres', 'project'}`.
   Indexing `['type']` raises mid-iteration, truncating the list rather than
   failing loudly — and the datastore can sort ahead of the service you care
   about. Here, having a `type` *is* the definition of deployable.
2. **Cron jobs reject a commit reference.** `POST /deploys` with `commitId`
   answers `400 … cannot deploy cron job service … by commit reference ID`.
   Rather than hardcode which types accept it, this tries with the commit and
   retries without on that specific rejection.
3. **A service that cannot be pinned deploys its branch head.** So pinning is
   only meaningful if the branch head already *is* the target commit. This
   refuses to run otherwise, because a release that pins one service to a commit
   while the rest take a different branch head is not a release.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
POLL_SECONDS = 20
# Generous: the browser image in a project like this takes many minutes to build,
# and a release that gives up early reports a failure that did not happen.
POLL_TIMEOUT_SECONDS = 45 * 60

TERMINAL_OK = {"live"}
TERMINAL_BAD = {"build_failed", "update_failed", "canceled", "deactivated", "pre_deploy_failed"}


def api(path: str, method: str = "GET", body: dict | None = None) -> tuple[int, object]:
    key = os.environ.get("RENDER_API_KEY")
    if not key:
        sys.exit('RENDER_API_KEY is not set. eval "$(grep \'^export RENDER_API_KEY\' ~/.zshrc)"')
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if data else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            raw = res.read().decode().strip()
            return res.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as err:
        raw = err.read().decode().strip()
        try:
            return err.code, json.loads(raw)
        except json.JSONDecodeError:
            return err.code, raw


def deployable_services(only: str | None) -> list[dict]:
    """Every service the key can see that is a service rather than a datastore.

    An allowlist of types is what this deliberately does not do — see the module
    docstring. Having a `type` is the test.
    """
    out: list[dict] = []
    cursor = None
    while True:
        path = "/services?limit=100" + (f"&cursor={cursor}" if cursor else "")
        status, body = api(path)
        if status != 200 or not isinstance(body, list) or not body:
            break
        for item in body:
            svc = item.get("service", item) if isinstance(item, dict) else {}
            if not svc.get("type"):
                continue  # datastore
            if only and only not in svc.get("name", ""):
                continue
            out.append(svc)
        cursor = body[-1].get("cursor") if isinstance(body[-1], dict) else None
        if not cursor:
            break
    return sorted(out, key=lambda s: s["name"])


def git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def check_branch_head(services: list[dict], sha: str) -> None:
    """Refuse when the target commit is not what the tracked branches point at.

    Services that cannot be pinned to a commit deploy their branch head. If that
    head is not `sha`, this run would put two different commits into production
    and call it one release.
    """
    branches = {s.get("branch") for s in services if s.get("branch")}
    for branch in sorted(b for b in branches if b):
        head = git("rev-parse", f"origin/{branch}")
        if head is None:
            print(f"! cannot read origin/{branch} locally — skipping the branch-head check")
            continue
        if head != sha:
            sys.exit(
                f"Refusing: origin/{branch} is at {head[:7]}, not {sha[:7]}.\n"
                "Services that cannot be pinned deploy the branch head, so this would\n"
                "release two different commits. Push or pick the right commit first."
            )


def trigger(service: dict, sha: str) -> tuple[bool, str]:
    """Deploy one service, pinning to the commit where the platform allows it."""
    sid = service["id"]
    status, body = api(f"/services/{sid}/deploys", "POST", {"commitId": sha})
    if status in (200, 201, 202):
        return True, "pinned"

    text = json.dumps(body) if not isinstance(body, str) else body
    if status == 400 and "commit reference" in text:
        # Cron jobs, and anything else Render will not pin: take the branch head,
        # which check_branch_head has already proven equals the target.
        status, body = api(f"/services/{sid}/deploys", "POST", {})
        if status in (200, 201, 202):
            return True, "branch head"
        return False, f"HTTP {status} {body}"
    return False, f"HTTP {status} {text[:160]}"


def latest_deploy(sid: str) -> tuple[str, str]:
    status, body = api(f"/services/{sid}/deploys?limit=1")
    if status != 200 or not isinstance(body, list) or not body:
        return "unknown", "-"
    dep = body[0].get("deploy", body[0])
    commit = (dep.get("commit") or {}).get("id", "-")
    return dep.get("status", "unknown"), commit[:7]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--commit", help="commit to release (default: git HEAD)")
    ap.add_argument("--only", help="restrict to services whose name contains this")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sha = args.commit or git("rev-parse", "HEAD")
    if not sha:
        sys.exit("No --commit given and this is not a git checkout.")

    services = deployable_services(args.only)
    if not services:
        sys.exit("No deployable services found. Wrong workspace, or --only matched nothing.")

    print(f"Releasing {sha[:7]} to {len(services)} service(s):")
    for s in services:
        print(f"  {s['name']:<30} {s['type']}")

    if args.dry_run:
        print("\n--dry-run: nothing was triggered.")
        return 0

    check_branch_head(services, sha)

    print()
    failures = []
    for s in services:
        ok, how = trigger(s, sha)
        print(f"  {'->' if ok else 'XX'} {s['name']:<30} {how}")
        if not ok:
            failures.append(s["name"])

    print("\nPolling until every service is live on the target commit.")
    deadline = time.time() + POLL_TIMEOUT_SECONDS
    target = sha[:7]
    while True:
        rows = [(s["name"], *latest_deploy(s["id"])) for s in services]
        done = [r for r in rows if r[1] in TERMINAL_OK and r[2] == target]
        stuck = [r for r in rows if r[1] in TERMINAL_BAD]
        print(f"  {time.strftime('%H:%M:%S')}  on target: {len(done)}/{len(rows)}", flush=True)
        if len(done) == len(rows) or stuck or time.time() > deadline:
            break
        time.sleep(POLL_SECONDS)

    print()
    bad = []
    for name, status, commit in rows:
        mark = "ok  " if (status in TERMINAL_OK and commit == target) else "FAIL"
        if mark == "FAIL":
            bad.append(name)
        print(f"  {mark} {name:<30} {status:<14} {commit}")

    if failures:
        print(f"\nNot triggered: {', '.join(failures)}")
    if bad:
        print(f"\nFAIL: {len(bad)} service(s) are not live on {target}: {', '.join(bad)}")
        return 1
    print(f"\nOK: all {len(rows)} services live on {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
