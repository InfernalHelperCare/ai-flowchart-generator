"""Read a source path and return a RawSource. Directory sources are
walked and concatenated with `# FILE: <path>` separators so downstream
extractors can attribute nodes back to files.
"""

from __future__ import annotations

from pathlib import Path

from ai_flowchart_generator.ingest.detect import detect
from ai_flowchart_generator.ingest.raw import RawSource

_TEXT_SUFFIXES = {".md", ".txt", ".mmd", ".dot", ".gv"}
_CODE_SUFFIXES = {
    ".py", ".cpp", ".cc", ".hpp", ".h", ".cs", ".java",
    ".js", ".ts", ".rs", ".go",
}
_MAX_FILE_BYTES = 2 * 1024 * 1024


def _read_file(p: Path) -> str:
    size = p.stat().st_size
    if size > _MAX_FILE_BYTES:
        raise OSError(f"{p} exceeds {_MAX_FILE_BYTES} byte limit ({size})")
    return p.read_text(encoding="utf-8", errors="replace")


def _walk_dir(root: Path) -> tuple[str, int]:
    parts: list[str] = []
    lines = 0
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix not in _TEXT_SUFFIXES | _CODE_SUFFIXES:
            continue
        if any(seg.startswith(".") for seg in p.parts):
            continue
        try:
            body = _read_file(p)
        except OSError:
            continue
        parts.append(f"# FILE: {p.relative_to(root)}\n{body}")
        lines += body.count("\n") + 1
    return "\n\n".join(parts), lines


def ingest(source: Path, *, from_code: bool = False) -> RawSource:
    if source.is_dir():
        text, lines = _walk_dir(source)
        kind = "code" if from_code else detect(text)
        return RawSource(kind=kind, text=text, origin=str(source), line_count=lines)

    text = _read_file(source)
    lines = text.count("\n") + 1
    kind = "code" if from_code else detect(text)
    return RawSource(kind=kind, text=text, origin=str(source), line_count=lines)