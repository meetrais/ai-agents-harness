"""Shared constants for the dataroom harness examples."""

from __future__ import annotations


DEFAULT_MODEL = "gpt-5.4"
DEFAULT_REASONING = {"effort": "none"}
DEFAULT_DOCKER_IMAGE = "python:3.14-slim"
DATAROOM_TASK_INSTRUCTION = (
    "Compare FY2025 revenue, operating income, and operating cash flow with FY2024. "
    "For each metric, include the FY2025 value, FY2024 value, absolute change, "
    "and percentage change. Use only files in data/ and cite metrics.md."
)
DATAROOM_AGENT_INSTRUCTIONS = (
    "Answer using only files in data/. Cite source filenames. "
    "Keep the response concise. Do not use external sources. "
    "When comparing metrics, include both years, absolute deltas, and percentage deltas."
)
