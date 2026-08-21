"""Tests für programmatisches CellsimMixMind-Audit."""

from __future__ import annotations

from cellsim.audit import (
    AuditReport,
    EvidenceGrade,
    audit_claim,
    grade_from_audit,
    via_negativa_audit,
)


def test_via_negativa_returns_all_10_tests() -> None:
    result = via_negativa_audit("ATP hydrolyzes spontaneously in water.")
    assert len(result.tests) == 10
    assert "confirmation_bias" in result.tests
    assert "modus_ponens_by_analogy" in result.tests


def test_grade_a_for_clean_claim() -> None:
    report = audit_claim(
        "Cellsim L3 is a reductionistic (AnA) approximation; if MES is implemented, "
        "the architecture would become SynA.",
        layer="L3",
        evidence="ROSEN_HORIZON constant defined; smoke tests pass.",
        strategic_vector="VECTOR_ROSEN_HORIZON",
    )
    assert report.grade == EvidenceGrade.A


def test_grade_f_for_unfalsifiable_claim() -> None:
    report = audit_claim("This simulation is correct.")
    # Kein "if" → unfalsifiable BORDERLINE → mindestens C
    assert report.grade in (EvidenceGrade.C, EvidenceGrade.F)


def test_grade_c_for_authority_claim() -> None:
    report = audit_claim(
        "Experts say the cellsim architecture is optimal.",
        layer="L1",
    )
    assert report.grade in (EvidenceGrade.C, EvidenceGrade.F)


def test_grade_b_for_candidate_claim() -> None:
    """Eine 'candidate'-Claim mit BORDERLINE apophenia → B oder C."""
    report = audit_claim(
        "QuQuint-V-Ladder is a candidate for Grover-Orakel-Reduktion.",
        layer="L4",
        evidence="Benchmark CSV shows 1.1-1.3x reduction.",
    )
    assert report.grade in (EvidenceGrade.B, EvidenceGrade.C)


def test_audit_report_has_all_fields() -> None:
    report = audit_claim("Test claim", layer="L2")
    assert isinstance(report, AuditReport)
    assert report.claim == "Test claim"
    assert report.layer == "L2"
    assert report.rationale != ""


def test_grade_from_audit_function() -> None:
    """Direkter Test der Grade-Funktion."""
    from cellsim.audit import ViaNegativaResult

    clean = ViaNegativaResult(claim="x", tests={k: "PASS" for k in "abcdefghij"})
    assert grade_from_audit(clean) == EvidenceGrade.A

    with_fail = ViaNegativaResult(claim="x", tests={k: "PASS" for k in "abcdefghij"})
    with_fail.tests["a"] = "FAIL"
    assert grade_from_audit(with_fail) == EvidenceGrade.C
