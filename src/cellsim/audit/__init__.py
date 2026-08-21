"""CellsimMixMind-Audit-Workflow programmatisch."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EvidenceGrade(str, Enum):
    """A-F Skala aus CellsimMixMind (siehe JsonMind)."""

    A = "A"  # CORROBORATED via_end_to_end
    B = "B"  # PLAUSIBLE
    C = "C"  # AMBIGUOUS
    F = "F"  # FALSIFIED


@dataclass
class ViaNegativaResult:
    """Ergebnis aller 10 Via-Negativa-Tests für eine Behauptung."""

    claim: str
    tests: dict[str, str] = field(default_factory=dict)
    # Pro Test: "PASS" | "FAIL" | "BORDERLINE"

    def is_clean(self) -> bool:
        return not any(v == "FAIL" for v in self.tests.values())


@dataclass
class AuditReport:
    """Vollständiger CellsimMixMind-Audit-Report für eine Behauptung."""

    claim: str
    layer: str   # L1, L2, L3, L4 oder Cross
    grade: EvidenceGrade
    via_negativa: ViaNegativaResult
    evidence: str
    strategic_vector: str
    rationale: str


def via_negativa_audit(claim: str) -> ViaNegativaResult:
    """Wendet alle 10 Via-Negativa-Tests auf eine Behauptung an.

    Diese Standard-Tests sind konservativ: bei Ambiguität → BORDERLINE.
    """
    result = ViaNegativaResult(claim=claim)
    # Automatische Heuristiken pro Test
    claim_lower = claim.lower()

    # 1. Confirmation Bias: Wenn Claim sehr spezifisch ("genau", "exakt")
    if any(w in claim_lower for w in ["exactly", "precisely", "exakt", "genau"]):
        result.tests["confirmation_bias"] = "BORDERLINE"
    else:
        result.tests["confirmation_bias"] = "PASS"

    # 2. Texas Sharpshooter: Wenn Claim "post-hoc" oder "fitted" enthält
    if any(w in claim_lower for w in ["post-hoc", "fitted", "nachträglich"]):
        result.tests["texas_sharpshooter"] = "FAIL"
    else:
        result.tests["texas_sharpshooter"] = "PASS"

    # 3. Circular Reasoning: Wenn Claim auf Definition referenziert
    if "because we define" in claim_lower or "per definition" in claim_lower:
        result.tests["circular_reasoning"] = "FAIL"
    else:
        result.tests["circular_reasoning"] = "PASS"

    # 4. Equivocation: Wenn Claim metaphorische Begriffe nutzt
    if any(w in claim_lower for w in ["quantum coherence means", "feels like"]):
        result.tests["equivocation"] = "FAIL"
    else:
        result.tests["equivocation"] = "PASS"

    # 5. Scope Creep: Wenn Claim von "P5 ticked 12 times" auf "causal intent" generalisiert
    if "therefore" in claim_lower and any(w in claim_lower for w in ["proves", "demonstrates"]):
        result.tests["scope_creep"] = "BORDERLINE"
    else:
        result.tests["scope_creep"] = "PASS"

    # 6. Apophenia: Wenn Claim auf Pattern ohne Replikation basiert
    if "hypothesis" in claim_lower or "candidate" in claim_lower:
        result.tests["apophenia"] = "BORDERLINE"
    else:
        result.tests["apophenia"] = "PASS"

    # 7. False Precision: Wenn Claim spezifische Zahlen ohne Konfidenzintervall
    if any(w in claim_lower for w in ["1000×", "99.6%", "0.0017"]):
        result.tests["false_precision"] = "BORDERLINE"
    else:
        result.tests["false_precision"] = "PASS"

    # 8. Unfalsifiable: Wenn Claim keine Falsifikationsbedingung nennt
    if "if" not in claim_lower and "would fail" not in claim_lower:
        result.tests["unfalsifiable"] = "BORDERLINE"
    else:
        result.tests["unfalsifiable"] = "PASS"

    # 9. Authority Appeal: Wenn Claim "experts say" oder ähnliches
    if any(w in claim_lower for w in ["experts say", "authorities agree"]):
        result.tests["authority_appeal"] = "FAIL"
    else:
        result.tests["authority_appeal"] = "PASS"

    # 10. Modus Ponens by Analogy: Wenn Claim auf Isomorphismus ohne Spezifikation
    if "is like" in claim_lower or "ähnlich" in claim_lower:
        result.tests["modus_ponens_by_analogy"] = "BORDERLINE"
    else:
        result.tests["modus_ponens_by_analogy"] = "PASS"

    return result


def grade_from_audit(via_neg: ViaNegativaResult) -> EvidenceGrade:
    """Leitet Evidence-Grade aus Via-Negativa-Result ab.

    Konservative Skala:
    - 0 FAIL und ≤1 BORDERLINE → A (clean)
    - 0 FAIL und 2-3 BORDERLINE → B (plausible)
    - 0 FAIL und ≥4 BORDERLINE → C (ambiguous)
    - 1 FAIL → C
    - ≥2 FAIL → F (falsified)
    - Spezialsignal: unfalsifiable BORDERLINE → mindestens C
    """
    fails = sum(1 for v in via_neg.tests.values() if v == "FAIL")
    borderlines = sum(1 for v in via_neg.tests.values() if v == "BORDERLINE")
    unfalsifiable_flag = via_neg.tests.get("unfalsifiable") == "BORDERLINE"

    if fails >= 2:
        return EvidenceGrade.F
    if fails == 1:
        return EvidenceGrade.C
    if unfalsifiable_flag and borderlines >= 1:
        # Unfalsifizierbare Claims sind grundsätzlich suspekt
        return EvidenceGrade.C
    if borderlines >= 4:
        return EvidenceGrade.C
    if borderlines >= 2:
        return EvidenceGrade.B
    return EvidenceGrade.A


def audit_claim(
    claim: str,
    layer: str = "L3",
    evidence: str = "",
    strategic_vector: str = "",
) -> AuditReport:
    """Komplettes CellsimMixMind-Audit für eine Behauptung."""
    via_neg = via_negativa_audit(claim)
    grade = grade_from_audit(via_neg)

    rationale = f"{sum(1 for v in via_neg.tests.values() if v == 'PASS')}/10 PASS, "
    rationale += f"{sum(1 for v in via_neg.tests.values() if v == 'BORDERLINE')}/10 BORDERLINE, "
    rationale += f"{sum(1 for v in via_neg.tests.values() if v == 'FAIL')}/10 FAIL"

    return AuditReport(
        claim=claim,
        layer=layer,
        grade=grade,
        via_negativa=via_neg,
        evidence=evidence,
        strategic_vector=strategic_vector,
        rationale=rationale,
    )
