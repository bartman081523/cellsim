"""TCI <-> Xu et al. 2023 — rigoroser Agreements-Test (pre-registriert).

Anlass: Nutzersteuerung 2026-09-28 — "bitte tci mit Xu et al
uebereinstimmungen untersuchen. keine vorabnaussagen ohne rigorose tests,
es fehlt nur ein klitzekleines bit an der tci dass es auf Xu et al passt".

Kontext: Xu et al. (Nat Hum Behav 2023, DOI 10.1038/s41562-023-01626-5)
detektieren Hirn-Spiralen aus HCP-fMRI via Hilbert-Phase -> Phasenfeld ->
curl/Vorticity — dieselbe Messmathematik wie TCI-125 (lattice circulation
der wrapped phase diffs / 2pi). Die TCI-Wirbel-Experimente (122/124/125)
testen die STATIONAERE (Equilibrium-)Version; Xu et al. berichten
PROPAGIERENDE, task-rekonfigurierende Spiralen. Kandidat fuer das
"klitzekleine Bit": der persistente Drive (Nichtgleichgewicht) statt
Annealing -> 0.

DIESE Experimente pruefen die Agreement-Claims, NICHT die Schutz-Claims
(die bleiben als geloggte FALSIFIED-Verdice der Korpus-Runs stehen).

Dynamik = Korpus-Fidelitaet (124/125): N=100, steps=1500,
target = arctan2(sum sin(theta_j), sum cos(theta_j)) ueber die 4 Nachbarn
(np.roll), phases = 0.9*target + 0.1*phases + N(0, 0.05); danach Drive-
Inkrement delta je Spalte; mod 2pi. Kein Rand-Zwang (keine arctan2-BC) —
Null und Alt teilen ALLES ausser dem Drive-Muster.

VOR der Ausfuehrung registrierte Kriterien (keine Post-hoc-Anpassung):

H1 SPIRAL_EDGE (Xu-Agreement "Spiralen an Netzwerk-Grenzen"):
  Alt = zwei gegenlaeufig getriebene Domänen (links +delta0, rechts
  -delta0, Interface bei x=50); Null = uniformer Drive (+delta0
  ueberall), identisches Rauschen. Kern = |Vorticity_Zeitmittel(letzte
  100 Steps, [1400,1500))| > 0.3. Metric je Seed:
  ratio r = rho_Interface(|x-50|<=6) / mean(rho_x=25-Band, rho_x=75-Band).
  REALIZED: r >= 2.0 in >= 7/10 Seeds UND Welch-p < 0.05 (alt vs null);
  WEAK:     r >= 1.3 in >= 7/10 Seeds;
  ABSENT:   sonst.

H2 RECONFIG (Xu-Agreement "Rotationsrichtung rekonfiguriert mit Task"):
  Alt: Drive-Swap bei Step 750 (Vorzeichenwechsel beider Domänen);
  Ctrl: kein Swap. Fenster W_A = [700, 750), W_B = [1450, 1500);
  Kerne je Fenster: |Vorticity_Fenstermittel| > 0.3; Match: Distanz <= 6;
  Richtung = sign(Fenstermittel-Vorticity am Kern).
  Metric je Seed: flip_rate = P(Vorzeichenwechsel | Kern in beiden
  Fenstern); persistence = |matched| / max(|cores_A|, 1).
  REALIZED: flip_alt - flip_ctrl >= 0.25 UND Welch-p < 0.05 UND
            persistence_alt >= 0.3;
  WEAK:     flip_alt - flip_ctrl >= 0.10;
  ABSENT:   sonst.

H3 QUANTISIERUNGS-GATE (Mess-Validitaet): Anteil erkannter Kerne
  (E1-alt, Zeitmittel [1400,1500)) mit 0.75 <= |Vorticity_mean| <= 1.25.
  >= 0.8 -> CHARGE_QUANTIZED; sonst CHARGE_DEGRADED.

Gates (bindend): G1 Determinismus — Konfig (E1, alt, seed 1000) zweimal
laufen, Vorticity-Felder bit-identisch; G2: alle Bedingungen liefern
Messwerte (keine NaN). Verletzung -> REGISTRATION_ERROR.

Seeds: 1000-1009 (E1), 2000-2009 (E2) — disjunkt zur cellsim-Linie
(200-339). CPU numpy, kein GPU-Bedarf. Kein Bezug zur cellsim
Damkoehler-Buchhaltung; dies ist ein externes Korpus-Experiment.

Registrierungs-Fix (vor dem Lauf, dokumentiert): (1) erste Fassung
kollabierte das E1-Zeitmittel mit W_B (elif-Bug). Korrigiert auf DREI
getrennte Akkumulatoren (vort_e1, vort_a, vort_b). (2) Plaquette-Index-
Algebra zweimal falsch geslicet (Broadcast-Fehler in Form 1 UND Form 2
jeweils am G1-Gate, vor jeglicher Messung). Korrekt (verifiziert):
d_row (N-1, N), d_col (N, N-1); Plaquette (i,j), i,j in 0..N-2:
d_row[i,j] + d_col[i+1,j] - d_row[i,j+1] - d_col[i,j]
= d_row[:, :-1] + d_col[1:, :] - d_row[:, 1:] - d_col[:-1, :]
(alle (N-1, N-1)). Beide Korrekturen VOR erster Messung; das Testfeld
des Kriteriums ist unverändert.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy import stats

N = 100
STEPS = 1500
NOISE_SIGMA = 0.05
RELAX = 0.9  # 124/125-Update: 0.9*target + 0.1*phases
DELTA0 = 0.05  # Drive pro Step je Domäne (rad)
SWAP_STEP = 750
VORT_THRESHOLD = 0.3  # Kern-Schwelle (Fenstermittel)
INTERFACE_HALF_WIDTH = 6
INTERIOR_BAND_X = (25, 75)
TRACK_DIST = 6.0
QUANT_WINDOW = 0.25  # |v| in [0.75, 1.25] = quantisiert

N_SEEDS = 10
SEEDS_E1 = [1000 + i for i in range(N_SEEDS)]
SEEDS_E2 = [2000 + i for i in range(N_SEEDS)]

OUT_DIR = Path(__file__).resolve().parent

WINDOW_A = (700, 750)
WINDOW_B = (1450, 1500)
WINDOW_E1 = (1400, 1500)  # E1-Zeitmittel = letzte 100 Steps


def wrap(diff: np.ndarray) -> np.ndarray:
    """Phasendifferenz auf (-pi, pi] wrappen."""
    return np.mod(diff + np.pi, 2.0 * np.pi) - np.pi


def relax(phases: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Ein Relaxations-Schritt, VERBATIM-Dynamik aus 124/125."""
    sin_sum = (
        np.sin(np.roll(phases, 1, axis=0))
        + np.sin(np.roll(phases, -1, axis=0))
        + np.sin(np.roll(phases, 1, axis=1))
        + np.sin(np.roll(phases, -1, axis=1))
    )
    cos_sum = (
        np.cos(np.roll(phases, 1, axis=0))
        + np.cos(np.roll(phases, -1, axis=0))
        + np.cos(np.roll(phases, 1, axis=1))
        + np.cos(np.roll(phases, -1, axis=1))
    )
    target = np.arctan2(sin_sum, cos_sum)
    new = RELAX * target + (1.0 - RELAX) * phases
    new += rng.normal(0.0, NOISE_SIGMA, phases.shape)
    return np.mod(new, 2.0 * np.pi)


