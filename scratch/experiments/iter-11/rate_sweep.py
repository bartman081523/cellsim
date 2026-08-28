"""Iter-11: RDME Rate-Sweep — Damköhler-Regime-Suche (VECTOR_RDME_TAU_LEAP_RATE_SWEEP).

Befund aus iter-10-retry: 1 globales Gillespie-Event/Schritt (an
zufälligem Voxel) hinterlässt keine Signatur in den Emergenz-Metriken
(reaktiv ≡ diffusiv; Diffusion sogar mehr LZ-Wachstum).

Fix hier: **lokales Tau-Leaping** — Propensitäten pro Voxel, Poisson-
Firings — so wirkt Chemie dort, wo das Substrat ist. Gesweept wird
das Operator-Splitting-Verhältnis Reaktion : Diffusion:

    a_voxel = k · dt_react · n_reaktant(voxel)     (first-order mass action)

Registry-k ist ODE-skaliert (per Sekunde, mM-Welt); die per-Voxel-
Propensität braucht daher dt_react als Sweep-Parameter. atp_synthase
(k=8800/s) bei dt_react=1e-3 → λ=8.8·n_ADP pro Schritt — das ist exakt
die Runaway-Zone, die Origin_Ruliad Phase 7 gegengetunt hat ("FIX:
Tuned chemistry parameters to prevent runaway"). Der Sweep kartiert
die Grenze ergebnisoffen: Gibt es ein stabiles Regime, in dem Chemie
sichtbar aus der Diffusion herausbricht — oder ist das Metrik-Suite
blind für Chemie? Beides ist ein Befund.

Chemie-Signatur zusätzlich zu MI/LZ: Kreuz-Spezies-Dekorrelation
(Glucose ↔ ATP). Diffusion allein erhält Proportionen identischer
Initialfelder (Korrelation ≈ +1); lokale Umwandlung Glucose→ATP
erzeugt Krater/Peak und senkt die Korrelation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.core.rng import make_rng
from cellsim.modules.emergence import (
    binarize,
    emergence_metrics,
    laplacian_3d,
)
from cellsim.modules.reactions import Reaction, default_registry

# Metabolit-Kern des Registry (first-order-Substrat pro Reaktion)
REACTION_SUBSET: dict[str, str] = {
    "glycolysis": "Glucose",      # Glc → 2 Pyr + 2 ATP
    "atp_hydrolysis": "ATP",      # ATP → ADP + Pi
    "atp_synthase": "ADP",        # ADP + Pi → ATP
}

Q_BIN = 0.75          # Binarisierungs-Quantil (wie iter-10-retry)
RUNAWAY_MASS_RATIO = 3.0
DISTINCT_CORR_DROP = 0.3   # Korrelations-Abfall vs. Kontrolle = Chemie sichtbar
DISTINCT_METRIC_DIFF = 0.05  # LZ/MI-Differenz vs. Kontrolle


def _load_subset() -> list[Reaction]:
    registry = default_registry()
    by_name = {r.name: r for r in registry.reactions}
    return [by_name[n] for n in REACTION_SUBSET]


def _gaussian_bump(grid: tuple[int, int, int], amp: float, width: float) -> np.ndarray:
    center = tuple(s // 2 for s in grid)
    idx3 = np.indices(grid)
    d2 = sum((idx3[axis] - c) ** 2 for axis, c in enumerate(center))
    return (amp * np.exp(-d2 / width)).astype(np.int64)


def _diffuse(fields: dict[str, np.ndarray], diff_coeff: float) -> None:
    """Vektorisierte Laplace-Diffusion mit Stabilitäts-Substepping.

    3D-7-Punkt-Laplacian = Summe dreier 1D-Differenzen (Eigenwerte je
    in [-4, 0]) → Gesamt-Spektrum λ ∈ [-12, 0]. Explizites Schema
    stabil für d ≤ 1/6 ≈ 0.167 — nicht 1/3 (iter-11-Fix: D=0.45
    divergierte bei d_sub=0.225 > 1/6 → INT64-Overflow). Größere D
    werden in Subschritte geteilt — physikalisch äquivalent.
    """
    n_sub = max(1, int(np.ceil(diff_coeff / 0.15)))
    d_sub = diff_coeff / n_sub
    for _ in range(n_sub):
        for s_id, f in fields.items():
            updated = f.astype(np.float64) + d_sub * laplacian_3d(f)
            if not np.all(np.isfinite(updated)):
                raise RuntimeError(
                    f"diffusion non-finite: species={s_id} d_sub={d_sub} "
                    f"max={np.nanmax(updated):.3e}"
                )
            fields[s_id] = np.maximum(np.rint(updated), 0.0).astype(np.int64)


def run_config(
    dt_react: float,
    diff_coeff: float,
    n_steps: int = 600,
    seed: int = 42,
    grid_shape: tuple[int, int, int] = (16, 16, 16),
    snap_every: int = 10,
) -> dict[str, float]:
    """Ein Sweep-Punkt: lokales Tau-Leaping + vektorisierte Laplace-Diffusion."""
    subset = _load_subset()
    rng = make_rng(seed, 0, 0)

    fields: dict[str, np.ndarray] = {
        s: np.full(grid_shape, 5, dtype=np.int64)
        for s in default_registry().species_ids
    }
    bump = _gaussian_bump(grid_shape, amp=150, width=6.0)
    fields["Glucose"] = fields["Glucose"] + bump
    fields["ATP"] = fields["ATP"] + bump

    initial_total = int(sum(v.sum() for v in fields.values()))
    events_total = 0
    snaps_atp: list[np.ndarray] = []
    snaps_glc: list[np.ndarray] = []
    corr_series: list[float] = []

    for step in range(n_steps):
        # 1) Vektorisierte Diffusion auf allen Spezies (Origin_Ruliad Phase 6)
        _diffuse(fields, diff_coeff)

        # 2) Lokales Tau-Leaping: Propensität pro Voxel, Poisson-Firings
        if dt_react > 0.0:
            for rxn in subset:
                reactant = REACTION_SUBSET[rxn.name]
                lam = rxn.k * dt_react * fields[reactant].astype(np.float64)
                if np.any(lam < 0) or not np.all(np.isfinite(lam)):
                    raise RuntimeError(
                        f"bad lam: rxn={rxn.name} min={lam.min():.3e} "
                        f"max={lam.max():.3e} field_min={fields[reactant].min()}"
                    )
                lam = np.minimum(lam, 1e6)  # Poisson-Obere-Grenze-Schutz
                fire = rng.poisson(lam).astype(np.int64)

                # Feasibility: alle negativen Stöchiometrien begrenzen
                for s_id, delta in rxn.species_change.items():
                    if delta < 0:
                        fire = np.minimum(fire, fields[s_id] // (-delta))
                n_fired = int(fire.sum())
                if n_fired == 0:
                    continue
                for s_id, delta in rxn.species_change.items():
                    v = fields.get(s_id)
                    if v is None:
                        continue
                    if delta < 0:
                        v -= fire * (-delta)
                    else:
                        v += fire * delta
                    np.maximum(v, 0, out=v)
                events_total += n_fired

        if step % snap_every == 0:
            g = fields["Glucose"].astype(np.float64)
            a = fields["ATP"].astype(np.float64)
            snaps_atp.append(binarize(a, q=Q_BIN).copy())
            snaps_glc.append(binarize(g, q=Q_BIN).copy())
            if g.std() > 1e-12 and a.std() > 1e-12:
                corr_series.append(float(np.corrcoef(g.ravel(), a.ravel())[0, 1]))
            else:
                corr_series.append(0.0)

    snaps = np.asarray(snaps_atp)
    m = emergence_metrics(snaps, grid_shape=grid_shape)

    final_total = int(sum(v.sum() for v in fields.values()))
    return {
        **m,
        "corr_glc_atp_mean": float(np.mean(corr_series)),
        "corr_glc_atp_last": float(corr_series[-1]),
        "p11_mean": float(np.mean(
            [float(np.mean((g & a).astype(np.float64)))
             for g, a in zip(snaps_glc, snaps_atp, strict=True)]
        )),
        "mass_ratio": float(final_total / max(initial_total, 1)),
        "reaction_events_total": float(events_total),
    }


def classify(cfg: dict[str, float], control: dict[str, float]) -> str:
    """Ein Sweep-Punkt vs. seine Diffusions-Kontrolle (gleiches D, dt_react=0)."""
    if not np.isfinite(cfg["mass_ratio"]) or cfg["mass_ratio"] > RUNAWAY_MASS_RATIO:
        return "RUNAWAY"
    corr_drop = abs(cfg["corr_glc_atp_mean"] - control["corr_glc_atp_mean"])
    lz_diff = abs(cfg["lz_growth"] - control["lz_growth"])
    tmi_diff = abs(cfg["temporal_mi_mean"] - control["temporal_mi_mean"])
    if corr_drop > DISTINCT_CORR_DROP or lz_diff > DISTINCT_METRIC_DIFF or tmi_diff > DISTINCT_METRIC_DIFF:
        return "DISTINCT"
    return "NULL"


def sweep(seeds: tuple[int, ...] = (42, 43, 44)) -> dict[str, Any]:
    dt_reacts = (0.0, 1e-6, 1e-5, 1e-4, 1e-3)
    diff_coeffs = (0.05, 0.15, 0.45)
    rows: list[dict[str, Any]] = []

    controls: dict[float, list[dict[str, float]]] = {}
    for D in diff_coeffs:
        controls[D] = [
            run_config(dt_react=0.0, diff_coeff=D, seed=s) for s in seeds
        ]

    for D in diff_coeffs:
        for dt_r in dt_reacts:
            if dt_r == 0.0:
                runs = controls[D]
                label, cls = "control", "CONTROL"
            else:
                runs = [run_config(dt_react=dt_r, diff_coeff=D, seed=s) for s in seeds]
                cls = classify_multi(
                    [classify(r, c) for r, c in zip(runs, controls[D], strict=True)]
                )
                label = f"D={D:g},dt={dt_r:g}"
            mean_run = {
                k: float(np.mean([r[k] for r in runs]))
                for k in runs[0]
            }
            rows.append({
                "label": label,
                "diff_coeff": D,
                "dt_react": dt_r,
                "classification": cls,
                "mean": mean_run,
            })
    return {"rows": rows, "n_seeds": len(seeds)}


def classify_multi(per_seed: list[str]) -> str:
    """Mehrheits-Entscheid über Seeds; RUNAWAY dominiert."""
    if per_seed.count("RUNAWAY") >= max(1, len(per_seed) // 2 + 1):
        return "RUNAWAY"
    distinct = per_seed.count("DISTINCT")
    if distinct >= max(1, len(per_seed) // 2 + 1):
        return "DISTINCT"
    return "NULL"


if __name__ == "__main__":
    print("=== iter-11: RDME Rate-Sweep (Damköhler-Regime-Suche) ===\n")
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

    distinct = [r for r in result["rows"] if r["classification"] == "DISTINCT"]
    runaway = [r for r in result["rows"] if r["classification"] == "RUNAWAY"]
    result["n_distinct"] = len(distinct)
    result["n_runaway"] = len(runaway)
    if distinct:
        # Stärkste Chemie-Signatur = stärkste Dekorrelation (|corr| minimal)
        best = min(distinct, key=lambda r: abs(r["mean"]["corr_glc_atp_mean"]))
        result["visible_regime"] = {
            "diff_coeff": best["diff_coeff"],
            "dt_react": best["dt_react"],
            "metrics": best["mean"],
        }
        print(f"\n→ Chemie sichtbar in {len(distinct)} Regimen; "
              f"Runaway-Zone: {len(runaway)} Konfigs.")
        print(f"→ Stabilste Chemie-Signatur: D={best['diff_coeff']:g}, "
              f"dt_react={best['dt_react']:g}")
        result["signal"] = "EMERGENT"
    elif runaway:
        print(f"\n→ Kein sichtbares Regime, aber Runaway-Grenze kartiert "
              f"({len(runaway)} Konfigs). Metrik-Suite möglicherweise chemie-blind.")
        result["signal"] = "NO_DISTINCT_RUNAWAY_ONLY"
    else:
        print("\n→ NULL: Chemie in keinem Regime von Diffusion unterscheidbar.")
        result["signal"] = "NULL"

    result["next_vectors"] = [
        "Falls EMERGENT: Regime in Production übernehmen (Tau-Leap-Option im RDMEAdapter) + Tests",
        "Falls NO_DISTINCT: Metrik-Sensitivität prüfen (Quantil, Gittergröße, Snapshot-Kadenz)",
        "VECTOR_GENESIS_UVC_BRIDGE: UVC 232 nm als ortsaufgelöste Photoreaktions-Quelle (iter-12)",
        "Querverbindung: Damköhler-Zahl Da = k·L²/D; Phase-Diagramm in experiment.md",
    ]

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")