"""Command-line entry point. Each pipeline phase adds commands here."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from rbiqa import __version__
from rbiqa.config import PROJECT_ROOT, load_config
from rbiqa.logging_utils import setup_logging

app = typer.Typer(
    help="RBIQA: grounded Q&A over RBI regulatory directions.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def _root() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    setup_logging()


@app.command()
def version() -> None:
    console.print(f"rbiqa {__version__}")


@app.command("show-config")
def show_config(
        override: Path | None = typer.Option(None, help="Optional experiment YAML to merge."),
        ) -> None:
    cfg = load_config(overrides=override)
    console.print_json(json.dumps(cfg.model_dump(mode="json"), indent=2))


@app.command()
def init() -> None:
    cfg = load_config()
    targets = [
        cfg.resolve(cfg.paths.raw_dir),
        cfg.resolve(cfg.paths.interim_dir),
        cfg.resolve(cfg.paths.processed_dir),
        cfg.resolve(cfg.paths.eval_dir),
        cfg.resolve(cfg.paths.manifest).parent,
    ]
    for directory in targets:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").touch(exist_ok=True)
    console.print(f"[green]Created {len(targets)} data directories under {cfg.resolve(Path('data'))}")


@app.command()
def check() -> None:
    cfg = load_config()
    data_dirs = [
        cfg.resolve(cfg.paths.raw_dir),
        cfg.resolve(cfg.paths.interim_dir),
        cfg.resolve(cfg.paths.processed_dir),
        cfg.resolve(cfg.paths.eval_dir),
    ]
    rows: list[tuple[str, bool, str]] = [
        ("Python >= 3.11", sys.version_info >= (3, 11), sys.version.split()[0]),
        ("Config loads", True, cfg.project_name),
        ("Data directories exist", all(d.is_dir() for d in data_dirs), "run: make init"),
        (
            "nvidia-smi on PATH (GPU driver visible in WSL)",
            shutil.which("nvidia-smi") is not None,
            "optional until Phase 3",
        ),
    ]
    if cfg.models.llm_provider == "gemini":
        rows.append(("GEMINI_API_KEY set", bool(os.getenv("GEMINI_API_KEY")), "value hidden"))

    table = Table(title="RBIQA environment check")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    for name, ok, detail in rows:
        table.add_row(name, "[green]OK" if ok else "[yellow]MISSING", detail)
    console.print(table)


if __name__ == "__main__":
    app()