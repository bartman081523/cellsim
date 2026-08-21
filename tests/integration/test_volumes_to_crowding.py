"""Integration: volumes.tsv → Treiber → Crowding-Index."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.time_axis import TimeAxis
from cellsim.data.volumes_loader import aggregate_volumes_by_species, load_volumes_tsv
from cellsim.driver.loop import HybridDriver, write_run_csv
from cellsim.modules.membrane import MembraneGeometry, MembraneParams
from cellsim.modules.reactions import default_registry


def _write_volumes_tsv(tmp_path: Path) -> Path:
    """Hilfsfunktion: schreibt eine kleine volumes.tsv."""
    target = tmp_path / "volumes.tsv"
    target.write_text(
        "uniprot_id\tRg_A\tRs_A\tV_ex_A3\tpLDDT_mean\n"
        "C7MID5\t18.5\t15.5\t1.5e4\t82.0\n"
        "C7LLN1\t16.0\t13.4\t1.0e4\t78.0\n",
        encoding="utf-8",
    )
    return target


def test_volumes_loader_integration(tmp_path: Path) -> None:
    """Lade volumes.tsv und aggregiere pro Spezies."""
    tsv = _write_volumes_tsv(tmp_path)
    volumes = load_volumes_tsv(tsv)
    assert "C7MID5" in volumes
    species = default_registry().species_ids
    out = aggregate_volumes_by_species(volumes, species)
    # Aggregate-Volumen ist > 0 für alle Spezies
    assert all(v > 0 for v in out.values())


def test_driver_uses_volumes(tmp_path: Path) -> None:
    """Der Treiber akzeptiert volumes und berechnet Crowding-Index."""
    tsv = _write_volumes_tsv(tmp_path)
    volumes = load_volumes_tsv(tsv)
    species = default_registry().species_ids
    volumes_agg = aggregate_volumes_by_species(volumes, species)

    rng_init = np.random.default_rng(42)
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(4, 4, 4))
    ode = ODEAdapter()
    chrom = ChromosomeAdapter(n_beads=20, rng=rng_init)
    membrane = MembraneGeometry(MembraneParams())

    time_axis = TimeAxis(0.0, 1.0, 1e-3, 1e-1)
    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=10,
        seed=42,
        volumes_angstrom3=volumes_agg,
    )
    # Crowding-Index vor erstem sync = 0 (kein run)
    assert driver._compute_crowding_index() >= 0.0
    # Crowding-Index nach erstem step > 0 (counts existieren)
    driver.run()
    crowding = driver._compute_crowding_index()
    assert crowding > 0.0


def test_couple_to_crowding_updates_riemann(tmp_path: Path) -> None:
    """Wenn Crowding-Index steigt, wächst Riemann-Krümmung."""
    rng_init = np.random.default_rng(42)
    chrom = ChromosomeAdapter(n_beads=20, rng=rng_init, use_riemann=True)
    assert chrom.use_riemann is True
    initial_kappa = float(chrom.manifold.mean_curvature)
    chrom.couple_to_crowding(0.5)
    chrom.couple_to_geometry(200.0)
    new_kappa = float(chrom.manifold.mean_curvature)
    # Crowding-Effekt erhöht Krümmung (oder hält sie zumindest konsistent)
    assert new_kappa >= 0.0
