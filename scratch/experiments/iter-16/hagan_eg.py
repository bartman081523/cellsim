"""Iter-16: Orch-OR unter der Hagan-Parametrisierung — korrigierte
Nachrechnung (Falsifikator für iter-7's eigene Rechnung).

VORAB-REGISTRIERTE Falsifikations-Kriterien (fixiert vor dem Lauf):

  - OPEN_SUBSTRATE : Es existiert eine (f, a, N, S)-Region mit
    τ_OR < τ_dec (OR schlägt Dekohärenz) UND τ_OR im physiologischen
    Bereich [1e-5, 1e-1] s — innerhalb großzügiger HYPOTHESE-Bereiche
    (f ≤ 5e-2, a ≤ 8 nm, N ≤ 1e11, S ≤ 1e6).
  - FALSIFIED_EVERYWHERE : keine viable Kombination in diesen Bereichen.
  - Zusätzlich gemeldet: ob ohne Shielding (S=1) IRGENDETWAS viable ist
    (ehrliche Erhaltung von Tegmarks Kernbefund für bulk water).

CORRECTION-Log (Fehler in iter-7, transparent dokumentiert):

  1. iter-7 nutzte E_G = ħ²/(G·m²·τ_min) — **dimensional invalid**:
     ħ²/(G·m²·τ) hat Einheit J·s/m, nicht J. Das berechnete
     "E_G = 186 J" für ein Protein und τ_collapse = 5.66e-37 s sind
     Artefakte dieser Formel.
  2. iter-7's Kriterium war invertiert: Orch-OR braucht τ_OR < τ_dec
     (die objektive Reduktion MUSS vor der Umgebungs-Dekohärenz
     greifen); iter-7 wertete τ_collapse > τ_decoherence als "viable"
     und bekam die Interpretation der Ratio falsch herum.

KORREKTE Penrose-Formel (Penrose 1994; Hagan et al. 2002):

  E_G = G·(ΔM)²/a   (Gravitations-Selbstenergie der verschobenen
                     Massen-Differenz),  τ_OR = ħ/E_G

  - Kollektiv korreliert: E_G(N) = N²·G·(ΔM)²/a → τ_OR ∝ 1/N².
  - Unkorreliert: E_G(N) = N·G·(ΔM)²/a → τ_OR ∝ 1/N.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HBAR = 1.054_571_817e-34      # J·s
KB = 1.380_649e-23            # J/K
G_NEWTON = 6.674_30e-11       # m³/kg/s²
M_TUBULIN_KG = 1.83e-22       # 110 kDa
T_BRAIN_K = 310.0
M_PROTON_KG = 1.672_621_923e-27

# Vorab-registrierte HYPOTHESE-Bereiche (großzügig, dokumentiert)
F_FRACS = (1e-3, 1e-2, 5e-2)          # Konformations-Masseanteil ΔM/m
A_DISPLACEMENTS_NM = (1.0, 2.5, 8.0)  # Verschiebung
N_TUBULINS = (1e8, 1e9, 1e10, 1e11)   # Hameroff: 10⁹⁻¹¹ pro Neuron
SHIELDINGS = (1.0, 1e2, 1e4, 1e6)     # S: ordered water, Debye, Gel
TAU_OR_PHYSIOLOGICAL = (1e-5, 1e-1)   # Hameroff-Penrose-Zielbereich
DELTA_M_OVER_M_BULK = 0.01            # Tegmark-Parameter (iter-7-Kontinuität)


def tegmark_tau_dec_bulk_s() -> float:
    """Tegmark 2000 bulk-water: τ = ħ/(k_B·T·(Δm/m)²)."""
    return HBAR / (KB * T_BRAIN_K * DELTA_M_OVER_M_BULK**2)


def penrose_tau_or_s(
    delta_mass_kg: float,
    displacement_m: float,
    n_tubulins: float,
    correlated: bool,
) -> float:
    """Korrekte Penrose-Rechnung: E_G = G·(ΔM)²/a; τ_OR = ħ/E_G.

    Korreliert: E_G ∝ N²; unkorreliert: E_G ∝ N.
    """
    e_single = G_NEWTON * delta_mass_kg**2 / displacement_m
    e_collective = e_single * (n_tubulins**2 if correlated else n_tubulins)
    return HBAR / e_collective


def iter7_artifact_flag() -> dict[str, float | str]:
    """Dimension-Check der iter-7-Formel: ħ²/(G·m²·τ) hat Einheit
    J·s/m — KEINE Energie. "E_G = 186 J" für ein Protein ist Artefakt."""
    tau_min = 8e-9 / 3e8
    e_g_artifact = (HBAR**2) / (G_NEWTON * M_TUBULIN_KG**2 * tau_min)
    e_g_correct = G_NEWTON * M_TUBULIN_KG**2 / 8e-9
    return {
        "e_g_artifact_j": e_g_artifact,
        "tau_collapse_artifact_s": HBAR / e_g_artifact,
        "dimension_of_iter7_formula": "J·s/m (invalid — korrekt wäre J)",
        "e_g_corrected_dimer_j": e_g_correct,
        "tau_or_corrected_dimer_s": HBAR / e_g_correct,
    }


def hagan_ballpark_check() -> dict[str, float]:
    """Hagans Ballpark: Proton-Displacement, korreliert, N ≈ 1e9
    → τ_OR im 1e-4…1e-3-s-Bereich?"""
    return {
        "tau_or_N1e9_proton_s": penrose_tau_or_s(M_PROTON_KG, 2.5e-9, 1e9, True),
        "tau_or_N1e10_proton_s": penrose_tau_or_s(M_PROTON_KG, 2.5e-9, 1e10, True),
        "hagan_claim_s": 1e-4,
    }


def phase_diagram() -> dict[str, Any]:
    """Sweep (f, a, N, korrelated, S): viable ⟺ τ_OR < τ_dec UND
    τ_OR physiologisch ([1e-5, 1e-1] s)."""
    tau_dec_bulk = tegmark_tau_dec_bulk_s()
    viable_bulk_unshielded = 0
    viable_total = 0
    viable_configs: list[dict[str, float | bool]] = []
    best_ratio = 0.0
    best_cfg: dict[str, float | bool] = {}

    for f in F_FRACS:
        for a_nm in A_DISPLACEMENTS_NM:
            for n in N_TUBULINS:
                delta_m = f * M_TUBULIN_KG
                for correlated in (True, False):
                    tau_or = penrose_tau_or_s(delta_m, a_nm * 1e-9, n, correlated)
                    for s in SHIELDINGS:
                        tau_dec = tau_dec_bulk * s
                        if tau_or < tau_dec:
                            if s == 1.0:
                                viable_bulk_unshielded += 1
                            if TAU_OR_PHYSIOLOGICAL[0] <= tau_or <= TAU_OR_PHYSIOLOGICAL[1]:
                                viable_total += 1
                                ratio = tau_or / tau_dec
                                cfg = {
                                    "f_frac": f,
                                    "a_nm": a_nm,
                                    "N": n,
                                    "S": s,
                                    "correlated": correlated,
                                    "tau_or_s": tau_or,
                                    "tau_dec_s": tau_dec,
                                    "ratio": ratio,
                                }
                                viable_configs.append(cfg)
                                if ratio > best_ratio:
                                    best_ratio = ratio
                                    best_cfg = cfg
    return {
        "tau_dec_bulk_s": tau_dec_bulk,
        "viable_bulk_unshielded": viable_bulk_unshielded,
        "viable_physiological": viable_total,
        "best_ratio": best_ratio,
        "best_cfg": best_cfg,
    }


if __name__ == "__main__":
    print("=== iter-16: Orch-OR unter der Hagan-Parametrisierung ===\n")

    print("CORRECTION-Log (iter-7-Artefakte):")
    art = iter7_artifact_flag()
    print(f"  iter-7 E_G (Artefakt)      : {art['e_g_artifact_j']:.2e} J (dimensional invalid)")
    print(f"  iter-7 τ_collapse (Artefakt): {art['tau_collapse_artifact_s']:.2e} s")
    print(f"  korrekt (Dimer, 8nm)       : E_G = {art['e_g_corrected_dimer_j']:.2e} J → "
          f"τ_OR = {art['tau_or_corrected_dimer_s']:.2e} s")

    print("\nHagan-Ballpark (Proton-Displacement, korreliert):")
    ball = hagan_ballpark_check()
    print(f"  N=1e9  : τ_OR = {ball['tau_or_N1e9_proton_s']:.2e} s")
    print(f"  N=1e10 : τ_OR = {ball['tau_or_N1e10_proton_s']:.2e} s")

    result = phase_diagram()
    print(f"\nTegmark-bulk τ_dec (S=1): {result['tau_dec_bulk_s']:.2e} s")
    print(f"Viable Konfigs mit physiologischem τ_OR: {result['viable_physiological']}")
    print(f"Viable OHNE Shielding (S=1, bulk): {result['viable_bulk_unshielded']}")
    if result["best_cfg"]:
        b = result["best_cfg"]
        print(f"Beste Region: f={b['f_frac']:.0e}, a={b['a_nm']:.1f}nm, N={b['N']:.0e}, "
              f"S={b['S']:.0e}, correlated={b['correlated']} → τ_OR/τ_dec = {b['ratio']:.2e}")

    if result["viable_physiological"] > 0:
        signal = "OPEN_SUBSTRATE"
        interpretation = (
            "Eine viable (f, a, N, S)-Region existiert. Orch-OR's Substrat ist "
            "numerisch OFFEN unter Hagan-Parametrisierung + Shielding — iter-7s "
            "27-Dekaden-CONTRADICTION war ein Formel-Artefakt. Tegmarks bulk-"
            "Befund bleibt ohne Shielding konsistent."
        )
    else:
        signal = "FALSIFIED_EVERYWHERE"
        interpretation = (
            "Keine viable Kombination in großzügigen HYPOTHESE-Bereichen — "
            "Orch-OR bleibt in ZELLSIM-Rahmen falsifiziert; iter-7 qualitativ "
            "bestätigt (mit korrigierter Begründung)."
        )

    print(f"\nSignal: {signal}")
    print(f"Interpretation: {interpretation}")

    out: dict[str, Any] = {
        **art,
        **ball,
        **result,
        "signal": signal,
        "interpretation": interpretation,
        "next_vectors": [
            "Falls OPEN_SUBSTRATE: S≈1e5–1e6 als HYPOTHESE-Region markieren; empirischer "
            "Prüfstein: gemessene Burst-Raten (Kurian-Typ) + UV-Chemie in Trp-reichen Zellen",
            "Falls OPEN: UV-Sync re-opened mit Limit-Cycle-Basis (iter-2-Artefakt vermeiden)",
            "Falls FALSIFIED: LIMITATIONS.md-Status bleibt; iter-7-Begründung korrigiert",
        ],
    }
    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"→ Wrote {target}")