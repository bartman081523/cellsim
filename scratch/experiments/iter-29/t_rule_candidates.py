"""iter-29 — VECTOR_T_RULE_CANDIDATES.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

MOTIVATION
  iter-28 V4 = SE_RULES_DIVERGE: die Welch-t-Regel (n=10 per-seed gegen
  10-Seed-Kontrolle) dominiert die 3-Seed-SE-Regel — sie findet 14
  zusaetzliche Signale, verliert keines. Aber: die t-Regel hat SELBST
  keine gemessene H0-Rate, und ihre staerksten Kandidaten
  (D=0.25 k=1 t=+4.60, D=0.15 k=14 t=-3.81, D=0.05 k=1 t=-3.42) sind
  Tier-A-Buchhaltung auf EXISTIERENDEN Seeds (200-209) — iter-28
  Struktur-Vorbehalt: die iter-27-Kontrolle definiert die Referenz und
  besteht aus denselben Seeds. Dieser Vektor misst (a) die H0-Rate der
  t-Statistik auf den Kontrollpools und (b) repliziert die drei
  Kandidaten an FRISCHEN Seeds mit FRISCHER Kontrolle — out-of-sample
  in Laeufen UND Kontroll-Seeds.

TEIL 1 — T_RULE_H0 (0 GPU, Buchhaltung auf iter-27-Kontrollpools)
  Je Anker: alle UNGEORDNETEN disjunkten 5/5-Splits der 10 Kontroll-
  Seeds (C(10,5)/2 = 126), Welch-t (ddof=1) zwischen den LZ-Vektoren
  der beiden Haelften, Rate von |t| >= 2.0. Nominal fuer df ≈ 8:
  P(|t| >= 2.0) ≈ 8.0 % — genau daran wird kalibriert.
  Sekundaer: die 3/3-Tripelpaare (2100 je Anker, h0_pairs VERBATIM aus
  iter-27) mit Welch-t auf Tripel-Ebene (df ≈ 4, nominal ≈ 11.6 %).
  Beides ist eine Eigenschaft der t-Statistik UNTER SCHWEREN
  VERTEILUNGSSCHWAENZEN des Metrik-Stacks, nicht der Zelle.

TEIL 2 — CANDIDATE_REPLICATION (out-of-sample, neue GPU-Laeufe)
  Zellen (die drei staerksten iter-28-t-Kandidaten):
    D=0.05 k=1   (Tier-A t=-3.42, negativ)
    D=0.15 k=14  (Tier-A t=-3.81, negativ)
    D=0.25 k=1   (Tier-A t=+4.60, positiv)
  Explorativ (angemeldet, nicht Teil von V2/V3): D=0.10 k=30
    (Tier-A t=+2.15 — Vertreterin des Hoch-k-Plateaus).
  Seeds 300-309 (frishe Block, disjunkt zu 200-209), dt_react = 1e-5,
  iter-25-Harness VERBATIM. Referenz: FRISCHE Kontrollen k=1, dt=0,
  Seeds 300-309 je Anker (4 Anker x 10 = 40 Kontroll-Laeufe; 4 Zellen
  x 10 = 40 Zell-Laeufe; 80 gesamt ≈ 14 min).
  Kriterium (registriert):
    STRICT: |t_fresh| >= 2.0 UND sign(t_fresh) == sign(t_tierA).
    ABS (sekundaer): |t_fresh| >= 2.0 (Richtung egal).
  K-C (berichtend): Konsistenz frische vs iter-27-Kontrollen —
    z = (mean_fresh - mean_i27) / sqrt(s1^2/10 + s2^2/10), ddof=1,
    beide Seiten. Erwartung: |z| ≲ 2-3; grosse |z| ⇒ Kontroll-Floor
    nicht seed-stabil (Vorbehalt wird geschaeft).

GATES (bindend)
  K1 Artefakt-Konsistenz: die 3 Kandidaten-t-Werte, recomputet aus den
     iter-27-per-seed-Vektoren, muessen bit-identisch zu iter-28
     result.json sein (Recompute mit EXAKT derselben welch_t-Funktion,
     import aus signal_reclass).
  K2 Determinismus: run_config doppelt bit-identisch.
  Verletzung ⇒ REGISTRATION_ERROR, kein Verdict.

VERDICT-NAMEN (vor dem Lauf fixiert)
  V1 (H0 der t-Regel, 5/5-Splits):
    T_H0_CALIBRATED — Rate <= 8 % auf allen Ankern (Nominal df ≈ 8).
    T_H0_INFLATED   — > 8 % auf >= 1 Anker, <= 15 % ueberall.
    T_H0_LEAKY      — > 15 % auf >= 1 Anker.
  V2 (Kandidaten-Replikation, STRICT, 3 Zellen):
    CAND_REPLICATED_ALL — 3/3 repliziert.
    CAND_PARTIAL        — 1-2/3.
    CAND_NONE           — 0/3.
  V3 (sekundaer, ABS): CAND_ABS_ALL / CAND_ABS_PARTIAL / CAND_ABS_NONE.
  V4 (explorativ, berichtend): EXPL_REPLICATED / EXPL_NOT_REPLICATED.
  REGISTRATION_ERROR — bindendes Gate verletzt.

NICHT BEHAUPTET
  Die Kandidaten sind POST-HOC aus iter-28 gewaehlt — genau das ist der
  Punkt: out-of-sample-Test von Post-hoc-Kandidaten. Replikation an
  frischen Seeds + frischer Kontrolle hebt sie zu Befunden; Scheitern
  entwertet die Tier-A-Stimme als Rauschen. Keine Landschafts-Claims;
  die t-H0-Rate ist eine Eigenschaft des Metrik-Stacks unter
  schweren Tails (df-approximiert), keine exakte Signifikanz-Theorie.
  Post-hoc-Konsistenz wird NIE als Bestaetigung gebucht.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-27"))
from seed_budget import SEEDS_10, h0_pairs  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-28"))
from signal_reclass import welch_t  # noqa: E402 (EXAKT dieselbe Funktion)

HERE = Path(__file__).resolve().parent
EXP = Path(__file__).resolve().parents[1]
ITER27_RESULT = EXP / "iter-27" / "result.json"
ITER28_RESULT = EXP / "iter-28" / "result.json"

T_THRESHOLD = 2.0
H0_CAL = 0.08      # nominal P(|t_df~8| >= 2) ≈ 8.0 %
H0_LEAKY = 0.15
ANCHORS = (0.05, 0.10, 0.15, 0.25)
CANDIDATES = ((0.05, 1.0), (0.15, 14.0), (0.25, 1.0))
EXPLORATORY = (0.10, 30.0)
SEEDS_FRESH = tuple(range(300, 310))
METRIC_KEYS = ("lz_growth", "corr_glc_atp_mean", "temporal_mi_mean",
               "p11_mean", "mass_ratio", "reaction_events_total")


def splits_5_5(seeds: tuple[int, ...]) -> list[tuple[tuple[int, ...],
                                                     tuple[int, ...]]]:
    """Alle ungeordneten disjunkten 5/5-Splits (126 bei 10 Seeds)."""
    out = []
    for a in itertools.combinations(seeds, 5):
        b = tuple(s for s in seeds if s not in a)
        if a[0] < b[0]:
            out.append((a, b))
    return out


def control_stats(runs: list[dict[str, float]]) -> tuple[float, float]:
    lz = [r["lz_growth"] for r in runs]
    return float(np.mean(lz)), float(np.std(lz, ddof=1))


def main() -> None:
    print("=== iter-29: T_RULE_CANDIDATES (t-H0 + frische Replikation, GPU) ===\n")

    iter27 = json.loads(ITER27_RESULT.read_text(encoding="utf-8"))
    iter28 = json.loads(ITER28_RESULT.read_text(encoding="utf-8"))
    anchors_all = (0.05, 0.10, 0.15, 0.25, 0.30)
    ctrl_per_seed = {d: iter27["controls"][f"{d:g}"]["per_seed"]
                     for d in anchors_all}
    i27_rows = {(r["diff_coeff"], r["k_factor"]): r for r in iter27["rows"]}
    i28_rows = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter28["se_reclass_rows"]}

    # --- Gates ---------------------------------------------------------------
    print("Gates:", flush=True)
    k1_all = True
    for d, k_f in CANDIDATES:
        t = welch_t(i27_rows[(d, k_f)]["per_seed"], ctrl_per_seed[d])
        ref = i28_rows[(d, k_f)]["welch_t"]
        k1_all = k1_all and (t == ref)
        print(f"  K1 D={d:g} k={k_f:g}: recomputed {t:.4f} == "
              f"iter-28 {ref:.4f} -> {t == ref}", flush=True)
    a = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 300)
    b = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 300)
    k2 = bool(a == b)
    print(f"  K2 Determinismus: bit-identisch = {k2}\n", flush=True)

    # --- Teil 1: H0 der t-Regel (5/5-Splits + 3/3-Tripel, Buchhaltung) -------
    print("Teil 1 — H0 der Welch-t-Regel (Buchhaltung):", flush=True)
    h0 = {}
    for d in anchors_all:
        lz = [r["lz_growth"] for r in ctrl_per_seed[d]]
        by_seed = {s: r["lz_growth"]
                   for s, r in zip(SEEDS_10, ctrl_per_seed[d], strict=True)}
        n55 = n55_hits = 0
        for a_seeds, b_seeds in splits_5_5(SEEDS_10):
            t = welch_t([{"lz_growth": by_seed[s]} for s in a_seeds],
                        [{"lz_growth": by_seed[s]} for s in b_seeds])
            n55 += 1
            if abs(t) >= T_THRESHOLD:
                n55_hits += 1
        n33 = n33_hits = 0
        for a_seeds, b_seeds in h0_pairs(SEEDS_10):
            t = welch_t([{"lz_growth": by_seed[s]} for s in a_seeds],
                        [{"lz_growth": by_seed[s]} for s in b_seeds])
            n33 += 1
            if abs(t) >= T_THRESHOLD:
                n33_hits += 1
        h0[f"{d:g}"] = {"rate_5_5": n55_hits / n55,
                        "rate_3_3": n33_hits / n33,
                        "n_5_5": n55, "n_3_3": n33}
        print(f"  D={d:g}: 5/5 {n55_hits}/{n55} "
              f"({100.0 * n55_hits / n55:.1f} %) | 3/3 {n33_hits}/{n33} "
              f"({100.0 * n33_hits / n33:.1f} %)", flush=True)
    rates55 = [h0[f"{d:g}"]["rate_5_5"] for d in anchors_all]
    if all(r <= H0_CAL for r in rates55):
        v1 = "T_H0_CALIBRATED"
    elif all(r <= H0_LEAKY for r in rates55):
        v1 = "T_H0_INFLATED"
    else:
        v1 = "T_H0_LEAKY"
    print(flush=True)

    # --- Teil 2: frische Kontrollen + Kandidaten (80 GPU-Laeufe) -------------
    print("Teil 2 — frische Replikation (Seeds 300-309, GPU):", flush=True)
    fresh_ctrl: dict[float, list[dict[str, float]]] = {}
    consistency = {}
    for d in ANCHORS:
        runs = [sm.run_config(1.0, 0.0, d, s) for s in SEEDS_FRESH]
        fresh_ctrl[d] = runs
        mf, sf = control_stats(runs)
        mi, si = control_stats(ctrl_per_seed[d])
        denom = (sf * sf / 10.0 + si * si / 10.0) ** 0.5
        z = (mf - mi) / denom if denom > 0 else float("inf")
        consistency[f"{d:g}"] = {"z": z, "mean_fresh": mf,
                                 "sigma_fresh": sf, "mean_i27": mi,
                                 "sigma_i27": si}
        print(f"  Kontrolle D={d:g}: LZ {mf:+.4f} (σ {sf:.4f}) vs iter-27 "
              f"{mi:+.4f} (σ {si:.4f}) | z = {z:+.2f}", flush=True)
    print(flush=True)

    def run_cell(d: float, k_f: float) -> list[dict[str, float]]:
        return [sm.run_config(k_f, sm.DT_SWEEP, d, s) for s in SEEDS_FRESH]

    cand_rows = []
    n_strict = n_abs = 0
    for d, k_f in CANDIDATES:
        runs = run_cell(d, k_f)
        t = welch_t(runs, fresh_ctrl[d])
        lz = [r["lz_growth"] for r in runs]
        sign_ok = (t > 0) == (i28_rows[(d, k_f)]["welch_t"] > 0)
        strict = bool(abs(t) >= T_THRESHOLD and sign_ok)
        abs_ok = bool(abs(t) >= T_THRESHOLD)
        n_strict += strict
        n_abs += abs_ok
        cand_rows.append({
            "diff_coeff": d, "k_factor": k_f,
            "t_tier_a_iter28": i28_rows[(d, k_f)]["welch_t"],
            "t_fresh": t, "lz_mean_fresh": float(np.mean(lz)),
            "sigma_fresh_ddof1": float(np.std(lz, ddof=1)),
            "sign_match": bool(sign_ok), "strict": strict, "abs": abs_ok,
            "per_seed": [{k: r[k] for k in METRIC_KEYS} for r in runs],
        })
        print(f"  Kandidat D={d:g} k={k_f:g}: LZ {float(np.mean(lz)):+.4f} "
              f"(σ {float(np.std(lz, ddof=1)):.4f}) |t_fresh| = {abs(t):.2f} "
              f"(Vorzeichen {'' if sign_ok else 'NICHT '}match) → "
              f"{'REPLIZIERT (strict)' if strict else ('ABS-only' if abs_ok else 'NICHT repliziert')}",
              flush=True)

    expl_runs = run_cell(*EXPLORATORY)
    expl_t = welch_t(expl_runs, fresh_ctrl[EXPLORATORY[0]])
    expl_lz = [r["lz_growth"] for r in expl_runs]
    v4 = ("EXPL_REPLICATED" if abs(expl_t) >= T_THRESHOLD
          else "EXPL_NOT_REPLICATED")
    print(f"  Explorativ D={EXPLORATORY[0]:g} k={EXPLORATORY[1]:g}: "
          f"LZ {float(np.mean(expl_lz)):+.4f} |t| = {abs(expl_t):.2f} → {v4}",
          flush=True)

    if n_strict == len(CANDIDATES):
        v2 = "CAND_REPLICATED_ALL"
    elif n_strict >= 1:
        v2 = "CAND_PARTIAL"
    else:
        v2 = "CAND_NONE"
    if n_abs == len(CANDIDATES):
        v3 = "CAND_ABS_ALL"
    elif n_abs >= 1:
        v3 = "CAND_ABS_PARTIAL"
    else:
        v3 = "CAND_ABS_NONE"

    gates_pass = k1_all and k2
    final = (f"{v1} | {v2} | {v3} | {v4}" if gates_pass
             else "REGISTRATION_ERROR")
    print(f"\nV1 (H0 der t-Regel): {v1}")
    print(f"V2 (Kandidaten, STRICT): {v2}")
    print(f"V3 (Kandidaten, ABS): {v3}")
    print(f"V4 (explorativ): {v4}")
    print(f"\nVERDICT: {final}")

    result: dict[str, Any] = {
        "vector": "VECTOR_T_RULE_CANDIDATES",
        "seeds_fresh": list(SEEDS_FRESH),
        "anchors": list(ANCHORS),
        "gates": {"k1_artifact_consistency": k1_all,
                  "k2_determinism": k2},
        "h0_t_rule": h0,
        "control_consistency": consistency,
        "candidates": {"criterion": "strict = |t|>=2 AND sign match",
                       "n_strict": n_strict, "n_abs": n_abs,
                       "rows": cand_rows},
        "exploratory": {"cell": {"diff_coeff": EXPLORATORY[0],
                                 "k_factor": EXPLORATORY[1]},
                        "welch_t": expl_t, "verdict": v4},
        "verdicts": {"v1_h0_t_rule": v1, "v2_strict": v2, "v3_abs": v3,
                     "v4_exploratory": v4, "final": final},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2),
                                      encoding="utf-8")
    print(f"\n→ {HERE / 'result.json'}")


if __name__ == "__main__":
    main()
