"""Iter-7: Penrose-Hameroff Orchestrated Objective Reduction (Orch-OR).

Hypothese: Quanten-Superpositionen in Mikrotubuli (Tubulin-Dimeren)
kollabieren spontan nach τ ≈ ħ/E_G (Penrose), wo E_G die
Gravitations-Selbstenergie ist. Dies soll mit Bewusstsein korreliert
sein.

Quellen:
  - Penrose, R. (1989): "The Emperor's New Mind"
  - Hameroff, S. & Penrose, R. (2014): "Consciousness in the universe:
    A review of the Orch-OR theory" — Phys. Life Rev. 11, 39
  - Tegmark, M. (2000): "Importance of quantum decoherence in brain
    processes" — Phys. Rev. E 61, 4194 (KRITIK)
  - Hagan, S. et al. (2002): "Quantum computation in brain microtubules:
    Decoherence and biological feasibility" — Phys. Rev. E 65, 061901
    (ANTWORT auf Tegmark)

Vorhersage der Theorie:
- Mikrotubuli-Dimer αβ-Tubulin haben 10⁹ Tubuline/ Neuron
- Jedes Dimer ist ein Qubit (dipol-Orientierung)
- Quanten-kohärenz dauert ~10⁻⁵ bis 10⁻⁴ s (Hameroff-Schätzung)
- In dieser Zeit: ~10⁴-10⁵ Kohärenz-Zyklen

Kritik (Tegmark 2000):
- Im warmen, nassen Gehirn ist Dekohärenz-Zeit τ ≈ 10⁻¹³ s
- Viel kürzer als relevante kognitive Zeitskalen
- Orch-OR müsste gegen Wärme-Bewegung isolieren

Wir prüfen die numerische Größenordnung und entscheiden via
CellsimMixMind, ob die Theorie physikalisch haltbar ist.
"""

from __future__ import annotations

import json

HBAR = 1.054_571_817e-34     # J·s
KB = 1.380_649e-23         # J/K
C_LIGHT = 299_792_458.0     # m/s
G_NEWTON = 6.674_30e-11     # m³/kg/s²


def penrose_self_energy_j(diameter_nm: float) -> float:
    """Penrose E_G = ħ / τ_G mit τ_G = ħ / (E_G).

    Vereinfacht: E_G = ħ²/(G · m² · τ)
    """
    # Mass eines Tubulin-Dimers ~ 110 kDa = 1.83e-22 kg
    mass_kg = 1.83e-22
    diameter_m = diameter_nm * 1e-9
    # E_G ≈ ħ² / (G · m² · τ_min)
    # Mit τ_min ≈ diameter/c (Licht-Laufzeit)
    tau_min = diameter_m / C_LIGHT
    e_g = (HBAR ** 2) / (G_NEWTON * mass_kg ** 2 * tau_min)
    return e_g


def penrose_collapse_time_s(diameter_nm: float) -> float:
    """τ = ħ / E_G."""
    e_g = penrose_self_energy_j(diameter_nm)
    return HBAR / e_g


def tegmark_decoherence_time_s(temperature_K: float) -> float:
    """Tegmark's Dekohärenz-Zeit im warmen Gehirn/Cytoplasma.

    τ_decoherence ≈ ħ / (k_B · T · (Δm/m)²)

    Vereinfacht: für einen Tubulin-Dimer bei 310 K mit Δm/m ≈ 0.01.
    """
    delta_m_over_m = 0.01
    return HBAR / (KB * temperature_K * delta_m_over_m ** 2)


def decoherence_vs_collapse(
    diameter_nm: float = 8.0,    # typischer Mikrotubulus-Durchmesser
    temperature_K: float = 310.0,
) -> dict[str, float]:
    """Vergleicht Penrose τ_collapse mit Tegmark τ_decoherence."""
    tau_collapse = penrose_collapse_time_s(diameter_nm)
    tau_decoherence = tegmark_decoherence_time_s(temperature_K)
    ratio = tau_collapse / tau_decoherence
    return {
        "tau_collapse_s": tau_collapse,
        "tau_decoherence_s": tau_decoherence,
        "ratio_collapse_to_decoherence": ratio,
        "is_viable": ratio > 1.0,
    }


def microtubule_count_per_neuron() -> int:
    """Hameroff-Schätzung: ~10⁹ Tubulin-Dimere pro Neuron."""
    return 10 ** 9


