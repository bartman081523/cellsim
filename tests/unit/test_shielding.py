"""Unit-Tests: ortsaufgelöstes Dekohärenz-Feld (iter-21, shielding.py).

Invarianz-Tests der Modul-Mathematik — KEINE Ergebnis-Buchung (die
Verdict-Logik liegt in scratch/experiments/iter-21 mit Vorab-Registrierung).
"""

from __future__ import annotations

import math

import pytest

from cellsim.modules.orch_or import ORConfig, penrose_tau_or_s, tegmark_tau_dec_s
from cellsim.modules.shielding import (
    DELTA_M_FLOOR,
    DELTA_M_ITER16,
    EPS_RES_OPTIMISTIC,
    EPS_RES_PESSIMISTIC,
    PHI_FREE_FLOOR,
    ShieldingConfig,
    coherence_core_radius_nm,
    corner_ratio,
    effective_suppression,
    gamma_bulk_collision_per_s,
    gamma_collision_per_s,
    gamma_needed_per_s,
    mean_core_gamma_per_s,
    phi_free_at,
    required_phi_free,
    s_needed,
)

CORNER = ORConfig()  # iter-16-Ecke: f=5e-2, a=8nm, N=1e9, korreliert, S=1e6


def test_gamma_bulk_is_inverse_of_tegmark_tau_dec() -> None:
    """Zweite Herleitung gegen Produktionscode (iter-19-Lektion)."""
    for dm in (DELTA_M_ITER16, DELTA_M_FLOOR, 3e-3):
        for t_k in (310.0, 273.15):
            cfg = ORConfig(t_k=t_k)
            bulk = gamma_bulk_collision_per_s(cfg, dm)
            tau = tegmark_tau_dec_s(
                ORConfig(t_k=t_k, delta_m_over_m_bulk=dm, shielding=1.0))
            assert bulk == pytest.approx(1.0 / tau, rel=1e-12)


def test_two_zone_field_values() -> None:
    cfg = ShieldingConfig(phi_free=1e-4, eps_res=1e-2, r_core_nm=8.0,
                          delta_m_over_m=DELTA_M_ITER16)
    inside = gamma_collision_per_s(0.0, cfg, CORNER)
    outside = gamma_collision_per_s(cfg.r_core_nm + 1e-9, cfg, CORNER)
    bulk = gamma_bulk_collision_per_s(CORNER, DELTA_M_ITER16)
    assert inside == pytest.approx(bulk * (1e-4 + (1 - 1e-4) * 1e-2))
    assert outside == pytest.approx(bulk)
    assert phi_free_at(cfg.r_core_nm, cfg) == 1e-4
    assert phi_free_at(cfg.r_core_nm * 1.001, cfg) == 1.0


def test_mean_core_and_suppression_consistency() -> None:
    cfg = ShieldingConfig(phi_free=1e-4, eps_res=1e-6,
                          delta_m_over_m=DELTA_M_ITER16)
    bulk = gamma_bulk_collision_per_s(CORNER, DELTA_M_ITER16)
    mean = mean_core_gamma_per_s(cfg, CORNER)
    assert mean == pytest.approx(bulk * (cfg.phi_free + (1 - cfg.phi_free)
                                         * cfg.eps_res))
    assert effective_suppression(cfg, CORNER) == pytest.approx(bulk / mean)


def test_s_needed_identity_with_gate_ratio() -> None:
    """S_need = Γ_bulk·τ_OR = τ_OR/τ_dec_bulk — analytische Identität."""
    for dm in (DELTA_M_ITER16, DELTA_M_FLOOR, 5e-3):
        need = s_needed(CORNER, dm)
        via_ratio = penrose_tau_or_s(CORNER) / tegmark_tau_dec_s(
            ORConfig(delta_m_over_m_bulk=dm, shielding=1.0))
        assert need == pytest.approx(via_ratio, rel=1e-9)


