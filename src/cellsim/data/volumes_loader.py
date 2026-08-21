"""Lädt volumes.tsv in ein Dict für Crowding-Module."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_volumes_tsv(path: Path) -> dict[str, dict[str, float]]:
    """Liest volumes.tsv und gibt Mapping {uniprot_id: {Rg, Rs, V_ex, …}} zurück."""
    if not path.exists():
        logger.warning("volumes.tsv nicht gefunden: %s — leeres Mapping", path)
        return {}
    out: dict[str, dict[str, float]] = {}
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            uniprot = row.get("uniprot_id", "").strip()
            if not uniprot:
                continue
            try:
                out[uniprot] = {
                    "Rg_A": float(row["Rg_A"]),
                    "Rs_A": float(row["Rs_A"]),
                    "V_ex_A3": float(row["V_ex_A3"]),
                    "pLDDT_mean": float(row["pLDDT_mean"]),
                }
            except (KeyError, ValueError) as exc:
                logger.debug("Skip %s: %s", uniprot, exc)
    logger.info("Loaded %d volume entries from %s", len(out), path)
    return out


def aggregate_volumes_by_species(
    volumes: dict[str, dict[str, float]],
    species_ids: tuple[str, ...],
) -> dict[str, float]:
    """Aggregiert Volumina: mittleres V_ex pro Spezies (Fallback bei fehlenden Einträgen).

    Wenn keine PDB-Daten für eine Spezies vorliegen, wird ein Stub-Volumen
    basierend auf typischer Proteingröße verwendet.
    """
    out: dict[str, float] = {}
    fallback_v_angstrom3 = 1500.0   # ~10 kDa globuläres Protein
    for s_id in species_ids:
        # Direkter Match
        if s_id in volumes:
            out[s_id] = volumes[s_id]["V_ex_A3"]
            continue
        # Mittelwert über alle vorhandenen Einträge
        if volumes:
            mean_v = sum(v["V_ex_A3"] for v in volumes.values()) / len(volumes)
            out[s_id] = max(mean_v, fallback_v_angstrom3)
        else:
            out[s_id] = fallback_v_angstrom3
    logger.info("Aggregated %d species volumes (fallback for missing entries)", len(out))
    return out
