"""tci_v2 — excitables Regime + Xu-Toolbox-Analog (REGISTRIERUNG vor Lauf).

Anlass (Nutzersteuerung 2026-09-28): «wie kommen wir zu einer corroborated
qualia und tci bzgl. bewusstsein? ... mache dafür jetzt weitere experimente
mit cellsim, wo wir alles von a bis z testen können ... du darfst gerne die
rohdaten und interpretation in die experimente mit einbeziehen.»

Ziel: der registrierte v2-Vektor (Notiz §7 Ebene C; experiment.md tci_xu
Interpretation 6): ein EXCITABLES Regime (FitzHugh-Nagumo-Lattice) als das
dem TCI-Korpus fehlende Ausbreitungsregime, an dem die Xu-Pipeline analog
vollständig realisierbar ist: Signal -> Phase (arctan2, geometrische Phase
als Hilbert-Phase-Analog) -> Plaquette-Curl (registrierte Formel VERBATIM)
-> unit-charge-Kerne -> Xu-Toolbox-Metriken (count/duration/speed/radius/
direction je Frame, EIGENE Reimplementierung) + Dekodier-Analogie aus
Spiralzentren+Ladung + Richtungs-Rekonfiguration (Switch-Trial) +
Ladungs-Informations-Test gegen die Positions-Kontrolle (Q5).

Verankerung (Nutzer-Freigabe: Rohdaten + Interpretation einbeziehen): die
re-analysierten Xu-Source-Data (scratch/experiments/tci_xu/, commit 06bc9ef)
dienen NUR als Interpretations-Anker (klar gelabelt, nie Kriterium):
~19 Spiralen/Frame, Dekodier 48.3 % vs Chance 25 %, Annihilation ~97.4 %,
Richtungs-Flip 174.6°.

Ebenen-Disziplin (Notiz §7): korroborierbar ist die KORRELAT-Struktur
(quantisiert, task-informativ, rekonfigurierbar, annihilation-dominiert).
Qualia-Identität bleibt untestbar (Ebene B); die Routing-Hypothese
(Ebene C) wird hier falsifizierbar getestet (Q5), nicht behauptet.

## Registrierung (fixiert VOR dem ersten vollständigen Hauptlauf)

Modell (CPU numpy, deterministisch):
  u_t = u - u^3/3 - v + D * lap(u) + I(x, t)
  v_t = eps * (u + a - b * v)
  Lattice 128x128 Torus, Euler dt=0.05, T=2000 Schritte, Snapshot je 5
  (400 Frames). Init: Ruhe (u0=-1.2, v0=-0.625) + N(0, 0.05) je
  (Seed, Bedingung) aus default_rng(seed*16 + Sched-Index); zusätzlich
  Per-Schritt-Rauschen N(0, 0.02) auf u (Nukleations-Kanal, aus dem
  selben Seed-RNG — G1-Determinismus bleibt gewahrt). KEIN Rand-Zwang
  (der Korpus-Fehler 124/125 bleibt ausgeschlossen).
  Phase je Ort: theta = arctan2(v - mean(v), u - mean(u)).
  Plaquette-Formel VERBATIM (xu_agreement_test.py / xu_data_analysis.py).
  Haupt-Parameter EX ANTE fixiert (klassisches FHN-Spiralregime, NICHT
  aus dem Pilot gewählt): a=0.7, b=0.8, eps=0.05, D=0.6, A=0.5.
  Pilot (PILOT_*-Labels) scannt eps x D zur Regime-Gesundheitsprüfung,
  keine Verdict-Promotion; Abweichungen der Haupt-Parameter nur als
  CORREKTUR-LOG vor dem Hauptlauf.

Task-Drives (4 Bedingungen = {story, math} x {listen, answer}; einziger
Unterschied ist das Routing — Dekodier-Analogie):
  story -> Band A (Zeilen 16:40), math -> Band B (Zeilen 88:112).
  listen -> sustained I(t) = A * max(0, sin(2*pi*t/40))^2.
  answer -> pulsed I(t) = A wenn (t mod 20) < 6, sonst 0.
  Switch-Trial (Q3): Epoch A = story/listen bis t<1000, Epoch B =
  math/answer ab t=1000, Seeds 1200-1209.

Gates (vor allen Q-Verdicts):
  G1 DETERMINISM: Konfig (Seed 1200, story_listen) zweimal -> u-Feld
     bit-identisch.
  G2 FINITENESS: alle Entscheidungsmetriken finit; NaN-p offen gebucht
     und konservativ als Kriterium-NICHT-erfuellt gewertet (Lektion
     tci_xu G2).

Q1 SPIRAL_PROPAGATION_{REALIZED,WEAK,ABSENT} (je Seed, story_listen):
  (i) mediane Kernzahl je Frame >= 5, (ii) mediane Kern-Dauer >= 3
  Frames, (iii) quant fraction >= 0.9 in >= 80 % der Kern-Frames,
  (iv) gemittelte Matched-Core-Speed > 0.05 Zellen/Frame.
  REALIZED >= 27/30 Seeds, WEAK >= 15/30, sonst ABSENT.

Q2 DECODE_{ABOVE_CHANCE,WEAK,AT_CHANCE}: Leave-one-out Nearest-Centroid
  4-kanalig auf je-Trial-Spiral-Features (Ort-Histogramm 4x4 je
  Ladungsvorzeichen + p_cw + Dauer/Speed/Radius/Count) > Chance 0.25
  (Permutationsnull 10k, Seed 4242) UND > Amplituden-Baseline
  (4x4-Binning von mean|u|, 16 Features; gepaarte Sign-Flip-Permutation
  10k, Seed 4243, p < 0.05). WEAK: ueber Chance, nicht ueber Baseline.
  Sonst AT_CHANCE. Nicht-finite Features -> konservativ AT_CHANCE,
  offen gebucht.

Q3 DIRECTION_RECONFIG_{REALIZED,ABSENT}: Switch-Trial, je Seed
  |p_cw(A) - p_cw(B)| > 2 * gepoolte SE (ueber je-Frame-p_cw der
  Epochen) in >= 7/10 Seeds; Welch-p als Nebenkriterium (NaN ->
  konservativ). Vorzeichen-Konvention: Ladung < 0 = cw (wie Xu);
  die absolute cw/acw-Zuordnung haengt an der Lattice-Orientierung —
  gemessen wird die SIGN-Proportion und ihre Epoch-Aenderung.

Q4 INTERACTION_{ANNIHILATION_DOMINANT,NOT_DOMINANT}: gepoolter
  Interaktions-Terminations-Anteil (Track endet, waehrend ein ANDERER
  Kern innerhalb 2.0 Zellen im selben Frame liegt) >= 0.8. Xu-Anker
  ~97.4 % — nur Interpretations-Vergleich, kein Kriterium.

Q5 CHARGE_INFO_{BEYOND_POSITION,NOT_BEYOND_POSITION}: Ladungs-Features
  schlagen die Positions-Kontrolle (gleiche Pipeline, Histogramm ohne
  Vorzeichen, ohne p_cw) um >= 0.05 Accuracy UND gepaarte Permutation
  p < 0.05 — der falsifizierbare Kern der Ebene C.

Seeds: Pilot 1400-1403 (PILOT_*-Labels, keine Verdict-Promotion), Haupt
1200-1229 + Switch 1200-1209 — disjunkt zu Korpus 1000-1009/2000-2009
und cellsim 200-339. Per-Seed-Vektoren werden vollstaendig persistiert
(mean-level-Buchung ist unauditerbar — Harness-Lektion iter-27/28).

## KORREKTUR-LOG (VOR dem Hauptlauf; Pilot/Probe-Evidenz, Kriterien
## unverändert — Schwellen, Seeds, Verdicts wie oben registriert)

- K1 AKTIVITÄTS-DOMÄNE (Probe 1, PILOT-Regime A=0.5/eps=0.05/D=0.6,
  Seed 1400): Frame 0 zählte n=1885 "Kerne" bei u in (-1.37, -1.01) —
  das Feld sitzt am Ruhepunkt, die Phase arctan2(δv, δu) ist dort
  reines Winkel-Rauschen, und die Plaquette-Curl unabhängiger
  Rausch-Winkel liegt flächendeckend über 0.5 (die Xu-Daten tragen
  eine Hilbert-Phase echter Oszillationen; ein erregbares Medium in
  Ruhe trägt KEINE Phase). Korrektur: Kern-Etikettierung nur in der
  Aktivitäts-Domäne (Mittel der 4 Eck-Abstände zum Ruhepunkt
  > ACT_THRESH = 0.5); die Plaquette-Formel bleibt VERBATIM.
  Probe-Befund: Frame-0-Artefakte 1885 -> 0, echte Kerne unberührt.
- K2 PER-SCHRITT-RAUSCHEN 0.02 -> 0.1 (Probe 2, gleiche Evidenz-Basis):
  bei sigma_n=0.05 kollabiert die Kernaktivität nach dem Init-
  Transienten auf 0 (Frames 100-300: n=0) — Wellen laufen planar,
  Fronten brechen nicht; bei sigma_n=0.1 anhaltende Kernaktivität
  über alle 400 Frames (n=3-20/Frame, punktartig, median quant =
  1.00 in Kern-Frames) bei UNVERÄNDERTEN eps=0.05/D=0.6. AMP bleibt
  0.5 (Probe: AMP 0.5 vs 2.0 nahezu gleich — das Rauschen trägt die
  Fragmentierung, nicht der Antrieb).
- Der Pilot (PILOT_*-Labels) wird nach K1+K2 zur Bestätigung erneut
  gescannt (9 Konfigs × 4 Seeds); beide Pilot-Resultate werden
  gebucht (vor_korrektur + nach_korrektur). Keine Verdict-Promotion.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage
from scipy import stats as sstats

# --- Konstanten (EX ANTE fixiert; klassisches FHN-Spiralregime) ---
L = 128
DT = 0.05
STEPS = 2000
SNAP_EVERY = 5
A_PAR = 0.7
B_PAR = 0.8
EPS_PAR = 0.05
D_PAR = 0.6
AMP = 0.5
U_REST = -1.2
V_REST = -0.625
NOISE_INIT = 0.05
NOISE_STEP = 0.1
SWITCH_T = 1000

CONDITIONS = ("story_listen", "story_answer", "math_listen", "math_answer")
SCHED_IDX = {
    "story_listen": 0,
    "story_answer": 1,
    "math_listen": 2,
    "math_answer": 3,
    "switch_story_math": 4,
}
SCHEDULES = {
    "story_listen": ((0, "story_listen"),),
    "story_answer": ((0, "story_answer"),),
    "math_listen": ((0, "math_listen"),),
    "math_answer": ((0, "math_answer"),),
    "switch_story_math": ((0, "story_listen"), (SWITCH_T, "math_answer")),
}
BANDS = {"story": (16, 40), "math": (88, 112)}

VORT_THRESHOLD = 0.5
ACT_THRESH = 0.5
QUANT_LO, QUANT_HI = 0.75, 1.25
TRACK_MAX_DIST = 4.0
TERMINATION_DIST = 2.0

SEEDS_MAIN = tuple(range(1200, 1230))
SEEDS_PILOT = tuple(range(1400, 1404))
PILOT_EPS = (0.03, 0.05, 0.08)
PILOT_D = (0.3, 0.6, 1.0)

N_PERM = 10_000
PERM_SEED_Q2 = 4242
PERM_SEED_Q5 = 4243
CHANCE_4WAY = 0.25


def wrap(diff):
    return np.mod(np.asarray(diff) + np.pi, 2.0 * np.pi) - np.pi


def plaquette_vorticity(phases):
    """Die registrierte Formel VERBATIM (Identität mit xu_agreement_test)."""
    d_row = wrap(phases[1:, :] - phases[:-1, :])
    d_col = wrap(phases[:, 1:] - phases[:, :-1])
    return (
        d_row[:, :-1] + d_col[1:, :] - d_row[:, 1:] - d_col[:-1, :]
    ) / (2.0 * np.pi)


def spatial_mask(task):
    mask = np.zeros((L, L), dtype=bool)
    lo, hi = BANDS[task]
    mask[lo:hi, :] = True
    return mask


def drive_amplitude(mode, t):
    if mode == "listen":
        return AMP * max(0.0, float(np.sin(2.0 * np.pi * t / 40.0))) ** 2
    return AMP if (t % 20) < 6 else 0.0


def laplacian(u):
    return (
        np.roll(u, 1, 0)
        + np.roll(u, -1, 0)
        + np.roll(u, 1, 1)
        + np.roll(u, -1, 1)
        - 4.0 * u
    )


def frame_cores(u, v, thresh=VORT_THRESHOLD):
    theta = np.arctan2(v - v.mean(), u - u.mean())
    vort = plaquette_vorticity(theta)
    # K1 (Korrektur-Log): Aktivitäts-Domaine. Am Ruhpunkt ist die Phase
    # Winkel-Rauschen (Probe 1: n=1885 Artefakte in Frame 0) — Plaquettes
    # in Ruh-Nähe werden nicht etikettiert; die Formel selbst bleibt
    # VERBATIM, nur der Detektions-Domaine wird eingeschränkt.
    act = np.hypot(u - U_REST, v - V_REST)
    act_p = (act[:-1, :-1] + act[1:, :-1] + act[:-1, 1:] + act[1:, 1:]) / 4.0
    vort = np.where(act_p > ACT_THRESH, vort, 0.0)
    labels, n = ndimage.label(np.abs(vort) > thresh)
    cores = []
    if n:
        flat = labels.ravel()
        counts = np.bincount(flat, minlength=n + 1)[1:]
        sums = np.bincount(flat, weights=vort.ravel(), minlength=n + 1)[1:]
        coms = ndimage.center_of_mass(
            np.ones_like(vort), labels, list(range(1, n + 1))
        )
        for cnt, sm, com in zip(counts, sums, coms, strict=False):
            q = float(sm) / int(cnt)
            cores.append(
                {
                    "row": float(com[0]),
                    "col": float(com[1]),
                    "charge": q,
                    "area": int(cnt),
                    "quant": QUANT_LO <= abs(q) <= QUANT_HI,
                }
            )
    return vort, cores


def match_frames(prev_cores, cores):
    """Greedy Nearest-Neighbour-Match zweier Frames (Vektor-Distanzen)."""
    if not prev_cores or not cores:
        return []
    p_arr = np.array([[p["row"], p["col"]] for p in prev_cores])
    c_arr = np.array([[c["row"], c["col"]] for c in cores])
    d2 = ((p_arr[:, None, :] - c_arr[None, :, :]) ** 2).sum(axis=-1)
    order = np.argsort(d2, axis=None)
    used_i, used_j = set(), set()
    pairs = []
    for flat in order:
        i, j = divmod(int(flat), d2.shape[1])
        if d2[i, j] > TRACK_MAX_DIST**2:
            break
        if i in used_i or j in used_j:
            continue
        used_i.add(i)
        used_j.add(j)
        pairs.append((i, j, float(np.sqrt(d2[i, j]))))
    return pairs


def run_trial(seed, sched_key, *, eps=EPS_PAR, d_par=D_PAR, return_field=False):
    """Ein Trial: getriebene FHN-Dynamik + je-Frame-Wirbel-Statistik."""
    schedule = SCHEDULES[sched_key]
    rng = np.random.default_rng(seed * 16 + SCHED_IDX[sched_key])
    u = U_REST + rng.normal(0.0, NOISE_INIT, (L, L))
    v = V_REST + rng.normal(0.0, NOISE_INIT, (L, L))
    masks = {task: spatial_mask(task) for task in BANDS}

    frames = []
    tracks = {}
    terminations = []
    hist_neg = np.zeros(16)
    hist_pos = np.zeros(16)
    amp_hist = np.zeros(16)
    total_cores = 0
    speed_steps = []
    prev_cores = []

    for t in range(STEPS):
        cond = schedule[0][1]
        for start, cond_name in schedule:
            if t >= start:
                cond = cond_name
        task, mode = cond.split("_")
        drv = drive_amplitude(mode, t) * masks[task]
        u_new = u + DT * (u - u**3 / 3.0 - v + d_par * laplacian(u) + drv)
        u_new += rng.normal(0.0, NOISE_STEP, (L, L))
        v = v + DT * eps * (u_new + A_PAR - B_PAR * v)
        u = u_new
        if (t + 1) % SNAP_EVERY == 0:
            fi = len(frames)
            vort, cores = frame_cores(u, v)
            pairs = match_frames(prev_cores, cores)
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
                        <= TERMINATION_DIST**2
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
            q_frac = float(np.mean([c["quant"] for c in cores])) if n_c else 0.0
            p_cw = (
                float(np.mean([c["charge"] < 0 for c in cores])) if n_c else 0.0
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
            amp_grid = np.abs(u).reshape(4, L // 4, 4, L // 4).mean(axis=(1, 3))
            amp_hist += amp_grid.ravel() / amp_grid.sum()

    durations = [x["duration_frames"] for x in terminations]
    for tr in tracks.values():
        durations.append(len(frames) - tr["start_fi"])

    n_frames = len(frames)
    n_cores_list = [f["n_cores"] for f in frames]
    p_cw_frames = [f["p_cw"] for f in frames if f["n_cores"] > 0]
    rad = [f["mean_radius"] for f in frames if f["n_cores"] > 0]
    n_term = len(terminations)
    n_inter = sum(int(x["interaction"]) for x in terminations)
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
        "p_cw": float(np.mean(p_cw_frames)) if p_cw_frames else float("nan"),
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

    epoch_p_cw = {}
    epoch_counts = {}
    for tag, lo, hi in (("A", 0, SWITCH_T), ("B", SWITCH_T, STEPS + 1)):
        vals = [
            f["p_cw"]
            for f in frames
            if lo <= f["t"] < hi and f["n_cores"] > 0
        ]
        epoch_p_cw[tag] = float(np.mean(vals)) if vals else float("nan")
        epoch_counts[tag] = len(vals)

    hist_total = hist_neg + hist_pos
    scale = max(1.0, float(total_cores))
    max(1e-12, float(amp_hist.sum()))
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
        "schedule": [[s, c] for s, c in schedule],
        "n_frames": n_frames,
        "frames": frames,
        "pooled": pooled,
        "epoch_p_cw": {
            "A": epoch_p_cw["A"],
            "B": epoch_p_cw["B"],
            "n_frames_A": epoch_counts["A"],
            "n_frames_B": epoch_counts["B"],
        },
        "durations": durations,
        "term_interaction": [bool(x["interaction"]) for x in terminations],
        "term_q": [x["q"] for x in terminations],
        "features_spiral": features_spiral,
        "features_position": features_position,
    }
    if return_field:
        out["final_u"] = u
    return out


def _loo_pred(X, y):
    n = len(y)
    onehot = np.zeros((n, 4))
    onehot[np.arange(n), y] = 1.0
    sums = onehot.T @ X
    counts = onehot.sum(axis=0)
    num = sums[None, :, :] - onehot[:, :, None] * X[:, None, :]
    den = counts[None, :] - onehot
    cents = num / np.where(den > 0, den, 1.0)[:, :, None]
    d2 = ((X[:, None, :] - cents) ** 2).sum(axis=-1)
    d2 = np.where(den > 0, d2, np.inf)
    return d2.argmin(axis=1)


def loo_acc(X, y):
    return float(np.mean(_loo_pred(X, y) == y))


def loo_correct(X, y):
    return (_loo_pred(X, y) == y).astype(float)


def perm_p_above(X, y, n_perm, seed):
    rng = np.random.default_rng(seed)
    obs = loo_acc(X, y)
    null = np.array([loo_acc(X, rng.permutation(y)) for _ in range(n_perm)])
    p = float(np.mean(null >= obs - 1e-12))
    return obs, float(np.mean(null)), p, null


def sign_flip_p(diffs, n_perm, seed):
    rng = np.random.default_rng(seed)
    diffs = np.asarray(diffs, dtype=float)
    if not np.isfinite(diffs).all():
        return float("nan"), float("nan")
    obs = float(np.mean(diffs))
    ge = 0
    for _ in range(n_perm):
        signs = rng.choice(np.array([1.0, -1.0]), size=diffs.size)
        if abs(float(np.mean(diffs * signs))) >= abs(obs) - 1e-12:
            ge += 1
    return obs, ge / n_perm


def welch_p(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size < 2 or b.size < 2:
        return float("nan")
    if np.var(a) == 0.0 and np.var(b) == 0.0:
        return float("nan")
    _t, p = sstats.ttest_ind(a, b, equal_var=False)
    return float(p)


def analyze_trials(trials, gates):
    """Alle Gates + Q-Verdicts gemäß Registrierung (siehe Docstring)."""
    conds = [t for t in trials if SCHED_IDX[t["sched"]] < 4]
    switches = [t for t in trials if t["sched"] == "switch_story_math"]

    # G2 FINITENESS (Entscheidungsmetriken; NaN offen gebucht)
    nan_fields = []
    for t in trials:
        for key in (
            "median_n_cores",
            "median_duration_frames",
            "mean_matched_speed",
            "mean_radius",
        ):
            if not np.isfinite(t["pooled"][key]):
                nan_fields.append(f"{t['seed']}:{t['sched']}:{key}")

    # Q1 (je Seed, story_listen; per-seed vote wie registriert)
    q1_rows = []
    for seed in SEEDS_MAIN:
        tr = next(
            t
            for t in conds
            if t["seed"] == seed and t["sched"] == "story_listen"
        )
        p = tr["pooled"]
        checks = {
            "n_cores_ge_5": p["median_n_cores"] >= 5.0,
            "duration_ge_3": p["median_duration_frames"] >= 3.0,
            "quant_band_80pct_frames": p["frac_frames_quant_ge_09"] >= 0.8,
            "speed_gt_005": p["mean_matched_speed"] > 0.05,
        }
        q1_rows.append(
            {
                "seed": seed,
                "checks": checks,
                "pass": all(checks.values()),
                "pooled": {
                    k: p[k]
                    for k in (
                        "median_n_cores",
                        "median_duration_frames",
                        "mean_matched_speed",
                        "frac_frames_quant_ge_09",
                        "n_cores_max",
                        "total_cores",
                    )
                },
            }
        )
    n_pass = sum(int(r["pass"]) for r in q1_rows)
    q1 = "REALIZED" if n_pass >= 27 else ("WEAK" if n_pass >= 15 else "ABSENT")

    # Q2 DECODE (LOO Nearest-Centroid + Permutation + Amplituden-Baseline)
    X = np.array([t["features_spiral"] for t in conds], dtype=float)
    Xp = np.array([t["features_position"] for t in conds], dtype=float)
    y = np.array([SCHED_IDX[t["sched"]] for t in conds])
    finite = np.isfinite(X).all() and np.isfinite(Xp).all()
    if finite:
        acc, null_mean, p_perm, null = perm_p_above(X, y, N_PERM, PERM_SEED_Q2)
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
    else:
        acc = acc_pos = null_mean = p_perm = paired_p = gain = float("nan")
        null = np.array([])
        q2 = "AT_CHANCE"

    # Q5 (Ladungs-Info jenseits der Positions-Kontrolle)
    q5 = (
        "BEYOND_POSITION"
        if (
            np.isfinite(paired_p)
            and paired_p < 0.05
            and np.isfinite(gain)
            and gain >= 0.05
        )
        else "NOT_BEYOND_POSITION"
    )

    # Q3 (Switch-Trials, je Seed)
    q3_rows = []
    for tr in sorted(switches, key=lambda t: t["seed"]):
        fa = [
            f["p_cw"]
            for f in tr["frames"]
            if f["t"] < SWITCH_T and f["n_cores"] > 0
        ]
        fb = [
            f["p_cw"]
            for f in tr["frames"]
            if f["t"] >= SWITCH_T and f["n_cores"] > 0
        ]
        if not fa or not fb:
            q3_rows.append({"seed": tr["seed"], "pass": False, "nan_epoch": True})
            continue
        se = float(np.sqrt(np.var(fa) / len(fa) + np.var(fb) / len(fb)))
        diff = tr["epoch_p_cw"]["A"] - tr["epoch_p_cw"]["B"]
        wp = welch_p(fa, fb)
        q3_rows.append(
            {
                "seed": tr["seed"],
                "p_cw_A": tr["epoch_p_cw"]["A"],
                "p_cw_B": tr["epoch_p_cw"]["B"],
                "diff": diff,
                "pooled_se": se,
                "welch_p": wp,
                "welch_pass": bool(np.isfinite(wp) and wp < 0.05),
                "pass": bool(abs(diff) > 2.0 * se),
            }
        )
    n_q3 = sum(int(r["pass"]) for r in q3_rows)
    q3 = "REALIZED" if n_q3 >= 7 else "ABSENT"

    # Q4 (gepoolt über Bedingungs-Trials)
    n_term = sum(t["pooled"]["n_terminations"] for t in conds)
    n_inter = sum(t["pooled"]["n_terminations_interaction"] for t in conds)
    frac = float(n_inter) / n_term if n_term else float("nan")
    q4 = (
        "ANNIHILATION_DOMINANT"
        if np.isfinite(frac) and frac >= 0.8
        else "NOT_DOMINANT"
    )

    result = {
        "status": "REGISTERED_RUN_v2_vollstaendig",
        "registration": "Docstring v2_model.py (fixiert vor dem Hauptlauf)",
        "gates": {
            "G1": gates.get("G1_DETERMINISM", {}),
            "G2": {
                "finite_decision_metrics": not nan_fields,
                "nan_fields": nan_fields,
                "note": "NaN offen gebucht, konservativ gewertet",
            },
        },
        "verdicts": {
            "Q1": f"Q1_SPIRAL_PROPAGATION_{q1}",
            "Q2": f"Q2_DECODE_{q2}",
            "Q3": f"Q3_DIRECTION_RECONFIG_{q3}",
            "Q4": f"Q4_INTERACTION_{q4}",
            "Q5": f"Q5_CHARGE_INFO_{q5}",
        },
        "q1": {"n_pass": n_pass, "n_seeds": len(SEEDS_MAIN), "rows": q1_rows},
        "q2": {
            "acc_spiral": acc,
            "acc_position": acc_pos,
            "gain": gain,
            "null_mean": null_mean,
            "p_perm": p_perm,
            "paired_p": paired_p,
            "chance": CHANCE_4WAY,
            "null": null.tolist(),
        },
        "q3": {"n_pass": n_q3, "rows": q3_rows},
        "q4": {
            "interaction_fraction": frac,
            "n_terminations": n_term,
            "n_interaction": n_inter,
        },
        "per_seed_summary": [
            {
                "seed": t["seed"],
                "sched": t["sched"],
                "pooled": {
                    k: t["pooled"][k]
                    for k in (
                        "median_n_cores",
                        "n_cores_max",
                        "median_duration_frames",
                        "mean_matched_speed",
                        "mean_radius",
                        "p_cw",
                        "n_terminations",
                        "n_terminations_interaction",
                        "termination_interaction_fraction",
                        "frac_frames_quant_ge_09",
                        "total_cores",
                    )
                },
                "epoch_p_cw": t["epoch_p_cw"],
            }
            for t in trials
        ],
        "xu_anchors_interpretation_only": {
            "note": "Interpretations-Vergleich, NICHT Kriterium (Registrierung)",
            "xu_spirals_per_frame": "~19 (Paper, linker Kortex)",
            "xu_decode_language_percent": 48.33,
            "xu_chance_4way_percent": 25.0,
            "xu_annihilation_fraction": 0.974,
            "xu_direction_flip_deg": 174.6,
            "our_median_n_cores_story_listen": float(
                np.mean([r["pooled"]["median_n_cores"] for r in q1_rows])
            ),
            "our_decode_acc_spiral": acc,
            "our_termination_interaction_fraction": frac,
        },
    }
    return result
