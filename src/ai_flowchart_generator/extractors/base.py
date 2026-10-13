"""Extractor protocol. Implementations take a RawSource, an LLM backend,
and the app config, and return a FlowGraph.

Contract:
- Must never mutate the RawSource.
- Must raise `ExtractionError` on unrecoverable parse failures.
- Should degrade gracefully: a spec that's half-parseable still yields a
  graph, with a `note` node explaining the failure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ai_flowchart_generator.config.schema import AppConfig
from ai_flowchart_generator.core.graph import FlowGraph
from ai_flowchart_generator.ingest.raw import RawSource
from ai_flowchart_generator.services.llm.base import LLMBackend


class ExtractionError(RuntimeError):
    pass


class BaseExtractor(ABC):
    kind: str = "base"

    @abstractmethod
    def extract(self, src: RawSource, backend: LLMBackend, cfg: AppConfig) -> FlowGraph:
        ...