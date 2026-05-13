# Adapter Sketches

Each adapter should translate one framework's execution model into the shared
`FrameworkAdapter` contract:

```python
class FrameworkAdapter(Protocol):
    name: str

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        ...
```

Keep adapters thin:

- Convert `HarnessTask` into the framework's native agent/workflow/task shape.
- Execute the framework.
- Capture traces, tool calls, artifacts, and final output.
- Return `AgentRunResult`.
- Let the harness own evaluation, run records, comparison, and CI policy.

The sketch files avoid real imports so this repo can demonstrate the architecture
without installing every framework.
