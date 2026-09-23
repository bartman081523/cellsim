"""iter-24 — VECTOR_WINDOW_REPLICATION_V2: Trägt das iter-14-Damköhler-
Fenster unter dem KORRIGIERTEN beidseitigen Sprung-Operator?

VORAB-REGISTRIERUNG (2026-09-23, vor dem Lauf fixiert)

FRAGE
  iter-16 definiert den Vektor: "iter-14-Fenster mit dem KORRIGIERTEN
  beidseitigen Sprung-Operator re-replizieren (iter-14 lief mit dem
  drift-behafteten Operator)".
  Befundlage (git 3fa5753, emergence.py bei iter-14): der damalige
  Operator sprang EINSEITIG (upwind) —
      moves = rng.binomial(f_int, p_dir)          # p = 𝒟
      fields[s_id] = f_int - moves + np.roll(moves, 1, axis=axis)
  Das ist Advektion mit Drift +𝒟 pro Achse (Mittelverschiebung, NICHT
  Diffusion) und Varianzwachstum ≈ 3𝒟 gesamt — die damals registrierte
  Kalibrierung "Varianzwachstum 6·𝒟" traf die Implementation NICHT.
  Der iter-15-Fix (Produktion, heutige Version) macht die Sprünge
  beidseitig: n_out = binomial(f, 2𝒟), 50/50 auf ±Richtung → Drift 0,
  Varianzwachstum exakt 6𝒟 gesamt (2𝒟 je Achse).
  V2 re-repliziert das Fenster-Signal unter dem korrigierten Operator.
  Replikation heißt: GLEICHE Kriterien, GLEICHE nominal-𝒟-Achse,
  GLEICHES Gitter/Registry/Bump — ANDERES Operator-Substrat.

REGISTRIERTES PROTOTOKOLL
  M1 iter-14-Protokoll VERBATIM (alle Konstanten und Logiken):
     N_STEPS=600, SNAP_EVERY=10, Q_BIN=0.75, GRID=24³,
     DT_REACTS=(0.0, 1e-6, 1e-5, 1e-4, 1e-3),
     DIFF_COEFFS=(0.05, 0.15, 0.45), MIN_STRONG=6, MIN_WEAK=3,
     3-Reaktions-Subset ("glycolysis", "atp_hydrolysis",
     "atp_synthase"), Gauß-Bump amp=150 width=6 auf Glucose+ATP,
     RDMEAdapter(use_tau_leap=True), Metriken via emergence_metrics +
     corr_glc_atp_mean + p11_mean + mass_ratio + reaction_events_total.
  M2 EINZIGE Änderungen gegenüber iter-14:
     (a) Operator = Produktion post-iter-15 (beidseitiger Sprung);
     (b) Seeds {200, 201, 202} — disjunkt zu iter-11 {42,43,44} und
         iter-14 {100,101,102}.
  M3 Nominal-𝒟-Achse unverändert (0.05, 0.15, 0.45): der Vergleich ist
     "gleiche nominale Diffusivität, korrigierter Operator". Die
     tatsächliche Mischrate unterscheidet sich (iter-14: 3𝒟 + Drift;
     V2: 6𝒟, driftfrei) — genau das ist der getestete Substrat-Wechsel.

KRITERIEN (vor dem Lauf fixiert)
  K1 Operator-Kalibrierung als UNABHÄNGIGE Messung (keine Selbst-
     Bezeugung durch den Docstring), Delta N=2e5 im Gitterzentrum:
     (a) Massenerhalt exakt (alle Probe-Läufe);
     (b) Drift: |com-Verschiebung pro Achse| ≤ 0.05 Voxel nach k=20
         Schritten auf 63³ (alter Operator: +𝒟·k = 1.0/3.0/9.0 Voxel —
         20× bis 180× über der Schwelle; Proben-Rauschen ≤ 0.01);
     (c) Varianz: |var/Achse − 2𝒟·k| / (2𝒟·k) ≤ 0.03 nach k=20 auf 63³
         (wrap-frei: 3σ = 12.7 < 31.5 Halbbreite);
     (d) Beidseitigkeit: Symmetrie-Ratio |c₊−c₋|/(c₊+c₋) der ±x-Nachbarn
         ≤ 0.1 nach 1 Schritt vom Delta (alter Operator: c₋ = 0 →
         ratio = 1 exakt; Proben-Rauschen ≤ 0.03).
     Vorarbeit-Note: ein vor der Registrierung dokumentierter Probe
     (seed 777) bestätigte Massenerhalt, Drift ≤ 2e-3/Achse und
     Varianz 2𝒟/Achse; er INFORMIERTE die Schwellen (Abstände ≥ 4×
     Rauschen), buchte aber KEIN Ergebnis.
  K2 Harness-Determinismus: Konfig (D=0.15, dt=1e-5, seed 200) doppelt
     ausgeführt → bit-identische Metrik-Dictionaries.
  K3 (BINDEND) iter-14-Verdict-Logik VERBATIM:
     classify je Seed: RUNAWAY wenn mass_ratio > 3 (Konfig-RUNAWAY bei
     ≥2/3 Seeds); DISTINCT wenn corr_drop > 0.3 ODER lz_diff > 0.05
     ODER tmi_diff > 0.05 gegen die seed-gepaarte Kontrolle (dt=0);
     Konfig-DISTINCT bei ≥2/3 Seeds DISTINCT.
     assess: 0 DISTINCT → FALSIFIED; Sättigungs-Rückkehr
     |corr(dt=1e-3) − ctrl| ≤ 0.1 je D; Fenster-Ordnung
     |corr(1e-6) − ctrl| < |corr(1e-5) − ctrl| für ≥2/3 D;
     ≥6 DISTINCT + sat + order≥2 → REPLICATED_STRONG; ≥3 →
     REPLICATED_WEAK; sonst PARTIAL.

VERDICT-NAMEN (keine Gesichts-sparende Verzweigung)
  REPLICATED_STRONG_V2 — Fenster trägt unter Operator-, Gitter- UND
      Seed-Wechsel (Kette iter-11→14→24: rint-Laplace 16³ → einseitig
      24³ → beidseitig 24³); stärkste Replikationsform; Basis des
      N*-Gesetzes steht.
  REPLICATED_WEAK_V2  — Struktur wiedergefunden, Grenzen verschoben.
  PARTIAL_V2          — 1–2 DISTINCT: Grenzen neu kalibrieren.
  FALSIFIED_V2        — 0 DISTINCT: iter-14-Signal war (teilweise)
      drift-kalibriert; Kette iter-11/14 korrigieren; das N*-Gesetz
      verliert seine empirische Basis (iter-15/16-Brücke offen).
  REGISTRATION_ERROR_V2 — K1/K2 verletzt.

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
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
SEEDS = (200, 201, 202)  # V2: disjunkt zu iter-11 {42..44}, iter-14 {100..102}
GRID: tuple[int, int, int] = (24, 24, 24)
DT_REACTS = (0.0, 1e-6, 1e-5, 1e-4, 1e-3)
DIFF_COEFFS = (0.05, 0.15, 0.45)
MIN_STRONG = 6
MIN_WEAK = 3

# K1-Anker (registriert)
K1_DELTA_N = 200_000
K1_GRID = (63, 63, 63)
K1_STEPS = 20
K1_DRIFT_TOL = 0.05    # Voxel pro Achse nach k Schritten
K1_VAR_TOL = 0.03      # relative Abweichung von 2𝒟·k pro Achse
K1_SYMMETRY_TOL = 0.1  # |c₊−c₋|/(c₊+c₋) nach 1 Schritt

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


def operator_calibration() -> dict[str, Any]:
    """K1: unabhängige Messung der registrierten Operator-Kalibrierung.

    Delta K1_DELTA_N im Zentrum von K1_GRID; (a) Massenerhalt nach 1
    und nach K1_STEPS Schritten; (b) Drift (com-Verschiebung pro Achse)
    nach K1_STEPS Schritten; (c) Varianz pro Achse vs 2𝒟·k; (d)
    Beidseitigkeit via ±x-Nachbar-Symmetrie nach 1 Schritt.
    """
    idx = np.indices(K1_GRID).astype(np.float64)
    center = tuple(s // 2 for s in K1_GRID)
    rows: list[dict[str, Any]] = []
    mass_ok = True
    drift_ok = True
    var_ok = True
    sym_ok = True
    for d in DIFF_COEFFS:
        rng = make_rng(555, 0, 0)
        f = np.zeros(K1_GRID, dtype=np.int64)
        f[center] = K1_DELTA_N
        fields = {"A": f}
        before = int(f.sum())
        # 1 Schritt → Beidseitigkeit + Massenerhalt
        stochastic_jump_diffusion(fields, d, rng)
        g = fields["A"].astype(np.float64)
        after1 = int(g.sum())
        cm = tuple(int(c) for c in center)
        c_minus = float(g[(cm[0] - 1, cm[1], cm[2])])
        c_plus = float(g[(cm[0] + 1, cm[1], cm[2])])
        sym = abs(c_plus - c_minus) / max(c_plus + c_minus, 1.0)
        sym_ok = sym_ok and sym <= K1_SYMMETRY_TOL
        # weitere k−1 Schritte → Drift + Varianz
        for _ in range(K1_STEPS - 1):
            stochastic_jump_diffusion(fields, d, rng)
        g = fields["A"].astype(np.float64)
        afterk = int(g.sum())
        mass_ok = mass_ok and before == after1 == afterk
        com = [float((g * idx[i]).sum() / afterk - center[i]) for i in range(3)]
        var = [
            float((g * (idx[i] - center[i] - com[i]) ** 2).sum() / afterk)
            for i in range(3)
        ]
        expect = 2.0 * d * K1_STEPS
        rel = [abs(v - expect) / expect for v in var]
        drift_ok = drift_ok and all(abs(c) <= K1_DRIFT_TOL for c in com)
        var_ok = var_ok and all(r <= K1_VAR_TOL for r in rel)
        rows.append({
            "d": d, "symmetry_ratio": sym,
            "c_plus_x": c_plus, "c_minus_x": c_minus,
            "com_per_axis": com, "var_per_axis": var,
            "expected_var": expect, "var_rel_err": rel,
        })
    return {
        "rows": rows, "mass_ok": mass_ok, "drift_ok": drift_ok,
        "var_ok": var_ok, "symmetry_ok": sym_ok,
        "pass": bool(mass_ok and drift_ok and var_ok and sym_ok),
    }


def determinism_check() -> dict[str, Any]:
    """K2: identischer Seed → bit-identische Metriken."""
    a = run_config(1e-5, 0.15, 200)
    b = run_config(1e-5, 0.15, 200)
    identical = a == b
    return {"identical": identical, "pass": bool(identical)}


def run_config(dt_react: float, diff_coeff: float, seed: int) -> dict[str, float]:
    """iter-14-Protokoll VERBATIM (Produktionstack, beidseitiger Operator)."""
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
    """iter-11/14-Kriterien unverändert: korrelation/LZ/tMI vs. Kontrolle."""
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
    for d in DIFF_COEFFS:
        controls[d] = [run_config(0.0, d, s) for s in SEEDS]

    for d in DIFF_COEFFS:
        for dt_r in DT_REACTS:
            if dt_r == 0.0:
                runs, cls, label = controls[d], "CONTROL", "control"
            else:
                runs = [run_config(dt_r, d, s) for s in SEEDS]
                per_seed = [
                    classify(r, c) for r, c in zip(runs, controls[d], strict=True)
                ]
                if per_seed.count("RUNAWAY") >= 2:
                    cls = "RUNAWAY"
                elif per_seed.count("DISTINCT") >= 2:
                    cls = "DISTINCT"
                else:
                    cls = "NULL"
                label = f"D={d:g},dt={dt_r:g}"
            mean_run = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
            rows.append({
                "label": label, "diff_coeff": d, "dt_react": dt_r,
                "classification": cls, "mean": mean_run,
            })

    return {"rows": rows, "n_seeds": len(SEEDS)}


def assess(result: dict[str, Any]) -> str:
    """iter-14-Kriterien VERBATIM auswerten."""
    rows = result["rows"]
    distinct = [
        r for r in rows
        if r["classification"] == "DISTINCT" and r["dt_react"] > 0
    ]
    n_distinct = len(distinct)
    if n_distinct == 0:
        return "FALSIFIED"

    result["n_distinct"] = n_distinct

    sat_ok = True
    for d in DIFF_COEFFS:
        row = next(r for r in rows if r["dt_react"] == 1e-3 and r["diff_coeff"] == d)
        ctrl = next(r for r in rows if r["dt_react"] == 0.0 and r["diff_coeff"] == d)
        if abs(row["mean"]["corr_glc_atp_mean"] - ctrl["mean"]["corr_glc_atp_mean"]) > 0.1:
            sat_ok = False

    order_ok = 0
    for d in DIFF_COEFFS:
        slow = next(r for r in rows if r["dt_react"] == 1e-6 and r["diff_coeff"] == d)
        mid = next(r for r in rows if r["dt_react"] == 1e-5 and r["diff_coeff"] == d)
        ctrl = next(r for r in rows if r["dt_react"] == 0.0 and r["diff_coeff"] == d)
        cs, cm, _cc = (
            row["mean"]["corr_glc_atp_mean"] - ctrl["mean"]["corr_glc_atp_mean"]
            for row in (slow, mid, ctrl)
        )
        if (abs(cs) < abs(cm)) or (cs == 0.0 and cm == 0.0):
            order_ok += 1

    result["saturation_return"] = sat_ok
    result["window_ordering_of"] = f"{order_ok}/3"
    if n_distinct >= MIN_STRONG and sat_ok and order_ok >= 2:
        return "REPLICATED_STRONG"
    if n_distinct >= MIN_WEAK:
        return "REPLICATED_WEAK"
    return "PARTIAL"


def main() -> None:
    print("=== iter-24: WINDOW_REPLICATION_V2 (korrigierter Sprung-Operator) ===")
    print(f"Gitter {GRID}, Seeds {SEEDS}, Operator: beidseitig (post-iter-15).\n")

    cal = operator_calibration()
    print("K1 Operator-Kalibrierung:")
    for r in cal["rows"]:
        print(f"  D={r['d']:g}: Symmetrie {r['symmetry_ratio']:.4f} "
              f"(c+ {r['c_plus_x']:.0f} / c- {r['c_minus_x']:.0f}), "
              f"Drift {[f'{c:+.4f}' for c in r['com_per_axis']]}, "
              f"Var/Achse {[f'{v:.3f}' for v in r['var_per_axis']]} "
              f"(erwartet {r['expected_var']:.3f}, "
              f"rel {[f'{e:.1e}' for e in r['var_rel_err']]})")
    print(f"  Masse {cal['mass_ok']}, Drift {cal['drift_ok']}, "
          f"Varianz {cal['var_ok']}, Beidseitigkeit {cal['symmetry_ok']} "
          f"({'PASS' if cal['pass'] else 'FAIL'})")

    det = determinism_check()
    print(f"K2 Determinismus: bit-identisch = {det['identical']} "
          f"({'PASS' if det['pass'] else 'FAIL'})\n")

    result: dict[str, Any] = sweep()
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
          f"DISTINCT: {result.get('n_distinct', 0)}/9")

    if not cal["pass"] or not det["pass"]:
        verdict = "REGISTRATION_ERROR_V2"
    elif signal == "REPLICATED_STRONG":
        verdict = "REPLICATED_STRONG_V2"
    elif signal == "REPLICATED_WEAK":
        verdict = "REPLICATED_WEAK_V2"
    elif signal == "PARTIAL":
        verdict = "PARTIAL_V2"
    else:
        verdict = "FALSIFIED_V2"
    result["verdict"] = verdict
    result["k1_operator_calibration"] = cal
    result["k2_determinism"] = det
    print(f"VERDICT: {verdict}")

    if verdict == "FALSIFIED_V2":
        result["next_vectors"] = [
            "iter-14-Signal als (teilweise) drift-kalibriert einstufen; "
            "strategic_vectors/iter-14.md + iter-16.md-Korrektur",
            "N*-Gesetz-Basis (iter-15/16) ohne empirisches Fenster neu "
            "begründen oder zurückstufen",
            "Neue Fenster-Suche von null unter dem beidseitigen Operator",
        ]
    elif verdict.endswith("_STRONG_V2") or verdict.endswith("_WEAK_V2"):
        result["next_vectors"] = [
            "Fenster trägt unter Operator-/Gitter-/Seed-Wechsel "
            "(iter-11→14→24); N*-Gesetz-Basis steht",
            "VECTOR_SATURATION_MARGIN mit beidseitigem Operator",
            "VECTOR_ENDOGEN_UVC_TIMESCALE",
        ]
    else:
        result["next_vectors"] = [
            "Grenzen unter dem beidseitigen Operator neu kalibrieren "
            "(Mischrate 2× iter-14, driftfrei)",
            "Sweep-Bereich um die neuen Grenzen verfeinern",
        ]

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")


if __name__ == "__main__":
    main()
