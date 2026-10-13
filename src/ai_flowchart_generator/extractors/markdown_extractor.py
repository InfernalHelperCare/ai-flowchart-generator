"""Markdown -> FlowGraph.

Heuristic: each `## Heading` becomes a process node. Ordered-list items
under a heading become children chained by solid edges. The LLM backend
is consulted only when `extract.mode == "llm"` or when the heuristic
yields fewer than two nodes (hybrid fallback).
"""

from __future__ import annotations

import re

from ai_flowchart_generator.config.schema import AppConfig
from ai_flowchart_generator.core.graph import FlowEdge, FlowGraph, FlowNode
from ai_flowchart_generator.extractors.base import BaseExtractor
from ai_flowchart_generator.ingest.raw import RawSource
from ai_flowchart_generator.services.llm