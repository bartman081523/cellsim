"""Re-Analyse der Xu-et-al-2023 Source Data (EXPLORATORY_REANALYSIS).

Anlass: Nutzersteuerung — die echten Messdaten der Studien laden und
die Verbindung Qualia <-> Messdaten <-> TCI-Theorie ehrlich pruefen.
Die 17 xlsx (MOESM9-25) sind die publizierten Source Data (Fig 2-8 +
Extended Data 1-10), gespeichert unter data/:
https://media.springernature.com/full/springer-static/esm/
art%3A10.1038%2Fs41562-023-01626-5/MediaObjects/41562_2023_1626_MOESM{i}_ESM.xlsx

STATUS: EXPLORATORY_REANALYSIS — Post-hoc-Re-Analyse der publizierten
Zusammenfassungs-Daten. KEINE Promotion zu TCI-Verdicts (das
pre-registrierte Verdict-Buch der Korpus-Linie bleibt unberuehrt:
result.json mit H1/H2 ABSENT, H3 CHARGE_DEGRADED). Kriterien hier
VOR dem ersten Lauf fixiert; Labels X*_*.

VOR dem Lauf fixierte Kriterien:

X1 RICHTUNGS-FLIP (Fig_8b_right, single-trial phase vector angle,
  Math Listening vs Math Answering; Struktur vor dem Lauf verifiziert:
  733 Trials, Spalten 1-5 = Listening, 7-11 = Answering, je 5
  Zeit-Schritte, Winkel in [-pi, pi], Daten ab Zeile 3):
  pro Trial Kreis-Resultante der 5 Winkel -> Trial-Winkel theta_i;
  zirkulaeres Mittel + Resultantenlaenge R je Bedingung;
  flip = |wrap(circmean_answer - circmean_listen)|.
  Test: zirkulaerer Permutationstest (10 000 Shuffles der Bedingungs-
  labels, rng seed 42, Statistik = |wrap(Differenz der beiden
  zirkulaeren Mittel)|) — bewusst statt Watson-Williams (robust bei
  kleiner Resultantenlaenge, keine kappa-Approximation).
  X1_FLIP_REALIZED: flip > pi/2 UND p < 0.05 UND beide R >= 0.3;
  X1_FLIP_WEAK:     flip > pi/4 UND p < 0.05;
  X1_FLIP_ABSENT:   sonst.
  Zusatz (deskriptiv): Anteil positiver Winkel je Zeit-Schritt je
  Bedingung; Anteil Trials, deren 5 Steps konsistent in einer
  Halb-Ebene liegen.

X2 DEKODIER-STÄRKEN (Fig_6b Language, Fig_6c WM): Mittel + SEM ueber
  die 100 Iterationen (ZEILEN 2-101, siehe Korrektur-Log A); one-
  sample-t je Spalte gegen ihre registrierte Chance — Fig_6b: 0.5 je
  Spalte; Fig_6c: '4 stimulus types' 0.25, 'Memory Load' 0.5,
  'Memory Performance' 0.5 (PER-SPALTE, siehe Korrektur-Log B);
  Welch-t spiral-original vs unfiltered-amplitude (Language).
  Labels je Spalte: X2_ABOVE_CHANCE / X2_AT_CHANCE / X2_BELOW_CHANCE
  (zweiseitig p < 0.05).
  Zusaetzlich (POST-HOC, klar gelabelt, KEIN registriertes Kriterium):
  dieselben t-Tests gegen Chance-Alternative 0.25 fuer Fig_6b — weil
  die Klassifikations-Zielgroesse des Papers (2-Klassen Story/Math
  vs 4 Bedingungen Story/Math x Listen/Answer) aus den Sheets selbst
  nicht hervorgeht; der Paper-Text entscheidet die Lesart, nicht
  dieses Kriterium.

X3 INTERAKTIONS-TYPEN (Fig_4a): Mittel ueber Subjects je Typ
  (Full/Partial Annihilation, Repulsion) — deskriptiv; nur Zeilen mit
  numerischer Subject-Nr (Spalte 0) zaehlen (Summary-Zeilen raus).
  Cross-Check: Mittel der Zeilensummen (sollte ~1 sein, wenn die
  drei Typen pro Subject Anteile sind).

X4 EIGENE FORMEL AUF ECHTER PHASE (moesm21 Fig_6c_left/mid/right;
  Layout vor dem Lauf verifiziert: 176x251, Zellen = Werte ohne
  Header-Zeile, NaN-Rand):
  exakt die registrierte plaquette_vorticity aus xu_agreement_test.py
  (identische wrap()-Konvention, NaN-faehig: nur Plaquettes mit 4
  nicht-NaN Ecken zaehlen). Kern = |v| > 0.3 (Korpus-Schwelle);
  quant fraction = Anteil Kerne mit 0.75 <= |v| <= 1.25 (H3-Fenster).
  Je Map: n_cores, n_pos, n_neg, quant_frac, max|v|, p99|v|.

X5 RICHTUNGS-PROPORTIONEN (Fig_5a/b/c/d_4th): Mittel ueber Subjects
  (nur Zeilen mit numerischer Subject-Nr) je Spalte (clockwise/
  anticlockwise je Task-Epoch) — deskriptiv. Header-Labels via
  Text-Grid (Korrektur-Log A). Cross-Check: Element-Identitaet
  Fig_5a_4th Spalte 2 vs Fig_5b_4th Spalte 1 (beide 0.3237 im
  ersten Lauf — Klon-Verdacht).

Ausgabe: xu_data_result.json + Log auf stdout.

CORREKTUR-LOG (Daten-Extraktion; registrierte Kriteria selbst
unveraendert — ausser B, wo der CODE von der Registrierung abwich):

A. Nach dem ersten Lauf (2026-09-28), VOR Buchung: (1) X2 las
   col_from_rows(..., 3) — Iterationen 2-100 PLUS 'Iteration Mean'-
   Zeile PLUS 's.e.m.'-Zeile (Iteration 1 fehlte). Layout verifiziert:
   Zeile 2 = Iteration 1, Zeilen 2-101 = Iterationen 1-100, Zeile 102
   = 'Iteration Mean', Zeile 103 = 's.e.m.'. Jetzt: Datenzeilen
   explizit bis zur Mean-Zeile; gespeicherte Zeilen als Cross-Check.
   (2) Header-Labels wurden aus dem NUMERISCHEN Array gelesen
   (Text -> NaN -> leere Labels). Jetzt: Text-Grid via openpyxl.
   (3) X3 n=95 zaehlte 2 Nicht-Subject-Zeilen (label sagt n=93);
   gemessen: 100 Subject-Zeilen, 7 ohne Werte (16/28/62/75/77/90/100),
   93 mit allen 3 Spalten, Zeilensumme exakt 1.0. Jetzt: Subject-Filter.
   (4) X5: 5a/5c haben je 1 Summary-Zeile mit numerischen Werten ->
   Mittel kontaminiert. Jetzt: Subject-Filter.
B. Nach dem ersten Lauf, VOR Buchung: Fig_6c-Chancen waren im CODE
   pro-Sheet (0.25 fuer alle 3 Spalten), die registrierten Kriterien
   sagen PER-SPALTE (4-Typen 0.25, Load 0.5, Performance 0.5). Der
   erste Lauf testete Load/Performance gegen die falsche Chance.
   Korrigiert auf die registrierten per-Spalte-Chancen. Die
   registrierten Kriterien selbst wurden NICHT geaendert.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import openpyxl
from scipy import stats

OUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUT_DIR / "data"

QUANT_WINDOW = 0.25  # wie Registrierung: |v| in [0.75, 1.25]
CORE_THRESHOLD = 0.3  # wie Registrierung (xu_agreement_test.py)
FLIP_REALIZED = np.pi / 2.0
FLIP_WEAK = np.pi / 4.0
N_PERMUTATIONS = 10_000
PERM_SEED = 42

# Registrierte Chance-Levels (Docstring): Fig_6b Language 0.5 je Spalte;
# Fig_6c WM: 4 stimulus types 0.25, Memory Load 0.5, Performance 0.5.
CHANCE_BY_SHEET = {"Fig_6b": 0.5, "Fig_6c": None}  # None -> per Spalte
CHANCE_ALT_LANGUAGE = 0.25  # POST-HOC, klar gelabelt (2-Klassen-Alternative)


def load_grid(path: Path, sheet: str) -> np.ndarray:
    """Komplettes Sheet als float-Array (numerische Zellen, Rest -> nan)."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = []
    for row in ws.iter_rows(values_only=True):
        rows.append(
            [
                float(v)
                if isinstance(v, (int, float)) and not isinstance(v, bool)
                else np.nan
                for v in row
            ]
        )
    wb.close()
    width = max(len(r) for r in rows)
    return np.array([r + [np.nan] * (width - len(r)) for r in rows], dtype=float)


