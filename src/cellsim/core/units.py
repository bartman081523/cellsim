"""Einheiten-Konventionen (Suffix-Spalten aus MT_Sim)."""

from __future__ import annotations

from typing import Final

NM_PER_M: Final[float] = 1e9
S_PER_MS: Final[float] = 1e-3
M_PER_S_PER_D: Final[float] = 1e-9  # Diffusion in m²/s; nm²/ms ist handlicher
NM2_PER_MS: Final[float] = 1.0      # D [nm²/ms] ist unsere Konvention

# Einheiten-Suffixe für CSV-Spalten
UNIT_NM: Final[str] = "_nm"
UNIT_A: Final[str] = "_A"
UNIT_A3: Final[str] = "_A3"
UNIT_S: Final[str] = "_s"
UNIT_MS: Final[str] = "_ms"
UNIT_MM: Final[float] = 1e-3  # für Konzentrationen


def angstrom_to_nm(angstrom: float) -> float:
    """1 Å = 0.1 nm."""
    return angstrom * 0.1


def nm3_to_a3(nm3: float) -> float:
    """1 nm³ = 1000 Å³."""
    return nm3 * 1000.0
