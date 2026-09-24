"""iter-28 — VECTOR_SIGNAL_RELATIVE_RECLASS + VECTOR_DEEP_CELL_REPLICATION.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

MOTIVATION
  iter-27 V2 = H0_DOMINANT: die registrierte 0.05-Schwellen-Klassifikation
  produziert auf 4/5 Ankern 18-27 % false-DISTINCT unter reinem
  Kontroll-Rauschen; die Schwelle liegt 2-3x unter der natuerlichen
  Paar-Diff-Streuung. Der Standard-Fix ist ein effektgroessen-basiertes
  Kriterium (Gap in Einheiten der gemessenen Kontroll-Streuung statt
  absolute Schwelle). Dieser Vektor bucht die LANDSCHAFT unter einem
  solchen Kriterium neu — als reine Buchhaltung auf den vollstaendig
  persistierten per-seed-Vektoren von iter-26/27 — und repliziert die
  tiefsten Zellen out-of-sample (n=10, neue GPU-Laeufe).

TEIL 1 — SIGNAL_RELATIVE_RECLASS (0 GPU-min, nur Buchhaltung)
  M1 Artefakte fixiert: iter-26 result.json (43 Zellen, 3-Seed-Mittel,
  gebuchte n=3-Klassifikation), iter-27 result.json (30 Tier-A-Zellen
  mit n=10-per-seed-Vektoren, 5 Kontrollpools). KEINE neuen Laeufe.
  Tier A = 30 in iter-27 gelaufene Zellen; Tier B = die uebrigen
  iter-26-Zellen (n=3-Mittel); D=0.45 ist nicht im iter-26-Rows-Set
  (aus iter-25 rechtszensiert uebernommen, keine 10-Seed-Kontrolle)
  und bleibt NICHT BEHANPELT.
  M2 NEUES KRITERIUM (registriert): se_units = |mean_lz(Zelle, 3-Seed-
  Mittel aus iter-26) − mean_lz(Kontrolle, 10-Seed-Mittel)| /
  (sigma_ctrl10_lz · sqrt(2/3)) — VERBATIM die iter-27-K-D-Form,
  jetzt als Klassifikations-Regel: Label_SE = DISTINCT ⇔ se_units ≥ 2.0
  (Schwelle konventionell, wie iter-27 DEPTH_SE).
  K-B (H0 des Kriteriums): je Anker alle 2100 ungeordneten disjunkten
  Kontroll-Tripelpaare (A, B) — se_units_h0 = |mean_A − mean_B| /
  (sigma_ctrl10 · sqrt(2/3)) ≥ 2.0 → Rate je Anker. In-sample-
  Kalibrierung, explizit deklariert.
  K-C (sekundaer, Tier A): Welch-t = (mean10_Zelle − mean10_Ktrl) /
  sqrt(s2_zelle/10 + s2_ktrl/10), s2 ddof=1; Label_t = DISTINCT ⇔
  |t| ≥ 2.0.
  K-D (berichtend): corr/tmi-Inertie — max per-seed corr_drop /
  tmi_diff ueber Tier-A-Zellen vs Schwellen 0.3/0.05 (Erwartung aus
  iter-24/27: feuert nie; wenn doch, wird der LZ-only-Charakter des
  Reclass-Stacks eingeschraenkt deklariert — Befund, kein Gate).
GATES (bindend, Artefakt-Konsistenz statt Determinismus — keine Laeufe
  in Teil 1)
  K1 Recompute der 22 gebuchten DISTINCT-se_units == iter-27
     signal_depth_distinct.rows (Anzahl + Werte bit-identisch).
  K2 cls_n3-Verankerung: die 30 Tier-A-Zellen tragen in iter-27
     cls_n3 == iter-26-Klassifikation (30/30, aus Artefakten gelesen).
  Verletzung ⇒ REGISTRATION_ERROR, kein Verdict.
VERDICT-NAMEN (vor dem Lauf fixiert)
  V1 (Ueberleben der 22 gebuchten DISTINCT unter Label_SE):
    RECLASS_SEVERE   — ≥ 50 % kippen auf NULL.
    RECLASS_MODERATE — ≥ 25 % kippen.
    RECLASS_MILD     — ≥ 10 % kippen.
    RECLASS_STABLE   — < 10 % kippen.
    (Registrierte Erwartung aus iter-27 K-D: 17/22 innerhalb 2 SE ⇒
    ~77 % Flip ⇒ RECLASS_SEVERE. Das ist die Hypothese, nicht das
    Ergebnis.)
  V2 (Kalibrierung des SE-Kriteriums):
    SE_H0_CALIBRATED — H0-Rate ≤ 5 % auf allen Ankern.
    SE_H0_MARGINAL   — > 5 % auf ≥ 1 Anker, ≤ 10 % ueberall.
    SE_H0_LEAKY      — > 10 % auf ≥ 1 Anker.
  V3 (Recovery auf der NULL-Seite):
    SE_RECOVERS_CELLS — ≥ 1 gebuchte NULL-Zelle mit Label_SE = DISTINCT.
    SE_RECOVERS_NONE  — keine.
  V4 (Regel-Kongruenz Tier A, Label_SE vs Label_t):
    SE_RULES_AGREE (≥ 90 % der 30), SE_RULES_MARGINAL (≥ 70 %),
    SE_RULES_DIVERGE (< 70 %).
  REGISTRATION_ERROR — bindendes Gate verletzt.

TEIL 2 — DEEP_CELL_REPLICATION (out-of-sample, neue GPU-Laeufe)
  Zellen: D=0.10 k=3 (3.5 SE — tiefste Zelle der Landschaft),
  D=0.30 k=300 (2.9 SE), D=0.30 k=1000 (2.8 SE) — die drei tiefen
  gebuchten DISTINCT-Zellen, die iter-27 NICHT re-gelaufen ist.
  n=10 Seeds (200-209), dt_react = 1e-5, iter-25-Harness VERBATIM
  (30 Laeufe ≈ 6 min). Kriterium: |Welch-t| ≥ 2.0 gegen die iter-27-
  10-Seed-Kontrolle (ddof=1).
  V5 ∈ {DEEP_REPLICATED (3/3 mit |t| ≥ 2), DEEP_PARTIAL (≥ 1),
        DEEP_NOT_REPLICATED (0)}.

NICHT BEHAUPTET
  Das SE-Kriterium ist IN-SAMPLE kalibriert (Kriterium + H0-Rate auf
  denselben Kontrollen) — V2 ist eine Konsistenz-Messung des Stacks,
  keine out-of-sample-Validierung; die liefert nur Teil 2 (und sie
  ist n=3-Zellen-umfangreich, nicht registrierungstauglich als
  "Bestaetigung" der Landstruktur). Keine Zell-Claims; Label_SE/Label_t
  sind Eigenschaften des Metrik-Stacks. D=0.45 ohne Kontrolle nicht
  buchbar. Post-hoc-Konsistenz wird NIE als Bestaetigung gebucht.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-25"))
import saturation_margin as sm  # noqa: E402 (Harness VERBATIM)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-27"))
from seed_budget import SEEDS_10, h0_pairs  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = Path(__file__).resolve().parents[1]
ITER26_RESULT = EXP / "iter-26" / "result.json"
ITER27_RESULT = EXP / "iter-27" / "result.json"

DEPTH_SE = 2.0
T_THRESHOLD = 2.0
SE_FACTOR = float(np.sqrt(2.0 / 3.0))  # VERBATIM wie iter-27 K-D
# Konventionelle Verdict-Schwellen (vor dem Lauf fixiert)
FLIP_SEVERE = 0.50
FLIP_MODERATE = 0.25
FLIP_MILD = 0.10
H0_CAL = 0.05
H0_LEAKY_SE = 0.10
AGREE_HI = 0.90
AGREE_LO = 0.70
DEEP_CELLS: tuple[tuple[float, float], ...] = ((0.10, 3.0), (0.30, 300.0),
                                               (0.30, 1000.0))
METRIC_KEYS = ("lz_growth", "corr_glc_atp_mean", "temporal_mi_mean",
               "p11_mean", "mass_ratio", "reaction_events_total")


def welch_t(runs: list[dict[str, float]],
            ctrl: list[dict[str, float]]) -> float:
    a = [r["lz_growth"] for r in runs]
    b = [r["lz_growth"] for r in ctrl]
    ma, mb = float(np.mean(a)), float(np.mean(b))
    sa, sb = float(np.std(a, ddof=1)), float(np.std(b, ddof=1))
    n_a, n_b = len(a), len(b)
    denom = (sa * sa / n_a + sb * sb / n_b) ** 0.5
    if denom == 0.0:
        return 0.0
    return (ma - mb) / denom


def main() -> None:
    print("=== iter-28: SIGNAL_RELATIVE_RECLASS + DEEP_CELL_REPLICATION ===\n")

    iter26 = json.loads(ITER26_RESULT.read_text(encoding="utf-8"))
    iter27 = json.loads(ITER27_RESULT.read_text(encoding="utf-8"))
    i26_rows = {(r["diff_coeff"], r["k_factor"]): r for r in iter26["rows"]}
    i27_rows = {(r["diff_coeff"], r["k_factor"]): r for r in iter27["rows"]}

    sigma_ctrl = {d: iter27["h0_false_distinct"][f"{d:g}"]["sigma_within"]
                  for d in sm_anchors()}
    ctrl_mean_lz = {d: iter27["controls"][f"{d:g}"]["mean"]["lz_growth"]
                    for d in sm_anchors()}
    ctrl_per_seed = {d: iter27["controls"][f"{d:g}"]["per_seed"]
                     for d in sm_anchors()}
    anchors = sm_anchors()

    # --- Gates (bindend, Artefakt-Konsistenz) -------------------------------
    print("Gates (Artefakt-Konsistenz):", flush=True)
    n22 = 0
    g1_all = True
    for (d, k_f), r26 in i26_rows.items():
        if r26["classification"] != "DISTINCT":
            continue
        se = sigma_ctrl[d] * SE_FACTOR
        gap = abs(r26["mean"]["lz_growth"] - ctrl_mean_lz[d])
        ref = [x for x in iter27["signal_depth_distinct"]["rows"]
               if x["diff_coeff"] == d and x["k_factor"] == k_f]
        ok = len(ref) == 1 and ref[0]["se_units"] == gap / se
        g1_all = g1_all and ok
    n22 = sum(1 for r in iter26["rows"]
              if r["classification"] == "DISTINCT")
    g1 = n22 == iter27["signal_depth_distinct"]["n_distinct"] and g1_all
    print(f"  K1 Recompute DISTINCT-Tiefe: {n22} Zellen, bit-identisch = {g1}",
          flush=True)
    g2_all = all(i27_rows[(d, k_f)]["cls_n3"] == r26["classification"]
                 for (d, k_f), r26 in i26_rows.items()
                 if (d, k_f) in i27_rows)
    g2 = g2_all
    print(f"  K2 cls_n3-Verankerung (Tier A): uebereinstimmend = {g2}\n",
          flush=True)

    # --- Teil 1: SE-Reclass ueber alle 43 Zellen ----------------------------
    rows = []
    for (d, k_f), r26 in sorted(i26_rows.items()):
        se = sigma_ctrl[d] * SE_FACTOR
        gap = abs(r26["mean"]["lz_growth"] - ctrl_mean_lz[d])
        se_units = gap / se if se > 0 else float("inf")
        label_se = "DISTINCT" if se_units >= DEPTH_SE else "NULL"
        tier = "A" if (d, k_f) in i27_rows else "B"
        rows.append({"diff_coeff": d, "k_factor": k_f, "tier": tier,
                     "iter26_classification": r26["classification"],
                     "lz_mean_3": r26["mean"]["lz_growth"],
                     "lz_gap": gap, "se_units": se_units,
                     "label_se": label_se})
    booked_distinct = [r for r in rows
                       if r["iter26_classification"] == "DISTINCT"]
    booked_null = [r for r in rows
                   if r["iter26_classification"] == "NULL"]
    n_flip = sum(1 for r in booked_distinct if r["label_se"] == "NULL")
    n_recov = sum(1 for r in booked_null if r["label_se"] == "DISTINCT")
    print(f"SE-Reclass: {n_flip}/{len(booked_distinct)} gebuchte DISTINCT "
          f"kippen auf NULL; {n_recov}/{len(booked_null)} gebuchte NULL "
          f"steigen auf DISTINCT", flush=True)
    for r in rows:
        if (r["iter26_classification"] == "DISTINCT") != (r["label_se"] == "DISTINCT"):
            print(f"  Flip D={r['diff_coeff']:g} k={r['k_factor']:g} "
                  f"({r['tier']}): iter-26 {r['iter26_classification']} -> "
                  f"{r['label_se']} (se_units {r['se_units']:.2f})", flush=True)

    # --- H0 des SE-Kriteriums (2100 Paare je Anker) --------------------------
    h0 = {}
    for d in anchors:
        per_seed = ctrl_per_seed[d]
        runs_by_seed = {s: r for s, r in zip(SEEDS_10, per_seed, strict=True)}
        se = sigma_ctrl[d] * SE_FACTOR
        n_total = n_distinct = 0
        for a_seeds, b_seeds in h0_pairs(SEEDS_10):
            ma = float(np.mean([runs_by_seed[s]["lz_growth"]
                                for s in a_seeds]))
            mb = float(np.mean([runs_by_seed[s]["lz_growth"]
                                for s in b_seeds]))
            n_total += 1
            if abs(ma - mb) / se >= DEPTH_SE:
                n_distinct += 1
        rate = n_distinct / n_total
        h0[f"{d:g}"] = {"n_pairs": n_total, "n_distinct": n_distinct,
                        "rate": rate}
        print(f"H0(SE) D={d:g}: DISTINCT {n_distinct}/{n_total} "
              f"({100.0 * rate:.1f} %)", flush=True)
    print(flush=True)

    # --- Welch-t Tier A (sekundaer) + corr/tmi-Inertie -----------------------
    for r in rows:
        if r["tier"] != "A":
            continue
        d, k_f = r["diff_coeff"], r["k_factor"]
        runs10 = i27_rows[(d, k_f)]["per_seed"]
        t = welch_t(runs10, ctrl_per_seed[d])
        r["welch_t"] = t
        r["label_t"] = "DISTINCT" if abs(t) >= T_THRESHOLD else "NULL"
    agree = sum(1 for r in rows if r["tier"] == "A"
                and r["label_se"] == r["label_t"])
    n_tier_a = sum(1 for r in rows if r["tier"] == "A")
    agree_rate = agree / n_tier_a
    print(f"Regel-Kongruenz Tier A: {agree}/{n_tier_a} ({100.0 * agree_rate:.0f} %)",
          flush=True)
    max_corr = max(
        (c["corr_glc_atp_mean"] - p["corr_glc_atp_mean"]
         for r in rows if r["tier"] == "A"
         for c, p in zip(i27_rows[(r["diff_coeff"], r["k_factor"])]["per_seed"],
                         ctrl_per_seed[r["diff_coeff"]], strict=True)),
        default=0.0)
    max_tmi = max(
        (abs(c["temporal_mi_mean"] - p["temporal_mi_mean"])
         for r in rows if r["tier"] == "A"
         for c, p in zip(i27_rows[(r["diff_coeff"], r["k_factor"])]["per_seed"],
                         ctrl_per_seed[r["diff_coeff"]], strict=True)),
        default=0.0)
    print(f"corr/tmi-Inertie: max corr_drop {max_corr:.4f} (Schwelle 0.3), "
          f"max tmi_diff {max_tmi:.4f} (Schwelle 0.05)\n", flush=True)

    # --- Verdicte Teil 1 ------------------------------------------------------
    flip_rate = n_flip / len(booked_distinct) if booked_distinct else 0.0
    if flip_rate >= FLIP_SEVERE:
        v1 = "RECLASS_SEVERE"
    elif flip_rate >= FLIP_MODERATE:
        v1 = "RECLASS_MODERATE"
    elif flip_rate >= FLIP_MILD:
        v1 = "RECLASS_MILD"
    else:
        v1 = "RECLASS_STABLE"
    rates = [h0[f"{d:g}"]["rate"] for d in anchors]
    if all(r <= H0_CAL for r in rates):
        v2 = "SE_H0_CALIBRATED"
    elif all(r <= H0_LEAKY_SE for r in rates):
        v2 = "SE_H0_MARGINAL"
    else:
        v2 = "SE_H0_LEAKY"
    v3 = "SE_RECOVERS_CELLS" if n_recov >= 1 else "SE_RECOVERS_NONE"
    if agree_rate >= AGREE_HI:
        v4 = "SE_RULES_AGREE"
    elif agree_rate >= AGREE_LO:
        v4 = "SE_RULES_MARGINAL"
    else:
        v4 = "SE_RULES_DIVERGE"

    # --- Teil 2: Deep-Cell-Replikation (30 GPU-Laeufe) ------------------------
    print("Teil 2 — Deep-Cell-Replikation (n=10, GPU):", flush=True)
    deep_rows = []
    for d, k_f in DEEP_CELLS:
        runs = [sm.run_config(k_f, sm.DT_SWEEP, d, s) for s in SEEDS_10]
        t = welch_t(runs, ctrl_per_seed[d])
        lz = [r["lz_growth"] for r in runs]
        deep_rows.append({
            "diff_coeff": d, "k_factor": k_f,
            "lz_mean_10": float(np.mean(lz)),
            "sigma_10_ddof1": float(np.std(lz, ddof=1)),
            "welch_t": t, "replicated": bool(abs(t) >= T_THRESHOLD),
            "per_seed": [{k: r[k] for k in METRIC_KEYS} for r in runs],
        })
        print(f"  D={d:g} k={k_f:g}: LZ-Mittel {float(np.mean(lz)):+.4f} "
              f"(σ {float(np.std(lz, ddof=1)):.4f}) |t| = {abs(t):.2f} "
              f"→ {'REPLIZIERT' if abs(t) >= T_THRESHOLD else 'NICHT repliziert'}",
              flush=True)
    n_deep = sum(1 for r in deep_rows if r["replicated"])
    if n_deep == len(DEEP_CELLS):
        v5 = "DEEP_REPLICATED"
    elif n_deep >= 1:
        v5 = "DEEP_PARTIAL"
    else:
        v5 = "DEEP_NOT_REPLICATED"

    gates_pass = g1 and g2
    verdicts = {"v1_reclass": v1, "v2_h0_se": v2, "v3_recovery": v3,
                "v4_rule_agreement": v4, "v5_deep_replication": v5}
    final = (" | ".join(verdicts.values()) if gates_pass
             else "REGISTRATION_ERROR")
    print(f"\nV1 (Reclass): {v1}")
    print(f"V2 (H0 des SE-Kriteriums): {v2}")
    print(f"V3 (NULL-Seite): {v3}")
    print(f"V4 (Regel-Kongruenz): {v4}")
    print(f"V5 (Deep-Replikation): {v5}")
    print(f"\nVERDICT: {final}")

    result = {
        "vector": "VECTOR_SIGNAL_RELATIVE_RECLASS + VECTOR_DEEP_CELL_REPLICATION",
        "seeds": list(SEEDS_10),
        "anchors": list(anchors),
        "gates": {"k1_artifact_consistency": g1, "k2_cls_n3_anchor": g2},
        "se_reclass_rows": rows,
        "h0_se_criterion": h0,
        "welch_t_agreement": {"n_tier_a": n_tier_a, "agree": agree,
                              "rate": agree_rate},
        "corr_tmi_inertia": {"max_corr_drop": max_corr,
                             "max_tmi_diff": max_tmi},
        "deep_cells": {"criterion": "welch_t >= 2.0 (ddof=1)",
                       "n_replicated": n_deep,
                       "rows": deep_rows},
        "verdicts": {**verdicts, "final": final},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2),
                                      encoding="utf-8")
    print(f"\n→ {HERE / 'result.json'}")


def sm_anchors() -> tuple[float, ...]:
    return (0.05, 0.10, 0.15, 0.25, 0.30)


if __name__ == "__main__":
    main()
