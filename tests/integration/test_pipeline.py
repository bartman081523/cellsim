"""Integration: Driver → CSV → Analysis-Pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.analysis.pipeline import run_analysis
from cellsim.driver.loop import HybridDriver, write_run_csv
from cellsim.modules.membrane import MembraneGeometry, MembraneParams
from cellsim.modules.reactions import default_registry
from cellsim.core.time_axis import TimeAxis


def test_pipeline_writes_all_outputs(tmp_path: Path) -> None:
    rng_init = np.random.default_rng(42)
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(4, 4, 4))
    ode = ODEAdapter()
    chrom = ChromosomeAdapter(n_beads=20, rng=rng_init)
    membrane = MembraneGeometry(MembraneParams(growth_rate_per_s=0.05))
    time_axis = TimeAxis(0.0, 2.0, 1e-3, 1e-1)
    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=10,
        seed=42,
    )
    result = driver.run()
    write_run_csv(result, tmp_path / "run.csv")

    ana = run_analysis(result, tmp_path, tag="smoke", write_plots=False)
    assert ana.run_csv.exists()
    assert ana.pairs_csv.exists()
    assert ana.discriminations_csv.exists()
    assert ana.summary_csv.exists()
    assert ana.manifest_path.exists()

    # summary.csv enthält _mean-Spalten
    import csv as _csv
    with ana.summary_csv.open() as fh:
        reader = _csv.DictReader(fh)
        rows = list(reader)
    assert len(rows) == 1
    assert any("_mean" in k for k in rows[0].keys())


def test_pipeline_writes_plots(tmp_path: Path) -> None:
    rng_init = np.random.default_rng(7)
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    ode = ODEAdapter()
    chrom = ChromosomeAdapter(n_beads=10, rng=rng_init)
    membrane = MembraneGeometry()
    time_axis = TimeAxis(0.0, 1.0, 1e-3, 1e-1)
    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=5,
        seed=7,
    )
    result = driver.run()
    write_run_csv(result, tmp_path / "run.csv")
    ana = run_analysis(result, tmp_path, write_plots=True)
    assert len(ana.plots) == 4
    for name, p in ana.plots.items():
        assert p.exists(), f"Plot fehlt: {name}"
        assert p.stat().st_size > 0
