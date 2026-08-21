"""Tests für RDME-Gillespie-Solver (sehr einfach)."""

from __future__ import annotations

import numpy as np

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.reactions import default_registry


def test_rdme_total_particles_initial() -> None:
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(4, 4, 4))
    n_species = len(default_registry().species_ids)
    expected = 4 * 4 * 4 * 50 * n_species
    assert rdme.total_particles == expected


def test_rdme_step_increments_counter() -> None:
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    rng = make_rng(42, 0, 0)
    n0 = rdme.state.step_count
    rdme.step(1e-3, rng)
    assert rdme.state.step_count == n0 + 1


def test_rdme_telemetry_keys() -> None:
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    rng = make_rng(42, 0, 0)
    tel = rdme.step(1e-3, rng)
    assert "total_particles" in tel
    assert "rdme_steps" in tel
    assert "voxel_count" in tel


def test_rdme_snapshot_restore() -> None:
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    rdme.step(1e-3, make_rng(42, 0, 0))
    snap = rdme.snapshot()
    n_after = rdme.total_particles
    rdme.step(1e-3, make_rng(42, 0, 1))
    rdme.restore(snap)
    assert rdme.total_particles == n_after
    assert rdme.state.step_count == 1


def test_rdme_deterministic_same_seed() -> None:
    a = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    b = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    for _ in range(20):
        a.step(1e-3, make_rng(7, 0, 0))
        b.step(1e-3, make_rng(7, 0, 0))
    assert a.total_particles == b.total_particles
