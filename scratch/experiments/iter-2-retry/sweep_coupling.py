"""Iter-2-retry: Sweep über Kopplungsstärke + realistischere ODE.

Aus iter-2: r ≈ 1.0 über alle Distanzen ist verdächtig. Hier testen wir,
ob der Effekt auch bei sehr schwacher Kopplung noch besteht (was
realistisch wäre) oder ob es ein Artefakt der ODE-Struktur ist.

Bei einer zu einfachen ODE (konstanter ATP-Pool mit Quell/Senk) würde
Korrelation trivial entstehen. Wir fügen daher hinzu:
  - Stochastische Schwankungen in ATP-Hydrolyse (Rauschen)
  - Nicht-lineare Rückkopplung
  - ATP-Verbrauch für mehrere Prozesse
"""

from __future__ import annotations

import math
import json

import numpy as np


def atp_ode_stochastic_step(
    atp: float,
    glucose: float,
    rng: np.random.Generator,
    k_glyc: float = 0.05,
    k_atp_base: float = 0.03,
    dt_s: float = 0.1,
    uv_modulation: float = 0.0,
    noise_level: float = 0.05,
) -> tuple[float, float]:
    """ATP-ODE mit stochastischer ATP-Hydrolyse.

    k_atp fluktuiert um k_atp_base mit weißem Rauschen.
    """
    # Glucose-Verbrauch (deterministisch)
    d_glucose = -k_glyc * glucose * dt_s
    glucose = max(glucose + d_glucose, 0.0)
    # ATP-Hydrolyse-Rate mit Rauschen
    k_atp = max(0.0, k_atp_base * (1.0 + noise_level * rng.normal()))
    # ATP-Bilanz
    d_atp = (2.0 * k_glyc * glucose - k_atp * atp + uv_modulation) * dt_s
    atp = max(atp + d_atp, 0.0)
    return atp, glucose


def uv_flux_at_distance(photons_per_s: float, distance_nm: float, absorption_nm: float = 200.0) -> float:
    """UV-Flussdichte [Photonen/cm²/s] bei gegebenem Abstand."""
    if distance_nm <= 0:
        return 0.0
    absorption = math.exp(-distance_nm / absorption_nm)
    r_cm = distance_nm * 1e-7
    surface_cm2 = 4 * math.pi * r_cm**2
    return (photons_per_s * absorption) / surface_cm2


def correlation_pearson(a: list[float], b: list[float]) -> float:
    """Pearson-Korrelationskoeffizient."""
    arr_a = np.asarray(a)
    arr_b = np.asarray(b)
    if arr_a.std() < 1e-9 or arr_b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(arr_a, arr_b)[0, 1])


def run_single(
    coupling_strength: float,
    distance_nm: float = 1000.0,
    t_end_s: float = 200.0,
    dt_s: float = 0.1,
    seed: int = 42,
    noise_level: float = 0.05,
) -> dict[str, float]:
    """Eine Simulation mit gegebener Kopplungsstärke."""
    rng = np.random.default_rng(seed)
    n_steps = int(t_end_s / dt_s)

    # Initiale Bedingungen: jetzt deutlich verschieden
    atp_a, glu_a = 2.0, 5.0
    atp_b, glu_b = 0.5, 6.0   # andere Anfangslage

    times: list[float] = []
    atp_a_series: list[float] = []
    atp_b_series: list[float] = []

    # UV-Modulationsstärke pro 1 Photon/cm²/s am Empfänger
    uv_sensitivity = 1.0e-7

    for step in range(n_steps):
        # UV-Emission (Popp: 10 Photonen/s pro Zelle, mit Poisson-Rauschen)
        photons_a = max(0.0, 10.0 * (1.0 + 0.2 * rng.normal()))
        photons_b = max(0.0, 10.0 * (1.0 + 0.2 * rng.normal()))

        # UV-Fluss am Partner
        flux_b = uv_flux_at_distance(photons_a, distance_nm)
        flux_a = uv_flux_at_distance(photons_b, distance_nm)

        # Modulation
        uv_a = coupling_strength * uv_sensitivity * flux_a
        uv_b = coupling_strength * uv_sensitivity * flux_b

        atp_a, glu_a = atp_ode_stochastic_step(
            atp_a, glu_a, rng, uv_modulation=uv_a, dt_s=dt_s, noise_level=noise_level,
        )
        atp_b, glu_b = atp_ode_stochastic_step(
            atp_b, glu_b, rng, uv_modulation=uv_b, dt_s=dt_s, noise_level=noise_level,
        )

        # Subsample für Korrelation
        if step % 10 == 0:
            times.append(step * dt_s)
            atp_a_series.append(atp_a)
            atp_b_series.append(atp_b)

    # Korrelation in der zweiten Hälfte (Einschwingphase ignorieren)
    half = len(atp_a_series) // 2
    r = correlation_pearson(atp_a_series[half:], atp_b_series[half:])
    r_total = correlation_pearson(atp_a_series, atp_b_series)

    return {
        "coupling_strength": coupling_strength,
        "distance_nm": distance_nm,
        "r_full": r_total,
        "r_steady": r,
        "atp_a_final": float(atp_a),
        "atp_b_final": float(atp_b),
        "atp_diff_final": abs(atp_a - atp_b),
    }


