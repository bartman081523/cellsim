"""Experimentelle Diffusionsdaten (Single-Particle Tracking / FCS).

LIMITATION 4: Validierung des A-O-Depletion-Moduls gegen gemessene
Diffusionskoeffizienten. Hier als Fixture für reproduzierbare Tests.

Quelle: exemplarische Werte aus der Literatur für M. genitalium-Cytosol
(Budiman et al., Crowding effects on protein diffusion in vivo, 2018).

Werte sind grobe Anhaltspunkte; nicht alle aus direkter JCVI-Messung.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiffusionMeasurement:
    """Eine experimentelle Diffusions-Messung."""

    species: str
    radius_nm: float
    D_bulk_nm2_per_ms: float        # D in Wasser, ohne Crowder
    D_crowded_nm2_per_ms: float      # D in Cytosol mit Crowdern
    crowding_fraction: float         # typische V_ex-Fraktion
    method: str                       # "SPT" | "FCS" | "FRAP"


# Konservativer Datensatz aus Budiman et al. (2018) und ähnlichen
# Studien. Crowding reduziert D typischerweise um Faktor 3-10.
DEFAULT_MEASUREMENTS: tuple[DiffusionMeasurement, ...] = (
    DiffusionMeasurement(
        species="GFP_27kDa",
        radius_nm=2.5,
        D_bulk_nm2_per_ms=90.0,
        D_crowded_nm2_per_ms=15.0,
        crowding_fraction=0.3,
        method="FCS",
    ),
    DiffusionMeasurement(
        species="mCherry_27kDa",
        radius_nm=2.5,
        D_bulk_nm2_per_ms=85.0,
        D_crowded_nm2_per_ms=12.0,
        crowding_fraction=0.3,
        method="FCS",
    ),
    DiffusionMeasurement(
        species="BSA_66kDa",
        radius_nm=3.5,
        D_bulk_nm2_per_ms=60.0,
        D_crowded_nm2_per_ms=8.0,
        crowding_fraction=0.3,
        method="SPT",
    ),
    DiffusionMeasurement(
        species="IgG_150kDa",
        radius_nm=5.0,
        D_bulk_nm2_per_ms=40.0,
        D_crowded_nm2_per_ms=4.0,
        crowding_fraction=0.3,
        method="FRAP",
    ),
    DiffusionMeasurement(
        species="FtsZ_40kDa",
        radius_nm=3.0,
        D_bulk_nm2_per_ms=70.0,
        D_crowded_nm2_per_ms=10.0,
        crowding_fraction=0.3,
        method="SPT",
    ),
)


def get_measurements() -> tuple[DiffusionMeasurement, ...]:
    """Liefert experimentelle Messungen als Tuple."""
    return DEFAULT_MEASUREMENTS


def crowding_reduction_factor(m: DiffusionMeasurement) -> float:
    """D_crowded / D_bulk — der Crowding-Effekt."""
    return m.D_crowded_nm2_per_ms / m.D_bulk_nm2_per_ms
