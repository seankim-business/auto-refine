from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RoutingPolicyIntegrationTests(unittest.TestCase):
    def test_generic_loop_handles_policy_artifact(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        src = repo_root / "examples" / "routing_policy_toy"
        with tempfile.TemporaryDirectory() as tmp:
            task_root = Path(tmp) / "routing_policy_toy"
            shutil.copytree(src, task_root)
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
            self.assertIn("security", final_policy["manual_review_categories"])
            self.assertTrue(final_policy["urgent_payment_manual"])
            self.assertNotIn("refund", final_policy["manual_review_categories"])

            report_text = (run_dir / "report.md").read_text()
            self.assertIn("constraint_failures", report_text)
            self.assertIn("over-escalate many categories to manual review", report_text)


if __name__ == "__main__":
    unittest.main()
