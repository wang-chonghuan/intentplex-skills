#!/usr/bin/env python3
"""Sync explicitly named keys from an ignored env file to a Render env group."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.render.com/v1"


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            sys.exit(f"{path}:{number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def require_ignored(path: Path) -> None:
    repo = subprocess.run(
        ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if repo.returncode != 0:
        sys.exit(f"{path}: not inside a Git repository")
    root = Path(repo.stdout.strip())
    ignored = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "--quiet", str(path)],
    )
    if ignored.returncode != 0:
        sys.exit(f"{path}: refusing because the env file is not Git-ignored")


def request(
    api_key: str,
    path: str,
    method: str = "GET",
    body: dict[str, str] | None = None,
) -> tuple[int, object | None]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if data else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode().strip()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        error.read()
        return error.code, None


def listed_keys(body: object | None) -> set[str]:
    if not isinstance(body, dict):
        return set()
    rows = body.get("envVars", body.get("env_vars", []))
    if not isinstance(rows, list):
        return set()
    keys: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = row.get("envVar", row)
        if isinstance(value, dict) and isinstance(value.get("key"), str):
            keys.add(value["key"])
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-group", required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--key", action="append", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("RENDER_API_KEY")
    if not api_key:
        sys.exit("RENDER_API_KEY is not set")

    env_file = args.env_file.expanduser().resolve()
    if not env_file.is_file():
        sys.exit(f"{env_file}: file not found")
    require_ignored(env_file)

    keys = list(dict.fromkeys(args.key))
    values = parse_env(env_file)
    missing = [key for key in keys if not values.get(key)]
    if missing:
        sys.exit(f"missing or empty in {env_file}: {', '.join(missing)}")

    action = "would sync" if not args.apply else "syncing"
    print(f"{action} {len(keys)} named key(s) to env group {args.env_group}:")
    for key in keys:
        print(f"  {key}")
    if not args.apply:
        print("dry-run: no Render values changed")
        return 0

    failed: list[str] = []
    for key in keys:
        escaped = urllib.parse.quote(key, safe="")
        status, _ = request(
            api_key,
            f"/env-groups/{args.env_group}/env-vars/{escaped}",
            "PUT",
            {"value": values[key]},
        )
        if status not in (200, 201, 204):
            failed.append(f"{key} (HTTP {status})")

    status, body = request(api_key, f"/env-groups/{args.env_group}")
    if status != 200:
        failed.append(f"verification (HTTP {status})")
    else:
        present = listed_keys(body)
        failed.extend(f"{key} (not listed after update)" for key in keys if key not in present)

    if failed:
        print("failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    print(f"verified {len(keys)} key name(s); values were not printed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
