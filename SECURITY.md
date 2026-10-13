# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Open a private security advisory on GitHub, or email
`security@ai-flowchart-generator.dev`. Do **not** open a public issue for
an unpatched vulnerability. We aim to respond within 72 hours and to ship
a patched release within 14 days for high-severity issues.

## Threat model

`ai-flowchart-generator` is a **local desktop tool**. It parses user
input and renders diagrams. The relevant attack surface:

- **Parser inputs.** Mermaid / Graphviz / free-text specs are parsed by
  our own tokenizer. Malformed input must never cause arbitrary code
  execution. We do not `eval` and we do not shell out to `dot` with
  unsanitized arguments.
- **Renderer outputs.** SVG exporters strip `<script>` and `on*=` event
  handlers by default. Set `render.allow_inline_scripts = true` only if
  you trust every spec file in the working directory.
- **LLM backends.** API keys are read from environment variables or
  `config/secrets.toml` (gitignored). Never commit keys. The HTTP client
  has a 30s timeout and refuses non-HTTPS endpoints unless
  `llm.allow_insecure = true`.
- **Plugin loading.** Node/renderer plugins are discovered from
  `ai_flowchart_generator.plugins` entry points. Loading a plugin runs
  its code. Only install plugins you trust.

## Hardening recommendations

- Run with a dedicated low-privilege user on shared machines.
- Keep `render.allow_inline_scripts` off unless you need it.
- Pin dependency hashes via `pip-compile --generate-hashes`.

## Out of scope

Denial of service via absurdly large graphs is acknowledged but not
patched — cap `pipeline.max_nodes` in config if you care.