# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Was dieses Verzeichnis ist

`/run/media/julian/ML3/cellsim/` ist die **Implementation** der holistischen 4-Schichten-Architektur
(siehe `Forschung Zur Vollständigen, Numerischen Und Modul....md`). Status: **L3 (numerisch)** + **L2-Brücke (A-O)** + **L4 (Riemann-Geometrie + QuQuint-Benchmark)** + **CellsimMixMind-Audit** programmatisch umgesetzt. L1/MES nicht implementiert (siehe LIMITATIONS.md §1).

## Schnellstart-Befehle

```bash
# Installation (in-place, editierbar)
pip install --user --break-system-packages -e .

# Linting
ruff check src/                  # alle (clean)
mypy src/cellsim/                # limitiert durch numpy-stub-Inkompat (3.14)

# Tests
PYTHONPATH=src pytest -q                              # alle (106 Tests, ~2.5s)
PYTHONPATH=src pytest tests/unit/ -v                  # nur Unit
PYTHONPATH=src pytest tests/integration/ -v           # nur Integration
PYTHONPATH=src pytest -m smoke                        # nur Smoke-Tests

# Daten-Cache (AlphaFold-Volumina für JCVI-syn3A)
PYTHONPATH=src python -m cellsim cache build --out-dir ./out
PYTHONPATH=src python -m cellsim cache inspect --out-dir ./out

# Smoke-Simulation (60 s sim, <5 min walltime)
PYTHONPATH=src python -m cellsim simulate --t-end-s 60 --out-dir ./out/smoke
# Mit L2-Brücke (Asakura-Oosawa / crowding-aware Diffusion):
PYTHONPATH=src python -m cellsim simulate --t-end-s 60 --out-dir ./out/smoke_ao --local-diffusion

# QuQuint-Benchmark (L4)
PYTHONPATH=src python -m cellsim benchmark --out-dir ./out/benchmark

# CellsimMixMind-Audit (einzelne Behauptung)
PYTHONPATH=src python -m cellsim audit --claim "QuQuint reduces Grover gate count by 1000x." --layer L4

# CellsimMixMind-Selbst-Audit (10 zentrale Behauptungen)
PYTHONPATH=src python -m cellsim self-audit --out-dir ./out/self_audit

# CLI-Hilfe
PYTHONPATH=src python -m cellsim --help
```

## Architektur

```
src/cellsim/
├── core/          # Konstanten, Einheiten, Zeitachsen, RNG (single source of truth)
├── data/          # UniProt + AlphaFold-PDBs (Fallback v6→v4→v3) + BRENDA + volumes.tsv-Loader
├── adapters/      # Protocol[Step] — RDME/Gillespie, ODE/scipy+Fröhlich, Chromosom/Bead-Spring+Riemann
├── modules/       # Membrane, Reaktionen (21 + BRENDA), Crowding, Asakura-Oosawa, Riemann, Fröhlich, MES
├── driver/        # HybridDriver — RDME + ODE + Chromosom + Membrane + MES + volumes
├── analysis/      # Pipeline (4 CSVs), Metrics (_mean/_sem), 4 PNG-Plots
├── audit/         # CellsimMixMind-Audit + Selbst-Audit (10 Via-Negativa-Tests, Grade A-F)
├── benchmarks/    # QuQuint-V-Ladder-Benchmark (L4)
└── cli/           # Typer-CLI: cache, simulate, benchmark, audit, self-audit, seed
```

### Datenflüsse

1. **CLI** → lade YAML + dataclass-Defaults → `SimConfig` → seedable RNG
2. **Proteom** → `UP000326712` (TSV) → AlphaFold v6→v4→v3 → PDB → `(Rg, Rs, V_ex, pLDDT)`
3. **Reaktionen** → 20 Komplexe aus 4DWCM-Tabelle S2; kinetische Konstanten teils 4DWCM/syn3A-Parametersatz (Quellen-Label MGENITALIUM), teils HYPOTHESE
4. **Solver-Aufbau** → `RDMEAdapter` (Gillespie-SSA, optional crowding-aware), `ODEAdapter` (RK45), `ChromosomeAdapter` (Verlet + optional Riemann-Mannigfaltigkeit)
5. **Treiber-Loop** → RDME-Schritte + ODE-Sync alle `sync_interval`-Schritte + optional A-O-Brücke
6. **Analyse** → `run.csv` → `pairs.csv` + `discriminations.csv` + `summary.csv` + 4 PNGs

