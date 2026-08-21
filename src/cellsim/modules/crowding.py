"""Macromolecular Crowding (Asakura-Oosawa-Vorbereitung).

Berechnet pro Voxel:
- V_ex_total = Σ_i N_i · V_ex_i  (excluded volume total)
- crowding_index = V_ex_total / V_voxel  (dimensionslos, 0..1)
- D_local = D_bulk · exp(-α · crowding_index)  (lokaler Diffusions-Koeffizient)

Hinweis: volle Asakura-Oosawa-Wechselwirkung mit Co-Solutes ist
VECTOR_BRIDGE_L2_L3; diese Datei liefert nur den Crowding-Vorposten.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CrowdingParams:
    """Konstanten für Crowding-Modell."""

    alpha: float = 1.0              # Dämpfungsfaktor in exp(-α · crowding_index)
    diffusion_bulk_nm2_per_ms: float = 1.0e3   # D_bulk


@dataclass
class CrowdingField:
    """Crowding pro Voxel + lokale Diffusionskoeffizienten."""

    grid_shape: tuple[int, int, int]
    v_ex_voxel: np.ndarray = field(default_factory=lambda: np.zeros(0))     # Å³
    crowding_index: np.ndarray = field(default_factory=lambda: np.zeros(0))  # dimensionslos
    d_local_nm2_per_ms: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def mean_crowding(self) -> float:
        return float(self.crowding_index.mean()) if self.crowding_index.size else 0.0

    @property
    def std_crowding(self) -> float:
        return float(self.crowding_index.std()) if self.crowding_index.size else 0.0


def compute_crowding(
    particle_counts: dict[str, np.ndarray],   # species_id → counts[grid_shape]
    volumes_angstrom3: dict[str, float],       # species_id → V_ex
    voxel_edge_nm: float,
    params: CrowdingParams | None = None,
) -> CrowdingField:
    """Berechnet Crowding-Feld aus Partikel-Counts pro Spezies."""
    params = params or CrowdingParams()
    if not particle_counts:
        return CrowdingField(grid_shape=(1, 1, 1))

    first = next(iter(particle_counts.values()))
    grid_shape = tuple(first.shape)
    v_voxel_angstrom3 = (voxel_edge_nm * 10.0) ** 3  # nm → Å

    v_ex_total = np.zeros(grid_shape, dtype=np.float64)
    for s_id, counts in particle_counts.items():
        v_ex_i = volumes_angstrom3.get(s_id, 0.0)
        v_ex_total += counts.astype(np.float64) * v_ex_i

    crowding_index = v_ex_total / max(v_voxel_angstrom3, 1.0)
    d_local = params.diffusion_bulk_nm2_per_ms * np.exp(-params.alpha * crowding_index)

    return CrowdingField(
        grid_shape=grid_shape,
        v_ex_voxel=v_ex_total,
        crowding_index=crowding_index,
        d_local_nm2_per_ms=d_local,
    )
