# OpenPalm Agent Framework

Production-grade systems so any agent or model has what it needs with minimal tokens.

## Components

| Module | Purpose |
|--------|---------|
| `core/agent.py` | Loop: ingest → retrieve → prompt → generate → tool → verify |
| `core/token_manager.py` | Budget, estimate, compress, pack messages |
| `memory/store.py` | Working / episodic / semantic memory with selective retrieval |
| `tools/registry.py` | Tool registration, caching, output compression |
| `tools/defaults.py` | calculator, summarize, search_memory |
| `pipelines/` | preprocess (tight context) and postprocess (grounding gate) |
| `observability/tracker.py` | Step and token accounting |

## Usage

```python
from harness_sidecar.framework.run import run_agent

result = run_agent(
    "What is 2140 / 4?",
    sources=["The home is 2,140 sqft with 4 bedrooms."],
)
print(result["draft"])
print(result["stats"])  # tokens_in, tokens_out, steps
```

## Design goals

- **Token efficiency** — compress context, drop old messages, cache tool results
- **Any model** — only needs a `generate(prompt, model) -> str` function
- **Grounding** — claims are checked against sources before copy is allowed
- **Observability** — every step reports token cost so you can tune

## Extending

Register a tool:

```python
agent.tools.register("my_tool", lambda arg: f"result for {arg}")
```

Swap memory backend by subclassing `MemoryStore` and overriding `retrieve`.

## Skills

Skills live in `skills/packs/` as markdown or Python.

```python
from harness_sidecar.framework.run import run_agent

result = run_agent(
    "Write a short description.",
    sources=["4 bed, 2.5 bath, 2140 sqft."],
    active_skills=["writing", "compliance"],
)
```

Available: writing, analysis, compliance, research.

## Tools

Built-in tools (auto-registered):

- calculator, summarize, search_memory
- datetime, list_ops, dict_lookup, word_count, extract_numbers

## Evaluation

```python
from harness_sidecar.framework import evaluate
print(evaluate(result))
# {'grounding': 1.0, 'brevity': 1.0, 'tokens': 190, 'unsupported': 0}
```

## Specialist Models

Purpose-built adapters for domain tasks. Each has a system prompt, validation, and fallback.

| Name | Domain |
|------|--------|
| linter, coder | code |
| spellcheck, translate | language |
| designer, cad | design |
| math | math |
| science | science |
| music, art | creative |
| tooluse | agent |

```python
from harness_sidecar.framework.models.router import ModelRouter
from harness_sidecar.inference.client import generate

router = ModelRouter(generate)
print(router.run("math", "2+2"))
```

API: `GET /models`, `POST /specialist/{name}`

## Protocols

- **MCP** — `MCPBridge` exposes tools and specialists
- **ACP** — `ACPHandler` supports `session/new`, `session/prompt`, `session/cancel`

API: `POST /acp`

## CLI

```bash
python -m harness_sidecar.cli chat "your message"
python -m harness_sidecar.cli specialist math "2+2"
python -m harness_sidecar.cli tools
python -m harness_sidecar.cli snapshot list
```

## Resilience

- **Snapshots** — atomic write via temp+rename (`SnapshotStore`)
- **Parallel states** — 3 slots with failover (`StateManager`)
- **Self-healing** — failover → snapshot → deterministic stub (`SelfHealer`)
- **Hot reload** — `HotReloader` watches and reloads modules

API: `GET /snapshots`, `POST /snapshot`

## ML Generation System

### Pipeline
```python
from harness_sidecar.framework.ml.pipeline.builder import ModelBuilder, ModelSpec
b = ModelBuilder()
b.build(ModelSpec("demo", "math", "Solve step by step."))
b.train("demo", epochs=2)
```

### Designer (drag-and-drop + code)
```python
from harness_sidecar.framework.ml.designer.graph import ModelGraph, Node
g = ModelGraph("tiny")
g.add_node(Node("in", "input"))
g.add_node(Node("out", "output"))
g.add_edge("in", "out")
print(g.to_json())   # for UI
print(g.to_code())   # for code editor
print(g.validate())
```

### Telemetry & Feedback
- `ThoughtStream` emits stage events (route, generate, tool, etc.)
- `FeedbackStore` collects ratings for model improvement
- `render_text` / `render_json` for visualization

### RAMA (Router And Model Architecture)
Local micro-router + MoE/MoA:
```python
from harness_sidecar.framework.ml.rama.router import RAMA
from harness_sidecar.inference.client import generate

rama = RAMA(generate)
rama.run("calculate 2+2", mode="auto")   # routes to math
rama.run("hello", mode="local")          # micro LM
rama.run("complex", mode="moe")          # mixture of experts
rama.register_agent("writer", lambda p: "...")
rama.run("task", mode="moa")             # mixture of agents
rama.train_route("lint this", "linter")  # learn routing
```

API: `POST /rama`, `POST /ml/build`, `POST /ml/train`, `GET /telemetry`
