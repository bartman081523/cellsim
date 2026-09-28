"""PILOT-Diagnose (keine Verdict-Promotion): Regime-Sonde für AMP/eps/D.

Frage des Pilot-Befunds: median n_cores = 0 bei eps<=0.05 — liegt es an
der Antriebs-Amplitude (A=0.5, quasi-statisch vermutlich unterm Zünd-
Knie) oder an der Dynamik? Kern-Flaechen distinguishen Linien-Artefakte
(Phasen-Slip-Kanten, maxArea riesig) von Punkt-Kernen (Flaeche ~1-12).
"""

from __future__ import annotations

import numpy as np
import v2_model as m


def probe(amp, seed, eps, d_par, label):
    rng = np.random.default_rng(seed * 16 + m.SCHED_IDX["story_listen"])
    u = m.U_REST + rng.normal(0.0, m.NOISE_INIT, (m.L, m.L))
    v = m.V_REST + rng.normal(0.0, m.NOISE_INIT, (m.L, m.L))
    masks = {task: m.spatial_mask(task) for task in m.BANDS}
    old_amp = m.AMP
    m.AMP = amp
    print(f"--- {label}: AMP={amp} eps={eps} D={d_par} seed={seed} ---")
    for t in range(m.STEPS):
        drv = m.drive_amplitude("listen", t) * masks["story"]
        u_new = u + m.DT * (u - u**3 / 3.0 - v + d_par * m.laplacian(u) + drv)
        u_new += rng.normal(0.0, m.NOISE_STEP, (m.L, m.L))
        v = v + m.DT * eps * (u_new + m.A_PAR - m.B_PAR * v)
        u = u_new
        if (t + 1) % m.SNAP_EVERY == 0:
            fi = (t + 1) // m.SNAP_EVERY - 1
            if fi in (0, 2, 5, 10, 20, 40, 80, 150, 250, 399):
                _vort, cores = m.frame_cores(u, v)
                areas = [c["area"] for c in cores]
                n_pt = sum(1 for a in areas if a <= 12)
                print(
                    f"  frame {fi:3d}: n={len(areas):5d} "
                    f"punktartig={n_pt:5d} "
                    f"maxArea={max(areas) if areas else 0:6d} "
                    f"uRange=({u.min():+.2f},{u.max():+.2f})"
                )
    m.AMP = old_amp


for cfg in (
    (0.5, 0.05, 0.6),
    (1.5, 0.05, 0.6),
    (3.0, 0.05, 0.6),
    (3.0, 0.08, 0.3),
):
    amp, eps, d_par = cfg
    probe(amp, 1400, eps, d_par, f"A{amp}_e{eps}_D{d_par}")
