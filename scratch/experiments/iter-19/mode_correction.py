#!/usr/bin/env python
"""iter-19 CORREKTUR — modus-aufgeloeste exakte Abbildung (Post-hoc).

Der Vorab-registrierten exakten Abbildung (turing_prospective.py:
eig_max_step) lag ein Stencil-Fehler zugrunde: mx = (1-2p*c)^3 und
my = (1-2*p_sub*c)^(3*n_sub) mit c = 1-cos(k) setzen die RADIALE
Wellenzahl k auf ALLE DREI Achsen gleichzeitig. Das ist der
Multiplikator der Diagonalmodus (k,k,k) (radial sqrt(3)*k), nicht der
einer Modus (k,0,0) oder allgemein (k_x,k_y,k_z).

Diese Korrektur rechnet die Abbildung PRO GITTERMODUS mit den
per-Achsen Wellenzahlen c_a = 1-cos(k_a) nach:
  mx = prod_a (1 - 2*du_step*c_a)          (EIN Aufruf, p = D_X)
  my = prod_a (1 - 2*p_sub*c_a)^n_sub      (n_sub Subschritte, p_sub)
  M  = diag(mx,my) * (I + DT*J),  Rate = ln max|eig(M)|  (Amplitude/Schritt)
und vergleicht mit (a) dem kontinuierlichen Symbol pro Modus und
(b) den gemessenen Frueh-Raten (Power-Fit / 2).

Erwartung (Theorie): korrigierte Abbildung ≈ kontinuierliches Symbol
auf O(dt*D*c) — die "Rivalitaet" der Vorab-Registrierung war ein
Artefakt des Stencil-Fehlers. Post-hoc-Konsistenz ist KEINE
Bestaetigung; sie wird hier nur als Fehler-Dokumentation gebucht.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent

A_FEED, B_FEED = 0.35, 0.65
K1, K2 = 0.5, 1.0
OMEGA, DT, D_X = 400.0, 0.05, 0.06
U_OP, V_OP = 0.9997, 1.2972  # iter-17 Arbeitspunkt

F_U = -K2 + 2 * K1 * U_OP * V_OP
F_V = K1 * U_OP * U_OP
G_U = -2 * K1 * U_OP * V_OP
G_V = -K1 * U_OP * U_OP
J_OP = np.array([[F_U, F_V], [G_U, G_V]])

BASE48 = 2.0 * math.pi / 48.0
SHELLS = {0.13090: 1, 0.18512: 2, 0.22672: 3, 0.26180: 4, 0.29272: 5,
          0.32064: 6, 0.37024: 8, 0.39270: 9, 0.41394: 10, 0.43415: 11,
          0.45345: 12, 0.47197: 13}


def exact_rate_mode(nvec: tuple[int, int, int], base: float, d_v: float,
                    du_step: float, null: bool = False) -> float:
    """Korrigierte exakte Abbildung pro Modus: ln max|eig(M)| pro Schritt."""
    ka = np.array(nvec, dtype=float) * base
    ka = np.where(ka > math.pi, 2.0 * math.pi - ka, ka)
    c = 1.0 - np.cos(ka)
    n_sub = max(1, math.ceil(d_v / 0.3))
    p_sub = d_v / n_sub
    if null:
        mx = float(np.prod(1.0 - 2.0 * p_sub * c))
        my = float(np.prod((1.0 - 2.0 * p_sub * c) ** n_sub))
    else:
        mx = float(np.prod(1.0 - 2.0 * du_step * c))
        my = float(np.prod((1.0 - 2.0 * p_sub * c) ** n_sub))
    mat = np.array([[mx * (1 + DT * F_U), mx * DT * F_V],
                    [my * DT * G_U, my * (1 + DT * G_V)]])
    return math.log(max(abs(np.linalg.eigvals(mat))))


def cont_rate_mode(nvec: tuple[int, int, int], base: float, d_v: float,
                   du_step: float, null: bool = False) -> float:
    """Kontinuierliches Symbol pro Modus: max Re eig * DT (pro Schritt)."""
    ka = np.array(nvec, dtype=float) * base
    ka = np.where(ka > math.pi, 2.0 * math.pi - ka, ka)
    csum = float((1.0 - np.cos(ka)).sum())
    du, dv = (d_v, d_v) if null else (du_step, d_v)
    mat = J_OP - np.diag([2.0 * csum * du / DT, 2.0 * csum * dv / DT])
    return float(np.linalg.eigvals(mat).real.max()) * DT


def registered_rate(k: float, d_v: float, du_step: float) -> float:
    """Die FEHLERHAFTE registrierte Formel (Diagonalmodus-Stencil)."""
    c = 1.0 - math.cos(k)
    mx = (1.0 - 2.0 * du_step * c) ** 3
    n_sub = max(1, math.ceil(d_v / 0.3))
    p_sub = d_v / n_sub
    my = (1.0 - 2.0 * p_sub * c) ** (3 * n_sub)
    mat = np.array([[mx * (1 + DT * F_U), mx * DT * F_V],
                    [my * DT * G_U, my * (1 + DT * G_V)]])
    return math.log(max(abs(np.linalg.eigvals(mat))))


def modes_in_shell(c_sh: float, tol: float = 0.004) -> list[tuple[int, ...]]:
    out = []
    for n1 in range(-24, 25):
        for n2 in range(-24, 25):
            for n3 in range(-24, 25):
                km = BASE48 * math.sqrt(n1 * n1 + n2 * n2 + n3 * n3)
                if km > 1e-9 and abs(km - c_sh) < tol:
                    out.append((n1, n2, n3))
    return out


def measured_amp_rate(tc: list[dict], c_sh: float) -> float | None:
    """Gemessene Power-Frueh-Rate / 2 (Amplitude/Schritt), [1.5,6]xA0."""
    ser = []
    for s in tc:
        for kk, val in ((float(k), val) for k, val in s["shells_x"].items()):
            if abs(kk - c_sh) < 2e-5:
                ser.append((s["step"], val))
    if len(ser) < 3:
        return None
    a0 = ser[0][1]
    win = [(t, x) for t, x in ser if 1.5 * a0 <= x <= 6.0 * a0] or ser[:3]
    t = np.array([w[0] for w in win], dtype=float)
    y = np.log([max(w[1], 1.0) for w in win])
    return float(np.polyfit(t, y, 1)[0]) / 2.0


def main() -> None:
    # 1) Integritaet: die fehlerhafte Formel reproduziert die Registrierung
    reg_check = {str(k): registered_rate(k, 3.0, D_X)
                 for k in (0.13090, 0.18512, 0.22670, 0.26180, 0.29270)}
    assert abs(reg_check["0.1309"] - 0.003472) < 3e-5
    assert abs(reg_check["0.18512"] - 0.004508) < 3e-5
    assert abs(reg_check["0.2927"]) < 0.003  # registriert "stabil"
    print("Registrierte Formel reproduziert (Stencil-Fehler bestaetigt):")
    for k, val in reg_check.items():
        print(f"  k={k}: {val:+.6f}")
    print()

    # 2) Korrigierte modus-aufgeloeste Tabelle
    res = json.loads((HERE / "result.json").read_text())
    tc3 = res["turing3"]["seeds"]["300"]["timecourse"]
    rows = []
    print(f"{'Schale':>8} {'n_mod':>5} | {'exact korr':>10} {'cont':>9} "
          f"{'diff':>7} | {'gemessen/2':>10}")
    for c_sh in sorted(SHELLS):
        ms = modes_in_shell(c_sh)
        ex = max(exact_rate_mode(m, BASE48, 3.0, D_X) for m in ms)
        ct = max(cont_rate_mode(m, BASE48, 3.0, D_X) for m in ms)
        meas = measured_amp_rate(tc3, c_sh)
        rows.append({"shell": c_sh, "n_modes": len(ms), "exact_corr": ex,
                     "continuous": ct, "diff": ex - ct,
                     "measured_amp": meas})
        print(f"{c_sh:8.5f} {len(ms):5d} | {ex:+10.5f} {ct:+9.5f} "
              f"{ex - ct:+7.4f} | "
              f"{'—' if meas is None else format(meas, '+10.5f')}")

    # 3) Korrigierte Bande (alle Moden scannen)
    lo = hi = None
    for n1 in range(0, 25):
        for n2 in range(0, 25):
            for n3 in range(0, 25):
                r = exact_rate_mode((n1, n2, n3), BASE48, 3.0, D_X)
                km = BASE48 * math.sqrt(n1 * n1 + n2 * n2 + n3 * n3)
                if r > 0 and 1e-9 < km <= math.pi:
                    lo = km if lo is None else min(lo, km)
                    hi = km if hi is None else max(hi, km)
    print(f"\nKorrigierte Bande (alle Moden, D_v=3): [{lo:.4f}, {hi:.4f}]")
    print("Kontinuierliches Symbol (registriert): [0.186, 0.456]")
    print("Registriert (fehlerhaft, Diagonalmodus-Einheiten): "
          "[0.1038, 0.2696] -> radial *sqrt(3) = "
          f"[{0.1038*math.sqrt(3):.4f}, {0.2696*math.sqrt(3):.4f}]")

    out = {
        "registered_reproduction": reg_check,
        "corrected_per_mode": rows,
        "corrected_band": [lo, hi],
        "continuous_band_registered": [0.186, 0.456],
        "registered_band_diagonal_units": [0.1038, 0.2696],
        "registered_band_radial_sqrt3": [0.1038 * math.sqrt(3),
                                         0.2696 * math.sqrt(3)],
    }
    (HERE / "mode_correction.json").write_text(json.dumps(out, indent=1))
    print("\nmode_correction.json geschrieben.")


if __name__ == "__main__":
    main()
