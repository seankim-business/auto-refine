from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ResumeIntegrationTests(unittest.TestCase):
    def test_resume_continues_latest_run_to_total_budget(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            task_root = Path(tmp) / "repo"
            shutil.copytree(repo_root / "auto_refine", task_root / "auto_refine")
            shutil.copytree(repo_root / "self_tasks", task_root / "self_tasks")
            shutil.copytree(repo_root / "marketing", task_root / "marketing")
            shutil.copy2(repo_root / "README.md", task_root / "README.md")
            shutil.copy2(repo_root / ".gitignore", task_root / ".gitignore")
            (task_root / "marketing" / "hero.md").write_text(
                "auto-refine helps improve artifacts by running bounded experiments.\n"
            )
            config_path = task_root / "self_tasks" / "marketing_copy" / "task.json"

            first = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "auto_refine",
                    "resume",
                    "--task",
                    str(config_path),
                    "--budget",
                    "2",
                ],
                cwd=task_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            self.assertIn("[complete] resumed_run_dir=", first.stdout)

            second = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "auto_refine",
                    "resume",
                    "--task",
                    str(config_path),
                    "--budget",
                    "4",
                ],
                cwd=task_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            self.assertIn("[complete] resumed_run_dir=", second.stdout)

            runs_dir = task_root / "runs" / "self-refine-marketing"
            run_dirs = sorted(runs_dir.glob("run-*"))
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]

            state = json.loads((run_dir / "state.json").read_text())
            self.assertEqual(state["attempts_completed"], 4)
            self.assertEqual(state["kept_trials"], 1)

            ledger_lines = [line for line in (run_dir / "ledger.jsonl").read_text().splitlines() if line.strip()]
            self.assertEqual(len(ledger_lines), 5)  # baseline + 4 trials

            final_artifact = (task_root / "marketing" / "hero.md").read_text()
            self.assertIn("trusted evaluator", final_artifact)
            self.assertIn("rolls back bad candidates automatically", final_artifact)

            incumbent_copy = (run_dir / "incumbent" / "marketing" / "hero.md").read_text()
            self.assertEqual(final_artifact, incumbent_copy)


if __name__ == "__main__":
    unittest.main()
