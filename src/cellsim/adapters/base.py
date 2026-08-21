"""Protocol[Step] — gemeinsame Schnittstelle aller numerischen Solver.

Aus MT_Sim (`adapters/{kmc_motors,mt_spindle}.py`): jede Solver-Klasse
hat `step(dt, rng) -> State`, `snapshot()` und `restore()`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Step(Protocol):
    """Ein Solver, der einen diskreten Zeitschritt ausführen kann."""

    name: str

    def step(self, dt: float, rng: np.random.Generator) -> dict[str, float]:
        """Führt einen Zeitschritt der Länge dt aus.

        Rückgabe: Telemetrie-Dict für den Treiber (z.B. {"n_particles": 1024}).
        """
        ...

    def snapshot(self) -> bytes:
        """Serialisiert den internen Zustand für Checkpoints."""
        ...

    def restore(self, blob: bytes) -> None:
        """Stellt den Zustand aus einem Snapshot wieder her."""
        ...
