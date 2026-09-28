"""Treiber fuer die tci_v3-Batterie (g0 | pilot | control | main | analyze).

Registrierung: Docstring v3_model.py (Kriterien/Gates/Seeds fixiert VOR
dem ersten vollstaendigen Hauptlauf). Pilot = PILOT_*-Labels, keine
Verdict-Promotion; die SELEKTIONS-REGEL ist im Docstring fixiert (aus
dem Pilot-Raster die Ecke mit median n_cores >= 5, Dauer >= 3,
quant >= 0.9 in >= 80 % Kern-Frames; bei mehreren: hoechste Dauer,
dann kleinste sigma_n). Hauptlauf: Seeds 1500-1529 (+ Switch 1500-1509),
disjunkt zu Korpus 1000-1009/2000-2009, cellsim 200-339 und v2
1200-1229/1400-1403. G0 vor dem Hauptlauf; G1 im ersten Slice.
alpha=0-Kontrolle (TH3-Falsifikator, R1) als eigener Stage.
Unterbrochene Laeufe werden nie gebucht (analyze prueft die Datei-Anzahl
gegen die Registrierung).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import v3_model as m

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "per_seed"


def stage_g0():
    time.time()
    gate = m.oscillator_gate()
    (HERE / "g0.json").write_text(json.dumps(gate, indent=2))
    print(f"G0 OSCILLATOR: {'PASS' if gate['pass'] else 'FAIL'} {gate}")


def _sel_key(rows):
    """Registrierte Selektions-Regel (Docstring): Kriterien a-c, dann
    hoechste Dauer, dann kleinste sigma_n."""
    ok = [
        r
        for r in rows
        if r["median_n_cores"] >= 5.0
        and r["median_duration_frames"] >= 3.0
        and r["frac_frames_quant_ge_09"] >= 0.8
    ]
    if not ok:
        return None
    best_dur = max(r["median_duration_frames"] for r in ok)
    ok = [r for r in ok if r["median_duration_frames"] == best_dur]
    return min(ok, key=lambda r: (r["noise_step"], r["d_par"]))


def stage_pilot():
    started = time.time()
    rows = []
    for d_par in m.PILOT_D:
        for noise in m.PILOT_NOISE:
            per_seed = []
            for seed in m.SEEDS_PILOT:
                t0 = time.time()
                rec = m.run_trial(seed, "story_listen", d_par=d_par,
                                  noise_step=noise)
                p = rec["pooled"]
                per_seed.append(p)
                print(
                    f"PILOT D={d_par} sigma_n={noise} seed={seed}: "
                    f"n_cores={p['median_n_cores']:.1f} "
                    f"max={p['n_cores_max']} "
                    f"dur={p['median_duration_frames']:.1f} "
                    f"quant={p['frac_frames_quant_ge_09']:.2f} "
                    f"speed={p['mean_matched_speed']:.3f} "
                    f"({time.time() - t0:.1f} s)"
                )
            rows.append(
                {
                    "d_par": d_par,
                    "noise_step": noise,
                    "median_n_cores": float(
                        np.median([p["median_n_cores"] for p in per_seed])
                    ),
                    "median_duration_frames": float(
                        np.median([p["median_duration_frames"] for p in per_seed])
                    ),
                    "frac_frames_quant_ge_09": float(
                        np.median([p["frac_frames_quant_ge_09"] for p in per_seed])
                    ),
                }
            )
    best = _sel_key(rows)
    if best is None:
        chosen = {"d_par": m.D_PAR, "noise_step": m.NOISE_STEP,
                  "note": "keine Ecke erfuellt die Kriterien — Default haelt"}
    else:
        chosen = {"d_par": best["d_par"], "noise_step": best["noise_step"]}
    changed = (chosen["d_par"], chosen["noise_step"]) != (m.D_PAR, m.NOISE_STEP)
    out = {
        "status": "PILOT_SCAN — keine Verdict-Promotion (Labels PILOT_*)",
        "selection_rule": "registriert (Docstring v3_model.py): "
        "n_cores>=5 & dur>=3 & quant>=0.9@80%; dann hoechste Dauer, "
        "dann kleinste sigma_n",
        "rows": rows,
        "selection": chosen,
        "korrektur_log": (
            [] if not changed else
            [f"Haupt-Parameter abweichend vom Default gewaehlt: "
             f"D={chosen['d_par']}, sigma_n={chosen['noise_step']} "
             f"(Default D={m.D_PAR}, sigma_n={m.NOISE_STEP}) — vor dem "
             f"Hauptlauf offen gebucht"]
        ),
        "runtime_s": round(time.time() - started, 1),
    }
    (HERE / "selection.json").write_text(json.dumps(out, indent=2))
    (HERE / "pilot_result.json").write_text(json.dumps(out, indent=2))
    print(
        f"PILOT fertig in {time.time() - started:.0f} s -> "
        f"Selektion D={chosen['d_par']} sigma_n={chosen['noise_step']} "
        f"({'KORREKTUR-LOG' if changed else 'Default'})"
    )


def stage_control():
    """TH3-Falsifikator-Kontrolle: alpha=0 (uniformes D), story_listen.

    Laufet am SELEKTIERTEN Punkt (d_par, noise_step aus selection.json)
    mit uniformem D — einziger Unterschied zum Hauptlauf ist die
    Crowding-Modulation (registrierte TH3-Diskriminierung).
    """
    SEED_DIR.mkdir(exist_ok=True)
    started = time.time()
    sel = json.loads((HERE / "selection.json").read_text())["selection"]
    d_par, noise_step = float(sel["d_par"]), float(sel["noise_step"])
    for seed in m.SEEDS_MAIN:
        t0 = time.time()
        rec = m.run_trial(seed, "story_listen", d_par=d_par,
                          noise_step=noise_step, d_local=None)
        rec["runtime_s"] = round(time.time() - t0, 2)
        rec["crowd"] = False
        path = SEED_DIR / f"trial_{seed}_0_control.json"
        path.write_text(json.dumps(rec, ensure_ascii=False))
        p = rec["pooled"]
        print(
            f"CONTROL seed={seed}: n_cores={p['median_n_cores']:.1f} "
            f"dur={p['median_duration_frames']:.1f} "
            f"({rec['runtime_s']} s)"
        )
    print(f"control fertig in {time.time() - started:.0f} s")


def stage_main(seed_start, seed_end):
    SEED_DIR.mkdir(exist_ok=True)
    started = time.time()
    sel_path = HERE / "selection.json"
    if not sel_path.exists():
        raise SystemExit("FEHLT: selection.json (Pilot) — main bricht ab.")
    sel = json.loads(sel_path.read_text())["selection"]
    d_par = float(sel["d_par"])
    noise_step = float(sel["noise_step"])
    if seed_start <= m.SEEDS_MAIN[0]:
        d_local = m.build_crowding_d()
        f1 = m.run_trial(m.SEEDS_MAIN[0], "story_listen", d_par=d_par,
                         noise_step=noise_step, d_local=d_local,
                         return_field=True)["final_x"]
        f2 = m.run_trial(m.SEEDS_MAIN[0], "story_listen", d_par=d_par,
                         noise_step=noise_step, d_local=d_local,
                         return_field=True)["final_x"]
        ident = bool(np.array_equal(f1, f2))
        g0 = json.loads((HERE / "g0.json").read_text())
        gates = {
            "G0_OSCILLATOR": g0,
            "G1_DETERMINISM": {
                "pass": ident,
                "max_abs_diff": float(np.max(np.abs(f1 - f2))),
            },
        }
        (HERE / "gates.json").write_text(json.dumps(gates, indent=2))
        print(f"G1 DETERMINISMUS: {'PASS' if ident else 'FAIL'}")
    for seed in range(seed_start, seed_end):
        extra = ("switch_story_math",) if seed < m.SEEDS_MAIN[0] + 10 else ()
        for sched in (*m.CONDITIONS, *extra):
            t0 = time.time()
            rec = m.run_trial(seed, sched, d_par=d_par,
                              noise_step=noise_step,
                              d_local=m.build_crowding_d())
            rec["runtime_s"] = round(time.time() - t0, 2)
            rec["crowd"] = True
            path = SEED_DIR / f"trial_{seed}_{m.SCHED_IDX[sched]}.json"
            path.write_text(json.dumps(rec, ensure_ascii=False))
            p = rec["pooled"]
            print(
                f"seed={seed} {sched}: n_cores={p['median_n_cores']:.1f} "
                f"dur={p['median_duration_frames']:.1f} "
                f"speed={p['mean_matched_speed']:.3f} "
                f"quant={p['frac_frames_quant_ge_09']:.2f} "
                f"({rec['runtime_s']} s)"
            )
    print(f"main {seed_start}:{seed_end} fertig in {time.time() - started:.0f} s")


def stage_analyze():
    started = time.time()
    trials = [
        json.loads(path.read_text())
        for path in sorted(SEED_DIR.glob("trial_*.json"))
    ]
    n_cond = sum(
        1 for t in trials
        if t["sched"] != "switch_story_math" and t.get("crowd", True)
    )
    n_switch = sum(1 for t in trials if t["sched"] == "switch_story_math")
    n_ctrl = sum(
        1 for t in trials
        if t["sched"] == "story_listen" and not t.get("crowd", True)
    )
    if n_cond != 120 or n_switch != 10 or n_ctrl != 30:
        raise SystemExit(
            f"UNVOLLSTAENDIG: {n_cond} Bedingungs-Trials + {n_switch} Switch "
            f"+ {n_ctrl} Kontrolle (erwartet 120 + 10 + 30) — "
            "unterbrochene Laeufe werden nicht gebucht."
        )
    for gname in ("g0.json", "gates.json"):
        if not (HERE / gname).exists():
            raise SystemExit(f"FEHLT: {gname} — analyze bricht ab.")
    gates = {
        "G0_OSCILLATOR": json.loads((HERE / "g0.json").read_text()),
        "G1_DETERMINISM": json.loads((HERE / "gates.json").read_text())[
            "G1_DETERMINISM"
        ],
    }
    result = m.analyze_trials(
        [t for t in trials if t.get("crowd", True)], gates
    )
    # R1 CROWDING_NUCLEATION (TH3-Falsifikator, registriert)
    crowd = sorted(
        (t for t in trials
         if t["sched"] == "story_listen" and t.get("crowd", True)),
        key=lambda t: t["seed"],
    )
    ctrl = sorted(
        (t for t in trials
         if t["sched"] == "story_listen" and not t.get("crowd", True)),
        key=lambda t: t["seed"],
    )
    a = [t["pooled"]["median_n_cores"] for t in crowd]
    b = [t["pooled"]["median_n_cores"] for t in ctrl]
    wp = m.welch_p(a, b)
    med_a = float(np.median(a)) if a else float("nan")
    med_b = float(np.median(b)) if b else float("nan")
    se_pool = float("nan")
    if len(a) >= 2 and len(b) >= 2:
        se_pool = float(
            np.sqrt(np.var(a) / len(a) + np.var(b) / len(b))
        )
    shifted = bool(
        np.isfinite(wp)
        and wp < 0.05
        and np.isfinite(se_pool)
        and abs(med_a - med_b) > 2.0 * se_pool
    )
    result["r1_crowding_nucleation"] = {
        "verdict": (
            "R1_CROWDING_NUCLEATION_SHIFTED"
            if np.isfinite(wp) and wp < 0.05 and shifted
            else "R1_CROWDING_NUCLEATION_NOT_SHIFTED"
        ),
        "median_n_cores_crowd": float(np.median(a)) if a else float("nan"),
        "median_n_cores_control": float(np.median(b)) if b else float("nan"),
        "welch_p": wp,
        "criterion": "Welch-p < 0.05 UND |Δmedian| > 2·gepoolte SE",
        "falsifies": "TH3 (Crowding-Heterogenitaet als Nukleationsquelle)",
    }
    result["runtime_s"] = round(time.time() - started, 1)
    (HERE / "v3_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )
    for key, val in result["verdicts"].items():
        print(f"{key}: {val}")
    print(
        "R1 CROWDING_NUCLEATION: "
        f"{result['r1_crowding_nucleation']['verdict']} (p={wp})"
    )
    print(f"analyze fertig in {time.time() - started:.0f} s -> v3_result.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=("g0", "pilot", "control", "main", "analyze")
    )
    parser.add_argument("--seed-start", type=int, default=m.SEEDS_MAIN[0])
    parser.add_argument(
        "--seed-end", type=int, default=m.SEEDS_MAIN[-1] + 1
    )
    args = parser.parse_args()
    if args.stage == "g0":
        stage_g0()
    elif args.stage == "pilot":
        stage_pilot()
    elif args.stage == "control":
        stage_control()
    elif args.stage == "main":
        stage_main(args.seed_start, args.seed_end)
    else:
        stage_analyze()


if __name__ == "__main__":
    main()
