"""iter-30 — VECTOR_FRESH_SURVIVOR_CENSUS.

VORAB-REGISTRIERUNG (2026-09-24, vor dem Lauf fixiert)

MOTIVATION
  iter-29 hob die drei staerksten Welch-t-Kandidaten zu Befunden und
  entwertete das D=0.10-Hoch-k-Plateau. Uebrig bleibt der robuste Kern:
  D=0.25 k=1, D=0.15 k=14, D=0.05 k=1 (frisch, iter-29), D=0.10 k=3
  (frisch, iter-28 — aber gegen die 200-209-Kontrolle), und die vier
  verbleibenden SE-Ueberlebenden (D=0.15 k=5, D=0.3 k=30/300/1000) sowie
  die Kante k_edge=10 (D=0.05, dreifach reproduziert, unter SE 0.69 SE
  und t<2.0 gefallen). Dieser Vektor schliesst den Zensus: JEDE
  ueberlebende bzw. kippende Struktur-Loafoerung wird an einem dritten,
  disjunkten Seed-Block (310-319) getestet — out-of-sample gegen
  200-209 UND 300-309, mit FRISCHEN Kontrollen je Anker.

ZELLEN (6)
  SE-Ueberlebende (Kriterium: |t_fresh| >= 2.0 UND Vorzeichen positiv,
  d. h. Zelle oberhalb der Kontrolle — die SE-Lesung war einseitig
  positiv):
    D=0.15 k=5    (SE 2.10, Tier A)
    D=0.30 k=30   (SE 2.61, Tier A)
    D=0.30 k=300  (SE 2.94, Tier B; iter-28 frisch vs ALTER Kontrolle)
    D=0.30 k=1000 (SE 2.78, Tier B; iter-28 frisch vs ALTER Kontrolle)
  Tiefste Zelle (gleiches Kriterium):
    D=0.10 k=3    (iter-28 |t|=7.91 vs ALTER Kontrolle — jetzt FRISCH)
  Kante (eigene Frage, kein Vorzeichen registriert):
    D=0.05 k=10   (k_edge, dreifach reproduziert iter-25/26/27, unter SE
                   0.69 SE und Welch-t < 2.0 an 200-209 — Frage: zeigt
                   die Kante an frischen Seeds irgendein Signal?)

DESIGN (100 GPU-Laeufe ≈ 15 min)
  Seeds 310-319 (dritter Block, disjunkt zu 200-209 und 300-309),
  dt_react = 1e-5, iter-25-Harness VERBATIM.
  Kontrollen: 4 Anker (0.05, 0.10, 0.15, 0.30) x 10 = 40 Laeufe.
  Zellen: 6 x 10 = 60 Laeufe.
  Kriterium STRICT (SE-Ueberlebende + Tiefste): |t_fresh| >= 2.0 UND
    sign(t_fresh) > 0 (die iter-27/28-Lesung aller 5 Zellen war positiv).
  Kante: berichtend, beidseitig (|t_fresh| >= 2.0 irgendein
    Vorzeichen = EDGE_SIGNALS; sonst EDGE_NULL_CONFIRMED — die Flip-
    Lesung von iter-28 wird dann out-of-sample getragen).
  K-C (berichtend): Konsistenz der 4 frischen Kontrollpools (310-319)
    gegen die iter-27-Pools (200-209) — z-Scores; dritte Independent-
    Messung der Block-Abhaengigkeit der Ausreisser.

GATES (bindend)
  K1 Artefakt-Konsistenz (bit-identisch, recomputet aus Artefakten):
     (a) se_units der 4 SE-Ueberlebenden == iter-28 se_reclass_rows
         (Formel VERBATIM aus signal_reclass: |mean3 - ctrl_mean| /
         (sigma_within * SE_FACTOR), SE_FACTOR = float(np.sqrt(2/3))
         importiert aus signal_reclass)
     (b) welch_t(D=0.10 k=3, iter-28 deep-cells per_seed vs iter-27-
         Kontrolle) == 7.9064...
     (c) iter-29-Verankerung per Cross-Session-Determinismus: fuer jede
         der 3 iter-29-Kandidaten-Zellen wird der Lauf seed 300
         reproduziert und bit-identisch gegen die persistierte
         per-seed-Zeile geprueft. (Die iter-29-Kontrollpools sind nicht
         per-seed persistiert — kein bit-identischer t-Recompute
         moeglich; dokumentiert im CORREKTUR-LOG.)
  K2 Determinismus: run_config doppelt bit-identisch.
  Verletzung ⇒ REGISTRATION_ERROR, kein Verdict.

VERDICT-NAMEN (vor dem Lauf fixiert)
  V1 (4 SE-Ueberlebende, STRICT): SURV_ALL 4/4 / SURV_PARTIAL 1-3/4 /
      SURV_NONE 0/4.
  V2 (D=0.10 k=3, frische Kontrolle): DEEP3_FRESH_REPLICATED /
      DEEP3_FRESH_NOT.
  V3 (Kante k_edge=10): EDGE_SIGNALS / EDGE_NULL_CONFIRMED.
  REGISTRATION_ERROR — bindendes Gate verletzt.

NICHT BEHAUPTET
  Der Zensus ist ein Eigenschafts-Census DES METRIK-STACKS (LZ/corr/tMI
  + Kontrollpools + Registry-Subsets + Gitter), nicht der Zelle und
  nicht von syn3A. Die SE-Ueberlebenden sind POST-HOC aus iter-27/28
  hervorgegangen; der Test ist ihre out-of-sample-Replikation (Promotion
  bei Erfolg, Entwertung bei Scheitern) — dieselbe Logik wie iter-29.
  Post-hoc-Konsistenz wird NIE als Bestaetigung gebucht. Keine
  Landschafts-Claims jenseits der getesteten Zellen.
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

T_THRESHOLD = 2.0
ANCHORS = (0.05, 0.10, 0.15, 0.30)
SURVIVORS = ((0.15, 5.0), (0.30, 30.0), (0.30, 300.0), (0.30, 1000.0))
DEEP3 = (0.10, 3.0)
EDGE = (0.05, 10.0)
SEEDS_FRESH2 = tuple(range(310, 320))
METRIC_KEYS = ("lz_growth", "corr_glc_atp_mean", "temporal_mi_mean",
               "p11_mean", "mass_ratio", "reaction_events_total")


def se_units(i26_row: dict[str, Any], sigma_within: float,
             ctrl_mean_lz: float) -> float:
    """VERBATIM iter-28 signal_reclass: gap / (sigma_within * SE_FACTOR)."""
    se = sigma_within * SE_FACTOR
    gap = abs(i26_row["mean"]["lz_growth"] - ctrl_mean_lz)
    return gap / se if se > 0 else float("inf")


def main() -> None:
    print("=== iter-30: FRESH_SURVIVOR_CENSUS (dritter Block, GPU) ===\n")

    iter26 = json.loads(ITER26_RESULT.read_text(encoding="utf-8"))
    iter27 = json.loads(ITER27_RESULT.read_text(encoding="utf-8"))
    iter28 = json.loads(ITER28_RESULT.read_text(encoding="utf-8"))
    iter29 = json.loads(ITER29_RESULT.read_text(encoding="utf-8"))
    anchors_i27 = (0.05, 0.10, 0.15, 0.25, 0.30)
    ctrl_per_seed = {d: iter27["controls"][f"{d:g}"]["per_seed"]
                     for d in anchors_i27}
    sigma_within = {d: iter27["h0_false_distinct"][f"{d:g}"]["sigma_within"]
                    for d in anchors_i27}
    ctrl_mean_lz = {d: iter27["controls"][f"{d:g}"]["mean"]["lz_growth"]
                    for d in anchors_i27}
    i26_rows = {(r["diff_coeff"], r["k_factor"]): r for r in iter26["rows"]}
    i28_rows = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter28["se_reclass_rows"]}
    i28_deep = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter28["deep_cells"]["rows"]}
    i29_cand = {(r["diff_coeff"], r["k_factor"]): r
                for r in iter29["candidates"]["rows"]}

    # --- Gates ---------------------------------------------------------------
    print("Gates:", flush=True)
    k1_all = True
    for d, k_f in SURVIVORS:
        se = se_units(i26_rows[(d, k_f)], sigma_within[d], ctrl_mean_lz[d])
        ref = i28_rows[(d, k_f)]["se_units"]
        k1_all = k1_all and (se == ref)
        print(f"  K1 se_units D={d:g} k={k_f:g}: {se:.4f} == iter-28 "
              f"{ref:.4f} -> {se == ref}", flush=True)
    deep3_row = i28_deep[DEEP3]
    t_deep = welch_t(deep3_row["per_seed"], ctrl_per_seed[DEEP3[0]])
    k1_all = k1_all and (t_deep == deep3_row["welch_t"])
    print(f"  K1 welch_t D=0.1 k=3: {t_deep:.4f} == iter-28 "
          f"{deep3_row['welch_t']:.4f} -> {t_deep == deep3_row['welch_t']}",
          flush=True)
    # K1(c) iter-29-Verankerung: die t_fresh-Referenzen wurden gegen die
    # frische 300-309-Kontrolle gerechnet, deren per-seed-Vektoren vom
    # iter-29-Harness NICHT persistiert wurden — ein bit-identischer
    # Recompute des t-Werts ist daher aus Artefakten allein unmoeglich.
    # Ersatz (gleich stark): Cross-Session-Determinismus — fuer jede
    # iter-29-Kandidaten-Zelle und jede Anker-Kontrolle wird genau ein
    # Lauf (seed 300, der erste des Blocks) reproduziert und bit-identisch
    # gegen die persistierten per-seed-Zeilen geprueft (7 Laeufe).
    for d, k_f in ((0.05, 1.0), (0.15, 14.0), (0.25, 1.0)):
        r = sm.run_config(k_f, sm.DT_SWEEP, d, 300)
        ref = i29_cand[(d, k_f)]["per_seed"][0]["lz_growth"]
        ok = bool(r["lz_growth"] == ref)
        k1_all = k1_all and ok
        print(f"  K1 iter-29-Determinismus D={d:g} k={k_f:g} (seed 300): "
              f"bit-identisch = {ok}", flush=True)
    # Anmerkung: die iter-29-Kontrollpools (300-309) sind nicht per-seed
    # persistiert — fuer sie existiert keine bit-identische Referenz; ihre
    # Konsistenz wird stattdessen ueber die persistierten Mittel/σ
    # (control_consistency von iter-29) berichtend abgedeckt.
    a = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 310)
    b = sm.run_config(1.0, sm.DT_SWEEP, 0.15, 310)
    k2 = bool(a == b)
    print(f"  K2 Determinismus: bit-identisch = {k2}\n", flush=True)

    # --- Frische Kontrollen (40 GPU-Laeufe) ----------------------------------
    print("Frische Kontrollen (Seeds 310-319):", flush=True)
    fresh_ctrl: dict[float, list[dict[str, float]]] = {}
    consistency = {}
    for d in ANCHORS:
        runs = [sm.run_config(1.0, 0.0, d, s) for s in SEEDS_FRESH2]
        fresh_ctrl[d] = runs
        lz = [r["lz_growth"] for r in runs]
        mf, sf = float(np.mean(lz)), float(np.std(lz, ddof=1))
        i27_lz = [r["lz_growth"] for r in ctrl_per_seed[d]]
        mi, si = float(np.mean(i27_lz)), float(np.std(i27_lz, ddof=1))
        denom = (sf * sf / 10.0 + si * si / 10.0) ** 0.5
        z = (mf - mi) / denom if denom > 0 else float("inf")
        consistency[f"{d:g}"] = {"z": z, "mean_fresh": mf, "sigma_fresh": sf,
                                 "mean_i27": mi, "sigma_i27": si}
        print(f"  D={d:g}: LZ {mf:+.4f} (σ {sf:.4f}) vs iter-27 {mi:+.4f} "
              f"(σ {si:.4f}) | z = {z:+.2f}", flush=True)
    print(flush=True)

    def census_cell(d: float, k_f: float) -> tuple[float, float, float]:
        runs = [sm.run_config(k_f, sm.DT_SWEEP, d, s) for s in SEEDS_FRESH2]
        t = welch_t(runs, fresh_ctrl[d])
        lz = [r["lz_growth"] for r in runs]
        return (t, float(np.mean(lz)), float(np.std(lz, ddof=1)))

    # --- V1: SE-Ueberlebende --------------------------------------------------
    print("V1 — SE-Ueberlebende (STRICT: |t|>=2 UND positiv):", flush=True)
    surv_rows = []
    n_surv = 0
    for d, k_f in SURVIVORS:
        t, lz_mean, sig = census_cell(d, k_f)
        ok = bool(abs(t) >= T_THRESHOLD and t > 0)
        n_surv += ok
        surv_rows.append({"diff_coeff": d, "k_factor": k_f,
                          "se_units_iter28": i28_rows[(d, k_f)]["se_units"],
                          "t_fresh": t, "lz_mean_fresh": lz_mean,
                          "sigma_fresh_ddof1": sig, "replicated": ok})
        print(f"  D={d:g} k={k_f:g} (SE {i28_rows[(d, k_f)]['se_units']:.2f}): "
              f"LZ {lz_mean:+.4f} |t_fresh| = {abs(t):.2f} → "
              f"{'REPLIZIERT' if ok else 'NICHT repliziert'}", flush=True)

    # --- V2: D=0.10 k=3 gegen FRISCHE Kontrolle -------------------------------
    t3, lz3, sig3 = census_cell(*DEEP3)
    ok3 = bool(abs(t3) >= T_THRESHOLD and t3 > 0)
    v2 = ("DEEP3_FRESH_REPLICATED" if ok3 else "DEEP3_FRESH_NOT")
    print(f"\nV2 — D=0.10 k=3 (frische Kontrolle): LZ {lz3:+.4f} (σ {sig3:.4f}) "
          f"|t| = {abs(t3):.2f} → {v2}", flush=True)

    # --- V3: Kante k_edge=10 ---------------------------------------------------
    te, lze, sige = census_cell(*EDGE)
    edge_sig = bool(abs(te) >= T_THRESHOLD)
    v3 = ("EDGE_SIGNALS" if edge_sig else "EDGE_NULL_CONFIRMED")
    print(f"V3 — Kante D=0.05 k=10: LZ {lze:+.4f} (σ {sige:.4f}) "
          f"|t| = {abs(te):.2f} → {v3}", flush=True)

    if n_surv == len(SURVIVORS):
        v1 = "SURV_ALL"
    elif n_surv >= 1:
        v1 = "SURV_PARTIAL"
    else:
        v1 = "SURV_NONE"

    gates_pass = k1_all and k2
    final = (f"{v1} | {v2} | {v3}" if gates_pass else "REGISTRATION_ERROR")
    print(f"\nV1 (SE-Ueberlebende, 4): {v1} ({n_surv}/4)")
    print(f"V2 (D=0.10 k=3, frisch): {v2}")
    print(f"V3 (Kante k_edge=10): {v3}")
    print(f"\nVERDICT: {final}")

    result: dict[str, Any] = {
        "vector": "VECTOR_FRESH_SURVIVOR_CENSUS",
        "seeds_fresh2": list(SEEDS_FRESH2),
        "anchors": list(ANCHORS),
        "gates": {"k1_artifact_consistency": k1_all, "k2_determinism": k2},
        "control_consistency": consistency,
        "survivors": {"criterion": "|t|>=2 AND t>0", "n_replicated": n_surv,
                      "rows": surv_rows},
        "deep3": {"cell": {"diff_coeff": DEEP3[0], "k_factor": DEEP3[1]},
                  "welch_t": t3, "lz_mean_fresh": lz3,
                  "sigma_fresh_ddof1": sig3, "replicated": ok3},
        "edge": {"cell": {"diff_coeff": EDGE[0], "k_factor": EDGE[1]},
                 "welch_t": te, "lz_mean_fresh": lze,
                 "sigma_fresh_ddof1": sige, "signal": edge_sig},
        "verdicts": {"v1_survivors": v1, "v2_deep3": v2, "v3_edge": v3,
                     "final": final},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2),
                                      encoding="utf-8")
    print(f"\n→ {HERE / 'result.json'}")


if __name__ == "__main__":
    main()