### Wichtige Module

- `src/cellsim/adapters/base.py` — `Protocol[Step]` mit `step(dt, rng) → dict`, `snapshot()`, `restore()`
- `src/cellsim/adapters/rdme.py` — Gillespie-SSA-Solver; `state.voxels[species_id]` als `np.ndarray[grid_shape]`; `_apply_local_diffusion` für L2-Brücke
- `src/cellsim/adapters/ode.py` — `scipy.integrate.solve_ivp` mit Glycolyse-Stub (3 Spezies)
- `src/cellsim/adapters/chromosome.py` — 1D-Bead-Spring-Verlet + optional Riemann-Mannigfaltigkeit
- `src/cellsim/modules/reactions.py` — `default_registry()` liefert 26 Spezies + 20 Reaktionen (MGENITALIUM+HYPOTHESE-Mix)
- `src/cellsim/modules/crowding.py` — `CrowdingField` mit `D_local = D_bulk · exp(-α · crowding_index)`
- `src/cellsim/modules/asakura_oosawa.py` — A-O-Depletion-Potenzial + lokal variierender D (L2↔L3-Brücke)
- `src/cellsim/modules/riemann.py` — Riemann-Mannigfaltigkeit für DNA-Konfigurationsraum (L4)
- `src/cellsim/driver/loop.py` — `HybridDriver.run()` → `DriverResult`
- `src/cellsim/analysis/pipeline.py` — `run_analysis(result, out_dir)` → 4 CSVs + manifest.json
- `src/cellsim/audit/__init__.py` — `audit_claim(claim, layer)` → `AuditReport` mit 10 Via-Negativa-Tests + Grade A-F
- `src/cellsim/benchmarks/ququint_vs_qubit.py` — V-Ladder-Benchmark Qubit/Qutrit/QuQuint

## Konventionen (aus MT_Sim)

- Adapter-Pattern mit `Protocol[Step]`
- Konfiguration in `configs/{default,smoke,brenda_kinetics}.yaml` + dataclass-Defaults
- `_mean`/`_sem`-Suffix in Metrik-Spalten
- tqdm-Fallback: `try: from tqdm import tqdm; except: def tqdm(x): return x`
- Seed-Konvention: `base_seed + run_idx * 1024 + cond_idx`
- `pathlib.Path` + `--out-dir` — keine relativen Pfade
- `logging` mit `dictConfig`, **kein** `print()` im Code (außer CLI)
- `ruff check src/` als Lint-Gate (clean)

## Bekannte Limitierungen

Siehe **LIMITATIONS.md** für detaillierte CellsimMixMind-Audit-Tabelle.

- **Rosen-Horizont** (`core/constants.py:ROSEN_HORIZON`): L3 ist reduktionistisch (`AnA`); für eine vollständige Zellsimulation ist L1/MES erforderlich.
- **Kein GPU**, keine Lattice-Microbes-Kopplung — eigene Python-Gillespie-SSA.
- **Kinetische Konstanten**: 16/20 aus 4DWCM/syn3A-Parametersatz (Quellen-Label MGENITALIUM), 4/20 HYPOTHESE — JCVI-syn3A-spezifische Kalibrierung wäre eigenes Forschungsprojekt. (CORREKTUR 2026-09-21: ältere Zählungen "6 BRENDA + 15 HYPOTHESE" bezogen sich auf einen früheren Registry-Stand; iter-20-Zensus: 26 Spezies, 20 Reaktionen.)
- **105-min-Vollzyklus nicht in Scope** — Smoke-Test läuft 60 s.
- **QuQuint-Vorteil konservativ repliziert** (1.1×–1.3×, nicht die 1000× aus Architekturtext).
- **mypy-Inkompat** mit numpy-stubs auf Python 3.14 (bekannter Bug); ruff ist die primäre Lint-Schiene.

