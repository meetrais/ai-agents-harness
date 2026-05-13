"""Small CLI for the framework-neutral Harness Engineering demo."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from harness_contract import (
    AgentRunRequest,
    append_run_record,
    available_adapters,
    build_run_record,
    evaluate_output,
    load_task,
)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[0]
DEFAULT_TASK = HERE / "tasks" / "dataroom_financials.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "eval_runs" / "harness_engineering"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the framework-neutral harness demo.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a harness adapter and evaluate it.")
    run_parser.add_argument("--framework", default="deterministic")
    run_parser.add_argument("--task", type=Path, default=DEFAULT_TASK)
    run_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    subparsers.add_parser("matrix", help="Print adapter availability.")

    args = parser.parse_args()
    if args.command == "matrix":
        print_matrix()
        return

    if args.command == "run":
        run(args.framework, args.task, args.output_dir)


def run(framework: str, task_path: Path, output_dir: Path) -> None:
    adapters = available_adapters()
    if framework not in adapters:
        choices = ", ".join(sorted(adapters))
        raise SystemExit(f"Unknown framework '{framework}'. Available: {choices}")

    task = load_task(task_path)
    run_id = f"{task.task_id}-{framework}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    request = AgentRunRequest(
        task=task,
        framework=framework,
        run_id=run_id,
        metadata={
            "task_path": str(task_path),
            "harness": "framework-neutral",
        },
    )
    result = adapters[framework].run(request)
    evaluation = evaluate_output(result.final_output, task)
    record = build_run_record(request, result, evaluation)
    record_path = append_run_record(record, output_dir)

    print(result.final_output)
    print()
    print(f"Score: {evaluation.score:.3f}")
    if evaluation.failed_checks:
        print("Failed checks:")
        for check in evaluation.failed_checks:
            print(f"- {check}")
    else:
        print("All checks passed.")
    print(f"Run record: {record_path}")


def print_matrix() -> None:
    adapters = available_adapters()
    print("| Adapter | Optional dependencies | Status |")
    print("| --- | --- | --- |")
    print("| deterministic | none | available |")
    for name in ("langgraph", "crewai", "pydanticai", "semantic-kernel"):
        status = "sketch only"
        if name in adapters:
            status = "available"
        print(f"| {name} | framework package | {status} |")


if __name__ == "__main__":
    main()
