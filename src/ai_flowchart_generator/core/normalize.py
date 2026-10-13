"""Graph normalization passes run between extraction and rendering.

Passes (in order):
    1. clamp_label  — truncate labels longer than max_label_len
    2. collapse_duplicates — merge nodes with identical (kind, label)
    3. drop_dangling — remove edges whose endpoints don't exist
    4. autolink_orphans — optionally chain orphan nodes in insertion order

All passes are pure: input graph is mutated in place and returned.
"""

from __future__ import annotations

from ai_flowchart_generator.config.schema import NormalizeConfig
from ai_flowchart_generator.core.graph import FlowEdge, FlowGraph, FlowNode


def _clamp(graph: FlowGraph, max_len: int) -> None:
    for node in graph.nodes:
        if len(node.label) > max_len:
            node.label = node.label[: max_len - 1].rstrip() + "…"


def _collapse(graph: FlowGraph, *, enabled: bool) -> None:
    if not enabled:
        return
    seen: dict[tuple[str, str], str] = {}
    remap: dict[str, str] = {}
    kept: list[FlowNode] = []
    for node in graph.nodes:
        key = (node.kind, node.label)
        if key in seen:
            remap[node.id] = seen[key]
        else:
            seen[key] = node.id
            kept.append(node)
    graph.nodes = kept
    for edge in graph.edges:
        edge.source = remap.get(edge.source, edge.source)
        edge.target = remap.get(edge.target, edge.target)


def _drop_dangling(graph: FlowGraph, *, enabled: bool) -> None:
    if not enabled:
        return
    live = {n.id for n in graph.nodes}
    graph.edges = [e for e in graph.edges if e.source in live and e.target in live]


def _autolink_orphans(graph: FlowGraph, *, enabled: bool) -> None:
    if not enabled:
        return
    touched: set[str] = set()
    for edge in graph.edges:
        touched.add(edge.source)
        touched.add(edge.target)
    orphans = [n for n in graph.nodes if n.id not in touched]
    for prev, nxt in zip(orphans, orphans[1:]):
        graph.edges.append(FlowEdge(source=prev.id, target=nxt.id, style="dotted"))


def normalize(graph: FlowGraph, *, cfg: NormalizeConfig) -> FlowGraph:
    _clamp(graph, cfg.max_label_len)
    _collapse(graph, enabled=cfg.collapse_duplicate_labels)
    _drop_dangling(graph, enabled=cfg.drop_dangling_edges)
    _autolink_orphans(graph, enabled=cfg.autolink_orphans)
    return graph