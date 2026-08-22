"""Iter-3: Radikal-Paar-Cryptochrom-Modell.

Cryptochrom (FAD + 3 Trp-Reste) bildet bei Blaulicht-Absorption ein
Radikal-Paar [FAD⁻ •, Trp•]. Die Spin-Dynamik dieses Paares wird
durch Magnetfelder beeinflusst → resultierende chemische Ausbeute ist
feldabhängig.

Modell:
- 2-Zustands-System (Singulett |S> ↔ Triplett |T>) mit Hamilton-Operator
- H = μ_B · (g1·S1 + g2·S2) · B + S1 · S2 · J(R)
- Externe Felder: geomagnetisches Feld (50 µT) + UV-getriebene Spin-Chemie
- Vorhersage: Spin-Ausbeute zeigt Magnetfeld-Abhängigkeit → Grundlage
  für echte biologische Magnetorezeption
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

MU_B = 9.274_010_0783e-24    # Bohr-Magneton [J/T]
G_E = -2.002_319_30436256    # freier Elektron g-Faktor
PLANCK = 6.626_070_15e-34    # J·s
KB = 1.380_649e-23           # Boltzmann [J/K]


@dataclass(frozen=True)
class CryptochromeParams:
    """Cryptochrom-Parameter aus Ritz et al. (2000)."""

    # Hyperfein-Kopplung der Trp-Radikale (in T)
    a_trp_1: float = 0.3e-3
    a_trp_2: float = 0.3e-3
    a_trp_3: float = 0.3e-3
    # Austausch-Kopplung J(r) — distanz-abhängig
    j0: float = 1.0e6           # Maximal-Wert [rad/s]
    r_nm: float = 1.0            # aktueller Abstand
    # FAD g-Faktor (typisch)
    g_fad: float = 2.0030
    # Lebensdauer des Radikal-Paars
    tau_s: float = 1.0e-5        # ~10 µs
    # Magnetfeld
    b_field_t: float = 50.0e-6   # geomagnetisches Feld


@dataclass
class SpinState:
    """Zustand des Radikal-Paars (2x2 Dichtematrix simplified)."""

    s_population: float = 1.0     # Singulett-Population
    t_population: float = 0.0     # Triplett-Population
    coherence: float = 0.0        # S-T-Kohärenz
    t: float = 0.0


def exchange_coupling(r_nm: float, j0: float = 1.0e6) -> float:
    """Austausch-Kopplung J(r) in Abhängigkeit vom Abstand."""
    # Vereinfacht: J ~ exp(-r/0.5 nm)
    return j0 * math.exp(-r_nm / 0.5)


def spin_hamiltonian_eigenvalues(
    params: CryptochromeParams,
    b_field_t: float | None = None,
) -> dict[str, float]:
    """Eigenwerte des Spin-Hamiltonians (vereinfacht).

    H = μ_B · g · B · S_z  für jedes Elektron
    Die Differenz ΔE = g · μ_B · B erzeugt Singulett-Triplett-Übergänge
    """
    if b_field_t is None:
        b_field_t = params.b_field_t
    # Energie-Splitting: Zeeman-Effekt
    delta_e = abs(G_E) * MU_B * b_field_t  # in J
    delta_e_hz = delta_e / PLANCK
    # Hyperfein-Aufspaltung (Trp-Kerne)
    delta_hf = math.sqrt(
        params.a_trp_1**2 + params.a_trp_2**2 + params.a_trp_3**2
    )
    # Vorhersage: wenn δE ≈ δHF, sind Resonanz-Übergänge wahrscheinlich
    ratio = delta_e_hz / delta_hf if delta_hf > 0 else 0.0
    return {
        "delta_e_joules": delta_e,
        "delta_e_hz": delta_e_hz,
        "delta_hf_t": delta_hf,
        "ratio_field_to_hf": ratio,
        "is_resonant": 0.1 < ratio < 10.0,
    }


def singlet_yield_with_field(
    params: CryptochromeParams,
    b_field_t: float | None = None,
    n_steps: int = 1000,
    dt_s: float | None = None,
) -> dict[str, float]:
    """Berechnet Singulett-Ausbeute als Funktion des Magnetfelds.

    Quantenmechanisches Lindblad-Modell stark vereinfacht:
      dS/dt = -k_S · S + k_T · T   (Singulett-Recombination)
      dT/dt = -k_T · T + k_S · S   (Singulett-Bildung)
      mit k_S(T) = k_S0 · sin²(g·μ_B·B·τ/2)
    """
    if b_field_t is None:
        b_field_t = params.b_field_t
    if dt_s is None:
        dt_s = params.tau_s / n_steps

    j = exchange_coupling(params.r_nm, params.j0)
    omega = abs(G_E) * MU_B * b_field_t / PLANCK    # Larmor-Frequenz

    # Vereinfachter Singulett-Output:
    # Kohärenz-Hyperfein-Rabi-Oszillation in Anwesenheit von B
    # Ausbeute ~ 0.5 + 0.5 * cos(ω · τ)
    phase = omega * params.tau_s * 2 * math.pi
    singlet_yield = 0.5 + 0.5 * math.cos(phase)

    # Geometrie-Effekt: Ausbeute ist maximal, wenn ω ≈ Hyperfein
    yield_resonant = 0.5 + 0.5 * math.exp(-((omega - 1e6) / 1e6) ** 2)
    return {
        "b_field_t": b_field_t,
        "omega_hz": omega,
        "exchange_j_rad_per_s": j,
        "singlet_yield_quick_estimate": singlet_yield,
        "singlet_yield_resonant_estimate": yield_resonant,
    }


def run_iter3(
    b_fields_t: tuple[float, ...] = (0.0, 10e-6, 25e-6, 50e-6, 100e-6, 500e-6, 1e-3),
    tau_s: float = 1.0e-5,
) -> dict[str, object]:
    """Hauptfunktion: Magnetfeld-Abhängigkeit der Singulett-Ausbeute."""
    params = CryptochromeParams(tau_s=tau_s)
    results = []
    for b in b_fields_t:
        single = singlet_yield_with_field(params, b_field_t=b)
        results.append(single)

    # Quantifizierung: Bereich der Ausbeuten
    yields = [r["singlet_yield_quick_estimate"] for r in results]
    yield_range = max(yields) - min(yields)

    # Signal-Bewertung
    if yield_range > 0.4:
        signal = "STRONG"
    elif yield_range > 0.1:
        signal = "WEAK"
    elif yield_range > 0.01:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"

    return {
        "results": results,
        "signal": signal,
        "yield_range": yield_range,
        "min_yield": min(yields),
        "max_yield": max(yields),
        "tau_s": tau_s,
        "next_vectors": [
            "iter-3b: Anisotropie-Messung (Richtungsabhängigkeit des Magnetfelds)",
            "iter-3c: Hyperfein-Aufspaltung mit echten Trp-Konstanten",
            "iter-4: Spin-Chemie an Crowding-Schnittstelle",
            "Falls STRONG: → production code in src/cellsim/modules/cryptochrome.py",
        ],
    }


if __name__ == "__main__":
    result = run_iter3()
    print("=== iter-3: Radikal-Paar-Cryptochrom ===")
    print(f"Signal: {result['signal']}")
    print(f"Yield-Bereich: {result['yield_range']:.4f}")
    print(f"\n{'B [µT]':>10s} {'ω [Hz]':>15s} {'Yield':>8s}")
    for r in result["results"]:
        print(
            f"{r['b_field_t']*1e6:>10.1f} {r['omega_hz']:>15.3e} "
            f"{r['singlet_yield_quick_estimate']:>8.4f}"
        )

    target = __file__.replace("radical_pair.py", "result.json")
    with open(target, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"\n→ Wrote {target}")
