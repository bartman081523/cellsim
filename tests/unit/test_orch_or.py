"""Tests für den Orch-OR-Kollaps-Kern (iter-18, VECTOR_OR_KERNEL).

Vorab registrierte Prüfungen:
- Formeln reproduzieren iter-16 (τ_OR ∝ N² korreliert / N unkorreliert)
- Gate-Grenze: S=1 (Tegmark-bulk) → OFF; großzügige Ecke → ON (Ratio 0.61)
- C3-Herniher: syn3A (N_eff=1, S=1) feuert NIE
"""

from __future__ import annotations

import pytest

from cellsim.core.rng import make_rng
from cellsim.modules.orch_or import (
    G_NEWTON,
    HBAR,
    KB,
    ORCollapseKernel,
    ORConfig,
    n_gate_threshold,
    penrose_tau_or_s,
    syn3a_gate_check,
    tegmark_tau_dec_s,
)

# Referenzwerte (iter-16, handgerechnet)
E_SINGLE_J = G_NEWTON * (5e-2 * 1.83e-22) ** 2 / 8e-9   # ≈ 6.985e-49
TAU_DEC_BULK_S = HBAR / (KB * 310.0 * 0.01**2)           # ≈ 2.464e-10


def test_tau_or_scales_n_squared_when_correlated() -> None:
    """Korreliert: E_G ∝ N² → τ_OR ∝ 1/N² (Zehnerpotenz → Faktor 100)."""
    tau_small = penrose_tau_or_s(ORConfig(n_tubulins=1e9))
    tau_large = penrose_tau_or_s(ORConfig(n_tubulins=1e8))
    assert tau_large / tau_small == pytest.approx(100.0)


def test_tau_or_scales_linear_when_uncorrelated() -> None:
    tau_small = penrose_tau_or_s(ORConfig(n_tubulins=1e9, correlated=False))
    tau_large = penrose_tau_or_s(ORConfig(n_tubulins=1e8, correlated=False))
    assert tau_large / tau_small == pytest.approx(10.0)


def test_tau_dec_bulk_matches_tegmark_value() -> None:
    """τ_dec(bulk, Δm/m=0.01, 310 K) ≈ 2.46e-10 s (iter-16-Referenz)."""
    cfg = ORConfig(shielding=1.0)
    assert tegmark_tau_dec_s(cfg) == pytest.approx(TAU_DEC_BULK_S, rel=1e-9)
    assert 2.4e-10 < TAU_DEC_BULK_S < 2.5e-10


def test_default_config_is_the_iter16_viable_corner() -> None:
    """Defaults (f=5e-2, a=8nm, N=1e9, S=1e6) → Ratio 0.61, Gate ON."""
    cfg = ORConfig()
    kernel = ORCollapseKernel(config=cfg)
    assert kernel.tau_or_s == pytest.approx(
        HBAR / (E_SINGLE_J * 1e18), rel=1e-9
    )
    assert 1.4e-4 < kernel.tau_or_s < 1.6e-4
    assert kernel.tau_dec_s == pytest.approx(TAU_DEC_BULK_S * 1e6, rel=1e-9)
    assert 0.5 < kernel.ratio < 0.7
    assert kernel.ratio == pytest.approx(0.613, rel=0.02)
    assert kernel.gate_on


def test_gate_off_at_bulk_shielding() -> None:
    """S=1 (Tegmark-bulk, ehrlicher Boundary) → Ratio ≫ 1 → Gate OFF."""
    kernel = ORCollapseKernel(config=ORConfig(shielding=1.0))
    assert kernel.ratio > 1e5
    assert not kernel.gate_on
    assert kernel.hazard_per_step() == 0.0


def test_gate_off_uncorrelated_even_at_n_1e11() -> None:
    """Ohne Korrelation (E_G ∝ N) klappt selbst N=1e11 nicht."""
    kernel = ORCollapseKernel(
        config=ORConfig(n_tubulins=1e11, correlated=False)
    )
    assert not kernel.gate_on


