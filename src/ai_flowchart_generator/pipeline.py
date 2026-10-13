"""End-to-end pipeline: source -> IR -> rendered flowchart.

Stages:
    1. ingest     — read source bytes, detect format (markdown / code / notes)
    2. extract    — LLM or rule-based extraction into a FlowGraph IR
    3. normalize  — collapse duplicate nodes, resolve dangling edges
    4. layout     — assign ranks (only for graphviz backend)
    5. render     — dispatch to the selected renderer

Concurrency: the pipeline is single-threaded per instance. For batch
jobs, create one pipeline per worker; config is immutable after load.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_flowchart_generator.config.schema import AppConfig
from ai_flowchart_generator.core.graph import FlowGraph
from ai_flowchart_generator.core.normalize import normalize
from ai_flowchart_generator.ingest.dispatch import ingest
from ai_flowchart_generator.services.llm.base import LLMBackend
from ai_flowchart_generator.services.llm.factory import build_backend
from ai_flowchart_generator.extractors.registry import get_extractor
from ai_flowchart_generator.renderers.registry import get_renderer


class PipelineError(RuntimeError):
    """Raised when any pipeline stage fails hard."""


@dataclass(slots=True, frozen=True)
class PipelineResult:
    artifact: str
    ir_json: str
    node_count: int
    edge_count: int
    backend_name: str


class FlowchartPipeline:
    def __init__(self, config: AppConfig) -> None:
        self._cfg = config
        self._backend: LLMBackend = build_backend(config.llm)

    def run(
        self,
        source: Path,
        *,
        from_code: bool = False,
        output_format: str = "mermaid",
    ) -> PipelineResult:
        try:
            raw = ingest(source, from_code=from_code)
        except OSError as exc:
            raise PipelineError(f"ingest failed: {exc}") from exc

        extractor = get_extractor(raw.kind)
        try:
            graph: FlowGraph = extractor.extract(raw, self._backend, self._cfg)
        except Exception as exc:  # noqa: BLE001 — surface as pipeline error
            raise PipelineError(f"extraction failed: {exc}") from exc

        graph = normalize(graph, cfg=self._cfg.normalize)

        if graph.node_count > self._cfg.pipeline.max_nodes:
            raise PipelineError(
                f"graph exceeds max_nodes ({graph.node_count} > {self._cfg.pipeline.max_nodes})"
            )

        renderer = get_renderer(output_format)
        artifact = renderer.render(graph, cfg=self._cfg.render)

        return PipelineResult(
            artifact=artifact,
            ir_json=json.dumps(graph.to_ir(), indent=2),
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            backend_name=self._backend.name,
        )