def test_monotonicity_in_shielding_parameters() -> None:
    """Mehr Schutz (kleineres φ_free, kleineres ε_res) → kleinere Rate,
    größere Unterdrückung, kleinere Ratio."""
    r_bulk = gamma_bulk_collision_per_s(CORNER, DELTA_M_ITER16)
    prev_rate = None
    prev_supp = None
    for phi, eps in ((1.0, 1.0), (1e-2, 1e-2), (1e-4, 1e-2), (1e-4, 1e-6)):
        cfg = ShieldingConfig(phi_free=phi, eps_res=eps,
                              delta_m_over_m=DELTA_M_ITER16)
        rate = mean_core_gamma_per_s(cfg, CORNER)
        supp = effective_suppression(cfg, CORNER)
        assert rate < r_bulk or (phi == 1.0 and eps == 1.0
                                 and rate == pytest.approx(r_bulk))
        if prev_rate is not None:
            assert rate < prev_rate
            assert supp > prev_supp
        prev_rate, prev_supp = rate, supp


def test_corner_no_coherence_core_at_registered_floors() -> None:
    """Ecke (Δm/m=1e-2): benötigt φ_in ≈ 1.6e-6 < Floor 1e-4 → kein Kern."""
    cfg = ShieldingConfig(phi_free=PHI_FREE_FLOOR,
                          eps_res=EPS_RES_OPTIMISTIC,
                          delta_m_over_m=DELTA_M_ITER16)
    need = required_phi_free(cfg, CORNER)
    assert need < PHI_FREE_FLOOR
    assert coherence_core_radius_nm(cfg, CORNER) == 0.0


def test_core_exists_in_confluence_region() -> None:
    """Δm/m = 1e-3, optimistisch: Γ̄ < Γ_need → Kern = r_core (Konsistenz
    der Zwei-Zonen-Geometrie, keine Ergebnis-Buchung)."""
    cfg = ShieldingConfig(phi_free=PHI_FREE_FLOOR,
                          eps_res=EPS_RES_OPTIMISTIC,
                          delta_m_over_m=1e-3)
    assert mean_core_gamma_per_s(cfg, CORNER) < gamma_needed_per_s(CORNER)
    assert coherence_core_radius_nm(cfg, CORNER) == cfg.r_core_nm


def test_corner_ratio_matches_gamma_definition() -> None:
    """ratio = Γ̄·τ_OR — identisch zur Gate-Definition in orch_or."""
    cfg = ShieldingConfig(phi_free=1e-3, eps_res=1e-4,
                          delta_m_over_m=DELTA_M_ITER16)
    expected = mean_core_gamma_per_s(cfg, CORNER) * penrose_tau_or_s(CORNER)
    assert corner_ratio(cfg, CORNER) == pytest.approx(expected, rel=1e-12)
    assert corner_ratio(cfg, CORNER) == pytest.approx(
        penrose_tau_or_s(CORNER) / (1.0 / mean_core_gamma_per_s(cfg, CORNER)),
        rel=1e-12)


def test_validation_rejects_bad_parameters() -> None:
    with pytest.raises(ValueError):
        ShieldingConfig(phi_free=-0.1)
    with pytest.raises(ValueError):
        ShieldingConfig(eps_res=2.0)
    with pytest.raises(ValueError):
        ShieldingConfig(delta_m_over_m=0.0)
    with pytest.raises(ValueError):
        ShieldingConfig(r_core_nm=0.0)
    with pytest.raises(ValueError):
        gamma_bulk_collision_per_s(CORNER, 0.0)


def test_registered_floors_are_importable_constants() -> None:
    """Registrierte Schranken unveränderlich als Modul-Konstanten."""
    assert PHI_FREE_FLOOR == 1e-4
    assert EPS_RES_PESSIMISTIC == 1e-2
    assert EPS_RES_OPTIMISTIC == 1e-6
    assert DELTA_M_FLOOR == 1e-4
    assert DELTA_M_ITER16 == 1e-2
    assert math.isfinite(gamma_needed_per_s(CORNER))
