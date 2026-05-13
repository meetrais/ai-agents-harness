"""Framework-neutral contracts for Harness Engineering examples."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Protocol


REPO_ROOT = Path(__file__).resolve().parents[1]
DATAROOM = REPO_ROOT / "dataroom"


@dataclass(frozen=True)
class HarnessTask:
    """A portable task definition that any framework adapter can run."""

    task_id: str
    instruction: str
    data_dir: str
    required_source: str
    expected_metrics: dict[str, dict[str, float | str]]
    disallowed_claims: list[str]


@dataclass(frozen=True)
class AgentRunRequest:
    """Input passed from the harness into a framework adapter."""

    task: HarnessTask
    framework: str
    run_id: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class AgentRunResult:
    """Framework-neutral result returned by an adapter."""

    run_id: str
    framework: str
    final_output: str
    artifacts: dict[str, str]
    trace: list[dict[str, Any]]


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluation output suitable for CI gates and run history."""

    score: float
    passed_checks: list[str]
    failed_checks: list[str]
    notes: list[str]


@dataclass(frozen=True)
class HarnessRunRecord:
    """Complete run record for replay, audit, and comparison."""

    timestamp: str
    request: AgentRunRequest
    result: AgentRunResult
    evaluation: EvaluationResult


class FrameworkAdapter(Protocol):
    """Minimal contract each framework implementation must satisfy."""

    name: str

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        """Execute the task and return a framework-neutral result."""


class DeterministicDataroomAdapter:
    """Dependency-free reference adapter used for local harness testing."""

    name = "deterministic"

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        metrics_path = DATAROOM / request.task.required_source
        metrics = _read_metrics_table(metrics_path)
        rows = []
        for metric_key, expected in request.task.expected_metrics.items():
            label = str(expected["label"])
            fy2025 = metrics["FY2025"][label]
            fy2024 = metrics["FY2024"][label]
            delta = fy2025 - fy2024
            pct = (delta / fy2024) * 100
            rows.append(
                f"| {label.title()} | ${fy2025:.1f}M | ${fy2024:.1f}M | "
                f"${delta:.1f}M | {pct:.1f}% |"
            )

        output = "\n".join([
            f"Using {request.task.required_source} only:",
            "",
            "| Metric | FY2025 | FY2024 | Absolute change | Percentage change |",
            "| --- | ---: | ---: | ---: | ---: |",
            *rows,
        ])
        return AgentRunResult(
            run_id=request.run_id,
            framework=self.name,
            final_output=output,
            artifacts={},
            trace=[
                {
                    "event": "read_source",
                    "path": str(metrics_path.relative_to(REPO_ROOT)),
                },
                {
                    "event": "compose_answer",
                    "metrics": list(request.task.expected_metrics),
                },
            ],
        )


def load_task(path: Path | str) -> HarnessTask:
    """Load a portable task definition from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return HarnessTask(**data)


def evaluate_output(output: str, task: HarnessTask) -> EvaluationResult:
    """Deterministically evaluate a dataroom answer against the task contract."""
    passed: list[str] = []
    failed: list[str] = []
    notes: list[str] = []
    metric_sections = _metric_sections(output, task.expected_metrics)

    for metric_key, metric in task.expected_metrics.items():
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
        failed.append(f"required source {task.required_source} missing")

    lowered = output.lower()
    for claim in task.disallowed_claims:
        if claim.lower() in lowered:
            failed.append(f"disallowed claim present: {claim}")
            notes.append("The answer should be grounded only in configured sources.")

    total = len(passed) + len(failed)
    score = round(len(passed) / total, 3) if total else 0.0
    return EvaluationResult(score=score, passed_checks=passed, failed_checks=failed, notes=notes)


def build_run_record(
    request: AgentRunRequest,
    result: AgentRunResult,
    evaluation: EvaluationResult,
) -> HarnessRunRecord:
    """Create a serializable run record."""
    return HarnessRunRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        request=request,
        result=result,
        evaluation=evaluation,
    )


def append_run_record(record: HarnessRunRecord, output_dir: Path | str) -> Path:
    """Write a JSON run record and return its path."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{record.request.run_id}.json"
    path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True), encoding="utf-8")
    return path


def available_adapters() -> dict[str, FrameworkAdapter]:
    """Return adapters that can run without optional dependencies."""
    deterministic = DeterministicDataroomAdapter()
    return {deterministic.name: deterministic}


def _read_metrics_table(path: Path) -> dict[str, dict[str, float]]:
    text = path.read_text(encoding="utf-8")
    metrics: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        if not line.startswith("| FY"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        year, revenue, income, cash_flow = parts
        metrics[year] = {
            "revenue": _money_to_float(revenue),
            "operating income": _money_to_float(income),
            "operating cash flow": _money_to_float(cash_flow),
        }
    return metrics


def _money_to_float(value: str) -> float:
    match = re.search(r"\$?([\d.]+)\s*M", value, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse money value: {value}")
    return float(match.group(1))


def _metric_sections(
    text: str,
    expected_values: dict[str, dict[str, float | str]],
) -> dict[str, str]:
    matches: list[tuple[int, str]] = []
    for key, metric in expected_values.items():
        match = re.search(re.escape(str(metric["label"])), text, flags=re.IGNORECASE)
        if match:
            matches.append((match.start(), key))

    matches.sort()
    sections: dict[str, str] = {}
    for index, (start, key) in enumerate(matches):
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        sections[key] = text[start:next_start]
    return sections


def _number_present(text: str, expected: float, *, percent: bool) -> bool:
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in _numeric_candidates(expected, percent=percent)
    )


def _numeric_candidates(value: float, *, percent: bool) -> list[str]:
    one_decimal = f"{value:.1f}"
    whole = f"{round(value):.0f}"
    escaped_decimal = re.escape(one_decimal)

    if percent:
        return [
            rf"(?<![\d.]){escaped_decimal}\s*%",
            rf"(?<![\d.]){escaped_decimal}\s+percent",
            rf"(?<![\d.]){whole}\s*%",
            rf"(?<![\d.]){whole}\s+percent",
        ]

    return [
        rf"\$\s*{escaped_decimal}\s*M\b",
        rf"(?<![\d.]){escaped_decimal}\s*M\b",
        rf"\$\s*{escaped_decimal}\s+million\b",
        rf"(?<![\d.]){escaped_decimal}\s+million\b",
        rf"(?<![\d.]){escaped_decimal}(?![\d.])",
    ]
