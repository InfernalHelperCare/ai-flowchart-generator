"""TOML config loader with layered merge.

Search order (later wins):
    1. package defaults (schema.py defaults)
    2. ./config/default.toml, if present
    3. ~/.config/ai-flowchart-generator/config.toml
    4. --config <path>
Env override: AIFLOW_<SECTION>__<FIELD> e.g. AIFLOW_LLM__MODEL=gpt-4o
"""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ai_flowchart_generator.config.schema import AppConfig


class ConfigError(RuntimeError):
    pass


def _deep_merge(dst: dict[str, Any], src: dict[str, Any]) -> dict[str, Any]:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc


def _env_overrides() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, val in os.environ.items():
        if not key.startswith("AIFLOW_"):
            continue
        _, _, rest = key.partition("AIFLOW_")
        if "__" not in rest:
            continue
        section, _, field = rest.partition("__")
        out.setdefault(section.lower(), {})[field.lower()] = _coerce(val)
    return out


def _coerce(val: str) -> Any:
    low = val.lower()
    if low in {"true", "false"}:
        return low == "true"
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        return val


def load_config(explicit: Path | None = None) -> AppConfig:
    merged: dict[str, Any] = {}

    bundled = Path(__file__).resolve().parent / "default.toml"
    if bundled.exists():
        _deep_merge(merged, _read_toml(bundled))

    user = Path.home() / ".config" / "ai-flowchart-generator" / "config.toml"
    if user.exists():
        _deep_merge(merged, _read_toml(user))

    if explicit is not None:
        if not explicit.exists():
            raise ConfigError(f"config file not found: {explicit}")
        _deep_merge(merged, _read_toml(explicit))

    _deep_merge(merged, _env_overrides())

    try:
        return AppConfig.model_validate(merged)
    except ValidationError as exc:
        print(f"config validation failed:\n{exc}", file=sys.stderr)
        raise ConfigError("see validation errors above") from exc