## Eingebundene Repos (Referenz)

- `/run/media/julian/ML4/riemann/` — Riemann-Nuclear-Synthesis + QuQuint-Implementierungen (L4-Material)
- `/run/media/julian/ML2/Python/MT_Sim/` — Multiscale Topological Simulation (Adapter-Pattern-Vorlage)
- `github.com/Luthey-Schulten-Lab/Minimal_Cell_4DWCM` — Referenzimplementierung (closed-source Lattice Microbes → eigener Python-Stub)

## Externe Datenquellen

- **UniProt-Proteom UP000326712** (549 entries, 455 Protein-codierend)
- **AlphaFold 2 Database** — URL-Schema: `https://alphafold.ebi.ac.uk/files/AF-{uniprot}-F1-model_v{6|4|3}.pdb`
- **AlphaFold REST-Check**: `https://www.alphafold.ebi.ac.uk/api/prediction/{uniprot}`
- **BRENDA** (https://www.brenda-enzymes.org/) — kinetische Konstanten
- **PMC9955871** — QuQuint-V-Ladder-Dekomposition (asymptotische Behauptung)

## CellsimMixMind-Audit-Status (programmatisch prüfbar)

| Modul/Vektor | Grade | Via-Negativa-Status |
|---|---|---|
| cellsim L3 (ganz) | **B** | 9/10 PASS, 1 BORDERLINE (unfalsifiable in Bezug auf Vollständigkeit) |
| Riemann-DNA (L4) | **B** | Frenet-Serret-Krümmung implementiert |
| Asakura-Oosawa (L2↔L3) | **B** | Crowding-aware Diffusion an/aus per CLI-Flag |
| QuQuint-Benchmark | **C** | gemessen 1.1×–1.3× statt behaupteter 1000× |
| BRENDA-Konstanten | **B** | 16/20 MGENITALIUM (4DWCM/syn3A) + 4/20 HYPOTHESE |
| Turing-Muster (iter-17/19) | **C** | nur künstlicher Schnakenberg-Kern; Registry-Turing-Kompetenz FALSIFIZIERT (iter-20); iter-19-Diskrimination void (Stencil-Fehler in der Registrierung), korrigierte Bande post-hoc konsistent; Schale-1-Anomalie offen (CORREKTUR-LOG in scratch/experiments/iter-19) |
| Orch-OR-Kern (iter-18) | **C** | Signatur robust, C2-Cap deklariert, syn3A-Gate OFF |
| Orch-OR-Schild (iter-21) | **C** | S=1e6 als ableitbar FALSIFIZIERT (S_max ≈ 9.9e3 vs S_need ≈ 6.1e5); Ecke stirbt bei Δm/m=1e-2 in beiden Bad-Regimen ohne Kohärenz-Kern; Überleben nur in Konfluenz (Δm/m ≲ 1.3e-3 UND ε_res ≲ 1e-6) — `modules/shielding.py` |
| Fröhlich-Stub | **C** | max. 5 % ATP-Einsparung, kontrovers |
| MES-Stub (L1) | **C** | Zustandsmaschine, keine echte MES-Theorie |
| CellsimMixMind programmatisch | **A** | 10 Via-Negativa-Tests, Grade A-F |
| Gesamt-Architektur | **B → A** | wenn alle Vektoren vollständig umgesetzt sind |

Ausführen:
- `python -m cellsim audit --claim "<text>" --layer <L1|L2|L3|L4>` (einzeln)
- `python -m cellsim self-audit --out-dir ./out/self_audit` (12 Kern-Claims)
- `cat ./out/self_audit/self_audit_report.md` (Markdown-Report)

**Letzter Selbst-Audit** (Stand 2026-09-21): 4× A, 0× B, 8× C, 0× F.
