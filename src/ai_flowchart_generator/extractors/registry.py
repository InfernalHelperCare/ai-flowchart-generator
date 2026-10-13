"""Maps a SourceKind to its extractor class. Extractors are stateless;
a fresh instance is returned per call so they can't leak state between
pipeline runs.
"""

from __future__ import annotations

from ai_flowchart_generator.extractors.base import BaseExtractor
from ai_flowchart_generator.extractors.code_extractor import CodeExtractor
from ai_flowchart_generator.extractors.markdown_extractor import MarkdownExtractor
from ai_flowchart_generator.extractors.notes_extractor import NotesExtractor
from ai_flowchart_generator.ingest.raw import SourceKind

_TABLE: dict[SourceKind, type[BaseExtractor]] = {
    "markdown": MarkdownExtractor,
    "code": CodeExtractor,
    "notes": NotesExtractor,
    "mermaid": MarkdownExtractor,   # mermaid is re-parsed, not generated
    "graphviz": MarkdownExtractor,
}


class UnknownSourceKind(KeyError):
    pass


def get_extractor(kind: SourceKind) -> BaseExtractor:
    try:
        cls = _TABLE[kind]
    except KeyError as exc:
        raise UnknownSourceKind(f"no extractor registered for kind={kind!r}") from exc
    return cls()