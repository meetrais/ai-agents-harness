"""Sketch: adapting PydanticAI to the framework-neutral harness contract.

PydanticAI is a good fit when the harness requires typed dependencies,
structured outputs, validation, and Python-first ergonomics.
"""

from __future__ import annotations

from harness_contract import AgentRunRequest, AgentRunResult


class PydanticAIAdapterSketch:
    name = "pydanticai"

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        """Translate HarnessTask into a typed PydanticAI agent call.

        Real implementation outline:
        1. Define dependency and result models for the task.
        2. Register tools for reading data and producing artifacts.
        3. Run the typed agent with request.task.instruction.
        4. Store validation errors and tool calls in `trace`.
        5. Return the validated output through AgentRunResult.
        """
        raise NotImplementedError("Install PydanticAI and implement this adapter.")
