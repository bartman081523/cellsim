"""Tests für AlphaFold-Fallback-Stack (mocked)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cellsim.data.alphafold import PdbSource, fetch_pdb


def test_fetch_pdb_no_network_returns_stub(tmp_path: Path) -> None:
    fetch = fetch_pdb("P12345", out_dir=tmp_path, use_network=False)
    assert fetch.source == PdbSource.STUB
    assert fetch.version is None
    assert fetch.pdb_text is None


def test_fetch_pdb_rest_check_says_no_returns_stub(tmp_path: Path) -> None:
    with patch("cellsim.data.alphafold._rest_check", return_value=False):
        fetch = fetch_pdb("P99999", out_dir=tmp_path)
    assert fetch.source == PdbSource.STUB


def test_fetch_pdb_rest_skipped_when_disabled(tmp_path: Path) -> None:
    """Wenn allow_rest_check=False, wird direkt v6 probiert."""
    fake_pdb = (
        "HEADER    FAKE                                01-JAN-00   FAK\n"
        "ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 70.00           C\n"
        "END\n"
    )

    def fake_download(uniprot: str, version: int, out_dir: Path):  # type: ignore[no-untyped-def]
        target = out_dir / f"{uniprot}_v{version}.pdb"
        target.write_text(fake_pdb, encoding="utf-8")
        return target, fake_pdb

    with patch("cellsim.data.alphafold._download_pdb", side_effect=fake_download):
        fetch = fetch_pdb("P00001", out_dir=tmp_path, allow_rest_check=False)
    assert fetch.source == PdbSource.V6
    assert fetch.version == 6
    assert fetch.pdb_text is not None
    assert "ATOM" in fetch.pdb_text


def test_fetch_pdb_v6_fail_fallback_v4(tmp_path: Path) -> None:
    """Wenn v6 leer ist (HTTP 200 aber winziger Content), fällt auf v4 zurück."""
    fake_pdb = (
        "HEADER    FALLBACK                           01-JAN-00   FBK\n"
        "ATOM      1  CA  ALA A   1       1.000   2.000   3.000  1.00 75.00           C\n"
        "END\n"
    )

    call_log: list[int] = []

    def fake_download(uniprot: str, version: int, out_dir: Path):  # type: ignore[no-untyped-def]
        call_log.append(version)
        if version == 6:
            # simuliere "zu kleinen Inhalt"
            return None
        target = out_dir / f"{uniprot}_v{version}.pdb"
        target.write_text(fake_pdb, encoding="utf-8")
        return target, fake_pdb

    with patch("cellsim.data.alphafold._rest_check", return_value=True):
        with patch("cellsim.data.alphafold._download_pdb", side_effect=fake_download):
            fetch = fetch_pdb("PABCDE", out_dir=tmp_path)
    assert fetch.source == PdbSource.V4
    assert 6 in call_log and 4 in call_log


def test_fetch_pdb_all_fail_returns_stub(tmp_path: Path) -> None:
    with patch("cellsim.data.alphafold._rest_check", return_value=True):
        with patch("cellsim.data.alphafold._download_pdb", return_value=None):
            fetch = fetch_pdb("PXXXXX", out_dir=tmp_path)
    assert fetch.source == PdbSource.STUB


@pytest.mark.parametrize("version", [6, 4, 3])
def test_fetch_pdb_version_mapping(tmp_path: Path, version: int) -> None:
    fake_pdb = "HEADER    V\nATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 50.00           C\nEND\n"

    def fake_download(uniprot: str, v: int, out_dir: Path):  # type: ignore[no-untyped-def]
        if v != version:
            return None
        target = out_dir / f"{uniprot}_v{v}.pdb"
        target.write_text(fake_pdb, encoding="utf-8")
        return target, fake_pdb

    with patch("cellsim.data.alphafold._rest_check", return_value=True):
        with patch("cellsim.data.alphafold._download_pdb", side_effect=fake_download):
            fetch = fetch_pdb("PVER", out_dir=tmp_path)
    assert fetch.version == version
