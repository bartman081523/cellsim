"""End-to-End-Integration: Cache → Volumes → Driver → Analyse → Audit.

Vektor VECTOR_E2E_FULL: kompletter Workflow mit gemockten AlphaFold-Daten.
"""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import patch

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.analysis.pipeline import run_analysis
from cellsim.audit.audit_self import run_self_audit, write_self_audit_report
from cellsim.core.time_axis import TimeAxis
from cellsim.data.volumes_loader import aggregate_volumes_by_species, load_volumes_tsv
from cellsim.driver.loop import HybridDriver, write_run_csv
from cellsim.modules.membrane import MembraneGeometry, MembraneParams
from cellsim.modules.mes import MESAdapter
from cellsim.modules.reactions import default_registry


def _fake_pdb(uniprot: str) -> str:
    return (
        f"HEADER    {uniprot:<40s}  01-JAN-00   SYN\n"
        f"ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 80.00           C\n"
        f"ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00 85.00           C\n"
        f"ATOM      3  CA  ALA A   3       7.600   0.000   0.000  1.00 75.00           C\n"
        f"ATOM      4  CA  ALA A   4      11.400   0.000   0.000  1.00 90.00           C\n"
        "END\n"
    )


def test_e2e_full_pipeline(tmp_path: Path, monkeypatch) -> None:
    """Cache → Volumes → Driver → Analyse → Audit in einem Test."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    # 1. Cache bauen
    cache_root = tmp_path / "cache" / "cellsim"
    cache_root.mkdir(parents=True, exist_ok=True)
    (cache_root / "proteome.tsv").write_text(
        "accession\tid\tgene_names\tprotein_name\tlength\n"
        "C7MID5\tDNAA\tdnaA\tChromosomal replication initiator\t455\n"
        "C7LLN1\tDBH\tdnaN\tDNA polymerase III beta\t373\n",
        encoding="utf-8",
    )

    def fake_fetch(uniprot, out_dir=None, use_network=True, **kw):  # type: ignore[no-untyped-def]
        from cellsim.data.alphafold import FetchResult, PdbSource
        return FetchResult(
            accession=uniprot,
            version=6,
            path=Path("/fake"),
            source=PdbSource.V6,
            pdb_text=_fake_pdb(uniprot),
        )

    with patch("cellsim.cli.cache.fetch_pdb", side_effect=fake_fetch):
        from cellsim.cli.cache import build_volumes_table

        volumes_tsv = build_volumes_table(out_dir=tmp_path, use_network=False)
    assert volumes_tsv.exists()

    # 2. Volumes in Treiber laden
    volumes = load_volumes_tsv(volumes_tsv)
    species = default_registry().species_ids
    volumes_agg = aggregate_volumes_by_species(volumes, species)

    # 3. Driver mit allen Layern
    rng_init = np.random.default_rng(42)
    rdme = RDMEAdapter(
        registry=default_registry(),
        grid_shape=(4, 4, 4),
        use_local_diffusion=True,
    )
    ode = ODEAdapter(use_frohlich=True)
    chrom = ChromosomeAdapter(n_beads=20, rng=rng_init, use_riemann=True)
    membrane = MembraneGeometry()
    mes = MESAdapter()

    time_axis = TimeAxis(0.0, 1.0, 1e-3, 1e-1)
    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=10,
        seed=42,
        volumes_angstrom3=volumes_agg,
        mes=mes,
    )
    result = driver.run()

    # 4. Outputs schreiben
    run_csv = write_run_csv(result, tmp_path / "run.csv")
    assert run_csv.exists()
    ana = run_analysis(result, tmp_path, write_plots=False)
    assert ana.summary_csv.exists()

    # 5. Audit
    reports = run_self_audit()
    audit_md = write_self_audit_report(reports, tmp_path / "self_audit.md")
    assert audit_md.exists()

    # End-to-end Sanity-Check
    assert result.walltime_s < 5.0   # Smoke < 5 min
    with ana.summary_csv.open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert "growth_rate_mean_nm_per_s" in rows[0]


def test_e2e_with_dying_cell_triggers_mes(tmp_path: Path) -> None:
    """Wenn ATP unter kritische Schwelle fällt, triggert MES DEAD."""
    rng_init = np.random.default_rng(1)
    rdme = RDMEAdapter(registry=default_registry(), grid_shape=(2, 2, 2))
    ode = ODEAdapter()
    chrom = ChromosomeAdapter(n_beads=10, rng=rng_init)
    membrane = MembraneGeometry()

    # MES mit sehr hohen Schwellen → Zelle wird schnell DEAD
    from cellsim.modules.mes import MESParams

    mes = MESAdapter(MESParams(atp_min_mM=10.0, atp_critical_mM=5.0))

    time_axis = TimeAxis(0.0, 1.0, 1e-3, 1e-1)
    driver = HybridDriver(
        time_axis=time_axis,
        rdme=rdme,
        ode=ode,
        chromosome=chrom,
        membrane=membrane,
        sync_interval=5,
        seed=1,
        mes=mes,
    )
    result = driver.run()

    # Zelle sollte DEAD sein, also weniger Sync-Ticks als n_steps
    assert not mes.is_alive()
    assert driver._sync_count < time_axis.n_rdme_steps / driver.sync_interval
