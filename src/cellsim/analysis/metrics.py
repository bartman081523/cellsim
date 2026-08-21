"""L3-Metriken mit _mean/_sem-Suffix-Konvention (MT_Sim)."""

from __future__ import annotations

import csv
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class L3Metrics:
    """Aggregierte Metriken aus einem Simulations-Lauf."""

    growth_rate_mean_nm_per_s: float
    growth_rate_sem_nm_per_s: float
    atp_ss_mean_mM: float
    atp_ss_sem_mM: float
    crowding_index_mean: float
    crowding_index_sem: float
    rdme_steps_per_sec_mean: float
    rdme_steps_per_sec_sem: float


def _sem(values: np.ndarray) -> float:
    """Standard Error of Mean."""
    n = len(values)
    if n < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(n))


def compute_metrics(
    time_s: np.ndarray,
    radius_nm: np.ndarray,
    atp_mM: np.ndarray,
    crowding_index: np.ndarray,
    rdme_steps: np.ndarray,
    particles_total: np.ndarray,
    t_ss_start_s: float = 30.0,
) -> L3Metrics:
    """Berechnet L3-Metriken aus Zeitreihen.

    - growth_rate: lineare Regression auf radius_nm in steady-state-Phase
    - atp_ss: Mittelwert von ATP ab t_ss_start_s
    - crowding_index: Mittelwert der räumlichen Crowding-Indizes
    - rdme_steps_per_sec: mittlere Schritt-Rate
    """
    time_s = np.asarray(time_s, dtype=np.float64)
    radius_nm = np.asarray(radius_nm, dtype=np.float64)
    atp_mM = np.asarray(atp_mM, dtype=np.float64)

    # Growth rate: linear slope in steady-state
    mask = time_s >= t_ss_start_s
    if mask.sum() < 2:
        mask = np.ones_like(time_s, dtype=bool)
    t_ss = time_s[mask]
    r_ss = radius_nm[mask]
    if len(t_ss) >= 2 and (t_ss.max() - t_ss.min()) > 0:
        slope, _ = np.polyfit(t_ss, r_ss, deg=1)
        growth_rates = np.full(len(t_ss), slope)
    else:
        growth_rates = np.zeros(1)

    # ATP steady-state
    atp_ss = atp_mM[time_s >= t_ss_start_s] if (time_s >= t_ss_start_s).any() else atp_mM

    # RDME steps/sec
    dt = np.diff(time_s)
    dr = np.diff(rdme_steps)
    rate = dr / np.maximum(dt, 1e-9)
    rate = rate[np.isfinite(rate)]

    return L3Metrics(
        growth_rate_mean_nm_per_s=float(np.mean(growth_rates)) if growth_rates.size else 0.0,
        growth_rate_sem_nm_per_s=_sem(growth_rates),
        atp_ss_mean_mM=float(np.mean(atp_ss)) if atp_ss.size else 0.0,
        atp_ss_sem_mM=_sem(atp_ss),
        crowding_index_mean=float(np.mean(crowding_index)),
        crowding_index_sem=_sem(crowding_index),
        rdme_steps_per_sec_mean=float(np.mean(rate)) if rate.size else 0.0,
        rdme_steps_per_sec_sem=_sem(rate),
    )


def metrics_to_row(metrics: L3Metrics, tag: str = "smoke") -> dict[str, str]:
    """Konvertiert Metriken in eine CSV-Zeile (Suffix _mean/_sem)."""
    return {
        "tag": tag,
        "growth_rate_mean_nm_per_s": f"{metrics.growth_rate_mean_nm_per_s:.6f}",
        "growth_rate_sem_nm_per_s": f"{metrics.growth_rate_sem_nm_per_s:.6f}",
        "atp_ss_mean_mM": f"{metrics.atp_ss_mean_mM:.6f}",
        "atp_ss_sem_mM": f"{metrics.atp_ss_sem_mM:.6f}",
        "crowding_index_mean": f"{metrics.crowding_index_mean:.6e}",
        "crowding_index_sem": f"{metrics.crowding_index_sem:.6e}",
        "rdme_steps_per_sec_mean": f"{metrics.rdme_steps_per_sec_mean:.3f}",
        "rdme_steps_per_sec_sem": f"{metrics.rdme_steps_per_sec_sem:.3f}",
    }


def write_summary_csv(metrics: L3Metrics, out_path, tag: str = "smoke") -> None:
    """Schreibt eine einzelne summary.csv (eine Zeile)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    row = metrics_to_row(metrics, tag=tag)
    fieldnames = list(row.keys())
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
