"""Iter-15: Tryptophan-Superradianz — N*-Skalierungsgesetz vs. Damköhler-Fenster.

VORAB-REGISTRIERTE Falsifikations-Kriterien (fixiert vor dem Lauf):

  - BRIDGE_OPEN : Es existiert ein (N_total, f_burst)-Regime mit
    Turnover im Damköhler-Fenster [1e-4, 0.1]/Schritt — erreichbar
    für neuronale Trp-Skalen (≥1e9 Trp), NICHT für syn3A (2e3 Trp).
  - FALSIFIED_BRIDGE : Φ* > 1e14 photons/s → endogene UVC-Photochemie
    bleibt in vivo unterm Fenster (iter-12-Befund auch mit Superradianz).
  - CONTRADICTION_ITER12 : N* ≤ 1e4 (syn3A-reachable) → Widerspruch zu
    iter-12s NULL → σ/QY-Annahmen revidieren.

Physik (Produktion, modules/superradiance.py):
  Φ_cell = M·N·f  [photons/s]  (ein Photon pro Emitter pro Burst)
  Φ(r)   = Φ_cell·exp(−r/r_abs)/(4πr²)   [photons/cm²/s]
  Turnover/Schritt = Φ(r)·σ·QY·dt

Biologische Anker:
  - JCVI-syn3A: ~2·10³ Trp (455 Proteine, ~1.3 % Trp)
  - neuronale Mega-Netzwerke (Kurian 2024): 10⁹⁻¹⁰ Trp, Cluster bis 1e5
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.core.rng import make_rng
from cellsim.modules.emergence import permutation_contrast_test, stochastic_jump_diffusion
from cellsim.modules.superradiance import (
    QUANTUM_YIELD_UVC,
    SIGMA_TRP_CM2,
    PhotonicCluster,
    aggregate_photon_rate_per_s,
    damkoehler_window_per_step,
    flux_at_cm2,
    threshold_aggregate_rate_per_s,
    turnover_per_second,
)

R_NM = 100.0
DT_S = 1e-3
GRID: tuple[int, int, int] = (16, 16, 16)

CLASS_ID = {"unter_Fenster": 0, "IM_FENSTER": 1, "Sättigung": 2}

# Biologische Referenz-Punkte (N_total = Tryptophan-Gesamtzahl der Zelle)
BIOLOGY = {
    "syn3A (2e3 Trp)": 2e3,
    "Bakterie groß (1e6 Trp)": 1e6,
    "Eukaryot (1e8 Trp)": 1e8,
    "Neuron (1e10 Trp)": 1e10,
    "Mega-Netzwerk (1e12 Trp)": 1e12,
}
F_BURSTS = (1.0, 10.0, 100.0, 1e3, 1e4, 1e6)


def classify_turnover(per_step: float, window: tuple[float, float]) -> str:
    lo, hi = window
    if per_step < lo:
        return "unter_Fenster"
    if per_step > hi:
        return "Sättigung"
    return "IM_FENSTER"


def analytic_phase_table() -> tuple[list[dict[str, float]], float, float]:
    """N\*-Sweep: (N_total, f_burst) → Turnover/Schritt vs. Fenster."""
    window = damkoehler_window_per_step(DT_S)
    phi_lo, phi_hi = threshold_aggregate_rate_per_s(r_nm=R_NM, dt_s=DT_S)
    rows: list[dict[str, float]] = []
    for n_trp in BIOLOGY.values():
        for f in F_BURSTS:
            phi_cell = aggregate_photon_rate_per_s(
                n_clusters=1, n_per_cluster=int(n_trp), f_burst_hz=f
            )  # effektiv: alle Trp feuern mit Rate f
            flux = flux_at_cm2(phi_cell, r_nm=R_NM)
            per_step = turnover_per_second(flux, SIGMA_TRP_CM2, QUANTUM_YIELD_UVC) * DT_S
            rows.append({
                "n_trp": n_trp,
                "f_burst": f,
                "phi_cell": phi_cell,
                "flux_cm2": flux,
                "turnover_per_step": per_step,
                "class_numeric": CLASS_ID[classify_turnover(per_step, window)],
            })
    return rows, phi_lo, phi_hi


def monte_carlo_burst_check(seed: int = 42, n_bursts: int = 200_000) -> dict[str, float]:
    """MC-Check der Burst-Integration: pro Burst absorbiert ein Molekül
    bei r=100nm mit p = N_c·σ·QY·G(r) (Poisson-Thinning)."""
    rng = make_rng(seed, 0, 0)
    n_cluster = 100
    g = float(np.exp(-R_NM / 200.0) / (4.0 * np.pi * (R_NM * 1e-7) ** 2))
    p_burst = n_cluster * SIGMA_TRP_CM2 * QUANTUM_YIELD_UVC * g
    n_molecules = 100_000
    events = rng.binomial(n_molecules, min(p_burst, 1.0), size=n_bursts)
    mc_per_burst = float(np.mean(events)) / n_molecules
    return {
        "analytic_per_burst": p_burst,
        "mc_per_burst": mc_per_burst,
        "relative_error": abs(mc_per_burst - p_burst) / p_burst,
    }


def dynamic_light_memory_check(seed: int = 42, n_steps: int = 600) -> dict[str, float]:
    """Dynamischer Check am Schwellen-Punkt: Burst-Züge treiben
    PhotoP→PhotoN auf dem Gitter; Permutationstest (iter-13-Produktion)
    prüft Produkt-Lokalisierung am Cluster."""
    rng = make_rng(seed, 0, 0)
    cluster = PhotonicCluster(n_emitters=100)
    phi_star_lo, _ = threshold_aggregate_rate_per_s(r_nm=R_NM, dt_s=DT_S)
    f_burst_hz = phi_star_lo / cluster.photons_per_burst  # Bursts/s

    photo_p = np.full(GRID, 8, dtype=np.int64)
    photo_n = np.zeros(GRID, dtype=np.int64)
    center = tuple(s // 2 for s in GRID)

    idx3 = np.indices(GRID)
    d2 = sum((idx3[a] - center[a]) ** 2 for a in range(3))
    dist_nm = np.sqrt(d2.astype(float)) * 100.0
    g_field = np.exp(-dist_nm / 200.0) / (4.0 * np.pi * (dist_nm * 1e-7) ** 2 + 1e-30)
    g_field[dist_nm < 50.0] = 0.0  # Cluster-Kern: Punktquellen-Singularität
    p_field = np.minimum(
        cluster.photons_per_burst * SIGMA_TRP_CM2 * QUANTUM_YIELD_UVC * g_field,
        1.0,
    )
    licht = (p_field > 0.05 * p_field.max()) & (dist_nm >= 50.0)
    # Am Schwellen-Punkt feuert das Cluster f ≈ Φ*/N_c ≈ 2e6 Bursts/s —
    # ~2·10³ Bursts pro 1-ms-Schritt → Poisson-pro-Schritt, dann
    # Binomial-Thinning pro Voxel.
    bursts_per_step_mean = f_burst_hz * DT_S

    events_total = 0
    for _ in range(n_steps):
        stochastic_jump_diffusion({"PhotoP": photo_p, "PhotoN": photo_n}, 0.10, rng)
        n_bursts = int(rng.poisson(bursts_per_step_mean))
        if n_bursts > 0:
            p_step_field = 1.0 - np.exp(-n_bursts * p_field)
            fire = rng.binomial(photo_p, p_step_field)
            n_fired = int(fire.sum())
            if n_fired:
                photo_p -= fire
                photo_n += fire
                events_total += n_fired

    n_zone = int(np.count_nonzero(licht))
    in_zone = int(photo_n[licht].sum())
    perm = permutation_contrast_test(
        n_events=int(photo_n.sum()),
        n_total_sites=int(np.prod(GRID)),
        n_zone_sites=n_zone,
        n_in_zone_observed=in_zone,
        n_permutations=2000,
        seed=seed,
    )
    return {
        "events_total": float(events_total),
        "products_total": float(photo_n.sum()),
        "p_value_light_memory": perm["p_value"],
        "h0_p99": perm["h0_p99"],
        "in_zone": float(in_zone),
        "expected_h0": perm["expected_in_zone_h0"],
    }


if __name__ == "__main__":
    print("=== iter-15: Tryptophan-Superradianz vs. Damköhler-Fenster ===\n")
    rows, phi_lo, phi_hi = analytic_phase_table()
    print(f"Schwellen-Rate Φ* (r={R_NM:.0f}nm, dt={DT_S:g}s):")
    print(f"  Fenster-Eintritt: Φ* ∈ [{phi_lo:.2e}, {phi_hi:.2e}] photons/s\n")

    header = f"{'N_total':>12} {'f_burst':>9} {'Φ_cell':>10} {'turnover/step':>13}  class"
    print(header)
    print("-" * len(header))
    for row in rows:
        label = ["unter_Fenster", "IM_FENSTER", "Sättigung"][int(row["class_numeric"])]
        print(f"{row['n_trp']:>12.0e} {row['f_burst']:>9.0e} "
              f"{row['phi_cell']:>10.2e} {row['turnover_per_step']:>13.2e}  {label}")

    in_window = [r for r in rows if r["class_numeric"] == 1]
    syn3a_in = any(r["class_numeric"] == 1 for r in rows if r["n_trp"] == 2e3)
    neuron_in = any(r["class_numeric"] == 1 for r in rows if r["n_trp"] >= 1e9)

    mc = monte_carlo_burst_check()
    print(f"\nMC-Check Burst-Integration: rel. Fehler {mc['relative_error']:.3f}")

    print("\nDynamischer Check am Schwellen-Punkt (Burst-Züge → Photochemie):")
    dyn = dynamic_light_memory_check()
    for k, v in dyn.items():
        print(f"  {k}: {v}")

    if in_window and not syn3a_in and neuron_in:
        signal = "BRIDGE_OPEN"
    elif not in_window:
        signal = "FALSIFIED_BRIDGE"
    elif syn3a_in:
        signal = "CONTRADICTION_ITER12"
    else:
        signal = "PARTIAL"

    print(f"\nFenster-Eintritt: {len(in_window)} Konfigs | syn3A: {syn3a_in} | Neuron: {neuron_in}")
    print(f"Signal: {signal}")

    result: dict[str, Any] = {
        "phi_star": [phi_lo, phi_hi],
        "n_in_window": len(in_window),
        "syn3a_in_window": syn3a_in,
        "neuron_in_window": neuron_in,
        "monte_carlo": mc,
        "dynamic_check": dyn,
        "signal": signal,
        "next_vectors": [
            "Falls BRIDGE_OPEN: photischer Kanal als EM→RDME-Kopplung im Produktionstack dokumentieren",
            "Falls FALSIFIED_BRIDGE: σ/QY revidieren oder Brücke verwerfen",
            "iter-16: Hagan-Parametrisierung E_G (scratch/experiments/iter-16)",
        ],
    }
    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"→ Wrote {target}")