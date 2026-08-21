"""Tests für L3-Metriken."""

from __future__ import annotations

import numpy as np

from cellsim.analysis.metrics import compute_metrics, metrics_to_row


def test_compute_metrics_basic() -> None:
    n = 100
    t = np.linspace(0, 100, n)
    r = 200.0 + 0.1 * t  # 0.1 nm/s
    atp = 2.0 * np.ones(n)
    crowding = np.zeros(n)
    rdme_steps = np.arange(n).astype(np.float64) * 10
    particles = np.full(n, 1000.0)
    m = compute_metrics(t, r, atp, crowding, rdme_steps, particles, t_ss_start_s=10.0)
    assert m.growth_rate_mean_nm_per_s == pytest_approx(0.1)
    assert m.atp_ss_mean_mM == pytest_approx(2.0)


def test_metrics_to_row_has_mean_sem_suffixes() -> None:
    from cellsim.analysis.metrics import L3Metrics

    m = L3Metrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    row = metrics_to_row(m, tag="x")
    assert "growth_rate_mean_nm_per_s" in row
    assert "growth_rate_sem_nm_per_s" in row
    assert row["tag"] == "x"


def pytest_approx(value: float, rel: float = 1e-6) -> float:  # type: ignore[no-redef]
    import pytest

    return pytest.approx(value, rel=rel)
