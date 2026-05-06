"""Run the dataroom harness, evaluate the answer, and append run history.

This is the first step toward the paper's Harness Evolution Loop:
Worker execution -> deterministic evaluation -> persisted history.
It intentionally does not auto-edit prompts or code yet.
"""

import asyncio
import logging
from pathlib import Path

from harness_config import DATAROOM_TASK_INSTRUCTION
from harness_eval import (
    append_run_record,
    build_run_record,
    evaluate_dataroom_output,
    format_eval_report,
)
from progress import Spinner

logging.basicConfig(level=logging.WARNING)


def evaluate_and_capture(final_output: str, history_path: Path | str = "eval_runs/dataroom_runs.jsonl"):
    """Evaluate a fixed output and append history without calling the model."""
    eval_result = evaluate_dataroom_output(final_output)
    record = build_run_record(final_output, eval_result)
    output_path = append_run_record(record, history_path)
    return eval_result, output_path


async def main() -> None:
    from harness_common import run_dataroom_task

    async with Spinner("Dataroom Analyst running with evaluation capture"):
        result = await run_dataroom_task(max_turns=10)

    eval_result, history_path = evaluate_and_capture(result.final_output)

    print("\n" + "=" * 60)
    print("TASK:")
    print(DATAROOM_TASK_INSTRUCTION)
    print("=" * 60)
    print("AGENT OUTPUT:")
    print("=" * 60)
    print(result.final_output)
    print("\n" + "=" * 60)
    print("EVALUATOR REPORT:")
    print("=" * 60)
    print(format_eval_report(eval_result))
    print(f"\nRun history appended to: {history_path}")


if __name__ == "__main__":
    asyncio.run(main())
