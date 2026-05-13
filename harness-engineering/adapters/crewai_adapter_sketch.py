"""Sketch: adapting CrewAI to the framework-neutral harness contract.

CrewAI is a natural fit for role-based teams where tasks decompose into analyst,
writer, reviewer, or supervisor roles.
"""

from __future__ import annotations

from harness_contract import AgentRunRequest, AgentRunResult


class CrewAIAdapterSketch:
    name = "crewai"

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        """Translate HarnessTask into CrewAI agents and tasks.

        Real implementation outline:
        1. Create role agents from harness metadata.
        2. Create a task using request.task.instruction and mounted data.
        3. Run the crew sequentially or hierarchically.
        4. Capture per-agent outputs and tool use into `trace`.
        5. Return the final crew output through AgentRunResult.
        """
        raise NotImplementedError("Install CrewAI and implement this adapter.")
