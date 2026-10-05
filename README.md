# cellsim — JCVI-syn3A-Simulator (L3 + L2-Brücke + L4 + Audit)

Python-Implementierung der **L3-Schicht** der 4-Schichten-Zellsimulations-Architektur
(siehe `Forschung Zur Vollständigen, Numerischen Und Modul....md`).
Plus **L2↔L3-Brücke** (Asakura-Oosawa-Depletion) und **L4** (Riemann-Geometrie + QuQuint-Benchmark).

## Schnellstart

```bash
# 1. Installation
pip install --user --break-system-packages -e .

# 2. Daten-Cache (UniProt-Proteom + AlphaFold-Volumina)
PYTHONPATH=src python -m cellsim cache build --out-dir ./out

# 3. Smoke-Simulation (60 s sim, deterministisch)
PYTHONPATH=src python -m cellsim simulate --t-end-s 60 --out-dir ./out/smoke
# Mit L2-Brücke (crowding-aware Diffusion):
PYTHONPATH=src python -m cellsim simulate --t-end-s 60 --local-diffusion --out-dir ./out/smoke_ao

# 4. QuQuint-Benchmark (L4)
PYTHONPATH=src python -m cellsim benchmark --out-dir ./out/benchmark

# 5. CellsimMixMind-Audit einer Behauptung
PYTHONPATH=src python -m cellsim audit --claim "..." --layer L4

# 6. Inspektion
PYTHONPATH=src python -m cellsim cache inspect --out-dir ./out
```

## Befehle

| Befehl | Zweck |
|---|---|
| `cache build` | Lädt JCVI-syn3A-Proteom + AlphaFold-PDBs, schreibt `volumes.tsv` |
| `cache inspect` | Statistiken über die Volumen-Tabelle |
| `simulate` | Führt die L3-Smoke-Simulation aus |
| `simulate --local-diffusion` | Wie simulate, aber mit A-O-Brücke |
| `benchmark` | QuQuint-V-Ladder-Benchmark (Qubit/Qutrit/QuQuint) |
| `audit` | CellsimMixMind-Audit einer Behauptung (Grade A-F) |
| `seed` | Zeigt den effektiven Seed für (base, run, cond) |

## Smoke-Output

Nach `python -m cellsim simulate --out-dir ./out/smoke` enthält das Verzeichnis:
- `run.csv` (Zeitreihen), `pairs.csv`, `discriminations.csv`, `summary.csv` (mit `_mean`/`_sem`)
- `manifest.json` (Seed + SHA256 + Walltime)
- 4 PNGs: Radius/ATP/Crowding-Proxy/Sync-Ticks

## Audit-Output

```
$ python -m cellsim audit --claim "QuQuint reduces Grover gate count by 1000x." --layer L4
Grade: C
Rationale: 9/10 PASS, 1/10 BORDERLINE, 0/10 FAIL
Via-Negativa: ...
```

## Architektur

```
src/cellsim/
├── core/          # Konstanten, Einheiten, Zeitachsen, RNG (single source of truth)
├── data/          # UniProt + AlphaFold-PDBs + BRENDA + volumes.tsv-Loader
├── adapters/      # Protocol[Step] — RDME/Gillespie, ODE/scipy, Chromosom/Bead-Spring+Riemann
├── modules/       # Membrane, Reaktionen, Crowding, Asakura-Oosawa, Riemann
├── driver/        # HybridDriver
├── analysis/      # Pipeline (4 CSVs), Metrics, Plots
├── audit/         # CellsimMixMind-Audit programmatisch
├── benchmarks/    # QuQuint-V-Ladder-Benchmark (L4)
└── cli/           # Typer-CLI
```

## Tests

```bash
PYTHONPATH=src pytest                              # alle (84 Tests)
PYTHONPATH=src pytest tests/unit/                  # nur Unit
PYTHONPATH=src pytest tests/integration/           # nur Integration
PYTHONPATH=src pytest -m smoke                     # nur Smoke
ruff check src/                                    # Lint (clean)
```

## Bekannte Limitierungen

Siehe **LIMITATIONS.md** für detaillierte CellsimMixMind-Audit-Tabelle.

- **Rosen-Horizont**: L3 ist reduktionistisch (`AnA`), nicht synthetisch (`SynA`).
- **Kein GPU**, keine Lattice-Microbes-Kopplung.
- **Kinetische Konstanten**: 6 BRENDA-extrahiert (E. coli), 15 HYPOTHESE.
- **QuQuint-Vorteil konservativ repliziert** (1.1×–1.3×, nicht die 1000× aus Architekturtext).
- **105-min-Vollzyklus nicht in Scope** — Smoke-Test läuft 60 s.

## Experiment-Linie tci_* — Rohdaten als Git LFS

Seit Roh-Commit `11949ec` (2026-10-05) sind die Per-Seed-Rohdaten der
TCI-Wirbel-Experimente öffentlich via Git LFS verfügbar:

- `scratch/experiments/tci_v2/per_seed/**` — 130 Trial-JSONs
- `scratch/experiments/tci_v3/per_seed/**` — 160
- `scratch/experiments/tci_v4/per_seed/**` — 160

Integrität: SHA-256 je Datei plus Manifest-Hash in den jeweiligen
`per_seed_manifest.json` (v2 `8a305f27efd278a1…`, v3
`5b0170d25588aa74…`, v4 `ab0988d5d5aae79c…`); ~792 von 1024 MB der
GitHub-LFS-Quota (free tier) sind damit belegt.

Bewusst NICHT im Repo: das Xu-Supplement (`scratch/experiments/tci_xu/
data/`, 17 Source-Data-xlsx, Drittanbieter-Daten — Download-Pattern im
Docstring von `xu_data_analysis.py`), Paper-PDFs, `neuro_vortices.txt`.

Quelle der Linie: Xu, Y., Long, X., Feng, J. & Gong, P. (2023),
„Interacting spiral wave patterns underlie complex brain dynamics and
are related to cognitive processing", Nature Human Behaviour 7,
1196–1215, DOI 10.1038/s41562-023-01626-5; weitere Video-Papers mit
DOIs in `scratch/notes/tci_vortex_assessment.md` §10. Protokolle und
Verdicts: `scratch/experiments/tci_{xu,v2,v3,v4}/experiment.md`;
Formel-Kette: `scratch/notes/tci_hylothese_formulas.md`.
