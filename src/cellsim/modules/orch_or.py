"""Orch-OR-Kollaps-Kern (L4-Brücke) — iter-16-Resultat als Kernel.

Rekonstruiert die iter-16-Phase-Diagramm-Rechnung (Hagan-Parametrisierung)
als ausführbaren Kollaps-Kern mit Gates — epistemische Bescheidenheit
eingebaut:

Claim-Leiter (modul-docstring, vorab registriert):
  C1  τ_OR < τ_dec ist in der großzügigen HYPOTHESE-Ecke erreichbar
      (f ≤ 5e-2, a ≤ 8 nm, N ≤ 1e11, S ≤ 1e6) — numerisches Resultat
      iter-16 (beste Ratio 0.61), hier programmatisch reproduziert.
      KEINE Behauptung über die physikalische Realität von Orch-OR.
  C2  Ein OR-Kollaps-Kern (hazard dt/τ_OR, kollektiver Kick pro
      Cluster) erzeugt in Simulation statistisch unterscheidbare
      Ereignis-Muster vs. gematchter klassischer Kontrolle (gleiche
      mittlere Rate, unabhängiges Poisson pro Voxel). Die
      Unterscheidbarkeit ist eine Eigenschaft der beiden Modelle, kein
      Nachweis von Kollaps-Physik.
  C3  Physiologische Relevanz in JCVI-syn3A wird NICHT behauptet:
      syn3A hat kein Mikrotubuli-Kollektiv (N_eff ≈ 1) → Gate OFF,
      Kernel feuert nie (test_or_kernel_syn3a_never_fires).

Formeln (Penrose 1994; Hagan et al. 2002; Tegmark 2000):
  E_G = G·(ΔM)²/a·N^(2|1)   (korreliert | unkorreliert)
  τ_OR = ħ/E_G
  τ_dec = ħ/(k_B·T·(Δm/m)²)·S   (S = 1 → Tegmark-bulk-Grenze)

Gate: OR greift nur wenn τ_OR < τ_dec (die objektive Reduktion MUSS
vor der Umgebungs-Dekohärenz greifen; iter-7-Kriterium, korrekt
herum). τ_OR > τ_dec → Gate OFF → hazard 0.

Status: PRODUCTION-Kern (iter-18) mit HYPOTHESE-Kennzeichnung: die
Kick-Kopplung (was ein Kollaps chemisch bewirkt) ist HYPOTHESE und
wird hier nicht behauptet — der Kernel liefert nur Ereignis-Muster.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Naturkonstanten (SI)
HBAR = 1.054_571_817e-34      # J·s
KB = 1.380_649e-23            # J/K
G_NEWTON = 6.674_30e-11       # m³/kg/s²


@dataclass(frozen=True)
class ORConfig:
    """Parameter der Orch-OR-/Dekohärenz-Rechnung.

    Defaults = iter-16 'beste Region' (großzügige HYPOTHESE-Ecke):
    f=5e-2, a=8 nm, N=1e9 korreliert, S=1e6 → τ_OR/τ_dec = 0.61.
    """

    f_frac: float = 5e-2            # Konformations-Masseanteil ΔM/m
    a_nm: float = 8.0               # Verschiebung
    n_tubulins: float = 1e9         # Kollektiv-Größe (Hameroff 1e9-1e11)
    shielding: float = 1e6          # S: ordered water/Debye/Gel (HYPOTHESE)
    correlated: bool = True         # E_G ∝ N² (korreliert) vs N
    m_tubulin_kg: float = 1.83e-22  # 110 kDa
    t_k: float = 310.0
    delta_m_over_m_bulk: float = 0.01  # Tegmark-Bulk-Parameter


def penrose_tau_or_s(cfg: ORConfig) -> float:
    """τ_OR = ħ/E_G mit E_G = G·(ΔM)²/a·N^(2|1).

    Korreliert: E_G ∝ N² (τ_OR ∝ 1/N²); unkorreliert: ∝ N.
    """
    if cfg.n_tubulins < 1:
        raise ValueError("n_tubulins >= 1")
    delta_m = cfg.f_frac * cfg.m_tubulin_kg
    e_single = G_NEWTON * delta_m**2 / (cfg.a_nm * 1e-9)
    e_collective = e_single * cfg.n_tubulins ** (2 if cfg.correlated else 1)
    return HBAR / e_collective


def tegmark_tau_dec_s(cfg: ORConfig) -> float:
    """τ_dec = ħ/(k_B·T·(Δm/m)²)·S.

    S = 1 → Tegmark-bulk-Grenze (ehrlicher Boundary des Modells);
    S > 1 ist die HYPOTHESE 'Shielding' (ordered water, Debye, Gel).
    """
    if cfg.shielding < 1.0:
        raise ValueError("shielding >= 1 (S=1 ist die Bulk-Grenze)")
    bulk = HBAR / (KB * cfg.t_k * cfg.delta_m_over_m_bulk**2)
    return bulk * cfg.shielding


def n_gate_threshold(cfg: ORConfig) -> float:
    """Kritische Kollektiv-Größe N* für Gate-ON: N² > ħ/(τ_dec·e_single).

    (nur für korreliert=True definiert; sonst inf).
    """
    if not cfg.correlated:
        return math.inf
    delta_m = cfg.f_frac * cfg.m_tubulin_kg
    e_single = G_NEWTON * delta_m**2 / (cfg.a_nm * 1e-9)
    tau_dec = tegmark_tau_dec_s(cfg)
    return math.sqrt(HBAR / (tau_dec * e_single))


@dataclass
class ORCollapseKernel:
    """Diskreter Kollaps-Kern mit Gates (iter-18).

    Pro Schritt (dt_s): wenn Gate ON, feuert der Kern mit hazard
    dt/τ_OR und kollabiert EIN kohärentes Cluster — alle Voxel des
    Clusters gleichzeitig (das kollektive Quanten-Signatur-Muster).
    Gate OFF → nie (hazard 0).

    Die Kick-Größe/-Richtung ist hier NICHT modelliert (HYPOTHESE,
    siehe Experiment or_discrimination.py): der Kernel liefert nur das
    Ereignis-Muster (welche Voxel, welcher Zeitpunkt).
    """

    config: ORConfig = field(default_factory=ORConfig)
    cluster_size: int = 16          # Voxel pro kohärentem Cluster (HYPOTHESE)
    dt_s: float = 1e-4              # Diskretisierungs-Schritt

    tau_or_s: float = field(init=False)
    tau_dec_s: float = field(init=False)

    def __post_init__(self) -> None:
        if self.cluster_size < 1:
            raise ValueError("cluster_size >= 1")
        if self.dt_s <= 0:
            raise ValueError("dt_s > 0")
        self.tau_or_s = penrose_tau_or_s(self.config)
        self.tau_dec_s = tegmark_tau_dec_s(self.config)

    @property
    def gate_on(self) -> bool:
        """Gate: τ_OR < τ_dec (Reduktion vor Umgebungs-Dekohärenz)."""
        return self.tau_or_s < self.tau_dec_s

    @property
    def ratio(self) -> float:
        """τ_OR/τ_dec; < 1 → Gate ON."""
        return self.tau_or_s / self.tau_dec_s

    def hazard_per_step(self) -> float:
        """dt/τ_OR wenn Gate ON (geclippt auf ≤ 1), sonst 0."""
        if not self.gate_on:
            return 0.0
        return min(self.dt_s / self.tau_or_s, 1.0)

    def step(self, rng: np.random.Generator, n_sites: int) -> list[int]:
        """Ein Diskretisierungsschritt: liefert kollabierte Site-Indices.

        Kollektives Muster: EIN Zufallsdraw kollabiert das GANZE Cluster
        (cluster_size Voxel gleichzeitig) — im Gegensatz zur klassischen
        Kontrolle (unabhängiges Poisson pro Voxel, gleiche mittlere
        Rate). Gate OFF → leere Liste (feuert nie).
        """
        h = self.hazard_per_step()
        if h <= 0.0 or n_sites < self.cluster_size:
            return []
        if rng.random() >= h:
            return []
        n_clusters = n_sites // self.cluster_size
        cluster = int(rng.integers(n_clusters))
        base = cluster * self.cluster_size
        return list(range(base, base + self.cluster_size))


def syn3a_gate_check() -> dict[str, object]:
    """C3-Check: JCVI-syn3A hat kein Mikrotubuli-Kollektiv (N_eff ≈ 1)
    → Gate OFF, Kernel feuert nie. Programmatisch prüfbar."""
    cfg = ORConfig(n_tubulins=1.0, shielding=1.0)
    kernel = ORCollapseKernel(config=cfg)
    return {
        "tau_or_s": kernel.tau_or_s,
        "tau_dec_s": kernel.tau_dec_s,
        "ratio": kernel.ratio,
        "gate_on": kernel.gate_on,
        "hazard_per_step": kernel.hazard_per_step(),
        "claim": "syn3A: kein OR-Kanal (N_eff=1, S=1 bulk) — Gate OFF",
    }
