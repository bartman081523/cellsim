"""Tests für Membran-Wachstum."""

from __future__ import annotations

from cellsim.modules.membrane import MembraneGeometry, MembraneParams


def test_membrane_grows_monotonically() -> None:
    geom = MembraneGeometry(MembraneParams(growth_rate_per_s=0.1))
    initial = geom.radius_nm
    for _ in range(50):
        geom.update(1.0)
    assert geom.radius_nm > initial


def test_membrane_capped_at_mature() -> None:
    params = MembraneParams(radius_initial_nm=100.0, radius_mature_nm=110.0, growth_rate_per_s=0.1)
    geom = MembraneGeometry(params)
    for _ in range(100):
        geom.update(1.0)
    assert geom.radius_nm <= params.radius_mature_nm + 1e-9


def test_membrane_volume_positive() -> None:
    geom = MembraneGeometry()
    assert geom.volume_nm3 > 0.0


def test_membrane_reset() -> None:
    geom = MembraneGeometry()
    for _ in range(10):
        geom.update(1.0)
    geom.reset()
    assert geom.radius_nm == geom.params.radius_initial_nm
    assert geom.t_s == 0.0
