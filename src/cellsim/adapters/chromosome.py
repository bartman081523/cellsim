"""Chromosome-Solver-Stub (Python).

1D-Bead-Spring-Modell als Stub-Ersatz für btree_chromo+LAMMPS.
Keine Replikation, keine Topoisomerase — nur Struktur-Konformation.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ChromosomeState:
    """Positionen + Geschwindigkeiten einer Bead-Kette."""

    positions: np.ndarray = field(default_factory=lambda: np.zeros((0, 1)))
    velocities: np.ndarray = field(default_factory=lambda: np.zeros((0, 1)))
    spring_constant: float = 1.0
    excluded_volume_radius_nm: float = 50.0
    step_count: int = 0


class ChromosomeAdapter:
    """Minimaler Bead-Spring-Verlet-Integrator."""

    name = "chromosome"

    def __init__(
        self,
        n_beads: int = 50,
        spring_constant: float = 1.0,
        excluded_volume_radius_nm: float = 50.0,
        initial_radius_nm: float = 100.0,
        rng: np.random.Generator | None = None,
        use_riemann: bool = False,
    ) -> None:
        self.state = ChromosomeState(
            positions=np.zeros((n_beads, 3), dtype=np.float64),
            velocities=np.zeros((n_beads, 3), dtype=np.float64),
            spring_constant=spring_constant,
            excluded_volume_radius_nm=excluded_volume_radius_nm,
        )
        # Initialisierung: Kette in einer Spirale um den Nukleoid
        rng = rng or np.random.default_rng(42)
        for i in range(n_beads):
            theta = i * 2 * np.pi / n_beads
            r = initial_radius_nm * (0.5 + 0.5 * (i / n_beads))
            self.state.positions[i, 0] = r * np.cos(theta)
            self.state.positions[i, 1] = r * np.sin(theta)
            self.state.positions[i, 2] = (i - n_beads / 2) * 2.0
            self.state.velocities[i] = rng.normal(scale=0.1, size=3)

        # Optional: Riemann-Mannigfaltigkeit (L4) parallel betreiben
        self.use_riemann = use_riemann
        self.manifold = None
        self._crowding_index = 0.0
        if use_riemann:
            from cellsim.modules.riemann import RiemannParams, init_manifold

            self.manifold = init_manifold(
                RiemannParams(n_beads=n_beads),
                initial_radius_nm=initial_radius_nm,
                seed=42,
            )

    @property
    def radius_of_gyration_nm(self) -> float:
        com = self.state.positions.mean(axis=0)
        rg = float(np.sqrt(((self.state.positions - com) ** 2).sum(axis=1).mean()))
        return rg

    def step(self, dt_s: float, rng: np.random.Generator) -> dict[str, float]:
        """Ein Velocity-Verlet-Schritt mit Federkraft + brown'scher Anregung."""
        self.state.step_count += 1
        n = self.state.positions.shape[0]

        # Federkraft zwischen benachbarten Beads
        forces = np.zeros_like(self.state.positions)
        if n > 1:
            diff = self.state.positions[1:] - self.state.positions[:-1]
            # Spring: F = -k * (length - rest_length) * direction
            rest = 5.0  # nm
            lengths = np.linalg.norm(diff, axis=1, keepdims=True)
            directions = diff / np.maximum(lengths, 1e-9)
            stretch = lengths - rest
            forces[:-1] += self.state.spring_constant * stretch * directions
            forces[1:] -= self.state.spring_constant * stretch * directions

        # Brown'sche Anregung (sehr klein)
        forces += rng.normal(scale=0.01, size=self.state.positions.shape)

        # Velocity-Verlet (sehr vereinfacht, ohne Masse)
        self.state.velocities += dt_s * forces
        self.state.positions += dt_s * self.state.velocities

        return self._telemetry()

    def couple_to_geometry(self, radius_nm: float) -> None:
        """Skaliert Positionen, wenn der Nukleoid wächst."""
        current_rg = self.radius_of_gyration_nm
        if current_rg < 1e-9:
            return
        scale = min(radius_nm / 100.0, 1.0)  # 100 nm initial
        self.state.positions *= scale

        # Riemann-Mannigfaltigkeit (L4) mit aktualisierter Geometrie
        if self.use_riemann and self.manifold is not None:
            from cellsim.modules.riemann import (
                RiemannParams,
                update_manifold_from_geometry,
            )

            update_manifold_from_geometry(
                self.manifold,
                cell_radius_nm=radius_nm,
                crowding_index=self._crowding_index,
                params=RiemannParams(n_beads=self.state.positions.shape[0]),
            )

    def couple_to_crowding(self, crowding_index: float) -> None:
        """Setzt Crowding-Index für Riemann-Mannigfaltigkeit."""
        self._crowding_index = crowding_index

    def _telemetry(self) -> dict[str, float]:
        result = {
            "rg_nm": self.radius_of_gyration_nm,
            "chromosome_steps": float(self.state.step_count),
        }
        if self.use_riemann and self.manifold is not None:
            result["riemann_curvature_mean"] = self.manifold.mean_curvature
            result["riemann_curvature_max"] = self.manifold.max_curvature
            result["riemann_R_scalar"] = self.manifold.riemann_tensor_components
        return result

    def snapshot(self) -> bytes:
        snap = {
            "step_count": self.state.step_count,
            "positions": self.state.positions.tolist(),
            "velocities": self.state.velocities.tolist(),
        }
        return json.dumps(snap).encode("utf-8")

    def restore(self, blob: bytes) -> None:
        snap = json.loads(blob.decode("utf-8"))
        self.state.step_count = snap["step_count"]
        self.state.positions = np.asarray(snap["positions"], dtype=np.float64)
        self.state.velocities = np.asarray(snap["velocities"], dtype=np.float64)
