"""PILOT-Diagnose 2 (keine Verdict-Promotion): Aktivitaets-Maske + Rausch-Fragmentierung.

Frage 1: killt eine Aktivitaets-Domaine (Radius zum Ruh-Punkt) die
         Rausch-Phasen-Kerne der Ruh-Frames, ohne echte Spiralkerne
         zu beruehren?
Frage 2: nucleiert bei groeberem Per-Schritt-Rauschen (0.05 / 0.10 wie
         Korpus-sigma) anhaltende Spiral-Turbulenz (median n_cores,
         quant-Fraktion)?
"""

from __future__ import annotations

import numpy as np
import v2_model as m
from scipy import ndimage

ACT_THRESH = 0.5
POINT_AREA_MAX = 12


def cores_masked(u, v):
    theta = np.arctan2(v - v.mean(), u - u.mean())
    vort = m.plaquette_vorticity(theta)
    act = np.hypot(u - m.U_REST, v - m.V_REST)
    pm = (act[:-1, :-1] + act[1:, :-1] + act[:-1, 1:] + act[1:, 1:]) / 4.0
    vort_m = np.where(pm > ACT_THRESH, vort, 0.0)
    labels, n = ndimage.label(np.abs(vort_m) > m.VORT_THRESHOLD)
    cores = []
    if n:
        flat = labels.ravel()
        counts = np.bincount(flat, minlength=n + 1)[1:]
        sums = np.bincount(flat, weights=vort_m.ravel(), minlength=n + 1)[1:]
        coms = ndimage.center_of_mass(
            np.ones_like(vort_m), labels, list(range(1, n + 1))
        )
        for cnt, sm, com in zip(counts, sums, coms, strict=False):
            q = float(sm) / int(cnt)
            cores.append(
                {
                    "row": float(com[0]),
                    "col": float(com[1]),
                    "charge": q,
                    "area": int(cnt),
                    "quant": m.QUANT_LO <= abs(q) <= m.QUANT_HI,
                }
            )
    return cores


def run_probe(noise_step, amp, seed, eps=0.05, d_par=0.6):
    rng = np.random.default_rng(seed * 16 + m.SCHED_IDX["story_listen"])
    u = m.U_REST + rng.normal(0.0, m.NOISE_INIT, (m.L, m.L))
    v = m.V_REST + rng.normal(0.0, m.NOISE_INIT, (m.L, m.L))
    masks = {task: m.spatial_mask(task) for task in m.BANDS}
    old_amp = m.AMP
    m.AMP = amp
    nc_frames = []
    q_frames = []
    for t in range(m.STEPS):
        drv = m.drive_amplitude("listen", t) * masks["story"]
        u_new = u + m.DT * (u - u**3 / 3.0 - v + d_par * m.laplacian(u) + drv)
        u_new += rng.normal(0.0, noise_step, (m.L, m.L))
        v = v + m.DT * eps * (u_new + m.A_PAR - m.B_PAR * v)
        u = u_new
        if (t + 1) % m.SNAP_EVERY == 0:
            fi = (t + 1) // m.SNAP_EVERY - 1
            cores = cores_masked(u, v)
            nc_frames.append(len(cores))
            if cores:
                q_frames.append(float(np.mean([c["quant"] for c in cores])))
                n_pt = sum(1 for c in cores if c["area"] <= POINT_AREA_MAX)
            else:
                q_frames.append(0.0)
                n_pt = 0
            if fi in (0, 2, 10, 40, 100, 200, 300, 399):
                print(
                    f"  frame {fi:3d}: n={len(cores):4d} punkt={n_pt:4d} "
                    f"maxA={max((c['area'] for c in cores), default=0):4d} "
                    f"quant={q_frames[-1]:.2f}"
                )
    m.AMP = old_amp
    n_med = float(np.median(nc_frames[50:]))
    q_med = float(np.median([q for q in q_frames[50:] if q > 0])) if any(
        q > 0 for q in q_frames[50:]
    ) else 0.0
    print(
        f"  SUMMARY sigma_n={noise_step} AMP={amp}: median n_cores "
        f"(frames 50+)= {n_med:.1f}, median quant(core-frames)={q_med:.2f}"
    )


for sigma_n, amp in ((0.05, 0.5), (0.05, 2.0), (0.1, 0.5), (0.1, 2.0)):
    print(f"--- sigma_n={sigma_n} AMP={amp} (eps=0.05, D=0.6) ---")
    run_probe(sigma_n, amp, 1400)
