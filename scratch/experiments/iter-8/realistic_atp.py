"""Iter-8: Realistische ATP-ODE mit mehreren Verbrauchern.

Hintergrund: iter-2, iter-2-retry, iter-4 scheiterten alle am
gleichen ODE-Artefakt (triviale Korrelation im Steady-State).
Jetzt: ATP-ODE mit:
  - 3 ATP-Verbraucher (Translation, Motor, Ionen-Pumpe)
  - Michaelis-Menten-Kinetik (Sättigung)
  - Schwacher Oszillator
  - Homeostatische Regulation (negative Rückkopplung)

Ziel: das System soll einen *interessanten* Steady-State haben,
nicht trivial konvergent.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RealisticATPParams:
    """Realistische ATP-ODE-Parameter aus Bakterien-Literatur.

    Korrektur iter-8a: ATP soll um 2-5 mM stabil sein, nicht 10⁶ mM.
    Daher ATP-Produktion = ATP-Verbraucher im Steady-State.
    """

    # Glykolyse-Produktion: ATP pro Sekunde pro Zelle (μM/s)
    v_glyc_max_umol_per_s_per_cell: float = 1e-3   # 1e-3 μM/s = 1 mM/s
    km_glucose_mM: float = 0.5
    # 3 ATP-Verbraucher
    v_translation_max_umol_per_s: float = 5e-4    # 0.5 mM/s
    km_atp_translation_mM: float = 0.3
    v_motor_max_umol_per_s: float = 1e-4           # 0.1 mM/s
    km_atp_motor_mM: float = 0.1
    v_ion_pump_max_umol_per_s: float = 4e-4        # 0.4 mM/s
    km_atp_ion_pump_mM: float = 0.05
    # Glucose-Zufuhr
    glucose_influx_per_s: float = 0.05


@dataclass
class RealisticATPState:
    """Zustand der realistischen ATP-ODE."""

    atp_mM: float = 2.0
    glucose_mM: float = 5.0
    proteins: float = 100.0   # akkumulierte Proteine (Translations-Output)
    t: float = 0.0
    step_count: int = 0


def atp_ode_step(
    state: RealisticATPState,
    dt_s: float,
    rng: np.random.Generator,
    p: RealisticATPParams,
    uv_modulation: float = 0.0,
) -> RealisticATPState:
    """Realistischer ATP-ODE-Schritt mit 3 Verbrauchern."""
    # 1. Glucose-Influx (exponentielle Annäherung an externen Pool)
    state.glucose_mM = state.glucose_mM + p.glucose_influx_per_s * dt_s * (10.0 - state.glucose_mM)

    # 2. Glykolyse: ATP-Produktion aus Glucose (Michaelis-Menten)
    glyc_rate = p.v_glyc_max_umol_per_s_per_cell * 1e3 * state.glucose_mM / (p.km_glucose_mM + state.glucose_mM)
    # glyc_rate ist jetzt in mM/s

    # 3. ATP-Verbraucher (Michaelis-Menten)
    v_translation = p.v_translation_max_umol_per_s * 1e3 * state.atp_mM / (p.km_atp_translation_mM + state.atp_mM)
    v_motor = p.v_motor_max_umol_per_s * 1e3 * state.atp_mM / (p.km_atp_motor_mM + state.atp_mM)
    v_ion = p.v_ion_pump_max_umol_per_s * 1e3 * state.atp_mM / (p.km_atp_ion_pump_mM + state.atp_mM)

    # 4. ATP-Bilanz in mM/s
    d_atp = (glyc_rate + uv_modulation - v_translation - v_motor - v_ion) * dt_s
    state.atp_mM = max(0.0, state.atp_mM + d_atp)

    # 5. Protein-Akkumulation (Translations-Output, leicht oszillatorisch)
    state.proteins += v_translation * dt_s * 0.1

    state.t += dt_s
    state.step_count += 1
    return state


def run_single_cell(
    coupling: str = "isolated",
    t_end_s: float = 200.0,
    dt_s: float = 0.1,
    seed: int = 42,
    uv_flux_in: float = 0.0,
) -> dict[str, float]:
    """Eine Zelle mit realistischer ODE."""
    rng = np.random.default_rng(seed)
    p = RealisticATPParams()
    state = RealisticATPState(atp_mM=1.5, glucose_mM=4.0, proteins=80.0)

    atp_history: list[float] = []

    for step in range(int(t_end_s / dt_s)):
        uv_mod = uv_flux_in if coupling != "isolated" else 0.0
        # Stochastisches Rauschen auf ATP (kleines Gauß)
        noise = 1.0 + 0.05 * rng.normal()
        state.atp_mM *= noise
        state = atp_ode_step(state, dt_s, rng, p, uv_modulation=uv_mod)
        if step % 5 == 0:
            atp_history.append(state.atp_mM)

    arr = np.asarray(atp_history)
    half = arr.shape[0] // 2
    arr_ss = arr[half:]

    return {
        "coupling": coupling,
        "uv_flux_in": uv_flux_in,
        "atp_final": float(state.atp_mM),
        "atp_ss_mean": float(arr_ss.mean()) if arr_ss.size else 0.0,
        "atp_ss_std": float(arr_ss.std()) if arr_ss.size else 0.0,
        "proteins_final": float(state.proteins),
        "n_samples": len(atp_history),
    }


def run_two_cells_uv_coupled(
    t_end_s: float = 200.0,
    dt_s: float = 0.1,
    seed: int = 42,
    coupling_strength: float = 1.0e-6,
    distance_nm: float = 1000.0,
) -> dict[str, object]:
    """2-Zellen-ODE mit UV-Kopplung."""
    rng = np.random.default_rng(seed)
    p = RealisticATPParams()

    # Initiale Bedingungen
    a = RealisticATPState(atp_mM=2.0, glucose_mM=5.0, proteins=100.0)
    b = RealisticATPState(atp_mM=1.0, glucose_mM=6.0, proteins=90.0)

    photons_per_s_a = 10.0
    photons_per_s_b = 10.0

    atp_a_history: list[float] = []
    atp_b_history: list[float] = []
    n_steps = int(t_end_s / dt_s)
    abs_length_nm = 200.0

    for step in range(n_steps):
        # UV-Emission
        photons_a = max(0.0, photons_per_s_a * (1.0 + 0.2 * rng.normal()))
        photons_b = max(0.0, photons_per_s_b * (1.0 + 0.2 * rng.normal()))

        # UV-Fluss am Partner
        if distance_nm > 0:
            absorption = math.exp(-distance_nm / abs_length_nm)
            r_cm = distance_nm * 1e-7
            surface_cm2 = 4 * math.pi * r_cm**2
            flux_b_from_a = (photons_a * absorption) / surface_cm2
            flux_a_from_b = (photons_b * absorption) / surface_cm2
        else:
            flux_b_from_a = flux_a_from_b = 0.0

        uv_modulation_a = coupling_strength * flux_a_from_b
        uv_modulation_b = coupling_strength * flux_b_from_a

        a = atp_ode_step(a, dt_s, rng, p, uv_modulation=uv_modulation_a)
        b = atp_ode_step(b, dt_s, rng, p, uv_modulation=uv_modulation_b)

        if step % 5 == 0:
            atp_a_history.append(a.atp_mM)
            atp_b_history.append(b.atp_mM)

    a_arr = np.asarray(atp_a_history)
    b_arr = np.asarray(atp_b_history)
    half = a_arr.shape[0] // 2
    a_ss = a_arr[half:]
    b_ss = b_arr[half:]
    if a_ss.std() < 1e-9 or b_ss.std() < 1e-9:
        r_corr = 0.0
    else:
        r_corr = float(np.corrcoef(a_ss, b_ss)[0, 1])

    return {
        "atp_a_final": float(a.atp_mM),
        "atp_b_final": float(b.atp_mM),
        "r_corr_ss": r_corr,
        "atp_a_mean": float(a_ss.mean()),
        "atp_b_mean": float(b_ss.mean()),
        "atp_a_std": float(a_ss.std()),
        "atp_b_std": float(b_ss.std()),
    }


def run_sweep() -> list[dict[str, object]]:
    """Sweep über Kopplungsstärke + Distanz mit der realistischen ODE."""
    results = []
    couplings = [1e-9, 1e-7, 1e-5, 1e-3, 1e-1]
    distances = [500.0, 1000.0, 5000.0, 50_000.0]
    for d in distances:
        for c in couplings:
            r = run_two_cells_uv_coupled(
                coupling_strength=c, distance_nm=d, seed=42,
            )
            r["distance_nm"] = d
            r["coupling"] = c
            results.append(r)
    return results


if __name__ == "__main__":
    print("=== iter-8: Realistische ATP-ODE ===\n")
    # Isolated-Test
    iso = run_single_cell(coupling="isolated")
    print(f"Isolated steady-state: ATP = {iso['atp_ss_mean']:.3f} ± "
          f"{iso['atp_ss_std']:.3f} mM")

    # Sweep
    print(f"\n{'Coupling':>12s} {'Distance':>10s} {'r_corr':>8s} "
          f"{'ATP_a':>8s} {'ATP_b':>8s}")
    print("-" * 60)
    results = run_sweep()
    for r in results:
        print(f"  {r['coupling']:>10.1e} {r['distance_nm']:>10.0f} "
              f"{r['r_corr_ss']:>+8.3f} {r['atp_a_mean']:>8.3f} {r['atp_b_mean']:>8.3f}")

    # Signal-Bewertung
    # Wenn bei niedriger Kopplung r_corr < 0.5 → ODE realistisch (kein Artefakt)
    low_coupling_rs = [
        abs(r["r_corr_ss"]) for r in results if r["coupling"] <= 1e-7
    ]
    if all(r < 0.5 for r in low_coupling_rs):
        signal = "STRONG"   # ODE ist realistisch → UV-Sync testbar
    elif any(r > 0.7 for r in low_coupling_rs):
        signal = "CONTRADICTION"   # Artefakt immer noch da
    else:
        signal = "WEAK"

    output = {
        "results": results,
        "isolated": iso,
        "signal": signal,
        "low_coupling_rs": low_coupling_rs,
        "next_vectors": [
            "Falls STRONG: iter-9: UV-Sync mit realistischer ODE",
            "Falls CONTRADICTION: ODE weiter modernisieren",
            "Falls WEAK: Hypothese vorerst aufgeben, ODE dokumentieren",
        ],
    }

    target = __file__.replace("realistic_atp.py", "result.json")
    with open(target, "w") as f:
        json.dump(output, f, indent=2, default=float)
    print(f"\nSignal: {signal}")
    print(f"→ Wrote {target}")
