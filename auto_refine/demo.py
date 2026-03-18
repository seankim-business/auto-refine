from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DemoBuildError(RuntimeError):
    pass


def _latest_match(repo_root: Path, pattern: str) -> Path:
    matches = sorted(repo_root.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise DemoBuildError(f"no summary matched pattern: {pattern}")
    return matches[-1]


def _primary_value(record: dict[str, Any], primary_metric: str) -> float | None:
    metrics = record.get("metrics", {})
    value = metrics.get(primary_metric)
    if value is None:
        return None
    return float(value)


def _select_best_record(records: list[dict[str, Any]], primary_metric: str, direction: str) -> dict[str, Any]:
    scored = [r for r in records if _primary_value(r, primary_metric) is not None]
    if not scored:
        raise DemoBuildError("no scored records found")
    reverse = direction == "maximize"
    scored.sort(key=lambda r: float(r["metrics"][primary_metric]), reverse=reverse)
    return scored[0]


def _incumbent_progression(records: list[dict[str, Any]], primary_metric: str) -> list[float]:
    baseline = next((r for r in records if r.get("phase") == "baseline"), None)
    if baseline is None:
        raise DemoBuildError("baseline record missing")
    current = float(baseline["metrics"][primary_metric])
    progression = [current]
    for record in records:
        if record.get("phase") != "trial":
            continue
        candidate = _primary_value(record, primary_metric)
        if record.get("decision") == "keep" and candidate is not None:
            current = candidate
        progression.append(current)
    return progression


def _merge_example(repo_root: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    summary_path = _latest_match(repo_root, metadata["summaryGlob"])
    summary = json.loads(summary_path.read_text())
    records = summary["records"]
    primary_metric = summary["primary_metric"]
    direction = summary["direction"]
    baseline = next((r for r in records if r.get("phase") == "baseline"), None)
    if baseline is None:
        raise DemoBuildError(f"baseline missing in {summary_path}")
    kept = [r for r in records if r.get("decision") == "keep"]
    best_record = _select_best_record(kept or records, primary_metric, direction)
    artifact_path = metadata["artifactPath"]

    return {
        **metadata,
        "primaryMetric": primary_metric,
        "direction": direction,
        "baselineValue": float(baseline["metrics"][primary_metric]),
        "bestValue": float(best_record["metrics"][primary_metric]),
        "baselineArtifact": baseline.get("artifacts", {}).get(artifact_path, ""),
        "bestArtifact": best_record.get("artifacts", {}).get(artifact_path, ""),
        "incumbentProgression": _incumbent_progression(records, primary_metric),
        "records": records,
        "generatedFrom": str(summary_path.relative_to(repo_root)),
    }


def _count_goal_nodes(node: dict[str, Any]) -> dict[str, int]:
    accepted = 1 if node.get("verdict") == "accepted" else 0
    rejected = 1 if node.get("verdict") == "rejected" else 0
    total = 1
    for child in node.get("children", []):
        child_counts = _count_goal_nodes(child)
        total += child_counts["total"]
        accepted += child_counts["accepted"]
        rejected += child_counts["rejected"]
    return {"total": total, "accepted": accepted, "rejected": rejected}



def _merge_goal_tree(repo_root: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    summary_path = _latest_match(repo_root, metadata["summaryGlob"])
    summary = json.loads(summary_path.read_text())
    counts = _count_goal_nodes(summary["root"])
    return {
        **metadata,
        "root": summary["root"],
        "nodeCounts": counts,
        "generatedFrom": str(summary_path.relative_to(repo_root)),
    }



def build_demo_data(config_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text())
    repo_root = (config_path.parent / config.get("repoRoot", "..")).resolve()

    data = {
        "site": config["site"],
        "whatGetsOptimized": config["whatGetsOptimized"],
        "decisionRules": config["decisionRules"],
        "examples": [_merge_example(repo_root, item) for item in config["examples"]],
        "goalTrees": [_merge_goal_tree(repo_root, item) for item in config.get("goalTrees", [])],
    }

    if output_path is not None:
        output = Path(output_path).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data
