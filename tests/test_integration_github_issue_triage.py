from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GithubIssueTriageIntegrationTests(unittest.TestCase):
    def test_public_issue_triage_example_keeps_best_policy(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        src = repo_root / "examples" / "github_issue_triage_public"
        with tempfile.TemporaryDirectory() as tmp:
            task_root = Path(tmp) / "github_issue_triage_public"
            shutil.copytree(src, task_root)
            (task_root / "policy.json").write_text(
                json.dumps(
                    {
                        "bug_keywords": ["bug", "fails", "error"],
                        "enhancement_keywords": ["should", "support"],
                        "manual_review_keywords": [],
                        "default_route": "enhancement",
                    },
                    indent=2,
                ) + "\n"
            )
            config_path = task_root / "task.json"

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "auto_refine",
                    "run",
                    str(config_path),
                    "--iterations",
                    "4",
                ],
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            self.assertIn("[complete] run_dir=", proc.stdout)

            runs_dir = task_root / "runs" / "auto-refine"
            run_dir = sorted(runs_dir.glob("run-*"))[-1]
            summary = json.loads((run_dir / "summary.json").read_text())
            records = summary["records"]
            keep_records = [r for r in records if r["decision"] == "keep"]
            discard_records = [r for r in records if r["decision"] == "discard"]

            self.assertTrue(keep_records)
            self.assertTrue(discard_records)

            final_policy = json.loads((task_root / "policy.json").read_text())
            self.assertIn("trusted host", final_policy["manual_review_keywords"])
            self.assertIn("json", final_policy["enhancement_keywords"])
            self.assertNotEqual(final_policy["default_route"], "manual_review")

            report_text = (run_dir / "report.md").read_text()
            self.assertIn("manual_review_rate", report_text)
            self.assertIn("over-escalate many issues to manual review", report_text)


if __name__ == "__main__":
    unittest.main()
