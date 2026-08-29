"""Tests für lokales Tau-Leaping im RDMEAdapter (iter-11-Portierung)."""

from __future__ import annotations

import numpy as np

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.reactions import Reaction, ReactionRegistry, default_registry


def _tau_adapter(
    grid_shape: tuple[int, int, int] = (8, 8, 8),
    registry: ReactionRegistry | None = None,
) -> RDMEAdapter:
    return RDMEAdapter(
        registry=registry or default_registry(),
        grid_shape=grid_shape,
        use_tau_leap=True,
    )


def test_tau_leap_never_negative_counts() -> None:
    """Feasibility-Cap: keine Spezies fällt unter 0 (iter-11-Invariante)."""
    rdme = _tau_adapter()
    rng = make_rng(42, 0, 0)
    for _ in range(200):
        rdme.step(1e-5, rng)
    for v in rdme.state.voxels.values():
        assert int(v.min()) >= 0
    assert np.isfinite(rdme.mass_conservation_ratio)


def test_tau_leap_deterministic() -> None:
    """Gleicher Seed → bit-identische Trajektorie (Projekt-Konvention)."""
    runs = []
    for _ in range(2):
        rdme = _tau_adapter()
        rng = make_rng(42, 0, 0)
        for _ in range(100):
            rdme.step(1e-5, rng)
        runs.append({k: v.copy() for k, v in rdme.state.voxels.items()})
    for s_id in runs[0]:
        assert np.array_equal(runs[0][s_id], runs[1][s_id])


def test_tau_leap_saturation_collapse() -> None:
    """Sättigungs-Kollaps (iter-11): Reaktionen feuern am Feasibility-Cap.

    k·dt = 4.5 ≫ Fenster-Obergrenze ~0.1 → Glykolyse feuert auf den
    Co-Substrat-Vorrat (ADP 2 pro Firing statt λ-Poisson). Zusätzlich
    verbrauchen die Hauswirtschafts-ATPasen (Gyrase, FtsZ, GroEL, …)
    ATP jede Schrittweite → ATP-Schuld: ADP akkumuliert, Pi wird von
    der Synthase (k·dt=88·n) sofort re-eingesammelt.
    """
    rdme = _tau_adapter()
    rng = make_rng(42, 0, 0)
    for _ in range(20):
        rdme.step(1e-2, rng)
    n_initial = 50 * 8 * 8 * 8
    glc = int(rdme.state.voxels["Glucose"].sum())
    assert glc < 0.75 * n_initial  # Substrat kollabiert (ADP-limitiert)
    assert int(rdme.state.voxels["ADP"].sum()) > 0.5 * n_initial  # ATP-Schuld
    assert int(rdme.state.voxels["Pi"].sum()) < 0.05 * n_initial  # Synthase-Fressen


def test_tau_leap_window_depletes_substrat_vs_disabled() -> None:
    """Im Damköhler-Fenster wird Glucose messbar umgesetzt; mit
    dt=0 (λ=0) bleibt sie exakt erhalten."""
    window = _tau_adapter()
    rng_w = make_rng(42, 0, 0)
    for _ in range(100):
        window.step(1e-5, rng_w)

    disabled = _tau_adapter()
    rng_d = make_rng(42, 0, 0)
    for _ in range(100):
        disabled.step(0.0, rng_d)

    glc_initial = 50 * 8 * 8 * 8
    glc_window = int(window.state.voxels["Glucose"].sum())
    glc_disabled = int(disabled.state.voxels["Glucose"].sum())
    assert glc_disabled == glc_initial  # dt=0: keine Firings
    assert glc_window < 0.9 * glc_initial  # Fenster: Substanz umgesetzt
    assert window.state.tau_leap_events > 100  # mehrere Events/Schritt


def test_tau_leap_zero_stoichiometry_noop() -> None:
    """Null-Stöchiometrie (z.B. rnap_init) ist no-op im Tau-Leap."""
    registry = ReactionRegistry(
        species_ids=("X", "Y"),
        reactions=(Reaction("noop", {"X": 0}, k=1e6),),
    )
    rdme = _tau_adapter(grid_shape=(4, 4, 4), registry=registry)
    rng = make_rng(42, 0, 0)
    for _ in range(10):
        rdme.step(1e-3, rng)
    assert int(rdme.state.voxels["X"].sum()) == 50 * 64
    assert rdme.state.tau_leap_events == 0


def test_tau_leap_default_mode_untouched() -> None:
    """Gillespie-Default zählt keine Tau-Leap-Events (Rückwärtskompatib.)."""
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(4, 4, 4))
    rng = make_rng(42, 0, 0)
    for _ in range(10):
        rdme.step(1e-5, rng)
    assert rdme.state.tau_leap_events == 0
    assert rdme.state.step_count == 10


def test_tau_leap_snapshot_roundtrip() -> None:
    """tau_leap_events überlebt Snapshot/Restore."""
    rdme = _tau_adapter()
    rng = make_rng(42, 0, 0)
    for _ in range(50):
        rdme.step(1e-5, rng)
    blob = rdme.snapshot()

    restored = RDMEAdapter(
        registry=default_registry(), grid_shape=(8, 8, 8), use_tau_leap=True
    )
    restored.restore(blob)
    assert restored.state.tau_leap_events == rdme.state.tau_leap_events
    for s_id in rdme.state.voxels:
        assert np.array_equal(restored.state.voxels[s_id], rdme.state.voxels[s_id])
