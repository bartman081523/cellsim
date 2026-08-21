"""Tests für Crowding-Modul."""

from __future__ import annotations

import numpy as np

from cellsim.modules.crowding import CrowdingField, CrowdingParams, compute_crowding


def test_crowding_empty_returns_zero() -> None:
    field = compute_crowding({}, {}, voxel_edge_nm=10.0)
    assert field.mean_crowding == 0.0


def test_crowding_signal_present() -> None:
    """Wenn ein Voxel deutlich voller ist, sollte std > 0 sein."""
    counts = {
        "A": np.zeros((4, 4, 4), dtype=np.int64),
    }
    counts["A"][0, 0, 0] = 100  # dichtes Voxel
    volumes = {"A": 1000.0}
    field = compute_crowding(counts, volumes, voxel_edge_nm=10.0)
    assert field.std_crowding > 0.0
    assert field.d_local_nm2_per_ms[0, 0, 0] < field.d_local_nm2_per_ms[3, 3, 3]


def test_crowding_d_local_monotone_decreasing_with_alpha() -> None:
    counts = {"A": np.full((2, 2, 2), 10, dtype=np.int64)}
    volumes = {"A": 500.0}
    low = compute_crowding(counts, volumes, voxel_edge_nm=10.0, params=CrowdingParams(alpha=0.5))
    high = compute_crowding(counts, volumes, voxel_edge_nm=10.0, params=CrowdingParams(alpha=5.0))
    assert high.d_local_nm2_per_ms.mean() < low.d_local_nm2_per_ms.mean()
