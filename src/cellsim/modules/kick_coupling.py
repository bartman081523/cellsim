"""Kick-Kopplungsbudget (L4-Brücke) — iter-22 VECTOR_OR_KICK_COUPLING.

Frage (vorab registriert, vor jedem Lauf): Was bewirkt ein OR-Kollaps
chemisch? iter-18 liefert nur Ereignis-Muster (C2-Cap); die Kick-Kopplung
ist in orch_or.py ausdrücklich HYPOTHESE ("Kick-Größe/-Richtung ist hier
NICHT modelliert"). Falsifizierbarer Kern der Hypothese ist der
ENERGETISCHE Kanal: kann ein Kollaps-Event innerhalb der registrierten
C1-Box überhaupt ein chemisches Quantum liefern?

Zentrale physikalische Aussage der Registrierung:
  Ein Selbst-Kollaps setzt höchstens E_G frei — die Gravitations-
  Selbstenergie, die die Branches trennt (Penrose 1994; E = ħ/T). Das
  registrierte BEST-CASE-Budget für Orch-OR:
    E_kick = e_collective = ħ/τ_OR      (GESAMTE Selbstenergie, korreliert
                                        N² → größtmögliches Budget)
    Lieferung zu 100 % in EIN Zielmode, ohne Verlust, keine Zwischen-
    kanäle. Ionen/Proteine/Felder ignorieren die Chemie nicht weiter.

  Adressierbarkeit (Fluktuations-Dissipation): eine Konformations-/Reak-
  tionsmode bei 310 K FLUKTUIERT selbst mit ~k_B·T. Ein Kick unterhalb
  k_B·T ist für die Chemie selbst nicht von einer thermischen Fluktuation
  unterscheidbar — er ist TEIL des Ensembles, kein Gate. Registrierter
  Floor: E_acc ≥ 1.0·k_B·T (kein Tuning-Parameter).

  Akkumulation nur innerhalb des Relaxationsfensters: Schläge, die
  langsamer eintreffen als die Mode thermalisiert, akkumulieren NICHT
  in der Mode — sie werden Wärme (Thermostat-klamppt). Registriert
  großzügig: τ_relax ≤ 1e-3 s (ms-Konformationsübergänge existieren
  real; ns-µs sind der Normalfall). Konvention großzügig für Orch-OR:
  E_acc = e_collective · max(1, τ_relax/τ_OR) — mindestens ein Event
  wirkt voll, schneller Nachschub akkumuliert linear im Fenster.

  Landauer-Kanal (zweiter, unabhängiger Blick): Bias b einer Rate
  kostet Arbeit ≥ k_B·T·ln(1+b) ≈ k_B·T·b → max. Bias pro Event =
  E_kick/k_B·T; kumulierter Bias im Relaxationsfenster = E_acc/k_B·T.
  Dasselbe Kriterium, zweiter Kanal — Cross-Check.

  Trigger-Zweig: ein Null-Energie-Selektor (Kollaps wählt nur unter
  thermischen Trajektorien aus) ist als Physik unfalsifizierbar —
  operationell ununterscheidbar von Stochastic-Seeding (C2-Cap,
  iter-18). Er wird NICHT als Unterstützung gebucht; der falsifizierbare
  Rest der Kick-Hypothese ist exakt der hier analysierte Energiekanal.

  Box (registriert, C1-Ecke iter-16): N ≤ 1e11 (Hameroff-Obergrenze),
  f ≤ 5e-2, a ≤ 8 nm, korreliert (N² — bester Fall für Energie UND
  Event-Rate). Δm/m-Achse berührt das Kick-Budget NICHT (Penrose-Seite).

  Ketten-Haken: (a) Gate-ON ohne Schild verlangt N ≥ 7.8e11 > Box —
  der Kick-Kanal braucht das Schild; mit dem ABLEITBAREN Schild
  (iter-21: S_max = 9.9e3) ist Gate-ON ab N ≥ 7.9e9 möglich — das
  Schild ist also NICHT der bindende Faktor, die Energie ist es.
  (b) Adressierbarkeit außerhalb der Box (N ≥ 1.74e11 bei τ_relax =
  1 ms) verlangt Kollektive jenseits der Hameroff-Grenze. (c) Kohärente
  Akkumulation ÜBER Relaxationsfenster hinweg (Sekunden bis Minuten)
  ist ein Kondensat-Typ-Mechanismus — REFUTED_BY_REIMERS_2010
  (VECTOR_FROEHLICH_CONDENSATION) in diesem Repo.

Claim-Deckel: dieses Modul leitet OB der Kick innerhalb der registrierten
Box chemisch adressierbar ist. Es behauptet NICHT, dass Orch-OR falsch
ist — Kollektive jenseits N=1e11, exotische Verstärker oder Trigger-ohne-
Energie bleiben außerhalb der registrierten Falsifikation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from cellsim.modules.orch_or import (
    G_NEWTON,
    HBAR,
    KB,
    ORConfig,
    n_gate_threshold,
    penrose_tau_or_s,
)

# --- Registrierte Schranken (VOR dem Lauf fixiert; siehe Modul-Docstring) ---

ADDRESSABILITY_KBT_FLOOR = 1.0   # Fluktuations-Dissipation: E_acc ≥ k_B·T
N_BOX_MAX = 1e11                 # Hameroff-Obergrenze (C1-Box, iter-16)
TAU_RELAX_GRID_S = (1e-7, 1e-6, 1e-3)  # großzügige obere Relaxations-Schranken
DELTA_G_ATP_J = 8.3e-20          # ~50 kJ/mol / N_A — Kontext-Anker
REG_E_SINGLE_J = 6.985e-49       # iter-16/18-Anker (K1, nicht neu hergeleitet)


@dataclass(frozen=True)
class KickBudget:
    """Registriertes Kick-Budget (Best-Case zugunsten von Orch-OR).

    tau_relax_s: obere Schranke des Relaxationsfensters der Zielmode
    (größter registrierter Wert = großzügigster Fall für Akkumulation).
    """

    tau_relax_s: float = 1e-3

    def __post_init__(self) -> None:
        if self.tau_relax_s <= 0.0:
            raise ValueError("tau_relax_s > 0")


def e_single_j(or_cfg: ORConfig) -> float:
    """E_G(dimer) = G·(f·m)²/a — zweite EXPLIZITE Route (iter-19-Lektion:
    niemals die Registrierung nur gegen den Produktionspfad prüfen)."""
    delta_m = or_cfg.f_frac * or_cfg.m_tubulin_kg
    return G_NEWTON * delta_m**2 / (or_cfg.a_nm * 1e-9)


def e_collective_j(or_cfg: ORConfig) -> float:
    """E_G(Kollektiv) = E_G(dimer)·N^(2|1) — explizite Route."""
    return e_single_j(or_cfg) * or_cfg.n_tubulins ** (2 if or_cfg.correlated else 1)


def per_event_thermal_ratio(or_cfg: ORConfig) -> float:
    """R_1 = E_kick/k_B·T — thermische Adressierbarkeit EINES Events."""
    return e_collective_j(or_cfg) / (KB * or_cfg.t_k)


def event_rate_per_s(or_cfg: ORConfig) -> float:
    """λ = 1/τ_OR — Produktions-Route (Cross-Check gegen explizite Route)."""
    return 1.0 / penrose_tau_or_s(or_cfg)


def relaxation_window_energy_j(or_cfg: ORConfig, tau_relax_s: float) -> float:
    """E_acc = E_kick·max(1, τ_relax/τ_OR) — Energie im Relaxationsfenster.

    Großzügige Konvention: mindestens EIN Event wirkt voll; schneller
    Nachschub (λ·τ_relax > 1) akkumuliert linear im Fenster.
    """
    n_events = max(1.0, tau_relax_s * event_rate_per_s(or_cfg))
    return e_collective_j(or_cfg) * n_events


def relaxation_window_bias(or_cfg: ORConfig, tau_relax_s: float) -> float:
    """Kumulierter Landauer-Bias im Fenster = E_acc/k_B·T (linearisiert)."""
    return relaxation_window_energy_j(or_cfg, tau_relax_s) / (KB * or_cfg.t_k)


def n_addressable_threshold(or_cfg: ORConfig, tau_relax_s: float) -> float:
    """Kleinstes N mit E_acc(N) ≥ Floor·k_B·T (Bisektion, branch-unabhängig).

    Zweite Route (analytisch, korreliert): N* = (ħ·Floor·k_B·T /
    (τ_relax·E_dimer²))^¼ für den Fall τ_relax > τ_OR(N); der Übergang
    liegt IMMER in diesem Zweig, weil der Branch-A-Schwellwert
    sqrt(Floor·k_B·T/E_dimer) ≫ sqrt(ħ/(τ_relax·E_dimer)) = N_x.
    """
    floor = ADDRESSABILITY_KBT_FLOOR
    e_d = e_single_j(or_cfg)
    n_analytic = (HBAR * floor * KB * or_cfg.t_k
                  / (tau_relax_s * e_d**2)) ** 0.25
    # Numerische Bisektion als unabhängige Kontrolle
    lo, hi = 1.0, 1e16

    def acc_minus_floor(n: float) -> float:
        cfg = ORConfig(
            f_frac=or_cfg.f_frac, a_nm=or_cfg.a_nm, n_tubulins=n,
            correlated=or_cfg.correlated, m_tubulin_kg=or_cfg.m_tubulin_kg,
            t_k=or_cfg.t_k,
        )
        return relaxation_window_energy_j(cfg, tau_relax_s) \
            - floor * KB * or_cfg.t_k

    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if acc_minus_floor(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    n_numeric = math.sqrt(lo * hi)
    if abs(n_analytic - n_numeric) / n_analytic > 1e-6:
        raise AssertionError(
            f"N*-Herleitung divergiert: analytisch {n_analytic:.6e} vs "
            f"numerisch {n_numeric:.6e}")
    return n_analytic


def gate_min_n_with_shield(or_cfg: ORConfig, shield: float) -> float:
    """Kleinstes N für Gate-ON bei gegebenem Schild (Reuse orch_or).

    Gate-ON ⇔ τ_OR(N) < τ_dec_bulk·S ⇔ N ≥ sqrt(ħ/(τ_dec·E_dimer)).
    """
    cfg = ORConfig(
        f_frac=or_cfg.f_frac, a_nm=or_cfg.a_nm, shielding=shield,
        correlated=or_cfg.correlated, m_tubulin_kg=or_cfg.m_tubulin_kg,
        t_k=or_cfg.t_k, delta_m_over_m_bulk=or_cfg.delta_m_over_m_bulk,
    )
    return n_gate_threshold(cfg)
