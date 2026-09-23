"""CLI-Entry-Point für cellsim.

Subcommands (Inkrement 1):
    cache build   — UniProt-Proteom + AlphaFold-Volumen-Tabelle bauen
    cache inspect — Cache-Status anzeigen
    simulate      — RDME/ODE/Chromosom-Smoke-Simulation ausführen
    seed          — effektiven Seed anzeigen
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer

from cellsim.cli.cache import build_volumes_table, inspect_cache
from cellsim.core.constants import ROSEN_HORIZON, SEED_BASE

app = typer.Typer(
    name="cellsim",
    help="Minimaler JCVI-syn3A-Simulator (L3-Kern der 4-Schichten-Architektur).",
    no_args_is_help=True,
    add_completion=False,
)
cache_app = typer.Typer(help="Cache-Operationen (Proteom + PDB-Volumen).")
app.add_typer(cache_app, name="cache")


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("cellsim")
    logger.warning(ROSEN_HORIZON)


@cache_app.command("build")
def cache_build(
    out_dir: Path = typer.Option(
        Path("./out"), "--out-dir", "-o", help="Zielverzeichnis für volumes.tsv"
    ),
    proteome: str = typer.Option(
        "UP000326712", "--proteome", help="UniProt-Proteom-ID"
    ),
    force_download: bool = typer.Option(
        False, "--force", help="Cache überschreiben"
    ),
    use_network: bool = typer.Option(
        True, "--no-network/--use-network", help="Netzwerkzugriff erlauben"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Baut die RDME-Volumen-Tabelle aus UniProt + AlphaFold."""
    _setup_logging(verbose)
    out_dir.mkdir(parents=True, exist_ok=True)
    tsv_path = build_volumes_table(
        out_dir=out_dir,
        proteome=proteome,
        force=force_download,
        use_network=use_network,
    )
    typer.echo(f"Wrote volume table: {tsv_path}")


