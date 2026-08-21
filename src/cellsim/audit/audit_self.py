"""CellsimMixMind-Selbstanwendung: Auditiere alle zentralen cellsim-Behauptungen.

Vektor VECTOR_MIXMIND_SELF_AUDIT: programmatischer Audit der cellsim-Architektur
gegen ihre eigenen Behauptungen. Liefert Evidence-Grade pro Aussage und
einen Gesamt-Report.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from cellsim.audit import (
    AuditReport,
    audit_claim,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SelfAuditItem:
    """Eine zentrale cellsim-Behauptung."""

    claim: str
    layer: str
    evidence: str
    strategic_vector: str


# Zentrale cellsim-Behauptungen — die "Kernthesen" der Architektur
CELLSIM_CORE_CLAIMS: tuple[SelfAuditItem, ...] = (
    SelfAuditItem(
        claim="JCVI-syn3A cellsim L3 implements a hybrid RDME + ODE + chromosome loop coupled at sync_interval.",
        layer="L3",
        evidence="src/cellsim/driver/loop.py:HybridDriver.run()",
        strategic_vector="VECTOR_L3_FIRST",
    ),
    SelfAuditItem(
        claim="The simulation uses real AlphaFold-derived volumes for crowding-aware diffusion; if PDB unavailable, stub is used.",
        layer="L2/L3",
        evidence="src/cellsim/data/volumes_loader.py + adapters/rdme.py:_apply_local_diffusion",
        strategic_vector="VECTOR_BRIDGE_L2_L3",
    ),
    SelfAuditItem(
        claim="Asakura-Oosawa depletion reduces effective diffusion in voxels with high crowder density.",
        layer="L2",
        evidence="src/cellsim/modules/asakura_oosawa.py:ao_diffusion_modifier",
        strategic_vector="VECTOR_BRIDGE_L2_L3",
    ),
    SelfAuditItem(
        claim="The 21 macromolecular complexes from 4DWCM Table S2 are modeled as reaction species with BRENDA-extracted kinetics.",
        layer="L3",
        evidence="src/cellsim/modules/reactions.py:default_registry() + configs/brenda_kinetics.yaml",
        strategic_vector="VECTOR_BRENDA_FULL",
    ),
    SelfAuditItem(
        claim="Riemann-geometric DNA manifold reduces torsion stress in the chromosome configuration space.",
        layer="L4",
        evidence="src/cellsim/modules/riemann.py:update_manifold_from_geometry",
        strategic_vector="VECTOR_RIEMANN_DNA",
    ),
    SelfAuditItem(
        claim="QuQuint-V-Ladder reduces two-qudit gate count by 1.1x to 1.3x for biologically realistic conformation counts.",
        layer="L4",
        evidence="src/cellsim/benchmarks/ququint_vs_qubit.py (own replication, conservative)",
        strategic_vector="VECTOR_QUQUINT_BENCHMARK",
    ),
    SelfAuditItem(
        claim="L1/MES adapter monitors cell state and triggers Kolimit-like repair when ATP falls below threshold.",
        layer="L1",
        evidence="src/cellsim/modules/mes.py:MESAdapter.step()",
        strategic_vector="VECTOR_L1_MES",
    ),
    SelfAuditItem(
        claim="Rosen's No-Go Theorem (AnA ≠ SynA) is acknowledged as a permanent horizon for L3 simulations.",
        layer="cross",
        evidence="cellsim/LIMITATIONS.md §1, core/constants.py:ROSEN_HORIZON",
        strategic_vector="VECTOR_ROSEN_HORIZON",
    ),
    SelfAuditItem(
        claim="Fröhlich condensation modulates ATP consumption by up to 5% in highly ordered cellular regions.",
        layer="L4",
        evidence="src/cellsim/modules/frohlich.py:FrohlichAdapter.atp_savings_factor",
        strategic_vector="VECTOR_FROEHLICH_CONDENSATION",
    ),
    SelfAuditItem(
        claim="CellsimMixMind audit applies 10 Via-Negativa tests to any claim and assigns Evidence Grade A-F.",
        layer="meta",
        evidence="src/cellsim/audit/__init__.py:audit_claim()",
        strategic_vector="VECTOR_MIXMIND_PROGRAMMATIC",
    ),
)


def run_self_audit() -> list[AuditReport]:
    """Auditiert alle CELLSIM_CORE_CLAIMS."""
    reports = []
    for item in CELLSIM_CORE_CLAIMS:
        report = audit_claim(
            claim=item.claim,
            layer=item.layer,
            evidence=item.evidence,
            strategic_vector=item.strategic_vector,
        )
        reports.append(report)
        logger.info(
            "Audit %s: Grade %s (%d/10 PASS)",
            item.layer,
            report.grade.value,
            sum(1 for v in report.via_negativa.tests.values() if v == "PASS"),
        )
    return reports


def write_self_audit_report(reports: list[AuditReport], out_path: Path) -> Path:
    """Schreibt Selbst-Audit als Markdown-Datei."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# CellsimMixMind Self-Audit Report\n"]
    lines.append(f"Generiert: {len(reports)} Claims auditiert\n")
    lines.append("\n## Zusammenfassung\n")
    grade_counts: dict[str, int] = {}
    for r in reports:
        grade_counts[r.grade.value] = grade_counts.get(r.grade.value, 0) + 1
    for g in ("A", "B", "C", "F"):
        lines.append(f"- Grade {g}: {grade_counts.get(g, 0)}")
    lines.append("\n## Detail\n")
    for r in reports:
        lines.append(f"\n### [{r.grade.value}] {r.layer} — {r.strategic_vector}\n")
        lines.append(f"**Claim:** {r.claim}\n")
        lines.append(f"**Evidence:** {r.evidence}\n")
        lines.append(f"**Rationale:** {r.rationale}\n")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote self-audit report → %s", out_path)
    return out_path
