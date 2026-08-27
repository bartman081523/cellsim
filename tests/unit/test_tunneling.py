"""Tests für Proton-Tunneling-Schicht."""

from __future__ import annotations

import pytest

from cellsim.quantum.tunneling import (
    arrhenius_rate,
    bell_tunnel_probability,
    quantum_enhancement,
    wigner_tunnel_probability,
)


def test_arrhenius_rate_positive() -> None:
    r = arrhenius_rate(prefactor=1e6, activation_eV=0.5, temperature_K=310.0)
    assert r > 0.0


def test_arrhenius_rate_decreases_with_activation() -> None:
    r1 = arrhenius_rate(1e6, 0.3, 310.0)
    r2 = arrhenius_rate(1e6, 0.7, 310.0)
    assert r1 > r2   # höhere Aktivierungsenergie → niedrigere Rate


def test_wigner_probability_decreases_with_width() -> None:
    """Tunnelwahrscheinlichkeit fällt exponentiell mit Breite."""
    p_thin = wigner_tunnel_probability(0.5, 0.3)
    p_thick = wigner_tunnel_probability(0.5, 1.5)
    assert p_thin > p_thick
    assert p_thin / p_thick > 1e10  # exponentieller Abfall


def test_bell_probability_thermal_assisted() -> None:
    """Bell-Korrektur: bei höherer T leicht höhere Tunnel-Wahrscheinlichkeit.

    Bell-Faktor modelliert asymmetrische Barriere; klein gegen Wigner.
    """
    p_cold = bell_tunnel_probability(0.5, 0.5, 77.0)
    p_warm = bell_tunnel_probability(0.5, 0.5, 310.0)
    # Bell skaliert mit T (thermisch assistiert)
    assert p_warm >= p_cold
    # Beide klein gegen 1
    assert p_warm < 1.0
    assert p_cold < 1.0


def test_quantum_enhancement_at_body_temp() -> None:
    """Bei 310 K und 0.5 Å-Barriere: Enhancement ~1.0 (thermische Aktivierung dominiert)."""
    enh = quantum_enhancement(0.5, 0.5, 310.0)
    assert 0.99 < enh["enhancement_factor"] < 2.0


def test_quantum_enhancement_at_cryo() -> None:
    """Bei 77 K: Wigner-Faktor ist winzig klein (< 10⁻⁶), aber exp(-V/kBT)
    bei 77 K → klassische Rate ist ähnlich klein → Enhancement = 1 + p_w
    bleibt nahe 1.
    """
    enh = quantum_enhancement(0.5, 0.5, 77.0)
    # Tunneling-Enhancement ist ein ADDITIVER Beitrag, daher nahe 1
    assert 0.99 < enh["enhancement_factor"] < 1.0001


def test_quantum_enhancement_thin_barrier_at_body_temp() -> None:
    """Bei 0.3 Å-Barriere und 310 K: messbarer Tunneling-Effekt (≈ 1 + p_w)."""
    enh = quantum_enhancement(0.5, 0.3, 310.0)
    # Bei 0.3 Å, V=0.5 eV: p_w ≈ 9e-5, daher Enhancement ≈ 1 + 9e-5 ≈ 1.00009
    assert 1.0 < enh["enhancement_factor"] < 1.001
    # Aber wir wollen, dass es > 1.0 ist (Tunneling hinzufügt)
    assert enh["enhancement_factor"] > 1.0


def test_quantum_enhancement_returns_log10() -> None:
    enh = quantum_enhancement(0.5, 0.3, 310.0)
    assert "log10_enhancement" in enh
    # log10(1.00009) ≈ 4e-5 (klein positiv)
    assert -1e-3 < enh["log10_enhancement"] < 1e-3


def test_isotope_effect_d_h_t() -> None:
    """Deuterium (D, 2× Masse) und Tritium (T, 3× Masse) tunneln weniger als H.

    Physikalischer Isotop-Effekt: schwerere Isotope haben kleinere
    Tunnel-Wahrscheinlichkeit (kappa ~ sqrt(m)).
    """
    # Mit verschiedenen Massen für H, D, T
    e_h = quantum_enhancement(0.5, 0.3, 310.0, proton_mass_kg=1.6726e-27)
    e_d = quantum_enhancement(0.5, 0.3, 310.0, proton_mass_kg=2 * 1.6726e-27)
    e_t = quantum_enhancement(0.5, 0.3, 310.0, proton_mass_kg=3 * 1.6726e-27)
    # Schwerere Masse → kleinere Tunnel-Wahrscheinlichkeit
    assert e_h["p_wigner"] > e_d["p_wigner"] > e_t["p_wigner"]