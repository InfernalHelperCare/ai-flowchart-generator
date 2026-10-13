"""Extractors: RawSource -> FlowGraph. One module per source kind."""

from ai_flowchart_generator.extractors.registry import get_extractor

__all__ = ["get_extractor"]