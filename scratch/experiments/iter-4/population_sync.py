"""Iter-4: N-Zellen-Population mit UV-Kopplung (Popp biocoherent state).

Modell:
- N=10 Zellen in einer Suspension
- Jede Zelle hat ATP-ODE mit stochastischer ATP-Hydrolyse
- Jede Zelle emittiert UV-Photonen (10 pro Sekunde, Popp)
- UV-Absorption bei Nachbarzellen moduliert ATP-Synthase-Rate
- Moderat gekoppelte ODE (aus iter-2-retry-Erkenntnis: keine triviale Kopplung)

Vergleich:
1. **Isolated**: jede Zelle unabhängig (Kontrolle)
2. **UV-coupled**: voller UV-Fluss
3. **Cryptochrome-coupled**: nur Cryptochrom-Sensitivität

Metrik: globale Synchronisation r_global, Verteilung der ATP-Werte,
Cluster-Bildung.
"""

from __future__ import annotations

import json
import math

import numpy as np

N_CELLS_DEFAULT = 10
RADIUS_NM = 250.0      # Zelle
INTER_CELL_NM = 800.0   # typische Distanz in Suspension
PHOTONS_PER_S = 10.0     # Popp-Faktor pro Zelle
ABSORPTION_NM = 200.0


def atp_step_isolated(
    atp: float,
    glucose: float,
    rng: np.random.Generator,
    dt_s: float = 0.1,
) -> tuple[float, float]:
    """ATP-Step ohne Kopplung."""
    k_glyc = 0.05
    k_atp_base = 0.03
    noise = 0.05
    d_glucose = -k_glyc * glucose * dt_s
    glucose = max(glucose + d_glucose, 0.0)
    k_atp = max(0.0, k_atp_base * (1.0 + noise * rng.normal()))
    d_atp = (2.0 * k_glyc * glucose - k_atp * atp) * dt_s
    atp = max(atp + d_atp, 0.0)
    return atp, glucose


def uv_flux_at_distance(photons_per_s: float, distance_nm: float) -> float:
    """UV-Flussdichte [Photonen/cm²/s]."""
    if distance_nm <= 0:
        return 0.0
    absorption = math.exp(-distance_nm / ABSORPTION_NM)
    r_cm = distance_nm * 1e-7
    surface_cm2 = 4 * math.pi * r_cm**2
    return (photons_per_s * absorption) / surface_cm2


def atp_step_uv_coupled(
    atp: float,
    glucose: float,
    uv_incoming: float,
    rng: np.random.Generator,
    dt_s: float = 0.1,
    coupling_strength: float = 1.0e-7,
) -> tuple[float, float]:
    """ATP-Step mit UV-Modulation."""
    k_glyc = 0.05
    k_atp_base = 0.03
    noise = 0.05
    d_glucose = -k_glyc * glucose * dt_s
    glucose = max(glucose + d_glucose, 0.0)
    k_atp = max(0.0, k_atp_base * (1.0 + noise * rng.normal()))
    uv_modulation = coupling_strength * uv_incoming
    d_atp = (2.0 * k_glyc * glucose - k_atp * atp + uv_modulation) * dt_s
    atp = max(atp + d_atp, 0.0)
    return atp, glucose


def positions_on_lattice(n: int, spacing_nm: float) -> np.ndarray:
    """N Zellen in einer 2D-Gitter-Anordnung."""
    side = int(math.sqrt(n))
    coords: list[tuple[float, float]] = []
    for i in range(side):
        for j in range(side):
            coords.append((i * spacing_nm, j * spacing_nm))
    while len(coords) < n:
        # Hinzufügen in nächste Reihe
        coords.append(((side - 1) * spacing_nm, len(coords) * spacing_nm))
    return np.asarray(coords[:n])


