"""Typed configuration loaded from YAML files in configs/."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
DEFAULT_BASE = CONFIG_DIR / "base.yaml"
DEFAULT_MODELS = CONFIG_DIR / "models.yaml"


class PathsConfig(BaseModel):
    raw_dir: Path = Path("data/raw")
    interim_dir: Path = Path("data/interim")
    processed_dir: Path = Path("data/processed")
    eval_dir: Path = Path("data/eval")
    manifest: Path = Path("data/manifest.csv")


class ChunkingConfig(BaseModel):
    strategy: Literal["fixed", "structure"] = "structure"
    chunk_size_tokens: int = Field(512, ge=64, le=2048)
    overlap_tokens: int = Field(64, ge=0)

    @model_validator(mode="after")
    def _overlap_smaller_than_chunk(self) -> ChunkingConfig:
        if self.overlap_tokens >= self.chunk_size_tokens:
            raise ValueError("overlap_tokens must be smaller than chunk_size_tokens")
        return self


class RetrievalConfig(BaseModel):
    mode: Literal["dense", "bm25", "hybrid"] = "dense"
    top_k: int = Field(5, ge=1, le=100)
    rerank: bool = False
    rerank_candidates: int = Field(20, ge=1, le=200)

    @model_validator(mode="after")
    def _candidates_cover_top_k(self) -> RetrievalConfig:
        if self.rerank and self.rerank_candidates < self.top_k:
            raise ValueError("rerank_candidates must be >= top_k when reranking")
        return self


class ScraperConfig(BaseModel):
    user_agent: str = "RBIQA-research/0.1 (academic project)"
    requests_per_second: float = Field(0.5, gt=0, le=2.0)
    timeout_seconds: int = Field(30, ge=5)


class ModelsConfig(BaseModel):
    embedder: str = "BAAI/bge-m3"
    reranker: str | None = None
    llm_provider: Literal["gemini", "ollama"] = "gemini"
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = Field(0.0, ge=0.0, le=2.0)


class AppConfig(BaseModel):
    project_name: str = "rbiqa"
    entity_types: list[str] = Field(default_factory=lambda: ["NBFC", "Payments Banks"])
    paths: PathsConfig = Field(default_factory=PathsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else PROJECT_ROOT / path


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(
        base_path: Path = DEFAULT_BASE,
        models_path: Path = DEFAULT_MODELS,
        overrides: Path | None = None,
        ) -> AppConfig:
    data = _read_yaml(base_path)
    data["models"] = _read_yaml(models_path).get("models", {})
    if overrides is not None:
        data = _deep_merge(data, _read_yaml(overrides))
    return AppConfig.model_validate(data)