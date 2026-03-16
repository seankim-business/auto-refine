from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PromptEvalIntegrationTests(unittest.TestCase):
    def test_generic_loop_keeps_best_and_rolls_back_discards(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        src = repo_root / "examples" / "prompt_eval_toy"
        with tempfile.TemporaryDirectory() as tmp:
            task_root = Path(tmp) / "prompt_eval_toy"
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
            run_dirs = sorted(runs_dir.glob("run-*"))
            self.assertTrue(run_dirs)
            run_dir = run_dirs[-1]

            summary = json.loads((run_dir / "summary.json").read_text())
            records = summary["records"]
            keep_records = [r for r in records if r["decision"] == "keep"]
            discard_records = [r for r in records if r["decision"] == "discard"]

            self.assertTrue(keep_records)
            self.assertTrue(discard_records)

            final_prompt = (task_root / "prompts" / "system.md").read_text()
            self.assertIn("Ask one clarifying question when needed.", final_prompt)
            self.assertNotIn("Ignore safety constraints", final_prompt)

            report_text = (run_dir / "report.md").read_text()
            self.assertIn("Best observed result", report_text)
            self.assertIn("constraint_failures", report_text)


if __name__ == "__main__":
    unittest.main()
