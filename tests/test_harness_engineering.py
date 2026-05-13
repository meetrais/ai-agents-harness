from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_ENGINEERING_DIR = REPO_ROOT / "harness-engineering"
sys.path.insert(0, str(HARNESS_ENGINEERING_DIR))

from harness_contract import (  # noqa: E402
    AgentRunRequest,
    available_adapters,
    evaluate_output,
    load_task,
)


class HarnessEngineeringTests(unittest.TestCase):
    def test_deterministic_adapter_scores_full_credit(self) -> None:
        task = load_task(HARNESS_ENGINEERING_DIR / "tasks" / "dataroom_financials.json")
        adapter = available_adapters()["deterministic"]
        result = adapter.run(
            AgentRunRequest(
                task=task,
                framework=adapter.name,
                run_id="test-run",
                metadata={},
            )
        )
        evaluation = evaluate_output(result.final_output, task)

        self.assertEqual(evaluation.score, 1.0)
        self.assertEqual(evaluation.failed_checks, [])

    def test_swapped_framework_neutral_values_fail(self) -> None:
        task = load_task(HARNESS_ENGINEERING_DIR / "tasks" / "dataroom_financials.json")
        output = """
        Source: metrics.md.
        Revenue: FY2025 was 18.6M versus FY2024 at 12.4M,
        up 6.2M, or 50%.
        Operating income: FY2025 was 124.3M versus 98.7M,
        up 25.6M, or 25.9%.
        Operating cash flow: FY2025 was 24.1M versus 17.9M,
        up 6.2M, or 34.6%.
        """
        evaluation = evaluate_output(output, task)

        self.assertLess(evaluation.score, 1.0)
        self.assertIn("revenue: fy2025 value missing or incorrect", evaluation.failed_checks)

    def test_cli_module_imports(self) -> None:
        module_path = HARNESS_ENGINEERING_DIR / "run_harness.py"
        spec = importlib.util.spec_from_file_location("run_harness", module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        self.assertTrue(hasattr(module, "main"))


if __name__ == "__main__":
    unittest.main()
