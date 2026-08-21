"""Tests für EM-Schicht."""

from __future__ import annotations

import numpy as np
import pytest

from cellsim.modules.em import (
    EMParams,
    EMSource,
    chemolumineszenz_photons_per_s,
    estimate_uv_emission,
    schwarzkoerper_emission,
)


pytest_approx = pytest.approx


def test_schwarzkoerper_zero_at_uv() -> None:
    """Bei 310K ist Schwarzkörper im UV praktisch null."""
    r250 = schwarzkoerper_emission(250.0, 310.0)
    assert r250 < 1e-70


def test_chemolumineszenz_scales_with_atp() -> None:
    """Bei 2× ATP-Rate → 2× Photonen."""
    p1 = chemolumineszenz_photons_per_s(1e6)
    p2 = chemolumineszenz_photons_per_s(2e6)
    assert abs(p2 - 2 * p1) < 1e-9


def test_source_flux_density_decreases_with_distance() -> None:
    """Flussdichte fällt mit 1/r² (mit Absorption-Korrektur)."""
    src = EMSource(
        position_nm=np.array([0.0, 0.0, 0.0]),
        photons_per_s=1.0e10,
        zell_radius_nm=250.0,
    )
    f1 = src.flux_density_at(
        np.array([1000.0, 0.0, 0.0]), absorption_length_nm=1e9,
    )   # Absorption deaktiviert (sehr lang)
    f2 = src.flux_density_at(
        np.array([2000.0, 0.0, 0.0]), absorption_length_nm=1e9,
    )
    # Ohne Absorption: 1/r² → Faktor 4
    assert f1 / f2 == pytest_approx(4.0, rel=0.01)


def test_estimate_uv_emission_returns_realistic_values() -> None:
    """Mit Default-Popp-Faktor: ~10⁷ Photonen/cm²/s bei 1 µm (ohne Absorption)."""
    result = estimate_uv_emission(EMParams(), wavelength_nm=300.0)
    assert result["chemolumineszenz_photons_per_s"] > 0.0
    # Default absorption_length_nm=200 dämpft stark: ~6·10⁵
    assert result["flux_density_1um"] > 1e4
    assert result["flux_density_1um"] < 1e9
