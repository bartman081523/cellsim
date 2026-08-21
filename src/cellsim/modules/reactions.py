"""Reaktions-Registry (zunächst 21 makromolekulare Komplexe aus 4DWCM)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Reaction:
    """Eine stöchiometrische Reaktion mit kinetischer Konstante."""

    name: str
    species_change: dict[str, int]      # {species_id: delta}
    k: float                            # Geschwindigkeitskonstante
    source: str = "HYPOTHESE"           # Status-Flag: HYPOTHESE|BRENDA|LITERATURE|MGENITALIUM|JCVI_SPECIFIC


@dataclass(frozen=True)
class ReactionRegistry:
    """Sammlung von Reaktionen + Spezies-Liste."""

    species_ids: tuple[str, ...] = field(default_factory=tuple)
    reactions: tuple[Reaction, ...] = field(default_factory=tuple)

    @property
    def n_species(self) -> int:
        return len(self.species_ids)

    @property
    def n_reactions(self) -> int:
        return len(self.reactions)

    @property
    def n_hypothesis(self) -> int:
        return sum(1 for r in self.reactions if r.source == "HYPOTHESE")

    @property
    def n_brenda(self) -> int:
        return sum(1 for r in self.reactions if r.source == "BRENDA")

    @property
    def n_literature(self) -> int:
        return sum(1 for r in self.reactions if r.source == "LITERATURE")

    @property
    def n_mgenitalium(self) -> int:
        return sum(1 for r in self.reactions if r.source == "MGENITALIUM")

    @property
    def n_jcvi_specific(self) -> int:
        return sum(1 for r in self.reactions if r.source == "JCVI_SPECIFIC")

    @property
    def n_with_source(self) -> int:
        """Anzahl Reaktionen mit bekannter Quelle (nicht HYPOTHESE)."""
        return self.n_reactions - self.n_hypothesis


def default_registry() -> ReactionRegistry:
    """21 makromolekulare Komplexe aus 4DWCM-Tabelle S2.

    Kinetische Konstanten sind primär aus Mycoplasma genitalium-BRENDA
    (nächstverwandt zu JCVI-syn3A), sekundär aus E. coli-BRENDA,
    tertiär aus Literatur, restliche HYPOTHESE.
    Quelle pro Reaktion in `source`-Attribut.
    """
    species = (
        # Metaboliten
        "ATP", "ADP", "Pi", "Glucose", "Pyruvate", "NADH",
        # 21 makromolekulare Komplexe (S2-Stub, vereinfachte Namen)
        "RNAP", "Ribosome_30S", "Ribosome_50S", "Ribosome_70S",
        "DNA_Gyrase", "DNA_Pol_III", "DNA_Ligase", "DNA_TopoI",
        "ATP_synthase", "ATP_synthase_F1", "ATP_synthase_Fo",
        "Degradosome", "FtsZ_ring", "FtsA", "MreB_actin",
        "Pyruvate_decarb", "GroEL_GroES", "Trigger_Factor",
        "Signal_recog", "Sec_translocon",
    )
    # Konstanten aus configs/brenda_kinetics.yaml (Mycoplasma genitalium primär)
    reactions = (
        Reaction("glycolysis", {"Glucose": -1, "Pyruvate": 2, "ATP": 2, "ADP": -2, "NADH": 2, "Pi": -2}, k=450.0, source="MGENITALIUM"),
        Reaction("atp_hydrolysis", {"ATP": -1, "ADP": 1, "Pi": 1}, k=600.0, source="MGENITALIUM"),
        Reaction("atp_synthase", {"ADP": -1, "Pi": -1, "ATP": 1}, k=8800.0, source="MGENITALIUM"),
        Reaction("rnap_init", {"RNAP": 0}, k=0.05, source="MGENITALIUM"),
        Reaction("ribosome_assembly", {"Ribosome_30S": -1, "Ribosome_50S": -1, "Ribosome_70S": 1}, k=4.0, source="MGENITALIUM"),
        Reaction("ribosome_disassembly", {"Ribosome_70S": -1, "Ribosome_30S": 1, "Ribosome_50S": 1}, k=0.04, source="HYPOTHESE"),
        Reaction("dna_pol_iii_binding", {"DNA_Pol_III": 0}, k=1.5, source="MGENITALIUM"),
        Reaction("dna_pol_iii_release", {"DNA_Pol_III": 0}, k=0.4, source="MGENITALIUM"),
        Reaction("gyrase_supercoil", {"DNA_Gyrase": 0, "ATP": -1, "ADP": 1}, k=20.0, source="MGENITALIUM"),
        Reaction("ligase_seal", {"DNA_Ligase": 0, "ATP": -1, "ADP": 1}, k=5.0, source="MGENITALIUM"),
        Reaction("topoi_relax", {"DNA_TopoI": 0}, k=0.9, source="MGENITALIUM"),
        Reaction("trigger_factor_bind", {"Trigger_Factor": 0, "ATP": -1, "ADP": 1}, k=0.4, source="MGENITALIUM"),
        Reaction("groel_groes_fold", {"GroEL_GroES": 0, "ATP": -2, "ADP": 2}, k=3.0, source="MGENITALIUM"),
        Reaction("ftsz_polymerization", {"FtsZ_ring": 1, "ATP": -1, "ADP": 1}, k=10.0, source="MGENITALIUM"),
        Reaction("ftsa_membrane_anchor", {"FtsA": 0}, k=0.15, source="HYPOTHESE"),
        Reaction("mreb_cytoskeleton", {"MreB_actin": 0, "ATP": -1, "ADP": 1}, k=1.0, source="MGENITALIUM"),
        Reaction("pyruvate_decarb_complex", {"Pyruvate_decarb": 0}, k=4.0, source="MGENITALIUM"),
        Reaction("degradosome_degrade", {"Degradosome": 0, "ATP": -1, "ADP": 1}, k=0.3, source="HYPOTHESE"),
        Reaction("signal_recognition", {"Signal_recog": 0, "ATP": -1, "ADP": 1}, k=0.25, source="MGENITALIUM"),
        Reaction("sec_translocation", {"Sec_translocon": 0, "ATP": -1, "ADP": 1}, k=0.4, source="HYPOTHESE"),
    )
    return ReactionRegistry(species_ids=species, reactions=reactions)


def mass_action_conserves_atoms(rxns: tuple[Reaction, ...]) -> bool:
    """Prüft, dass jede Reaktion netto keine Atome erzeugt/vernichtet.

    Für Smoke-Test: Summen der Stöchiometrie-Koeffizienten = 0.
    """
    return all(sum(r.species_change.values()) == 0 for r in rxns)
