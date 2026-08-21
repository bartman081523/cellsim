"""AlphaFold-Loader mit Fallback-Stack v6→v4→v3→Stub."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

import requests

from cellsim.core.constants import (
    ALPHAFOLD_REST_URL_TEMPLATE,
    ALPHAFOLD_URL_TEMPLATE,
    ALPHAFOLD_VERSIONS,
)
from cellsim.data.cache import pdb_dir

logger = logging.getLogger(__name__)

ALPHAFOLD_TIMEOUT_S: Final[float] = 20.0
PDB_HEADER_MIN_SIZE: Final[int] = 200  # Realistische PDB > 200 Bytes


class PdbSource(str, Enum):
    """Quelle einer PDB-Datei."""

    V6 = "v6"
    V4 = "v4"
    V3 = "v3"
    STUB = "stub"


@dataclass(frozen=True)
class FetchResult:
    """Ergebnis eines PDB-Fetch-Versuchs."""

    accession: str
    version: int | None  # None für Stub
    path: Path
    source: PdbSource
    pdb_text: str | None  # None für Stub (kein PDB generiert)


def _rest_check(uniprot: str, timeout_s: float = ALPHAFOLD_TIMEOUT_S) -> bool:
    """True, wenn AlphaFold für uniprot eine Vorhersage hat."""
    url = ALPHAFOLD_REST_URL_TEMPLATE.format(uniprot=uniprot)
    try:
        r = requests.get(url, timeout=timeout_s)
    except requests.RequestException as exc:
        logger.debug("REST check failed for %s: %s", uniprot, exc)
        return False
    if r.status_code != 200:
        return False
    try:
        payload = r.json()
    except ValueError:
        return False
    return bool(payload) and "pdbUrl" in payload


def _download_pdb(
    uniprot: str,
    version: int,
    out_dir: Path,
    timeout_s: float = ALPHAFOLD_TIMEOUT_S,
) -> tuple[Path, str] | None:
    """Lädt eine PDB-Datei herunter; gibt (Pfad, Inhalt) oder None zurück."""
    url = ALPHAFOLD_URL_TEMPLATE.format(uniprot=uniprot, version=version)
    target = out_dir / f"{uniprot}_v{version}.pdb"
    try:
        r = requests.get(url, timeout=timeout_s)
    except requests.RequestException as exc:
        logger.debug("Download failed %s v%d: %s", uniprot, version, exc)
        return None
    if r.status_code != 200:
        return None
    if len(r.content) < PDB_HEADER_MIN_SIZE:
        logger.debug("Downloaded content too small: %s v%d", uniprot, version)
        return None
    target.write_bytes(r.content)
    return target, r.text


def fetch_pdb(
    uniprot: str,
    out_dir: Path | None = None,
    use_network: bool = True,
    allow_rest_check: bool = True,
) -> FetchResult:
    """Holt eine PDB-Datei mit Fallback-Stack.

    Reihenfolge: v6 → v4 → v3 → Stub.
    Bei use_network=False wird sofort Stub zurückgegeben.
    Bei allow_rest_check=False wird der REST-Check übersprungen (z.B. in
    Tests mit deterministischer Vers-Reihenfolge).
    """
    target_dir = out_dir or pdb_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    if not use_network:
        return FetchResult(
            accession=uniprot,
            version=None,
            path=target_dir / f"{uniprot}_stub.pdb",
            source=PdbSource.STUB,
            pdb_text=None,
        )

    if allow_rest_check and not _rest_check(uniprot):
        logger.debug("REST check says no prediction: %s", uniprot)
        return FetchResult(
            accession=uniprot,
            version=None,
            path=target_dir / f"{uniprot}_stub.pdb",
            source=PdbSource.STUB,
            pdb_text=None,
        )

    for version in ALPHAFOLD_VERSIONS:
        result = _download_pdb(uniprot, version, target_dir)
        if result is not None:
            path, text = result
            logger.info("Fetched %s v%d (%d bytes)", uniprot, version, len(text))
            return FetchResult(
                accession=uniprot,
                version=version,
                path=path,
                source=PdbSource(f"v{version}"),
                pdb_text=text,
            )

    logger.debug("All versions failed for %s, falling back to stub", uniprot)
    return FetchResult(
        accession=uniprot,
        version=None,
        path=target_dir / f"{uniprot}_stub.pdb",
        source=PdbSource.STUB,
        pdb_text=None,
    )
