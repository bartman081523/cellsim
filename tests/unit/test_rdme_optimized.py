"""Tests für optimierten RDME-Adapter."""

from __future__ import annotations

from cellsim.adapters.rdme_optimized import (
    OptimizedRDMEAdapter,
    estimate_speedup,
)
from cellsim.core.rng import make_rng
from cellsim.modules.reactions import default_registry


def test_optimized_rdme_basic() -> None:
    rdme = OptimizedRDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    assert rdme.is_jit_compiled is False  # numba nicht installiert im Test


def test_optimized_rdme_step() -> None:
    rdme = OptimizedRDMEAdapter(
        registry=default_registry(),
        grid_shape=(3, 3, 3),
        use_local_diffusion=True,
    )
    initial = rdme.total_particles
    for _ in range(50):
        rdme.step(1e-3, make_rng(42, 0, 0))
    assert rdme.state.step_count == 50
    assert abs(rdme.mass_conservation_ratio - 1.0) < 0.01


def test_estimate_speedup_scales_with_grid() -> None:
    """Größere Gitter → höherer Speedup-Faktor."""
    small = estimate_speedup((4, 4, 4))
    large = estimate_speedup((16, 16, 16))
    assert large > small


def test_estimate_speedup_minimum() -> None:
    """Auch bei kleinem Gitter ≥ 1×."""
    s = estimate_speedup((2, 2, 2))
    assert s >= 1.0
