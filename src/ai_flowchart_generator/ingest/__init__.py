"""Source ingestion: read bytes, detect format, produce a RawSource."""

from ai_flowchart_generator.ingest.dispatch import ingest
from ai_flowchart_generator.ingest.raw import RawSource, SourceKind

__all__ = ["ingest", "RawSource", "SourceKind"]