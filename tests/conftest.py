"""Geteilte Test-Fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from cellsim.core.constants import SEED_BASE


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Jeder Test bekommt sein eigenes Cache-Verzeichnis."""
    cache_root = tmp_path / "cache"
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache_root))


@pytest.fixture
def seed_base() -> int:
    """Zentraler Seed für deterministische Tests."""
    return SEED_BASE


@pytest.fixture
def sample_pdb_text() -> str:
    """Mini-PDB mit 3 CA-Atomen."""
    return (
        "HEADER    SAMPLE                               01-JAN-00   SAMP\n"
        "ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 70.00           C\n"
        "ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00 80.00           C\n"
        "ATOM      3  CA  ALA A   3       7.600   0.000   0.000  1.00 90.00           C\n"
        "END\n"
    )
