"""Sketch: adapting LangGraph to the framework-neutral harness contract.

LangGraph is a strong fit when the harness needs explicit state transitions,
retry branches, human review nodes, replay, and durable checkpoints.
"""

from __future__ import annotations

from harness_contract import AgentRunRequest, AgentRunResult


class LangGraphAdapterSketch:
    name = "langgraph"

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        """Translate HarnessTask into a LangGraph state graph.

        Real implementation outline:
        1. Build a graph state with task, data_dir, messages, tool trace.
        2. Add nodes such as read_sources -> analyze -> draft -> verify.
        3. Use a checkpointer for resumability.
        4. Stream or collect graph events into `trace`.
        5. Return final answer and artifacts through AgentRunResult.
        """
        raise NotImplementedError("Install LangGraph and implement this adapter.")
