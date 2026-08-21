"""Asakura-Oosawa-Depletion-Kopplung (L2↔L3-Brücke).

Berechnet Depletion-Kräfte zwischen großen Makromolekülen
in Anwesenheit kleinerer Crowder-Moleküle. Klassisches AO-Potenzial:

    U_AO(r) = -Π_c · v_ex(r)         für r < R_i + R_j
              0                       sonst

Π_c = osmotischer Druck der Crowder (ideal: n_c · k_B · T)
v_ex = Überlappungsvolumen der excluded-volume-Hüllen

VECTOR_BRIDGE_L2_L3: dies ist die direkte Brücke zwischen der
L2-physikalischen Schicht (A-O-Theorie) und der L3-numerischen
Schicht (RDME-Gitter).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np

from cellsim.core.constants import BOLTZMANN

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AOParams:
    """Parameter für Asakura-Oosawa-Depletion."""

    temperature_K: float = 310.0   # physiologisch ~37 °C
    crowder_concentration_mM: float = 50.0   # ~Cytosol
    crowder_radius_nm: float = 0.5           # typische kleine Moleküle

    @property
    def osmotic_pressure_pa(self) -> float:
        """Ideal osmotischer Druck Π = n · k_B · T in Pascal."""
        # 1 mM = 1 mol/m³ (für wässrige Lösungen)
        n_per_m3 = self.crowder_concentration_mM * 1.0e3  # mol/m³
        return n_per_m3 * BOLTZMANN * self.temperature_K


def depletion_overlap_volume(r_nm: float, r_i_nm: float, r_j_nm: float) -> float:
    """Berechnet das Überlappungsvolumen zweier Kugeln.

    Formel aus klassischer Geometrie (AO-Standard).
    r: Distanz zwischen den Schwerpunkten [nm]
    r_i, r_j: Radien der beiden Makromoleküle [nm]
    Rückgabe: v_ex in nm³.
    """
    R = r_i_nm + r_j_nm
    if r_nm >= R:
        return 0.0
    if r_nm <= abs(r_i_nm - r_j_nm):
        # Eine Kugel vollständig in der anderen
        return (4.0 / 3.0) * math.pi * min(r_i_nm, r_j_nm) ** 3
    # Standardfall: partielle Überlappung
    term = (R - r_nm) ** 2 * (r_nm ** 2 + 2 * r_nm * R - 3 * (r_i_nm - r_j_nm) ** 2 + 6 * r_i_nm * r_j_nm)
    return (math.pi * term) / (12.0 * r_nm)


@dataclass
class DepletionField:
    """Aggregiertes Depletion-Potenzial pro Voxel-Paar."""

    grid_shape: tuple[int, int, int]
    attractive_potential_nm3: np.ndarray
    osmotic_pressure_pa: float
    max_pair_force_nm3_pa: float

    @property
    def mean_potential(self) -> float:
        return float(self.attractive_potential_nm3.mean()) if self.attractive_potential_nm3.size else 0.0


def compute_depletion_field(
    crowder_counts: np.ndarray,        # [grid_shape] Anzahlen Crowder pro Voxel
    crowder_radius_nm: float = 0.5,
    macro_radius_nm: float = 5.0,       # typisches Makromolekül
    params: AOParams | None = None,
    voxel_edge_nm: float = 10.0,
) -> DepletionField:
    """Berechnet das Depletion-Potenzial-Feld auf dem RDME-Gitter.

    Vereinfachung: Wir nehmen an, dass pro Voxel die Crowder-Anzahl
    ein direktes Maß für die attraktive Kraft zwischen benachbarten
    Makromolekülen ist. v_ex wird als Überlappung zweier Kugeln mit
    Radius `macro_radius_nm` im Voxel-Mittelpunktsabstand berechnet.
    """
    params = params or AOParams(crowder_radius_nm=crowder_radius_nm)
    grid_shape = crowder_counts.shape

    # Lokales Π pro Voxel (Mole pro Voxel · k_B · T / Voxel-Volumen)
    # Voxel-Volumen in m³
    voxel_volume_m3 = (voxel_edge_nm * 1e-9) ** 3
    crowder_counts = crowder_counts.astype(np.float64)
    n_per_m3_local = crowder_counts / voxel_volume_m3
    pi_local = n_per_m3_local * BOLTZMANN * params.temperature_K

    # Effektive Paar-Distanz: zwei Makromoleküle stoßen im Voxel zusammen,
    # also typischerweise 1 Macro-Radius Abstand (Kontaktdistanz).
    pair_distance_nm = macro_radius_nm  # Kontaktabstand: r_i + r_j > r
    v_ex_pair = depletion_overlap_volume(
        r_nm=pair_distance_nm,
        r_i_nm=macro_radius_nm,
        r_j_nm=macro_radius_nm,
    )

    # attractive_potential in Einheiten, die numerisch sichtbar sind:
    # Π · v_ex · 1e30 (Skalierung für numerische Sichtbarkeit)
    # Die physikalische Aussage ist nur das Verhältnis zwischen Voxeln.
    attractive_potential_nm3 = pi_local * v_ex_pair * 1.0e30  # dimensionslos skaliert
    max_force = float(np.abs(attractive_potential_nm3).max())

    return DepletionField(
        grid_shape=grid_shape,
        attractive_potential_nm3=attractive_potential_nm3,
        osmotic_pressure_pa=float(pi_local.mean()),
        max_pair_force_nm3_pa=max_force,
    )


def ao_diffusion_modifier(
    depletion: DepletionField,
    d_bulk_nm2_per_ms: float,
    sensitivity: float = 0.5,
) -> np.ndarray:
    """Berechnet lokalen Diffusions-Koeffizienten aus Depletion-Feld.

    Erhöhte attraktive Kraft → reduzierte effektive Diffusion
    (depletionsinduzierte Cluster-Bildung).

    D_local = D_bulk · exp(-sensitivity · crowding_index)
    crowding_index = Π_local / Π_ref, wobei Π_ref = max(Π_local).
    """
    pi_local = depletion.attractive_potential_nm3
    pi_ref = float(pi_local.max()) if pi_local.size and pi_local.max() > 0 else 1.0
    crowding_index = pi_local / pi_ref
    return d_bulk_nm2_per_ms * np.exp(-sensitivity * crowding_index)