def coherent_cycles_estimate(diameter_nm: float = 8.0, temperature_K: float = 310.0) -> dict[str, float]:
    """Wie viele Quanten-Zyklen in der kohärenten Zeit?

    cycle_duration = τ_decoherence (realistischste Schätzung)
    cognitive_timescale = 0.1 s (100 ms — typisches Bewusstseins-Update)
    """
    decoherence = tegmark_decoherence_time_s(temperature_K)
    collapse = penrose_collapse_time_s(diameter_nm)
    cognitive = 0.1
    # Wie viele Dekohärenz-Zyklen passen in eine Bewusstseins-Zeitskala?
    decoherence_cycles = cognitive / decoherence
    collapse_cycles = cognitive / collapse
    return {
        "decoherence_time_s": decoherence,
        "collapse_time_s": collapse,
        "decoherence_cycles_per_cognitive_step": decoherence_cycles,
        "collapse_cycles_per_cognitive_step": collapse_cycles,
        "hameroff_claim_104": 1e4,
        "teemark_claim_zero": 0,
    }


def run_iter7() -> dict[str, object]:
    """Hauptfunktion für iter-7."""
    # Hauptvergleich: Penrose-Collapse vs. Tegmark-Dekohärenz
    d_microtubule = 8.0  # nm
    results = decoherence_vs_collapse(d_microtubule, 310.0)
    cycles = coherent_cycles_estimate(d_microtubule, 310.0)

    # Vorhersage der Theorie
    cycles_hameroff = cycles["hameroff_claim_104"]
    cycles_actual = cycles["decoherence_cycles_per_cognitive_step"]

    # Signal-Bewertung
    # Wenn τ_collapse >> τ_decoherence → Orch-OR funktioniert
    # Wenn τ_collapse << τ_decoherence → Tegmark hat recht
    if results["ratio_collapse_to_decoherence"] > 100:
        signal = "STRONG"
    elif results["ratio_collapse_to_decoherence"] > 1.0:
        signal = "WEAK"
    elif results["ratio_collapse_to_decoherence"] > 0.01:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"   # Orch-OR kollabiert (Tegmark bestätigt)

    return {
        "tau_collapse_s": results["tau_collapse_s"],
        "tau_decoherence_s": results["tau_decoherence_s"],
        "ratio": results["ratio_collapse_to_decoherence"],
        "decoherence_cycles_per_cognitive_step": cycles_actual,
        "hameroff_claim_104_cycles": cycles_hameroff,
        "signal": signal,
        "is_viable": results["is_viable"],
        "next_vectors": [
            "Falls CONTRADICTION: → Orch-OR als Theorie verwerfen? Oder Hagan-Antwort prüfen (structured water)?",
            "Falls WEAK: → iter-7b mit strukturiertem Wasser (Debye-Hückel-Effekt)",
            "Falls STRONG: → iter-7c mit realistischen Tubulin-Daten",
        ],
    }


if __name__ == "__main__":
    result = run_iter7()
    print("=== iter-7: Penrose-Hameroff Orch-OR ===\n")
    print(f"Penrose τ_collapse:   {result['tau_collapse_s']:.3e} s")
    print(f"Tegmark τ_decoherence: {result['tau_decoherence_s']:.3e} s")
    print(f"Ratio (collapse/decoherence): {result['ratio']:.3e}")
    print(f"\nDekohärenz-Zyklen pro 100 ms Bewusstseins-Update: "
          f"{result['decoherence_cycles_per_cognitive_step']:.3e}")
    print(f"Hameroffs behauptete 10⁴ Zyklen: {result['hameroff_claim_104_cycles']:.0e}")
    print(f"\nIs Orch-OR viable? {result['is_viable']}")
    print(f"Signal: {result['signal']}")

    if result["signal"] == "CONTRADICTION":
        print(
            "\nBefund: Penrose-Collapse-Zeit ist viel KÜRZER als die "
            "Dekohärenz-Zeit. Das bedeutet: Quanten-Superpositionen "
            "kollabieren VOR ihrer Entstehung — Orch-OR ist nicht "
            "physikalisch realisierbar."
        )

    target = __file__.replace("orch_or.py", "result.json")
    with open(target, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"\n→ Wrote {target}")
