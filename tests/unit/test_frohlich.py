"""Tests für Fröhlich-Kondensation-Stub (revidiert nach Reimers et al. 2010)."""

from __future__ import annotations

from cellsim.modules.frohlich import (
    FROEHLICH_IN_VIVO_STATUS,
    FrohlichAdapter,
)


def test_frohlich_in_vivo_status_is_refuted() -> None:
    """Fröhlich in vivo ist REFUTED_BY_REIMERS_2010."""
    assert FROEHLICH_IN_VIVO_STATUS == "REFUTED_BY_REIMERS_2010"


def test_frohlich_starts_with_zero_coherence() -> None:
    f = FrohlichAdapter()
    assert f.state.coherence_order_parameter == 0.0


def test_frohlich_atp_savings_max_0_1_percent() -> None:
    """REVIDIERT nach Reimers et al. (2010): max 0.1% ATP-Einsparung.

    Vorher: 5% (HYPOTHESE)
    Jetzt:  0.1% (REFUTED_BY_REIMERS_2010)
    """
    f = FrohlichAdapter(initial_coherence=1.0)
    savings_factor = f.atp_savings_factor()
    assert savings_factor >= 0.999    # max 0.1% Einsparung
    assert savings_factor <= 1.0


def test_frohlich_coherence_capped_at_one() -> None:
    f = FrohlichAdapter()
    for _ in range(1000):
        f.step(dt_s=1.0, energy_input_j=1.0)
    assert f.state.coherence_order_parameter <= 1.0


def test_frohlich_telemetry_includes_status() -> None:
    """Telemetrie enthält frohlich_status als Marker."""
    f = FrohlichAdapter()
    tel = f.step(dt_s=1e-3, energy_input_j=1e-15)
    assert "frohlich_coherence" in tel
    assert "frohlich_status" in tel
