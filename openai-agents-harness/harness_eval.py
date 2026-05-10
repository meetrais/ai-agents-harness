"""Deterministic evaluation and history capture for harness runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from harness_config import (
    DATAROOM_AGENT_INSTRUCTIONS,
    DATAROOM_TASK_INSTRUCTION,
    DEFAULT_DOCKER_IMAGE,
    DEFAULT_MODEL,
    DEFAULT_REASONING,
)


EXPECTED_METRICS = {
    "revenue": {
        "label": "revenue",
        "fy2025": 124.3,
        "fy2024": 98.7,
        "delta": 25.6,
        "pct": 25.9,
    },
    "operating_income": {
        "label": "operating income",
        "fy2025": 18.6,
        "fy2024": 12.4,
        "delta": 6.2,
        "pct": 50.0,
    },
    "operating_cash_flow": {
        "label": "operating cash flow",
        "fy2025": 24.1,
        "fy2024": 17.9,
        "delta": 6.2,
        "pct": 34.6,
    },
}


@dataclass(frozen=True)
class TaskDefinition:
    instruction: str
    expected_values: dict[str, dict[str, float | str]]
    required_source: str
    success_criteria: list[str]


@dataclass(frozen=True)
class EvalResult:
    score: float
    passed_checks: list[str]
    failed_checks: list[str]
    notes: list[str]


@dataclass(frozen=True)
class RunRecord:
    timestamp: str
    task: TaskDefinition
    harness_config: dict[str, Any]
    final_output: str
    eval_result: EvalResult


DATAROOM_TASK = TaskDefinition(
    instruction=DATAROOM_TASK_INSTRUCTION,
    expected_values=EXPECTED_METRICS,
    required_source="metrics.md",
    success_criteria=[
        "Includes FY2025 and FY2024 values for all required metrics.",
        "Includes absolute and percentage deltas for all required metrics.",
        "Cites metrics.md as the data source.",
        "Does not use or claim to use external data.",
    ],
)


def evaluate_dataroom_output(output: str, task: TaskDefinition = DATAROOM_TASK) -> EvalResult:
    """Score a dataroom answer against explicit, deterministic criteria."""
    passed: list[str] = []
    failed: list[str] = []
    notes: list[str] = []
    metric_sections = _metric_sections(output, task.expected_values)

    for metric_key, metric in task.expected_values.items():
        label = str(metric["label"])
        metric_text = metric_sections.get(metric_key, "")
        if metric_text:
            passed.append(f"{label}: label present")
        else:
            failed.append(f"{label}: label missing")

        for field in ("fy2025", "fy2024", "delta", "pct"):
            expected = float(metric[field])
            if _number_present(metric_text, expected, percent=(field == "pct")):
                passed.append(f"{label}: {field} value present")
            else:
                failed.append(f"{label}: {field} value missing or incorrect")

    if task.required_source.lower() in output.lower():
        passed.append("required source cited")
    else:
        failed.append("required source metrics.md missing")
        notes.append("The answer should cite metrics.md explicitly.")

    if _mentions_external_sources(output):
        failed.append("external source usage claimed")
        notes.append("The harness requires answers to use only files in data/.")
    else:
        passed.append("no external source usage claimed")

    total = len(passed) + len(failed)
    score = round(len(passed) / total, 3) if total else 0.0
    return EvalResult(score=score, passed_checks=passed, failed_checks=failed, notes=notes)


def build_run_record(final_output: str, eval_result: EvalResult) -> RunRecord:
    """Create a serializable run record for the standard dataroom harness."""
    return RunRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        task=DATAROOM_TASK,
        harness_config={
            "worker_agent": "Dataroom Analyst",
            "model": DEFAULT_MODEL,
            "reasoning": DEFAULT_REASONING,
            "sandbox_backend": "docker",
            "docker_image": DEFAULT_DOCKER_IMAGE,
            "max_turns": 10,
            "instructions": DATAROOM_AGENT_INSTRUCTIONS,
        },
        final_output=final_output,
        eval_result=eval_result,
    )


def append_run_record(record: RunRecord, path: Path | str = "eval_runs/dataroom_runs.jsonl") -> Path:
    """Append a run record as JSONL and return the resolved path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return output_path


def format_eval_report(result: EvalResult) -> str:
    """Format a compact human-readable report for terminal output."""
    lines = [f"Score: {result.score:.3f}"]
    if result.failed_checks:
        lines.append("Failed checks:")
        lines.extend(f"- {check}" for check in result.failed_checks)
    else:
        lines.append("All checks passed.")
    if result.notes:
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in result.notes)
    return "\n".join(lines)


def _number_present(text: str, expected: float, *, percent: bool) -> bool:
    candidates = _numeric_candidates(expected, percent=percent)
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in candidates)


def _metric_sections(
    text: str,
    expected_values: dict[str, dict[str, float | str]],
) -> dict[str, str]:
    """Return the text region belonging to each metric label."""
    labels = {
        key: str(metric["label"]).lower()
        for key, metric in expected_values.items()
    }
    matches: list[tuple[int, int, str]] = []
    for key, label in labels.items():
        match = re.search(re.escape(label), text, flags=re.IGNORECASE)
        if match:
            matches.append((match.start(), match.end(), key))

    matches.sort()
    sections: dict[str, str] = {}
    for index, (start, _end, key) in enumerate(matches):
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        sections[key] = text[start:next_start]
    return sections


def _numeric_candidates(value: float, *, percent: bool) -> list[str]:
    one_decimal = f"{value:.1f}"
    whole = f"{round(value):.0f}"
    escaped_decimal = re.escape(one_decimal)

    if percent:
        patterns = [
            rf"(?<![\d.]){escaped_decimal}\s*%",
            rf"(?<![\d.]){escaped_decimal}\s+percent",
            rf"(?<![\d.]){whole}\s*%",
            rf"(?<![\d.]){whole}\s+percent",
        ]
        return patterns

    return [
        rf"\$\s*{escaped_decimal}\s*M\b",
        rf"(?<![\d.]){escaped_decimal}\s*M\b",
        rf"\$\s*{escaped_decimal}\s+million\b",
        rf"(?<![\d.]){escaped_decimal}\s+million\b",
        rf"(?<![\d.]){escaped_decimal}(?![\d.])",
    ]


def _mentions_external_sources(text: str) -> bool:
    lowered = text.lower()
    suspicious_phrases = [
        "external source",
        "outside source",
        "web search",
        "searched the web",
        "according to the web",
        "internet source",
    ]
    return any(phrase in lowered for phrase in suspicious_phrases)
