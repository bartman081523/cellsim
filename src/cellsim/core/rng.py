"""Seedable RNG-Factory.

Konvention aus MT_Sim: `base_seed + run_idx * num_conditions + cond_idx`.
"""

from __future__ import annotations

import numpy as np

from cellsim.core.constants import SEED_BASE


def make_rng(
    base_seed: int = SEED_BASE,
    run_idx: int = 0,
    cond_idx: int = 0,
) -> np.random.Generator:
    """Baut einen seedable Generator.

    Identische (base, run, cond) → identische Sequenz.
    """
    seed = base_seed + run_idx * 1024 + cond_idx
    return np.random.default_rng(seed=seed)


def seed_for(base_seed: int, run_idx: int, cond_idx: int) -> int:
    """Gibt nur den effektiven Seed zurück (für Manifest-Output)."""
    return base_seed + run_idx * 1024 + cond_idx
