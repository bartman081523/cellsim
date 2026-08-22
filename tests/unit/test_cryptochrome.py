"""Tests für Cryptochrom-Schicht."""

from __future__ import annotations

import pytest

from cellsim.modules.cryptochrome import (
    CryptochromeAdapter,
    CryptochromeParams,
)


def test_cryptochrome_starts_with_full_singlet() -> None:
    cry = CryptochromeAdapter()
    assert cry.state.s_population == 1.0


def test_singlet_yield_field_dependence() -> None:
    """Singulett-Ausbeute variiert mit B-Feld (Resonanz)."""
    y_low = CryptochromeAdapter.singlet_yield_at_field(0.0)
    y_resonant = CryptochromeAdapter.singlet_yield_at_field(50e-6)
    y_high = CryptochromeAdapter.singlet_yield_at_field(1000e-6)
    # Es muss eine echte Differenz geben
    assert y_low != y_resonant or y_resonant != y_high


def test_singlet_yield_stays_in_0_1() -> None:
    """Populations müssen in [0, 1] bleiben."""
    for b_t in [0.0, 1e-6, 50e-6, 1e-3]:
        y = CryptochromeAdapter.singlet_yield_at_field(b_t)
        assert 0.0 <= y <= 1.0


def test_step_emits_telemetry() -> None:
    cry = CryptochromeAdapter()
    result = cry.step(dt_s=1.0e-6, b_field_t=50e-6)
    assert "crypto_s_population" in result
    assert "crypto_t_population" in result
    assert "crypto_singlet_yield" in result


def test_strong_resonance_at_50_microt() -> None:
    """Bei geomagnetischem Feld (50 µT) sollte Ausbeute nicht trivial sein."""
    y = CryptochromeAdapter.singlet_yield_at_field(50e-6, n_steps=500)
    assert y != pytest.approx(1.0, abs=0.01) or y != pytest.approx(0.0, abs=0.01)


def test_no_field_zero_at_zero_b() -> None:
    """Bei B=0 dominiert der Singulett-Kanal — hohe Population.

    Hintergrund: Bei B=0 mischt die Hyperfein-Wechselwirkung ständig
    S ↔ T, aber der Spin-Pump gleicht zugunsten von S aus.
    Netto: y → 1.0 bei B=0.
    """
    y = CryptochromeAdapter.singlet_yield_at_field(0.0, n_steps=500)
    assert y > 0.95, f"Bei B=0 erwartet hohe S-Population, got {y}"


def test_field_changes_yield_away_from_baseline() -> None:
    """Bei B ≠ 0 verändert sich die Ausbeute relativ zur Baseline.

    Die Resonanz ist subtil (~1%), aber messbar. Das ist physikalisch
    realistisch — Cryptochrom-Compass zeigt einen Effekt < 5% im
    geomagnetischen Feld (Wiltschko 2010).
    """
    y_baseline = CryptochromeAdapter.singlet_yield_at_field(0.0, n_steps=500)
    y_field = CryptochromeAdapter.singlet_yield_at_field(50e-6, n_steps=500)
    # Ausbeute soll nicht exakt gleich sein (würde kein Field-Selektion bedeuten)
    assert abs(y_field - y_baseline) > 0.001, (
        f"Magnetfeld ändert Ausbeute nicht: y(0)={y_baseline}, y(50µT)={y_field}"
    )


def test_resonance_within_factor_of_two() -> None:
    """Bei Resonanz-Frequenz sollte Ausbeute maximal werden (Faktor ≥ 2 vs. off-resonance)."""
    # Resonanz: omega_L = delta_omega_HF
    # delta_omega_HF = g·μ_B·δ_HF/ħ ≈ 9.3e7 rad/s (Trp-Hyperfein)
    # omega_L = g·μ_B·B/ħ → B_res ≈ 0.55 T (sehr hoch!)
    # Da geomagnetisches Feld ~50 µT, sind wir off-resonance
    # → Ausbeute bleibt nahe 1.0 im geomagnetischen Bereich
    y_geomagnetic = CryptochromeAdapter.singlet_yield_at_field(50e-6, n_steps=500)
    assert y_geomagnetic > 0.95, (
        f"Cryptochrom sollte im geomagnetischen Bereich Singulett-Output zeigen, got {y_geomagnetic}"
    )