@cache_app.command("inspect")
def cache_inspect(
    out_dir: Path = typer.Option(
        Path("./out"), "--out-dir", "-o", help="Verzeichnis mit volumes.tsv"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Zeigt Cache-Status (Anzahl Einträge, Quellenverteilung)."""
    _setup_logging(verbose)
    if not (out_dir / "volumes.tsv").exists():
        typer.echo(f"No volumes.tsv in {out_dir}; run `cellsim cache build` first.")
        raise typer.Exit(code=1)
    info = inspect_cache(out_dir)
    typer.echo(f"Cache dir: {out_dir}")
    typer.echo(f"Proteome entries: {info['n_entries']}")
    typer.echo(f"Sources: {info['source_counts']}")
    typer.echo(f"Mean Rs (Å): {info['rs_mean']:.1f}")
    typer.echo(f"Total V_ex (Å³): {info['v_ex_total']:.3e}")


@app.command("benchmark")
def benchmark(
    out_dir: Path = typer.Option(
        Path("./out/benchmark"), "--out-dir", "-o", help="Zielverzeichnis"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """VECTOR_QUQUINT_BENCHMARK: Vergleicht Qudit-V-Ladder-Architekturen."""
    _setup_logging(verbose)

    from cellsim.benchmarks.ququint_vs_qubit import (
        benchmark_conformation_range,
        write_benchmark_csv,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    results = benchmark_conformation_range()
    csv_path = write_benchmark_csv(results, out_dir / "ququint_benchmark.csv")
    typer.echo(f"Wrote benchmark → {csv_path} ({len(results)} rows)")
    # Kompakte Zusammenfassung
    for r in results:
        typer.echo(
            f"  {r.system:>8s} (d={r.dimension}) n={r.n_conformations:>7d} "
            f"→ naive={r.n_two_qudit_gates_naive:>6d} "
            f"V-ladder={r.n_two_qudit_gates_v_ladder:>6d} "
            f"reduction={r.reduction_factor:.2f}×"
        )


@app.command("self-audit")
def self_audit_cmd(
    out_dir: Path = typer.Option(
        Path("./out/self_audit"), "--out-dir", "-o", help="Zielverzeichnis"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """CellsimMixMind-Selbstanwendung: auditiere alle zentralen cellsim-Behauptungen."""
    _setup_logging(verbose)

    from cellsim.audit.audit_self import (
        run_self_audit,
        write_self_audit_report,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    reports = run_self_audit()
    md_path = write_self_audit_report(reports, out_dir / "self_audit_report.md")
    typer.echo(f"Wrote {md_path} ({len(reports)} claims audited)")
    # Kompakte Zusammenfassung
    grade_counts: dict[str, int] = {}
    for r in reports:
        grade_counts[r.grade.value] = grade_counts.get(r.grade.value, 0) + 1
    typer.echo("Grade-Verteilung:")
    for g in ("A", "B", "C", "F"):
        typer.echo(f"  Grade {g}: {grade_counts.get(g, 0)}")


@app.command("audit")
def audit_cmd(
    claim: str = typer.Option(
        ...,
        "--claim",
        help="Zu prüfende Behauptung",
    ),
    layer: str = typer.Option(
        "L3", "--layer", help="L1|L2|L3|L4|cross"
    ),
    evidence: str = typer.Option(
        "", "--evidence", help="Beleg-Quelle / Datei / Commit"
    ),
    strategic_vector: str = typer.Option(
        "", "--vector", help="Strategischer Vektor"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """CellsimMixMind-Audit: Via-Negativa + Evidence-Grade."""
    _setup_logging(verbose)

    from cellsim.audit import audit_claim

    report = audit_claim(
        claim=claim,
        layer=layer,
        evidence=evidence,
        strategic_vector=strategic_vector,
    )
    typer.echo(f"Claim: {report.claim}")
    typer.echo(f"Layer: {report.layer}")
    typer.echo(f"Grade: {report.grade.value}")
    typer.echo(f"Rationale: {report.rationale}")
    typer.echo("Via-Negativa:")
    for test, status in report.via_negativa.tests.items():
        typer.echo(f"  {test:>30s} : {status}")
    if report.evidence:
        typer.echo(f"Evidence: {report.evidence}")
    if report.strategic_vector:
        typer.echo(f"Strategic Vector: {report.strategic_vector}")


@app.command("seed")
def show_seed(
    base: int = typer.Option(SEED_BASE, "--base", help="Base-Seed"),
    run: int = typer.Option(0, "--run", help="Run-Index"),
    cond: int = typer.Option(0, "--cond", help="Condition-Index"),
) -> None:
    """Zeigt den effektiven Seed für (base, run, cond)."""
    from cellsim.core.rng import seed_for

    typer.echo(seed_for(base, run, cond))


@app.command("simulate")
def simulate(
    out_dir: Path = typer.Option(
        Path("./out/smoke"), "--out-dir", "-o", help="Zielverzeichnis für run.csv"
    ),
    preset: str = typer.Option(
        "smoke", "--preset", help="Vordefinierte Konfiguration (smoke)"
    ),
    t_end_s: float = typer.Option(
        60.0, "--t-end-s", help="Simulationszeit in Sekunden"
    ),
    sync_interval: int = typer.Option(
        100, "--sync-interval", help="RDME-Schritte zwischen ODE-Syncs"
    ),
    seed: int = typer.Option(
        SEED_BASE, "--seed", help="Base-Seed für Reproduzierbarkeit"
    ),
    use_local_diffusion: bool = typer.Option(
        False, "--local-diffusion/--global-diffusion",
        help="L2↔L3-Brücke: crowding-aware Diffusion an/aus",
    ),
    use_superradiance: bool = typer.Option(
        False, "--superradiance/--no-superradiance",
        help="Photonische Kopplung (iter-23): Superradianz-Quelle an/aus",
    ),
    analyze: bool = typer.Option(
        True, "--analyze/--no-analyze", help="Analyse-Pipeline nach Sim ausführen"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Führt eine Smoke-Simulation aus und schreibt run.csv (+ Analyse)."""
    _setup_logging(verbose)

    from cellsim.adapters.rdme import RDMEAdapter
    from cellsim.core.time_axis import smoke_time_axis
    from cellsim.driver.loop import (
        HybridDriver,
        default_chromosome,
        default_membrane,
        default_ode,
        write_run_csv,
    )
    from cellsim.modules.reactions import default_registry

    if preset != "smoke":
        typer.echo(f"Unknown preset: {preset}; only 'smoke' available")
        raise typer.Exit(code=1)

    base_axis = smoke_time_axis()
    time_axis = type(base_axis)(
        t_start_s=0.0,
        t_end_s=t_end_s,
        dt_rdme_s=base_axis.dt_rdme_s,
        dt_ode_s=base_axis.dt_ode_s,
    )

    rdme = RDMEAdapter(
        registry=default_registry(),
        grid_shape=(6, 6, 6),
        use_local_diffusion=use_local_diffusion,
    )
    ode = default_ode()
    chrom = default_chromosome(seed=seed)
    membrane = default_membrane()
    photonic = None
    if use_superradiance:
        from cellsim.modules.photonic_coupling import PhotonicSource

        photonic = PhotonicSource()

    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=sync_interval,
        seed=seed,
        photonic=photonic,
    )
    result = driver.run()

    run_csv = write_run_csv(result, out_dir / "run.csv")
    typer.echo(
        f"Wrote {run_csv} ({len(result.time_s)} samples, {result.walltime_s:.1f}s walltime)"
    )

    if analyze:
        from cellsim.analysis.pipeline import run_analysis

        ana = run_analysis(result, out_dir, tag="smoke")
        typer.echo(f"Wrote summary: {ana.summary_csv}")
        typer.echo(f"Wrote {len(ana.plots)} plots → {out_dir}")


def main() -> None:
    """Entry-Point für `python -m cellsim` und Konsolen-Script `cellsim`."""
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
