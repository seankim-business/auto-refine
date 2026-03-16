from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from auto_refine.demo import build_demo_data


class DemoBuilderTests(unittest.TestCase):
    def test_build_demo_data_merges_runtime_summary_with_static_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            runs = root / "runs" / "example" / "run-1"
            docs.mkdir(parents=True)
            runs.mkdir(parents=True)

            summary = {
                "task": "example-task",
                "primary_metric": "quality_score",
                "direction": "maximize",
                "records": [
                    {
                        "attempt": 0,
                        "phase": "baseline",
                        "name": "baseline",
                        "mutation": "baseline",
                        "metrics": {"quality_score": 0.2},
                        "decision": "baseline",
                        "improved": False,
                        "constraint_failures": [],
                        "artifacts": {"artifact.txt": "before"},
                    },
                    {
                        "attempt": 1,
                        "phase": "trial",
                        "name": "attempt-1",
                        "mutation": "better candidate",
                        "metrics": {"quality_score": 0.9},
                        "decision": "keep",
                        "improved": True,
                        "constraint_failures": [],
                        "artifacts": {"artifact.txt": "after"},
                    },
                    {
                        "attempt": 2,
                        "phase": "trial",
                        "name": "attempt-2",
                        "mutation": "bad candidate",
                        "metrics": {"quality_score": 0.5},
                        "decision": "discard",
                        "improved": False,
                        "constraint_failures": ["latency too high"],
                        "artifacts": {"artifact.txt": "bad"},
                    },
                ],
            }
            (runs / "summary.json").write_text(json.dumps(summary))

            config = {
                "repoRoot": "..",
                "site": {"title": "demo", "tagline": "tag", "proofNote": "note"},
                "whatGetsOptimized": [],
                "decisionRules": [],
                "examples": [
                    {
                        "id": "example",
                        "summaryGlob": "runs/example/run-*/summary.json",
                        "title": "Example",
                        "artifactType": "text",
                        "artifactPath": "artifact.txt",
                        "problem": "problem",
                        "objectiveSummary": "objective",
                        "optimizedThing": "thing",
                        "whyKept": "why",
                        "caseStudies": [],
                    }
                ],
            }
            config_path = docs / "demo-config.json"
            config_path.write_text(json.dumps(config))
            output_path = docs / "demo-data.json"

            data = build_demo_data(config_path, output_path=output_path)
            example = data["examples"][0]

            self.assertEqual(example["baselineValue"], 0.2)
            self.assertEqual(example["bestValue"], 0.9)
            self.assertEqual(example["baselineArtifact"], "before")
            self.assertEqual(example["bestArtifact"], "after")
            self.assertEqual(example["incumbentProgression"], [0.2, 0.9, 0.9])
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
