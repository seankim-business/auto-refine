from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GoalTreeIntegrationTests(unittest.TestCase):
    def test_recursive_goal_tree_accepts_and_rejects_hypotheses(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(repo_root / "auto_refine", root / "auto_refine")
            shutil.copytree(repo_root / "goal_trees", root / "goal_trees")
            (root / "goal_trees" / "marketing_strategy" / "tasks" / "specificity_explicit" / "hero.md").write_text(
                "auto-refine makes artifacts better.\n"
            )
            (root / "goal_trees" / "marketing_strategy" / "tasks" / "specificity_vague" / "hero.md").write_text(
                "auto-refine makes artifacts better.\n"
            )
            (root / "goal_trees" / "marketing_strategy" / "tasks" / "hype_branch" / "hero.md").write_text(
                "auto-refine improves systems safely.\n"
            )
            config_path = root / "goal_trees" / "marketing_strategy" / "tree.json"

            proc = subprocess.run(
                [sys.executable, "-m", "auto_refine", "run-goal-tree", str(config_path)],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            self.assertIn("[complete] goal_tree_run_dir=", proc.stdout)

            runs_dir = root / "runs" / "goal-trees"
            run_dir = sorted(runs_dir.glob("run-*"))[-1]
            summary = json.loads((run_dir / "goal-tree-summary.json").read_text())
            root_node = summary["root"]

            self.assertEqual(root_node["verdict"], "accepted")
            self.assertEqual(len(root_node["children"]), 2)

            specificity = next(child for child in root_node["children"] if child["name"] == "improve-specificity")
            hype = next(child for child in root_node["children"] if child["name"] == "increase-excitement-with-hype")

            self.assertEqual(specificity["verdict"], "accepted")
            self.assertEqual(hype["verdict"], "rejected")
            self.assertEqual(len(specificity["children"]), 2)

            explicit = next(child for child in specificity["children"] if child["name"] == "name-bounded-artifacts-explicitly")
            vague = next(child for child in specificity["children"] if child["name"] == "keep-it-vague")

            self.assertEqual(explicit["verdict"], "accepted")
            self.assertEqual(vague["verdict"], "rejected")
            self.assertEqual(explicit["depth"], 2)
            self.assertEqual(vague["depth"], 2)

            report_text = (run_dir / "goal-tree-report.md").read_text()
            self.assertIn("strengthen-product-positioning", report_text)
            self.assertIn("increase-excitement-with-hype", report_text)


if __name__ == "__main__":
    unittest.main()
