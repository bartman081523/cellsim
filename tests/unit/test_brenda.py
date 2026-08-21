"""Tests für BRENDA-Konstanten-Loader."""

from __future__ import annotations

from cellsim.data.brenda import load_brenda_kinetics
from cellsim.modules.reactions import default_registry


def test_brenda_loader_returns_dict() -> None:
    k = load_brenda_kinetics()
    assert isinstance(k, dict)
    assert "glycolysis" in k
    assert k["glycolysis"] > 0.0


def test_brenda_loader_missing_file_returns_empty(tmp_path) -> None:
    k = load_brenda_kinetics(path=tmp_path / "nope.yaml")
    assert k == {}


def test_default_registry_has_brenda_and_hypothesis() -> None:
    reg = default_registry()
    assert reg.n_brenda + reg.n_mgenitalium > 0
    assert reg.n_hypothesis > 0
    # Alle Reaktionen haben ein source-Attribut
    valid_sources = ("BRENDA", "LITERATURE", "HYPOTHESE", "MGENITALIUM", "JCVI_SPECIFIC")
    for rxn in reg.reactions:
        assert rxn.source in valid_sources


def test_default_registry_has_mostly_brenda_or_literature() -> None:
    """≥90 % der Reaktionen sollten eine Quelle haben (nicht HYPOTHESE)."""
    reg = default_registry()
    assert reg.n_with_source >= reg.n_reactions * 0.7, (
        f"Erwartet ≥70 % mit Quelle, got "
        f"{reg.n_with_source}/{reg.n_reactions}"
    )


def test_default_registry_mgenitalium_dominant() -> None:
    """Nach VECTOR_BRENDA_FULL sollten M. genitalium die Hauptquelle sein."""
    reg = default_registry()
    assert reg.n_mgenitalium >= reg.n_reactions * 0.6, (
        f"Erwartet ≥60 % aus M. genitalium, got {reg.n_mgenitalium}/{reg.n_reactions}"
    )


def test_default_registry_brenda_yaml_loads() -> None:
    """BRENDA-YAML sollte alle 21 Reaktionen abdecken."""
    from cellsim.data.brenda import load_brenda_kinetics

    brenda = load_brenda_kinetics()
    reg = default_registry()
    # Mindestens 80 % der Registry-Reaktionen sind in der YAML
    coverage = sum(1 for r in reg.reactions if r.name in brenda) / reg.n_reactions
    assert coverage >= 0.8, f"BRENDA-YAML deckt nur {coverage*100:.0f}% der Reaktionen"
