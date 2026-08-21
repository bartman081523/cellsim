"""PDB → RDME-Volumen-Parameter (Rg, Rs, V_ex, pLDDT_mean)."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VolumeParams:
    """Aggregierte Volumen-Parameter eines Proteins für RDME."""

    uniprot_id: str
    rg_angstrom: float
    rs_angstrom: float           # Stokes-Radius (globular approximation)
    v_ex_angstrom3: float        # Excluded Volume in Å³
    plddt_mean: float            # 0-100
    n_ca_atoms: int              # Anzahl ausgewerteter CA-Atome
    source: str                  # "v6"|"v4"|"v3"|"stub"

    @property
    def rs_nm(self) -> float:
        return self.rs_angstrom * 0.1

    @property
    def v_ex_nm3(self) -> float:
        return self.v_ex_angstrom3 * 1e-3


# Globular protein: Rs ≈ 0.84 * Rg  (Tcherkala & Svergun 2021, übliche Näherung)
_RG_TO_RS_FACTOR: float = 0.84

# Fallback-Stub: mittlere AS-Volumen ≈ 150 Å³
_STUB_V_PER_A: float = 150.0
_STUB_RG_PER_ASQRT: float = 2.5   # Rg ≈ 2.5 * sqrt(N) in Å (random coil Grenze)
_STUB_RS_FACTOR: float = 0.6      # kompaktere Form


def _parse_plddt_from_pdb_text(pdb_text: str) -> tuple[np.ndarray, np.ndarray]:
    """Extrahiert (coords, bfactors) für CA-Atome aus PDB-Text.

    B-Factor (Spalte 61-66) trägt im AlphaFold-Output pLDDT (0-100).
    """
    coords: list[tuple[float, float, float]] = []
    bfactors: list[float] = []
    for line in pdb_text.splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        atom_name = line[12:16].strip()
        if atom_name != "CA":
            continue
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            b = float(line[60:66])
        except ValueError:
            continue
        coords.append((x, y, z))
        bfactors.append(b)
    if not coords:
        return np.empty((0, 3)), np.empty(0)
    return np.asarray(coords, dtype=np.float64), np.asarray(bfactors, dtype=np.float64)


def _params_from_ca(
    uniprot_id: str,
    coords: np.ndarray,
    bfactors: np.ndarray,
    source: str,
) -> VolumeParams:
    """Berechnet (Rg, Rs, V_ex, pLDDT) aus CA-Koordinaten."""
    com = coords.mean(axis=0)
    sq = ((coords - com) ** 2).sum(axis=1)
    rg = float(math.sqrt(sq.mean()))
    rs = _RG_TO_RS_FACTOR * rg
    v_ex = (4.0 / 3.0) * math.pi * rs**3
    plddt = float(bfactors.mean()) if bfactors.size else 0.0
    return VolumeParams(
        uniprot_id=uniprot_id,
        rg_angstrom=rg,
        rs_angstrom=rs,
        v_ex_angstrom3=v_ex,
        plddt_mean=plddt,
        n_ca_atoms=int(coords.shape[0]),
        source=source,
    )


def stub_volume_params(uniprot_id: str, length: int, source: str = "stub") -> VolumeParams:
    """Stub-Parameter aus Sequenzlänge (Fallback ohne PDB)."""
    if length <= 0:
        length = 100
    rg = _STUB_RG_PER_ASQRT * math.sqrt(length)
    rs = _STUB_RS_FACTOR * rg
    v_ex = (4.0 / 3.0) * math.pi * rs**3
    # pLDDT-Stub: typische mittlere Confidence ~70
    plddt = 70.0
    return VolumeParams(
        uniprot_id=uniprot_id,
        rg_angstrom=rg,
        rs_angstrom=rs,
        v_ex_angstrom3=v_ex,
        plddt_mean=plddt,
        n_ca_atoms=length,
        source=source,
    )


def volume_params_from_pdb_file(
    pdb_path: Path,
    uniprot_id: str | None = None,
) -> VolumeParams:
    """Liest eine PDB-Datei und gibt VolumeParams zurück."""
    from Bio.PDB import PDBParser  # type: ignore[import-not-found]
    from Bio.PDB.PDBIO import PDBIO  # noqa: F401  # trigger biopython import

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("x", str(pdb_path))
    ca_atoms = [a for a in structure.get_atoms() if a.get_name() == "CA"]
    if not ca_atoms:
        # Fallback: leere PDB → leeres Params
        return VolumeParams(
            uniprot_id=uniprot_id or pdb_path.stem,
            rg_angstrom=0.0,
            rs_angstrom=0.0,
            v_ex_angstrom3=0.0,
            plddt_mean=0.0,
            n_ca_atoms=0,
            source="empty",
        )
    coords = np.asarray([a.get_coord() for a in ca_atoms], dtype=np.float64)
    # Biopython B-Factor pro Atom (float)
    bfactors = np.asarray(
        [getattr(a, "get_bfactor", lambda: 0.0)() for a in ca_atoms],
        dtype=np.float64,
    )
    return _params_from_ca(
        uniprot_id or pdb_path.stem, coords, bfactors, source="biopython"
    )


def volume_params_from_pdb_text(
    pdb_text: str,
    uniprot_id: str,
    source: str,
) -> VolumeParams:
    """Parst PDB-Text direkt (ohne Biopython, für Smoke/Stub-Pfade)."""
    coords, bfactors = _parse_plddt_from_pdb_text(pdb_text)
    if coords.shape[0] == 0:
        return VolumeParams(
            uniprot_id=uniprot_id,
            rg_angstrom=0.0,
            rs_angstrom=0.0,
            v_ex_angstrom3=0.0,
            plddt_mean=0.0,
            n_ca_atoms=0,
            source=source + "_empty",
        )
    return _params_from_ca(uniprot_id, coords, bfactors, source=source)
