"""Analyse-Pipeline: 4 CSVs (raw, pairs, discriminations, summary).

MT_Sim-Konvention aus `analyze_results.py`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from cellsim.analysis.metrics import compute_metrics, metrics_to_row
from cellsim.analysis.plots import write_all_plots
from cellsim.driver.loop import DriverResult

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Output-Verzeichnis und Kern-Metriken."""

    out_dir: Path
    run_csv: Path = field(default_factory=lambda: Path())
    pairs_csv: Path = field(default_factory=lambda: Path())
    discriminations_csv: Path = field(default_factory=lambda: Path())
    summary_csv: Path = field(default_factory=lambda: Path())
    manifest_path: Path = field(default_factory=lambda: Path())
    plots: dict[str, Path] = field(default_factory=dict)


def _read_run_csv(run_csv: Path) -> dict[str, np.ndarray]:
    """Liest run.csv in ein Dict von Arrays."""
    data: dict[str, list[float]] = {}
    with run_csv.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            for k, v in row.items():
                data.setdefault(k, []).append(float(v))
    return {k: np.asarray(v, dtype=np.float64) for k, v in data.items()}


def _write_pairs_csv(out_path: Path, series_a: dict[str, np.ndarray], series_b: dict[str, np.ndarray]) -> None:
    """Schreibt pairs.csv: HYP/ANT-gepaart mit _H/_A-Suffix."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted(set(series_a.keys()) & set(series_b.keys()))
    if "time_s" in keys:
        keys.remove("time_s")
        keys.insert(0, "time_s")
    fieldnames = ["time_s"]
    for k in keys[1:]:
        fieldnames.extend([f"{k}_H", f"{k}_A", f"{k}_gap", f"{k}_ratio"])
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(fieldnames)
        n = len(series_a["time_s"])
        for i in range(n):
            row: list[str] = [f"{series_a['time_s'][i]:.6f}"]
            for k in keys[1:]:
                a = float(series_a[k][i]) if i < len(series_a[k]) else 0.0
                b = float(series_b[k][i]) if i < len(series_b[k]) else 0.0
                row.extend([f"{a:.6f}", f"{b:.6f}", f"{a - b:.6f}", f"{a / max(b, 1e-30):.6e}"])
            writer.writerow(row)


def _write_discriminations_csv(
    out_path: Path, series: dict[str, np.ndarray]
) -> None:
    """Welche Variable dominiert (höchste Varianz)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for k, v in series.items():
        if k == "time_s":
            continue
        if v.size < 2:
            continue
        rows.append(
            {
                "metric": k,
                "mean": float(v.mean()),
                "std": float(v.std()),
                "cv": float(v.std() / max(abs(v.mean()), 1e-30)),
                "min": float(v.min()),
                "max": float(v.max()),
            }
        )
    rows.sort(key=lambda r: r["std"], reverse=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["metric", "mean", "std", "cv", "min", "max"])
        writer.writeheader()
        writer.writerows(rows)


def _write_manifest(manifest_path: Path, run_csv: Path, seed: int, walltime_s: float) -> None:
    """Schreibt manifest.json mit Seed + Hash + Walltime."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "run_csv": str(run_csv),
        "run_csv_sha256": hashlib.sha256(run_csv.read_bytes()).hexdigest(),
        "seed": seed,
        "walltime_s": walltime_s,
    }
    manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_analysis(
    result: DriverResult,
    out_dir: Path,
    tag: str = "smoke",
    write_plots: bool = True,
) -> AnalysisResult:
    """Komplette MT_Sim-konforme Analyse: 4 CSVs + Plots + manifest.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    run_csv = out_dir / "run.csv"
    pairs_csv = out_dir / "pairs.csv"
    disc_csv = out_dir / "discriminations.csv"
    summary_csv = out_dir / "summary.csv"
    manifest = out_dir / "manifest.json"

    # Series laden
    series = _read_run_csv(run_csv)
    # Crowding-Index aus particles_total schätzen (sehr grob; ohne Volumen-Map)
    crowding_proxy = series["particles_total"] / max(float(series["particles_total"].max()), 1.0)

    metrics = compute_metrics(
        time_s=series["time_s"],
        radius_nm=series["radius_nm"],
        atp_mM=series["atp_mM"],
        crowding_index=crowding_proxy,
        rdme_steps=series["rdme_steps"],
        particles_total=series["particles_total"],
    )

    # pairs.csv: Vergleich mit sich selbst (HYP vs. ANT, beide gleich)
    _write_pairs_csv(pairs_csv, series, series)
    # discriminations.csv
    _write_discriminations_csv(disc_csv, series)
    # summary.csv
    row = metrics_to_row(metrics, tag=tag)
    with summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    # manifest.json
    _write_manifest(manifest, run_csv, seed=result.seed, walltime_s=result.walltime_s)

    plots: dict[str, Path] = {}
    if write_plots:
        plots = write_all_plots(series, crowding_proxy, out_dir)

    return AnalysisResult(
        out_dir=out_dir,
        run_csv=run_csv,
        pairs_csv=pairs_csv,
        discriminations_csv=disc_csv,
        summary_csv=summary_csv,
        manifest_path=manifest,
        plots=plots,
    )