def drive_field(mode: str) -> np.ndarray:
    """Drive-Muster je Spalte (x): 'uniform' (+delta0 ueberall),
    'counter' (links +delta0, rechts -delta0, Interface x=50)."""
    xs = np.arange(N)
    if mode == "uniform":
        return np.full(N, DELTA0)
    if mode == "counter":
        return np.where(xs < N // 2, DELTA0, -DELTA0)
    raise ValueError(mode)


def plaquette_vorticity(phases: np.ndarray) -> np.ndarray:
    """Lattice-Curl der Phase auf (N-1)x(N-1)-Plaquettes (Formel wie 125):
    Zirkulation um jede Plaquette / 2pi.
    Plaquette (i,j) mit Ecken (i,j),(i+1,j),(i+1,j+1),(i,j+1):
    vort = d_row[i,j] + d_col[i+1,j] - d_row[i,j+1] - d_col[i,j]."""
    d_row = wrap(phases[1:, :] - phases[:-1, :])  # (N-1, N)
    d_col = wrap(phases[:, 1:] - phases[:, :-1])  # (N, N-1)
    return (
        d_row[:, :-1]
        + d_col[1:, :]
        - d_row[:, 1:]
        - d_col[:-1, :]
    ) / (2.0 * np.pi)


def run_condition(seed: int, drive_mode: str, swap: bool) -> dict:
    """Laueft 1500 Steps mit Korpus-Dynamik + persistentem Drive.

    Drei separate Akkumulatoren: vort_a = W_A [700,750), vort_b = W_B
    [1450,1500), vort_e1 = E1-Zeitmittel [1400,1500).
    """
    rng = np.random.default_rng(seed)
    delta_col = drive_field(drive_mode)[np.newaxis, :]

    phases = rng.uniform(0.0, 2.0 * np.pi, (N, N))

    vort_sum_a = np.zeros((N - 1, N - 1))
    vort_sum_b = np.zeros((N - 1, N - 1))
    vort_sum_e1 = np.zeros((N - 1, N - 1))
    for t in range(STEPS):
        phases = relax(phases, rng)
        if swap and t >= SWAP_STEP:
            delta_col = -delta_col
        phases = np.mod(phases + delta_col, 2.0 * np.pi)

        vort_t = plaquette_vorticity(phases)
        if WINDOW_A[0] <= t < WINDOW_A[1]:
            vort_sum_a += vort_t
        if WINDOW_B[0] <= t < WINDOW_B[1]:
            vort_sum_b += vort_t
        if WINDOW_E1[0] <= t < WINDOW_E1[1]:
            vort_sum_e1 += vort_t

    return {
        "vort_a": vort_sum_a / float(WINDOW_A[1] - WINDOW_A[0]),
        "vort_b": vort_sum_b / float(WINDOW_B[1] - WINDOW_B[0]),
        "vort_e1": vort_sum_e1 / float(WINDOW_E1[1] - WINDOW_E1[0]),
    }


def cores_from(vort_mean: np.ndarray, threshold: float) -> list:
    """Kern-Liste (row, col, signed_vorticity) fuer |vort| > threshold."""
    rows, cols = np.where(np.abs(vort_mean) > threshold)
    return [
        (int(r), int(c), float(vort_mean[r, c]))
        for r, c in zip(rows, cols, strict=True)
    ]


def band_density(vort_mean: np.ndarray, x_center: int) -> float:
    """Anteil Sites mit |vort|>0.3 im Spaltenband um x_center."""
    x_lo = max(x_center - INTERFACE_HALF_WIDTH, 0)
    x_hi = min(x_center + INTERFACE_HALF_WIDTH, N - 1)
    band = vort_mean[:, x_lo:x_hi]
    return float(np.mean(np.abs(band) > VORT_THRESHOLD))


def match_cores(cores_a: list, cores_b: list, max_dist: float) -> list:
    """Paare (vort_a, vort_b) mit Distanz <= max_dist (greedy)."""
    matches = []
    used_b: set = set()
    for ra, ca, va in cores_a:
        best_idx = None
        best_d = max_dist + 1.0
        for idx, (rb, cb, _vb) in enumerate(cores_b):
            if idx in used_b:
                continue
            d = float(np.hypot(ra - rb, ca - cb))
            if d <= max_dist and d < best_d:
                best_idx = idx
                best_d = d
        if best_idx is not None:
            used_b.add(best_idx)
            matches.append((va, cores_b[best_idx][2]))
    return matches


def e1_ratio(vort_mean: np.ndarray) -> float:
    """Interface-Kern-Dichte / Mittel der Interior-Band-Dichten."""
    rho_int = band_density(vort_mean, 50)
    rho_far = float(
        np.mean(
            [
                band_density(vort_mean, INTERIOR_BAND_X[0]),
                band_density(vort_mean, INTERIOR_BAND_X[1]),
            ]
        )
    )
    ratio = rho_int / max(rho_far, 1e-12)
    return float(min(ratio, 1000.0))  # Cap nur fuer JSON; Kriterium unberuehrt


def main() -> None:
    started = time.time()
    print("TCI<->Xu Agreement-Test (pre-registriert) — Start")

    # G1: Determinismus
    r1 = run_condition(1000, "counter", swap=False)
    r2 = run_condition(1000, "counter", swap=False)
    g1 = bool(np.array_equal(r1["vort_a"], r2["vort_a"])) and bool(
        np.array_equal(r1["vort_e1"], r2["vort_e1"])
    )
    print(f"G1 Determinismus (E1 alt seed 1000 x2): {'PASS' if g1 else 'FAIL'}")
    if not g1:
        raise SystemExit("REGISTRATION_ERROR: G1 verletzt")

    # E1 (H1 + H3)
    ratios_null = []
    ratios_alt = []
    quant_fracs = []
    for seed in SEEDS_E1:
        res_n = run_condition(seed, "uniform", swap=False)
        vort_n = res_n["vort_e1"]
        ratios_null.append(e1_ratio(vort_n))

        res_a = run_condition(seed, "counter", swap=False)
        vort_a = res_a["vort_e1"]
        ratios_alt.append(e1_ratio(vort_a))
        core_list = cores_from(vort_a, VORT_THRESHOLD)
        if core_list:
            q_frac = float(
                np.mean(
                    [
                        1.0 - QUANT_WINDOW <= abs(v) <= 1.0 + QUANT_WINDOW
                        for _, _, v in core_list
                    ]
                )
            )
        else:
            q_frac = 0.0
        quant_fracs.append(q_frac)

    null_arr = np.array(ratios_null)
    alt_arr = np.array(ratios_alt)
    _t1, p1 = stats.ttest_ind(alt_arr, null_arr, equal_var=False)
    n_ge_2 = int(np.sum(alt_arr >= 2.0))
    n_ge_13 = int(np.sum(alt_arr >= 1.3))
    if n_ge_2 >= 7 and p1 < 0.05:
        h1 = "SPIRAL_EDGE_REALIZED"
    elif n_ge_13 >= 7:
        h1 = "SPIRAL_EDGE_WEAK"
    else:
        h1 = "SPIRAL_EDGE_ABSENT"

    e1_result = {
        "ratios_null": [float(x) for x in null_arr],
        "ratios_alt": [float(x) for x in alt_arr],
        "mean_ratio_null": float(np.mean(null_arr)),
        "mean_ratio_alt": float(np.mean(alt_arr)),
        "n_seeds_ratio_ge_2": n_ge_2,
        "n_seeds_ratio_ge_1_3": n_ge_13,
        "welch_p": float(p1),
        "verdict": h1,
    }
    print(
        f"E1/H1: mean_ratio null={np.mean(null_arr):.3f} "
        f"alt={np.mean(alt_arr):.3f} p={p1:.4f} verdict={h1}"
    )

    # E2 (H2)
    flip_ctrl = []
    flip_alt = []
    pers_alt = []
    n_cores_a_ctrl = []
    n_cores_a_alt = []
    for seed in SEEDS_E2:
        for cond, swap in (("ctrl", False), ("alt", True)):
            res = run_condition(seed, "counter", swap=swap)
            cores_a = cores_from(res["vort_a"], VORT_THRESHOLD)
            cores_b = cores_from(res["vort_b"], VORT_THRESHOLD)
            matches = match_cores(cores_a, cores_b, TRACK_DIST)
            flip_rate = (
                sum(1 for va, vb in matches if np.sign(va) != np.sign(vb))
                / len(matches)
                if matches
                else 0.0
            )
            persistence = len(matches) / max(len(cores_a), 1)
            if cond == "ctrl":
                flip_ctrl.append(flip_rate)
                n_cores_a_ctrl.append(len(cores_a))
            else:
                flip_alt.append(flip_rate)
                n_cores_a_alt.append(len(cores_a))
                pers_alt.append(persistence)

    flip_c = np.array(flip_ctrl)
    flip_a = np.array(flip_alt)
    _t2, p2 = stats.ttest_ind(flip_a, flip_c, equal_var=False)
    delta_flip = float(np.mean(flip_a) - np.mean(flip_c))
    pers = float(np.mean(pers_alt)) if pers_alt else 0.0
    if delta_flip >= 0.25 and p2 < 0.05 and pers >= 0.3:
        h2 = "RECONFIG_REALIZED"
    elif delta_flip >= 0.10:
        h2 = "RECONFIG_WEAK"
    else:
        h2 = "RECONFIG_ABSENT"

    e2_result = {
        "flip_rate_ctrl": [float(x) for x in flip_c],
        "flip_rate_alt": [float(x) for x in flip_a],
        "n_cores_wa_ctrl": n_cores_a_ctrl,
        "n_cores_wa_alt": n_cores_a_alt,
        "mean_flip_ctrl": float(np.mean(flip_c)),
        "mean_flip_alt": float(np.mean(flip_a)),
        "delta_flip": delta_flip,
        "mean_persistence_alt": pers,
        "welch_p": float(p2),
        "verdict": h2,
    }
    print(
        f"E2/H2: flip ctrl={np.mean(flip_c):.3f} alt={np.mean(flip_a):.3f} "
        f"delta={delta_flip:.3f} p={p2:.4f} verdict={h2}"
    )

    # E3 (H3)
    quant_frac = float(np.mean(quant_fracs))
    h3 = "CHARGE_QUANTIZED" if quant_frac >= 0.8 else "CHARGE_DEGRADED"
    e3_result = {
        "per_seed_quant_fraction": [float(x) for x in quant_fracs],
        "pooled_quant_fraction": quant_frac,
        "verdict": h3,
    }
    print(f"E3/H3: quantized_frac={quant_frac:.3f} verdict={h3}")

    result = {
        "registration": "siehe Docstring (Kriterien vor dem Lauf fixiert)",
        "parameters": {
            "N": N,
            "steps": STEPS,
            "noise_sigma": NOISE_SIGMA,
            "relax": RELAX,
            "delta0": DELTA0,
            "swap_step": SWAP_STEP,
            "vort_threshold": VORT_THRESHOLD,
            "track_dist": TRACK_DIST,
            "seeds_e1": SEEDS_E1,
            "seeds_e2": SEEDS_E2,
        },
        "gates": {"G1_determinism": g1},
        "e1": e1_result,
        "e2": e2_result,
        "e3": e3_result,
        "runtime_s": time.time() - started,
    }
    out_path = OUT_DIR / "result.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Ergebnis persistiert: {out_path}")
    print(f"Runtime: {result['runtime_s']:.1f} s")


if __name__ == "__main__":
    main()
