"""Tests für Reaktions-Registry."""

from __future__ import annotations

from cellsim.modules.reactions import (
    default_registry,
    mass_action_conserves_atoms,
)


def test_default_registry_has_at_least_21_species() -> None:
    """Inkrement 3 erweitert die Registry; jetzt ≥21 Spezies + Reaktionen."""
    reg = default_registry()
    assert reg.n_species >= 21, f"Erwartet ≥21 Spezies, got {reg.n_species}"
    assert reg.n_reactions >= 6, f"Erwartet ≥6 Reaktionen, got {reg.n_reactions}"


def test_default_registry_reactions_reference_known_species() -> None:
    """Alle Reaktionen referenzieren nur Spezies aus der Registry."""
    reg = default_registry()
    known = set(reg.species_ids)
    for rxn in reg.reactions:
        for s_id in rxn.species_change.keys():
            assert s_id in known, f"Reaction {rxn.name} referenziert unbekannte Spezies {s_id}"


def test_default_registry_net_molecule_change_is_small() -> None:
    """Sanity-Check: keine Reaktion erzeugt/vernichtet mehr als 5 Moleküle netto.

    Biologische Reaktionen erhalten Atome, aber nicht unbedingt die Summe
    der Spezies-Counts. Wir prüfen nur auf numerisch plausible Bilanzen.
    """
    reg = default_registry()
    for rxn in reg.reactions:
        net = sum(rxn.species_change.values())
        assert abs(net) <= 5, (
            f"Reaction {rxn.name} hat unplausible Netto-Bilanz: {net}"
        )
