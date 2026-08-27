"""Tests für Integration-Adapter."""

from __future__ import annotations

import numpy as np

from cellsim.driver.integration import IntegratedCell, run_integrated


def test_integrated_cell_initializes() -> None:
    from cellsim.adapters.rdme import RDMEAdapter
    from cellsim.modules.reactions import default_registry

    cell = IntegratedCell()
    # RDME wird im __init__ mit initialen Partikeln gefüllt
    expected_particles = (
        6 * 6 * 6 * 50 * len(default_registry().species_ids)
    )
    assert cell.state.rdme_particles == expected_particles
    assert cell.state.ode_atp_mM > 0
    assert cell.state.membrane_radius_nm > 0


def test_integrated_cell_step_advances_state() -> None:
    cell = IntegratedCell()
    rng = np.random.default_rng(42)
    initial_steps = cell.state.n_steps
    cell.step(1e-3, rng)
    assert cell.state.n_steps == initial_steps + 1


def test_integrated_cell_produces_telemetry() -> None:
    cell = IntegratedCell()
    rng = np.random.default_rng(42)
    tel = cell.step(1e-3, rng)
    assert "rdme_particles" in tel
    assert "atp_mM" in tel
    assert "chromo_yield" in tel
    assert "em_uv_photons_per_s" in tel


def test_integrated_cell_atp_stays_realistic() -> None:
    """Mit aktivierter ODE bleibt ATP im mM-Bereich stabil."""
    cell = IntegratedCell()
    rng = np.random.default_rng(42)
    for _ in range(1000):
        cell.step(1e-3, rng)
    assert 0.01 < cell.state.ode_atp_mM < 100.0   # im mM-Bereich


def test_run_integrated_returns_final_state() -> None:
    state = run_integrated(t_end_s=0.1, dt_s=1e-3, seed=42)
    assert "n_steps" in state
    assert "atp_mM" in state


def test_integrated_cell_disable_modules() -> None:
    """Module können einzeln deaktiviert werden."""
    from cellsim.driver.integration import IntegrationConfig, IntegratedCell

    cell = IntegratedCell(
        IntegrationConfig(
            use_em_chemoluminescence=False,
            use_cryptochrome=False,
        ),
    )
    assert cell.em_source is None
    assert cell.cryptochrome is None


def test_integrated_cell_consistent_across_runs() -> None:
    """Zwei Läufe mit gleichem Seed → gleiches Ergebnis."""
    s1 = run_integrated(t_end_s=0.05, dt_s=1e-3, seed=42)
    s2 = run_integrated(t_end_s=0.05, dt_s=1e-3, seed=42)
    assert s1["n_steps"] == s2["n_steps"]
    assert abs(s1["rdme_particles"] - s2["rdme_particles"]) < 1e-6