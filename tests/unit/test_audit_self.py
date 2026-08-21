"""Tests für CellsimMixMind-Selbstanwendung."""

from __future__ import annotations

from pathlib import Path

from cellsim.audit.audit_self import (
    CELLSIM_CORE_CLAIMS,
    run_self_audit,
    write_self_audit_report,
)


def test_core_claims_not_empty() -> None:
    assert len(CELLSIM_CORE_CLAIMS) >= 8


def test_self_audit_returns_reports() -> None:
    reports = run_self_audit()
    assert len(reports) == len(CELLSIM_CORE_CLAIMS)
    # Alle Behauptungen sollten mindestens Grade C erreichen (keine F)
    for r in reports:
        assert r.grade.value in ("A", "B", "C"), (
            f"FALSIFIED: {r.claim[:80]}"
        )


def test_self_audit_writes_report(tmp_path: Path) -> None:
    target = tmp_path / "self_audit.md"
    write_self_audit_report(run_self_audit(), target)
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "CellsimMixMind Self-Audit Report" in content
    assert "## Zusammenfassung" in content
