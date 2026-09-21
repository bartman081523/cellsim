"""Tests für Emergenz-Metriken (portiert aus Origin_Ruliad)."""

from __future__ import annotations

import numpy as np
import pytest

from cellsim.core.rng import make_rng
from cellsim.modules.emergence import (
    binarize,
    laplacian_3d,
    lz_complexity_binary,
    mutual_information_binary,
    permutation_contrast_test,
    radial_power_spectrum,
    stochastic_jump_diffusion,
)


def test_binarize_quantile_splits() -> None:
    z = np.array([1.0, 2.0, 3.0, 4.0])
    b = binarize(z, q=0.5)
    assert b.dtype == np.uint8
    assert set(np.unique(b).tolist()) <= {0, 1}


def test_mutual_information_identical_fields_equals_entropy() -> None:
    """MI(X, X) = H(X) — statische Felder haben volle Selbst-Information."""
    rng = np.random.default_rng(42)
    a = (rng.random(20000) > 0.5).astype(np.uint8)
    mi = mutual_information_binary(a, a)
    assert 0.9 < mi < 1.0


def test_mutual_information_independent_fields_near_zero() -> None:
    """Unabhängige Felder haben MI ≈ 0."""
    rng = np.random.default_rng(42)
    a = (rng.random(50000) > 0.5).astype(np.uint8)
    b = (rng.random(50000) > 0.5).astype(np.uint8)
    mi = mutual_information_binary(a, b)
    assert mi < 0.01


def test_lz_complexity_random_field_high() -> None:
    """Zufallsfelder haben hohe LZ-Komplexität (~2.0 in Origin_Ruliad-Norm)."""
    rng = np.random.default_rng(42)
    noise = (rng.random(10000) > 0.5).astype(np.uint8)
    assert lz_complexity_binary(noise) > 1.5


def test_lz_complexity_uniform_field_low() -> None:
    """Konstante Felder haben niedrige LZ-Komplexität (~0.45)."""
    lz = lz_complexity_binary(np.ones(1000, dtype=np.uint8))
    assert lz < 0.6


def test_lz_complexity_random_much_higher_than_uniform() -> None:
    """Rauschen hat deutlich höhere LZ als konstante Felder."""
    rng = np.random.default_rng(42)
    lz_random = lz_complexity_binary((rng.random(10000) > 0.5).astype(np.uint8))
    lz_const = lz_complexity_binary(np.ones(1000, dtype=np.uint8))
    assert lz_random > 1.5
    assert lz_random > 2 * lz_const


def test_laplacian_3d_zero_for_constant_field() -> None:
    """Konstantes Feld → Laplacian = 0."""
    z = np.full((5, 5, 5), 7.0)
    lap = laplacian_3d(z)
    assert np.allclose(lap, 0.0)


def test_laplacian_3d_flux_direction() -> None:
    """Am Peak ist der Laplacian negativ (fließt weg), an Senken positiv."""
    z = np.zeros((5, 5, 5))
    z[2, 2, 2] = 100.0
    lap = laplacian_3d(z)
    assert lap[2, 2, 2] < 0
    assert lap[1, 2, 2] > 0


# --- Stochastische Sprung-Diffusion (iter-12) ------------------------


def test_jump_diffusion_mass_conserved_exactly() -> None:
    """Massenerhalt exakt über alle Achsen (Sprung-Teilchen, kein rint)."""
    rng = make_rng(1, 0, 0)
    fields = {
        f"s{i}": rng.integers(0, 50, size=(6, 6, 6)).astype(np.int64)
        for i in range(3)
    }
    before = sum(int(f.sum()) for f in fields.values())
    for _ in range(20):
        stochastic_jump_diffusion(fields, 0.30, rng)
    after = sum(int(f.sum()) for f in fields.values())
    assert before == after


def test_jump_diffusion_single_particle_survives() -> None:
    """O(1)-Counts überleben — delta-Funktion diffundiert statt zu
    verschwinden (iter-12 Diskretheits-Boden der rint-Variante)."""
    rng = make_rng(2, 0, 0)
    fields = {"a": np.zeros((8, 8, 8), dtype=np.int64)}
    fields["a"][3, 3, 3] = 1
    for _ in range(50):
        stochastic_jump_diffusion(fields, 0.20, rng)
        assert int(fields["a"].sum()) == 1
    # Bewegungs-Wahrscheinlichkeit ~1−(1−p)¹² ≈ 0.93/Schritt: nach 50
    # Schritten ist Gehen sicher; Teilchen verlässt Startpunkt
    # (Determinismus via Seed).
    assert fields["a"][3, 3, 3] == 0


def test_jump_diffusion_no_drift() -> None:
    """iter-15-Fix: beidseitige Sprünge — Delta-Funktion breitet sich
    symmetrisch aus (Erwartungswert bleibt am Startort), kein
    upwind-Advektions-Drift mehr."""
    n_runs = 400
    displacement: list[float] = []
    for run in range(n_runs):
        rng = make_rng(1000 + run, 0, 0)
        fields = {"a": np.zeros((9, 9, 9), dtype=np.int64)}
        fields["a"][4, 4, 4] = 1
        for _ in range(100):
            stochastic_jump_diffusion(fields, 0.30, rng)
        coords = np.argwhere(fields["a"] == 1)
        assert coords.shape[0] == 1
        displacement.append(float(np.abs(coords[0] - 4).max()))
    mean_displacement = float(np.mean(displacement))
    # Unbiased walk: E[|Δ|max nach 100 Schritten, D=0.3] ~ O(√(𝒟t));
    # der alte upwind-Drift hätte ~30 Voxel erzeugt (p·t = 0.3·100).
    assert mean_displacement < 10.0


