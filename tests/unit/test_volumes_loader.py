"""Tests für volumes.tsv-Loader."""

from __future__ import annotations

from pathlib import Path

from cellsim.data.volumes_loader import aggregate_volumes_by_species, load_volumes_tsv


SAMPLE_TSV = (
    "uniprot_id\tRg_A\tRs_A\tV_ex_A3\tpLDDT_mean\n"
    "C7MID5\t18.5\t15.5\t1.5e4\t82.0\n"
    "C7LLN1\t16.0\t13.4\t1.0e4\t78.0\n"
    "Q6MT75\t14.0\t11.8\t6.9e3\t91.0\n"
)


def test_load_volumes_tsv_returns_dict(tmp_path: Path) -> None:
    tsv = tmp_path / "volumes.tsv"
    tsv.write_text(SAMPLE_TSV, encoding="utf-8")
    data = load_volumes_tsv(tsv)
    assert len(data) == 3
    assert data["C7MID5"]["Rs_A"] == 15.5
    assert data["Q6MT75"]["V_ex_A3"] == 6.9e3


def test_load_volumes_tsv_missing_file(tmp_path: Path) -> None:
    data = load_volumes_tsv(tmp_path / "nonexistent.tsv")
    assert data == {}


def test_aggregate_volumes_by_species_uses_fallback() -> None:
    volumes = {
        "C7MID5": {"Rg_A": 18.5, "Rs_A": 15.5, "V_ex_A3": 1.5e4, "pLDDT_mean": 82.0},
    }
    species = ("ATP", "Glucose", "C7MID5")
    out = aggregate_volumes_by_species(volumes, species)
    assert out["C7MID5"] == 1.5e4
    assert out["ATP"] >= 1500.0    # Fallback
    assert out["Glucose"] >= 1500.0  # Fallback
