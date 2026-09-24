"""iter-26 — VECTOR_EDGE_FINE_SWEEP: Feine Kante + D-Abhängigkeit.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

FRAGE
  Aus iter-25 next_vectors (MODERATE): "Feiner Sweep um die Kante +
  D-Abhängigkeit der Kante".
  (a) Wo liegt die Metrik-Kante bei D=0.05 genau (iter-25: k_edge=10,
      Band 10-30, Gitterabstand 3/Dezade)?
  (b) Wo bei D=0.15 (iter-25: k_edge=100, NULL bei k=10 INNERHALB der
      DISTINCT-Region 3 und 30)?
  (c) Wie wächst k_edge mit D (iter-25: 10 → 100 → nicht lokalisiert;
      Anteil Metrik-Baseline-Effekt offen)?
  (d) Ist die nicht-monotone D=0.05-Spalte (k=1/3/10 → D/NULL/D)
      Zellrauschen (iter-24-Lektion) oder Band-Struktur?

STRUKTURELLER VORAB-BEFUND
  iter-25 K4 hat die k·dt-Äquivalenz bereits 4/4 bit-identisch
  gemessen — der feine Sweep ist eine Verfeinerung desselben
  Damköhler-Gitters. Überschneidungszellen müssen bit-identisch zu
  iter-25 sein (K5, REGISTRATION_ERROR-Gate).

REGISTRIERTES PROTOTOKOLL
  M1 iter-25-Harness VERBATIM (import saturation_margin: run_config,
     classify, config_classification, SEEDS unverändert; GPU-Operator,
     RNG-Split). Kein Code-Wechsel am Harness.
  M2 FEIN-GITTER: D=0.05: k_f ∈ {1,2,3,5,7,10,14,20,30} (Faktor-
     Abstand ≤ 1.55); D=0.15: k_f ∈ {1,3,5,7,10,14,20,30,45,70,100,
     140,200}; dt=1e-5, Seeds {200,201,202}.
  M3 NEUE ANKER: D ∈ {0.10, 0.25, 0.30} mit Coarse-Gitter
     {1,3,10,30,100,300,1000} (Kanten-Verlauf; 0.45 aus iter-25
     wiederverwendet, rechtszensiert — OPPORTUN: bestehende Messung).
  M4 Kontrolle dt=0 je Anker (5 Anker), seed-gepaart.
  K1 Operator-Kalibrierung (validate_gpu, iter-24-Schwellen) — GATE.
  K2 Determinismus: run_config(1.0,1e-5,0.15,200) doppelt bit-identisch.
  K4a Äquivalenz-Spot-Check: (7,1e-5) vs (1,7e-5) und (14,1e-5) vs
     (1,1.4e-4) bei D=0.15 — bit-identisch erwartet.
  K5 Übergangs-Check: Fine-Grid-Zellen, die iter-25 bereits enthält
     (D=0.05: k∈{1,3,10,30}; D=0.15: k∈{1,3,10,30,100}) müssen in
     ALLEN Metrik-Feldern bit-identisch zu iter-25 result.json rows
     sein (läuferverschende Determinismus) — GATE.

KRITERIEN (BINDEND, K3)
  k_edge(D) = größtes k_f mit DISTINCT (per-Seed ≥2/3, VERBATIM
  iter-14/24/25). Registrierte Oberenden-Regel (iter-25, diesmal im
  Code): ist die Gitterspitze selbst DISTINCT, ist die Kante NICHT
  lokalisiert (untere Schranke = Gitterspitze).
  OBERKANTE_KLAR: alle k_f > k_edge NULL (kein DISTINCT oberhalb).
  BAND_ZUSAMMENHÄNGEND: kein NULL zwischen zwei DISTINCT-Zellen
  unterhalb der Kante (inkl. k=1 als Bandunterkante).
  Global = min der lokalisierten Kanten (konservativ, iter-25-Regel).

VERDICT-NAMEN
  V1a (D=0.05) / V1b (D=0.15):
    EDGE_UPPER_CONFIRMED  — lokalisiert, OBERKANTE_KLAR, k_edge ==
       iter-25-Wert (10 / 100)
    EDGE_UPPER_SHIFTED    — lokalisiert, OBERKANTE_KLAR, k_edge !=
       iter-25-Wert (iter-25-Kante korrigiert)
    EDGE_UPPER_UNCLEAR    — DISTINCT oberhalb des letzten DISTINCT
       (Rauschen/Struktur unentschieden; iter-25-Kante als
       rauschdominiert markiert)
    EDGE_NOT_LOCALIZED    — Gitterspitze DISTINCT
  V2 (D-Abhängigkeit über {0.05, 0.10, 0.15, 0.25, 0.30} + iter-25
     0.45 rechtszensiert):
    EDGE_D_MONOTONE       — konsistente monoton wachsende Kanten
       (Intervall-Konsistenz mit Zensur: für jedes benachbarte Paar
       gilt lb_i ≤ ub_{i+1} ∧ lb_{i+1} ≤ ub_i)
    EDGE_D_NONMONOTONE    — Verletzung
  REGISTRATION_ERROR — K1/K2/K4a/K5 verletzt.

  Fragen (a)/(b)/(d) laufen in V1a/V1b auf; (c) in V2.
  Zusätzlich berichtet: BAND_CONNECTED je Anker (Frage d).

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-25"))
import saturation_margin as sm  # noqa: E402 (Harness VERBATIM)

ITER25_RESULT = Path(__file__).resolve().parents[1] / "iter-25" / "result.json"

FINE_D005 = (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0)
FINE_D015 = (1.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0, 45.0, 70.0,
             100.0, 140.0, 200.0)
NEW_ANCHORS: dict[float, tuple[float, ...]] = {
    0.10: (1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0),
    0.25: (1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0),
    0.30: (1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0),
}
EQ_PAIRS = ((7.0, 1e-5), (14.0, 1e-5))
ITER25_EDGES = {"0.05": 10.0, "0.15": 100.0}


def run_anchor(diff_coeff: float, k_grid: tuple[float, ...],
               controls: dict[float, list[dict[str, float]]]) -> list[dict[str, Any]]:
    rows = []
    for k_f in k_grid:
        runs = [sm.run_config(k_f, sm.DT_SWEEP, diff_coeff, s) for s in sm.SEEDS]
        cls = sm.config_classification(runs, controls[diff_coeff])
        mean_run = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
        rows.append({"diff_coeff": diff_coeff, "k_factor": k_f,
                     "turnover_k_dt": k_f * sm.DT_SWEEP,
                     "classification": cls, "mean": mean_run})
        print(f"  D={diff_coeff:g} k_f={k_f:g} → {cls}", flush=True)
    return rows


def assess_anchor(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """K3 mit der REGISTRIERTEN Oberenden-Regel (iter-25, im Code)."""
    cells = {r["k_factor"]: r for r in rows if r["k_factor"] > 1.0}
    base = next(r for r in rows if r["k_factor"] == 1.0)
    grid = sorted(cells)
    distinct = [k for k in grid if cells[k]["classification"] == "DISTINCT"]
    if not distinct:
        return {"k_edge": None, "localized": False,
                "k1_class": base["classification"],
                "upper_clear": None, "band_connected": None}
    k_edge = max(distinct)
    localized = k_edge < grid[-1]  # Oberenden-Regel: Spitze DISTINCT ⇒ nicht lokalisiert
    upper_clear = all(
        cells[k]["classification"] == "NULL" for k in grid if k > k_edge
    ) if localized else None
    internal_nulls = [
        k for k in grid
        if any(d < k for d in distinct) and any(d > k for d in distinct)
        and cells[k]["classification"] != "DISTINCT"
    ]
    band_connected = len(internal_nulls) == 0
    return {"k_edge": k_edge, "localized": bool(localized),
            "k1_class": base["classification"],
            "upper_clear": bool(upper_clear) if upper_clear is not None else None,
            "band_connected": bool(band_connected),
            "internal_nulls": internal_nulls}


def verdict_anchor(a: dict[str, Any], iter25_edge: float) -> str:
    if not a["localized"]:
        return "EDGE_NOT_LOCALIZED"
    if not a["upper_clear"]:
        return "EDGE_UPPER_UNCLEAR"
    return "EDGE_UPPER_CONFIRMED" if a["k_edge"] == iter25_edge \
        else "EDGE_UPPER_SHIFTED"


def d_dependence(edges: dict[str, dict[str, Any]],
                 grids: dict[str, tuple[float, ...]]) -> dict[str, Any]:
    """V2: Intervall-Konsistenz mit Rechtszensur (Gitterspitze = lb)."""
    order = ["0.05", "0.1", "0.15", "0.25", "0.3", "0.45"]
    seq = []
    for d in order:
        key = next((k for k in edges if float(k) == float(d)), None)
        if key is None:
            continue
        e = edges[key]
        lb = e["k_edge"] if e["localized"] else max(grids[key])
        ub = e["k_edge"] if e["localized"] else float("inf")
        seq.append({"d": float(key), "lb": lb, "ub": ub,
                    "localized": e["localized"]})
    monotone = True
    for a, b in zip(seq, seq[1:], strict=False):
        if not (a["lb"] <= b["ub"] and b["lb"] <= a["ub"]):
            monotone = False
    # iter-25-Anker D=0.45: KORRIGIERTE Lesung (registrierte Oberenden-
    # Regel) = NICHT lokalisiert, untere Schranke = Gitterspitze 1e4.
    seq.append({"d": 0.45, "lb": 10000.0, "ub": float("inf"),
                "localized": False, "source": "iter-25_CORRIGIERT"})
    return {"sequence": seq, "verdict": "EDGE_D_MONOTONE" if monotone
            else "EDGE_D_NONMONOTONE"}


def main() -> None:
    print("=== iter-26: EDGE_FINE_SWEEP (feine Kante + D-Abhängigkeit, GPU) ===\n")

    print("K1 Operator-Kalibrierung:", flush=True)
    cal = sm.validate_gpu()
    print(f"  PASS={cal['pass']} (Masse {cal['mass_ok']}, Drift {cal['drift_ok']}, "
          f"Varianz {cal['var_ok']}, Beidseitigkeit {cal['symmetry_ok']})", flush=True)

    a = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 200)
    b = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 200)
    det = {"identical": a == b, "pass": bool(a == b)}
    print(f"K2 Determinismus: bit-identisch = {det['identical']}\n", flush=True)

    # K4a Äquivalenz-Spot-Check
    eq_rows = []
    eq_all = True
    for k_f, dt0 in EQ_PAIRS:
        x = [sm.run_config(k_f, dt0 / k_f, 0.15, s) for s in sm.SEEDS]
        y = [sm.run_config(1.0, dt0, 0.15, s) for s in sm.SEEDS]
        pair_equal = all(p == q for p, q in zip(x, y, strict=True))
        eq_all = eq_all and pair_equal
        eq_rows.append({"k_factor": k_f, "dt0": dt0, "bit_identical": pair_equal})
        print(f"K4a Äquiv (k={k_f:g}, dt={dt0 / k_f:g} vs 1, {dt0:g}): "
              f"bit-identisch={pair_equal}", flush=True)

    # K5 Übergangs-Check gegen iter-25
    iter25 = json.loads(ITER25_RESULT.read_text(encoding="utf-8"))
    iter25_rows = {(r["diff_coeff"], r["k_factor"]): r["mean"]
                   for r in iter25["rows"]}
    overlap = [(0.05, k) for k in (1.0, 3.0, 10.0, 30.0)] + \
              [(0.15, k) for k in (1.0, 3.0, 10.0, 30.0, 100.0)]
    k5_rows = []
    k5_all = True
    for d, k in overlap:
        runs = [sm.run_config(k, sm.DT_SWEEP, d, s) for s in sm.SEEDS]
        mean = {kk: float(np.mean([r[kk] for r in runs])) for kk in runs[0]}
        ref = iter25_rows[(d, k)]
        same = mean == ref
        k5_all = k5_all and same
        k5_rows.append({"diff_coeff": d, "k_factor": k, "bit_identical": same})
        print(f"K5 Übergang (D={d:g}, k={k:g}): bit-identisch={same}", flush=True)
    k5 = {"pass": bool(k5_all), "rows": k5_rows}
    print(flush=True)

    controls: dict[float, list[dict[str, float]]] = {}
    grids: dict[str, tuple[float, ...]] = {}

    print("Feine Anker:", flush=True)
    rows: list[dict[str, Any]] = []
    for d, grid in ((0.05, FINE_D005), (0.15, FINE_D015)):
        controls[d] = [sm.run_config(1.0, 0.0, d, s) for s in sm.SEEDS]
        grids[f"{d:g}"] = grid
        rows.extend(run_anchor(d, grid, controls))

    print("\nNeue D-Anker (Kanten-Verlauf):", flush=True)
    for d, grid in NEW_ANCHORS.items():
        controls[d] = [sm.run_config(1.0, 0.0, d, s) for s in sm.SEEDS]
        grids[f"{d:g}"] = grid
        rows.extend(run_anchor(d, grid, controls))

    print(f"\n{'label':<20} {'class':<9} {'LZgrw':>7} {'corr':>7} "
          f"{'tMI':>6} {'events':>10}")
    for row in rows:
        m = row["mean"]
        label = f"D={row['diff_coeff']:g},k={row['k_factor']:g}"
        print(f"{label:<20} {row['classification']:<9} {m['lz_growth']:>+7.3f} "
              f"{m['corr_glc_atp_mean']:>7.3f} {m['temporal_mi_mean']:>6.3f} "
              f"{m['reaction_events_total']:>10.0f}")

    edges: dict[str, dict[str, Any]] = {}
    anchor_verdicts: dict[str, str] = {}
    for d in (0.05, 0.15):
        key = f"{d:g}"
        a_ = assess_anchor([r for r in rows if r["diff_coeff"] == d])
        edges[key] = a_
        anchor_verdicts[key] = verdict_anchor(a_, ITER25_EDGES[key])
        print(f"\nAnker D={d:g}: {json.dumps(a_)} → {anchor_verdicts[key]}")
    for d in NEW_ANCHORS:
        key = f"{d:g}"
        edges[key] = assess_anchor([r for r in rows if r["diff_coeff"] == d])
        print(f"Anker D={d:g}: {json.dumps(edges[key])}")

    dd = d_dependence(edges, grids)
    print(f"\nD-Abhängigkeit: {dd['verdict']}")
    for s in dd["sequence"]:
        print(f"  D={s['d']:g}: lb {s['lb']:g} ub {s['ub']:g} "
              f"(lokalisiert={s['localized']})")

    result: dict[str, Any] = {
        "rows": rows, "n_seeds": len(sm.SEEDS),
        "edges": edges, "anchor_verdicts": anchor_verdicts,
        "d_dependence": dd,
        "k1_operator_calibration": {"pass": bool(cal["pass"])},
        "k2_determinism": det,
        "k4a_equivalence": {"rows": eq_rows, "pass": bool(eq_all)},
        "k5_iter25_consistency": k5,
    }
    final = "REGISTRATION_ERROR" if not (
        cal["pass"] and det["pass"] and eq_all and k5_all
    ) else "|".join([anchor_verdicts["0.05"], anchor_verdicts["0.15"], dd["verdict"]])
    result["final_verdict"] = final
    print(f"\nVERDICT: {final}")

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")


if __name__ == "__main__":
    main()
