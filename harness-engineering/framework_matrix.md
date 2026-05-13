# Framework Matrix

Harness Engineering should make the framework decision explicit and reversible.

| Framework category | Examples | Best fit | Harness concern |
| --- | --- | --- | --- |
| Explicit state graphs | LangGraph | Complex workflows, branching, retries, human review, replay | Capture graph state, node transitions, checkpoints |
| Role-based crews | CrewAI | Multi-agent division of labor, fast prototypes, analyst/writer/reviewer teams | Attribute outputs and failures to roles |
| Typed Python agents | PydanticAI | Structured outputs, dependency injection, validation-heavy workflows | Store validation errors and schema versions |
| Enterprise planners | Semantic Kernel | Microsoft/Azure stacks, C# parity, planner/plugin workflows | Capture plugin calls and planner decisions |
| Data-grounded agents | LlamaIndex agents | RAG-heavy workflows over private corpora | Capture retrieved nodes, indexes, citations |
| Conversational multi-agent | AutoGen/AG2 | Research-style agent conversations and debate loops | Detect loops, speaker drift, and termination failures |
| Provider-native SDKs | OpenAI Agents SDK, Claude Agent SDK, Google ADK | Tight integration with a provider's model/tool/runtime stack | Preserve portability with adapter boundaries |
| Low-code orchestration | n8n, visual builders | Business process automation and ops handoff | Export workflow versions and human approvals |

## Adapter Readiness Checklist

- Can run the same `HarnessTask`.
- Can return an `AgentRunResult` with final output, artifacts, and trace.
- Can preserve tool calls or equivalent steps.
- Can expose model/provider metadata.
- Can support deterministic replay or explain why not.
- Can clean up external sessions and mounted data.
- Can run in CI with either real credentials or a deterministic fake.

## Evaluation Compatibility

| Eval type | Purpose | Should be framework-specific? |
| --- | --- | --- |
| Deterministic fact checks | CI gate for known answers | No |
| Source/citation checks | Grounding and auditability | No |
| Tool correctness | Tool choice and argument quality | Mostly no |
| Trajectory checks | Plan quality, loops, redundant steps | Adapter normalizes trace shape |
| LLM-as-judge | Rubric scoring for open-ended work | No, but judge prompts should know trace schema |
| Human review | Production escalation and labeling | No |
