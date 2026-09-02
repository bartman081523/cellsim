"""Tests für das Superradianz-Modul (iter-15, aus MT_Sim portiert)."""

from __future__ import annotations

import numpy as np
import pytest

from cellsim.modules.superradiance import (
    PhotonicCluster,
    aggregate_photon_rate_per_s,
    dicke_intensity_photons_per_s,
    flux_at_cm2,
    photon_energy_j,
    superradiance_time_s,
    threshold_aggregate_rate_per_s,
    turnover_per_second,
)


def test_tau_sr_scales_inverse_n() -> None:
    """Dicke: τ_SR = τ_sp/N."""
    assert superradiance_time_s(10) == pytest.approx(1e-10)
    assert superradiance_time_s(1000) == pytest.approx(1e-12)
    assert superradiance_time_s(1) == pytest.approx(1e-9)


def test_peak_scales_n_squared() -> None:
    """Peak ∝ N² (Dicke-Verstärkung), exakt via Property (N²/(2τ_sp))."""
    peak_100 = PhotonicCluster(n_emitters=100).peak_photons_per_s
    peak_200 = PhotonicCluster(n_emitters=200).peak_photons_per_s
    assert peak_200 / peak_100 == pytest.approx(4.0, rel=1e-9)


def test_burst_integral_equals_n_photons() -> None:
    """Energie-Erhalt: ein Photon pro Emitter pro Burst."""
    n = 100
    tau_sr = 1e-9 / n
    t = np.linspace(-tau_sr, 3 * tau_sr * 10, 200_000)
    intensity = dicke_intensity_photons_per_s(n, t)
    total = float(np.trapezoid(intensity, t))
    assert total == pytest.approx(n, rel=0.02)


def test_stability_at_mega_network() -> None:
    """Kurian-Mega-Netzwerke (N ~ 1e5): kein Overflow/NaN."""
    cluster = PhotonicCluster(n_emitters=100_000)
    assert np.isfinite(cluster.peak_photons_per_s)
    assert cluster.peak_photons_per_s > 0
    t = np.linspace(0, 1e-5, 1000)
    intensity = np.asarray(cluster.intensity(t))
    assert np.all(np.isfinite(intensity))
    assert float(np.max(intensity)) > 0


def test_cluster_properties() -> None:
    cluster = PhotonicCluster(n_emitters=100)
    assert cluster.tau_sr_s == pytest.approx(1e-11)
    assert cluster.peak_photons_per_s == pytest.approx(100**2 / 2e-9, rel=0.01)
    assert cluster.photons_per_burst == 100.0


def test_invalid_emitters() -> None:
    with pytest.raises(ValueError):
        superradiance_time_s(0)
    with pytest.raises(ValueError):
        dicke_intensity_photons_per_s(0, 0.0)


def test_aggregate_rate_and_flux_bridge() -> None:
    """Brücke: Φ = M·N·f → Flux(r) → Turnover → Fenster."""
    phi = aggregate_photon_rate_per_s(n_clusters=10_000, n_per_cluster=100, f_burst_hz=1_000)
    assert phi == 1e9  # M·N·f = 1e4·100·1e3
    flux = flux_at_cm2(phi, r_nm=100.0)
    turnover = turnover_per_second(flux)
    assert flux > 0
    assert turnover == pytest.approx(flux * 1e-17 * 0.1)


def test_threshold_aggregate_rate_in_expected_decade() -> None:
    """Φ* für Fenster-Eintritt (r=100nm, σ·QY=1e-18): Vorab-Skalierung
    sagt ~1e8–1e11 photons/s."""
    lo, hi = threshold_aggregate_rate_per_s(r_nm=100.0)
    # G(100nm) = exp(-0.5)/(4π·1e-10 cm²) ≈ 4.83e8 /cm²
    g_expected = 4.83e8
    coupling = g_expected * 1e-17 * 0.1 * 1e-3
    assert lo == pytest.approx(1e-4 / coupling, rel=0.02)
    assert hi == pytest.approx(0.1 / coupling, rel=0.02)


def test_photon_energy() -> None:
    """E(280nm) ≈ 4.43 eV (UV-B/C-Band)."""
    e_j = photon_energy_j(280.0)
    e_ev = e_j / 1.602_176_634e-19
    assert 4.3 < e_ev < 4.6
