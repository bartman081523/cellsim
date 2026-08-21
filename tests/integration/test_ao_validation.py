"""Integration: Asakura-Oosawa-Validierung gegen experimentelle Diffusionsdaten."""

from __future__ import annotations

import numpy as np

from cellsim.data.diffusion_experimental import (
    DEFAULT_MEASUREMENTS,
    crowding_reduction_factor,
    get_measurements,
)
from cellsim.modules.asakura_oosawa import (
    AOParams,
    ao_diffusion_modifier,
    compute_depletion_field,
)


def test_experimental_dataset_loadable() -> None:
    meas = get_measurements()
    assert len(meas) >= 3


def test_crowding_reduces_diffusion() -> None:
    """Alle Messungen zeigen D_crowded < D_bulk."""
    for m in DEFAULT_MEASUREMENTS:
        ratio = crowding_reduction_factor(m)
        assert ratio < 1.0, f"{m.species}: Crowding reduziert D nicht"


def test_ao_predicts_crowding_effect() -> None:
    """A-O-Modell sagt eine D-Reduktion voraus (Richtung OK)."""
    counts = np.full((4, 4, 4), 100, dtype=np.int64)
    field = compute_depletion_field(counts, voxel_edge_nm=10.0)
    d_field = ao_diffusion_modifier(field, d_bulk_nm2_per_ms=100.0, sensitivity=0.5)
    assert d_field.mean() < 100.0  # Reduktion


def test_ao_with_experimental_calibration() -> None:
    """Kalibrierung des A-O-Modells gegen gemessene D-Werte."""
    results = []
    for m in DEFAULT_MEASUREMENTS:
        # Setup: Voxel mit Crowdern + 1 großes Makromolekül pro Voxel
        crowder_counts = np.full((4, 4, 4), 50, dtype=np.int64)
        field = compute_depletion_field(
            crowder_counts,
            voxel_edge_nm=10.0,
            macro_radius_nm=m.radius_nm,
            params=AOParams(crowder_concentration_mM=50.0, crowder_radius_nm=0.5),
        )
        d_local = ao_diffusion_modifier(field, d_bulk_nm2_per_ms=m.D_bulk_nm2_per_ms)
        # Vergleich gegen gemessenes D
        d_predicted = float(d_local.mean())
        ratio = d_predicted / m.D_crowded_nm2_per_ms
        results.append((m.species, m.D_crowded_nm2_per_ms, d_predicted, ratio))

    # Wir erwarten, dass D_predicted in derselben Größenordnung wie D_crowded ist
    for species, d_obs, d_pred, ratio in results:
        # Toleranz: Faktor 10 (A-O ist sehr grob)
        assert 0.1 < ratio < 10.0, (
            f"{species}: predicted={d_pred:.2f}, observed={d_obs:.2f}, ratio={ratio:.2f}"
        )


def test_ao_validation_summary() -> None:
    """Schreibt eine Kalibrierungs-Zusammenfassung (kann manuell geprüft werden)."""
    print("\n=== A-O Validierung ===")
    for m in DEFAULT_MEASUREMENTS:
        reduction = crowding_reduction_factor(m)
        print(f"  {m.species:>15s}: D_bulk={m.D_bulk_nm2_per_ms:.0f}, "
              f"D_crowded={m.D_crowded_nm2_per_ms:.0f}, "
              f"reduction={reduction:.2f}, method={m.method}")
