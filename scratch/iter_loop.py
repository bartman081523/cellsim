"""Iterative Forschungsschleife — empirisch, ergebnisoffen, transkategorial.

Dieses Skript ist der Kern des scratch/-Workflows:
1. Lädt alle Experimente aus scratch/experiments/iter-N/
2. Wertet sie automatisch aus
3. Extrahiert strategische Vektoren (was lernen wir?)
4. Schreibt Verbesserungsvorschläge nach scratch/strategic_vectors/

Status: selbst-iterierend. Wenn ein Iter keine neuen Signale produziert,
schlägt es vor, externe Quellordner erneut zu konsultieren.

VECTOR_ITER_LOOP: endlosschleife der Theorie-Vertiefung.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

SCRATCH_ROOT: Path = Path(__file__).resolve().parent
EXPERIMENTS_DIR: Path = SCRATCH_ROOT / "experiments"
RESULTS_DIR: Path = SCRATCH_ROOT / "results"
VECTORS_DIR: Path = SCRATCH_ROOT / "strategic_vectors"


@dataclass(frozen=True)
class IterationResult:
    """Ergebnis einer Iterations-Auswertung."""

    iter_id: str
    hypothesis: str
    method: str
    result: str
    signal: str                # "STRONG" | "WEAK" | "NULL" | "CONTRADICTION"
    next_vectors: tuple[str, ...] = field(default_factory=tuple)


def discover_iterations() -> list[Path]:
    """Findet alle iter-N/-Verzeichnisse."""
    if not EXPERIMENTS_DIR.exists():
        return []
    return sorted(EXPERIMENTS_DIR.glob("iter-*"))


def evaluate_iter(iter_dir: Path) -> IterationResult | None:
    """Wertet eine Iteration aus (sofern experiment.md + result.json existieren)."""
    experiment_md = iter_dir / "experiment.md"
    result_json = iter_dir / "result.json"
    if not experiment_md.exists() or not result_json.exists():
        return None
    text = experiment_md.read_text(encoding="utf-8")
    result_data = json.loads(result_json.read_text(encoding="utf-8"))
    # Einfache Parsing-Heuristik
    hypothesis = _extract_section(text, "Hypothese") or "?"
    method = _extract_section(text, "Method") or "?"
    result = _extract_section(text, "Result") or "?"
    signal = result_data.get("signal", "NULL")
    next_vectors = tuple(result_data.get("next_vectors", ()))
    return IterationResult(
        iter_id=iter_dir.name,
        hypothesis=hypothesis[:200],
        method=method[:200],
        result=result[:200],
        signal=signal,
        next_vectors=next_vectors,
    )


def _extract_section(text: str, name: str) -> str | None:
    """Extrahiert eine Markdown-Section."""
    for line in text.splitlines():
        if line.startswith(f"# {name}"):
            return line.lstrip(f"# {name}").strip()
    return None


def suggest_next_iterations(last_results: list[IterationResult]) -> list[str]:
    """Schlägt nächste Iterationen basierend auf dem letzten Ergebnis vor."""
    if not last_results:
        return ["iter-1: erstes Experiment"]
    last = last_results[-1]
    suggestions = []

    if last.signal == "STRONG":
        # Hypothese bestätigt → Verfeinerung
        suggestions.append(
            f"{last.iter_id}-refine: Verfeinerung mit höherer Auflösung oder "
            "längerer Laufzeit"
        )
        suggestions.append(
            f"{last.iter_id}-extend: Anwendung auf verwandte Systeme "
            "(z.B. JCVI-syn3A statt E. coli)"
        )

    elif last.signal == "WEAK":
        # Signal schwach → Wiederholung mit anderen Bedingungen
        suggestions.append(
            f"{last.iter_id}-retry: Wiederholung mit höherer Statistik "
            "(n × 10 Samples)"
        )

    elif last.signal == "NULL":
        # Kein Signal → Theorie-Hypothese verwerfen oder modifizieren
        suggestions.append(
            f"{last.iter_id}-retire: Hypothese verwerfen, dokumentieren in LIMITATIONS.md"
        )
        suggestions.append(
            "iter-new: Konsultiere /run/media/julian/ML4/riemann/ + /ML3/faizal-rebuttal-*/"
            "für alternative Theorie-Hypothesen"
        )

    elif last.signal == "CONTRADICTION":
        # Hypothese widerlegt → kritischer Bericht
        suggestions.append(
            f"{last.iter_id}-report: Ausführlicher Widerlegungs-Bericht mit "
            "Roh-Daten + Statistik"
        )
        suggestions.append(
            f"{last.iter_id}-redirect: Pivot zu verwandter Theorie"
        )

    return suggestions


def write_run_summary() -> Path:
    """Schreibt eine Zusammenfassung aller bisherigen Iterationen."""
    target = VECTORS_DIR / "run_summary.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Iterations-Zusammenfassung\n"]
    iters = discover_iterations()
    results = [r for r in (evaluate_iter(d) for d in iters) if r is not None]
    lines.append(f"Anzahl Iterationen: {len(results)}\n")
    lines.append("\n## Detail\n")
    for r in results:
        lines.append(f"\n### {r.iter_id} ({r.signal})\n")
        lines.append(f"**Hypothese:** {r.hypothesis}\n")
        lines.append(f"**Result:** {r.result}\n")
        if r.next_vectors:
            lines.append("**Nächste Vektoren:**\n")
            for v in r.next_vectors:
                lines.append(f"- {v}\n")
    target.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote run summary → %s", target)
    return target
