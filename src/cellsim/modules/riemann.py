"""Riemannsche Geometrie für DNA-Konfigurationsraum (L4).

Konfigurationsraum der DNA als dynamische Riemannsche Mannigfaltigkeit.
Torsionsstress und Supercoiling als Krümmung des Raums statt als
mechanische Federkräfte. Architekturtext §6.2.

VECTOR_RIEMANN_DNA: Riemann-Formulierung vs. klassisches Bead-Spring.

Diese Implementierung ist eine sehr vereinfachte Variante:
- 1D-Polymermannigfaltigkeit mit lokaler Krümmung κ(s) entlang der Konturlänge
- Vergleich gegen harmonische Federkraft F = -k · (x - x_0)
- Ziel: zeigen, dass eine Riemannsche Formulierung numerisch stabiler ist
  bei extremer Torsion als klassisches Bead-Spring.

Konsultiere `cellsim/modules/chromosome.py` für den Bead-Spring-Stub.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RiemannParams:
    """Parameter der Riemannschen DNA-Mannigfaltigkeit."""

    n_beads: int = 50
    contour_length_nm: float = 250.0     # 543 kbp × 0.34 nm/bp / 2 ≈ 90 nm gepackt
    packing_ratio: float = 50.0          # typisch für Bakterienchromosom
    torsion_persistence_nm: float = 50.0 # Persistenzlänge für DNA
    crowder_density: float = 0.3         # V_ex_fraction


@dataclass
class RiemannManifold:
    """1D-Polymermannigfaltigkeit entlang DNA-Konturlänge."""

    s: np.ndarray                    # Konturlänge [0, L]
    r: np.ndarray                    # 3D-Position pro Bead
    metric_g: np.ndarray             # 1D-Metrik g(s) = 1 (isotrop)
    curvature_kappa: np.ndarray      # Krümmung κ(s)
    torsion_tau: np.ndarray          # Torsion τ(s)
    riemann_tensor_components: float  # Skalar: R^ρ_σμν (1D = 0 für isotrop)
    step_count: int = 0

    @property
    def mean_curvature(self) -> float:
        return float(self.curvature_kappa.mean()) if self.curvature_kappa.size else 0.0

    @property
    def max_curvature(self) -> float:
        return float(self.curvature_kappa.max()) if self.curvature_kappa.size else 0.0


def init_manifold(
    params: RiemannParams,
    initial_radius_nm: float = 100.0,
    seed: int = 42,
) -> RiemannManifold:
    """Initialisiert eine 1D-Mannigfaltigkeit mit realistischer Konformation."""
    rng = np.random.default_rng(seed)
    s = np.linspace(0.0, params.contour_length_nm, params.n_beads)
    r = np.zeros((params.n_beads, 3), dtype=np.float64)

    # Initiale Konformation: Helix um Nukleoid-Zentrum
    for i in range(params.n_beads):
        theta = i * 2 * np.pi * params.packing_ratio / params.n_beads
        r[i, 0] = initial_radius_nm * np.cos(theta)
        r[i, 1] = initial_radius_nm * np.sin(theta)
        r[i, 2] = (i - params.n_beads / 2) * 0.5
    # Kleines Rauschen
    r += rng.normal(scale=0.5, size=r.shape)

    metric_g = np.ones(params.n_beads, dtype=np.float64)
    curvature_kappa = np.zeros(params.n_beads, dtype=np.float64)
    torsion_tau = np.zeros(params.n_beads, dtype=np.float64)

    return RiemannManifold(
        s=s,
        r=r,
        metric_g=metric_g,
        curvature_kappa=curvature_kappa,
        torsion_tau=torsion_tau,
        riemann_tensor_components=0.0,
        step_count=0,
    )


def compute_curvature(manifold: RiemannManifold) -> np.ndarray:
    """Berechnet κ(s) aus der 3D-Konformation.

    κ = |r' × r''| / |r'|³   (klassische Frenet-Serret-Formel für 1D-Kurve)
    """
    r = manifold.r
    if r.shape[0] < 3:
        return np.zeros(r.shape[0])
    dr = np.gradient(r, axis=0)               # r'
    ddr = np.gradient(dr, axis=0)              # r''
    cross = np.cross(dr, ddr)                 # r' × r''
    norm_dr_cubed = (np.linalg.norm(dr, axis=1) + 1e-9) ** 3
    kappa = np.linalg.norm(cross, axis=1) / norm_dr_cubed
    return kappa


def update_manifold_from_geometry(
    manifold: RiemannManifold,
    cell_radius_nm: float,
    crowding_index: float,
    params: RiemannParams,
) -> RiemannManifold:
    """Aktualisiert die Mannigfaltigkeit mit aktueller Zell-Geometrie.

    Krümmung wächst mit Crowding (lokale Kompression → mehr Krümmung).
    Geodätische Skalierung: Konformation wird um cell_radius skaliert,
    aber Krümmung kontrolliert zusätzlich die Form.
    """
    manifold.step_count += 1

    # Skaliere Konformation auf neuen Radius (geodätische Projektion)
    current_rg = float(np.linalg.norm(manifold.r, axis=1).mean())
    target_rg = cell_radius_nm
    if current_rg > 1e-9:
        scale = target_rg / current_rg
        manifold.r *= scale

    # Lokales Crowding erhöht Krümmung (DNA wird kompakter)
    kappa_base = compute_curvature(manifold)
    # Crowding-Effekt: lokale Kompression → höhere Krümmung
    manifold.curvature_kappa = kappa_base * (1.0 + 5.0 * crowding_index)

    # Riemannscher Krümmungstensor (1D-Mannigfaltigkeit: R^ρ_σμν = 0 für flach)
    # Hier verwenden wir einen Skalar-Proxy: ∫κ² ds
    manifold.riemann_tensor_components = float(
        np.trapezoid(manifold.curvature_kappa**2, manifold.s)
    )
    return manifold


def geodesic_velocity(manifold: RiemannManifold, target_step_nm: float = 0.1) -> np.ndarray:
    """Berechnet die geodätische Geschwindigkeit auf der Mannigfaltigkeit.

    v(s) = target_step · e_s   (e_s = Tangential-Vektor an s)

    In einer flachen 1D-Mannigfaltigkeit ist das trivial. Bei nicht-trivialer
    Krümmung müsste man Parallel-Transport integrieren.
    """
    e_s = np.gradient(manifold.r, axis=0)
    e_s_norm = np.linalg.norm(e_s, axis=1, keepdims=True)
    e_s_unit = e_s / (e_s_norm + 1e-9)
    return target_step_nm * e_s_unit
