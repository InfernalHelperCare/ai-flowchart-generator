"""FlowGraph IR: the intermediate representation every extractor emits and
every renderer consumes.

Design notes:
- Stable node ids are generated from a hash of (kind, label) so repeated
  extraction of the same source is idempotent.
- Edges reference node ids, not indices. Orphaned edges are legal until
  `core.normalize` runs.
- `metadata` is a free-form dict for extractor-specific hints (e.g. rank
  hints, source line numbers). Renderers may ignore it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Literal

NodeKind = Literal[
    "start", "end", "process", "decision", "io", "subroutine", "note", "group"
]


def _stable_id(kind: str, label: str) -> str:
    digest = hashlib.blake2s(f"{kind}:{label}".encode("utf-8"), digest_size=6).hexdigest()
    return f"n_{digest}"


@dataclass(slots=True)
class FlowNode:
    kind: NodeKind
    label: str
    id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = _stable_id(self.kind, self.label)


@dataclass(slots=True)
class FlowEdge:
    source: str
    target: str
    label: str | None = None
    style: Literal["solid", "dashed", "dotted"] = "solid"

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError(f"self-loop not allowed: {self.source}")


@dataclass(slots=True)
class FlowGraph:
    nodes: list[FlowNode] = field(default_factory=list)
    edges: list[FlowEdge] = field(default_factory=list)
    title: str = "Flowchart"

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def add_node(self, node: FlowNode) -> FlowNode:
        for existing in self.nodes:
            if existing.id == node.id:
                return existing
        self.nodes.append(node)
        return node

    def add_edge(self, edge: FlowEdge) -> FlowEdge:
        if edge.source == edge.target:
            raise ValueError("self-loop rejected at graph level")
        self.edges.append(edge)
        return edge

    def to_ir(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "nodes": [
                {"id": n.id, "kind": n.kind, "label": n.label, "meta": n.metadata}
                for n in self.nodes
            ],
            "edges": [
                {"s": e.source, "t": e.target, "label": e.label, "style": e.style}
                for e in self.edges
            ],
        }