"""Tests für Emergenz-Metriken (portiert aus Origin_Ruliad)."""

from __future__ import annotations

import numpy as np

from cellsim.modules.emergence import (
    binarize,
    laplacian_3d,
    lz_complexity_binary,
    mutual_information_binary,
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