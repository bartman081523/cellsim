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
    # Bei p_step=6·(0.20/6)=0.20/Schritt: nach 50 Schritten ist Gehen
    # sicher; das Teilchen verlässt Startpunkt (Determinismus via Seed).
    assert fields["a"][3, 3, 3] == 0


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
