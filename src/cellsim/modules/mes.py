"""L1/MES-Stub — Memory Evolutive Systems (Ehresmann/Vanbremeersch).

VECTOR_ROSEN_HORIZON-Erweiterung: kategorientheoretische Kolimit-Reparatur
als Stub. Ermöglicht dem Treiber, "tote" Solver-Zustände (z.B. toxische
Metabolit-Konzentrationen) durch Sub-Netzwerk-Reorganisation zu retten.

LIMITATION 3: Echte MES-Theorie (Ehresmann/Vanbremeersch) umfasst:
  - Pattern-Komplexe als kategorientheoretische Objekte
  - Adjunktionen zwischen Komplexen
  - Kolimites als Reparatur-Mechanismus
  - Hierarchische Dekolimitation

Diese Implementation vereinfacht zu:
  - Sub-Netzwerke als benannte Diagramme (string-IDs)
  - Kolimit-Reparatur: Ersetzen eines beschädigten Sub-Netzwerks durch
    ein alternatives aus dem Repair-Pool
  - Memory als exponentiell geglättetes Gedächtnis
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CellState(str, Enum):
    """Zellzustände nach MES."""

    HEALTHY = "healthy"
    STRESSED = "stressed"
    DAMAGED = "damaged"
    REPAIRING = "repairing"
    DEAD = "dead"


@dataclass(frozen=True)
class SubNetwork:
    """Ein Sub-Netzwerk im kategorientheoretischen Sinne.

    Vereinfacht: ein benannter Satz von Reaktionen + Spezies.
    Health-Score wird via dataclasses.replace aktualisiert (frozen für
    kategorientheoretische Invarianten).
    """

    name: str
    reactions: tuple[str, ...] = field(default_factory=tuple)
    species: tuple[str, ...] = field(default_factory=tuple)
    health_score: float = 1.0   # 0 = tot, 1 = voll funktional

    def with_health(self, new_health: float) -> SubNetwork:
        """Immutable Update: ersetzt health_score."""
        from dataclasses import replace

        return replace(self, health_score=new_health)


@dataclass(frozen=True)
class MESParams:
    """Parameter für MES-Trigger."""

    atp_min_mM: float = 0.5
    atp_critical_mM: float = 0.1
    repair_rate_per_s: float = 0.1
    damage_threshold: float = 0.3
    memory_decay_per_s: float = 0.01
    # Kolimit-Reparatur: Mindest-Anzahl alternativer Sub-Netzwerke
    min_alternative_count: int = 2


@dataclass
class MESState:
    """Aktueller MES-Zustand mit kategorientheoretischen Strukturen.

    Bewusst nicht frozen, weil Kolimit-Reparaturen Sub-Netzwerke
    in-place ersetzen.
    """

    cell_state: CellState = CellState.HEALTHY
    memory: dict[str, float] = field(default_factory=dict)
    sub_networks: dict[str, SubNetwork] = field(default_factory=dict)
    alternative_pools: dict[str, tuple[str, ...]] = field(default_factory=dict)
    repair_count: int = 0
    damage_count: int = 0
    kolimit_repairs: int = 0   # Echte MES-Reparaturen
    step_count: int = 0


class MESAdapter:
    """Memory Evolutive Systems — Stub mit Kolimit-Reparatur."""

    name = "mes"

    def __init__(
        self,
        params: MESParams | None = None,
        sub_networks: dict[str, SubNetwork] | None = None,
    ) -> None:
        self.params = params or MESParams()
        self.state = MESState()
        # Default: drei funktionale Sub-Netzwerke mit Alternativen
        self.state.sub_networks = sub_networks or self._default_sub_networks()
        self.state.alternative_pools = self._default_alternative_pools()

    def _default_sub_networks(self) -> dict[str, SubNetwork]:
        """Standard-Sub-Netzwerke: Energie, Replikation, Sekretion."""
        return {
            "energy": SubNetwork(
                name="energy",
                reactions=("glycolysis", "atp_synthase", "atp_hydrolysis"),
                species=("ATP", "ADP", "Pi", "Glucose"),
                health_score=1.0,
            ),
            "replication": SubNetwork(
                name="replication",
                reactions=("dna_pol_iii_binding", "gyrase_supercoil", "ligase_seal"),
                species=("DNA_Pol_III", "DNA_Gyrase", "DNA_Ligase"),
                health_score=1.0,
            ),
            "secretion": SubNetwork(
                name="secretion",
                reactions=("signal_recognition", "sec_translocation"),
                species=("Signal_recog", "Sec_translocon"),
                health_score=1.0,
            ),
        }

    def _default_alternative_pools(self) -> dict[str, tuple[str, ...]]:
        """Kolimit-Alternative: Ersatz-Sub-Netzwerke bei Beschädigung."""
        return {
            "energy": ("energy_alt_aerobic", "energy_alt_fermentation"),
            "replication": ("replication_alt_polI",),
            "secretion": ("secretion_alt_tat",),
        }

    def step(
        self,
        dt_s: float,
        atp_mM: float,
        toxic_fraction: float = 0.0,
    ) -> dict[str, float]:
        """Ein MES-Schritt: Zustands-Übergang + Memory + Sub-Network-Health."""
        self.state.step_count += 1
        prev_state = self.state.cell_state
        params = self.params

        # 1. Aktualisiere Sub-Network-Health (immutable via replace)
        for name, sn in list(self.state.sub_networks.items()):
            new_score = sn.health_score
            if atp_mM < params.atp_min_mM:
                new_score = max(0.0, new_score - 0.05)
            elif atp_mM >= params.atp_min_mM * 2.0:
                new_score = min(1.0, new_score + 0.01)
            if toxic_fraction > params.damage_threshold:
                new_score = max(0.0, new_score - 0.1 * toxic_fraction)
            if new_score != sn.health_score:
                self.state.sub_networks[name] = sn.with_health(new_score)

        # 2. Trigger Kolimit-Reparatur bei beschädigten Sub-Netzwerken
        for name, sn in list(self.state.sub_networks.items()):
            if (
                sn.health_score < 0.3
                and name in self.state.alternative_pools
                and self._kolimit_repair(name)
            ):
                self.state.kolimit_repairs += 1

        # 3. Aggregiere globale Zustandsmaschine
        min_health = min(sn.health_score for sn in self.state.sub_networks.values())
        if prev_state == CellState.DEAD:
            return self._telemetry()
        if min_health < 0.1 or atp_mM < params.atp_critical_mM:
            new_state = CellState.DEAD
        elif min_health < 0.4 or atp_mM < params.atp_min_mM:
            if prev_state == CellState.DAMAGED or prev_state == CellState.REPAIRING:
                new_state = CellState.REPAIRING
                self.state.repair_count += 1
            else:
                new_state = CellState.DAMAGED
                self.state.damage_count += 1
        elif prev_state == CellState.REPAIRING:
            if min_health > 0.7 and atp_mM >= params.atp_min_mM * 1.5:
                new_state = CellState.HEALTHY
            else:
                new_state = CellState.REPAIRING
        elif prev_state == CellState.DAMAGED:
            new_state = CellState.REPAIRING
            self.state.repair_count += 1
        else:
            new_state = CellState.HEALTHY

        # Memory-Update
        self.state.memory["atp_mM"] = (
            self.state.memory.get("atp_mM", atp_mM) * (1 - params.memory_decay_per_s * dt_s)
            + atp_mM * params.memory_decay_per_s * dt_s
        )
        self.state.memory["min_health"] = (
            self.state.memory.get("min_health", min_health)
            * (1 - params.memory_decay_per_s * dt_s)
            + min_health * params.memory_decay_per_s * dt_s
        )

        self.state.cell_state = new_state
        return self._telemetry()

    def _kolimit_repair(self, name: str) -> bool:
        """Kolimit-Reparatur: ersetze beschädigtes Sub-Netzwerk durch Alternative.

        Vereinfachte kategorientheoretische Operation:
          - Input: beschädigtes Sub-Netzwerk S
          - Kolimit: lim(S, Alt) — das neue Sub-Netzwerk ist die
            kategorientheoretische Vereinigung von S und Alt unter
            Berücksichtigung der Überschneidungen.
        """
        alts = self.state.alternative_pools.get(name, ())
        if not alts:
            return False
        # Wähle erste Alternative
        alt_name = alts[0]
        original = self.state.sub_networks[name]
        # Kolimit-Bildung (vereinfacht: ersetze Reaktionen)
        new_sn = SubNetwork(
            name=name,
            reactions=original.reactions + (f"{alt_name}_reaction",),
            species=original.species,
            health_score=0.8,    # Reparatur gibt Health zurück
        )
        self.state.sub_networks[name] = new_sn
        logger.info(
            "MES Kolimit-Reparatur: %s via %s (Health→0.8)",
            name,
            alt_name,
        )
        return True

    def trigger_repair(self) -> bool:
        """Manuelle Reparatur: alle beschädigten Sub-Netzwerke reparieren."""
        triggered = False
        for name in list(self.state.sub_networks.keys()):
            if (
                self.state.sub_networks[name].health_score < 0.5
                and self._kolimit_repair(name)
            ):
                self.state.kolimit_repairs += 1
                triggered = True
        return triggered

    def is_alive(self) -> bool:
        return self.state.cell_state != CellState.DEAD

    def _telemetry(self) -> dict[str, float]:
        return {
            "mes_state_code": float(self.state.cell_state.value.__hash__() % 1000),
            "mes_repair_count": float(self.state.repair_count),
            "mes_damage_count": float(self.state.damage_count),
            "mes_kolimit_repairs": float(self.state.kolimit_repairs),
            "mes_min_health": float(min(sn.health_score for sn in self.state.sub_networks.values())),
            "mes_memory_atp": float(self.state.memory.get("atp_mM", 0.0)),
        }

