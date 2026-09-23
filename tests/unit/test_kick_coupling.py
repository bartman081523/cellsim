"""Unit-Tests: Kick-Kopplungsbudget (iter-22, kick_coupling.py).

Invarianz-Tests der Modul-Mathematik — KEINE Ergebnis-Buchung (die
Verdict-Logik liegt in scratch/experiments/iter-22 mit Vorab-Registrierung).
"""

from __future__ import annotations

import math

import pytest

from cellsim.modules.kick_coupling import (
    ADDRESSABILITY_KBT_FLOOR,
    DELTA_G_ATP_J,
    N_BOX_MAX,
    REG_E_SINGLE_J,
    TAU_RELAX_GRID_S,
    e_collective_j,
    e_single_j,
    event_rate_per_s,
    gate_min_n_with_shield,
    n_addressable_threshold,
    per_event_thermal_ratio,
    relaxation_window_bias,
    relaxation_window_energy_j,
)
from cellsim.modules.orch_or import (
    G_NEWTON,
    HBAR,
    KB,
    ORConfig,
    penrose_tau_or_s,
)

CORNER = ORConfig()  # iter-16-Ecke: f=5e-2, a=8nm, N=1e9, korreliert, S=1e6


def test_e_collective_matches_inverse_tau_or() -> None:
    """Zweite explizite Route ≡ Produktionspfad ħ/τ_OR (iter-19-Lektion)."""
    for n in (1.0, 1e9, 1e11):
        cfg = ORConfig(n_tubulins=n)
        assert e_collective_j(cfg) == pytest.approx(
            HBAR / penrose_tau_or_s(cfg), rel=1e-12)


def test_e_single_matches_registered_anchor() -> None:
    """E_G(dimer) gegen den registrierten iter-16/18-Anker."""
    assert e_single_j(CORNER) == pytest.approx(REG_E_SINGLE_J, rel=1e-4)


def test_per_event_ratio_is_inverse_atp_scale() -> None:
    """R_1 = E/(k_B·T); konsistenz-Check gegen ΔG_ATP als Kontext-Anker."""
    r1 = per_event_thermal_ratio(CORNER)
    assert r1 == pytest.approx(e_collective_j(CORNER) / (KB * 310.0), rel=1e-12)
    # E_kick/ΔG_ATP = R_1·k_B·T/ΔG_ATP — dieselbe Größe, zweiter Ausdruck
    ratio_atp = e_collective_j(CORNER) / DELTA_G_ATP_J
    assert ratio_atp == pytest.approx(r1 * KB * 310.0 / DELTA_G_ATP_J,
                                      rel=1e-12)


def test_rate_cross_route_identity() -> None:
    """λ = 1/τ_OR (Produktion) ≡ λ = E/ħ (explizit)."""
    for n in (1e9, 1e11):
        cfg = ORConfig(n_tubulins=n)
        assert event_rate_per_s(cfg) == pytest.approx(
            e_collective_j(cfg) / HBAR, rel=1e-12)


def test_relaxation_window_convention() -> None:
    """max(1, τ_relax/τ_OR): seltene Events wirken voll, dichte akkumulieren."""
    # N=1e9: τ_OR ≈ 1.5e-4 s ≫ τ_relax → genau ein Event wirkt voll
    e_slow = relaxation_window_energy_j(ORConfig(), 1e-6)
    assert e_slow == pytest.approx(e_collective_j(ORConfig()), rel=1e-12)
    # N=1e11: τ_OR ≈ 1.5e-8 s < τ_relax → linear akkumuliert
    cfg_fast = ORConfig(n_tubulins=1e11)
    e_fast = relaxation_window_energy_j(cfg_fast, 1e-6)
    n_ev = 1e-6 * event_rate_per_s(cfg_fast)
    assert e_fast == pytest.approx(e_collective_j(cfg_fast) * n_ev, rel=1e-12)
    # zweite Route: τ_relax·E²/ħ (nur im akkumulierenden Zweig)
    assert e_fast == pytest.approx(1e-6 * e_collective_j(cfg_fast)**2 / HBAR,
                                   rel=1e-12)


def test_window_bias_equals_energy_ratio() -> None:
    """Landauer-Kanal = Energie-Kanal (dasselbe Kriterium, zweite Sicht)."""
    for tau in TAU_RELAX_GRID_S:
        b = relaxation_window_bias(CORNER, tau)
        e = relaxation_window_energy_j(CORNER, tau)
        assert b == pytest.approx(e / (KB * 310.0), rel=1e-12)


def test_n_threshold_analytic_vs_bisection() -> None:
    """N*-Formel ≡ numerische Inversion (im Modul assertiert)."""
    for tau in TAU_RELAX_GRID_S:
        n_star = n_addressable_threshold(CORNER, tau)
        assert n_star > 0
    # Skalierung N* ∝ τ_relax^(-1/4) (akkumulierender Zweig)
    n1 = n_addressable_threshold(CORNER, 1e-6)
    n2 = n_addressable_threshold(CORNER, 1e-3)
    assert n2 / n1 == pytest.approx((1e-3 / 1e-6) ** -0.25, rel=1e-6)


def test_threshold_monotone_and_outside_box_for_registered_tau() -> None:
    """N* wächst mit fallendem τ_relax; für registrierte τ_relax außerhalb
    der Box (Invarianz der Formel, KEINE Ergebnis-Buchung — die Box-
    Aussage ist Sache des Experiments)."""
    prev = None
    for tau in (1e-3, 1e-6, 1e-7):
        n_star = n_addressable_threshold(CORNER, tau)
        if prev is not None:
            assert n_star > prev
        prev = n_star


def test_gate_threshold_reuse_consistency() -> None:
    """gate_min_n_with_shield ≡ n_gate_threshold von orch_or (Reuse)."""
    from cellsim.modules.orch_or import n_gate_threshold
    for shield in (1.0, 9.901e3, 1e6):
        n_min = gate_min_n_with_shield(CORNER, shield)
        cfg = ORConfig(shielding=shield)
        assert n_min == pytest.approx(n_gate_threshold(cfg), rel=1e-12)
    # Monotonie: mehr Schild → Gate-ON früher (kleineres N)
    assert gate_min_n_with_shield(CORNER, 1e6) \
        < gate_min_n_with_shield(CORNER, 1.0)


def test_validation_rejects_bad_parameters() -> None:
    from cellsim.modules.kick_coupling import KickBudget
    with pytest.raises(ValueError):
        KickBudget(tau_relax_s=0.0)
    with pytest.raises(ValueError):
        penrose_tau_or_s(ORConfig(n_tubulins=0.5))


def test_registered_floors_are_importable_constants() -> None:
    """Registrierte Schranken unveränderlich als Modul-Konstanten."""
    assert ADDRESSABILITY_KBT_FLOOR == 1.0
    assert N_BOX_MAX == 1e11
    assert TAU_RELAX_GRID_S == (1e-7, 1e-6, 1e-3)
    assert math.isclose(DELTA_G_ATP_J, 8.3e-20)
    assert math.isclose(G_NEWTON, 6.674_30e-11)