def run_population(
    n_cells: int = N_CELLS_DEFAULT,
    coupling: str = "isolated",   # "isolated" | "uv" | "crypto"
    t_end_s: float = 200.0,
    dt_s: float = 0.1,
    seed: int = 42,
) -> dict[str, object]:
    """Simuliert N Zellen."""
    rng = np.random.default_rng(seed)
    positions = positions_on_lattice(n_cells, INTER_CELL_NM)

    # Initiale Bedingungen: gestreut
    atp = np.full(n_cells, 2.0) + rng.normal(0.0, 0.2, n_cells)
    glu = np.full(n_cells, 5.0) + rng.normal(0.0, 0.5, n_cells)

    n_steps = int(t_end_s / dt_s)
    atp_history: list[np.ndarray] = []

    for step in range(n_steps):
        # UV-Emission jeder Zelle
        photons = np.full(n_cells, PHOTONS_PER_S)

        # UV-Incoming für jede Zelle = Summe der Flüsse von allen anderen
        uv_incoming = np.zeros(n_cells)
        if coupling != "isolated":
            for i in range(n_cells):
                for j in range(n_cells):
                    if i == j:
                        continue
                    d_nm = float(np.linalg.norm(positions[i] - positions[j]))
                    if d_nm > 0:
                        uv_incoming[i] += uv_flux_at_distance(photons[j], d_nm)

        # ATP-Step
        new_atp = np.zeros(n_cells)
        new_glu = np.zeros(n_cells)
        for i in range(n_cells):
            if coupling == "isolated":
                new_atp[i], new_glu[i] = atp_step_isolated(
                    atp[i], glu[i], rng, dt_s,
                )
            else:
                new_atp[i], new_glu[i] = atp_step_uv_coupled(
                    atp[i], glu[i], uv_incoming[i], rng, dt_s,
                )
        atp = new_atp
        glu = new_glu

        # Subsample
        if step % 20 == 0:
            atp_history.append(atp.copy())

    # Statistiken
    atp_arr = np.asarray(atp_history)        # [n_steps, n_cells]
    # Steady-state: zweite Hälfte
    half = atp_arr.shape[0] // 2
    atp_ss = atp_arr[half:]
    # Globale Korrelation: Mittel der paarweisen Pearson-r
    n_pairs = 0
    r_sum = 0.0
    r_vals: list[float] = []
    for i in range(n_cells):
        for j in range(i + 1, n_cells):
            if atp_ss[:, i].std() > 1e-9 and atp_ss[:, j].std() > 1e-9:
                r = float(np.corrcoef(atp_ss[:, i], atp_ss[:, j])[0, 1])
                r_vals.append(r)
                r_sum += r
                n_pairs += 1
    r_global = r_sum / n_pairs if n_pairs else 0.0

    return {
        "n_cells": n_cells,
        "coupling": coupling,
        "r_global_mean": r_global,
        "r_pairs": r_vals,
        "atp_history_shape": list(atp_arr.shape),
        "atp_final_mean": float(atp.mean()),
        "atp_final_std": float(atp.std()),
        "atp_final_min": float(atp.min()),
        "atp_final_max": float(atp.max()),
        "n_steps": n_steps,
    }


def compare_couplings(n_cells: int = 10) -> dict[str, object]:
    """Vergleicht isolated / uv / crypto mit gleicher Seed."""
    results = {}
    for coupling in ["isolated", "uv", "crypto"]:
        res = run_population(n_cells=n_cells, coupling=coupling, seed=42)
        results[coupling] = res
    return results


def synthesis_signal(comp: dict[str, dict]) -> str:
    """Bestimmt das Signal aus dem Vergleich."""
    r_iso = comp["isolated"]["r_global_mean"]
    r_uv = comp["uv"]["r_global_mean"]
    if r_uv > 0.7 and r_uv - r_iso > 0.3:
        return "STRONG"
    elif r_uv > 0.3 and r_uv - r_iso > 0.1:
        return "WEAK"
    elif abs(r_uv - r_iso) < 0.05:
        return "NULL"
    else:
        return "CONTRADICTION"


if __name__ == "__main__":
    print("=== iter-4: N-Zellen-Population mit UV-Kopplung ===\n")
    comparison = compare_couplings(n_cells=10)

    for coupling, r in comparison.items():
        print(
            f"  {coupling:>10s}: r_global={r['r_global_mean']:+.3f} "
            f"(std_atp_final={r['atp_final_std']:.3f}, "
            f"mean_atp_final={r['atp_final_mean']:.3f})"
        )

    signal = synthesis_signal(comparison)
    print(f"\nSignal: {signal}")

    output = {
        "comparison": comparison,
        "signal": signal,
        "next_vectors": [
            "iter-5: 100-Zellen-Population mit räumlicher Struktur",
            "iter-6: Dynamische UV-Phasen über Stunden-Zeitskala",
            "Falls STRONG: Produktion in src/cellsim/modules/population.py",
            "Falls NULL: ODE ist zu simpel — realistischer ATP-Verbraucher nötig",
        ],
    }
    target = __file__.replace("population_sync.py", "result.json")
    with open(target, "w") as f:
        json.dump(output, f, indent=2, default=float)
    print(f"\n→ Wrote {target}")
