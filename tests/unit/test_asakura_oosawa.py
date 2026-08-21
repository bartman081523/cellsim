"""Tests für Asakura-Oosawa-Depletion-Modul (L2↔L3-Brücke)."""

from __future__ import annotations

import numpy as np

from cellsim.modules.asakura_oosawa import (
    AOParams,
    DepletionField,
    ao_diffusion_modifier,
    compute_depletion_field,
    depletion_overlap_volume,
)


def test_overlap_volume_zero_at_distance() -> None:
    """Wenn Distanz > R_i + R_j, kein Überlapp."""
    v = depletion_overlap_volume(r_nm=15.0, r_i_nm=5.0, r_j_nm=5.0)
    assert v == 0.0


def test_overlap_volume_positive_when_close() -> None:
    """Wenn Distanz < R_i + R_j, positives Überlappungsvolumen."""
    v = depletion_overlap_volume(r_nm=8.0, r_i_nm=5.0, r_j_nm=5.0)
    assert v > 0.0


def test_overlap_volume_full_overlap() -> None:
    """Wenn Distanz <= |R_i - R_j|, vollständige Inklusion."""
    v = depletion_overlap_volume(r_nm=2.0, r_i_nm=5.0, r_j_nm=3.0)
    expected = (4.0 / 3.0) * np.pi * 3.0**3
    assert abs(v - expected) < 1e-6


def test_depletion_field_returns_positive_potential() -> None:
    """Mit Crowder im Voxel ist die attraktive Kraft positiv."""
    counts = np.zeros((4, 4, 4), dtype=np.int64)
    counts[1, 1, 1] = 100
    field = compute_depletion_field(counts, voxel_edge_nm=10.0)
    assert field.attractive_potential_nm3[1, 1, 1] > 0.0
    assert field.attractive_potential_nm3[0, 0, 0] == 0.0


def test_depletion_field_pressure_positive() -> None:
    counts = np.full((2, 2, 2), 10, dtype=np.int64)
    field = compute_depletion_field(counts, voxel_edge_nm=10.0)
    assert field.osmotic_pressure_pa > 0.0


def test_ao_diffusion_modifier_decreases_d_for_inhomogeneous_field() -> None:
    """Höheres Crowding lokal → niedrigerer D lokal."""
    counts = np.zeros((4, 4, 4), dtype=np.int64)
    counts[0, 0, 0] = 10      # niedriges Crowding
    counts[3, 3, 3] = 1000    # hohes Crowding
    field = compute_depletion_field(counts, voxel_edge_nm=10.0)
    d = ao_diffusion_modifier(field, d_bulk_nm2_per_ms=1.0e3)
    # Dichte Voxel: niedrigerer D
    assert d[0, 0, 0] > d[3, 3, 3]


def test_ao_diffusion_modifier_uniform_field_keeps_d_constant() -> None:
    """Bei uniformem Crowding-Feld bleibt D überall gleich."""
    counts = np.full((2, 2, 2), 100, dtype=np.int64)
    field = compute_depletion_field(counts, voxel_edge_nm=10.0)
    d = ao_diffusion_modifier(field, d_bulk_nm2_per_ms=1.0e3)
    # Dichte ist überall gleich, also D auch (innerhalb FP-Toleranz)
    assert abs(d.max() - d.min()) < 1e-9


def test_ao_params_default_temperature() -> None:
    params = AOParams()
    assert params.temperature_K == 310.0
