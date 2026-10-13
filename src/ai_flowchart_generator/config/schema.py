"""Typed configuration schema. All fields have defaults; user config
overrides via merged TOML. Validation runs at load time, not at use time.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    backend: str = Field(default="mock", description="mock | openai | anthropic | local")
    model: str = "gpt-4o-mini"
    endpoint: str | None = None
    api_key_env: str = "AIFLOW_API_KEY"
    timeout_s: float = Field(default=30.0, ge=1.0, le=300.0)
    allow_insecure: bool = False
    max_tokens: int = Field(default=2048, ge=64, le=32768)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class ExtractConfig(BaseModel):
    mode: str = Field(default="hybrid", description="rules | llm | hybrid")
    chunk_lines: int = Field(default=400, ge=50, le=4000)
    max_depth: int = Field(default=12, ge=1, le=64)


class NormalizeConfig(BaseModel):
    collapse_duplicate_labels: bool = True
    drop_dangling_edges: bool = True
    autolink_orphans: bool = False
    max_label_len: int = Field(default=64, ge=8, le=512)


class RenderConfig(BaseModel):
    theme: str = "default"
    direction: str = Field(default="TD", pattern="^(TD|LR|BT|RL)$")
    allow_inline_scripts: bool = False
    font_family: str = "Inter"


class PipelineConfig(BaseModel):
    max_nodes: int = Field(default=5000, ge=1)
    max_edges: int = Field(default=20000, ge=1)
    cache_dir: str = ".ai_flowchart_cache"


class AppConfig(BaseModel):
    llm: LLMConfig = LLMConfig()
    extract: ExtractConfig = ExtractConfig()
    normalize: NormalizeConfig = NormalizeConfig()
    render: RenderConfig = RenderConfig()
    pipeline: PipelineConfig = PipelineConfig()