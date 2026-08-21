"""ODE-Solver-Stub (Python).

scipy.integrate.solve_ivp für hochkonzentrierte Metaboliten.
Stub-Ersatz für odecell.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp

logger = logging.getLogger(__name__)


@dataclass
class ODEState:
    """Konzentrationen der Metaboliten."""

    n_species: int
    species_ids: tuple[str, ...]
    concentrations_mM: np.ndarray = field(default_factory=lambda: np.zeros(0))
    t_s: float = 0.0
    step_count: int = 0


class ODEAdapter:
    """Glykolyse-Stub: Glucose → ATP mit 6 Schritten (sehr vereinfacht)."""

    name = "ode"

    def __init__(
        self,
        species_ids: tuple[str, ...] = ("Glucose", "ATP", "ADP"),
        initial_mM: tuple[float, ...] = (5.0, 2.0, 0.5),
        use_frohlich: bool = False,
    ) -> None:
        self.state = ODEState(
            n_species=len(species_ids),
            species_ids=species_ids,
            concentrations_mM=np.asarray(initial_mM, dtype=np.float64),
        )
        self._initial_total = float(self.state.concentrations_mM.sum())
        # Optional: Fröhlich-Kohärenz moduliert ATP-Verbrauch (L4, kontrovers)
        self.use_frohlich = use_frohlich
        self.frohlich = None
        if use_frohlich:
            from cellsim.modules.frohlich import FrohlichAdapter
            self.frohlich = FrohlichAdapter()

    @property
    def concentrations(self) -> np.ndarray:
        return self.state.concentrations_mM

    def step(self, dt_s: float, rng: np.random.Generator) -> dict[str, float]:
        """Ein ODE-Schritt: solve_ivp von t bis t+dt."""
        self.state.step_count += 1
        t_span = (self.state.t_s, self.state.t_s + dt_s)
        sol = solve_ivp(
            fun=self._rhs,
            t_span=t_span,
            y0=self.state.concentrations_mM,
            method="RK45",
            rtol=1e-6,
            atol=1e-9,
            max_step=dt_s / 4.0,
        )
        self.state.concentrations_mM = sol.y[:, -1]
        # Nicht-Negativität erzwingen
        np.maximum(self.state.concentrations_mM, 0.0, out=self.state.concentrations_mM)
        self.state.t_s = t_span[1]
        # Fröhlich-Update nach ODE-Schritt
        if self.use_frohlich and self.frohlich is not None:
            # Energie-Input ~ metabolischer Fluss (sehr grob)
            metabolic_energy_j = float(self.state.concentrations_mM[1]) * 1e-21
            self.frohlich.step(dt_s=dt_s, energy_input_j=metabolic_energy_j)
        return self._telemetry()

    def _rhs(self, t: float, y: np.ndarray) -> np.ndarray:
        """Glykolyse-ODE: ATP-Produktion aus Glucose, ATP-Verbrauch."""
        glucose = max(float(y[0]), 0.0)
        atp = max(float(y[1]), 0.0)

        # Glucose-Verbrauch: v = k * Glucose
        k_glyc = 0.05   # 1/s
        # ATP-Verbrauch: v = k * ATP (mit optionaler Fröhlich-Modulation)
        k_atp_base = 0.03   # 1/s
        frohlich_factor = 1.0
        if self.use_frohlich and self.frohlich is not None:
            frohlich_factor = self.frohlich.atp_savings_factor()
        k_atp = k_atp_base * frohlich_factor

        d_glucose = -k_glyc * glucose
        # ATP-Produktion = 2 × Glucose-Verbrauch (Glykolyse-Bruttogleichung)
        d_atp = 2.0 * (-d_glucose) - k_atp * atp
        d_adp = -d_atp  # ADP ↔ ATP spiegelt sich (sehr vereinfacht)

        return np.asarray([d_glucose, d_atp, d_adp], dtype=np.float64)

    def _telemetry(self) -> dict[str, float]:
        tel = {
            "t_s": float(self.state.t_s),
            "glucose_mM": float(self.state.concentrations_mM[0]),
            "atp_mM": float(self.state.concentrations_mM[1]),
            "adp_mM": float(self.state.concentrations_mM[2]),
        }
        if self.use_frohlich and self.frohlich is not None:
            tel["frohlich_coherence"] = self.frohlich.state.coherence_order_parameter
        return tel

    def snapshot(self) -> bytes:
        snap = {
            "t_s": self.state.t_s,
            "step_count": self.state.step_count,
            "concentrations_mM": self.state.concentrations_mM.tolist(),
            "species_ids": list(self.state.species_ids),
        }
        return json.dumps(snap).encode("utf-8")

    def restore(self, blob: bytes) -> None:
        snap = json.loads(blob.decode("utf-8"))
        self.state.t_s = snap["t_s"]
        self.state.step_count = snap["step_count"]
        self.state.concentrations_mM = np.asarray(snap["concentrations_mM"], dtype=np.float64)
        self.state.species_ids = tuple(snap["species_ids"])
