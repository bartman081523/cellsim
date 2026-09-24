"""iter-27 — VECTOR_STOCH_CONTROL_METRIC: Seed-Budget + Kontroll-Rausch-Floor.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

FRAGE (dreifach motiviert: iter-24 Zellrauschen, iter-25 Kante ruht auf
der schwächsten Anker-Zelle, iter-26 NONMONOTONE + LZ-Straddle +
22/43-Mittel-Ebenen-Diskordanz)
  (a) Wie oft liefert die registrierte Schwellen-Klassifikation
      DISTINCT, wenn NUR Kontroll-Rauschen drin ist (False-DISTINCT-
      Rate unter H0, gemessen an 10-Seed-Kontrollpools)?
  (b) Ist die gebuchte Kanten-/Band-Landschaft der Fein-Anker stabil
      unter Verzehnfachung des Seed-Budgets (n=3 → n=10), oder verschiebt
      sich die Kante / kippt der Lokalisierungs-Status / löst sich die
      Insel-Struktur auf?
  (c) Ist die Zell-seitige per-seed-Streuung (Diffusion + Tau-leap)
      größer als die Kontroll-seitige (nur Diffusion, dt=0)?

STRUKTURELLER VORAB-BEFUND (Registrierung, nicht Ergebnis)
  iter-26 mean_vs_perseed: die registrierte Klassifikation ist eine
  per-Seed-Stimme (≥2/3), keine Mittel-Ebenen-Eigenschaft (22/43
  Widersprüche); die per-seed-LZ-Streuung der Kontrollen allein beträgt
  bis 0.139 (D=0.05) / 0.109 (D=0.15) — dieselbe Größenordnung wie die
  registrierte 0.05-Schwelle. Erwartung daher: der Floor ist NICHT
  klein gegen die Schwelle. Das ist die Hypothese, nicht das Ergebnis.

REGISTRIERTES PROTOTOKOLL
  M1 iter-25-Harness VERBATIM (import saturation_margin: run_config,
     classify, config_classification, SEEDS, Konstanten unverändert;
     GPU-Operator iter-24-validiert). KEINE Änderung am Solver.
     Output-ERWEITERung (registriert, Lektion iter-26 CORREKTUR #1):
     per-seed-Metrikvektoren werden vollständig persistiert.
  M2 Seed-Budget n=10: SEEDS_10 = (200..209). Anker
     D ∈ {0.05, 0.10, 0.15, 0.25, 0.30}. Kontrollen: k=1, dt=0,
     10 Seeds je Anker (50 Läufe).
  M3 Zellen (n=10): ALLE Feingitter-Zellen der Fein-Anker — D=0.05:
     k_f ∈ {1,2,3,5,7,10,14,20,30}; D=0.15: k_f ∈ {1,3,5,7,10,14,20,
     30,45,70,100,140,200} — plus die Diskordanz-/Kanten-Zellen der
     Coarse-Anker D=0.10 {30,100,300,1000}, D=0.25 {1,30},
     D=0.30 {10,30}. Insgesamt 30 Zellen × 10 Seeds = 300 Läufe,
     dt_react = 1e-5. Kostenschätzung: ~351 Läufe ≈ 60-70 min.
  M4 Klassifikations-Regeln (beide persistiert):
     - n=3-Regel VERBATIM (iter-14/24/25): seeds (200,201,202),
       seed-gepaart gegen die 3-Seed-Kontrolle (Teilmenge des
       10-Seed-Pools), ≥2/3 DISTINCT. Dient der Kontinuität und dem
       K5''-Gate.
     - n=10-Regel (NEU, registriert): per-seed classify(run_s,
       ctrl_mean_10) für alle 10 Seeds (Referenz = 10-Seed-Kontroll-
       Mittel — es existiert kein 1:1-Seed-Pairing über 200..209
       hinaus; deklarierte Abweichung von der Paarung, nicht von den
       Schwellen). RUNAWAY bei ≥5/10 RUNAWAY, sonst DISTINCT bei
       ≥6/10 DISTINCT, sonst NULL.
GATES
  K1 Operator-Kalibrierung (iter-24-Schwellen, in-run berichtet).
  K2 (bindend) Determinismus: run_config(1.0, 1e-5, 0.15, 200) doppelt
     bit-identisch.
  K5' (bindend) Übergang: die 3-Seed-Submittel (200-202) aller 30
     Zellen müssen in ALLEN Metrik-Feldern bit-identisch zu iter-26
     result.json sein (läuferübergreifender Determinismus).
  K5'' (bindend) cls_n3 aller 30 Zellen == iter-26 gebuchte
     Klassifikation (bei bit-identischen Mitteln und Kontrollen zwingend).
  Verletzung eines bindenden Gates ⇒ REGISTRATION_ERROR, kein Verdict.
KRITERIEN (vor dem Lauf fixiert)
  K-A (H0-Rate, Frage a): je Anker alle UNGEORDNETEN disjunkten
     Tripelpaare (A, B) aus den 10 Kontroll-Seeds — A als Zellen, B als
     Kontrolle, config_classification VERBATIM. 2100 Paare je Anker.
     Rate = DISTINCT / 2100.
  K-B (Kante unter n=10, Frage b): k_edge_n10 je Fein-Anker mit der
     registrierten Oberenden-Regel (iter-25/26): Gitterspitze DISTINCT
     ⇒ nicht lokalisiert; Vergleich von k_edge/lokalisiert/
     band_connected gegen die n=3-Werte DIESES Laufs (K5''-verankert).
     Coarse-Anker: nur Zell-Ebene (kein k_edge-Claim, Gitter unvollständig).
  K-C (Spread-Ratio, Frage c): σ_within(lz_growth, ddof=0, n=10) je
     Zelle vs σ_within der Kontrolle; Median-Ratio je Anker.
  K-D (Signal-Tiefe, aus iter-26-Artefakten, ohne neue Läufe): je
     gebuchte DISTINCT-Zelle (ohne D=0.45) Differenz |cell_mean3_lz −
     ctrl_mean10_lz| in Einheiten von SE = σ_ctrl10·sqrt(2/3); zählne,
     wie viele innerhalb 2 SE liegen (grenznah).
VERDICT-NAMEN (keine Gesichts-sparende Verzweigung)
  V1 (Frage b, stärkste Kategorie zuerst):
    EDGE_STATUS_CHANGED_N10 — ≥1 Fein-Anker wechselt lokalisiert ↔
        nicht lokalisiert unter n=10.
    EDGE_SHIFTED_N10      — ≥1 Fein-Anker: k_edge_n10 ≠ k_edge_n3.
    BAND_STRUCTURE_CHANGED_N10 — Kante + Status stabil, aber
        band_connected kippt (Insel-Struktur ist Seed-Budget-Artefakt
        oder erst unter n=10 sichtbar).
    EDGE_STABLE_N10       — Kante, Status und Band unverändert.
  V2 (Frage a):
    H0_CLEAN    — False-DISTINCT-Rate < 5 % auf allen Ankern.
    H0_LEAKY    — ≥ 5 % auf ≥ 1 Anker, < 20 % überall.
    H0_DOMINANT — ≥ 20 % auf ≥ 2 Ankern.
    (Schwellen konventionell, vor dem Lauf fixiert.)
  V3 (Frage c):
    SPREAD_SYMMETRIC      — Median-Ratio < 1.5 auf allen Ankern.
    SPREAD_CELL_DOMINATED — Median-Ratio ≥ 1.5 auf ≥ 2 Ankern.
  REGISTRATION_ERROR — bindendes Gate verletzt.
NICHT BEHAUPTET
  Keine neuen Kanten-Claims (iter-26-Verdicte stehen; n=10-Werte sind
  eine NEUE registrierte Regel, keine Revision der gebuchten n=3-
  Klassifikation). Keine Aussage über reale syn3A-Enzymdichten; die
  H0-Rate ist eine Eigenschaft DIESES Metrik-Stacks (LZ/ corr/tMI,
  0.05/0.3/0.05-Schwellen) + Registry-Subsets + Gitters, nicht der Zelle.

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-25"))
import saturation_margin as sm  # noqa: E402 (Harness VERBATIM)

HERE = Path(__file__).resolve().parent
ITER26_RESULT = Path(__file__).resolve().parents[1] / "iter-26" / "result.json"

SEEDS_10 = tuple(range(200, 210))
ANCHORS = (0.05, 0.10, 0.15, 0.25, 0.30)
FINE_GRIDS: dict[float, tuple[float, ...]] = {
    0.05: (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0),
    0.15: (1.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0, 45.0, 70.0,
           100.0, 140.0, 200.0),
}
COARSE_CELLS: dict[float, tuple[float, ...]] = {
    0.10: (30.0, 100.0, 300.0, 1000.0),
    0.25: (1.0, 30.0),
    0.30: (10.0, 30.0),
}
# H0-Schwellen und Spread-Schwelle (konventionell, vor dem Lauf fixiert)
H0_LEAKY = 0.05
H0_DOMINANT = 0.20
SPREAD_RATIO = 1.5
DEPTH_SE = 2.0
METRIC_KEYS = ("lz_growth", "corr_glc_atp_mean", "temporal_mi_mean",
               "p11_mean", "mass_ratio", "reaction_events_total")


def cls_n10(runs: list[dict[str, float]],
            ctrl_mean: dict[str, float]) -> str:
    """NEUE registrierte n=10-Regel (Schwellen VERBATIM, Referenz = Mittel)."""
    per_seed = [sm.classify(r, ctrl_mean) for r in runs]
    if per_seed.count("RUNAWAY") >= 5:
        return "RUNAWAY"
    if per_seed.count("DISTINCT") >= 6:
        return "DISTINCT"
    return "NULL"


def h0_pairs(seeds: tuple[int, ...]) -> list[tuple[tuple[int, ...],
                                                   tuple[int, ...]]]:
    """Alle ungeordneten disjunkten Tripelpaare aus 10 Seeds (2100)."""
    out = []
    for a in itertools.combinations(seeds, 3):
        rest = tuple(s for s in seeds if s not in a)
        for b in itertools.combinations(rest, 3):
            if a < b:
                out.append((a, b))
    return out


def assess_grid_n10(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """K-B: k_edge unter der n=10-Regel (Oberenden-Regel wie iter-26)."""
    cells = {r["k_factor"]: r for r in rows if r["k_factor"] > 1.0}
    grid = sorted(cells)
    distinct = [k for k in grid if cells[k]["cls_n10"] == "DISTINCT"]
    if not distinct:
        return {"k_edge": None, "localized": False,
                "band_connected": None, "internal_nulls": []}
    k_edge = max(distinct)
    localized = k_edge < grid[-1]
    internal_nulls = [
        k for k in grid
        if any(d < k for d in distinct) and any(d > k for d in distinct)
        and cells[k]["cls_n10"] != "DISTINCT"
    ]
    return {"k_edge": k_edge, "localized": bool(localized),
            "band_connected": len(internal_nulls) == 0,
            "internal_nulls": internal_nulls}


def main() -> None:
    print("=== iter-27: STOCH_CONTROL_METRIC (Seed-Budget + Rausch-Floor, GPU) ===\n")

    print("K1 Operator-Kalibrierung:", flush=True)
    cal = sm.validate_gpu()
    print(f"  PASS={cal['pass']} (Masse {cal['mass_ok']}, Drift {cal['drift_ok']}, "
          f"Varianz {cal['var_ok']}, Beidseitigkeit {cal['symmetry_ok']})", flush=True)

    a = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 200)
    b = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 200)
    k2 = bool(a == b)
    print(f"K2 Determinismus: bit-identisch = {k2}\n", flush=True)

    # --- Kontrollen: 10 Seeds je Anker (50 Läufe) --------------------------
    controls_per_seed: dict[float, list[dict[str, float]]] = {}
    controls_mean: dict[float, dict[str, float]] = {}
    for d in ANCHORS:
        runs = [sm.run_config(1.0, 0.0, d, s) for s in SEEDS_10]
        controls_per_seed[d] = runs
        controls_mean[d] = {k: float(np.mean([r[k] for r in runs]))
                            for k in runs[0]}
        lz = [r["lz_growth"] for r in runs]
        print(f"Kontrolle D={d:g}: LZ-Mittel "
              f"{controls_mean[d]['lz_growth']:+.4f} | per-seed "
              f"{[f'{v:+.3f}' for v in lz]} | σ {float(np.std(lz)):.4f}",
              flush=True)
    print(flush=True)

    # --- Zellen: 30 Konfigurationen × 10 Seeds (300 Läufe) -----------------
    iter26 = json.loads(ITER26_RESULT.read_text(encoding="utf-8"))
    iter26_rows = {(r["diff_coeff"], r["k_factor"]): r
                   for r in iter26["rows"]}

    rows: list[dict[str, Any]] = []
    k5p_rows, k5pp_rows = [], []
    k5p_all, k5pp_all = True, True
    for d in ANCHORS:
        grid = FINE_GRIDS[d] if d in FINE_GRIDS else COARSE_CELLS[d]
        for k_f in grid:
            runs = [sm.run_config(k_f, sm.DT_SWEEP, d, s) for s in SEEDS_10]
            mean10 = {k: float(np.mean([r[k] for r in runs]))
                      for k in runs[0]}
            sub3 = [r for r, s in zip(runs, SEEDS_10, strict=True)
                    if s in sm.SEEDS]
            mean3 = {k: float(np.mean([r[k] for r in sub3]))
                     for k in sub3[0]}
            ctrl3 = [r for r, s in zip(controls_per_seed[d], SEEDS_10,
                                       strict=True) if s in sm.SEEDS]
            cls3 = sm.config_classification(sub3, ctrl3)
            cls10 = cls_n10(runs, controls_mean[d])
            ref = iter26_rows[(d, k_f)]
            same_mean = mean3 == ref["mean"]
            same_cls = cls3 == ref["classification"]
            k5p_all = k5p_all and same_mean
            k5pp_all = k5pp_all and same_cls
            k5p_rows.append({"diff_coeff": d, "k_factor": k_f,
                             "bit_identical": same_mean})
            k5pp_rows.append({"diff_coeff": d, "k_factor": k_f,
                              "match": same_cls})
            rows.append({
                "diff_coeff": d, "k_factor": k_f,
                "turnover_k_dt": k_f * sm.DT_SWEEP,
                "cls_n3": cls3, "cls_n10": cls10,
                "iter26_classification": ref["classification"],
                "mean_3": mean3, "mean_10": mean10,
                "per_seed": [{k: r[k] for k in METRIC_KEYS}
                             for r in runs],
            })
            print(f"Zelle D={d:g} k={k_f:g}: n3={cls3} n10={cls10} "
                  f"(iter-26: {ref['classification']})", flush=True)
    k5p = {"pass": bool(k5p_all), "n": len(k5p_rows), "rows": k5p_rows}
    k5pp = {"pass": bool(k5pp_all), "rows": k5pp_rows}
    print(f"\nK5' (3-Seed-Submittel vs iter-26): {k5p['n']} Zellen, "
          f"bit-identisch = {k5p['pass']}", flush=True)
    print(f"K5'' (cls_n3 vs iter-26-Klassifikation): übereinstimmend = "
          f"{k5pp['pass']}\n", flush=True)

    # --- K-A: False-DISTINCT-Rate unter H0 (Buchhaltung, keine Läufe) ------
    h0: dict[str, Any] = {}
    for d in ANCHORS:
        runs_by_seed = {s: r for s, r in zip(SEEDS_10,
                                             controls_per_seed[d],
                                             strict=True)}
        n_total = n_distinct = n_runaway = 0
        for a_seeds, b_seeds in h0_pairs(SEEDS_10):
            runs_a = [runs_by_seed[s] for s in a_seeds]
            runs_b = [runs_by_seed[s] for s in b_seeds]
            verdict = sm.config_classification(runs_a, runs_b)
            n_total += 1
            if verdict == "DISTINCT":
                n_distinct += 1
            elif verdict == "RUNAWAY":
                n_runaway += 1
        lz = [r["lz_growth"] for r in controls_per_seed[d]]
        pair_diffs = [abs(x - y) for x, y in itertools.combinations(lz, 2)]
        rate = n_distinct / n_total
        h0[f"{d:g}"] = {
            "n_pairs": n_total, "n_distinct": n_distinct,
            "n_runaway": n_runaway, "rate_distinct": rate,
            "lz_pair_q50": float(np.quantile(pair_diffs, 0.50)),
            "lz_pair_q95": float(np.quantile(pair_diffs, 0.95)),
            "lz_pair_max": float(np.max(pair_diffs)),
            "sigma_within": float(np.std(lz)),
        }
        print(f"H0 D={d:g}: DISTINCT {n_distinct}/{n_total} "
              f"({100.0 * rate:.1f} %) | |ΔLZ| q95 "
              f"{h0[f'{d:g}']['lz_pair_q95']:.4f} | σ "
              f"{h0[f'{d:g}']['sigma_within']:.4f}", flush=True)

    # --- K-B: Kanten unter n=10 (Fein-Anker) -------------------------------
    edges_n10: dict[str, Any] = {}
    for d in FINE_GRIDS:
        key = f"{d:g}"
        a_n10 = assess_grid_n10([r for r in rows if r["diff_coeff"] == d])
        # n=3-Referenz DIESES Laufs (K5''-verankert gegen iter-26)
        grid = FINE_GRIDS[d]
        cells3 = {r["k_factor"]: r for r in rows
                  if r["diff_coeff"] == d and r["k_factor"] > 1.0}
        d3 = [k for k in sorted(cells3)
              if cells3[k]["cls_n3"] == "DISTINCT"]
        k_edge_n3 = max(d3) if d3 else None
        loc_n3 = k_edge_n3 is not None and k_edge_n3 < grid[-1]
        edges_n10[key] = {
            "n3": {"k_edge": k_edge_n3,
                   "localized": bool(loc_n3)},
            "n10": a_n10,
        }
        print(f"\nKante D={d:g}: n3 (k_edge {k_edge_n3}, lokalisiert "
              f"{loc_n3}) vs n10 (k_edge {a_n10['k_edge']}, lokalisiert "
              f"{a_n10['localized']}, Band zusammenhängend "
              f"{a_n10['band_connected']}, interne NULLs "
              f"{a_n10['internal_nulls']})", flush=True)

    # --- K-C: Spread-Ratio --------------------------------------------------
    spread: dict[str, Any] = {}
    for d in ANCHORS:
        sig_ctrl = h0[f"{d:g}"]["sigma_within"]
        ratios = []
        for r in rows:
            if r["diff_coeff"] != d:
                continue
            lz = [p["lz_growth"] for p in r["per_seed"]]
            sig_cell = float(np.std(lz))
            ratios.append(sig_cell / sig_ctrl if sig_ctrl > 0 else np.inf)
        med = float(np.median(ratios))
        spread[f"{d:g}"] = {"median_ratio": med, "n_cells": len(ratios)}
        print(f"Spread D={d:g}: Median-Ratio σ_zelle/σ_kontrolle = "
              f"{med:.2f} ({len(ratios)} Zellen)", flush=True)

    # --- K-D: Signal-Tiefe der gebuchten DISTINCT-Zellen (iter-26-Artefakt)
    ctrl_mean10_lz = {d: controls_mean[d]["lz_growth"] for d in ANCHORS}
    depth_rows = []
    for r in iter26["rows"]:
        d = r["diff_coeff"]
        if d not in ANCHORS:  # D=0.45: keine 10-Seed-Kontrolle registriert
            continue
        if r["classification"] != "DISTINCT":
            continue
        diff = abs(r["mean"]["lz_growth"] - ctrl_mean10_lz[d])
        se = h0[f"{d:g}"]["sigma_within"] * np.sqrt(2.0 / 3.0)
        depth_rows.append({"diff_coeff": d, "k_factor": r["k_factor"],
                           "lz_gap": diff, "se_units": diff / se if se > 0
                           else np.inf})
    n_shallow = sum(1 for x in depth_rows if x["se_units"] < DEPTH_SE)
    print(f"\nSignal-Tiefe: {n_shallow}/{len(depth_rows)} gebuchte "
          f"DISTINCT-Zellen innerhalb {DEPTH_SE:g} SE des Kontroll-"
          f"Rauschens", flush=True)

    # --- Verdicte ------------------------------------------------------------
    status_changed = any(
        edges_n10[f"{d:g}"]["n3"]["localized"]
        != edges_n10[f"{d:g}"]["n10"]["localized"] for d in FINE_GRIDS)
    shifted = any(
        edges_n10[f"{d:g}"]["n3"]["k_edge"]
        != edges_n10[f"{d:g}"]["n10"]["k_edge"] for d in FINE_GRIDS)
    band_changed = any(
        edges_n10[f"{d:g}"]["n3"]["localized"]
        and edges_n10[f"{d:g}"]["n10"]["localized"]
        and edges_n10[f"{d:g}"]["n10"]["band_connected"] is not None
        and edges_n10[f"{d:g}"]["n10"]["band_connected"]
        != _band_connected_n3(rows, d) for d in FINE_GRIDS)
    if status_changed:
        v1 = "EDGE_STATUS_CHANGED_N10"
    elif shifted:
        v1 = "EDGE_SHIFTED_N10"
    elif band_changed:
        v1 = "BAND_STRUCTURE_CHANGED_N10"
    else:
        v1 = "EDGE_STABLE_N10"

    rates = [h0[f"{d:g}"]["rate_distinct"] for d in ANCHORS]
    n_dom = sum(1 for r in rates if r >= H0_DOMINANT)
    n_leaky = sum(1 for r in rates if r >= H0_LEAKY)
    if n_dom >= 2:
        v2 = "H0_DOMINANT"
    elif n_leaky >= 1:
        v2 = "H0_LEAKY"
    else:
        v2 = "H0_CLEAN"

    ratios_med = [spread[f"{d:g}"]["median_ratio"] for d in ANCHORS]
    n_hi = sum(1 for x in ratios_med if x >= SPREAD_RATIO)
    v3 = "SPREAD_CELL_DOMINATED" if n_hi >= 2 else "SPREAD_SYMMETRIC"

    gates_pass = k2 and k5p["pass"] and k5pp["pass"]
    final = f"{v1} | {v2} | {v3}" if gates_pass else "REGISTRATION_ERROR"

    print(f"\nV1 (Seed-Budget): {v1}")
    print(f"V2 (H0-Rate): {v2}")
    print(f"V3 (Spread): {v3}")
    print(f"\nVERDICT: {final}")

    result = {
        "vector": "VECTOR_STOCH_CONTROL_METRIC",
        "seeds": list(SEEDS_10),
        "anchors": list(ANCHORS),
        "gates": {"k1": cal, "k2_determinism": k2,
                  "k5p_bit_identical": k5p, "k5pp_cls_match": k5pp},
        "controls": {f"{d:g}": {
            "mean": controls_mean[d],
            "per_seed": [{k: r[k] for k in METRIC_KEYS}
                         for r in controls_per_seed[d]],
        } for d in ANCHORS},
        "rows": rows,
        "h0_false_distinct": h0,
        "edges_n10_vs_n3": edges_n10,
        "spread_ratio": spread,
        "signal_depth_distinct": {
            "se_units_threshold": DEPTH_SE,
            "n_distinct": len(depth_rows),
            "n_within_2se": n_shallow,
            "rows": depth_rows,
        },
        "verdicts": {"v1_seed_budget": v1, "v2_h0_rate": v2,
                     "v3_spread": v3, "final": final},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2),
                                      encoding="utf-8")
    print(f"\n→ {HERE / 'result.json'}")


def _band_connected_n3(rows: list[dict[str, Any]], d: float) -> bool | None:
    """band_connected der n=3-Klassifikation DIESES Laufs (Fein-Anker)."""
    cells = {r["k_factor"]: r for r in rows
             if r["diff_coeff"] == d and r["k_factor"] > 1.0}
    grid = sorted(cells)
    distinct = [k for k in grid if cells[k]["cls_n3"] == "DISTINCT"]
    if not distinct:
        return None
    internal = [k for k in grid
                if any(dd < k for dd in distinct)
                and any(dd > k for dd in distinct)
                and cells[k]["cls_n3"] != "DISTINCT"]
    return len(internal) == 0


if __name__ == "__main__":
    main()
