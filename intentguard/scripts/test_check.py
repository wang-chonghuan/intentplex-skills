"""Regression tests for the skill's checker, not a target-product test layer."""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

import check


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="intentguard-check-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "repo" / ".intentgurad"
        self.root.mkdir(parents=True)
        self.case = {
            "id": "E2E-001", "cuj": "CUJ-CART", "title": "Refuse zero quantity",
            "status": "active", "source": "Test fixture contract",
            "approval": "Approved fixture",
            "given": ["An authenticated buyer has a prepared cart."],
            "then": [
                {"id": "A1", "expect": "The request is refused."},
                {"id": "A2", "expect": "The cart remains unchanged."},
            ],
            "data": {"setup": "Prepare cart.", "cleanup": "Restore owned cart."},
            "limitations": [],
            "executions": [
                {"id": "ui", "surface": "web", "when": ["Submit using UI."],
                 "projects": ["chromium"]},
                {"id": "http", "surface": "api", "when": ["POST zero quantity."],
                 "projects": ["api"]},
            ],
        }
        self.suite = {
            "version": 2, "playwright_config": "playwright.config.ts",
            "projects": ["chromium", "api"], "approval": "Approved fixture matrix",
            "cases": [self.case],
        }
        (self.root / "playwright.config.ts").write_text("// Fixture\n")
        folder = self.root / "tests" / "E2E-001"
        folder.mkdir(parents=True)
        (folder / "case.spec.ts").write_text("// Fixture\n")
        self.started = datetime.now(timezone.utc).isoformat()
        self.args = SimpleNamespace(
            report=str(self.base / "report.json"),
            started_after=self.started, exit_code=0,
        )

    def catalog(self):
        (self.root / "e2e.json").write_text(json.dumps(self.suite))
        return check.catalog(self.root)

    def report(self):
        suite, cases, _ = self.catalog()
        specs = []
        for case in cases:
            if case["status"] != "active":
                continue
            for execution in case["executions"]:
                for project in execution["projects"]:
                    annotations = [
                        {"type": "intentguard.case", "description": case["id"]},
                        {"type": "intentguard.digest", "description": case["digest"]},
                    ]
                    if suite["version"] == 2:
                        annotations.append({
                            "type": "intentguard.execution", "description": execution["id"],
                        })
                    specs.append({
                        "file": f"{case['id']}/case.spec.ts",
                        "tests": [{
                            "annotations": annotations, "projectName": project,
                            "status": "expected", "expectedStatus": "passed",
                            "results": [{
                                "status": "passed", "retry": 0, "workerIndex": 0,
                                "startTime": self.started, "errors": [],
                                "steps": [{"title": f"Then {a}"} for a in case["assertions"]],
                            }],
                        }],
                    })
        return {
            "config": {
                "rootDir": str(self.root / "tests"),
                "configFile": str(self.root / "playwright.config.ts"),
                "forbidOnly": True, "shard": None,
                "projects": [
                    {"name": p, "outputDir": str(self.base / "artifacts"),
                     "repeatEach": 1, "retries": 0} for p in suite["projects"]
                ],
            },
            "errors": [],
            "stats": {"startTime": self.started, "expected": len(specs),
                      "unexpected": 0, "skipped": 0, "flaky": 0},
            "suites": [{"specs": specs}],
        }

    def verify(self, report):
        Path(self.args.report).write_text(json.dumps(report))
        suite, cases, summary = self.catalog()
        return check.check_report(self.root, suite, cases, summary, self.args)

    def test_v2_selected_matrix_not_cartesian(self):
        result = self.verify(self.report())
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual((result["expected"], result["recorded"]), (2, 2))
        self.assertEqual({r["surface"] for r in result["cases"]}, {"web", "api"})

    def test_v2_single_api_execution(self):
        self.case["executions"] = [self.case["executions"][1]]
        result = self.verify(self.report())
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["expected"], 1)

    def test_v1_unchanged_digest_and_all_project_semantics(self):
        self.suite["version"] = 1
        del self.case["executions"]
        self.case.update(surface="public-api", when=["POST zero quantity."])
        original = deepcopy(self.case)
        expected_digest = hashlib.sha256(json.dumps(
            original, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        ).encode()).hexdigest()
        _, cases, _ = self.catalog()
        self.assertEqual(cases[0]["digest"], expected_digest)
        self.assertEqual(cases[0]["executions"][0]["projects"], self.suite["projects"])
        result = self.verify(self.report())
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["expected"], 2)
        self.assertEqual(self.suite["cases"][0], original)

    def test_invalid_execution_shapes(self):
        original = deepcopy(self.case["executions"])
        invalid = [
            [], [original[0], original[0]],
            [{**original[0], "id": "Bad ID"}],
            [{**original[0], "surface": "private"}],
            [{**original[0], "when": []}],
            [{**original[0], "projects": []}],
            [{**original[0], "projects": ["unknown"]}],
            [{**original[0], "projects": ["api", "api"]}],
            [{**original[0], "then": []}],
        ]
        for executions in invalid:
            with self.subTest(executions=executions):
                self.case["executions"] = executions
                with self.assertRaises(check.Invalid):
                    self.catalog()

    def test_mixed_version_shapes_rejected(self):
        self.case["surface"] = "web"
        with self.assertRaises(check.Invalid):
            self.catalog()
        del self.case["surface"]
        self.suite["version"] = 1
        with self.assertRaises(check.Invalid):
            self.catalog()

    def test_missing_duplicate_unknown_and_wrong_project(self):
        for kind in ("missing", "duplicate", "unknown", "wrong-project", "no-annotation"):
            with self.subTest(kind=kind):
                report = self.report()
                specs = report["suites"][0]["specs"]
                test = specs[0]["tests"][0]
                if kind == "missing":
                    specs.pop()
                    report["stats"]["expected"] -= 1
                elif kind == "duplicate":
                    specs.append(deepcopy(specs[0]))
                    report["stats"]["expected"] += 1
                elif kind == "unknown":
                    test["annotations"][-1]["description"] = "unapproved"
                elif kind == "wrong-project":
                    test["projectName"] = "api"
                else:
                    test["annotations"].pop()
                self.assertFalse(self.verify(report)["ok"])

    def test_stale_digest_and_report(self):
        report = self.report()
        self.case["then"][0]["expect"] = "The approved outcome changed."
        self.assertFalse(self.verify(report)["ok"])
        report = self.report()
        report["stats"]["startTime"] = "2020-01-01T00:00:00Z"
        self.assertFalse(self.verify(report)["ok"])

    def test_failures_cannot_be_reported_as_success(self):
        for kind in ("then-missing", "then-duplicate", "then-error", "cleanup",
                     "retry", "skipped", "flaky", "expected-failure", "global", "exit"):
            with self.subTest(kind=kind):
                report = self.report()
                test = report["suites"][0]["specs"][0]["tests"][0]
                attempt = test["results"][0]
                self.args.exit_code = 0
                if kind == "then-missing":
                    attempt["steps"].pop()
                elif kind == "then-duplicate":
                    attempt["steps"].append(deepcopy(attempt["steps"][0]))
                elif kind == "then-error":
                    attempt["steps"][0]["error"] = {"message": "Assertion failed"}
                elif kind == "cleanup":
                    attempt["errors"].append({"message": "Teardown failed"})
                elif kind == "retry":
                    attempt["retry"] = 1
                elif kind in ("skipped", "flaky"):
                    test["status"] = kind
                    report["stats"]["expected"] -= 1
                    report["stats"][kind] += 1
                elif kind == "expected-failure":
                    test["expectedStatus"] = "failed"
                elif kind == "global":
                    report["errors"].append({"message": "Global teardown failed"})
                else:
                    self.args.exit_code = 1
                self.assertFalse(self.verify(report)["ok"])

    def test_drafts_and_missing_approval_block_readiness(self):
        self.suite["approval"] = None
        self.case["status"] = "draft"
        self.case["approval"] = None
        _, _, summary = self.catalog()
        self.assertFalse(summary["ready"])
        self.assertEqual(len(summary["blockers"]), 3)

    def test_source_layout_and_committed_source_checks(self):
        suite, cases, _ = self.catalog()
        repo = self.root.parent
        def git(*args):
            subprocess.run(["git", "-C", str(repo), *args], check=True,
                           capture_output=True)
        git("init", "-q")
        git("add", ".intentgurad")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture")
        self.assertTrue(check.check_sources(self.root, suite, cases)["ok"])
        (self.root / "tests" / "E2E-001" / "case.spec.ts").write_text("// Changed\n")
        self.assertFalse(check.check_sources(self.root, suite, cases)["ok"])
        (self.root / "tests" / "E2E-001" / "case.spec.js").write_text("// Extra\n")
        with self.assertRaises(check.Invalid):
            check.source_layout(self.root, suite, cases)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(check.Invalid):
            check.decode_json('{"version": 2, "version": 1}')


if __name__ == "__main__":
    unittest.main()
