"""Cache-Operationen (build, inspect)."""

from __future__ import annotations

import csv
import logging
from collections import Counter
from pathlib import Path

from cellsim.data.alphafold import fetch_pdb
from cellsim.data.cache import ensure_cache_dirs, proteome_path, volumes_csv_path
from cellsim.data.uniprot import (
    ProteinEntry,
    download_proteome,
    load_proteome,
)
from cellsim.data.volumes import (
    VolumeParams,
    stub_volume_params,
    volume_params_from_pdb_text,
)

logger = logging.getLogger(__name__)

VOLUMES_HEADER: tuple[str, ...] = (
    "uniprot_id",
    "entry_id",
    "gene_names",
    "length",
    "Rg_A",
    "Rs_A",
    "V_ex_A3",
    "pLDDT_mean",
    "n_ca_atoms",
    "source",
)


def _volumes_row(entry: ProteinEntry, vp: VolumeParams) -> dict[str, str]:
    return {
        "uniprot_id": vp.uniprot_id,
        "entry_id": entry.entry_id,
        "gene_names": entry.gene_names,
        "length": str(entry.length),
        "Rg_A": f"{vp.rg_angstrom:.3f}",
        "Rs_A": f"{vp.rs_angstrom:.3f}",
        "V_ex_A3": f"{vp.v_ex_angstrom3:.3e}",
        "pLDDT_mean": f"{vp.plddt_mean:.2f}",
        "n_ca_atoms": str(vp.n_ca_atoms),
        "source": vp.source,
    }


def build_volumes_table(
    out_dir: Path,
    proteome: str = "UP000326712",
    force: bool = False,
    use_network: bool = True,
) -> Path:
    """Lädt Proteom + AlphaFold-PDBs, schreibt volumes.tsv nach out_dir.

    use_network steuert beides: Proteom-Download UND PDB-Download.
    Bei use_network=False wird nur der vorhandene Cache benutzt; fehlt
    das Proteom, wird eine klare Fehlermeldung geworfen.
    """
    cache_root = ensure_cache_dirs()
    ppath = proteome_path(cache_root)
    if not ppath.exists():
        if not use_network:
            raise RuntimeError(
                f"Proteom-Cache fehlt ({ppath}); zuerst mit use_network=True laufen."
            )
        download_proteome(out_path=ppath, proteome=proteome, force=force)

    entries = load_proteome(cache_path=ppath, use_network=False)
    logger.info("Loaded %d proteome entries", len(entries))

    target = volumes_csv_path(out_dir)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=VOLUMES_HEADER, delimiter="\t")
        writer.writeheader()
        for entry in entries:
            vp = _volumes_for_entry(entry, use_network=use_network)
            writer.writerow(_volumes_row(entry, vp))

    logger.info("Wrote %d rows → %s", len(entries), target)
    return target


def _volumes_for_entry(entry: ProteinEntry, use_network: bool) -> VolumeParams:
    """Holt PDB oder fällt auf Stub zurück."""
    fetch = fetch_pdb(entry.accession, use_network=use_network)
    if fetch.source.value == "stub":
        return stub_volume_params(entry.accession, entry.length, source="stub")
    assert fetch.pdb_text is not None
    vp = volume_params_from_pdb_text(
        fetch.pdb_text, uniprot_id=entry.accession, source=fetch.source.value
    )
    if vp.n_ca_atoms == 0:
        return stub_volume_params(entry.accession, entry.length, source="stub_empty")
    return vp


def inspect_cache(out_dir: Path) -> dict[str, object]:
    """Inspektion der volumes.tsv."""
    target = volumes_csv_path(out_dir)
    n = 0
    sources: Counter[str] = Counter()
    rs_sum = 0.0
    v_ex_sum = 0.0
    with target.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            n += 1
            sources[row["source"]] += 1
            rs_sum += float(row["Rs_A"])
            v_ex_sum += float(row["V_ex_A3"])
    return {
        "n_entries": n,
        "source_counts": dict(sources),
        "rs_mean": rs_sum / n if n else 0.0,
        "v_ex_total": v_ex_sum,
    }
