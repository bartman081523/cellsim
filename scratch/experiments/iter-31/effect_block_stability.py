"""iter-31 — VECTOR_EFFECT_BLOCK_STABILITY.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

MOTIVATION
  iter-30 Hypothese 3: Effektstaerken sind NICHT seed-block-stabil —
  dieselbe Zelle (Kante k_edge=10) liest 0.69 SE an Block 200-209 gegen
  4.21 SE an Block 310-319 (Faktor ~6 im Zell-Abstand). Alle 8 Kern-Zellen
  tragen bisher Punkt-Schaetzungen aus 1-2 Bloecken. Dieser Vektor misst
  die Block-Stabilitaet systematisch: je Zelle 4 Bloecke (2 alte + 2
  neue), Gap in LZ-Einheiten als primaere Metrik, plus Varianz-Zerlegung
  in within-Block-Sampling-Rauschen vs echte Block-Varianz.

ZELLEN (9)  [robuster Kern iter-29/30 + Kante als motivierter Fall]
  SE-Ueberlebende: D=0.10 k=3, D=0.15 k=5, D=0.30 k=30, D=0.30 k=300,
                   D=0.30 k=1000
  iter-29-Befunde: D=0.05 k=1, D=0.15 k=14, D=0.25 k=1
  Kante:           D=0.05 k=10  (k_edge — der paradigmatische
                   Block-Fluktuierer aus iter-30)

BLOCK-COVERAGE (je Zelle 4 Bloecke, ohne Nachlauf alter Zellen)
  iter-29-Kandidaten (D=0.05 k=1, D=0.15 k=14, D=0.25 k=1):
      Bloecke 1 (200-209, iter-26 n=3 vs iter-27-Ktrl), 2 (300-309,
      iter-29), 4 (320-329), 5 (330-339)
  uebrige 6 Zellen:
      Bloecke 1, 3 (310-319, iter-30), 4, 5
  Die Asymmetrie (welche alten Bloecke je Zelle gemessen sind) ist
  Design-Eigenschaft: innerhalb jeder Zelle ist sigma_effect ueber ihre
  4 Bloecke wohldefiniert; zelluebergreifende Block-Vergleiche tragen
  den Vorbehalt.

DESIGN (280 GPU-Laeufe ≈ 40 min)
  Neu: 2 Bloecke (320-329, 330-339) × [5 Anker × 10 Kontrollen + 9
  Zellen × 10] = 140 + 140. dt_react = DT_SWEEP (Zellen) / 0.0
  (Kontrollen), k_f = 1.0 (Kontrollen), iter-25-Harness VERBATIM.
  Per-seed-Vektoren VOLL persistiert (Zellen UND Kontrollen) — erstmals
  fuer alle Bloecke eines Vektors der Linie.

METRIK
  Primaer: signiertes Gap g_b = mean_cell,b − mean_ctrl,b (LZ-Einheiten)
  je Block. Deskriptiv je Zelle ueber alle 4 Bloecke: mean_g, sigma_g
  (ddof=1), CV = sigma_g/|mean_g|, Intervall [min, max]. Sekundaer:
  welch_t je Block, wo verfuegbar.

DEKOMPOSITION (primär, je Zelle ueber "informierte" Bloecke)
  Informierte Bloecke = Bloecke mit within-Block-Sigmas BEIDER Seiten:
    deep3 / k=300 / k=1000: {1, 3, 4, 5} (Block 1 per-seed in iter-28
      deep_cells, Block 3 via iter-30 sigma_fresh-Zellen + cc
      sigma_fresh-Ktrl);
    D=0.15 k=5, D=0.30 k=30, Kante: {3, 4, 5} (Block 1 der iter-26-n=3-
      Zellen ist NICHT informiert — iter-26 persistiert keine per-seed-
      Sigmas; er geht nur in die Deskriptik ein);
    iter-29-Kandidaten: {2, 4, 5} (Block 2 via iter-29 per_seed-Zellen +
      cc sigma_fresh-Ktrl).
  Var_obs  = Var(g) ueber informierte Bloecke (ddof=1)
  Var_samp = mean_b( s²_cell,b / n_b + s²_ctrl,b / n_b )
  f_block  = max(0, Var_obs − Var_samp) / Var_obs
  Zelle BLOCK_REAL falls f_block ≥ 0.5.

GATES (bindend)
  K1 (a) se_units der 5 SE-Ueberlebenden bit-identisch zu iter-28
         (VERBATIM-Formel via signal_reclass-Import)
      (b) welch_t D=0.10 k=3 (iter-28-deep-per_seed vs iter-27-Ktrl) ==
         7.9064... bit-identisch
      (c) iter-29-Verankerung: seed 300 je Kandidaten-Zelle reproduziert,
         bit-identisch vs persistierte per-seed-Zeile
      (d) iter-28-Verankerung (NEU): seed 200, D=0.10 k=3 reproduziert,
         bit-identisch vs deep-per_seed[0]
  K2 Determinismus: run_config doppelt bit-identisch.
  Verletzung ⇒ REGISTRATION_ERROR, kein Verdict.

VERDICT-NAMEN (vor dem Lauf fixiert)
  V1 (Dekomposition, 9 Zellen): BLOCK_VAR_DOMINANT ≥6/9 BLOCK_REAL /
      MIXED 3-5 / SAMPLING_DOMINANT ≤2
  V2 (Deskriptiv, CV ≤ 0.5 = STABLE_DEPTH; |mean_g| < 0.005 gilt als
      FLUCTUATING): DEPTHS_STABLE_MAJORITY ≥6/9 / DEPTHS_MIXED 3-5 /
      DEPTHS_UNSTABLE_MAJORITY ≤2
  V3 (Vorzeichen ueber alle 4 Bloecke, berichtend): je Zelle
      ALL_SAME_SIGN / SIGN_FLIP; Aggregat n_signstable/9.
  REGISTRATION_ERROR — bindendes Gate verletzt.

NICHT BEHAUPTET
  Alle Gaps sind Eigenschaften DES METRIK-STACKS (LZ + Kontrollpools +
  Registry-Subsets + Gitter), nicht der Zelle und nicht von syn3A.
  f_block ist eine Schaetzung aus 3-4 Block-Werten mit verrauschten
  within-Block-Sigmas — die Zerlegung quantifiziert die Groessenordnung,
  sie ist keine praezise Varianz-Komponenten-Schaetzung. Keine
  Landschafts-Claims jenseits der 9 Zellen. Post-hoc-Befunde (z. B.
  Vorzeichen-Wechsel an einem neuen Block) werden als Befund gebucht,
  nicht geglaettet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-25"))
import saturation_margin as sm  # noqa: E402 (Harness VERBATIM)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-28"))
from signal_reclass import SE_FACTOR, welch_t  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = Path(__file__).resolve().parents[1]
ITER26_RESULT = EXP / "iter-26" / "result.json"
ITER27_RESULT = EXP / "iter-27" / "result.json"
ITER28_RESULT = EXP / "iter-28" / "result.json"
ITER29_RESULT = EXP / "iter-29" / "result.json"
ITER30_RESULT = EXP / "iter-30" / "result.json"

CV_THRESHOLD = 0.5
F_BLOCK_THRESHOLD = 0.5
MIN_MEAN_G = 0.005
ANCHORS = (0.05, 0.10, 0.15, 0.25, 0.30)
DEEP3 = (0.10, 3.0)
SURVIVORS = (DEEP3, (0.15, 5.0), (0.30, 30.0), (0.30, 300.0), (0.30, 1000.0))
CANDIDATES = ((0.05, 1.0), (0.15, 14.0), (0.25, 1.0))
EDGE = (0.05, 10.0)
CELLS = SURVIVORS + CANDIDATES + (EDGE,)
SEEDS_B4 = tuple(range(320, 330))
SEEDS_B5 = tuple(range(330, 340))
METRIC_KEYS = ("lz_growth", "corr_glc_atp_mean", "temporal_mi_mean",
               "p11_mean", "mass_ratio", "reaction_events_total")


def se_units(i26_row: dict[str, Any], sigma_within: float,
             ctrl_mean_lz: float) -> float:
    """VERBATIM iter-28 signal_reclass: gap / (sigma_within * SE_FACTOR)."""
    se = sigma_within * SE_FACTOR
    gap = abs(i26_row["mean"]["lz_growth"] - ctrl_mean_lz)
    return gap / se if se > 0 else float("inf")


def mean_sigma(vals: list[float]) -> tuple[float, float]:
    return float(np.mean(vals)), float(np.std(vals, ddof=1))


def main() -> None:
    print("=== iter-31: EFFECT_BLOCK_STABILITY (2 neue Bloecke, GPU) ===\n",
          flush=True)

    iter26 = json.loads(ITER26_RESULT.read_text(encoding="utf-8"))
    i26_rows = {(r["diff_coeff"], r["k_factor"]): r for r in iter26["rows"]}
    iter27 = json.loads(ITER27_RESULT.read_text(encoding="utf-8"))
    iter28 = json.loads(ITER28_RESULT.read_text(encoding="utf-8"))
    iter29 = json.loads(ITER29_RESULT.read_text(encoding="utf-8"))
    iter30 = json.loads(ITER30_RESULT.read_text(encoding="utf-8"))

    anchors_i27 = (0.05, 0.1, 0.15, 0.25, 0.3)
    ctrl_i27_per_seed = {d: iter27["controls"][f"{d:g}"]["per_seed"]
                         for d in anchors_i27}
    ctrl_i27_mean = {d: iter27["controls"][f"{d:g}"]["mean"]["lz_growth"]
                     for d in anchors_i27}
    sigma_within = {d: iter27["h0_false_distinct"][f"{d:g}"]["sigma_within"]
                    for d in anchors_i27}
    i28_reclass = {(r["diff_coeff"], r["k_factor"]): r
                   for r in iter28["se_reclass_rows"]}
    i28_deep = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter28["deep_cells"]["rows"]}
    i29_cand = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter29["candidates"]["rows"]}
    i29_cc = {float(k): v for k, v in iter29["control_consistency"].items()}
    i30_cc = {float(k): v for k, v in iter30["control_consistency"].items()}
    i30_rows = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter30["survivors"]["rows"]}
    i30_rows[(iter30["deep3"]["cell"]["diff_coeff"],
              iter30["deep3"]["cell"]["k_factor"])] = iter30["deep3"]
    i30_rows[(iter30["edge"]["cell"]["diff_coeff"],
              iter30["edge"]["cell"]["k_factor"])] = iter30["edge"]

    # --- Gates ---------------------------------------------------------------
    print("Gates:", flush=True)
    k1_all = True
    for d, k_f in SURVIVORS:
        se = se_units(i26_rows[(d, k_f)], sigma_within[d], ctrl_i27_mean[d])
        ref = i28_reclass[(d, k_f)]["se_units"]
        ok = bool(se == ref)
        k1_all = k1_all and ok
        print(f"  K1a se_units D={d:g} k={k_f:g}: {se:.4f} == iter-28 "
              f"{ref:.4f} -> {ok}", flush=True)
    deep3_ref = i28_deep[DEEP3]
    t_deep = welch_t(deep3_ref["per_seed"], ctrl_i27_per_seed[DEEP3[0]])
    ok = bool(t_deep == deep3_ref["welch_t"])
    k1_all = k1_all and ok
    print(f"  K1b welch_t D=0.1 k=3: {t_deep:.4f} == iter-28 "
          f"{deep3_ref['welch_t']:.4f} -> {ok}", flush=True)
    for d, k_f in CANDIDATES:
        r = sm.run_config(k_f, sm.DT_SWEEP, d, 300)
        ref = i29_cand[(d, k_f)]["per_seed"][0]["lz_growth"]
        ok = bool(r["lz_growth"] == ref)
        k1_all = k1_all and ok
        print(f"  K1c iter-29-Determinismus D={d:g} k={k_f:g} (seed 300): "
              f"bit-identisch = {ok}", flush=True)
    r = sm.run_config(DEEP3[1], sm.DT_SWEEP, DEEP3[0], 200)
    ok = bool(r["lz_growth"] == deep3_ref["per_seed"][0]["lz_growth"])
    k1_all = k1_all and ok
    print(f"  K1d iter-28-Determinismus D=0.1 k=3 (seed 200): "
          f"bit-identisch = {ok}", flush=True)
    a = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 320)
    b = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 320)
    k2 = bool(a == b)
    print(f"  K2 Determinismus: bit-identisch = {k2}\n", flush=True)

    # --- 2 neue Bloecke (200 GPU-Laeufe) --------------------------------------
    seeds_by_block: dict[str, tuple[int, ...]] = {"4": SEEDS_B4, "5": SEEDS_B5}
    new_gaps: dict[str, list[dict[str, Any]]] = {k: [] for k in
                                                 (f"{d:g}|{kf:g}"
                                                  for d, kf in CELLS)}
    new_meta: dict[str, dict[str, Any]] = {"controls": {}, "cells": {}}
    for bname, seeds in seeds_by_block.items():
        print(f"--- Block {bname} (Seeds {seeds[0]}-{seeds[-1]}) ---",
              flush=True)
        ctrl_block: dict[str, dict[str, Any]] = {}
        for d in ANCHORS:
            runs = [sm.run_config(1.0, 0.0, d, s) for s in seeds]
            lz = [r["lz_growth"] for r in runs]
            m, s = mean_sigma(lz)
            ctrl_block[f"{d:g}"] = {"mean": m, "sigma": s, "per_seed": runs}
            print(f"  Ktrl D={d:g}: LZ {m:+.4f} (σ {s:.4f})", flush=True)
        new_meta["controls"][bname] = ctrl_block
        cells_block: dict[str, dict[str, Any]] = {}
        for d, k_f in CELLS:
            runs = [sm.run_config(k_f, sm.DT_SWEEP, d, s) for s in seeds]
            lz = [r["lz_growth"] for r in runs]
            m, s = mean_sigma(lz)
            t = welch_t(runs, ctrl_block[f"{d:g}"]["per_seed"])
            gap = m - ctrl_block[f"{d:g}"]["mean"]
            cells_block[f"{d:g}|{k_f:g}"] = {
                "mean": m, "sigma": s, "per_seed": runs,
                "t_fresh": t, "gap": gap}
            print(f"  Zelle D={d:g} k={k_f:g}: LZ {m:+.4f} (σ {s:.4f}) "
                  f"gap {gap:+.4f} |t| = {abs(t):.2f}", flush=True)
        new_meta["cells"][bname] = cells_block
        for d, k_f in CELLS:
            e = cells_block[f"{d:g}|{k_f:g}"]
            new_gaps[f"{d:g}|{k_f:g}"].append({
                "block": int(bname), "n_cell": 10,
                "mean_cell": e["mean"], "sigma_cell": e["sigma"],
                "mean_ctrl": ctrl_block[f"{d:g}"]["mean"],
                "sigma_ctrl": ctrl_block[f"{d:g}"]["sigma"],
                "s2_cell": e["sigma"] ** 2, "s2_ctrl": ctrl_block[f"{d:g}"]["sigma"] ** 2,
                "gap": e["gap"], "t": e["t_fresh"],
                "source": "iter-31 (per-seed persistiert)", "informed": True})
    print(flush=True)

    # --- Alte Bloecke aus Artefakten -------------------------------------------
    old_blocks: dict[str, list[dict[str, Any]]] = {}
    for d, k_f in CELLS:
        entries: list[dict[str, Any]] = []
        rc = i28_reclass[(d, k_f)]
        s_ctrl1 = float(np.std([r["lz_growth"]
                                for r in ctrl_i27_per_seed[d]], ddof=1))
        if (d, k_f) in i28_deep:
            dr = i28_deep[(d, k_f)]
            entries.append({
                "block": 1, "seeds": "200-209", "n_cell": 10,
                "mean_cell": dr["lz_mean_10"], "sigma_cell": dr["sigma_10_ddof1"],
                "mean_ctrl": ctrl_i27_mean[d], "sigma_ctrl": s_ctrl1,
                "s2_cell": dr["sigma_10_ddof1"] ** 2, "s2_ctrl": s_ctrl1 ** 2,
                "gap": dr["lz_mean_10"] - ctrl_i27_mean[d],
                "t": dr["welch_t"],
                "source": "iter-28 deep_cells vs iter-27-Kontrolle (per-seed)",
                "informed": True})
        else:
            entries.append({
                "block": 1, "seeds": "200-209", "n_cell": 3,
                "mean_cell": rc["lz_mean_3"], "sigma_cell": None,
                "mean_ctrl": ctrl_i27_mean[d], "sigma_ctrl": s_ctrl1,
                "s2_cell": None, "s2_ctrl": s_ctrl1 ** 2,
                "gap": rc["lz_mean_3"] - ctrl_i27_mean[d],
                "t": rc.get("welch_t"),
                "source": "iter-26 n=3 (iter-28 se_reclass) vs iter-27-Ktrl "
                          "(kein per-seed-Sigma der Zelle)",
                "informed": False})
        if (d, k_f) in i29_cand:
            c = i29_cand[(d, k_f)]
            _, s_cell2 = mean_sigma([r["lz_growth"] for r in c["per_seed"]])
            entries.append({
                "block": 2, "seeds": "300-309", "n_cell": 10,
                "mean_cell": c["lz_mean_fresh"], "sigma_cell": s_cell2,
                "mean_ctrl": i29_cc[d]["mean_fresh"],
                "sigma_ctrl": i29_cc[d]["sigma_fresh"],
                "s2_cell": s_cell2 ** 2, "s2_ctrl": i29_cc[d]["sigma_fresh"] ** 2,
                "gap": c["lz_mean_fresh"] - i29_cc[d]["mean_fresh"],
                "t": c["t_fresh"],
                "source": "iter-29 Kandidaten (per-seed) vs frische Ktrl "
                          "(Mittel/σ persistiert)",
                "informed": True})
        if (d, k_f) in i30_rows:
            c = i30_rows[(d, k_f)]
            entries.append({
                "block": 3, "seeds": "310-319", "n_cell": 10,
                "mean_cell": c["lz_mean_fresh"], "sigma_cell": c["sigma_fresh_ddof1"],
                "mean_ctrl": i30_cc[d]["mean_fresh"],
                "sigma_ctrl": i30_cc[d]["sigma_fresh"],
                "s2_cell": c["sigma_fresh_ddof1"] ** 2,
                "s2_ctrl": i30_cc[d]["sigma_fresh"] ** 2,
                "gap": c["lz_mean_fresh"] - i30_cc[d]["mean_fresh"],
                # deep3/edge tragen "welch_t", survivors-Zeilen "t_fresh"
                "t": c["t_fresh"] if "t_fresh" in c else c["welch_t"],
                "source": "iter-30 (Mittel/σ persistiert, keine per-seed)",
                "informed": True})
        old_blocks[f"{d:g}|{k_f:g}"] = entries

    # --- Per-Zelle: Deskriptik + Dekomposition ---------------------------------
    per_cell: dict[str, Any] = {}
    n_block_real = 0
    n_cv_stable = 0
    n_sign_stable = 0
    for d, k_f in CELLS:
        key = f"{d:g}|{k_f:g}"
        all_entries = sorted(old_blocks[key] + new_gaps[key],
                             key=lambda e: e["block"])
        gaps = [e["gap"] for e in all_entries]
        informed = [e for e in all_entries if e.get("informed")]
        mg, sg = mean_sigma(gaps)
        cv = abs(sg / mg) if abs(mg) >= MIN_MEAN_G else float("inf")
        var_obs = (float(np.var([e["gap"] for e in informed], ddof=1))
                   if len(informed) >= 2 else 0.0)
        var_samp = (float(np.mean([e["s2_cell"] / e["n_cell"]
                                   + e["s2_ctrl"] / e["n_cell"]
                                   for e in informed]))
                    if informed else 0.0)
        f_block = (max(0.0, var_obs - var_samp) / var_obs
                   if var_obs > 0 else 0.0)
        block_real = bool(f_block >= F_BLOCK_THRESHOLD)
        sign_stable = bool(all(g > 0 for g in gaps)
                           or all(g < 0 for g in gaps))
        n_block_real += block_real
        n_cv_stable += cv <= CV_THRESHOLD
        n_sign_stable += sign_stable
        per_cell[key] = {
            "blocks": [e["block"] for e in all_entries],
            "n_cell_by_block": [e["n_cell"] for e in all_entries],
            "gaps": gaps, "mean_g": mg, "sigma_g": sg,
            "cv": cv if cv != float("inf") else None,
            "interval": [min(gaps), max(gaps)],
            "informed_blocks": [e["block"] for e in informed],
            "var_obs": var_obs, "var_samp": var_samp, "f_block": f_block,
            "block_real": block_real, "sign_stable": sign_stable}
        print(f"  {key}: mean_g {mg:+.4f} σ_g {sg:.4f} "
              f"CV {cv if cv != float('inf') else 'undef'} | "
              f"f_block {f_block:.2f} → "
              f"{'BLOCK_REAL' if block_real else 'sampling-dominiert'} | "
              f"{'Vorzeichen-stabil' if sign_stable else 'VORZEICHEN-FLIP'}",
              flush=True)

    if n_block_real >= 6:
        v1 = "BLOCK_VAR_DOMINANT"
    elif n_block_real >= 3:
        v1 = "MIXED"
    else:
        v1 = "SAMPLING_DOMINANT"
    if n_cv_stable >= 6:
        v2 = "DEPTHS_STABLE_MAJORITY"
    elif n_cv_stable >= 3:
        v2 = "DEPTHS_MIXED"
    else:
        v2 = "DEPTHS_UNSTABLE_MAJORITY"
    v3 = f"{n_sign_stable}/9 VORZEICHEN_STABIL"

    gates_pass = k1_all and k2
    final = (f"{v1} | {v2} | {v3}" if gates_pass else "REGISTRATION_ERROR")
    print(f"\nV1 (Dekomposition): {v1} ({n_block_real}/9 BLOCK_REAL)")
    print(f"V2 (Deskriptiv, CV<=0.5): {v2} ({n_cv_stable}/9 STABLE_DEPTH)")
    print(f"V3 (Vorzeichen ueber 4 Bloecke): {v3}")
    print(f"\nVERDICT: {final}")

    result: dict[str, Any] = {
        "vector": "VECTOR_EFFECT_BLOCK_STABILITY",
        "seeds_new": {"block4": list(SEEDS_B4), "block5": list(SEEDS_B5)},
        "anchors": list(ANCHORS),
        "gates": {"k1_artifact_consistency": k1_all, "k2_determinism": k2},
        "new_blocks": new_meta,
        "old_blocks": old_blocks,
        "per_cell": per_cell,
        "verdicts": {"v1_block_var": v1, "v2_depths": v2, "v3_signs": v3,
                     "final": final},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2),
                                      encoding="utf-8")
    print(f"\n→ {HERE / 'result.json'}")


if __name__ == "__main__":
    main()
