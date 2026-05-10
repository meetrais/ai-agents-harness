from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO_ROOT / "openai-agents-harness"
sys.path.insert(0, str(HARNESS_DIR))

from harness_eval import evaluate_dataroom_output  # noqa: E402


PASSING_OUTPUT = """
Using metrics.md only:

| Metric | FY2025 | FY2024 | Absolute change | Percentage change |
| --- | ---: | ---: | ---: | ---: |
| Revenue | $124.3M | $98.7M | $25.6M | 25.9% |
| Operating income | $18.6M | $12.4M | $6.2M | 50.0% |
| Operating cash flow | $24.1M | $17.9M | $6.2M | 34.6% |
"""


class HarnessEvalTests(unittest.TestCase):
    def test_passing_output_scores_full_credit(self) -> None:
        result = evaluate_dataroom_output(PASSING_OUTPUT)

        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.failed_checks, [])

    def test_missing_metric_fails(self) -> None:
        output = PASSING_OUTPUT.replace("| Operating cash flow |", "| Cash from operations |")
        result = evaluate_dataroom_output(output)

        self.assertLess(result.score, 1.0)
        self.assertIn("operating cash flow: label missing", result.failed_checks)

    def test_incorrect_value_fails(self) -> None:
        output = PASSING_OUTPUT.replace("$124.3M", "$120.0M")
        result = evaluate_dataroom_output(output)

        self.assertLess(result.score, 1.0)
        self.assertIn("revenue: fy2025 value missing or incorrect", result.failed_checks)

    def test_swapped_metric_values_fail(self) -> None:
        output = """
        Source: metrics.md.
        Revenue: FY2025 was 18.6M versus FY2024 at 12.4M,
        up 6.2M, or 50%.
        Operating income: FY2025 was 124.3M versus 98.7M,
        up 25.6M, or 25.9%.
        Operating cash flow: FY2025 was 24.1M versus 17.9M,
        up 6.2M, or 34.6%.
        """
        result = evaluate_dataroom_output(output)

        self.assertLess(result.score, 1.0)
        self.assertIn("revenue: fy2025 value missing or incorrect", result.failed_checks)
        self.assertIn("operating income: fy2025 value missing or incorrect", result.failed_checks)

    def test_missing_source_fails_with_note(self) -> None:
        output = PASSING_OUTPUT.replace("Using metrics.md only:", "Using the provided file only:")
        result = evaluate_dataroom_output(output)

        self.assertLess(result.score, 1.0)
        self.assertIn("required source metrics.md missing", result.failed_checks)
        self.assertTrue(result.notes)

    def test_formatting_variations_are_accepted(self) -> None:
        output = """
        Source: metrics.md.
        Revenue: FY2025 was 124.3 million versus FY2024 at 98.7 million,
        up 25.6 million, or 26 percent.
        Operating income: FY2025 was $18.6 million versus $12.4 million,
        up $6.2 million, or 50%.
        Operating cash flow: FY2025 was 24.1M versus 17.9M,
        up 6.2M, or 35%.
        """
        result = evaluate_dataroom_output(output)

        self.assertEqual(result.score, 1.0)

    def test_external_source_claim_fails(self) -> None:
        output = PASSING_OUTPUT + "\nI also checked an external source for context."
        result = evaluate_dataroom_output(output)

        self.assertLess(result.score, 1.0)
        self.assertIn("external source usage claimed", result.failed_checks)

    def test_eval_loop_smoke_uses_fixed_output_without_model_call(self) -> None:
        module_path = HARNESS_DIR / "08_harness_eval_loop.py"
        spec = importlib.util.spec_from_file_location("harness_eval_loop", module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        history_path = REPO_ROOT / "eval_runs" / "test_dataroom_runs.jsonl"
        if history_path.exists():
            history_path.unlink()

        try:
            eval_result, output_path = module.evaluate_and_capture(PASSING_OUTPUT, history_path)

            self.assertEqual(eval_result.score, 1.0)
            self.assertEqual(output_path, history_path)
            record = json.loads(history_path.read_text(encoding="utf-8").strip())
            self.assertEqual(record["eval_result"]["score"], 1.0)
            self.assertIn("Dataroom Analyst", record["harness_config"]["worker_agent"])
        finally:
            if history_path.exists():
                history_path.unlink()


if __name__ == "__main__":
    unittest.main()
