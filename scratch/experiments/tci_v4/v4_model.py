"""tci_v4 — Registrierter Diskriminator der Hylothese-Kette (Glied iii).

Basis: v3 (Brusselator-Träger, G0-PASS, Q1-ABSENT-Regime mit ~550
Rausch-Turbulenz-Kernen/Frame, Dekodier-Gain 0). Die Hylothese-Kette
(scratch/notes/tci_hylothese_formulas.md, F4) sagt nach der Korrektur:
Dekodier-Gain erfordert, dass der Task-Drive die KOPPLUNGSSTRUKTUR
moduliert — nicht nur additiv das Substrat. Das ist hier die einzige
Variation gegenüber v3.

Registrierung (vor der ersten Messung fixiert):

- Basisfeld: v3-Bauform wörtlich (echtes Modul compute_crowding,
  6 Gauß-Cluster, V_ex = 5e4 Å³, voxel 100 nm, alpha = 4.0), Crowding-
  Seed 4243 (disjunkt zu v3-Seed 4242). Statischer Arm:
  d_local = const = D_par·exp(−α·c0)/max → D_par-normiert (v3-Form).
- Modulation (deklariertes konstruiertes Surrogat, EINHEIT B3:
  übertragene Größe = lokales excluded volume): der Crowding-Index
  im AKTIVEN Task-Band wird um +δ_c·drv_norm(t) erhöht (Drive rekrutiert
  Makromoleküle → Crowding ↑ → d ↓), im anderen Band um −δ_c·drv_norm
  erniedrigt; drv_norm = drive_amplitude/AMP ∈ [0, 1] (registrierte
  Wellenform aus v3). d_local(t,x) = D_par·exp(−α·c0(x)·M(t,x))/
  max_statisch mit fester Normierung (die des statischen Felds) — die
  Arme unterscheiden sich AUSSCHLIESSLICH durch die Modulation, gleiche
  Blobs, gleiche Skalierung. Vorzeichenkonvention ex ante fixiert.
- delta_c: deklariert frei; LADDER = (0.2, 0.5) fix. Primär 0.2.
  Eskalation auf 0.5 NUR bei Feasibility-Fail (KORREKTUR-LOG vor dem
  Lauf). Nach Messung kein Wechsel.
- FEASIBILITY (vor dem Lauf, Throwaway-Seed 1999 — nie gebucht):
  (i) G0 (v3-Kriterien wörtlich) am statischen Träger PASS;
  (ii) relative d-Modulation am c0-Maximum des aktiven Bandes bei
     vollem Drive strikt > 0 (KORREKTUR vor dem gebuchten Lauf:
     zuvor wurde am GLOBALEN c0-Max gemessen, was den anti-phase
     Zeichenkonvention des anderen Bandes zum Kriterium machte;
     geloggt, vor jeder gebuchten Messung repariert);
  (iii) ein vollständiger Trial je Arm über beide Wellenformen
     (story_listen, math_answer) finit (alle pooled-Metriken endlich).
  Fail von (ii)/(iii) bei 0.2 → KORREKTUR-LOG + Eskalation 0.5; Fail
  beider Ladder-Einträge → modulierter Arm UNFEASIBLE (Buchung, kein
  Dekodier-Lauf). Fail von (i) → v3-Basis abhanden, Lauf entfällt.
- Replikate: je (Seed, Schedule, Arm) 2 Replikate r ∈ {0, 1} —
  RNG-Stream = default_rng(seed*16 + SCHED_IDX[sched] + r*REP_PRIME),
  REP_PRIME = 7919 (deklariert). Grund (vor dem Lauf, mechanistisch):
  R2 vergleicht per-seed Accuracy-Bündel; LOO Nearest-Centroid braucht
  ≥ 2 Trials je Klasse je Seed. Rep 0 ist der unveränderte v3-Stream.
- Trials: 10 Seeds 1600–1609 (disjunkt zu v3 1500–1529/1700–1703,
  Korpus 1000–1009/2000–2009, cellsim 200–339, v2 1200–1229/1400–1403)
  × 4 Schedules × 2 Arme × 2 Replikate = 160 Trials. Keine Switch-Trials.
- Dekodier-Analyse (je Arm, verbatim v3): Features spiral/position,
  LOO Nearest-Centroid 4-kanalig über die 80 Trials des Arms,
  Permutationsnull 10k (PERM_SEED_Q2 = 4347), Amplituden-Baseline mit
  gepaarter Sign-Flip-Permutation (PERM_SEED_Q5 = 4348), Chance 0.25.
  Arm-Labels folgen den Q2-Regeln wörtlich (Deskriptor je Arm).
- R2 (registriert, Glied iii): je (Seed, Arm) LOO-Accuracy über die
  8 Trials (Features spiral); Δacc = mean(acc_mod) − mean(acc_static);
  gepoolte SE = sqrt(var_mod/10 + var_static/10).
  R2_MOD_CARRIES iff welch_p < 0.05 UND Δacc > 2·gepoolte SE;
  R2_WRONG_DIRECTION iff welch_p < 0.05 UND Δacc < −2·gepoolte SE;
  sonst R2_NULL (NaN konservativ als NULL gebucht).
  Alles außer MOD_CARRIES falsifiziert Glied (iii) und mit ihm F4 in
  der Ebene-C-Lesart; NULL ist Regime-Aussage (Residuum L2, nie
  Unmöglichkeit).
- Gates: G0 OSCILLATOR vor dem Lauf (v3 wörtlich, statischer Träger —
  ungetrieben ist die Modulation identisch dem statischen Feld);
  G1 DETERMINISM im ersten Slice (beide Arme, Feld-Doppellauf);
  G2 FINITENESS wörtlich. Unterbrochene Läufe werden nie gebucht
  (analyze prüft 160 Dateien).
- Per-Seed-Vektoren vollständig persistiert (per_seed/; mean-level-
  Buchung ist unauditierbar — Harness-Lektion iter-27/28).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "tci_v3"))

import v3_model as base  # noqa: E402  (verbatim-Übername der Maschinerie)

# --- Registrierte Konstanten (EX ANTE) ---
CROWD_SEED_V4 = 4243
DELTA_C = 0.2
DELTA_LADDER = (0.2, 0.5)
FEAS_SEED = 1999
REP_PRIME = 7919
N_REP = 2
SEEDS_V4 = tuple(range(1600, 1610))
PERM_SEED_Q2 = 4347
PERM_SEED_Q5 = 4348
N_PERM = 10_000
CHANCE_4WAY = 0.25
ARMS = ("static", "mod")
SEEDS_MAIN = SEEDS_V4
R2_CRITERION_DOC = (
    "R2_MOD_CARRIES iff welch_p < 0.05 UND Δacc > 2·gepoolte SE; "
    "R2_WRONG_DIRECTION iff welch_p < 0.05 UND Δacc < −2·gepoolte SE; "
    "sonst R2_NULL"
)

D_PAR = base.D_PAR
AMP = base.AMP
L = base.L
STEPS = base.STEPS
SCHED_IDX = base.SCHED_IDX
CONDITIONS = base.CONDITIONS


def build_base():
    """Statisches D-Feld + Crowding-Index über das echte cellsim-Modul
    (v3-Bauform verbatim, Crowding-Seed 4243).
    """
    rng = np.random.default_rng(CROWD_SEED_V4)
    counts = np.zeros((L, L, 1))
    yy, xx = np.mgrid[0:L, 0:L]
    for _ in range(base.CROWD_BLOBS):
        ci, cj = rng.uniform(0.0, L, size=2)
        rad = rng.uniform(6.0, 14.0)
        amp = rng.uniform(400.0, 1200.0)
        counts[:, :, 0] += amp * np.exp(
            -((xx - ci) ** 2 + (yy - cj) ** 2) / (2.0 * rad**2)
        )
    fld = base.compute_crowding(
        {"synthetic_macromol": counts},
        {"synthetic_macromol": base.MACROMOL_V_EX},
        base.VOXEL_EDGE_NM,
        base.CrowdingParams(
            alpha=base.CROWD_ALPHA, diffusion_bulk_nm2_per_ms=1.0e3
        ),
    )
    c0 = fld.crowding_index[:, :, 0]
    e_max = float(np.exp(-base.CROWD_ALPHA * c0).max())
    d_static = D_PAR * np.exp(-base.CROWD_ALPHA * c0) / e_max
    return c0, d_static


class ModulatedProvider:
    """Task-moduliertes d_local: c' = c0·(1 ± δ_c·drv_norm) je Band, mit
    fester Normierungskonstante. Felder je (Band, drv)-Wert vorbereitet
    (drv aus der registrierten Wellenform — 40 diskrete Werte je Cycle
    für listen, 2 für answer).

    Vorzeichen: aktives Band 1 + δ·drv (Crowding ↑, d ↓), anderes Band
    1 − δ·drv. Die Task-Kopplung läuft DURCH die Kopplungsstruktur —
    der einzige Unterschied zum statischen Arm.
    """

    def __init__(self, c0, d_static, delta):
        self.c0 = c0
        self.delta = float(delta)
        e_max = float(np.exp(-base.CROWD_ALPHA * c0).max())
        self._norm = D_PAR / e_max  # feste Normierungskonstante
        self._d_static = d_static
        self.fields = {}
        for task in ("story", "math"):
            other = "math" if task == "story" else "story"
            own_mask = base.spatial_mask(task)
            other_mask = base.spatial_mask(other)

            def _store(key, drv, own, oth):
                if key in self.fields:
                    return
                mult = np.where(own, 1.0 + self.delta * drv, 1.0)
                mult = np.where(oth, 1.0 - self.delta * drv, mult)
                self.fields[key] = self._norm * np.exp(
                    -base.CROWD_ALPHA * c0 * mult
                )

            # Wellenform-Phase als Key (keine Float-Keys — t%40 resp.
            # t%20<6 reproduziert drive_amplitude exakt, Periodizität
            # wörtlich).
            for tm in range(40):
                drv = base.drive_amplitude("listen", tm) / AMP
                _store((task, "listen", tm), drv, own_mask, other_mask)
            for on in (True, False):
                drv = 1.0 if on else 0.0
                _store((task, "answer", on), drv, own_mask, other_mask)

    def field(self, cond, t):
        task, mode = cond.split("_")
        key = (
            (task, "listen", t % 40)
            if mode == "listen"
            else (task, "answer", (t % 20) < 6)
        )
        return self.fields[key]

    def modulation_stats(self):
        """Relative d-Modulationstiefe bei vollem Drive (Feasibility ii).

        KORREKTUR vor dem gebuchten Lauf (Feasibility-Stufe, Throwaway-
        Seed 1999, nie gebucht): die Tiefe wird am c0-Maximum INNERHALB
        des aktiven Bandes des Tasks gemessen — nicht am globalen c0-Max.
        Grund: die registrierte Vorzeichenkonvention ist anti-phase (aktives
        Band 1 + δ, anderes 1 − δ); am globalen Maximum liegt das aktive
        Band nur für einen der beiden Tasks, dort trägt der andere
        Task zwangsläufig das entgegengesetzte Vorzeichen. Geprüft wird
        die registrierte Behauptung: im GETRIEBENEN Band ist die
        Modulationstiefe strikt > 0.
        """
        out = {}
        for task in ("story", "math"):
            other = "math" if task == "story" else "story"
            d_mod = self.fields[(task, "listen", 10)]
            ratio = d_mod / self._d_static
            own = base.spatial_mask(task)
            oth = base.spatial_mask(other)
            # c0-Maximum innerhalb des eigenen (getriebenen) Bandes
            own_idx = np.where(own, self.c0, -np.inf)
            imax = np.unravel_index(
                np.argmax(own_idx), self.c0.shape
            )
            oth_idx = np.where(oth, self.c0, -np.inf)
            imax_oth = np.unravel_index(
                np.argmax(oth_idx), self.c0.shape
            )
            out[task] = {
                "ratio_at_c0_max_own_band": float(
                    ratio[imax]
                ),
                "depth_at_c0_max_own_band": float(1.0 - ratio[imax]),
                "ratio_at_c0_max_other_band": float(ratio[imax_oth]),
                "depth_at_c0_max_other_band": float(
                    1.0 - ratio[imax_oth]
                ),
                "ratio_min": float(ratio.min()),
                "ratio_max": float(ratio.max()),
                "band_d_std_over_mean": float(
                    self._d_static[own].std() / self._d_static.mean()
                ),
            }
        return out


def run_trial_v4(
    seed,
    sched_key,
    *,
    arm="static",
    rep=0,
    delta=None,
    d_static=None,
    c0=None,
    provider=None,
    noise_step=base.NOISE_STEP,
    return_field=False,
):
    """Ein Trial (v3-Stepping wörtlich; Arm entscheidet über d_local)."""
    schedule = base.SCHEDULES[sched_key]
    rng = np.random.default_rng(
        seed * 16 + base.SCHED_IDX[sched_key] + REP_PRIME * rep
    )
    x = base.X_FP + rng.normal(0.0, base.NOISE_INIT, (L, L))
    y = base.Y_FP + rng.normal(0.0, base.NOISE_INIT, (L, L))
    if arm == "static":
        d_local_static = d_static
    elif provider is None:
        provider = ModulatedProvider(c0, d_static, delta)
    masks = {task: base.spatial_mask(task) for task in base.BANDS}

    frames = []
    tracks = {}
    terminations = []
    hist_neg = np.zeros(16)
    hist_pos = np.zeros(16)
    amp_hist = np.zeros(16)
    total_cores = 0
    speed_steps = []
    prev_cores = []

    for t in range(base.STEPS):
        cond = schedule[0][1]
        for start, cond_name in schedule:
            if t >= start:
                cond = cond_name
        task, mode = cond.split("_")
        drv = base.drive_amplitude(mode, t) * masks[task]
        d_loc = (
            d_local_static if arm == "static" else provider.field(cond, t)
        )
        x_new = x + base.DT * (
            base.A_PAR
            + drv
            + x**2 * y
            - (base.B_PAR + 1.0) * x
            + d_loc * base.laplacian(x)
        )
        x_new += rng.normal(0.0, noise_step, (L, L))
        y = y + base.DT * (
            base.B_PAR - x**2 * y + d_loc * base.laplacian(y)
        )
        x = x_new
        if (t + 1) % base.SNAP_EVERY == 0:
            fi = len(frames)
            vort, cores = base.frame_cores(x, y, d_loc)
            pairs = base.match_frames(prev_cores, cores)
            matched_i = {i for i, _j, _d in pairs}
            matched_j = {j for _i, j, _d in pairs}
            new_tracks = {}
            for i, j, dist in pairs:
                tr = tracks.get(i)
                if tr is None:
                    tr = {"start_fi": fi, "speeds": [], "qs": []}
                else:
                    tr["speeds"].append(dist)
                tr["qs"].append(cores[j]["charge"])
                tr["end"] = (cores[j]["row"], cores[j]["col"])
                new_tracks[j] = tr
                speed_steps.append(dist)
            for i, tr in tracks.items():
                if i not in matched_i:
                    near = any(
                        (tr["end"][0] - c["row"]) ** 2
                        + (tr["end"][1] - c["col"]) ** 2
                        <= base.TERMINATION_DIST**2
                        for c in cores
                    )
                    terminations.append(
                        {
                            "frame": fi,
                            "duration_frames": fi - tr["start_fi"],
                            "interaction": bool(near),
                            "q": tr["qs"][-1] if tr["qs"] else 0.0,
                        }
                    )
            for j, c in enumerate(cores):
                if j not in matched_j:
                    new_tracks[j] = {
                        "start_fi": fi,
                        "speeds": [],
                        "qs": [c["charge"]],
                        "end": (c["row"], c["col"]),
                    }
            tracks = new_tracks
            prev_cores = cores

            n_c = len(cores)
            q_frac = (
                float(np.mean([c["quant"] for c in cores])) if n_c else 0.0
            )
            p_cw = (
                float(np.mean([c["charge"] < 0 for c in cores]))
                if n_c
                else 0.0
            )
            mean_radius = (
                float(np.mean([np.sqrt(c["area"] / np.pi) for c in cores]))
                if n_c
                else 0.0
            )
            frames.append(
                {
                    "t": t,
                    "n_cores": n_c,
                    "quant_frac": q_frac,
                    "p_cw": p_cw,
                    "mean_radius": mean_radius,
                    "max_abs_vort": float(np.max(np.abs(vort))),
                }
            )
            for c in cores:
                bi = min(3, int(c["row"] * 4.0 / L))
                bj = min(3, int(c["col"] * 4.0 / L))
                target = hist_neg if c["charge"] < 0 else hist_pos
                target[bi * 4 + bj] += 1.0
                total_cores += 1
            act_grid = np.hypot(x - base.X_FP, y - base.Y_FP)
            amp_grid = act_grid.reshape(4, L // 4, 4, L // 4).mean(axis=(1, 3))
            amp_hist += amp_grid.ravel() / amp_grid.sum()

    durations = [z["duration_frames"] for z in terminations]
    for tr in tracks.values():
        durations.append(len(frames) - tr["start_fi"])

    n_frames = len(frames)
    n_cores_list = [f["n_cores"] for f in frames]
    p_cw_frames = [f["p_cw"] for f in frames if f["n_cores"] > 0]
    rad = [f["mean_radius"] for f in frames if f["n_cores"] > 0]
    n_term = len(terminations)
    n_inter = sum(int(z["interaction"]) for z in terminations)
    pooled = {
        "median_n_cores": float(np.median(n_cores_list)),
        "n_cores_max": int(max(n_cores_list)),
        "median_duration_frames": (
            float(np.median(durations)) if durations else 0.0
        ),
        "mean_matched_speed": (
            float(np.mean(speed_steps)) if speed_steps else 0.0
        ),
        "n_speed_steps": len(speed_steps),
        "mean_radius": float(np.mean(rad)) if rad else 0.0,
        "p_cw": (
            float(np.mean(p_cw_frames)) if p_cw_frames else float("nan")
        ),
        "n_terminations": n_term,
        "n_terminations_interaction": n_inter,
        "termination_interaction_fraction": (
            float(n_inter) / n_term if n_term else float("nan")
        ),
        "frac_frames_quant_ge_09": (
            float(
                np.mean(
                    [
                        f["quant_frac"] >= 0.9
                        for f in frames
                        if f["n_cores"] > 0
                    ]
                )
            )
            if any(f["n_cores"] > 0 for f in frames)
            else 0.0
        ),
        "total_cores": total_cores,
    }

    hist_total = hist_neg + hist_pos
    scale = max(1.0, float(total_cores))
    amp_hist = amp_hist / max(1e-12, float(amp_hist.sum()))
    dyn = [
        pooled["median_duration_frames"],
        pooled["mean_matched_speed"],
        pooled["mean_radius"],
        pooled["median_n_cores"],
    ]
    features_spiral = (
        (hist_neg / scale).tolist()
        + (hist_pos / scale).tolist()
        + [pooled["p_cw"]]
        + dyn
    )
    features_position = (hist_total / scale).tolist() + dyn

    out = {
        "seed": seed,
        "sched": sched_key,
        "arm": arm,
        "rep": rep,
        "delta": float(delta),
        "schedule": [[s, c] for s, c in schedule],
        "n_frames": n_frames,
        "frames": frames,
        "pooled": pooled,
        "durations": durations,
        "term_interaction": [bool(z["interaction"]) for z in terminations],
        "term_q": [z["q"] for z in terminations],
        "features_spiral": features_spiral,
        "features_position": features_position,
    }
    if return_field:
        out["final_x"] = x
        out["final_y"] = y
    return out


# --- Dekodier-Maschinerie: verbatim aus v3 (base) übernommen ---
_loo_pred = base._loo_pred
loo_acc = base.loo_acc
loo_correct = base.loo_correct
perm_p_above = base.perm_p_above
sign_flip_p = base.sign_flip_p
welch_p = base.welch_p


def decode_analysis(trials):
    """Q2-Maschinerie wörtlich aus v3 (je Arm angewendet)."""
    X = np.array([t["features_spiral"] for t in trials], dtype=float)
    Xp = np.array([t["features_position"] for t in trials], dtype=float)
    y = np.array([base.SCHED_IDX[t["sched"]] for t in trials])
    finite = bool(np.isfinite(X).all() and np.isfinite(Xp).all())
    if not finite:
        return {
            "acc_spiral": float("nan"),
            "acc_position": float("nan"),
            "gain": float("nan"),
            "null_mean": float("nan"),
            "p_perm": float("nan"),
            "paired_p": float("nan"),
            "n_trials": len(trials),
            "label": "Q2_AT_CHANCE",
        }
    acc, null_mean, p_perm, null = perm_p_above(
        X, y, N_PERM, PERM_SEED_Q2
    )
    acc_pos = loo_acc(Xp, y)
    diffs = loo_correct(X, y) - loo_correct(Xp, y)
    _dstat, paired_p = sign_flip_p(diffs, N_PERM, PERM_SEED_Q5)
    gain = acc - acc_pos
    if (
        p_perm < 0.05
        and acc > CHANCE_4WAY
        and np.isfinite(paired_p)
        and paired_p < 0.05
    ):
        q2 = "ABOVE_CHANCE"
    elif acc > CHANCE_4WAY:
        q2 = "WEAK"
    else:
        q2 = "AT_CHANCE"
    return {
        "acc_spiral": acc,
        "acc_position": acc_pos,
        "gain": gain,
        "null_mean": float(null_mean),
        "p_perm": p_perm,
        "paired_p": paired_p,
        "n_trials": len(trials),
        "label": f"Q2_DECODE_{q2}",
    }


def per_seed_accuracy(trials, feature_key="features_spiral"):
    """Je (Seed, Arm) LOO-Accuracy über die 2·4 Trials (R2-Einheit)."""
    by_seed = {}
    for t in trials:
        by_seed.setdefault(t["seed"], []).append(t)
    rows = []
    for seed in SEEDS_V4:
        group = by_seed.get(seed, [])
        X = np.array([t[feature_key] for t in group], dtype=float)
        y = np.array([base.SCHED_IDX[t["sched"]] for t in group])
        finite = bool(np.isfinite(X).all())
        rows.append(
            {
                "seed": seed,
                "acc": loo_acc(X, y) if finite else float("nan"),
                "n_trials": len(group),
            }
        )
    return rows


def analyze_v4(trials, gates):
    """G2 + Arm-Deskriptoren (Q2-Maschinerie verbatim je Arm) + R2."""
    nan_fields = []
    for t in trials:
        for key in (
            "median_n_cores",
            "median_duration_frames",
            "mean_matched_speed",
            "mean_radius",
        ):
            if not np.isfinite(t["pooled"][key]):
                nan_fields.append(f"{t['seed']}:{t['sched']}:arm={t['arm']}:{key}")

    arms = {}
    for arm in ARMS:
        sel = [t for t in trials if t["arm"] == arm]
        dec = decode_analysis(sel)
        dec["per_seed"] = {
            feature: per_seed_accuracy(sel, feature)
            for feature in ("features_spiral", "features_position")
        }
        dec["pooled_desc"] = {
            "median_n_cores": float(
                np.mean([t["pooled"]["median_n_cores"] for t in sel])
            ),
            "interaction_fraction": float(
                sum(t["pooled"]["n_terminations_interaction"] for t in sel)
                / max(1, sum(t["pooled"]["n_terminations"] for t in sel))
            ),
            "frac_frames_quant_ge_09": float(
                np.mean([t["pooled"]["frac_frames_quant_ge_09"] for t in sel])
            ),
        }
        arms[arm] = dec

    a = [r["acc"] for r in arms["mod"]["per_seed"]["features_spiral"]]
    b = [r["acc"] for r in arms["static"]["per_seed"]["features_spiral"]]
    wp = welch_p(a, b)
    delta_acc = float(np.mean(a) - np.mean(b))
    se_pool = float(np.sqrt(np.var(a) / len(a) + np.var(b) / len(b)))
    if not (np.isfinite(wp) and np.isfinite(se_pool)):
        r2 = "R2_NULL"
    elif wp < 0.05 and delta_acc > 2.0 * se_pool:
        r2 = "R2_MOD_CARRIES"
    elif wp < 0.05 and delta_acc < -2.0 * se_pool:
        r2 = "R2_WRONG_DIRECTION"
    else:
        r2 = "R2_NULL"

    return {
        "status": "REGISTERED_RUN_v4_vollstaendig",
        "registration": "Docstring v4_model.py (fixiert vor dem Lauf)",
        "delta_c": float(DELTA_C),
        "gates": gates,
        "g2": {
            "finite_decision_metrics": not nan_fields,
            "nan_fields": nan_fields,
            "note": "NaN offen gebucht, konservativ gewertet",
        },
        "arms": arms,
        "r2": {
            "verdict": r2,
            "delta_acc": delta_acc,
            "pooled_se": se_pool,
            "welch_p": wp,
            "acc_mean_mod": float(np.mean(a)),
            "acc_mean_static": float(np.mean(b)),
            "acc_per_seed_mod": a,
            "acc_per_seed_static": b,
            "criterion": R2_CRITERION_DOC,
            "falsifies": (
                "Hylothese-Kette Glied (iii) und mit ihm F4 "
                "(Ebene-C-Lesart) — außer bei MOD_CARRIES"
            ),
        },
    }