def load_text_grid(path: Path, sheet: str) -> list:
    """Komplettes Sheet als Roh-Liste — Strings bleiben erhalten."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    wb.close()
    width = max(len(r) for r in rows)
    return [r + [None] * (width - len(r)) for r in rows]


def _text(cell) -> str:
    return str(cell).strip() if cell is not None else ""


def col_from_rows(arr: np.ndarray, col: int, first: int) -> np.ndarray:
    """Numerische Zellen einer Spalte ab Zeile `first` (0-basiert)."""
    vals = arr[first:, col]
    return vals[~np.isnan(vals)]


def subject_column(
    arr: np.ndarray, col: int, first: int
) -> tuple[np.ndarray, int]:
    """Spaltenwerte nur aus Zeilen mit numerischer Subject-Nr (col 0).

    Filtert Summary-Zeilen (Text in Spalte 0, numerische Werte in den
    Daten-Spalten) heraus. Rueckgabe (Werte, n_subject_rows).
    """
    vals = []
    n_subject_rows = 0
    for r in range(first, arr.shape[0]):
        if np.isnan(arr[r, 0]):
            continue
        n_subject_rows += 1
        if not np.isnan(arr[r, col]):
            vals.append(arr[r, col])
    return np.array(vals, dtype=float), n_subject_rows


def wrap(diff):
    """Phasendifferenz auf (-pi, pi] wrappen (identisch zur Registrierung)."""
    return np.mod(np.asarray(diff) + np.pi, 2.0 * np.pi) - np.pi


def plaquette_vorticity(phases: np.ndarray) -> np.ndarray:
    """Exakt die registrierte Formel (xu_agreement_test.py), NaN-faehig."""
    d_row = wrap(phases[1:, :] - phases[:-1, :])  # (N-1, N)
    d_col = wrap(phases[:, 1:] - phases[:, :-1])  # (N, N-1)
    return (
        d_row[:, :-1] + d_col[1:, :] - d_row[:, 1:] - d_col[:-1, :]
    ) / (2.0 * np.pi)


def trial_resultants(block: np.ndarray) -> tuple:
    """Kreis-Resultante je Zeile (Trial) ueber die 5 Zeit-Schritte.

    Nur Trials mit allen 5 Winkeln und Resultantenlaenge > 0.1.
    """
    valid = ~np.isnan(block)
    c = np.where(valid, np.cos(np.nan_to_num(block)), 0.0)
    s = np.where(valid, np.sin(np.nan_to_num(block)), 0.0)
    c_sum = c.sum(axis=1)
    s_sum = s.sum(axis=1)
    n_valid = valid.sum(axis=1)
    theta = np.arctan2(s_sum, c_sum)
    r = np.hypot(c_sum, s_sum) / np.maximum(n_valid, 1)
    ok = (n_valid == block.shape[1]) & (r > 0.1)
    return theta[ok], r[ok]


def flip_stat(pooled: np.ndarray, mask_a: np.ndarray) -> float:
    """|wrap(Differenz der zirkulaeren Mittel)| der beiden Label-Gruppen."""
    m_a = np.arctan2(
        float(np.mean(np.sin(pooled[mask_a]))),
        float(np.mean(np.cos(pooled[mask_a]))),
    )
    m_b = np.arctan2(
        float(np.mean(np.sin(pooled[~mask_a]))),
        float(np.mean(np.cos(pooled[~mask_a]))),
    )
    return abs(float(wrap(np.array([m_b - m_a]))[0]))


def x1_direction_flip(data: dict) -> dict:
    """Single-Trial Phasenvektor-Winkel: Listening vs Answering."""
    raw = load_grid(data["moesm15"], "Fig_8b_right")
    listen = raw[3:, 1:6]
    answer = raw[3:, 7:12]

    theta_l, _ = trial_resultants(listen)
    theta_a, _ = trial_resultants(answer)

    def circ_mean(theta: np.ndarray) -> tuple:
        c = float(np.mean(np.cos(theta)))
        s = float(np.mean(np.sin(theta)))
        return float(np.arctan2(s, c)), float(np.hypot(c, s))

    mean_l, r_l_mean = circ_mean(theta_l)
    mean_a, r_a_mean = circ_mean(theta_a)
    flip = float(abs(wrap(np.array([mean_a - mean_l]))[0]))

    # Zirkulaerer Permutationstest ueber gepoolte Trial-Winkel
    pooled = np.concatenate([theta_l, theta_a])
    n_l = len(theta_l)
    rng = np.random.default_rng(PERM_SEED)
    count = 0
    for _ in range(N_PERMUTATIONS):
        mask = rng.permutation(len(pooled)) < n_l
        if flip_stat(pooled, mask) >= flip:
            count += 1
    p_perm = float(count / N_PERMUTATIONS)

    if flip > FLIP_REALIZED and p_perm < 0.05 and r_l_mean >= 0.3 and r_a_mean >= 0.3:
        verdict = "X1_FLIP_REALIZED"
    elif flip > FLIP_WEAK and p_perm < 0.05:
        verdict = "X1_FLIP_WEAK"
    else:
        verdict = "X1_FLIP_ABSENT"

    # Deskriptiv: Anteil positiver Winkel je Zeit-Schritt
    step_props = {"listening": [], "answering": []}
    for block, key in ((listen, "listening"), (answer, "answering")):
        for j in range(block.shape[1]):
            col = block[:, j]
            col = col[~np.isnan(col)]
            step_props[key].append(float(np.mean(col > 0)))

    # Anteil Trials, deren 5 Steps konsistent in einer Halb-Ebene liegen
    def consistency(block: np.ndarray) -> float:
        valid = ~np.isnan(block)
        n_pos = np.where(valid, block > 0, 0.0).sum(axis=1)
        n_neg = np.where(valid, block < 0, 0.0).sum(axis=1)
        full = valid.sum(axis=1) == block.shape[1]
        one_side = (n_pos == 0) | (n_neg == 0)
        return float(np.mean(one_side[full]))

    return {
        "n_trials_listen": int(len(theta_l)),
        "n_trials_answer": int(len(theta_a)),
        "circ_mean_listen_rad": mean_l,
        "circ_mean_answer_rad": mean_a,
        "resultant_listen": r_l_mean,
        "resultant_answer": r_a_mean,
        "flip_rad": flip,
        "flip_deg": float(np.degrees(flip)),
        "permutation_p": p_perm,
        "consistency_within_trial_listen": float(consistency(listen)),
        "consistency_within_trial_answer": float(consistency(answer)),
        "step_props_pos": step_props,
        "verdict": verdict,
    }


def _column_chance(sheet: str, j: int, label: str) -> float:
    """Registrierte Chance je Spalte (Docstring X2)."""
    low = label.lower()
    if sheet == "Fig_6c":
        if "stimulus" in low:
            return 0.25
        if "load" in low or "performance" in low:
            return 0.5
        # Fallback auf Spalten-Index (1-basiert): Typ/Load/Performance
        return [0.25, 0.5, 0.5][j - 1] if 1 <= j <= 3 else 0.5
    return 0.5


def x2_classification(data: dict) -> dict:
    """Fig_6b/6c: 100 Iterationen (Zeilen 2-101), t vs registrierte Chance.

    Korrektur-Log A(1): Datenzeilen explizit 2 bis 'Iteration Mean'-Zeile
    (exklusiv); die gespeicherten Summary-Zeilen dienen als Cross-Check.
    """
    out = {}
    for sheet, default_chance in (("Fig_6b", 0.5), ("Fig_6c", None)):
        arr = load_grid(data["moesm13"], sheet)
        raw = load_text_grid(data["moesm13"], sheet)

        mean_row = sem_row = None
        for r in range(len(raw)):
            first = _text(raw[r][0]) if raw[r] else ""
            if first == "Iteration Mean":
                mean_row = r
            elif first == "s.e.m.":
                sem_row = r

        entry = {
            "layout": {
                "mean_row_index": mean_row,
                "sem_row_index": sem_row,
                "n_rows_total": len(raw),
            }
        }
        data_last = mean_row if mean_row is not None else arr.shape[0]

        for j in range(1, arr.shape[1]):
            label = _text(raw[1][j]) if len(raw) > 1 and j < len(raw[1]) else ""
            vals = arr[2:data_last, j]
            vals = vals[~np.isnan(vals)]
            if len(vals) < 50:
                continue

            chance = (
                _column_chance(sheet, j, label)
                if default_chance is None
                else default_chance
            )
            mean = float(np.mean(vals))
            sem = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
            t_stat, p_val = stats.ttest_1samp(vals, chance)
            if p_val < 0.05 and mean > chance:
                label_verdict = "X2_ABOVE_CHANCE"
            elif p_val < 0.05 and mean < chance:
                label_verdict = "X2_BELOW_CHANCE"
            else:
                label_verdict = "X2_AT_CHANCE"

            col_result = {
                "column_label": label[:60],
                "chance": chance,
                "mean": mean,
                "sem": sem,
                "n_iterations": int(len(vals)),
                "iteration_1_value": float(arr[2, j]),
                "t_vs_chance": float(t_stat),
                "p_vs_chance": float(p_val),
                "label": label_verdict,
                "stored_iteration_mean": (
                    float(arr[mean_row, j])
                    if mean_row is not None and not np.isnan(arr[mean_row, j])
                    else None
                ),
                "stored_sem": (
                    float(arr[sem_row, j])
                    if sem_row is not None and not np.isnan(arr[sem_row, j])
                    else None
                ),
            }
            if col_result["stored_iteration_mean"] is not None:
                col_result["stored_mean_matches"] = bool(
                    abs(col_result["stored_iteration_mean"] - mean) < 1e-6
                )
            if col_result["stored_sem"] is not None:
                col_result["stored_sem_ratio"] = float(
                    col_result["stored_sem"] / sem
                )
            entry[label[:60] or f"col{j}"] = col_result

        # POST-HOC (klar gelabelt, kein registriertes Kriterium):
        # Fig_6b-Spalten zusaetzlich gegen Chance-Alternative 0.25 — die
        # Zielgroesse der Language-Klassifikation (2-Klassen Story/Math
        # vs 4 Bedingungen Story/Math x Listen/Answer) steht nicht in den
        # Sheets; der Paper-Text entscheidet, nicht dieses Kriterium.
        if sheet == "Fig_6b":
            alt = {}
            for j in range(1, arr.shape[1]):
                vals = arr[2:data_last, j]
                vals = vals[~np.isnan(vals)]
                if len(vals) < 50:
                    continue
                col_label = _text(raw[1][j]) if len(raw) > 1 and j < len(raw[1]) else ""
                t_stat, p_val = stats.ttest_1samp(vals, CHANCE_ALT_LANGUAGE)
                alt[col_label[:60] or f"col{j}"] = {
                    "mean": float(np.mean(vals)),
                    "t_vs_0_25": float(t_stat),
                    "p_vs_0_25": float(p_val),
                }
            entry["post_hoc_chance_alt_0_25"] = {
                "note": (
                    "POST-HOC, kein registriertes Kriterium: Alternative-"
                    "Chance 0.25 (4-Bedingungen Story/Math x Listen/Answer), "
                    "registrierte Chance bleibt 0.5"
                ),
                "columns": alt,
            }
        out[sheet] = entry

    arr = load_grid(data["moesm13"], "Fig_6b")
    raw = load_text_grid(data["moesm13"], "Fig_6b")
    spiral = arr[2:102, 1]
    amplitude = arr[2:102, 3]
    spiral = spiral[~np.isnan(spiral)]
    amplitude = amplitude[~np.isnan(amplitude)]
    _t, p = stats.ttest_ind(spiral, amplitude, equal_var=False)
    out["language_spiral_vs_amplitude"] = {
        "mean_spiral_original": float(np.mean(spiral)),
        "mean_amplitude": float(np.mean(amplitude)),
        "n_spiral": int(len(spiral)),
        "n_amplitude": int(len(amplitude)),
        "welch_p": float(p),
    }
    return out


def x3_interaction_types(data: dict) -> dict:
    """Fig_4a: Mittel ueber Subjects je Interaktions-Typ (Subject-Filter)."""
    arr = load_grid(data["moesm11"], "Fig_4a")
    raw = load_text_grid(data["moesm11"], "Fig_4a")
    sublabel = _text(raw[2][1]) if len(raw) > 2 else ""
    out = {
        "sheet_sublabel": sublabel[:60],
        "n_subject_rows_numeric_col0": 0,
        "columns": {},
    }
    row_sums = []
    n_with_all = 0
    for r in range(3, arr.shape[0]):
        if not np.isnan(arr[r, 0]) and not any(
            np.isnan(arr[r, j]) for j in (1, 2, 3)
        ):
            row_sums.append(arr[r, 1] + arr[r, 2] + arr[r, 3])
            n_with_all += 1
    for j in range(1, arr.shape[1]):
        vals, n_subject_rows = subject_column(arr, j, 3)
        if len(vals) == 0:
            continue
        out["n_subject_rows_numeric_col0"] = n_subject_rows
        name = _text(raw[1][j]) if len(raw) > 1 and j < len(raw[1]) else ""
        out["columns"][name[:60] or f"col{j}"] = {
            "mean": float(np.mean(vals)),
            "n": int(len(vals)),
        }
    if row_sums:
        out["mean_row_sum"] = float(np.mean(row_sums))
        out["n_rows_all_three_columns"] = n_with_all
    return out


def x4_formula_on_real_phase(data: dict) -> list:
    """Unsere Plaquette-Formel auf den drei echten Phasenfeldern."""
    wb = openpyxl.load_workbook(data["moesm21"], read_only=True, data_only=True)
    results = []
    for name in ("Fig_6c_left", "Fig_6c_mid", "Fig_6c_right"):
        ws = wb[name]
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append(
                [
                    float(v)
                    if isinstance(v, (int, float)) and not isinstance(v, bool)
                    else np.nan
                    for v in row
                ]
            )
        phase = np.array(rows, dtype=float)
        vort = plaquette_vorticity(phase)
        valid = ~np.isnan(vort)
        strong = valid & (np.abs(vort) > CORE_THRESHOLD)
        n_cores = int(np.sum(strong))
        if n_cores > 0:
            core_vals = np.abs(vort[strong])
            quant_frac = float(
                np.mean(
                    (core_vals >= 1.0 - QUANT_WINDOW)
                    & (core_vals <= 1.0 + QUANT_WINDOW)
                )
            )
            n_pos = int(np.sum(vort[strong] > 0))
            n_neg = int(np.sum(vort[strong] < 0))
        else:
            quant_frac = 0.0
            n_pos = 0
            n_neg = 0
        results.append(
            {
                "sheet": name,
                "n_valid_plaquettes": int(np.sum(valid)),
                "n_cores": n_cores,
                "n_pos": n_pos,
                "n_neg": n_neg,
                "quant_fraction": quant_frac,
                "max_abs_vort": float(np.nanmax(np.abs(vort))),
                "p99_abs_vort": float(np.nanpercentile(np.abs(vort), 99)),
            }
        )
        print(
            f"X4 {name}: n_cores={n_cores} pos={n_pos} neg={n_neg} "
            f"quant={quant_frac:.3f} max|v|={results[-1]['max_abs_vort']:.3f} "
            f"p99={results[-1]['p99_abs_vort']:.3f}"
        )
    wb.close()
    return results


def x5_direction_proportions(data: dict) -> dict:
    """Fig_5a/b/c/d_4th: cw/acw-Anteile je Task-Epoch (Subject-Filter)."""
    out = {}
    grids = {}
    for sheet in ("Fig_5a_4th", "Fig_5b_4th", "Fig_5c_4th", "Fig_5d_4th"):
        arr = load_grid(data["moesm12"], sheet)
        raw = load_text_grid(data["moesm12"], sheet)
        grids[sheet] = arr
        labels = [
            _text(raw[0][j]) if j < len(raw[0]) else ""
            for j in range(min(5, arr.shape[1]))
        ]
        entry = {"header": labels}
        cols = {}
        for j in range(1, min(5, arr.shape[1])):
            vals, n_subject_rows = subject_column(arr, j, 1)
            if len(vals):
                name = labels[j][:40] if j < len(labels) else f"col{j}"
                cols[name or f"col{j}"] = {
                    "mean": float(np.mean(vals)),
                    "n": int(len(vals)),
                    "n_subject_rows": n_subject_rows,
                }
        entry["columns"] = cols
        out[sheet] = entry

    # Cross-Check: Fig_5a_4th Spalte 2 vs Fig_5b_4th Spalte 1 (im ersten
    # Lauf trug je eine Spalte den identischen Mittelwert 0.3237).
    arr_a, arr_b = grids["Fig_5a_4th"], grids["Fig_5b_4th"]
    pairs = []
    for r in range(1, min(arr_a.shape[0], arr_b.shape[0])):
        x, y = arr_a[r, 2], arr_b[r, 1]
        if not np.isnan(x) and not np.isnan(y):
            pairs.append((x, y))
    if pairs:
        diffs = [abs(x - y) for x, y in pairs]
        out["cross_check_5a_col2_vs_5b_col1"] = {
            "n_common": len(pairs),
            "n_identical": int(sum(1 for x, y in pairs if x == y)),
            "max_abs_diff": float(max(diffs)),
        }
    return out


def main() -> None:
    started = time.time()
    data = {
        "moesm11": DATA_DIR / "moesm11_Fig4.xlsx",
        "moesm12": DATA_DIR / "moesm12_Fig5.xlsx",
        "moesm13": DATA_DIR / "moesm13_Fig6.xlsx",
        "moesm15": DATA_DIR / "moesm15_Fig8.xlsx",
        "moesm21": DATA_DIR / "moesm21_ED.xlsx",
    }
    print("Xu-Source-Data Re-Analyse (EXPLORATORY_REANALYSIS) — Start")

    x1 = x1_direction_flip(data)
    print(
        f"X1: flip={x1['flip_rad']:.3f} rad ({x1['flip_deg']:.1f} deg), "
        f"R_listen={x1['resultant_listen']:.2f} "
        f"R_answer={x1['resultant_answer']:.2f} "
        f"p={x1['permutation_p']:.4f} -> {x1['verdict']}"
    )
    print(f"X1 step_props_pos: {x1['step_props_pos']}")
    print(
        f"X1 consistency within trial: "
        f"listen={x1['consistency_within_trial_listen']:.3f} "
        f"answer={x1['consistency_within_trial_answer']:.3f}"
    )

    x2 = x2_classification(data)
    for sheet in ("Fig_6b", "Fig_6c"):
        for key, val in x2[sheet].items():
            if key in ("post_hoc_chance_alt_0_25", "layout"):
                continue
            print(
                f"X2 {sheet} {key}: mean={val['mean']:.4f} "
                f"sem={val['sem']:.4f} (stored sem "
                f"{val['stored_sem']:.4f}) "
                f"n={val['n_iterations']} p={val['p_vs_chance']:.3e} "
                f"{val['label']}"
            )
    for key, val in x2["Fig_6b"]["post_hoc_chance_alt_0_25"]["columns"].items():
        print(
            f"X2 POST-HOC Fig_6b {key} vs 0.25: "
            f"t={val['t_vs_0_25']:.2f} p={val['p_vs_0_25']:.3e}"
        )
    lang = x2["language_spiral_vs_amplitude"]
    print(
        f"X2 Language spiral-vs-amplitude: "
        f"{lang['mean_spiral_original']:.4f} vs {lang['mean_amplitude']:.4f} "
        f"p={lang['welch_p']:.3e}"
    )

    x3 = x3_interaction_types(data)
    print(
        f"X3 label: '{x3['sheet_sublabel']}', n_subject_rows="
        f"{x3['n_subject_rows_numeric_col0']}, rows all 3 cols="
        f"{x3['n_rows_all_three_columns']}, mean row-sum="
        f"{x3['mean_row_sum']:.4f}"
    )
    for key, val in x3["columns"].items():
        print(f"X3 {key}: mean={val['mean']:.4f} (n={val['n']})")

    x4 = x4_formula_on_real_phase(data)

    x5 = x5_direction_proportions(data)
    for sheet, entry in x5.items():
        if sheet == "cross_check_5a_col2_vs_5b_col1":
            print(f"X5 cross-check 5a(col2) vs 5b(col1): {entry}")
            continue
        props = {
            k: round(v["mean"], 4) for k, v in entry["columns"].items()
        }
        ns = {k: v["n"] for k, v in entry["columns"].items()}
        print(f"X5 {sheet}: n={ns}")
        print(f"X5   {props}")

    result = {
        "status": "EXPLORATORY_REANALYSIS der publizierten Source Data",
        "not_part_of": "pre-registrierte Korpus-Registrierung (result.json)",
        "criteria": "vor dem Lauf fixiert (Docstring), Labels X*_*",
        "correction_log": [
            "A(1) X2 Datenzeilen 2-101 statt 3+ (Summary-Zeilen raus, "
            "Iteration 1 drin); Cross-Check gegen gespeicherte "
            "Mean/SEM-Zeilen",
            "A(2) Header-Labels via Text-Grid statt numerischem Array",
            "A(3) X3 Subject-Filter (100 Subject-Zeilen, 93 mit allen 3 "
            "Spalten, Zeilensumme 1.0) — Label 'n = 93' bestätigt",
            "A(4) X5 Subject-Filter (5a/5c hatten je 1 Summary-Zeile)",
            "B Fig_6c Chancen PER-SPALTE wie registriert (erster Lauf "
            "nutzte 0.25 für alle 3 Spalten — Code-vs-Registrierung-Bug, "
            "vor Buchung korrigiert)",
        ],
        "x1_direction_flip": x1,
        "x2_classification": x2,
        "x3_interaction_types": x3,
        "x4_formula_on_real_phase": x4,
        "x5_direction_proportions": x5,
        "runtime_s": time.time() - started,
    }
    out_path = OUT_DIR / "xu_data_result.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str)
    )
    print(f"Ergebnis persistiert: {out_path}")
    print(f"Runtime: {result['runtime_s']:.1f} s")


if __name__ == "__main__":
    main()
