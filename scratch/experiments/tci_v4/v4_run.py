"""Treiber fuer tci_v4 (g0 | feasibility | run | analyze).

Registrierung: Docstring v4_model.py (fixiert VOR der ersten Messung).
Feasibility-Versuche laufen am Throwaway-Seed 1999 (FEAS-Label, nie
gebucht). Der Hauptlauf liest feasibility.json (gewaehltes delta_c);
unterbrochene Laeufe werden nie gebucht (analyze prueft 160 Dateien
gegen die Registrierung). Trials laufen parallel (multiprocessing Pool),
Ergebnisse persistieren je Trial in per_seed/.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import v4_model as m

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "per_seed"

_CTX0 = None  # (d_static, c0, provider) je Worker


def _init_worker(delta):
    global _CTX0
    c0, d_static = m.build_base()
    provider = m.ModulatedProvider(c0, d_static, delta)
    _CTX0 = (d_static, c0, provider)


def _one_trial(job):
    seed, sched, arm, rep = job
    d_static, c0, provider = _CTX0
    t0 = time.time()
    rec = m.run_trial_v4(
        seed,
        sched,
        arm=arm,
        rep=rep,
        delta=provider.delta,
        d_static=d_static,
        c0=c0,
        provider=provider,
    )
    rec["runtime_s"] = round(time.time() - t0, 2)
    return seed, sched, arm, rep, rec


def stage_g0():
    _c0, d_static = m.build_base()
    gate = m.base.oscillator_gate(d_local=d_static)
    (HERE / "g0.json").write_text(json.dumps(gate, indent=2))
    print(f"G0 OSCILLATOR: {'PASS' if gate['pass'] else 'FAIL'} {gate}",
          flush=True)


def _trial_finite(rec):
    return all(
        np.isfinite(rec["pooled"][key])
        for key in (
            "median_n_cores",
            "median_duration_frames",
            "mean_matched_speed",
            "mean_radius",
        )
    )


def stage_feasibility():
    """Registrierte Feasibility (Throwaway-Seed 1999, nie gebucht).

    (i) G0 am statischen Träger; (ii) relative d-Modulation am c0-Max
    strikt > 0; (iii) je Arm ein voller Trial je Wellenform finit.
    Fehler bei 0.2 → Eskalation 0.5 (KORREKTUR-LOG); beide fail →
    UNFEASIBLE (kein Dekodier-Lauf).
    """
    started = time.time()
    c0, d_static = m.build_base()
    g0 = json.loads((HERE / "g0.json").read_text())
    korrektur = []
    ladder_report = []
    chosen = None
    unfeasible = False
    for delta in m.DELTA_LADDER:
        provider = m.ModulatedProvider(c0, d_static, delta)
        stats = provider.modulation_stats()
        depth_ok = all(
            v["depth_at_c0_max_own_band"] > 0.0
            and np.isfinite(v["depth_at_c0_max_own_band"])
            for v in stats.values()
        )
        fin_ok = True
        for arm in m.ARMS:
            for sched in ("story_listen", "math_answer"):
                rec = m.run_trial_v4(
                    m.FEAS_SEED,
                    sched,
                    arm=arm,
                    rep=0,
                    delta=delta,
                    d_static=d_static,
                    c0=c0,
                    provider=provider,
                )
                ok = _trial_finite(rec)
                fin_ok = fin_ok and ok
                print(
                    f"FEAS seed={m.FEAS_SEED} {sched} arm={arm} "
                    f"delta={delta}: finite={ok} "
                    f"n_cores={rec['pooled']['median_n_cores']:.1f}"
                )
        entry = {
            "delta": delta,
            "depth": stats,
            "depth_positive": depth_ok,
            "finiteness": fin_ok,
            "g0_pass": bool(g0["pass"]),
            "feasible": bool(depth_ok and fin_ok and g0["pass"]),
        }
        ladder_report.append(entry)
        if entry["feasible"] and chosen is None:
            chosen = delta
        elif chosen is None and not entry["feasible"]:
            korrektur.append(
                f"Ladder-Eintrag delta_c={delta} scheitert Feasibility "
                f"(depth_positive={depth_ok}, finiteness={fin_ok}, "
                f"G0={bool(g0['pass'])}) — Eskalation/Buchung vor dem Lauf"
            )
    if chosen is None:
        unfeasible = True
        korrektur.append(
            "beide Ladder-Einträge scheitern — modulierter Arm UNFEASIBLE"
        )
    out = {
        "status": ("UNFEASIBLE" if unfeasible else "FEASIBLE"),
        "chosen_delta_c": chosen,
        "ladder": ladder_report,
        "g0": g0,
        "korrektur_log": korrektur,
        "note": "Throwaway-Seed 1999 — nie gebucht (Registrierung)",
        "runtime_s": round(time.time() - started, 1),
    }
    (HERE / "feasibility.json").write_text(json.dumps(out, indent=2))
    print(
        f"feasibility: status={out['status']} "
        f"delta_c={chosen} in {time.time() - started:.0f} s "
        f"(KORREKTUR: {len(korrektur)})"
    )


def stage_run():
    SEED_DIR.mkdir(exist_ok=True)
    started = time.time()
    feas = json.loads((HERE / "feasibility.json").read_text())
    if feas["status"] != "FEASIBLE":
        raise SystemExit("modulierter Arm UNFEASIBLE — kein Lauf (gebucht)")
    delta = float(feas["chosen_delta_c"])
    c0, d_static = m.build_base()
    jobs = []
    for seed in m.SEEDS_V4:
        for sched in m.CONDITIONS:
            for arm in m.ARMS:
                for rep in range(m.N_REP):
                    jobs.append((seed, sched, arm, rep))
    # G1 DETERMINISM (beide Arme, Feld-Doppellauf) im ersten Slice
    provider = m.ModulatedProvider(c0, d_static, delta)
    gates_g1 = {}
    for arm in m.ARMS:
        f1 = m.run_trial_v4(
            m.SEEDS_V4[0], "story_listen", arm=arm, rep=0, delta=delta,
            d_static=d_static, c0=c0, provider=provider,
            return_field=True,
        )["final_x"]
        f2 = m.run_trial_v4(
            m.SEEDS_V4[0], "story_listen", arm=arm, rep=0, delta=delta,
            d_static=d_static, c0=c0, provider=provider,
            return_field=True,
        )["final_x"]
        ident = bool(np.array_equal(f1, f2))
        gates_g1[arm] = {
            "pass": ident,
            "max_abs_diff": float(np.max(np.abs(f1 - f2))),
        }
        print(f"G1 DETERMINISM [{arm}]: {'PASS' if ident else 'FAIL'}")
    g0 = feas["g0"]
    (HERE / "gates.json").write_text(
        json.dumps(
            {
                "G0_OSCILLATOR": g0,
                "G1_DETERMINISM": gates_g1,
                "delta_c_used": delta,
            },
            indent=2,
        )
    )

    # Die G1-Doppelläufe sind Throwaway-Gate-Läufe; alle 160
    # registrierten Trials laufen danach (Seed 1600 inklusive).
    with mp.Pool(
        processes=min(8, mp.cpu_count() - 1),
        initializer=_init_worker,
        initargs=(delta,),
    ) as pool:
        for done, (seed, sched, arm, rep, rec) in enumerate(
            pool.imap_unordered(_one_trial, jobs), start=1
        ):
            name = (
                f"trial_{seed}_{m.SCHED_IDX[sched]}_{arm}_{rep}.json"
            )
            (SEED_DIR / name).write_text(
                json.dumps(rec, ensure_ascii=False)
            )
            p = rec["pooled"]
            print(
                f"seed={seed} {sched} {arm} rep={rep}: "
                f"n_cores={p['median_n_cores']:.1f} "
                f"quant={p['frac_frames_quant_ge_09']:.2f} "
                f"itx={p['termination_interaction_fraction']:.3f} "
                f"({rec['runtime_s']} s) [{done}/{len(jobs)}]",
                flush=True,
            )
    print(f"run fertig in {time.time() - started:.0f} s (160 Trials)")


def stage_analyze():
    started = time.time()
    for gname in ("g0.json", "gates.json", "feasibility.json"):
        if not (HERE / gname).exists():
            raise SystemExit(f"FEHLT: {gname} — analyze bricht ab.")
    feas = json.loads((HERE / "feasibility.json").read_text())
    if feas["status"] != "FEASIBLE":
        raise SystemExit("Feasibility UNFEASIBLE — kein Gebuchter Lauf.")
    gates = json.loads((HERE / "gates.json").read_text())
    if not gates["G0_OSCILLATOR"]["pass"]:
        raise SystemExit("G0 FAIL — gebuchte Analyse verboten (Registrierung).")
    paths = sorted(SEED_DIR.glob("trial_*.json"))
    if len(paths) != 160:
        raise SystemExit(
            f"UNVOLLSTAENDIG: {len(paths)} Dateien (erwartet 160; "
            "unterbrochene Laeufe werden nicht gebucht)."
        )
    trials = [json.loads(p.read_text()) for p in paths]
    delta_used = float(gates.get("delta_c_used", 0.0))
    for t in trials:
        if not float(np.isclose(t["delta"], delta_used)):
            raise SystemExit(
                f"delta_c-Mismatch: trial delta={t['delta']} vs {delta_used}"
            )
    for arm in m.ARMS:
        sel = [t for t in trials if t["arm"] == arm]
        if len(sel) != 80:
            raise SystemExit(
                f"Arm {arm}: {len(sel)} Trials (erwartet 80) — "
                "Lauf unvollständig, nicht buchen."
            )
    result = m.analyze_v4(trials, gates)
    result["runtime_s"] = round(time.time() - started, 1)
    (HERE / "v4_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )
    print(
        "R2 HYLOTHESE-Glied-(iii): "
        f"{result['r2']['verdict']} (Δacc={result['r2']['delta_acc']:.4f}, "
        f"2SE={2.0 * result['r2']['pooled_se']:.4f}, "
        f"welch_p={result['r2']['welch_p']})"
    )
    for arm in m.ARMS:
        d = result["arms"][arm]
        print(f"[{arm}] {d['label']}: acc={d['acc_spiral']:.4f} "
              f"pos={d['acc_position']:.4f} gain={d['gain']:.4f} "
              f"p_perm={d['p_perm']}")
    print(f"analyze fertig in {time.time() - started:.0f} s -> v4_result.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=("g0", "feasibility", "run", "analyze")
    )
    args = parser.parse_args()
    if args.stage == "g0":
        stage_g0()
    elif args.stage == "feasibility":
        stage_feasibility()
    elif args.stage == "run":
        stage_run()
    else:
        stage_analyze()


if __name__ == "__main__":
    main()
