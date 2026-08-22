"""Tests für QuQuint-VQE-Schicht."""

from __future__ import annotations

import pytest

from cellsim.quantum.ququint import (
    QuQuintParams,
    H_PT_ququint,
    gf5_add,
    gf5_inverse,
    gf5_mul,
    threshold_improvement_factor,
)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0, 0, 0),
        (1, 2, 3),
        (3, 4, 2),   # 7 mod 5 = 2
        (4, 4, 3),   # 8 mod 5 = 3
    ],
)
def test_gf5_add(a: int, b: int, expected: int) -> None:
    assert gf5_add(a, b) == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, 1),
        (2, 3, 1),   # 6 mod 5 = 1
        (4, 2, 3),   # 8 mod 5 = 3
    ],
)
def test_gf5_mul(a: int, b: int, expected: int) -> None:
    assert gf5_mul(a, b) == expected


@pytest.mark.parametrize(
    "a,expected",
    [(1, 1), (2, 3), (3, 2), (4, 4)],   # 4*4=16≡1 (mod 5)
)
def test_gf5_inverse(a: int, expected: int) -> None:
    assert gf5_inverse(a) == expected


def test_gf5_inverse_zero_raises() -> None:
    with pytest.raises(ZeroDivisionError):
        gf5_inverse(0)


def test_threshold_improvement_factor() -> None:
    f = threshold_improvement_factor()
    assert 30.0 < f < 40.0   # ~36.3 erwartet


def test_H_PT_ququint_is_5x5() -> None:
    import numpy as np

    E = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    H = H_PT_ququint(E, QuQuintParams(gamma=0.05))
    assert H.shape == (5, 5)


def test_H_PT_ququint_has_imaginary_perturbation() -> None:
    """Bei gamma > 0 muss H nicht-Hermite'sch sein (komplex)."""
    import numpy as np

    E = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    H = H_PT_ququint(E, QuQuintParams(gamma=0.05))
    # H ist komplex (Imaginaerteil != 0)
    assert np.any(np.abs(H.imag) > 0)
    # Diagonal ist reell (Eigenwerte)
    assert np.allclose(np.diag(H).imag, 0)


def test_H_PT_ququint_diag_matches_input() -> None:
    import numpy as np

    E = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    H = H_PT_ququint(E, QuQuintParams(gamma=0.02))
    np.testing.assert_allclose(np.diag(H).real, E)
