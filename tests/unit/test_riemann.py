"""Tests für Riemannsche DNA-Mannigfaltigkeit."""

from __future__ import annotations

import numpy as np

from cellsim.modules.riemann import (
    RiemannParams,
    compute_curvature,
    geodesic_velocity,
    init_manifold,
    update_manifold_from_geometry,
)


def test_init_manifold_correct_shape() -> None:
    m = init_manifold(RiemannParams())
    assert m.r.shape == (RiemannParams.n_beads, 3)
    assert m.curvature_kappa.shape == (RiemannParams.n_beads,)
    assert m.metric_g.shape == (RiemannParams.n_beads,)


def test_compute_curvature_positive_for_curved_path() -> None:
    """Eine Helix hat nicht-triviale Krümmung."""
    m = init_manifold(RiemannParams(n_beads=50, contour_length_nm=100.0))
    kappa = compute_curvature(m)
    assert kappa.max() > 0.0


def test_compute_curvature_zero_for_straight_line() -> None:
    """Eine gerade Linie hat Krümmung = 0."""
    m = init_manifold(RiemannParams(n_beads=20))
    m.r = np.zeros((20, 3))
    m.r[:, 0] = np.linspace(0, 10, 20)
    kappa = compute_curvature(m)
    assert kappa.max() < 1e-6


def test_update_increases_curvature_with_crowding() -> None:
    """Mehr Crowding → mehr Krümmung."""
    m = init_manifold(RiemannParams())
    update_manifold_from_geometry(m, cell_radius_nm=200.0, crowding_index=0.0, params=RiemannParams())
    kappa_no_crowd = m.curvature_kappa.copy()
    update_manifold_from_geometry(m, cell_radius_nm=200.0, crowding_index=0.5, params=RiemannParams())
    kappa_with_crowd = m.curvature_kappa.copy()
    assert kappa_with_crowd.mean() > kappa_no_crowd.mean()


def test_update_scales_configuration() -> None:
    """Mit wachsendem Zellradius wird Konformation größer."""
    m = init_manifold(RiemannParams())
    rg_before = float(np.linalg.norm(m.r, axis=1).mean())
    update_manifold_from_geometry(m, cell_radius_nm=400.0, crowding_index=0.0, params=RiemannParams())
    rg_after = float(np.linalg.norm(m.r, axis=1).mean())
    assert rg_after > rg_before


def test_geodesic_velocity_finite() -> None:
    m = init_manifold(RiemannParams())
    v = geodesic_velocity(m, target_step_nm=0.1)
    assert v.shape == m.r.shape
    assert np.all(np.isfinite(v))


def test_riemann_tensor_scalar_finite() -> None:
    m = init_manifold(RiemannParams())
    update_manifold_from_geometry(m, cell_radius_nm=200.0, crowding_index=0.3, params=RiemannParams())
    assert np.isfinite(m.riemann_tensor_components)
    assert m.riemann_tensor_components >= 0.0
