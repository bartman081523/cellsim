"""Tests für PDB → RDME-Volumen-Berechnung."""

from __future__ import annotations

import math

from cellsim.data.volumes import (
    _RG_TO_RS_FACTOR,
    stub_volume_params,
    volume_params_from_pdb_text,
)


def test_volume_params_from_minimal_pdb(sample_pdb_text: str) -> None:
    vp = volume_params_from_pdb_text(sample_pdb_text, "TEST", "v6")
    assert vp.uniprot_id == "TEST"
    assert vp.n_ca_atoms == 3
    assert vp.source == "v6"
    assert vp.rg_angstrom > 0.0
    assert vp.rs_angstrom == _RG_TO_RS_FACTOR * vp.rg_angstrom
    expected_v_ex = (4.0 / 3.0) * math.pi * vp.rs_angstrom**3
    assert abs(vp.v_ex_angstrom3 - expected_v_ex) < 1e-6
    # pLDDT = Mittel von 70, 80, 90 = 80.0
    assert abs(vp.plddt_mean - 80.0) < 1e-9


def test_volume_params_plddt_mean_in_range(sample_pdb_text: str) -> None:
    vp = volume_params_from_pdb_text(sample_pdb_text, "X", "v4")
    assert 0.0 <= vp.plddt_mean <= 100.0


def test_stub_volume_params_reasonable() -> None:
    vp = stub_volume_params("STUB", length=200)
    # Rg ~ 2.5 * sqrt(200) ≈ 35.4 Å
    assert 30.0 < vp.rg_angstrom < 45.0
    assert vp.rs_angstrom > 0.0
    assert vp.v_ex_angstrom3 > 0.0
    assert vp.source == "stub"


def test_stub_handles_zero_length() -> None:
    vp = stub_volume_params("STUB", length=0)
    assert vp.rg_angstrom > 0.0
