from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SelfRefineMarketingIntegrationTests(unittest.TestCase):
    def test_repo_can_refine_its_own_marketing_copy(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            task_root = Path(tmp) / "repo"
            shutil.copytree(repo_root / "auto_refine", task_root / "auto_refine")
            shutil.copytree(repo_root / "self_tasks", task_root / "self_tasks")
            shutil.copytree(repo_root / "marketing", task_root / "marketing")
            shutil.copy2(repo_root / "README.md", task_root / "README.md")
            shutil.copy2(repo_root / ".gitignore", task_root / ".gitignore")
            config_path = task_root / "self_tasks" / "marketing_copy" / "task.json"

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
                cwd=task_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            self.assertIn("[complete] run_dir=", proc.stdout)

            runs_dir = task_root / "runs" / "self-refine-marketing"
            run_dir = sorted(runs_dir.glob("run-*"))[-1]
            summary = json.loads((run_dir / "summary.json").read_text())
            records = summary["records"]

            keep_records = [r for r in records if r["decision"] == "keep"]
            discard_records = [r for r in records if r["decision"] == "discard"]
            self.assertTrue(keep_records)
            self.assertTrue(discard_records)

            final_artifact = (task_root / "marketing" / "hero.md").read_text()
            self.assertIn("trusted evaluator", final_artifact)
            self.assertIn("rolls back bad candidates automatically", final_artifact)
            self.assertNotIn("magical", final_artifact)

            baseline_record = next(r for r in records if r["phase"] == "baseline")
            kept_record = next(r for r in records if r["decision"] == "keep")
            self.assertIn("marketing/hero.md", baseline_record["artifacts"])
            self.assertIn("marketing/hero.md", kept_record["artifacts"])


if __name__ == "__main__":
    unittest.main()
