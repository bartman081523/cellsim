"""Vier Standard-Plots für L3-Output."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def write_all_plots(
    series: dict[str, np.ndarray],
    crowding_proxy: np.ndarray,
    out_dir: Path,
) -> dict[str, Path]:
    """Erzeugt die vier Standard-Plots (matplotlib, keine Style-Annahmen)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    plots: dict[str, Path] = {}

    # 1) Radius vs. Zeit
    f1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(series["time_s"], series["radius_nm"], label="radius_nm")
    ax1.set_xlabel("time_s")
    ax1.set_ylabel("radius_nm")
    ax1.set_title("Zellradius vs. Zeit")
    ax1.grid(alpha=0.3)
    f1.tight_layout()
    p1 = out_dir / "radius_vs_time.png"
    f1.savefig(p1, dpi=110)
    plt.close(f1)
    plots["radius_vs_time"] = p1

    # 2) ATP vs. Zeit
    f2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(series["time_s"], series["atp_mM"], label="atp_mM", color="tab:orange")
    ax2.set_xlabel("time_s")
    ax2.set_ylabel("ATP (mM)")
    ax2.set_title("ATP-Haushalt vs. Zeit")
    ax2.grid(alpha=0.3)
    f2.tight_layout()
    p2 = out_dir / "atp_vs_time.png"
    f2.savefig(p2, dpi=110)
    plt.close(f2)
    plots["atp_vs_time"] = p2

    # 3) Crowding-Proxy (Zeitreihe, da 3D-Heatmap ohne RDME-Snapshot nicht trivial)
    f3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(series["time_s"], crowding_proxy, label="crowding_proxy", color="tab:green")
    ax3.set_xlabel("time_s")
    ax3.set_ylabel("crowding_index (proxy)")
    ax3.set_title("Crowding-Proxy vs. Zeit")
    ax3.grid(alpha=0.3)
    f3.tight_layout()
    p3 = out_dir / "crowding_proxy_vs_time.png"
    f3.savefig(p3, dpi=110)
    plt.close(f3)
    plots["crowding_proxy_vs_time"] = p3

    # 4) Sync-Zeitpunkte
    f4, ax4 = plt.subplots(figsize=(6, 4))
    sync_times = series["time_s"][series["sync_count"] > 0]
    if sync_times.size > 0:
        ax4.vlines(sync_times, ymin=0.0, ymax=1.0, color="tab:red", alpha=0.4, label="sync tick")
    ax4.plot(series["time_s"], series["particles_total"], label="particles_total", color="tab:blue")
    ax4.set_xlabel("time_s")
    ax4.set_ylabel("particles_total")
    ax4.set_title("Solver-Sync-Zeitpunkte über Partikel-Zeitreihe")
    ax4.legend()
    ax4.grid(alpha=0.3)
    f4.tight_layout()
    p4 = out_dir / "sync_ticks.png"
    f4.savefig(p4, dpi=110)
    plt.close(f4)
    plots["sync_ticks"] = p4

    logger.info("Wrote %d plots → %s", len(plots), out_dir)
    return plots
