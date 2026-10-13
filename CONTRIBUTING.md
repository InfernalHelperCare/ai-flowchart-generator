# Contributing to ai-flowchart-generator

Thanks for wanting to help build the flowchart engine. This repo is a
modular Python toolkit that turns natural-language specs, code, and
structured notes into rendered flowcharts (Mermaid / Graphviz / SVG / PNG).

## Ground rules

- Python 3.11+ required. We target 3.11 and 3.12 in CI.
- Every new node type lives under `src/ai_flowchart_generator/nodes/`.
- Every new renderer lives under `src/ai_flowchart_generator/renderers/`.
- No new runtime dependency without a note in `pyproject.toml` and a
  short paragraph in the PR description explaining why stdlib can't do it.
- Type hints are mandatory on all public functions. We run `mypy --strict`
  on `src/ai_flowchart_generator/core/`.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Running tests

```bash
pytest -q
pytest --cov=ai_flowchart_generator tests/
```

## Adding a node type

1. Subclass `BaseNode` from `nodes.base`.
2. Declare `node_kind`, `required_fields`, and `optional_fields`.
3. Implement `to_mermaid()` and `to_graphviz()`.
4. Register it in `nodes.registry.NODE_REGISTRY`.
5. Add a fixture under `tests/fixtures/nodes/` and one round-trip test.

## Adding an LLM backend

The pipeline is backend-agnostic. Implement the `LLMBackend` protocol in
`services/llm/`. Ship a deterministic `MockBackend` alongside so tests
don't require network access.

## Commit style

Conventional commits. `feat(nodes): add parallel-gateway node`,
`fix(renderers): escape label colons in graphviz output`.

## Code of conduct

Be useful. Ship code. Leave the drama in the issues you don't open.