"""Integration: cellsim cache build mit gemocktem Netzwerk."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cellsim.data.uniprot import ProteinEntry

SAMPLE_TSV = (
    "accession\tid\tgene_names\tprotein_name\tlength\n"
    "C7MID5\tDNAA\tdnaA\tChromosomal replication initiator\t455\n"
    "C7LLN1\tDBH\tdnaN\tDNA polymerase III beta\t373\n"
    "Q6MT75\tLDH\tldh\tL-lactate dehydrogenase\t313\n"
)


def _fake_pdb(uniprot: str) -> str:
    """Tiny PDB mit 4 CA-Atomen für Smoke-Test."""
    return (
        f"HEADER    {uniprot:<40s}  01-JAN-00   SYN\n"
        f"ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 80.00           C\n"
        f"ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00 85.00           C\n"
        f"ATOM      3  CA  ALA A   3       7.600   0.000   0.000  1.00 75.00           C\n"
        f"ATOM      4  CA  ALA A   4      11.400   0.000   0.000  1.00 90.00           C\n"
        "END\n"
    )


@pytest.mark.integration
def test_cache_build_end_to_end(tmp_path: Path) -> None:
    """Lädt Proteom (gemockt), AlphaFold (gemockt), schreibt volumes.tsv."""
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # Proteom aus Cache laden — Pfad-Konvention: $XDG_CACHE_HOME/cellsim/proteome.tsv
    # conftest setzt XDG_CACHE_HOME auf tmp_path/cache
    cache_root = tmp_path / "cache" / "cellsim"
    cache_root.mkdir(parents=True, exist_ok=True)
    (cache_root / "proteome.tsv").write_text(SAMPLE_TSV, encoding="utf-8")

    # PDB-Fetch mocken
    def fake_fetch(uniprot, out_dir=None, use_network=True, **kw):  # type: ignore[no-untyped-def]
        from cellsim.data.alphafold import FetchResult, PdbSource

        return FetchResult(
            accession=uniprot,
            version=6,
            path=Path("/fake"),
            source=PdbSource.V6,
            pdb_text=_fake_pdb(uniprot),
        )

    with patch("cellsim.cli.cache.fetch_pdb", side_effect=fake_fetch):
        from cellsim.cli.cache import build_volumes_table

        tsv_path = build_volumes_table(out_dir=out_dir, use_network=False)

    assert tsv_path.exists()
    content = tsv_path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    assert len(lines) == 1 + 3  # Header + 3 Einträge
    assert "uniprot_id" in lines[0]
    assert "C7MID5" in content
    assert "Q6MT75" in content
    # Alle aus v6 (mock)
    assert content.count("v6") == 3


@pytest.mark.integration
def test_cache_inspect_after_build(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    cache_root = tmp_path / "cache" / "cellsim"
    cache_root.mkdir(parents=True, exist_ok=True)
    (cache_root / "proteome.tsv").write_text(SAMPLE_TSV, encoding="utf-8")

    def fake_fetch(uniprot, out_dir=None, use_network=True, **kw):  # type: ignore[no-untyped-def]
        from cellsim.data.alphafold import FetchResult, PdbSource

        return FetchResult(
            accession=uniprot,
            version=4,
            path=Path("/fake"),
            source=PdbSource.V4,
            pdb_text=_fake_pdb(uniprot),
        )

    with patch("cellsim.cli.cache.fetch_pdb", side_effect=fake_fetch):
        from cellsim.cli.cache import build_volumes_table, inspect_cache

        build_volumes_table(out_dir=out_dir, use_network=False)
        info = inspect_cache(out_dir)

    assert info["n_entries"] == 3
    assert info["source_counts"] == {"v4": 3}
    assert info["rs_mean"] > 0.0
    assert info["v_ex_total"] > 0.0
