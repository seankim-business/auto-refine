from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import load_task_config
from .decision import evaluate_constraints, is_improvement, primary_value
from .models import TaskConfig, TrialRecord


class EngineError(RuntimeError):
    pass


def _now_slug() -> str:
    return datetime.now().strftime("run-%Y%m%d-%H%M%S")


def _read_snapshot(paths: list[Path]) -> dict[str, bytes]:
    return {str(path): path.read_bytes() for path in paths}


def _restore_snapshot(snapshot: dict[str, bytes]) -> None:
    for raw_path, payload in snapshot.items():
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def _extract_last_json_line(output: str) -> dict[str, Any]:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise EngineError("no JSON object found in command output")


def _run_command(command: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_path.write_text(proc.stdout)
    return proc.returncode, proc.stdout


class GenericAutoresearchEngine:
    def __init__(self, task: TaskConfig, run_dir: Path):
        self.task = task
        self.run_dir = run_dir
        self.ledger_path = run_dir / "ledger.jsonl"
        self.records: list[TrialRecord] = []

    @classmethod
    def from_config(cls, config_path: str | Path) -> "GenericAutoresearchEngine":
        task = load_task_config(config_path)
        run_dir = task.output_dir / _now_slug()
        run_dir.mkdir(parents=True, exist_ok=True)
        return cls(task=task, run_dir=run_dir)

    def _base_env(self, attempt: int) -> dict[str, str]:
        env = os.environ.copy()
        env["AUTORESEARCH_TASK_ROOT"] = str(self.task.task_root)
        env["AUTORESEARCH_RUN_DIR"] = str(self.run_dir)
        env["AUTORESEARCH_ATTEMPT"] = str(attempt)
        env["AUTORESEARCH_MUTABLE_PATHS_JSON"] = json.dumps(
            [str(path.relative_to(self.task.task_root)) for path in self.task.mutable_paths]
        )
        return env

    def _append_record(self, record: TrialRecord) -> None:
        self.records.append(record)
        with self.ledger_path.open("a") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def run(self, iteration_override: int | None = None) -> Path:
        iterations = iteration_override or self.task.iterations
        incumbent_snapshot = _read_snapshot(self.task.mutable_paths)
        baseline_record = self._run_baseline(incumbent_snapshot)
        incumbent_metrics = baseline_record.metrics

        for attempt in range(1, iterations + 1):
            _restore_snapshot(incumbent_snapshot)
            record, candidate_snapshot = self._run_trial(attempt, incumbent_metrics)
            if record.decision == "keep":
                incumbent_snapshot = candidate_snapshot
                incumbent_metrics = record.metrics
            else:
                _restore_snapshot(incumbent_snapshot)
            self._append_record(record)
            primary = record.metrics.get(self.task.objective.primary_metric)
            print(
                f"[trial {attempt}] {record.name} decision={record.decision} primary={primary}",
                flush=True,
            )

        _restore_snapshot(incumbent_snapshot)
        self._write_report()
        return self.run_dir

    def _run_baseline(self, incumbent_snapshot: dict[str, bytes]) -> TrialRecord:
        _restore_snapshot(incumbent_snapshot)
        env = self._base_env(0)
        eval_log = self.run_dir / "baseline-evaluator.log"
        exit_code, output = _run_command(self.task.baseline_command, self.task.task_root, env, eval_log)
        if exit_code != 0:
            raise EngineError(f"baseline failed; see {eval_log}")
        metrics = _extract_last_json_line(output)
        record = TrialRecord(
            attempt=0,
            phase="baseline",
            name="baseline",
            mutation="baseline",
            metrics=metrics,
            decision="baseline",
            improved=False,
            constraint_failures=[],
            evaluator_exit_code=exit_code,
            evaluator_log=str(eval_log),
            candidate_primary=primary_value(metrics, self.task.objective),
        )
        self._append_record(record)
        print(
            f"[baseline] primary={record.metrics.get(self.task.objective.primary_metric)}",
            flush=True,
        )
        return record

    def _run_trial(self, attempt: int, incumbent_metrics: dict[str, Any]) -> tuple[TrialRecord, dict[str, bytes]]:
        env = self._base_env(attempt)
        env["AUTORESEARCH_INCUMBENT_METRICS_JSON"] = json.dumps(incumbent_metrics)

        proposer_log = self.run_dir / f"attempt-{attempt:03d}-proposer.log"
        proposer_exit, proposer_output = _run_command(
            self.task.proposer_command,
            self.task.task_root,
            env,
            proposer_log,
        )
        mutation = "candidate"
        if proposer_output.strip():
            try:
                mutation = _extract_last_json_line(proposer_output).get("description", mutation)
            except EngineError:
                mutation = proposer_output.strip().splitlines()[-1][:120]
        if proposer_exit != 0:
            return (
                TrialRecord(
                    attempt=attempt,
                    phase="trial",
                    name=f"attempt-{attempt}",
                    mutation=mutation,
                    metrics={},
                    decision="discard",
                    improved=False,
                    constraint_failures=["proposer failed"],
                    proposer_exit_code=proposer_exit,
                    proposer_log=str(proposer_log),
                    error="proposer failed",
                ),
                _read_snapshot(self.task.mutable_paths),
            )

        candidate_snapshot = _read_snapshot(self.task.mutable_paths)
        trial_log = self.run_dir / f"attempt-{attempt:03d}-trial.log"
        evaluator_exit, evaluator_output = _run_command(
            self.task.trial_command,
            self.task.task_root,
            env,
            trial_log,
        )
        if evaluator_exit != 0:
            return (
                TrialRecord(
                    attempt=attempt,
                    phase="trial",
                    name=f"attempt-{attempt}",
                    mutation=mutation,
                    metrics={},
                    decision="discard",
                    improved=False,
                    constraint_failures=["trial command failed"],
                    proposer_exit_code=proposer_exit,
                    evaluator_exit_code=evaluator_exit,
                    proposer_log=str(proposer_log),
                    evaluator_log=str(trial_log),
                    error="trial command failed",
                ),
                candidate_snapshot,
            )

        metrics = _extract_last_json_line(evaluator_output)
        failures = evaluate_constraints(metrics, self.task.objective)
        improved = not failures and is_improvement(metrics, incumbent_metrics, self.task.objective)
        decision = "keep" if improved else "discard"
        return (
            TrialRecord(
                attempt=attempt,
                phase="trial",
                name=f"attempt-{attempt}",
                mutation=mutation,
                metrics=metrics,
                decision=decision,
                improved=improved,
                constraint_failures=failures,
                proposer_exit_code=proposer_exit,
                evaluator_exit_code=evaluator_exit,
                proposer_log=str(proposer_log),
                evaluator_log=str(trial_log),
                incumbent_primary=primary_value(incumbent_metrics, self.task.objective),
                candidate_primary=primary_value(metrics, self.task.objective),
            ),
            candidate_snapshot,
        )

    def _write_report(self) -> None:
        primary = self.task.objective.primary_metric
        direction = self.task.objective.direction
        trials = [r for r in self.records if r.phase == "trial"]
        kept = [r for r in trials if r.decision == "keep"]
        baseline = next((r for r in self.records if r.phase == "baseline"), None)
        scored = [r for r in self.records if r.metrics.get(primary) is not None]
        scored.sort(
            key=lambda r: float(r.metrics[primary]),
            reverse=(direction == "maximize"),
        )

        lines = [
            "# auto-refine Report",
            "",
            f"Task: `{self.task.name}`",
            f"Run dir: `{self.run_dir}`",
            f"Primary metric: `{primary}` ({direction})",
            "",
        ]
        if baseline:
            lines.append(
                f"Baseline `{primary}`: **{baseline.metrics.get(primary)}**"
            )
            lines.append("")
        if scored:
            winner = scored[0]
            lines.append(
                f"Best observed result: **{winner.name}** — `{primary}={winner.metrics.get(primary)}`"
            )
            lines.append("")
        lines.extend([
            "## Leaderboard",
            "",
        ])
        for idx, record in enumerate(scored, 1):
            lines.append(
                f"{idx}. **{record.name}** — {primary} `{record.metrics.get(primary)}` · decision `{record.decision}` · mutation `{record.mutation}`"
            )
        if not scored:
            lines.append("- none")
        lines.append("")
        lines.extend([
            "## Trial Summary",
            "",
            f"Trials: `{len(trials)}`",
            f"Kept: `{len(kept)}`",
            f"Discarded: `{len([r for r in trials if r.decision == 'discard'])}`",
            "",
        ])
        for record in trials:
            lines.append(f"### {record.name}")
            lines.append(f"- mutation: {record.mutation}")
            lines.append(f"- decision: {record.decision}")
            lines.append(f"- {primary}: {record.metrics.get(primary)}")
            if record.constraint_failures:
                lines.append(f"- constraint_failures: {', '.join(record.constraint_failures)}")
            if record.error:
                lines.append(f"- error: {record.error}")
            lines.append("")

        (self.run_dir / "report.md").write_text("\n".join(lines))
        summary = {
            "task": self.task.name,
            "primary_metric": primary,
            "direction": direction,
            "records": [asdict(record) for record in self.records],
        }
        (self.run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))


def run_from_config(config_path: str | Path, iteration_override: int | None = None) -> Path:
    engine = GenericAutoresearchEngine.from_config(config_path)
    return engine.run(iteration_override=iteration_override)
