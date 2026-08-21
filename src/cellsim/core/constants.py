"""Zentrale Konstanten für cellsim.

Single source of truth — keine Duplikation in Adaptern/Modulen.
JCVI-syn3A-spezifische Zahlen aus Luthey-Schulten-Lab 4DWCM-Publikationen.
"""

from __future__ import annotations

from typing import Final

# --- Physikalische Konstanten ---
AVOGADRO: Final[float] = 6.022_140_76e23  # 1/mol
BOLTZMANN: Final[float] = 1.380_649e-23    # J/K

# --- JCVI-syn3A Organismus-Parameter ---
JCVI_GENOME_BP: Final[int] = 543_434
JCVI_PROTEIN_COUNT: Final[int] = 455
JCVI_RRNA_COUNT: Final[int] = 6
JCVI_TRNA_COUNT: Final[int] = 29
JCVI_PROTEOME: Final[str] = "UP000326712"

# --- Zellgeometrie (default) ---
JCVI_CELL_RADIUS_NM_INITIAL: Final[float] = 200.0   # sphärisch
JCVI_CELL_RADIUS_NM_MATURE: Final[float] = 400.0
JCVI_CELL_CYCLE_S: Final[float] = 105.0 * 60.0       # 105 min aus 4DWCM §5.1

# --- RDME-Defaults ---
RDME_VOXEL_NM_DEFAULT: Final[float] = 10.0
RDME_DT_S_DEFAULT: Final[float] = 1.0e-3              # 1 ms

# --- ODE-Defaults ---
ODE_DT_S_DEFAULT: Final[float] = 1.0e-1               # 100 ms

# --- Treiber-Loop ---
DRIVER_SYNC_INTERVAL_DEFAULT: Final[int] = 100         # alle 100 RDME-Schritte ODE-Sync

# --- Reproduzierbarkeit ---
SEED_BASE: Final[int] = 0xC1CE

# --- AlphaFold-URL-Schema ---
ALPHAFOLD_URL_TEMPLATE: Final[str] = (
    "https://alphafold.ebi.ac.uk/files/AF-{uniprot}-F1-model_v{version}.pdb"
)
ALPHAFOLD_REST_URL_TEMPLATE: Final[str] = (
    "https://www.alphafold.ebi.ac.uk/api/prediction/{uniprot}"
)
ALPHAFOLD_VERSIONS: Final[tuple[int, ...]] = (6, 4, 3)  # Fallback-Reihenfolge

# --- UniProt-Proteom-Liste ---
UNIPROT_PROTEOME_URL_TEMPLATE: Final[str] = (
    "https://rest.uniprot.org/uniprotkb/search"
    "?query=proteome:{proteome}&format=tsv"
    "&fields=accession,id,gene_names,protein_name,length"
)

# --- Rosen-Horizont (CLAUDE.md §Epistemische Leitlinien) ---
ROSEN_HORIZON: Final[str] = (
    "L3-Kern ist reduktionistisch (AnA). Vollständige Zellsimulation "
    "erfordert L1/MES-Architektur. Siehe Architekturtext §2.1."
)

# --- L3-Läuft-Metrik-Schwellen ---
L3_MASS_CONSERVATION_TOL: Final[float] = 0.05          # ±5 %
L3_CROWDING_STD_MIN: Final[float] = 1.0e-6             # std > 0
