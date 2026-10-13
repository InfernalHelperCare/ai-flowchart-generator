"""Command-line entry point for ai-flowchart-generator.

Usage:
    aiflow render spec.md -o out.svg
    aiflow render --from-code ./src -o arch.mmd --format mermaid
    aiflow parse notes.txt --emit-ir

Exit codes:
    0  success
    1  parse error (malformed input)
    2  render error (backend failed)
    3  config error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_flowchart_generator.config.loader import load_config, ConfigError
from ai_flowchart_generator.pipeline import FlowchartPipeline, PipelineError


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aiflow",
        description="AI-driven flowchart generator (2026).",
    )
    p.add_argument("--config", type=Path, default=None, help="path to config.toml")
    p.add_argument("--verbose", "-v", action="count", default=0)

    sub = p.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="generate a flowchart from a source file")
    render.add_argument("source", type=Path)
    render.add_argument("-o", "--output", type=Path, default=Path("out.mmd"))
    render.add_argument(
        "--format",
        choices=["mermaid", "graphviz", "svg", "png"],
        default="mermaid",
    )
    render.add_argument("--from-code", action="store_true", help="treat source as a code tree")
    render.add_argument("--emit-ir", action="store_true", help="dump intermediate IR as JSON")

    sub.add_parser("doctor", help="check backend availability and config sanity")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 3

    if args.command == "doctor":
        from ai_flowchart_generator.services.doctor import run_doctor

        return run_doctor(cfg)

    if args.command == "render":
        if not args.source.exists():
            print(f"source not found: {args.source}", file=sys.stderr)
            return 1

        try:
            pipe = FlowchartPipeline(cfg)
            result = pipe.run(
                source=args.source,
                from_code=args.from_code,
                output_format=args.format,
            )
        except PipelineError as exc:
            print(f"pipeline error: {exc}", file=sys.stderr)
            return 2

        args.output.write_text(result.artifact, encoding="utf-8")
        if args.emit_ir:
            ir_path = args.output.with_suffix(".ir.json")
            ir_path.write_text(result.ir_json, encoding="utf-8")
            print(f"wrote {ir_path}")
        print(f"wrote {args.output} ({len(result.artifact)} bytes, {result.node_count} nodes)")
        return 0

    return 3


if __name__ == "__main__":
    sys.exit(main())