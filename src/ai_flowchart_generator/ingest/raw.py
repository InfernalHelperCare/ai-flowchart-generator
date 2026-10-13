"""Container for ingested source before extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SourceKind = Literal["markdown", "code", "notes", "mermaid", "graphviz"]


@dataclass(slots=True, frozen=True)
class RawSource:
    kind: SourceKind
    text: str
    origin: str
    line_count: int

    @property
    def is_large(self) -> bool:
        return self.line_count > 2000