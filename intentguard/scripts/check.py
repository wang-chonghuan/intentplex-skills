#!/usr/bin/env python3
"""Validate a behavior catalog and reconcile native Playwright JSON evidence."""

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise Invalid(f"Non-JSON constant: {value}")


def decode_json(raw):
    return json.loads(
        raw, object_pairs_hook=unique_object, parse_constant=invalid_constant
    )


def read_json(path):
    return decode_json(path.read_text(encoding="utf-8"))


def timestamp(value):
    require(text(value), "Expected an ISO-8601 timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Invalid("Invalid ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None, "Timestamp must include its timezone")
    return parsed


def collection(obj, key, where, optional=False):
    value = obj.get(key, [] if optional else None)
    require(isinstance(value, list), f"{where}.{key} must be an array")
    return value


ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+")
ASSERTION = re.compile(r"A[1-9][0-9]*")
THEN_STEP = re.compile(r"Then (A[1-9][0-9]*)")
SPEC = re.compile(r"case\.spec\.(?:[cm]?[jt]s|[jt]sx)")
ROOT = ".intentgurad"


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def read_case(case, index):
    where = f"e2e.json cases[{index}]"
    keys = {"id", "title", "cuj", "surface", "status", "source", "approval",
            "given", "when", "then", "data"}
    require(isinstance(case, dict) and
            keys <= set(case) <= keys | {"limitations"},
            f"{where}: missing or unsupported case fields")
    for key in ("id", "cuj"):
        require(text(case[key]) and ID.fullmatch(case[key]),
                f"{where}: invalid {key}")
    require(case["status"] in ("draft", "active", "retired"),
            f"{where}: invalid status")
    require(case["surface"] in ("web", "public-api", "public-mcp"),
            f"{where}: surface must be web, public-api, or public-mcp")
    for key in ("title", "source"):
        require(text(case[key]), f"{where}: {key} is required")
    require(case["approval"] is None or text(case["approval"]),
            f"{where}: approval must be null or a nonempty reference")
    require(case["status"] == "draft" or text(case["approval"]),
            f"{where}: {case['status']} case needs actual approval")
    for key in ("given", "when"):
        values = collection(case, key, where)
        require(values and all(text(value) for value in values),
                f"{where}: {key} needs nonempty statements")
    assertions = []
    for item in collection(case, "then", where):
        require(isinstance(item, dict) and set(item) == {"id", "expect"},
                f"{where}: each Then needs id and expect")
        require(text(item["id"]) and ASSERTION.fullmatch(item["id"]) and
                text(item["expect"]), f"{where}: invalid Then ID or expectation")
        assertions.append(item["id"])
    require(assertions and len(assertions) == len(set(assertions)),
            f"{where}: missing or duplicate assertion IDs")
    data = case["data"]
    require(isinstance(data, dict) and set(data) == {"setup", "cleanup"} and
            all(text(value) for value in data.values()),
            f"{where}: data needs setup and cleanup descriptions")
    limitations = collection(case, "limitations", where, optional=True)
    require(all(text(value) for value in limitations),
            f"{where}: limitations must be nonempty descriptions")
    return {
        **{key: case[key] for key in (
            "id", "title", "cuj", "surface", "status", "source", "approval"
        )},
        "assertions": assertions,
        "limitations": limitations,
        "digest": digest(case),
    }


