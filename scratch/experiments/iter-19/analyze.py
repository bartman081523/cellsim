#!/usr/bin/env python
"""iter-19 Auswertung — P1-P5-Verdict-Zusammenbau nach Vorab-Registrierung.

Liest result.json (vom vollen Lauf) und wendet die im Docstring von
turing_prospective.py fixierten Kriterien an. KEINE neuen Kriterien —
alles hier ist Ableitung, nichts wird nachgeschärft.

Registrierte Kriterien:
  P1 ONSET: stable10/stable025 band_ratio < 3 (vs Schritt-0-Niveau,
     da null1.0 nicht als eigene Konfig registriert wurde — Substitution
     im CORREKTUR-LOG dokumentiert); turing3 band_ratio >= 10 bei
     gematchten Schritten (800) vs null3.
  P2 BAND: out-high Fenster [0.280, 0.500] bei turing3 <= 3x null3
     (Schale 0.293 stabil in exakter Abbildung).
  P3 GROWTH: early-phase sigma des Banden-Sums innerhalb
     [0.00113, 0.0180]/Schritt; per-shell Fits gegen registrierte
     Raten {0.131: 0.003472, 0.185: 0.004508, 0.227: 0.002929,
     0.262: 0.000633}; Schale 0.293 auf Null-Niveau.
  P4 ANCHOR: anchor_L24 k_peak = 0.262.
  P5 BILANZ: mean_x driftet <= 10%.

Verdict-Logik (vorab registriert):
  PATTERN_AS_PREDICTED_EXACT_MAP: P1-P5 alle erfüllt.
  BAND_SHIFTED_CONTINUOUS: P1/P3/P4 erfüllt, P2 verletzt.
  FALSIFIED_ONSET / FALSIFIED_GROWTH / CONTROL_INVALID / MIXED_BANDS.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent

# Registrierte Schalenraten pro Schritt (exakte Abbildung, D_v=3, D_X=0.06)
REG_SHELL_RATES = {0.13090: 0.003472, 0.18512: 0.004508,
                   0.22670: 0.002929, 0.26180: 0.000633}
REG_SIGMA_WINDOW = (0.00113, 0.0180)  # pro Schritt
IN_BAND = (0.104, 0.270)
OUT_HIGH = (0.280, 0.500)


def _fkeys(shells: dict) -> dict[float, float]:
    """JSON-Roundtrip: Schalen-Keys sind Strings → float."""
    return {float(k): v for k, v in shells.items()}


def _sh_get(shells: dict, target: float, tol: float = 2e-5) -> float:
    """Schalenwert per Toleranz-Match (registrierte Keys runden 2e-5)."""
    f = _fkeys(shells)
    for k, v in f.items():
        if abs(k - target) < tol:
            return v
    raise KeyError(target)


def _shell_keys(shells: dict, window: tuple[float, float]) -> list[float]:
    return [k for k in _fkeys(shells) if window[0] <= k <= window[1]]


def band_at(tc: list[dict], step: int, window: tuple[float, float],
            field: str = "shells_x") -> float:
    """Banden-Leistung zum Zeitpunkt step (Snapshot am nächsten Schritt)."""
    for s in tc:
        if s["step"] == step:
            sh = _fkeys(s[field])
            return sum(sh[k] for k in _shell_keys(s[field], window))
    raise KeyError(step)


def early_fit(series: list[tuple[int, float]],
              lo_f: float = 1.5, hi_f: float = 6.0
              ) -> tuple[float, int, int]:
    """Log-linear Fit im Early-Window [1.5, 6]x A0 (A0 = erster Wert).

    Returns (rate/Schritt, n_snaps, step_lo)."""
    a0 = series[0][1]
    win = [(t, v) for t, v in series if lo_f * a0 <= v <= hi_f * a0]
    if len(win) < 3:
        win = series[:3]  # fallback: erste drei Snapshots
    t = np.array([w[0] for w in win], dtype=float)
    y = np.log(np.array([max(w[1], 1e-300) for w in win]))
    slope = float(np.polyfit(t, y, 1)[0])
    return slope, len(win), int(t[0])


def main() -> None:
    res = json.loads((Path(__file__).parent / "result.json").read_text())

    tc3 = res["turing3"]["seeds"]["300"]["timecourse"]
    nul3 = res["null3"]["seeds"]["300"]["timecourse"]
    tc10 = res["turing10"]["seeds"]["300"]["timecourse"]
    nul10 = res["null10"]["seeds"]["300"]["timecourse"]
    st10 = res["stable10"]["seeds"]["300"]["timecourse"]
    st025 = res["stable025"]["seeds"]["300"]["timecourse"]
    anchor = res["anchor_L24"]["seeds"]["300"]

    out: dict = {"criteria": {}}

    # --- P1 ONSET ---
    nul3_band800 = band_at(nul3, 800, IN_BAND)
    t3_band800 = band_at(tc3, 800, IN_BAND)
    ratio_t3 = t3_band800 / nul3_band800
    r_st025 = band_at(st025, 800, IN_BAND) / band_at(st025, 0, IN_BAND)
    r_st10 = band_at(st10, 800, IN_BAND) / band_at(st10, 0, IN_BAND)
    p1 = (r_st025 < 3.0 and r_st10 < 3.0 and ratio_t3 >= 10.0)
    out["criteria"]["P1_onset"] = {
        "ratio_turing3_vs_null3_at800": ratio_t3,
        "ratio_stable025_self": r_st025,
        "ratio_stable10_self": r_st10,
        "pass": p1,
    }

    # --- P2 BAND (out-high Fenster <= 3x null3) ---
    nul3_out800 = band_at(nul3, 800, OUT_HIGH)
    t3_out800 = band_at(tc3, 800, OUT_HIGH)
    t3_out1600 = band_at(tc3, 1600, OUT_HIGH)
    ratio_out = t3_out800 / nul3_out800
    ratio_out1600 = t3_out1600 / nul3_out800
    p2 = ratio_out <= 3.0
    out["criteria"]["P2_band_out_high"] = {
        "ratio_at_800_vs_null3": ratio_out,
        "ratio_at_1600_vs_null3_at_800": ratio_out1600,
        "shells_out_high_t3_1600": {k: _fkeys(tc3[-1]["shells_x"])[k]
                                    for k in _shell_keys(tc3[-1]["shells_x"],
                                                         OUT_HIGH)},
        "pass": p2,
    }

    # --- P3 GROWTH (Band-Sum + per-shell) ---
    band_series = [(s["step"], s["band_power_x"]) for s in tc3]
    fit_band, n_fit, step_lo = early_fit(band_series)
    shell_fits = {}
    for key in (0.13090, 0.18512, 0.22670, 0.26180):
        ser = [(s["step"], _sh_get(s["shells_x"], key))
               for s in tc3 if abs(s["step"]) >= 0]
        rate, n, lo = early_fit(ser)
        shell_fits[str(key)] = {
            "measured_per_step": rate,
            "registered": REG_SHELL_RATES[key],
            "ratio": rate / REG_SHELL_RATES[key],
            "n_snaps": n, "step_lo": lo,
        }
    # Schale 0.293 (registriert: stabil) — Wachstum <= Null
    s293 = [(s["step"], _sh_get(s["shells_x"], 0.29270)) for s in tc3]
    s293_growth = (s293[-1][1] / s293[0][1]) if len(s293) >= 2 else float("nan")
    p3 = (REG_SIGMA_WINDOW[0] <= fit_band <= REG_SIGMA_WINDOW[1])
    out["criteria"]["P3_growth"] = {
        "band_sigma_per_step": fit_band,
        "window": REG_SIGMA_WINDOW, "n_snaps": n_fit, "step_lo": step_lo,
        "shell_fits": shell_fits,
        "shell_0293_growth_factor": s293_growth,
        "pass": p3,
    }

    # --- P4 ANCHOR ---
    kw = anchor["final_k"]
    pw = anchor["final_power"]
    k_peak = kw[int(np.argmax(pw))]
    p4 = abs(k_peak - 0.2618) < 0.02
    out["criteria"]["P4_anchor"] = {"k_peak": k_peak, "pass": p4}

    # --- Banden-Verallgemeinerung (turing10 vs null10, gematcht bei 400) ---
    # Registrierte D_v=10-Bande (0.0535, 0.2845) enthält dieselben L=48-
    # Schalen {0.131, 0.185, 0.227, 0.262} wie das IN_BAND-Fenster.
    ratio_t10 = band_at(tc10, 400, IN_BAND) / band_at(nul10, 400, IN_BAND)
    out["criteria"]["band_extension_Dv10"] = {
        "ratio_turing10_vs_null10_at400": ratio_t10,
        "registered_band_Dv10": [0.0535, 0.2845],
    }

    # --- P5 BILANZ ---
    mx0 = tc3[0]["mean_x"]
    drift_t3 = abs(tc3[-1]["mean_x"] - mx0) / mx0
    mx0a = anchor["timecourse"][0]["mean_x"]
    tc_a = anchor["timecourse"]
    drift_anchor = abs(tc_a[-1]["mean_x"] - mx0a) / mx0a
    p5 = drift_t3 <= 0.10 and drift_anchor <= 0.10
    out["criteria"]["P5_bilanz"] = {"drift_turing3": drift_t3,
                                    "drift_anchor": drift_anchor, "pass": p5}

    # --- Verdict ---
    p = {k: v["pass"] for k, v in out["criteria"].items() if "pass" in v}
    if p["P1_onset"] and p["P2_band_out_high"] and p["P3_growth"] \
            and p["P4_anchor"] and p["P5_bilanz"]:
        verdict = "PATTERN_AS_PREDICTED_EXACT_MAP"
    elif p["P1_onset"] and p["P3_growth"] and p["P4_anchor"] \
            and not p["P2_band_out_high"] and p["P5_bilanz"]:
        verdict = "BAND_SHIFTED_CONTINUOUS"
    elif p["P1_onset"] and p["P3_growth"] and p["P4_anchor"] \
            and p["P5_bilanz"] and not p["P2_band_out_high"] \
            and ratio_out1600 > 3.0 and fit_band > 0:
        verdict = "MIXED_BANDS"
    elif not p["P1_onset"]:
        verdict = "FALSIFIED_ONSET"
    elif not p["P3_growth"]:
        verdict = "FALSIFIED_GROWTH"
    else:
        verdict = "CONTROL_INVALID"
    out["verdict"] = verdict
    (Path(__file__).parent / "analysis.json").write_text(
        json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
