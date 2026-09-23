"""Unit-Tests: Photonic-Coupling (iter-23, photonic_coupling.py).

Invarianz-Tests der Modul-Mathematik — KEINE Ergebnis-Buchung (die
Verdict-Logik liegt in scratch/experiments/iter-23 mit Vorab-Registrierung).
"""

from __future__ import annotations

import pytest

from cellsim.modules.kick_coupling import DELTA_G_ATP_J
from cellsim.modules.photonic_coupling import (
    N_TRP_EST_PER_CELL,
    PhotonicSource,
    burst_invariance_check,
    classify_window,
    n_trp_estimate,
    pump_cap_photons_per_s,
    window_bounds_per_s,
)
from cellsim.modules.superradiance import (
    QUANTUM_YIELD_UVC,
    SIGMA_TRP_CM2,
    TRYPTOPHAN_WAVELENGTH_NM,
    aggregate_photon_rate_per_s,
    photon_energy_j,
    threshold_aggregate_rate_per_s,
    turnover_per_second,
)

SRC_DEFAULT = PhotonicSource()


def test_pump_cap_energy_conservation() -> None:
    """Φ_cap = atp·ΔG_ATP/E_photon; zweite Route via E_photon-Identität."""
    cap = pump_cap_photons_per_s(1.0e6, TRYPTOPHAN_WAVELENGTH_NM)
    e_ph = photon_energy_j(TRYPTOPHAN_WAVELENGTH_NM)
    assert cap == pytest.approx(1.0e6 * DELTA_G_ATP_J / e_ph, rel=1e-12)
    # E_photon/ΔG_ATP ≈ 8.5 (Kontext-Anker, Größenordnung)
    assert e_ph / DELTA_G_ATP_J == pytest.approx(8.5, rel=0.1)
    # Monotonie: mehr Pump-Leistung → höhere Obergrenze
    assert pump_cap_photons_per_s(2.0e6) > cap


def test_effective_rate_never_exceeds_pump_cap() -> None:
    """Effective ≡ min(declared, cap); Flag kippt genau an der Obergrenze."""
    for f in (1.0, 1e3, 1e6, 1e9):
        src = PhotonicSource(f_burst_hz=f)
        assert src.effective_rate_per_s <= src.pump_cap_per_s
    assert SRC_DEFAULT.declared_rate_per_s == pytest.approx(
        aggregate_photon_rate_per_s(
            SRC_DEFAULT.n_clusters, SRC_DEFAULT.n_per_cluster, 1.0
        ), rel=1e-12)
    assert not SRC_DEFAULT.pump_cap_active
    saturating = PhotonicSource(f_burst_hz=1e9)
    assert saturating.pump_cap_active
    assert saturating.effective_rate_per_s == pytest.approx(
        saturating.pump_cap_per_s, rel=1e-12)


def test_declared_rate_reuse_identity() -> None:
    """declared ≡ superradiance.aggregate_photon_rate_per_s (Reuse)."""
    for clusters, per, f in ((1, 2011, 1.0), (10, 100, 5.0), (3, 50, 0.0)):
        src = PhotonicSource(n_clusters=clusters, n_per_cluster=per,
                             f_burst_hz=f)
        assert src.declared_rate_per_s == pytest.approx(
            clusters * per * f, rel=1e-12)


def test_flux_and_turnover_chain() -> None:
    """Turnover ≡ flux·σ·QY; zweite Route via Threshold-Inversion."""
    src = SRC_DEFAULT
    eff = src.effective_rate_per_s
    flux = src.flux_at_target_cm2
    turnover = src.turnover_at_target_per_s
    assert turnover == pytest.approx(
        flux * SIGMA_TRP_CM2 * QUANTUM_YIELD_UVC, rel=1e-12)
    # Turnover ≡ (eff/Φ*_lo)·window_lo (Inversion der registrierten
    # threshold_aggregate_rate_per_s — zweite Route, iter-19-Lektion)
    lo_star, _ = threshold_aggregate_rate_per_s(
        r_nm=src.target_distance_nm,
        sigma_cm2=SIGMA_TRP_CM2,
        quantum_yield=QUANTUM_YIELD_UVC,
        absorption_length_nm=src.absorption_length_nm,
    )
    lo_window, _ = window_bounds_per_s()
    assert turnover == pytest.approx(eff / lo_star * lo_window, rel=1e-9)


