"""Iter-14: Damköhler-Fenster-Replikation auf Produktionstack (Falsifikator).

VORAB-REGISTRIERTE Falsifikations-Kriterien (fixiert vor dem Lauf):

  - REPLICATED_STRONG : ≥6/9 (D, dt)-Konfigs DISTINCT nach den
    iter-11-Kriterien, UND Sättigungs-Rückkehr
    (|corr(dt=1e-3) − corr_Kontrolle| ≤ 0.1), UND Fenster-Ordnung
    (corr(1e-6) > corr(1e-5) für ≥2 der 3 D).
  - REPLICATED_WEAK   : ≥3/9 DISTINCT (Struktur unter geänderten
    Bedingungen wiedergefunden, Grenzen verschoben).
  - PARTIAL           : 1–2 DISTINCT.
  - FALSIFIED         : 0 DISTINCT → iter-11-Fenster war ein
    Gitter-/Seed-/Numerik-Artefakt der Scratch-Hybriden.

Änderungen gegenüber iter-11 (alles andere identical protocol):
  - Gitter: 24³ statt 16³ (7.3× Voxel)
  - Seeds: {100, 101, 102} statt {42, 43, 44} (disjunkter Raum)
  - Code: Produktionstack statt Scratch-Hybrid —
      RDMEAdapter(use_tau_leap=True) + stochastic_jump_diffusion
  - Diffusion numerisch anders (Teilchen-Sprünge statt rint-Laplace)
    und physikalisch kalibriert (p_dir = 𝒟, iter-14-Korrektur der
    früheren p = 𝒟/6-Untermischung)

Reproduziert das Fenster NICHT, trägt iter-11 nicht als Physik.
Reproduziert es es, gilt es unter Gitter-, Seed- UND Numerikwechsel —
die stärkste Replikationsform ohne Rechenzentrum.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.emergence import (
    binarize,
    emergence_metrics,
    stochastic_jump_diffusion,
)
from cellsim.modules.reactions import ReactionRegistry, default_registry

N_STEPS = 600
SNAP_EVERY = 10
Q_BIN = 0.75
SEEDS = (100, 101, 102)
GRID: tuple[int, int, int] = (24, 24, 24)
DT_REACTS = (0.0, 1e-6, 1e-5, 1e-4, 1e-3)
DIFF_COEFFS = (0.05, 0.15, 0.45)
MIN_STRONG = 6
MIN_WEAK = 3

# Protocol-Fidelity zu iter-11: derselbe 3-Reaktions-Metabolit-Kern
# (die 21-Reaktions-Netzwerk-Dynamik ist ein eigener Vektor, siehe
# iter-13-Sättigungs-Test — hier würde sie das Sweep-Protokoll ändern)
_SUBSET_NAMES = ("glycolysis", "atp_hydrolysis", "atp_synthase")


def _subset_registry() -> ReactionRegistry:
    full = default_registry()
    by_name = {r.name: r for r in full.reactions}
    return ReactionRegistry(
        species_ids=full.species_ids,
        reactions=tuple(by_name[n] for n in _SUBSET_NAMES),
    )


def _gaussian_bump(grid: tuple[int, int, int], amp: float, width: float) -> np.ndarray:
    center = tuple(s // 2 for s in grid)
    idx3 = np.indices(grid)
    d2 = sum((idx3[axis] - c) ** 2 for axis, c in enumerate(center))
    return (amp * np.exp(-d2 / width)).astype(np.int64)


def run_config(dt_react: float, diff_coeff: float, seed: int) -> dict[str, float]:
    """Produktionstack-Replikation eines iter-11-Sweep-Punkts."""
    rdme = RDMEAdapter(
        registry=_subset_registry(), grid_shape=GRID, use_tau_leap=True
    )
    rng = make_rng(seed, 0, 0)
    bump = _gaussian_bump(GRID, amp=150.0, width=6.0)
    rdme.state.voxels["Glucose"] = rdme.state.voxels["Glucose"] + bump
    rdme.state.voxels["ATP"] = rdme.state.voxels["ATP"] + bump
    rdme.state.total_particles = sum(
        int(v.sum()) for v in rdme.state.voxels.values()
    )
    initial_total = rdme.state.total_particles

    snaps_atp: list[np.ndarray] = []
    snaps_glc: list[np.ndarray] = []
    corr_series: list[float] = []

    for step in range(N_STEPS):
        stochastic_jump_diffusion(rdme.state.voxels, diff_coeff, rng)
        rdme.step(dt_react, rng)
        if step % SNAP_EVERY == 0:
            g = rdme.state.voxels["Glucose"].astype(np.float64)
            a = rdme.state.voxels["ATP"].astype(np.float64)
            snaps_atp.append(binarize(a, q=Q_BIN).copy())
            snaps_glc.append(binarize(g, q=Q_BIN).copy())
            if g.std() > 1e-12 and a.std() > 1e-12:
                corr_series.append(float(np.corrcoef(g.ravel(), a.ravel())[0, 1]))
            else:
                corr_series.append(0.0)

    snaps = np.asarray(snaps_atp)
    m = emergence_metrics(snaps, grid_shape=GRID)
    return {
        **m,
        "corr_glc_atp_mean": float(np.mean(corr_series)),
        "p11_mean": float(np.mean([
            float(np.mean((g & a).astype(np.float64)))
            for g, a in zip(snaps_glc, snaps_atp, strict=True)
        ])),
        "mass_ratio": float(rdme.state.total_particles / max(initial_total, 1)),
        "reaction_events_total": float(
            rdme.state.tau_leap_events
        ),
    }


def classify(cfg: dict[str, float], control: dict[str, float]) -> str:
    """iter-11-Kriterien unverändert: korrelation/LZ/tMI vs. Kontrolle."""
    if cfg["mass_ratio"] > 3.0 or not np.isfinite(cfg["mass_ratio"]):
        return "RUNAWAY"
    corr_drop = abs(cfg["corr_glc_atp_mean"] - control["corr_glc_atp_mean"])
    lz_diff = abs(cfg["lz_growth"] - control["lz_growth"])
    tmi_diff = abs(cfg["temporal_mi_mean"] - control["temporal_mi_mean"])
    if corr_drop > 0.3 or lz_diff > 0.05 or tmi_diff > 0.05:
        return "DISTINCT"
    return "NULL"


def sweep() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    controls: dict[float, list[dict[str, float]]] = {}
    for D in DIFF_COEFFS:
        controls[D] = [run_config(0.0, D, s) for s in SEEDS]

    for D in DIFF_COEFFS:
        for dt_r in DT_REACTS:
            if dt_r == 0.0:
                runs, cls, label = controls[D], "CONTROL", "control"
            else:
                runs = [run_config(dt_r, D, s) for s in SEEDS]
                per_seed = [
                    classify(r, c) for r, c in zip(runs, controls[D], strict=True)
                ]
                if per_seed.count("RUNAWAY") >= 2:
                    cls = "RUNAWAY"
                elif per_seed.count("DISTINCT") >= 2:
                    cls = "DISTINCT"
                else:
                    cls = "NULL"
                label = f"D={D:g},dt={dt_r:g}"
            mean_run = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
            rows.append({
                "label": label, "diff_coeff": D, "dt_react": dt_r,
                "classification": cls, "mean": mean_run,
            })

    return {"rows": rows, "n_seeds": len(SEEDS)}


def assess(result: dict[str, Any]) -> str:
    """Vorab-registrierte Kriterien (docstring) auswerten."""
    rows = result["rows"]
    distinct = [
        r for r in rows
        if r["classification"] == "DISTINCT" and r["dt_react"] > 0
    ]
    n_distinct = len(distinct)
    if n_distinct == 0:
        return "FALSIFIED"

    result["n_distinct"] = n_distinct

    # Sättigungs-Rückkehr: corr(1e-3) nahe Kontrolle
    sat_ok = True
    for D in DIFF_COEFFS:
        row = next(r for r in rows if r["dt_react"] == 1e-3 and r["diff_coeff"] == D)
        ctrl = next(r for r in rows if r["dt_react"] == 0.0 and r["diff_coeff"] == D)
        if abs(row["mean"]["corr_glc_atp_mean"] - ctrl["mean"]["corr_glc_atp_mean"]) > 0.1:
            sat_ok = False

    # Fenster-Ordnung: langsam näher an Kontrolle als mittel
    order_ok = 0
    for D in DIFF_COEFFS:
        slow = next(r for r in rows if r["dt_react"] == 1e-6 and r["diff_coeff"] == D)
        mid = next(r for r in rows if r["dt_react"] == 1e-5 and r["diff_coeff"] == D)
        ctrl = next(r for r in rows if r["dt_react"] == 0.0 and r["diff_coeff"] == D)
        cs, cm, cc = (
            row["mean"]["corr_glc_atp_mean"] - ctrl["mean"]["corr_glc_atp_mean"]
            for row in (slow, mid, ctrl)
        )
        if (abs(cs) < abs(cm)) or (cs == 0.0 and cm == 0.0):
            order_ok += 1
        del cc

    result["saturation_return"] = sat_ok
    result["window_ordering_of"] = f"{order_ok}/3"
    if n_distinct >= MIN_STRONG and sat_ok and order_ok >= 2:
        return "REPLICATED_STRONG"
    if n_distinct >= MIN_WEAK:
        return "REPLICATED_WEAK"
    return "PARTIAL"


if __name__ == "__main__":
    print("=== iter-14: Damköhler-Fenster auf Produktionstack (Falsifikator) ===")
    print(f"Gitter {GRID} (=24³), Seeds {SEEDS}, Produktionstack.\n")
    result = sweep()

    print(f"{'label':<18} {'class':<9} {'tMI':>6} {'sMI':>6} {'LZgrw':>7} "
          f"{'corr':>7} {'p11':>6} {'mass':>6} {'events':>10}")
    for row in result["rows"]:
        m = row["mean"]
        print(f"{row['label']:<18} {row['classification']:<9} "
              f"{m['temporal_mi_mean']:>6.3f} {m['spatial_mi_mean']:>6.3f} "
              f"{m['lz_growth']:>+7.3f} {m['corr_glc_atp_mean']:>7.3f} "
              f"{m['p11_mean']:>6.3f} {m['mass_ratio']:>6.2f} "
              f"{m['reaction_events_total']:>10.0f}")

    signal = assess(result)
    result["signal"] = signal
    print(f"\nSättigungs-Rückkehr: {result.get('saturation_return')}  "
          f"Fenster-Ordnung: {result.get('window_ordering_of')}  "
          f"DISTINCT: {result.get('n_distinct')}/9")
    print(f"Signal: {signal}")

    if signal == "FALSIFIED":
        result["next_vectors"] = [
            "iter-11-Fenster als Gitter-/Numerik-Artefakt einstufen; "
            "strategic_vectors/iter-11.md-Korrektur",
            "Neue Fenster-Suche mit Produktionstack (Sweep auf 24³ von null)",
        ]
    elif signal.startswith("REPLICATED"):
        result["next_vectors"] = [
            "Fenster als reproduzierte Physik akzeptieren (CANDIDATE → CONFIRMED-Verdacht)",
            "VECTOR_SATURATION_MARGIN mit produktionellem Tau-Leap",
            "VECTOR_ENDOGEN_UVC_TIMESCALE",
        ]
    else:
        result["next_vectors"] = [
            "Grenzen neu kalibrieren (Sprung-Diffusion vs. rint-Laplace mischt anders)",
            "Sweep-Bereich um die neuen Grenzen verfeinern",
        ]

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")
