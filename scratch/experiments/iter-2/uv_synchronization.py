"""Iter-2: UV-Phasen-Synchronisation zwischen 2 Zellen.

Modelliert 2 Zellen A und B mit:
  - ATP-ODE (Glykolyse + Synthase + Hydrolyse)
  - EM-Kopplung über UV-Biophotonen
  - Feedback: UV moduliert ATP-Synthase-Rate
"""

from __future__ import annotations

import math

import numpy as np

# Konsistente Konstanten
h_planck = 6.626_070_15e-34
c_light = 299_792_458.0


def atp_ode_step(
    atp: float,
    glucose: float,
    k_glyc: float = 0.05,
    k_atp: float = 0.03,
    dt_s: float = 0.1,
    uv_modulation: float = 0.0,
) -> tuple[float, float]:
    """Ein ODE-Schritt für ATP mit UV-Modulation.

    uv_modulation: zusätzliche ATP-Synthase-Rate durch UV-Absorption.
    """
    # Glucose-Verbrauch
    d_glucose = -k_glyc * glucose * dt_s
    glucose = max(glucose + d_glucose, 0.0)
    # ATP-Produktion aus Glucose + UV-Modulation
    d_atp = (2.0 * k_glyc * glucose - k_atp * atp + uv_modulation) * dt_s
    atp = max(atp + d_atp, 0.0)
    return atp, glucose


def chemolumineszenz(atp: float, factor: float = 1.0e-5) -> float:
    """UV-Photonen/s proportional zur ATP-Hydrolyse."""
    # Vereinfacht: konstanter ATP-Fluss = 10⁶/s, Ausbeute 1e-5
    return factor * 1.0e6


def uv_flux_at_distance(photons_per_s: float, distance_nm: float, absorption_nm: float = 200.0) -> float:
    """UV-Flussdichte [Photonen/cm²/s] bei gegebenem Abstand."""
    if distance_nm <= 0:
        return 0.0
    absorption = math.exp(-distance_nm / absorption_nm)
    r_cm = distance_nm * 1e-7
    surface_cm2 = 4 * math.pi * r_cm**2
    return (photons_per_s * absorption) / surface_cm2


def uv_modulation_from_flux(flux_density: float, sensitivity: float = 1.0e-5) -> float:
    """ATP-Synthase-Modulation aus UV-Flussdichte [mM/s]."""
    return sensitivity * flux_density


def run_iter2(
    t_end_s: float = 100.0,
    dt_s: float = 0.1,
    distance_nm: float = 1000.0,
    coupling_strength: float = 1.0,
) -> dict[str, object]:
    """Hauptfunktion für iter-2: 2-Zellen-Synchronisation."""
    n_steps = int(t_end_s / dt_s)

    # Initiale Bedingungen (leicht unterschiedlich → Synchronisation beobachtbar)
    atp_a, glu_a = 2.0, 5.0
    atp_b, glu_b = 2.5, 4.0

    # Telemetrie
    times: list[float] = []
    atp_a_series: list[float] = []
    atp_b_series: list[float] = []
    coupling_a_series: list[float] = []
    coupling_b_series: list[float] = []

    for step in range(n_steps):
        t = step * dt_s
        # UV-Emission jeder Zelle
        photons_a = chemolumineszenz(atp_a)
        photons_b = chemolumineszenz(atp_b)

        # UV-Fluss am Partner
        flux_b = uv_flux_at_distance(photons_a, distance_nm)
        flux_a = uv_flux_at_distance(photons_b, distance_nm)

        # Modulation der ATP-Synthase
        uv_a = coupling_strength * uv_modulation_from_flux(flux_a)
        uv_b = coupling_strength * uv_modulation_from_flux(flux_b)

        # ODE-Schritt
        atp_a, glu_a = atp_ode_step(atp_a, glu_a, uv_modulation=uv_a, dt_s=dt_s)
        atp_b, glu_b = atp_ode_step(atp_b, glu_b, uv_modulation=uv_b, dt_s=dt_s)

        if step % 10 == 0:
            times.append(t)
            atp_a_series.append(atp_a)
            atp_b_series.append(atp_b)
            coupling_a_series.append(uv_a)
            coupling_b_series.append(uv_b)

    # Korrelationskoeffizient (Pearson r)
    a_arr = np.asarray(atp_a_series)
    b_arr = np.asarray(atp_b_series)
    if a_arr.std() < 1e-9 or b_arr.std() < 1e-9:
        r_corr = 0.0
    else:
        r_corr = float(np.corrcoef(a_arr, b_arr)[0, 1])

    # Signal-Bewertung
    if r_corr > 0.7:
        signal = "STRONG"
    elif r_corr > 0.3:
        signal = "WEAK"
    elif r_corr > 0.05:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"

    return {
        "distance_nm": distance_nm,
        "coupling_strength": coupling_strength,
        "t_end_s": t_end_s,
        "correlation_r": r_corr,
        "signal": signal,
        "atp_a_final": float(atp_a),
        "atp_b_final": float(atp_b),
        "n_samples": len(atp_a_series),
        "next_vectors": [
            "iter-3: Radikal-Paar-Magnetorezeption",
            "iter-4: QuQuint-Beschleunigung der RDME-Raten",
            "iter-5: N>2 Zellen → populations-Synchronisation",
        ],
    }


if __name__ == "__main__":
    import json

    # Verschiedene Distanzen testen
    print("=== iter-2: UV-Phasen-Synchronisation ===\n")
    for d_nm in [500.0, 1000.0, 5000.0, 50_000.0]:
        r = run_iter2(distance_nm=d_nm)
        print(f"  Abstand {d_nm:>6.0f} nm: r={r['correlation_r']:+.3f} "
              f"({r['signal']})")

    # Standard-Lauf
    result = run_iter2(distance_nm=1000.0)
    print(f"\nStandard-Lauf (1 µm): r={result['correlation_r']:+.3f} ({result['signal']})")

    # Schreibe result.json
    target = __file__.replace("uv_synchronization.py", "result.json")
    with open(target, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n→ Wrote {target}")