def test_jump_diffusion_deterministic() -> None:
    """Gleicher Seed → identisches Feld; Counts bleiben nicht-negativ."""
    runs = []
    for _ in range(2):
        rng = make_rng(7, 0, 0)
        fields = {
            "a": rng.integers(0, 30, size=(5, 5, 5)).astype(np.int64)
        }
        for _ in range(30):
            stochastic_jump_diffusion(fields, 0.45, rng)
        runs.append(fields["a"].copy())
    assert np.array_equal(runs[0], runs[1])
    assert int(runs[0].min()) >= 0


def test_jump_diffusion_dense_field_no_mean_drift() -> None:
    """Dichtes Feld: Mittelwert bleibt exakt (Summen-Erhalt)."""
    rng = make_rng(11, 0, 0)
    fields = {"a": (rng.poisson(50, size=(8, 8, 8))).astype(np.int64)}
    mean_before = float(fields["a"].mean())
    for _ in range(10):
        stochastic_jump_diffusion(fields, 0.15, rng)
    assert abs(float(fields["a"].mean()) - mean_before) < 1e-9


# --- Permutations-Statistik für spärliche Felder (iter-12) -----------


def test_permutation_test_uniform_observation_high_p() -> None:
    """Beobachtung ≈ H0-Erwartung → hoher p-Wert (keine Signifikanz)."""
    r = permutation_contrast_test(
        n_events=100, n_total_sites=1000, n_zone_sites=100,
        n_in_zone_observed=10, n_permutations=2000, seed=3,
    )
    assert r["expected_in_zone_h0"] == 10.0
    assert r["p_value"] > 0.3


def test_permutation_test_localized_events_low_p() -> None:
    """Alle Events in kleinem Bereich → p klein (starke Lokalisierung)."""
    r = permutation_contrast_test(
        n_events=50, n_total_sites=1000, n_zone_sites=5,
        n_in_zone_observed=50, n_permutations=2000, seed=3,
    )
    assert r["expected_in_zone_h0"] == 0.25
    assert r["p_value"] < 0.001


def test_permutation_test_deterministic() -> None:
    a = permutation_contrast_test(30, 500, 10, 15, n_permutations=500, seed=9)
    b = permutation_contrast_test(30, 500, 10, 15, n_permutations=500, seed=9)
    assert a["p_value"] == b["p_value"]
    assert a["h0_p99"] == b["h0_p99"]


def test_permutation_test_zero_events() -> None:
    r = permutation_contrast_test(0, 100, 10, 0, n_permutations=100, seed=1)
    assert r["p_value"] == 1.0
    assert r["expected_in_zone_h0"] == 0.0


def test_permutation_test_validates_inputs() -> None:
    with pytest.raises(ValueError):
        permutation_contrast_test(10, 100, 200, 5)
    with pytest.raises(ValueError):
        permutation_contrast_test(10, 100, 10, 11)
    with pytest.raises(ValueError):
        permutation_contrast_test(10, 100, 10, 5, n_permutations=0)


# --- Radiales Leistungsspektrum (iter-17) -----------------------------


def test_spectrum_plane_wave_peak_at_predicted_k() -> None:
    """Ebene Welle sin(2π·n·x/L) → Peak bei |k| = 2π·n/L.

    Direkt die iter-17-Vorhersage: das Schnakenberg-Muster mit
    λ* ≈ 8 Voxel auf einem L=24-Gitter entspricht Shell n=3,
    k = 2π·3/24 ≈ 0.785 rad/Zelle.
    """
    n_grid, mode = 24, 3
    x = np.arange(n_grid)
    field = np.sin(2.0 * np.pi * mode * x / n_grid) + 3.0
    field = np.broadcast_to(field, (n_grid, n_grid, n_grid)).copy()
    k_vals, power = radial_power_spectrum(field)
    assert k_vals[0] > 0.0  # k=0 ausgeklammert
    k_peak = float(k_vals[np.argmax(power)])
    assert abs(k_peak - 2.0 * np.pi * mode / n_grid) < 0.05


def test_spectrum_constant_field_no_k0_leakage() -> None:
    """Konstantes Feld → mittelfrei, Leistung nur bei k=0 (entfernt)."""
    field = np.full((8, 8, 8), 12.5)
    k_vals, power = radial_power_spectrum(field)
    assert k_vals.shape == power.shape
    assert k_vals[0] > 0.0
    assert float(power.max()) < 1e-6


def test_spectrum_noise_no_dominant_peak() -> None:
    """Weißes Rauschen: kein Peak dominiert (max/median moderat)."""
    rng = make_rng(5, 0, 0)
    field = rng.poisson(3.0, size=(16, 16, 16)).astype(np.float64)
    k_vals, power = radial_power_spectrum(field)
    ratio = float(power.max() / max(np.median(power), 1e-12))
    assert ratio < 10.0


def test_spectrum_rejects_1d() -> None:
    with pytest.raises(ValueError):
        radial_power_spectrum(np.arange(16.0))


def test_spectrum_deterministic() -> None:
    rng = make_rng(6, 0, 0)
    field = rng.poisson(5.0, size=(10, 10, 10)).astype(np.float64)
    a = radial_power_spectrum(field)
    b = radial_power_spectrum(field)
    assert np.array_equal(a[0], b[0])
    assert np.array_equal(a[1], b[1])
