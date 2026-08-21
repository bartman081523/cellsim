"""BRENDA/SABIO-RK Loader für kinetische Konstanten.

Liest `configs/brenda_kinetics.yaml` und liefert ein Mapping
{reaction_name: k} für die Reaktionen in `modules/reactions.py`.

Hinweis: Diese Konstanten sind aus BRENDA extrahiert für die
nächstverwandten Spezies (meist E. coli). Sie sind NICHT
spezifisch für JCVI-syn3A kalibriert. HYPOTHESE-Status: niedrig.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import yaml

logger = logging.getLogger(__name__)

DEFAULT_BRENDA_YAML: Final[Path] = (
    Path(__file__).resolve().parents[3] / "configs" / "brenda_kinetics.yaml"
)


def load_brenda_kinetics(path: Path | None = None) -> dict[str, float]:
    """Lädt BRENDA-Konstanten und gibt Mapping reaction_name → k zurück."""
    target = path or DEFAULT_BRENDA_YAML
    if not target.exists():
        logger.warning("BRENDA YAML nicht gefunden: %s", target)
        return {}
    with target.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out: dict[str, float] = {}
    for reaction_name, params in data.items():
        if isinstance(params, dict) and "k" in params:
            out[reaction_name] = float(params["k"])
    logger.info("Loaded %d BRENDA reaction constants from %s", len(out), target)
    return out


def load_brenda_with_status(path: Path | None = None) -> dict[str, dict[str, object]]:
    """Lädt BRENDA-Konstanten MIT Status (BRENDA/LITERATURE/HYPOTHESE).

    Rückgabe: {reaction_name: {"k": float, "status": str, "organism": str}}.
    """
    target = path or DEFAULT_BRENDA_YAML
    if not target.exists():
        return {}
    with target.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out: dict[str, dict[str, object]] = {}
    for reaction_name, params in data.items():
        if isinstance(params, dict) and "k" in params:
            out[reaction_name] = {
                "k": float(params["k"]),
                "status": str(params.get("status", "HYPOTHESE")),
                "organism": str(params.get("organism", "Escherichia coli")),
                "kcat_per_s": float(params["kcat_per_s"]) if params.get("kcat_per_s") else None,
                "Km_mM": float(params.get("Km_atp_mM", 0.0)) or float(params.get("Km_glucose_mM", 0.0)),
            }
    return out


def apply_brenda_overrides(
    registry,
    brenda_k: dict[str, float],
) -> None:
    """Überschreibt die k-Werte einer ReactionRegistry.

    Mapping ist 1:1 (BRENDA-YAML-Keys = Registry-Keys).
    """
    from cellsim.modules.reactions import Reaction

    new_reactions = []
    for rxn in registry.reactions:
        if rxn.name in brenda_k:
            new_k = brenda_k[rxn.name]
            rxn = Reaction(
                name=rxn.name,
                species_change=rxn.species_change,
                k=new_k,
                source="BRENDA",
            )
            logger.info("Override %s: k=%.3e (BRENDA)", rxn.name, new_k)
        new_reactions.append(rxn)
    return type(registry)(
        species_ids=registry.species_ids,
        reactions=tuple(new_reactions),
    )
