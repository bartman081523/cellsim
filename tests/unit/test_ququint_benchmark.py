"""Tests für QuQuint-V-Ladder-Benchmark."""

from __future__ import annotations

from cellsim.benchmarks.ququint_vs_qubit import (
    QuDitSpec,
    benchmark_conformation_range,
    benchmark_single,
    n_qudits_for_conformations,
    n_two_qudit_gates_v_ladder,
)


def test_n_qudits_qubit_for_8_conformations() -> None:
    """3 Qubits kodieren 2³=8 Konformationen."""
    assert n_qudits_for_conformations(8, d=2) == 3


def test_n_qudits_qutrit_for_27_conformations() -> None:
    """3 Qutrits kodieren 3³=27 Konformationen."""
    assert n_qudits_for_conformations(27, d=3) == 3


def test_n_qudits_ququint_for_125_conformations() -> None:
    """3 QuQuints kodieren 5³=125 Konformationen."""
    assert n_qudits_for_conformations(125, d=5) == 3


def test_v_ladder_reduces_for_ququint() -> None:
    """V-Ladder reduziert Gatter-Anzahl für QuQuints vs. naive QuQuints."""
    n_5 = n_qudits_for_conformations(1000, d=5)
    naive = n_5 * n_5
    v_ladder_5 = n_two_qudit_gates_v_ladder(n_5, d=5)
    # QuQuint-V-Ladder nutzt Ancilla |4⟩, daher weniger als naive
    assert v_ladder_5 < naive


def test_v_ladder_equals_naive_for_qubit() -> None:
    """Qubits haben kein Ancilla-Niveau, daher kein V-Ladder-Vorteil."""
    n_q = n_qudits_for_conformations(1000, d=2)
    naive = n_q * n_q
    v_ladder = n_two_qudit_gates_v_ladder(n_q, d=2)
    assert v_ladder == naive


def test_benchmark_single_returns_expected_fields() -> None:
    spec = QuDitSpec(name="ququint", dimension=5)
    r = benchmark_single(spec, n_conformations=1000)
    assert r.system == "ququint"
    assert r.dimension == 5
    assert r.n_qudits >= 1
    assert r.reduction_factor > 0.0


def test_benchmark_range_covers_three_systems() -> None:
    results = benchmark_conformation_range()
    systems = set(r.system for r in results)
    assert systems == {"qubit", "qutrit", "ququint"}