def test_n_gate_threshold_value() -> None:
    """N* = sqrt(ħ/(τ_dec·e_single)) ≈ 7.8e8 — N=1e9 liegt knapp darüber."""
    cfg = ORConfig()
    n_star = n_gate_threshold(cfg)
    assert 7e8 < n_star < 9e8
    # N = N* → τ_OR ≈ τ_dec (Definition)
    cfg_at = ORConfig(n_tubulins=n_star)
    assert penrose_tau_or_s(cfg_at) == pytest.approx(
        tegmark_tau_dec_s(cfg_at), rel=1e-6
    )
    assert n_gate_threshold(ORConfig(correlated=False)) == float("inf")


def test_hazard_semantics() -> None:
    """hazard = dt/τ_OR (geclippt ≤ 1) bei Gate ON, 0 bei OFF."""
    kernel = ORCollapseKernel(config=ORConfig(), dt_s=1e-4)
    expected = min(1e-4 / kernel.tau_or_s, 1.0)
    assert 0.6 < expected < 0.7
    assert kernel.hazard_per_step() == pytest.approx(expected)
    # dt ≫ τ_OR → geclippt auf 1
    big = ORCollapseKernel(config=ORConfig(), dt_s=1.0)
    assert big.hazard_per_step() == 1.0


def test_collective_kick_is_contiguous_cluster() -> None:
    """Ein Draw → genau cluster_size Voxel, zusammenhängend, Cluster-
    aligniert (das kollektive Muster)."""
    kernel = ORCollapseKernel(config=ORConfig(), cluster_size=16)
    rng = make_rng(17, 0, 0)
    fired = 0
    for _ in range(200):
        sites = kernel.step(rng, n_sites=4096)
        if sites:
            fired += 1
            assert len(sites) == 16
            assert sites == list(range(sites[0], sites[0] + 16))
            assert sites[0] % 16 == 0
            assert 0 <= sites[-1] < 4096
    # hazard ≈ 0.66 → über 200 Schritte ~132 Feuervorgänge
    assert 80 < fired < 180


def test_kernel_gate_off_never_fires() -> None:
    """Gate OFF (bulk-S) → step liefert über viele Draws nie ein Event."""
    kernel = ORCollapseKernel(config=ORConfig(shielding=1.0))
    rng = make_rng(19, 0, 0)
    for _ in range(2000):
        assert kernel.step(rng, n_sites=4096) == []


def test_or_kernel_syn3a_never_fires() -> None:
    """C3 (vorab registriert): syn3A hat kein Mikrotubuli-Kollektiv
    (N_eff = 1) und keine Shielding-Hypothese (S = 1) → Gate OFF,
    Kernel feuert nie."""
    check = syn3a_gate_check()
    assert check["gate_on"] is False
    assert check["hazard_per_step"] == 0.0
    assert check["ratio"] > 1e17

    kernel = ORCollapseKernel(config=ORConfig(n_tubulins=1.0, shielding=1.0))
    rng = make_rng(23, 0, 0)
    for _ in range(1000):
        assert kernel.step(rng, n_sites=512) == []


def test_too_few_sites_no_fire() -> None:
    """n_sites < cluster_size → kein Event (auch bei Gate ON)."""
    kernel = ORCollapseKernel(config=ORConfig(), cluster_size=16)
    rng = make_rng(29, 0, 0)
    for _ in range(200):
        assert kernel.step(rng, n_sites=8) == []


def test_kernel_deterministic_same_seed() -> None:
    def run() -> list[list[int]]:
        kernel = ORCollapseKernel(config=ORConfig())
        rng = make_rng(31, 0, 0)
        return [kernel.step(rng, 4096) for _ in range(100)]

    assert run() == run()


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        penrose_tau_or_s(ORConfig(n_tubulins=0.5))
    with pytest.raises(ValueError):
        tegmark_tau_dec_s(ORConfig(shielding=0.5))
    with pytest.raises(ValueError):
        ORCollapseKernel(cluster_size=0)
    with pytest.raises(ValueError):
        ORCollapseKernel(dt_s=0.0)