def catalog(root):
    suite = read_json(root / "e2e.json")
    keys = {"version", "playwright_config", "projects", "approval", "cases"}
    require(isinstance(suite, dict) and set(suite) == keys,
            "e2e.json: unexpected or missing fields")
    require(type(suite["version"]) is int and suite["version"] == 1,
            "e2e.json: unsupported version")
    config = suite["playwright_config"]
    require(text(config) and not Path(config).is_absolute() and
            ".." not in Path(config).parts and "\\" not in config and ":" not in config,
            "e2e.json: playwright_config must be a path inside .intentgurad")
    projects = suite["projects"]
    require(isinstance(projects, list) and projects and all(text(p) for p in projects),
            "e2e.json: projects must be a nonempty list of names")
    require(len(projects) == len(set(projects)), "e2e.json: duplicate project names")
    require(suite["approval"] is None or text(suite["approval"]),
            "e2e.json: approval must be null or a nonempty reference")
    definitions = collection(suite, "cases", "e2e.json")
    require(definitions, "Empty catalog: e2e.json has no cases")
    cases = [read_case(case, index) for index, case in enumerate(definitions)]
    ids = [case["id"] for case in cases]
    require(len(ids) == len(set(ids)), "Duplicate case IDs across the catalog")
    counts = Counter(case["status"] for case in cases)
    blockers = []
    if not text(suite["approval"]):
        blockers.append("Execution scope is not approved")
    if not counts["active"]:
        blockers.append("No active approved cases")
    if counts["draft"]:
        blockers.append(f"{counts['draft']} candidate cases are still drafts")
    return suite, cases, {
        "ok": True,
        "ready": not blockers,
        "blockers": blockers,
        "catalog_digest": digest(suite),
        "counts": {state: counts[state] for state in ("draft", "active", "retired")},
        "projects": projects,
        "cases": cases,
    }


def source_layout(root, suite, cases):
    paths = sorted(root.rglob("*"))
    require(not any(path.is_symlink() for path in paths),
            ".intentgurad must contain real source files, not symlinks")
    config = root / suite["playwright_config"]
    require(config.is_file(), "The configured Playwright source file is missing")
    require((root / "tests").is_dir(), "Missing tests/<case-id>/ directories")
    known = {case["id"]: case for case in cases}
    for entry in (root / "tests").iterdir():
        require(entry.is_dir() and entry.name in known,
                f"Unexpected entry under tests/: {entry.name}")
    specs = {}
    for case in cases:
        folder = root / "tests" / case["id"]
        found = [path for path in folder.glob("case.spec.*") if path.is_file()]
        if case["status"] == "active":
            require(len(found) == 1 and SPEC.fullmatch(found[0].name),
                    f"{case['id']}: expected one tests/{case['id']}/case.spec.*")
            specs[case["id"]] = found[0].resolve()
        else:
            require(not found, f"{case['id']}: inactive case still has an executable spec")
    return [path for path in paths if path.is_file()], specs


def git(root, *args, input_text=None, allowed=(0,)):
    result = subprocess.run(
        ["git", "-C", str(root), *args], input=input_text,
        capture_output=True, text=True,
    )
    require(result.returncode in allowed,
            f"Git check failed: {result.stderr.strip() or 'no repository/commit'}")
    return result.stdout


def check_sources(root, suite, cases):
    files, _ = source_layout(root, suite, cases)
    repo = Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve()
    require(root == repo / ROOT, "Harness must be at <repo-root>/.intentgurad")
    relative = [str(path.relative_to(repo)) for path in files]
    # --no-index also catches ignore rules hidden by a previous forced git add.
    ignored = git(repo, "check-ignore", "--no-index", "-z", "--stdin",
                  input_text="\0".join([ROOT + "/", *relative]) + "\0",
                  allowed=(0, 1)).strip("\0").split("\0")
    errors = [f"Ignored source: {path}" for path in ignored if path]
    commit = git(repo, "rev-parse", "--verify", "HEAD").strip()
    committed = set(git(repo, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--",
                        ROOT).strip("\0").split("\0"))
    for path in sorted(set(relative) - committed):
        errors.append(f"Not committed: {path}")
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--", ROOT)
    if status:
        errors.append("Harness has pending changes relative to HEAD")
    flags = git(repo, "ls-files", "-v", "-z", "--", ROOT).strip("\0").split("\0")
    if any(line and (line[0].islower() or line[0] == "S") for line in flags):
        errors.append("Harness uses assume-unchanged or skip-worktree flags")
    return {
        "ok": not errors, "committed": not errors, "commit": commit,
        "files": len(files), "errors": errors,
        "pending_changes": status.splitlines(),
    }


def report_tests(suites):
    for suite in suites:
        require(isinstance(suite, dict), "Report suite must be an object")
        for spec in collection(suite, "specs", "suite"):
            require(isinstance(spec, dict), "Report spec must be an object")
            tests = collection(spec, "tests", "spec")
            require(tests, "Report spec has no tests")
            for test in tests:
                require(isinstance(test, dict), "Report test must be an object")
                yield spec, test
        yield from report_tests(collection(suite, "suites", "suite", optional=True))


