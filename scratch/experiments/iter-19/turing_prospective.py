#!/usr/bin/env python
"""iter-19 — VECTOR_TURING_PROSPECTIVE (iter-17b): Turing-Muster PROSPEKTIV.

Vorab registrierte Vorhersagen (fixiert 2026-09-21, VOR jedem Lauf).

Substrat: exakt der iter-17-Kern (Schnakenberg 2-Spezies, Sprung-Diffusion).
  A_FEED=0.35, B_FEED=0.65, K1=0.5, K2=1.0, OMEGA=400, DT=0.05, D_X=0.06.
  tau_leap: Propensitäten vom Schrittstart; Diffusion danach.
  Sprung-Diffusion (Produktionsmodul stochastic_jump_diffusion): pro Achse
  Abreise-Wkeit 2p, 50/50-Split → Moden-Multiplikator (1 - 2p(1-cos k))
  pro Achse und Subschritt; n_sub = ceil(d_v/0.3), p_sub = d_v/n_sub.

Zwei Analysen der GLEICHEN Regel, zwei rivalisierende Vorhersagen:
  (a) EXAKTE DISKRETE ABILDUNG (primär) — M(k) = diag(mx, my)·(I + dt·J),
      die exakte Linearisierung des implementierten Updates. Keine Näherung
      außer der Linearisierung selbst. Diffusion ist pro Schritt O(1)
      (damp·D_v ≈ 0.2), daher weicht die kontinuierliche Symbol-Näherung
      erheblich ab (Splitting-Fehler O(dt·damp·D), nicht klein).
  (b) KONTINUIERLICHES SYMBOL (Referenz) — J − 2(1-cos k)·diag(D/dt);
      iter-17-Korrektur (D_eff = D/DT). Onset dt-invariant, analytisch.

Registrierte Zahlen (exakte Abbildung, berechnet vor dem Lauf):
  D_v=0.25 / 1.0 : stabil (max|eig| <= 1 über alle k)
  D_v= 3.0 : Bande k in [0.1038, 0.2696], k*=0.1690, sigma*=+0.0934/t
             (= +0.004671/Schritt); L=48-Schaleninstabilitätsraten:
             0.131: 0.00347/Schritt, 0.185: 0.00451, 0.227: 0.00293,
             0.262: 0.00063. Schale 0.293 STABIL (Jury-Marge 0.0011).
  D_v=10.0 : Bande k in [0.0535, 0.2845], k*=0.1266,
             sigma*=+0.1884/t (= +0.009422/Schritt); stärkste Schale 0.131.
  Onset (exakte Abbildung): D_v = 1.427 pro Schritt.
Referenz (kontinuierliches Symbol): D_v=3: [0.186, 0.456], k*=0.292;
  D_v=10: [0.094, 0.490]; Onset 1.556.

DISKRIMINIERENDE Konsequenz auf L=48 (2pi/48 = 0.1309):
  exakte Abbildung: Muster nur in Schalen {0.131, 0.185, 0.227, 0.262};
    Schale 0.293 muss auf Null-Niveau bleiben (<= 3x isotrope Null).
  kontinuierliches Symbol: Muster bis 0.453, Peak bei 0.293.
  iter-17 (L=24) kann das nicht unterscheiden — 0.293 existiert dort nicht.

Vorab registrierte Kriterien:
  P1 ONSET: D_v=1.0 bleibt auf Null-Niveau (band_ratio < 3 vs isotrope
     Null D_u=D_v=1.0); D_v=3.0 waechst (band_ratio >= 10). [beide
     Analysen stimmen überein — Onset-Bracket]
  P2 BAND (exakte Abbildung, primär): bei D_v=3 bleibt die Leistung im
     Fenster [0.280, 0.500] <= 3x Null-Niveau (Schale 0.293 stabil).
  P3 WACHSTUM: early-phase sigma des dominanten Banden-Modus innerhalb
     [sigma*/4, 4·sigma*] = [0.00113, 0.0180]/Schritt (sigma* = 0.00451 =
     max Schalenrate bei D_v=3, exakte Abbildung).
  P4 ANKER: L=24-Kern mit identischem Substrat repliziert iter-17
     (k_peak = 0.262, Muster vorhanden) → Substrat-Äquivalenz.
  P5 BILANZ: mean_x driftet <= 10% während des Musterwachstums
     (Feed/Entfernung im Gleichgewicht).

Verdicts:
  PATTERN_AS_PREDICTED_EXACT_MAP: P1-P5 alle erfüllt → prospektive
    Bestätigung der exakten Abbildung; kontinuierliches Symbol in P2
    FALSIFIZIERT (0.293 müsste dort aktiv sein).
  BAND_SHIFTED_CONTINUOUS: P1, P3, P4 erfüllt, aber P2 verletzt
    (Muster dehnt sich in [0.280, 0.500] aus, 0.293 aktiv) → exakte
    Abbildung falsifiziert, kontinuierliches Symbol bestätigt; dann
    muss der Modellierungsfehler in der Abbildung gefunden werden.
  FALSIFIED_ONSET / FALSIFIED_GROWTH / CONTROL_INVALID wie iter-17.
  MIXED_BANDS: beide Fenster aktiv mit korrekten early rates → nicht-
    lineare Kaskade dominiert; lineare Diskrimination nur im Early-
    Window modus-aufgelöst lesbar (per-shell Fits werden geliefert).

Design (base_seed 300, RNG make_rng(seed, 17, cfg_idx)):
  anchor_L24 : D_v=3.0, L=24, T=800, 1 Seed   (P4)
  stable025  : D_v=0.25, L=48, T=800, 2 Seeds (P1-Rand)
  stable1.0  : D_v=1.0,  L=48, T=800, 2 Seeds (P1-Rand)
  turing3    : D_v=3.0,  L=48, T=1600, 2 Seeds (P1/P2/P3/P5)
  turing10   : D_v=10.0, L=48, T=1600, 1 Seed  (Banden-Verallgemeinerung)
  null3      : D_u=D_v=3.0, L=48, T=800, 2 Seeds (isotrope Null)
  null10     : D_u=D_v=10.0, L=48, T=400, 1 Seed (isotrope Null)
  Vergleiche bei gematchten Schritten (800 bzw. 400).
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import numpy as np

from cellsim.core.rng import make_rng
from cellsim.modules.emergence import (
    radial_power_spectrum,
    stochastic_jump_diffusion,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
LOG = logging.getLogger("iter19")

# --- Kern-Konstanten (identisch zu iter-17) ---
A_FEED, B_FEED = 0.35, 0.65
K1, K2 = 0.5, 1.0
OMEGA = 400.0
DT = 0.05
D_X = 0.06
SNAP_EVERY = 25

# --- Vorab registrierte Vorhersagen (exakte diskrete Abbildung) ---
REG = {
    3.0: {
        "band": (0.1038, 0.2696),
        "k_star": 0.1690,
        "sigma_star_step": 0.004671,
        "shells": {0.13090: 0.003472, 0.18512: 0.004508, 0.22670: 0.002929,
                   0.26180: 0.000633},
    },
    10.0: {
        "band": (0.0535, 0.2845),
        "k_star": 0.1266,
        "sigma_star_step": 0.009422,
    },
}


def jacobian_at() -> tuple[float, float, float, float]:
    """Jacobi-Matrix am gemessenen Arbeitspunkt (iter-17: u=0.9997,
    v=1.2972)."""
    u, v = 0.9997, 1.2972
    f_u = -K2 + 2.0 * K1 * u * v
    f_v = K1 * u * u
    g_u = -2.0 * K1 * u * v
    g_v = -K1 * u * u
    return f_u, f_v, g_u, g_v


def eig_max_step(k: float, d_v: float, du_step: float) -> float:
    """max|eig| des exakten diskreten Abbilders bei Modenwellenzahl k."""
    f_u, f_v, g_u, g_v = jacobian_at()
    c = 1.0 - math.cos(k)
    mx = (1.0 - 2.0 * du_step * c) ** 3
    n_sub = max(1, int(math.ceil(d_v / 0.3)))
    p_sub = d_v / n_sub
    my = (1.0 - 2.0 * p_sub * c) ** (3 * n_sub)
    m = np.array([[mx * (1 + DT * f_u), mx * DT * f_v],
                  [my * DT * g_u, my * (1 + DT * g_v)]])
    return max(abs(np.linalg.eigvals(m)))


def exact_band(d_v: float, du_step: float) -> tuple[float, float, float, float]:
    """(lo, hi, k*, sigma*_step) der exakten Abbildung; None wenn stabil."""
    ks = np.linspace(1e-4, math.pi, 4000)
    ev = np.array([eig_max_step(float(k), d_v, du_step) for k in ks])
    i = int(np.argmax(ev))
    if ev[i] <= 1.0:
        return None
    lo = hi = i
    while lo > 0 and ev[lo - 1] > 1.0:
        lo -= 1
    while hi < len(ks) - 1 and ev[hi + 1] > 1.0:
        hi += 1
    return float(ks[lo]), float(ks[hi]), float(ks[i]), float(math.log(ev[i]) / DT)


def verify_registration() -> None:
    """Vorab-Registrierung gegen Neuberechnung prüfen (Integrität)."""
    for dv, reg in REG.items():
        b = exact_band(dv, D_X)
        assert b is not None, f"D_v={dv} sollte instabil sein"
        lo, hi, k_star, sig = b
        r_lo, r_hi = reg["band"]
        assert abs(lo - r_lo) < 5e-3 and abs(hi - r_hi) < 5e-3, (dv, lo, hi)
        assert abs(k_star - reg["k_star"]) < 5e-3, (dv, k_star)
        assert abs(sig * DT - reg["sigma_star_step"]) < 1e-6, (dv, sig)
        for shell, rate in reg.get("shells", {}).items():
            meas = math.log(eig_max_step(shell, dv, D_X))  # pro Schritt
            assert abs(meas - rate) < 3e-5, (dv, shell, meas, rate)


def tau_leap(x: np.ndarray, y: np.ndarray, rng: np.random.Generator
             ) -> tuple[np.ndarray, np.ndarray]:
    lam_r3 = np.minimum(K1 * DT * x.astype(np.float64) ** 2 * y / OMEGA**2, 1e6)
    lam_r2 = np.minimum(K2 * DT * x.astype(np.float64), 1e6)
    n_r3 = np.minimum(rng.poisson(lam_r3), y)
    n_r2 = np.minimum(rng.poisson(lam_r2), x)
    x = x + rng.poisson(OMEGA * A_FEED * DT, size=x.shape) + n_r3 - n_r2
    y = y + rng.poisson(OMEGA * B_FEED * DT, size=y.shape) - n_r3
    return x, y


def run_config(name: str, grid: int, n_steps: int, d_v: float, seeds: tuple[int, ...],
               cfg_idx: int, null: bool) -> dict:
    """Ein Lauf: Zeitverläufe (Schalenleistung, band_power, mean_x, std_x)
    + Finale Spektren. null=True: D_u = D_v (isotrope Kontrolle)."""
    shape = (grid, grid, grid)
    fp_x = OMEGA * (A_FEED + B_FEED)
    fp_y = 520.0  # iter-17: Y* = B/(K1·u*²) am gemessenen Arbeitspunkt
    results: dict = {"name": name, "grid": grid, "n_steps": n_steps,
                     "d_v": d_v, "null": null, "seeds": {}}
    shell_centers = _shell_centers(grid)
    n_sub = max(1, int(math.ceil(d_v / 0.3)))
    p_sub = d_v / n_sub
    for seed in seeds:
        rng = make_rng(seed, 17, cfg_idx)
        x = rng.poisson(fp_x, size=shape).astype(np.int64)
        y = rng.poisson(fp_y, size=shape).astype(np.int64)
        timecourse: list[dict] = []
        for step in range(n_steps + 1):
            if step % SNAP_EVERY == 0:
                timecourse.append(_snapshot(step, x, y, shell_centers))
            if step == n_steps:
                break
            x, y = tau_leap(x, y, rng)
            xd = {"X": x}
            if null:
                # Isotrope Kontrolle: X mit demselben Subschritt-Schema
                # wie Y (per-Schritt-Varianz identisch D_u = D_v = d_v).
                for _ in range(n_sub):
                    stochastic_jump_diffusion(xd, p_sub, rng)
            else:
                stochastic_jump_diffusion(xd, D_X, rng)
            x = xd["X"]
            yd = {"Y": y}
            for _ in range(n_sub):
                stochastic_jump_diffusion(yd, p_sub, rng)
            y = yd["Y"]
        kw, gp = radial_power_spectrum(x.astype(np.float64))
        seed_res = {
            "timecourse": timecourse,
            "final_k": [round(v, 4) for v in kw],
            "final_power": [round(v, 4) for v in gp],
            "mean_x_final": float(x.mean()),
            "mean_y_final": float(y.mean()),
        }
        results["seeds"][str(seed)] = seed_res
        LOG.info("  %s seed=%d fertig (mean_x=%.1f, mean_y=%.1f)",
                 name, seed, seed_res["mean_x_final"], seed_res["mean_y_final"])
    return results


def _shell_centers(grid: int) -> tuple[float, ...]:
    base = 2.0 * math.pi / grid
    rs = (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 16)
    return tuple(base * math.sqrt(r) for r in rs)


def _snapshot(step: int, x: np.ndarray, y: np.ndarray,
              centers: tuple[float, ...]) -> dict:
    fx = x.astype(np.float64) - x.mean()
    fy = y.astype(np.float64) - y.mean()
    px = np.abs(np.fft.fftn(fx)) ** 2
    py = np.abs(np.fft.fftn(fy)) ** 2
    n = x.shape[0]
    base = 2.0 * math.pi / n
    idx = np.indices(px.shape)
    kmag = np.sqrt(sum(idx[a] ** 2 for a in range(3)))
    kmag = np.where(kmag > n // 2, n - kmag, kmag) * (base)
    shells = {}
    for c in centers:
        sel = np.abs(kmag - c) < 0.004
        if sel.any():
            shells[round(c, 5)] = float(px[sel].mean())
    band = sum(v for k, v in shells.items() if 0.104 <= k <= 0.270)
    shells_y = {}
    for c in centers:
        sel = np.abs(kmag - c) < 0.004
        if sel.any():
            shells_y[round(c, 5)] = float(py[sel].mean())
    return {"step": step,
            "shells_x": shells,
            "band_power_x": band,
            "band_power_y": sum(v for k, v in shells_y.items()
                                if 0.104 <= k <= 0.270),
            "std_x": float(x.std()),
            "std_y": float(y.std()),
            "mean_x": float(x.mean())}


def main() -> None:
    out = Path(__file__).parent
    verify_registration()
    LOG.info("Vorab-Registrierung verifiziert (exakte Abbildung reproduziert).")
    configs = [
        ("anchor_L24", 24, 800, 3.0, (300,), False, 0),
        ("stable025", 48, 800, 0.25, (300, 301), False, 1),
        ("stable10", 48, 800, 1.0, (300, 301), False, 2),
        ("turing3", 48, 1600, 3.0, (300, 301), False, 3),
        ("turing10", 48, 1600, 10.0, (300,), False, 4),
        ("null3", 48, 800, 3.0, (300, 301), True, 6),
        ("null10", 48, 400, 10.0, (300,), True, 7),
    ]
    all_results = {}
    for name, grid, n_steps, d_v, seeds, null, cfg_idx in configs:
        LOG.info("Laufe %s (L=%d, T=%d, D_v=%.2f, null=%s)",
                 name, grid, n_steps, d_v, null)
        all_results[name] = run_config(name, grid, n_steps, d_v, seeds,
                                       cfg_idx, null)
    (out / "result.json").write_text(json.dumps(all_results, indent=1))
    LOG.info("result.json geschrieben.")


if __name__ == "__main__":
    main()
