"""Cache-Pfad-Konventionen — $XDG_CACHE_HOME/cellsim/."""

from __future__ import annotations

import os
from pathlib import Path

CACHE_SUBDIR: str = "cellsim"
PROTEOME_FILENAME: str = "proteome.tsv"
PDB_SUBDIR: str = "pdb"


def cellsim_cache_root() -> Path:
    """Gibt das Cache-Wurzelverzeichnis zurück."""
    base = os.environ.get("XDG_CACHE_HOME")
    if base:
        return Path(base) / CACHE_SUBDIR
    return Path.home() / ".cache" / CACHE_SUBDIR


def proteome_path(cache_root: Path | None = None) -> Path:
    """Pfad zur gecachten UniProt-Proteom-TSV."""
    root = cache_root or cellsim_cache_root()
    return root / PROTEOME_FILENAME


def pdb_dir(cache_root: Path | None = None) -> Path:
    """Verzeichnis für gecachte PDB-Dateien (eine Datei pro UniProt-ID)."""
    root = cache_root or cellsim_cache_root()
    return root / PDB_SUBDIR


def volumes_csv_path(out_dir: Path) -> Path:
    """Zielpfad für die Volumen-Tabelle (Output des Cache-Builds)."""
    return out_dir / "volumes.tsv"


def ensure_cache_dirs(cache_root: Path | None = None) -> Path:
    """Legt Cache-Verzeichnisse an, gibt Root zurück."""
    root = cache_root or cellsim_cache_root()
    root.mkdir(parents=True, exist_ok=True)
    pdb_dir(root).mkdir(parents=True, exist_ok=True)
    return root
