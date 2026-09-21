#!/usr/bin/env python
"""iter-18 / VECTOR_OR_KERNEL: OR-Kollaps-Kern vs. gematchte klassische
Kontrolle — Ereignis-Muster-Diskrimination mit Readout-Dünnungs-Leiter.

VORAB REGISTRIERTE KRITERIA (fixiert vor dem Lauf; 2026-09-21)
==============================================================

Arme (je 3 Seeds, base_seed 400, cond_idx 0/1/2):
  or_kernel    ORCollapseKernel, Defaults = iter-16-Ecke
               (Gate ON, ratio 0.61, hazard dt/τ_OR @ dt=1e-4),
               cluster_size 16, n_sites 4096, T 4000 Schritte.
  classical    gematchte Kontrolle: K' ~ Poisson(h·K) Events/Schritt,
               Sites uniform unabhängig — identische mittlere
               Gesamt-Ereignisrate, kein kollektives Muster.
  shuffled     OR-Matrix mit permutierten Site-Labels — Marginals exakt
               erhalten, Clusterstruktur zerstört (S3-Negativkontrolle).

Dünnungs-Leiter: jedes wahre Event wird unabhängig mit q beobachtet,
q ∈ {1.0, 0.5, 0.1} (Binomial-Dünnung der Event-Matrix).

Observablen (h ≈ 0.66, K = 16, p = h/N_Cluster ≈ 0.0026):
  S1  Fano der per-Schritt-Serien: OR ≈ (1−q) + (1−h)·K·q
      = 5.40 / 3.20 / 1.44 bei q = 1 / 0.5 / 0.1; klassisch ≈ 1.
  S2  Fano der per-Voxel-Counts. [VORAB REGISTRIERT: 1−h = 0.34 —
      KORREKTUR-LOG: falsch, korrekt ist 1 − p ≈ 0.997 (die Cluster-
      Wahl ist uniform, per-Cluster-Counts ~ Binomial(T, p) → Rand
      nahezu Poisson). Messung 0.88–1.01 bestätigt die Korrektur;
      S2 hat in diesem Design KEINE Trennkraft — die kollektive
      Signatur lebt in S1+S3, nicht in Voxel-Marginals.]
  S3  Within-Cluster-Korrelation (15 Positionspaare × 256 Cluster):
      OR ≈ q·(1−p)/(1−p·q) → ≈ 1.00 / 0.50 / 0.10 bei q = 1 / 0.5 / 0.1.
      [VORAB REGISTRIERT mit h statt p: 0.25 / 0.036 — KORREKTUR-LOG:
      in die Korrelationsformel gehört die per-Cluster-Feuer-
      wahrscheinlichkeit p = h/256, nicht h. Messung (0.49 / 0.10)
      bestätigt die korrigierte Formel.] klassisch ≈ 0.
      Permutationstest: 200 Site-Label-Permutationen, letzte 1000
      Schritte.

Verdicts:
  DISTINGUISHED_q  [p_S3 < 0.005 UND z_S3 > 4] ODER
                   [p_S1 < 0.01 UND Fano_step(OR) ≥ 3·Fano_step(classical)]
  CONTROL_INVALID  Fano_step(classical, q=1) ∉ [0.8, 1.25] bei irgendeinem
                   Seed
  SIGNATURE_ROBUST       DISTINGUISHED bei q=0.1 in allen Seeds
  SIGNATURE_DETECTABLE   DISTINGUISHED bei q ∈ {1.0, 0.5} in allen Seeds,
                         nicht bei q=0.1
  INDISTINGUISHABLE      nicht DISTINGUISHED bei q=1

CLAIM-DECKEL (C2): Die Kollektivität ist per Konstruktion EINGEBAUT
(ein Draw → K Sites). Das Experiment prüft, ob die beiden GENERATIVEN
Modelle an den vorab registrierten Statistiken unterscheidbar sind und
welche Statistik welchen Readout-Verlust überlebt — es ist KEIN Nachweis
von Kollaps-Physik und KEINE Natur-Messung.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

from cellsim.core.rng import make_rng
from cellsim.modules.orch_or import ORCollapseKernel, ORConfig

BASE_SEED = 400
SEEDS = (0, 1, 2)
N_SITES = 4096
CLUSTER_SIZE = 16
N_CLUSTERS = N_SITES // CLUSTER_SIZE
T_STEPS = 4000
DT_S = 1e-4
Q_LEVELS = (1.0, 0.5, 0.1)
N_PERM_S1 = 2000
N_PERM_S3 = 200
S3_SUB_STEPS = 1000
OUT_DIR = Path(__file__).resolve().parent / "out"

ARM_OR, ARM_CLASSICAL, ARM_SHUFFLED = 0, 1, 2


def make_kernel() -> ORCollapseKernel:
    return ORCollapseKernel(
        config=ORConfig(), cluster_size=CLUSTER_SIZE, dt_s=DT_S
    )


def kernel_meta() -> dict[str, float | bool]:
    kernel = make_kernel()
    return {
        "tau_or_s": kernel.tau_or_s,
        "tau_dec_s": kernel.tau_dec_s,
        "ratio": kernel.ratio,
        "hazard": kernel.hazard_per_step(),
        "gate_on": kernel.gate_on,
    }


def simulate_or(rng: np.random.Generator) -> np.ndarray:
    """OR-Arm: Kollaps-Feuermarken als (T, n_sites)-bool-Matrix."""
    kernel = make_kernel()
    matrix = np.zeros((T_STEPS, N_SITES), dtype=bool)
    for t in range(T_STEPS):
        sites = kernel.step(rng, N_SITES)
        if sites:
            matrix[t, sites] = True
    return matrix


def simulate_classical(
    rng: np.random.Generator, hazard: float
) -> np.ndarray:
    """Matched Kontrolle: gleiche mittlere Rate, unabhängige Sites."""
    matrix = np.zeros((T_STEPS, N_SITES), dtype=bool)
    for t in range(T_STEPS):
        n_events = int(rng.poisson(hazard * CLUSTER_SIZE))
        if n_events:
            sites = rng.choice(N_SITES, size=n_events, replace=False)
            matrix[t, sites] = True
    return matrix


def thin(
    matrix: np.ndarray, q: float, rng: np.random.Generator
) -> np.ndarray:
    """Jedes wahre Event unabhängig mit q beobachtet (zeilenweise)."""
    out = np.zeros(matrix.shape, dtype=bool)
    for t in range(matrix.shape[0]):
        out[t] = matrix[t] & (rng.random(N_SITES) < q)
    return out


def fano(counts: np.ndarray) -> float:
    mean = float(np.mean(counts))
    if mean <= 0.0:
        return float("nan")
    return float(np.var(counts)) / mean


def within_cluster_corr(matrix: np.ndarray) -> float:
    """Mittel der Pearson-Korrelationen benachbarter Voxel-Positionen
    über die letzten S3_SUB_STEPS Schritte (binär-exakt über Mittel)."""
    sub = matrix[-S3_SUB_STEPS:].reshape(
        S3_SUB_STEPS, N_CLUSTERS, CLUSTER_SIZE
    )
    x = sub[:, :, :-1]
    y = sub[:, :, 1:]
    p_x = x.mean(axis=(0, 1))
    p_y = y.mean(axis=(0, 1))
    p_xy = (x & y).mean(axis=(0, 1))
    var_x = p_x * (1.0 - p_x)
    var_y = p_y * (1.0 - p_y)
    denom = np.sqrt(var_x * var_y)
    corrs = np.divide(
        p_xy - p_x * p_y,
        denom,
        out=np.zeros_like(p_xy),
        where=denom > 1e-12,
    )
    return float(corrs.mean())


def perm_s3(
    matrix: np.ndarray, rng: np.random.Generator
) -> tuple[float, float, float]:
    """S3-Statistik + Permutations-p (Site-Labels permutieren) + z."""
    stat_obs = within_cluster_corr(matrix)
    stat_perm = np.empty(N_PERM_S3)
    for i in range(N_PERM_S3):
        perm = rng.permutation(N_SITES)
        stat_perm[i] = within_cluster_corr(matrix[:, perm])
    p = (float(np.sum(stat_perm >= stat_obs)) + 1.0) / (N_PERM_S3 + 1.0)
    n_samples = S3_SUB_STEPS * N_CLUSTERS
    z = stat_obs * math.sqrt(n_samples)
    return p, z, stat_obs


def perm_s1_fano(
    t_or: np.ndarray,
    t_cl: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    """S1: Fano der per-Schritt-Serien + Label-Swap-Permutations-p."""
    ser_or = t_or.sum(axis=1).astype(np.float64)
    ser_cl = t_cl.sum(axis=1).astype(np.float64)
    fano_or = fano(ser_or)
    fano_cl = fano(ser_cl)
    diff_obs = fano_or - fano_cl
    pool = np.concatenate([ser_or, ser_cl])
    n = len(ser_or)
    count = 0
    for _ in range(N_PERM_S1):
        rng.shuffle(pool)
        d = fano(pool[:n]) - fano(pool[n:])
        if abs(d) >= abs(diff_obs):
            count += 1
    p = (count + 1.0) / (N_PERM_S1 + 1.0)
    return fano_or, fano_cl, p


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    kernel = make_kernel()
    hazard = kernel.hazard_per_step()
    print(
        f"[kernel] tau_or={kernel.tau_or_s:.4e}s tau_dec={kernel.tau_dec_s:.4e}s"
        f" ratio={kernel.ratio:.4f} hazard={hazard:.4f} gate_on={kernel.gate_on}"
    )
    print(
        f"[theorie] Fano_step(OR)=(1-q)+(1-h)*K*q: 5.40/3.20/1.44 bei"
        f" q=1/0.5/0.1 (klassisch 1); Fano_voxel(OR)=1-h/N_cluster="
        f"{1.0 - hazard / (N_SITES / CLUSTER_SIZE):.3f} (klassisch 1);"
        f" S3 corr(q)=q*(1-p)/(1-p*q) mit p=h/N_cluster="
        f"{hazard / (N_SITES / CLUSTER_SIZE):.4f} -> ~q"
    )

    runs: list[dict[str, object]] = []
    for seed in SEEDS:
        rng_or = make_rng(BASE_SEED, seed, ARM_OR)
        m_or = simulate_or(rng_or)
        rng_cl = make_rng(BASE_SEED, seed, ARM_CLASSICAL)
        m_cl = simulate_classical(rng_cl, hazard)
        rng_sh = make_rng(BASE_SEED, seed, ARM_SHUFFLED)
        m_sh = m_or[:, rng_sh.permutation(N_SITES)]

        control_fano_q1 = fano(m_cl.sum(axis=1).astype(np.float64))
        control_ok = 0.8 <= control_fano_q1 <= 1.25

        or_rows: list[dict[str, object]] = []
        cl_rows: list[dict[str, object]] = []
        sh_rows: list[dict[str, object]] = []
        for q_idx, q in enumerate(Q_LEVELS):
            rng_q = make_rng(BASE_SEED, seed, 10 + q_idx)
            t_or = thin(m_or, q, rng_q)
            t_cl = thin(m_cl, q, rng_q)
            fano_or_step, fano_cl_step, p_s1 = perm_s1_fano(t_or, t_cl, rng_q)
            fano_or_voxel = fano(t_or.sum(axis=0).astype(np.float64))
            fano_cl_voxel = fano(t_cl.sum(axis=0).astype(np.float64))
            rng_s3 = make_rng(BASE_SEED, seed, 20 + q_idx)
            p_s3, z_s3, corr_or = perm_s3(t_or, rng_s3)
            rng_s3sh = make_rng(BASE_SEED, seed, 30 + q_idx)
            p_s3sh, z_s3sh, corr_sh = perm_s3(t_sh := thin(m_sh, q, rng_q), rng_s3sh)
            distinguished = (p_s3 < 0.005 and z_s3 > 4.0) or (
                p_s1 < 0.01
                and fano_or_step >= 3.0 * max(fano_cl_step, 1e-12)
            )
            or_rows.append(
                {
                    "q": q,
                    "fano_step": fano_or_step,
                    "fano_voxel": fano_or_voxel,
                    "s3_corr": corr_or,
                    "p_s1": p_s1,
                    "p_s3": p_s3,
                    "z_s3": z_s3,
                    "distinguished": bool(distinguished),
                }
            )
            cl_rows.append(
                {
                    "q": q,
                    "fano_step": fano_cl_step,
                    "fano_voxel": fano_cl_voxel,
                }
            )
            sh_rows.append(
                {
                    "q": q,
                    "s3_corr": corr_sh,
                    "p_s3": p_s3sh,
                    "z_s3": z_s3sh,
                }
            )
        runs.append(
            {
                "seed": seed,
                "control_fano_step_q1": control_fano_q1,
                "control_ok": control_ok,
                "or": or_rows,
                "classical": cl_rows,
                "shuffled": sh_rows,
            }
        )
        or_q1 = or_rows[0]
        print(
            f"[seed {seed}] control-Fano(q=1)={control_fano_q1:.3f}"
            f" ok={control_ok} | OR Fano_step={or_q1['fano_step']:.2f}"
            f" Fano_voxel={or_q1['fano_voxel']:.2f}"
            f" S3 corr={or_q1['s3_corr']:.3f} p={or_q1['p_s3']:.4f}"
            f" | shuffled S3 corr={sh_rows[0]['s3_corr']:.3f}"
        )

    def n_distinguished(q: float) -> int:
        return sum(
            1
            for row in runs
            for rr in row["or"]
            if rr["q"] == q and rr["distinguished"]
        )

    control_all_ok = all(bool(row["control_ok"]) for row in runs)
    if not control_all_ok:
        final = "CONTROL_INVALID"
    elif n_distinguished(0.1) == len(SEEDS):
        final = "SIGNATURE_ROBUST"
    elif n_distinguished(1.0) == len(SEEDS) and n_distinguished(0.5) == len(SEEDS):
        final = "SIGNATURE_DETECTABLE"
    elif n_distinguished(1.0) == len(SEEDS):
        final = "SIGNATURE_ROBUST_PARTIAL"
    else:
        final = "INDISTINGUISHABLE"
    verdicts = {
        "final": final,
        "n_distinguished_q1.0": n_distinguished(1.0),
        "n_distinguished_q0.5": n_distinguished(0.5),
        "n_distinguished_q0.1": n_distinguished(0.1),
        "n_seeds": len(SEEDS),
        "control_all_ok": control_all_ok,
    }
    print(f"[verdict] {final} | {verdicts}")

    result = {
        "experiment": "iter-18_or_discrimination",
        "config": {
            "base_seed": BASE_SEED,
            "n_sites": N_SITES,
            "cluster_size": CLUSTER_SIZE,
            "n_clusters": N_CLUSTERS,
            "t_steps": T_STEPS,
            "dt_s": DT_S,
            "q_levels": list(Q_LEVELS),
            "n_perm_s1": N_PERM_S1,
            "n_perm_s3": N_PERM_S3,
            "s3_sub_steps": S3_SUB_STEPS,
        },
        "kernel": kernel_meta(),
        "runs": runs,
        "verdicts": verdicts,
        "walltime_s": time.perf_counter() - t0,
    }
    out = OUT_DIR / "result.json"
    out.write_text(json.dumps(result, indent=2, default=float))
    print(f"[done] {out}")


if __name__ == "__main__":
    main()