def report_steps(steps):
    for step in steps:
        require(isinstance(step, dict) and text(step.get("title")),
                "Report step must have a title")
        yield step
        yield from report_steps(collection(step, "steps", "step", optional=True))


def annotation(test, kind):
    values = [a.get("description") for a in collection(test, "annotations", "test")
              if isinstance(a, dict) and a.get("type") == kind]
    require(len(values) == 1 and text(values[0]),
            f"Test requires exactly one static {kind} annotation")
    return values[0]


def check_report(root, suite, cases, summary, args):
    _, specs = source_layout(root, suite, cases)
    report_path = Path(args.report).resolve()
    require(not report_path.is_relative_to(root.parent),
            "Runtime report must be outside the target repository")
    report = read_json(report_path)
    require(isinstance(report, dict), "Playwright report must be an object")
    errors = list(summary["blockers"])
    if args.exit_code != 0:
        errors.append(f"Playwright runner exited {args.exit_code}")
    config = report.get("config")
    require(isinstance(config, dict), "Report.config is required")
    report_root = config.get("rootDir")
    require(text(report_root) and Path(report_root).is_absolute(),
            "Report.config.rootDir must be absolute")
    report_config = config.get("configFile")
    require(text(report_config), "Report.config.configFile is required")
    if Path(report_config).resolve() != (root / suite["playwright_config"]).resolve():
        errors.append("Report uses a different Playwright config")
    if config.get("forbidOnly") is not True:
        errors.append("Full run did not enforce forbidOnly")
    if config.get("shard") is not None:
        errors.append("A shard is not a full-suite run")
    configured = collection(config, "projects", "config")
    names = []
    for project in configured:
        require(isinstance(project, dict) and text(project.get("name")),
                "Report project requires a name")
        names.append(project["name"])
        output_dir = project.get("outputDir")
        if (not text(output_dir) or not Path(output_dir).is_absolute() or
                Path(output_dir).resolve().is_relative_to(root.parent)):
            errors.append(f"{project['name']}: outputDir must be outside the repository")
        if (type(project.get("repeatEach")) is not int or project["repeatEach"] != 1 or
                type(project.get("retries")) is not int or project["retries"] != 0):
            errors.append(f"{project['name']}: repeatEach must be 1 and retries 0")
    if Counter(names) != Counter(suite["projects"]):
        errors.append("Report project matrix differs from the approved matrix")
    if collection(report, "errors", "report"):
        errors.append("Playwright reported global errors")
    stats = report.get("stats")
    require(isinstance(stats, dict), "Report.stats is required")
    cutoff = timestamp(args.started_after)
    started = timestamp(stats.get("startTime"))
    if started < cutoff:
        errors.append("Report predates this invocation")
    if started > datetime.now(timezone.utc) + timedelta(seconds=5):
        errors.append("Report start time is in the future")
    outcomes = ("expected", "unexpected", "skipped", "flaky")
    for key in outcomes:
        require(type(stats.get(key)) is int and stats[key] >= 0,
                f"Report.stats.{key} must be a nonnegative integer")
    if any(stats[key] for key in ("unexpected", "skipped", "flaky")):
        errors.append("Run contains failed, skipped, or flaky tests")
    tests = list(report_tests(collection(report, "suites", "report")))
    actual_outcomes = Counter()
    by_id = {case["id"]: case for case in cases}
    active = [case for case in cases if case["status"] == "active"]
    expected = {(case["id"], project) for case in active for project in suite["projects"]}
    seen = Counter()
    rows = []
    for index, (spec, test) in enumerate(tests):
        issues = []
        require(test.get("status") in outcomes, "Invalid test outcome")
        actual_outcomes[test["status"]] += 1
        try:
            case_id = annotation(test, "intentguard.case")
            case_digest = annotation(test, "intentguard.digest")
        except Invalid as exc:
            errors.append(f"Test #{index + 1}: {exc}")
            continue
        project = test.get("projectName")
        require(text(project), f"{case_id}: test projectName is missing")
        pair = (case_id, project)
        seen[pair] += 1
        case = by_id.get(case_id)
        if pair not in expected:
            issues.append("Case/project is outside the active approved catalog")
        file = spec.get("file")
        if (not text(file) or
                (Path(report_root) / file).resolve() != specs.get(case_id)):
            issues.append("Test is not implemented in its own case directory")
        if case and case_digest != case["digest"]:
            issues.append("Test implements an older/different case digest")
        if test.get("expectedStatus") != "passed" or test["status"] != "expected":
            issues.append("Test did not pass as an ordinary expected-success test")
        results = collection(test, "results", "test")
        if len(results) != 1:
            issues.append("Expected exactly one executed attempt, without retries")
        for result in results:
            require(isinstance(result, dict), "Report result must be an object")
            if (result.get("status") != "passed" or
                    type(result.get("retry")) is not int or result["retry"] != 0):
                issues.append("Attempt failed, skipped, interrupted, or retried")
            worker = result.get("workerIndex")
            if type(worker) is not int or worker < 0:
                issues.append("Attempt has no executed worker")
            if result.get("error") is not None or collection(result, "errors", "result"):
                issues.append("Attempt contains assertion, fixture, or cleanup errors")
            if timestamp(result.get("startTime")) < started:
                issues.append("Attempt predates the reported run")
            steps = list(report_steps(collection(result, "steps", "result", optional=True)))
            if any(step.get("error") is not None for step in steps):
                issues.append("A step contains an error")
            assertion_steps = Counter()
            for step in steps:
                match = THEN_STEP.fullmatch(step["title"])
                if match:
                    assertion_steps[match[1]] += 1
            if case and assertion_steps != Counter(case["assertions"]):
                issues.append("Then steps are missing, duplicated, or outside the case")
        rows.append({
            "id": case_id, "project": project,
            "outcome": test["status"], "passed": not issues, "issues": issues,
            "limitations": case["limitations"] if case else [],
        })
        errors.extend(f"{case_id}/{project}: {issue}" for issue in issues)
    for pair in sorted(expected - set(seen)):
        case_id, project = pair
        errors.append(f"{case_id}/{project}: missing execution")
        rows.append({"id": case_id, "project": project,
                     "outcome": "missing", "passed": False, "issues": ["Not executed"]})
    for (case_id, project), count in sorted(seen.items()):
        if count != 1:
            errors.append(f"{case_id}/{project}: {count} executions instead of one")
            for row in rows:
                if row["id"] == case_id and row["project"] == project:
                    row["passed"] = False
                    row["issues"].append("Duplicate execution")
    for key in outcomes:
        if stats[key] != actual_outcomes[key]:
            errors.append(f"Report.stats.{key} does not match actual test records")
    if len(tests) != len(expected):
        errors.append(f"Expected {len(expected)} case/project tests, received {len(tests)}")
    return {
        "ok": not errors,
        "complete": not errors,
        "catalog_digest": summary["catalog_digest"],
        "projects": suite["projects"],
        "expected": len(expected),
        "recorded": len(tests),
        "passed": sum(row["passed"] for row in rows),
        "errors": errors,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("catalog", help="Validate and summarize cases")
    inspect.add_argument("--root", default=ROOT)
    sources = commands.add_parser("sources", help="Require committed, unignored harness sources")
    sources.add_argument("--root", default=ROOT)
    verify = commands.add_parser("report", help="Check a fresh full Playwright JSON report")
    verify.add_argument("--root", default=ROOT)
    verify.add_argument("--report", required=True)
    verify.add_argument("--started-after", required=True)
    verify.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()
    try:
        require(not Path(args.root).is_symlink(), "Harness root cannot be a symlink")
        root = Path(args.root).resolve()
        suite, cases, summary = catalog(root)
        if args.command == "catalog":
            result = summary
        elif args.command == "sources":
            result = check_sources(root, suite, cases)
        else:
            result = check_report(root, suite, cases, summary, args)
    except (Invalid, OSError, ValueError, TypeError, RecursionError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
