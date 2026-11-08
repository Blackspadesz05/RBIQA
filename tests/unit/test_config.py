from pathlib import Path

import pytest
from pydantic import ValidationError

from rbiqa.config import ChunkingConfig, RetrievalConfig, _deep_merge, load_config


def test_default_config_loads() -> None:
    cfg = load_config()
    assert cfg.project_name == "rbiqa"
    assert "NBFC" in cfg.entity_types
    assert "Payments Banks" in cfg.entity_types


def test_overlap_must_be_smaller_than_chunk() -> None:
    with pytest.raises(ValidationError):
        ChunkingConfig(chunk_size_tokens=128, overlap_tokens=128)


def test_rerank_candidates_must_cover_top_k() -> None:
    with pytest.raises(ValidationError):
        RetrievalConfig(mode="dense", top_k=10, rerank=True, rerank_candidates=5)


def test_deep_merge_overrides_only_given_keys() -> None:
    base = {"retrieval": {"mode": "dense", "top_k": 5}}
    merged = _deep_merge(base, {"retrieval": {"mode": "hybrid"}})
    assert merged == {"retrieval": {"mode": "hybrid", "top_k": 5}}


def test_resolve_makes_relative_paths_absolute() -> None:
    cfg = load_config()
    resolved = cfg.resolve(Path("data/raw"))
    assert resolved.is_absolute()
    assert resolved.parts[-2:] == ("data", "raw")