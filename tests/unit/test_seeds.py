"""Tests für seed-Konvention."""

from __future__ import annotations

from cellsim.core.rng import make_rng, seed_for


def test_seed_for_deterministic() -> None:
    assert seed_for(42, 0, 0) == seed_for(42, 0, 0)


def test_seed_for_distinct() -> None:
    assert seed_for(42, 0, 0) != seed_for(42, 0, 1)
    assert seed_for(42, 0, 0) != seed_for(42, 1, 0)


def test_make_rng_reproducible() -> None:
    a = make_rng(42, 0, 0)
    b = make_rng(42, 0, 0)
    for _ in range(10):
        assert a.random() == b.random()


def test_make_rng_distinct() -> None:
    a = make_rng(42, 0, 0)
    b = make_rng(42, 0, 1)
    assert a.random() != b.random()