def test_burst_invariance_n_cancellation() -> None:
    """Lemma: mit pump-konsistenter f = Φ_cap/N ist der Burst-Route-
    Turnover ≡ Average-Route-Turnover EINER pump-geklemmten Quelle
    (effective ≡ Φ_cap) — N kürzt sich (reine Identität, keine
    Ergebnis-Buchung)."""
    capped = PhotonicSource(f_burst_hz=1e9)  # pump_cap_active, eff ≡ Φ_cap
    assert capped.pump_cap_active
    avg_route = capped.turnover_at_target_per_s
    cap = capped.pump_cap_per_s
    for n in (1, 100, N_TRP_EST_PER_CELL, 10_000):
        f = cap / n
        burst = burst_invariance_check(capped, n, f)
        assert burst == pytest.approx(avg_route, rel=1e-9)


def test_burst_invariance_rejects_saturation() -> None:
    """N·g·σ >= 1 (Sättigungsregime) wird abgelehnt — Lemma-Gültigkeitsraum."""
    with pytest.raises(ValueError):
        burst_invariance_check(SRC_DEFAULT, 10**20, 1.0)


def test_n_trp_estimate_identity_and_inventory_bound() -> None:
    """N_trp ≡ 455·340·1.3e-2 (HYPOTHESE-Anker) und N_trp·σ ≪ 1."""
    assert n_trp_estimate() == N_TRP_EST_PER_CELL
    assert n_trp_estimate() == pytest.approx(455 * 340 * 1.3e-2, rel=1e-3)
    # Sättigungsunmöglichkeit: selbst das GESAMTE Inventar sättigt nie
    # (N·σ ≪ 1; Sättigung bräuchte N ≥ 1/σ = 1e17 Emitter)
    assert N_TRP_EST_PER_CELL * SIGMA_TRP_CM2 < 1e-10


def test_window_classification_boundaries() -> None:
    """below/in/above exakt an den registrierten Grenzen."""
    lo, hi = window_bounds_per_s()
    assert (lo, hi) == pytest.approx((0.1, 100.0))
    assert classify_window(lo * 0.999) == "below"
    assert classify_window(lo) == "in"
    assert classify_window((lo + hi) / 2) == "in"
    assert classify_window(hi) == "in"
    assert classify_window(hi * 1.001) == "above"


def test_rates_telemetry_keys() -> None:
    """Telemetrie-Schema: exakt 4 Float-Keys (run.csv-Spalten)."""
    rates = SRC_DEFAULT.rates()
    assert set(rates.keys()) == {
        "photon_rate_per_s",
        "photon_flux_cm2_s",
        "photochem_turnover_per_s",
        "photon_pump_capped",
    }
    for v in rates.values():
        assert isinstance(v, float)
    assert rates["photon_rate_per_s"] == pytest.approx(
        SRC_DEFAULT.effective_rate_per_s, rel=1e-12)
    assert rates["photon_pump_capped"] in (0.0, 1.0)


def test_validation_rejects_bad_parameters() -> None:
    for bad in (
        {"n_clusters": 0},
        {"n_per_cluster": 0},
        {"f_burst_hz": -1.0},
        {"wavelength_nm": 0.0},
        {"target_distance_nm": -5.0},
        {"atp_hydrolysis_per_s": -1.0},
        {"absorption_length_nm": 0.0},
    ):
        with pytest.raises(ValueError):
            PhotonicSource(**bad)


def test_pump_cap_zero_atp_and_monotone_in_distance() -> None:
    """Φ_cap(0) = 0; Flux fällt mit der Entfernung (Monotonie)."""
    assert pump_cap_photons_per_s(0.0) == 0.0
    src_near = PhotonicSource(target_distance_nm=50.0)
    src_far = PhotonicSource(target_distance_nm=500.0)
    assert src_near.flux_at_target_cm2 > src_far.flux_at_target_cm2
    assert src_near.turnover_at_target_per_s > src_far.turnover_at_target_per_s
    assert turnover_per_second(src_far.flux_at_target_cm2) == pytest.approx(
        src_far.turnover_at_target_per_s, rel=1e-12)
