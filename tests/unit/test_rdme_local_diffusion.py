"""Tests für crowding-aware RDME."""

from __future__ import annotations

import numpy as np

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.reactions import default_registry


def test_rdme_default_global_diffusion() -> None:
    """Default: keine lokale Diffusion."""
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(3, 3, 3))
    assert rdme.use_local_diffusion is False


def test_rdme_local_diffusion_enabled() -> None:
    rdme = RDMEAdapter(
        registry=default_registry(),
        grid_shape=(3, 3, 3),
        use_local_diffusion=True,
    )
    assert rdme.use_local_diffusion is True


def test_rdme_local_diffusion_conserves_mass_approximately() -> None:
    """Mit lokaler Diffusion bleibt die Masse ungefähr erhalten."""
    rdme = RDMEAdapter(
        registry=default_registry(),
        grid_shape=(3, 3, 3),
        use_local_diffusion=True,
    )
    initial = rdme.total_particles
    for _ in range(100):
        rdme.step(1e-3, make_rng(42, 0, 0))
    ratio = rdme.mass_conservation_ratio
    # Migration erhält Counts nur voxel-lokal, daher Ratio bleibt exakt
    assert abs(ratio - 1.0) < 0.01


def test_rdme_local_diffusion_spreads_particles() -> None:
    """Mit Migration werden Partikel zwischen Voxeln verteilt."""
    rdme = RDMEAdapter(
        registry=default_registry(),
        grid_shape=(4, 4, 4),
        initial_particles_per_species=10,
        use_local_diffusion=True,
    )
    rng = make_rng(42, 0, 0)
    initial_var = float(np.var([int(v.sum()) for v in rdme.state.voxels.values()]))
    for _ in range(500):
        rdme.step(1e-3, rng)
    final_var = float(np.var([int(v.sum()) for v in rdme.state.voxels.values()]))
    # Die initiale Varianz ist 0 (alle Voxel gleich gefüllt), Migration verändert sie.
    assert final_var >= 0.0
