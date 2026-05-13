# Observability Contract

Every framework adapter should return enough information for the harness to
debug, compare, replay, and gate runs.

## Required Run Record Fields

- `timestamp`
- `run_id`
- `framework`
- `task_id`
- `task_instruction`
- `data_dir`
- `required_sources`
- `model` and provider metadata when available
- `final_output`
- `evaluation.score`
- `evaluation.failed_checks`
- `trace`

## Recommended Trace Events

| Event | Required fields |
| --- | --- |
| `run_started` | run_id, framework, task_id |
| `model_call` | model, input summary, output summary, token usage if available |
| `tool_call` | tool name, arguments, result summary, duration, error |
| `read_source` | path, checksum if available |
| `write_artifact` | path, artifact type |
| `human_review` | reviewer, decision, edited fields |
| `retry` | reason, attempt number |
| `run_finished` | status, duration, cleanup status |

## Quality Gates

- Minimum deterministic eval score.
- No missing required citations.
- No disallowed external-source claims.
- No unhandled tool errors.
- No unexpected writes outside the configured artifact directory.
- Maximum step count or duration for bounded tasks.

## Why This Matters

Frameworks differ in how they model agents: graph nodes, crews, planners, typed
agent calls, or provider-native sessions. Harness Engineering gives those
different runtimes a common audit shape so quality can be measured across them.
