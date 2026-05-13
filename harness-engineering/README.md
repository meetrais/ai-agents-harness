# Harness Engineering

This folder demonstrates **Harness Engineering** as a framework-neutral discipline:
the same task contract, run record, evaluation policy, and observability shape can
wrap different agent frameworks.

The sibling `openai-agents-harness/` folder shows one concrete OpenAI Agents SDK
implementation. This folder shows the reusable harness layer you would keep even
when swapping orchestration frameworks.

## Current Landscape

As of 2026, agent engineering has separated into two practical layers:

- **Agent orchestration frameworks**: LangGraph, CrewAI, Semantic Kernel,
  LlamaIndex agents, PydanticAI, AutoGen/AG2, provider-native SDKs, and similar
  tools.
- **Harness quality systems**: deterministic evals, LLM-as-judge evals,
  trace capture, replay, CI gates, experiment comparison, and production
  observability through tools such as DeepEval, Braintrust, LangSmith, Phoenix,
  promptfoo-style checks, and custom evaluators.

The key design choice here is to make agent frameworks pluggable adapters rather
than the center of the repo.

## Folder Contents

```text
harness-engineering/
|-- README.md
|-- run_harness.py              # Framework-neutral CLI
|-- harness_contract.py         # Shared dataclasses, adapter protocol, evaluator
|-- framework_matrix.md         # When to use which framework category
|-- observability_contract.md   # Trace and artifact capture contract
|-- tasks/
|   `-- dataroom_financials.json
`-- adapters/
    |-- README.md
    |-- langgraph_adapter_sketch.py
    |-- crewai_adapter_sketch.py
    |-- pydanticai_adapter_sketch.py
    `-- semantic_kernel_adapter_sketch.py
```

The adapter sketches are intentionally dependency-free. They document where each
framework would plug into the same harness contract without forcing this repo to
install every framework.

## Run The Demo Harness

From the repo root:

```bash
python harness-engineering/run_harness.py run
python harness-engineering/run_harness.py run --framework deterministic
python harness-engineering/run_harness.py matrix
```

The deterministic adapter reads `dataroom/metrics.md`, returns a grounded answer,
evaluates it, and writes a JSON run record under `eval_runs/`.

## Harness Engineering Principles

1. **One task contract, many frameworks**: task input, expected facts, source
   requirements, and safety expectations are framework-independent.
2. **Adapters are thin**: LangGraph, CrewAI, Semantic Kernel, PydanticAI, and
   other frameworks should adapt to the harness, not redefine it.
3. **Evaluation is first-class**: every run produces a score, failed checks, and
   a machine-readable result.
4. **Observability is a contract**: traces should capture inputs, tool calls,
   artifacts, timing, model/provider metadata, and cleanup status.
5. **Reproducibility beats demos**: run records should preserve the config and
   task definition needed to replay or compare runs later.

## Suggested Expansion Path

- Add real adapters for LangGraph, CrewAI, PydanticAI, Semantic Kernel, and
  LlamaIndex behind optional extras.
- Add `compare` and `replay` CLI commands.
- Add a provider capability matrix generated from contract tests.
- Add CI gates for deterministic evals and optional integration evals behind
  secrets.
- Add LLM-as-judge evaluators while keeping deterministic checks as the baseline.
