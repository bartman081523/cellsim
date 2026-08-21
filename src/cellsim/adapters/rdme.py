"""RDME-Solver-Stub (Python).

Sehr einfache Gillespie-SSA-Implementierung als Stub-Ersatz für
Lattice Microbes. Zweck: zeigen, dass das Solver-Interface funktioniert
und deterministisch ist — keine biologische Korrektheit beansprucht.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import numpy as np

from cellsim.modules.reactions import ReactionRegistry

logger = logging.getLogger(__name__)


@dataclass
class RDMEState:
    """Voxel-Gitter mit Anzahl-Matrix pro Spezies."""

    n_species: int
    grid_shape: tuple[int, int, int]
    voxels: dict[str, np.ndarray] = field(default_factory=dict)
    species_ids: tuple[str, ...] = ()
    total_particles: int = 0
    step_count: int = 0


class RDMEAdapter:
    """Sehr einfacher Gillespie-SSA-Solver."""

    name = "rdme"

    def __init__(
        self,
        registry: ReactionRegistry,
        grid_shape: tuple[int, int, int] = (8, 8, 8),
        initial_particles_per_species: int = 50,
        use_local_diffusion: bool = False,
    ) -> None:
        self.registry = registry
        self.grid_shape = grid_shape
        self.use_local_diffusion = use_local_diffusion

        # Voxel-Belegung: species_id -> np.ndarray[grid_shape] (counts)
        species_ids = tuple(registry.species_ids)
        voxels: dict[int, np.ndarray] = {}
        for s_id in species_ids:
            voxels[s_id] = np.full(grid_shape, initial_particles_per_species, dtype=np.int64)
        total = sum(int(v.sum()) for v in voxels.values())

        self.state = RDMEState(
            n_species=len(species_ids),
            grid_shape=grid_shape,
            voxels=voxels,
            species_ids=species_ids,
            total_particles=total,
            step_count=0,
        )
        self._initial_total = total

    @property
    def total_particles(self) -> int:
        return self.state.total_particles

    def step(self, dt_s: float, rng: np.random.Generator) -> dict[str, float]:
        """Ein RDME-Schritt: Gillespie-SSA mit dt_s als maximale Wartezeit."""
        self.state.step_count += 1

        # Reaktions-Raten aus Registry (sehr einfach: k * Produkt der Konz.)
        rates = self._compute_rates()
        a0 = sum(rates)
        if a0 <= 0.0:
            return self._telemetry()

        # Wähle Reaktions-Index
        u1 = rng.random() * a0
        cumulative = 0.0
        chosen = len(rates) - 1
        for i, r in enumerate(rates):
            cumulative += r
            if cumulative >= u1:
                chosen = i
                break

        # Wähle Voxel + Reaktions-Partner
        idx_flat = rng.integers(0, self._n_voxels())
        idx_3d = np.unravel_index(idx_flat, self.grid_shape)

        # Lokale Diffusions-Modifikation (L2↔L3-Brücke, VECTOR_BRIDGE_L2_L3)
        if self.use_local_diffusion:
            self._apply_local_diffusion(idx_3d, dt_s, rng)

        # Wende Reaktion an (stöchiometrisch, sehr einfach)
        rxn = self.registry.reactions[chosen]
        self._apply_rxn(rxn.species_change, idx_3d)
        self.state.total_particles = sum(int(v.sum()) for v in self.state.voxels.values())

        return self._telemetry()

    def _apply_local_diffusion(
        self,
        idx_3d: tuple[int, ...],
        dt_s: float,
        rng: np.random.Generator,
    ) -> None:
        """Crowding-aware Diffusion: lokal reduzierte D reduziert Migrationsrate.

        Sehr einfach: pro Voxel wird die Reaktions-Wahrscheinlichkeit
        mit dem lokalen Crowding-Faktor multipliziert. Effektiv
        längere Verweilzeit in dichten Voxeln.
        """
        i, j, k = idx_3d
        # Lokales Crowding = Summe aller Counts im Voxel
        local_crowding = sum(int(v[i, j, k]) for v in self.state.voxels.values())
        # Lokaler Dämpfungsfaktor (e^{-alpha · crowding_normalized})
        alpha = 1.0
        max_per_species = max(int(v.max()) for v in self.state.voxels.values())
        n_voxel_max = max(max_per_species * len(self.state.voxels), 1)
        crowding_norm = local_crowding / n_voxel_max
        damping = float(np.exp(-alpha * crowding_norm))
        # Wahrscheinlichkeit, dass die Reaktion *nicht* stattfindet
        if rng.random() > damping:
            # Diffusion statt Reaktion: Teilchen wandert zu Nachbar-Voxel
            self._migrate_particle(idx_3d, rng)

    def _migrate_particle(
        self,
        idx_3d: tuple[int, ...],
        rng: np.random.Generator,
    ) -> None:
        """Migriert ein zufälliges Teilchen in ein Nachbar-Voxel."""
        i, j, k = idx_3d
        # Wähle zufällige Spezies und Richtung
        species_keys = list(self.state.voxels.keys())
        if not species_keys:
            return
        s_key = species_keys[rng.integers(0, len(species_keys))]
        v = self.state.voxels[s_key]
        if int(v[i, j, k]) <= 0:
            return
        v[i, j, k] -= 1
        # Wähle Nachbar (periodisch)
        di = int(rng.integers(-1, 2))
        dj = int(rng.integers(-1, 2))
        dk = int(rng.integers(-1, 2))
        ni = (i + di) % self.grid_shape[0]
        nj = (j + dj) % self.grid_shape[1]
        nk = (k + dk) % self.grid_shape[2]
        v[ni, nj, nk] += 1

    def _compute_rates(self) -> list[float]:
        rates: list[float] = []
        for rxn in self.registry.reactions:
            # Mass-action: rate = k * n_reactant (sehr vereinfacht)
            rate = rxn.k * self._reactant_count(rxn.species_change)
            rates.append(rate)
        return rates

    def _reactant_count(self, species_change: dict[str, int]) -> float:
        # Negative Stöchiometrie = Reaktant
        prod = 1.0
        for s_id, delta in species_change.items():
            if delta < 0:
                v = self.state.voxels.get(self._s_id_to_int(s_id))
                if v is None:
                    return 0.0
                prod *= float(v.sum())
        return prod

    def _apply_rxn(self, species_change: dict[str, int], idx_3d: tuple[int, ...]) -> None:
        for s_id, delta in species_change.items():
            v = self.state.voxels.get(self._s_id_to_int(s_id))
            if v is None:
                continue
            new_val = int(v[idx_3d]) + delta
            if new_val < 0:
                new_val = 0
            v[idx_3d] = new_val

    def _s_id_to_int(self, s_id: str) -> int:
        """Vereinfachtes Mapping: Index in species_ids."""
        try:
            return self.state.species_ids.index(s_id)
        except ValueError:
            return -1

    def _n_voxels(self) -> int:
        return self.state.grid_shape[0] * self.state.grid_shape[1] * self.state.grid_shape[2]

    def _telemetry(self) -> dict[str, float]:
        return {
            "total_particles": float(self.state.total_particles),
            "rdme_steps": float(self.state.step_count),
            "voxel_count": float(self._n_voxels()),
        }

    def snapshot(self) -> bytes:
        snap = {
            "step_count": self.state.step_count,
            "total_particles": self.state.total_particles,
            "voxels": {k: v.tolist() for k, v in self.state.voxels.items()},
            "species_ids": list(self.state.species_ids),
        }
        return json.dumps(snap).encode("utf-8")

    def restore(self, blob: bytes) -> None:
        snap = json.loads(blob.decode("utf-8"))
        self.state.step_count = snap["step_count"]
        self.state.total_particles = snap["total_particles"]
        species_ids = tuple(snap["species_ids"])
        voxels: dict[str, np.ndarray] = {}
        for k, v in snap["voxels"].items():
            voxels[str(k)] = np.asarray(v, dtype=np.int64)
        self.state.voxels = voxels
        self.state.species_ids = species_ids

    @property
    def mass_conservation_ratio(self) -> float:
        """Anfangs-Total / Aktuelles Total (sollte ≈ 1 sein)."""
        if self._initial_total == 0:
            return 1.0
        return self.state.total_particles / self._initial_total
