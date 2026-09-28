"""Treiber fuer die tci_v2-Batterie (pilot | main | analyze).

Registrierung: Docstring v2_model.py (Kriterien/Gates/Seeds fixiert VOR
dem ersten vollstaendigen Hauptlauf). Pilot = PILOT_*-Labels, keine
Verdict-Promotion. Hauptlauf: Seeds 1200-1229 (+ Switch 1200-1209),
disjunkt zu Korpus 1000-1009/2000-2009 und cellsim 200-339; G1 im
ersten Slice. Unterbrochene Laeufe werden nie gebucht (analyze prueft
die Datei-Anzahl gegen die Registrierung).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import v2_model as m

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "per_seed"


def stage_pilot():
    started = time.time()
    rows = []
    for eps in m.PILOT_EPS:
        for d_par in m.PILOT_D:
            for seed in m.SEEDS_PILOT:
                t0 = time.time()
                rec = m.run_trial(seed, "story_listen", eps=eps, d_par=d_par)
                p = rec["pooled"]
                rows.append(
                    {
                        "label": f"PILOT_eps{eps}_d{d_par}_seed{seed}",
                        "eps": eps,
                        "d_par": d_par,
                        "seed": seed,
                        "median_n_cores": p["median_n_cores"],
                        "n_cores_max": p["n_cores_max"],
                        "median_duration_frames": p["median_duration_frames"],
                        "frac_frames_quant_ge_09": p["frac_frames_quant_ge_09"],
                        "mean_matched_speed": p["mean_matched_speed"],
                        "runtime_s": round(time.time() - t0, 2),
                    }
                )
                print(
                    f"PILOT eps={eps} D={d_par} seed={seed}: "
                    f"n_cores={p['median_n_cores']:.1f} "
                    f"max={p['n_cores_max']} "
                    f"dur={p['median_duration_frames']:.1f} "
                    f"quant={p['frac_frames_quant_ge_09']:.2f} "
                    f"speed={p['mean_matched_speed']:.3f} "
                    f"({time.time() - t0:.1f} s)"
                )
    out = {
        "status": "PILOT_SCAN — keine Verdict-Promotion (Labels PILOT_*)",
        "rows": rows,
        "runtime_s": round(time.time() - started, 1),
    }
    (HERE / "pilot_result.json").write_text(json.dumps(out, indent=2))
    print(f"PILOT fertig in {time.time() - started:.0f} s -> pilot_result.json")


def stage_main(seed_start, seed_end):
    SEED_DIR.mkdir(exist_ok=True)
    started = time.time()
    if seed_start <= 1200:
        f1 = m.run_trial(1200, "story_listen", return_field=True)["final_u"]
        f2 = m.run_trial(1200, "story_listen", return_field=True)["final_u"]
        ident = bool(np.array_equal(f1, f2))
        gates = {
            "G1_DETERMINISM": {
                "pass": ident,
                "max_abs_diff": float(np.max(np.abs(f1 - f2))),
            }
        }
        (HERE / "gates.json").write_text(json.dumps(gates, indent=2))
        print(f"G1 DETERMINISMUS: {'PASS' if ident else 'FAIL'}")
    for seed in range(seed_start, seed_end):
        extra = ("switch_story_math",) if seed < 1210 else ()
        for sched in (*m.CONDITIONS, *extra):
            t0 = time.time()
            rec = m.run_trial(seed, sched)
            rec["runtime_s"] = round(time.time() - t0, 2)
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
    n_cond = sum(1 for t in trials if t["sched"] != "switch_story_math")
    n_switch = sum(1 for t in trials if t["sched"] == "switch_story_math")
    if n_cond != 120 or n_switch != 10:
        raise SystemExit(
            f"UNVOLLSTAENDIG: {n_cond} Bedingungs-Trials + {n_switch} Switch "
            f"(erwartet 120 + 10) — unterbrochene Laeufe werden nicht gebucht."
        )
    gates_path = HERE / "gates.json"
    if not gates_path.exists():
        raise SystemExit("FEHLT: gates.json (G1) — analyze bricht ab.")
    gates = json.loads(gates_path.read_text())
    result = m.analyze_trials(trials, gates)
    result["runtime_s"] = round(time.time() - started, 1)
    (HERE / "v2_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )
    for key, val in result["verdicts"].items():
        print(f"{key}: {val}")
    print(f"analyze fertig in {time.time() - started:.0f} s -> v2_result.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("pilot", "main", "analyze"))
    parser.add_argument("--seed-start", type=int, default=1200)
    parser.add_argument("--seed-end", type=int, default=1230)
    args = parser.parse_args()
    if args.stage == "pilot":
        stage_pilot()
    elif args.stage == "main":
        stage_main(args.seed_start, args.seed_end)
    else:
        stage_analyze()


if __name__ == "__main__":
    main()
