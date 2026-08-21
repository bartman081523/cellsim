"""Integration: Treiber-Loop koppelt RDME + ODE + Chromosom."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.constants import JCVI_PROTEIN_COUNT, L3_MASS_CONSERVATION_TOL
from cellsim.core.time_axis import TimeAxis
from cellsim.driver.loop import HybridDriver, write_run_csv
from cellsim.modules.membrane import MembraneGeometry, MembraneParams
from cellsim.modules.reactions import default_registry


def test_driver_runs_and_writes_csv(tmp_path: Path) -> None:
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

    out_csv = tmp_path / "run.csv"
    write_run_csv(result, out_csv)
    assert out_csv.exists()

    with out_csv.open() as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert len(rows) >= 2  # mindestens t=0 und t=2.0
    assert "atp_mM" in rows[0]
    assert all(float(r["atp_mM"]) >= 0.0 for r in rows)


def test_driver_mass_conservation() -> None:
    """Partikelzahl innerhalb ±5 % über die Sim."""
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(4, 4, 4))
    rng_init = np.random.default_rng(42)
    ode = ODEAdapter()
    chrom = ChromosomeAdapter(n_beads=20, rng=rng_init)
    membrane = MembraneGeometry()
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
    driver.run()

    ratio = rdme.mass_conservation_ratio
    assert abs(ratio - 1.0) < L3_MASS_CONSERVATION_TOL


def test_driver_determinism_same_seed(tmp_path: Path) -> None:
    """Zwei Läufe mit gleichem Seed → bit-identische run.csv."""
    out_a = tmp_path / "a" / "run.csv"
    out_b = tmp_path / "b" / "run.csv"

    def _run(out_path: Path) -> None:
        rng_init = np.random.default_rng(99)
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
            seed=99,
        )
        result = driver.run()
        write_run_csv(result, out_path)

    _run(out_a)
    _run(out_b)
    assert out_a.read_bytes() == out_b.read_bytes()


def test_jcvi_protein_count_constant_present() -> None:
    """Sicherstellen, dass JCVI_PROTEIN_COUNT = 455 (Sanity-Check)."""
    assert JCVI_PROTEIN_COUNT == 455
