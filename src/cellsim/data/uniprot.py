"""UniProt-Proteom-Loader für JCVI-syn3A.

Download der TSV-Liste (UP000326712) mit Caching unter
$XDG_CACHE_HOME/cellsim/proteome.tsv.
"""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import requests

from cellsim.core.constants import (
    JCVI_PROTEOME,
    UNIPROT_PROTEOME_URL_TEMPLATE,
)
from cellsim.data.cache import proteome_path

logger = logging.getLogger(__name__)

UNIPROT_FIELDS: Final[tuple[str, ...]] = (
    "accession",
    "id",
    "gene_names",
    "protein_name",
    "length",
)
UNIPROT_TIMEOUT_S: Final[float] = 30.0


@dataclass(frozen=True)
class ProteinEntry:
    """Ein Protein-Eintrag aus dem JCVI-syn3A-Proteom."""

    accession: str       # UniProt-ID (z.B. "C7MID5")
    entry_id: str        # z.B. "DnaA_MYCMS"
    gene_names: str      # z.B. "dnaA"
    protein_name: str    # z.B. "Chromosomal replication initiator protein DnaA"
    length: int          # Anzahl AS

    @property
    def short_label(self) -> str:
        """Kurzes Label für Logs (accession | gene_names)."""
        return f"{self.accession}|{self.gene_names}"


def fetch_proteome_tsv(
    proteome: str = JCVI_PROTEOME,
    timeout_s: float = UNIPROT_TIMEOUT_S,
) -> str:
    """Holt die Proteom-TSV frisch von UniProt."""
    url = UNIPROT_PROTEOME_URL_TEMPLATE.format(proteome=proteome)
    logger.info("Fetching proteome TSV from UniProt: %s", url)
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    return response.text


def download_proteome(
    out_path: Path | None = None,
    proteome: str = JCVI_PROTEOME,
    force: bool = False,
) -> Path:
    """Lädt Proteom-TSV herunter und cached sie lokal.

    Bei force=True wird der Cache überschrieben. Gibt den Cache-Pfad zurück.
    """
    target = out_path or proteome_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        logger.info("Using cached proteome: %s", target)
        return target
    text = fetch_proteome_tsv(proteome=proteome)
    target.write_text(text, encoding="utf-8")
    logger.info("Wrote proteome TSV: %s (%d bytes)", target, len(text))
    return target


def parse_proteome_tsv(text: str) -> list[ProteinEntry]:
    """Parst eine UniProt-Proteom-TSV in ProteinEntry-Liste."""
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    missing = set(UNIPROT_FIELDS) - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"UniProt TSV missing required fields: {sorted(missing)}")

    entries: list[ProteinEntry] = []
    for row in reader:
        # UniProt TSVs können mehrzeilige protein_name-Felder haben;
        # csv-Reader fasst sie als eine logische Zeile auf.
        accession = (row.get("accession") or "").strip()
        if not accession:
            continue
        entry_id = (row.get("id") or "").strip()
        gene_names = (row.get("gene_names") or "").strip()
        protein_name = (row.get("protein_name") or "").strip()
        length_raw = (row.get("length") or "0").strip()
        try:
            length = int(length_raw)
        except ValueError:
            length = 0
        entries.append(
            ProteinEntry(
                accession=accession,
                entry_id=entry_id,
                gene_names=gene_names,
                protein_name=protein_name,
                length=length,
            )
        )
    return entries


def load_proteome(
    cache_path: Path | None = None,
    proteome: str = JCVI_PROTEOME,
    use_network: bool = True,
) -> list[ProteinEntry]:
    """Lädt Proteom: zuerst Cache, dann (optional) Netzwerk."""
    target = cache_path or proteome_path()
    if not target.exists() and use_network:
        target = download_proteome(target, proteome=proteome)
    if not target.exists():
        raise FileNotFoundError(
            f"Proteom cache missing and use_network=False: {target}"
        )
    text = target.read_text(encoding="utf-8")
    return parse_proteome_tsv(text)