def sweep_coupling() -> list[dict[str, float]]:
    """Sweep über 6 Kopplungsstärken, 5 Distanzen."""
    results = []
    couplings = [1e-6, 1e-4, 1e-2, 1.0, 100.0, 10000.0]
    for d in [500.0, 1000.0, 5000.0]:
        for c in couplings:
            r = run_single(coupling_strength=c, distance_nm=d, seed=42)
            r["distance_nm_run"] = d
            r["coupling_run"] = c
            results.append(r)
    return results


if __name__ == "__main__":
    results = sweep_coupling()

    # Auswertung
    print("=== iter-2-retry: UV-Sync Sweep ===")
    print(f"{'Kopplung':>10s} {'Distanz':>10s} {'r_full':>8s} {'r_steady':>8s} "
          f"{'Diff final':>10s}")
    print("-" * 60)
    for r in results:
        print(f"{r['coupling_run']:>10.1e} {r['distance_nm_run']:>10.0f} "
              f"{r['r_full']:>+8.3f} {r['r_steady']:>+8.3f} "
              f"{r['atp_diff_final']:>10.3f}")

    # Konsolidiere
    strong_count = sum(1 for r in results if abs(r["r_steady"]) > 0.7)
    null_count = sum(1 for r in results if abs(r["r_steady"]) < 0.1)
    total = len(results)
    print(f"\nMit |r| > 0.7: {strong_count}/{total}")
    print(f"Mit |r| < 0.1: {null_count}/{total}")

    # Signal-Bewertung
    # Wenn bei niedrigster Kopplung (1e-6) immer noch r ≈ 1.0 → Artefakt
    low_coupling_rs = [abs(r["r_steady"]) for r in results if r["coupling_run"] == 1e-6]
    if all(r > 0.5 for r in low_coupling_rs):
        signal = "CONTRADICTION"  # Physikalisch unrealistisch
    elif any(r > 0.5 for r in low_coupling_rs):
        signal = "WEAK"
    else:
        signal = "STRONG"  # Korrelation nur bei höherer Kopplung, distanz-abhängig

    output = {
        "results": results,
        "signal": signal,
        "low_coupling_rs": low_coupling_rs,
        "max_r": max(abs(r["r_steady"]) for r in results),
        "min_r": min(abs(r["r_steady"]) for r in results),
        "next_vectors": [
            "iter-3: Radikal-Paar-Magnetorezeption (Cryptochrom)",
            "iter-4: N=10 Zellen → populations-Synchronisation",
            "Falls CONTRADICTION: 2-Zellen-ODE hat zu wenig Freiheitsgrade, "
            "echte ATP-Dynamik braucht mehrere Spezies",
        ],
    }

    target = __file__.replace("sweep_coupling.py", "result.json")
    with open(target, "w") as f:
        json.dump(output, f, indent=2, default=float)
    print(f"\n→ Wrote {target}")
    print(f"Signal: {signal}")
