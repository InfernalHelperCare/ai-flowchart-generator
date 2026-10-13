"""Heuristic source-format detection. No LLM, no I/O beyond the text.

Order matters: mermaid and graphviz are checked first because their
headers are unambiguous. Markdown vs notes is decided by heading density.
Code is the fallback for anything that looks like source.
"""

from __future__ import annotations

import re

from ai_flowchart_generator.ingest.raw import SourceKind

_MERMAID_HEAD = re.compile(r"^\s*(flowchart|graph)\s+(TD|LR|BT|RL)\b", re.MULTILINE)
_GRAPHVIZ_HEAD = re.compile(r"^\s*(strict\s+)?(di)?graph\b", re.MULTILINE)
_MD_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_CODE_HINT = re.compile(
    r"^\s*(def |class |function |public |private |#include|import |using )", re.MULTILINE
)


def detect(text: str) -> SourceKind:
    if _MERMAID_HEAD.search(text):
        return "mermaid"
    if _GRAPHVIZ_HEAD.search(text):
        return "graphviz"
    headings = len(_MD_HEADING.findall(text))
    if headings >= 2:
        return "markdown"
    if _CODE_HINT.search(text):
        return "code"
    return "notes"