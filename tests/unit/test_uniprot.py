"""Tests für Proteom-TSV-Parser (keine Netzwerk-Aufrufe)."""

from __future__ import annotations

from cellsim.data.uniprot import parse_proteome_tsv


SAMPLE_TSV = (
    "accession\tid\tgene_names\tprotein_name\tlength\n"
    "C7MID5\tDNAA_MYCMS\tdnaA\tChromosomal replication initiator\t455\n"
    "C7LLN1\tDBH_MYCMS\tdnaN\tDNA polymerase III subunit beta\t373\n"
    "Q6MT75\tLDH_MYCMS\tldh\tL-lactate dehydrogenase\t313\n"
)


def test_parse_proteome_tsv_basic() -> None:
    entries = parse_proteome_tsv(SAMPLE_TSV)
    assert len(entries) == 3
    assert entries[0].accession == "C7MID5"
    assert entries[0].length == 455
    assert entries[0].gene_names == "dnaA"
    assert "Chromosomal" in entries[0].protein_name


def test_parse_proteome_tsv_missing_field() -> None:
    bad = "accession\tid\nC7MID5\tDNAA\n"
    import pytest

    with pytest.raises(ValueError, match="missing required fields"):
        parse_proteome_tsv(bad)


def test_parse_proteome_tsv_skips_blank_accession() -> None:
    text = SAMPLE_TSV + "\t\t\t\t0\n"  # leerer accession
    entries = parse_proteome_tsv(text)
    assert len(entries) == 3


def test_parse_proteome_tsv_handles_bad_length() -> None:
    text = (
        "accession\tid\tgene_names\tprotein_name\tlength\n"
        "C7MID5\tDNAA\tdnaA\tX\tabc\n"
    )
    entries = parse_proteome_tsv(text)
    assert entries[0].length == 0
