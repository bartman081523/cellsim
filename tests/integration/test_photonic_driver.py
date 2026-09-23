"""Integration: Photonische Kopplung im HybridDriver (iter-23).

Prüft das Produktions-Wiring (Quelle an/aus, run.csv-Schema,
Determinismus) — KEINE Ergebnis-Buchung.
"""

from __future__ import annotations

import csv

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.time_axis import TimeAxis
from cellsim.driver.loop import (
    HybridDriver,
    default_chromosome,
    default_membrane,
    default_ode,
    write_run_csv,
)
from cellsim.modules.photonic_coupling import PhotonicSource
from cellsim.modules.reactions import default_registry


def _make_driver(photonic: object | None, seed: int = 49582) -> HybridDriver:

    axis = TimeAxis(
        t_start_s=0.0,
        t_end_s=0.05,
        dt_rdme_s=1e-3,
        dt_ode_s=1e-3,
    )
    return HybridDriver(
        time_axis=axis,
        rdme=RDMEAdapter(registry=default_registry(), grid_shape=(6, 6, 6)),
        ode=default_ode(),
        chromosome=default_chromosome(seed=seed),
        membrane=default_membrane(),
        sync_interval=10,
        seed=seed,
        photonic=photonic,
    )


def test_photonic_columns_present_with_and_without_source(tmp_path) -> None:
    """Schema stabil: 4 Photonics-Spalten immer vorhanden (0.0 ohne Quelle)."""
    for name, photonic in (("no_source", None), ("with_source", PhotonicSource())):
        result = _make_driver(photonic).run()
        csv_path = write_run_csv(result, tmp_path / name / "run.csv")
        with csv_path.open() as fh:
            header = next(csv.reader(fh))
        for col in (
            "photon_rate_per_s",
            "photon_flux_cm2_s",
            "photochem_turnover_per_s",
            "photon_pump_capped",
        ):
            assert col in header
        assert len(result.photon_rate_per_s) == len(result.time_s)


def test_photonic_source_telemetry_values() -> None:
    """Mit Quelle: Raten > 0, Pump-Cap inaktiv (Default f=1 Hz)."""
    src = PhotonicSource()
    result = _make_driver(src).run()
    assert all(v > 0.0 for v in result.photon_rate_per_s)
    assert all(v > 0.0 for v in result.photochem_turnover_per_s)
    assert all(v == 0.0 for v in result.photon_pump_capped)


def test_photonic_off_by_default_zero_columns() -> None:
    """Default (keine Quelle): alle 4 Spalten exakt 0.0."""
    result = _make_driver(None).run()
    for series in (
        result.photon_rate_per_s,
        result.photon_flux_cm2_s,
        result.photochem_turnover_per_s,
        result.photon_pump_capped,
    ):
        assert series and all(v == 0.0 for v in series)


def test_photonic_run_deterministic(tmp_path) -> None:
    """Gleicher Seed → bit-identische run.csv (Konvention test_rdme_ode_sync)."""
    out_a = tmp_path / "a" / "run.csv"
    out_b = tmp_path / "b" / "run.csv"
    write_run_csv(_make_driver(PhotonicSource(), seed=1234).run(), out_a)
    write_run_csv(_make_driver(PhotonicSource(), seed=1234).run(), out_b)
    assert out_a.read_bytes() == out_b.read_bytes()
