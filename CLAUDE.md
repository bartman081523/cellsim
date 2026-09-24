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
PYTHONPATH=src pytest -q                              # alle (249 Tests, ~11s)
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
- **Kein GPU im Produktionstack** (eigene Python-Gillespie-SSA); GPU-Operator-Port (cupy, micromamba-env `cellsim` an `/run/media/julian/ML3/micromamba`) als experimentelle Infrastruktur seit iter-24 validiert (33–34×, G1–G5) — `scratch/experiments/iter-24/gpu_operator.py`.
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
| Orch-OR-Kick (iter-22) | **C** | Kick-Kopplung energetisch entwertet in der Box (N ≤ 1e11): N* = 1.74e11 bei τ_relax = 1 ms (1.74× über Hameroff-Decke); per Event 1.6e-10 k_B·T an der Ecke; Gate braucht Schild, Energie ist bindend — `modules/kick_coupling.py` |
| Photonische Kopplung (iter-23) | **C** | PHOTONIC_CHANNEL_INERT_FOR_SYN3A: Pump-Cap Φ_cap = P_ATP/E_photon = 1.17e5/s (kollektiv-unabhängig); Burst-Lemma (N kürzt sich); Turnover am Pump-Cap 5.65e-5/s bei r=100 nm = 1.77e3× unter Damköhler-Fenster — INERT; Produktionskopplung: HybridDriver `photonic`, CLI `--superradiance`, run.csv +4 Spalten — `modules/photonic_coupling.py` |
| Damköhler-Fenster (iter-11→14→24→26) | **B** | REPLICATED_STRONG_V2: Fenster trägt unter Operator-Wechsel (einseitig drift-behaftet → beidseitig driftfrei), Gitter-Wechsel (16³→24³) und Seed-Wechsel — 8/9 DISTINCT, Ordnung 3/3, Sättigung True; K1-Messung bestätigt die 6𝒟-Kalibrierung erst für den post-iter-15-Operator (alter Operator: 3𝒟 + Drift, scheitert K1 um 20×–180×); Träger ist LZ-Entropie (corr-Kriterium feuert nie), Zellgrenzen an der 0.05-Schranke kippen; iter-26 (Feingitter): D=0.05-Kante 10 exakt bestätigt, K5 9/9 bit-identisch, aber kein zusammenhängendes Band — `scratch/experiments/iter-24`, `iter-26` |
| Sättigungs-Marge (iter-25) | **B** | SATURATION_MARGIN_MODERATE: k-Sweep Richtung Sättigung (27 Zellen, GPU) — tau-leap λ=k·dt·n linear ⇒ k·dt exakte Reparametrisierung (K4 bit-identisch 4/4), Sweep = feines Damköhler-Gitter; Metrik-Kante 10 (D=0.05) / 100 (D=0.15) / nicht lokalisiert >1e4 (D=0.45), global 10 ⇒ iter-11-Hypothese schwach getragen (1–2 Dekaden Reserve zur Metrik-Kante, 2.5–3 zur Substrat-Sperre: Events-Plateau, k-invariante Trajektorien ab k_f≈300–1000); Kante wächst mit D (Mischung trägt das Signal; Teil = Metrik-Baseline-Effekt; **KORRIGIERT durch iter-26**: Kantenfolge nicht monoton, D=0.15-Kante nicht lokalisiert ≥200); CORREKTUR: registrierte Oberenden-Regel fehlte im Code (Verdict-robust), Kontrollen per deterministischem Recovery persistiert — `scratch/experiments/iter-25` |
| Feine Kante + D-Abhängigkeit (iter-26) | **B** | EDGE_UPPER_CONFIRMED\|EDGE_NOT_LOCALIZED\|EDGE_D_NONMONOTONE: Feingitter (Faktor ≤1.55) + Anker {0.10, 0.25, 0.30}, 43 Zellen GPU; Gates K1/K2/K4a 2/2/**K5 9/9 bit-identisch zu iter-25**; D=0.05-Kante 10 exakt bestätigt (Band nicht zusammenhängend), D=0.15 nicht lokalisiert (≥200, Gitterspitze DISTINCT — iter-25-Kante 100 war Auflösungs-Artefakt), Kantenfolge über D nicht monoton (D=0.10 → 3, D=0.25 → 30); LZgrw −0.049…+0.081 straddelt ±0.05 → Rauschen vs Struktur offen, VECTOR_STOCH_CONTROL_METRIC dreifach motiviert; Events-Plateau auf allen Ankern (k_f≈300–1000) — `scratch/experiments/iter-26` |
| Seed-Budget + Rausch-Floor (iter-27) | **B** | EDGE_STATUS_CHANGED_N10\|H0_DOMINANT\|SPREAD_SYMMETRIC: n=10 Seeds (200–209), 5 Anker, 30 Zellen, 355 Läufe GPU; n=3-Regel VERBATIM + n=10-Regel NEU; Gates K1/K2/**K5' 30/30 bit-identisch**/K5'' 30/30. H0_DOMINANT: False-DISTINCT unter Kontroll-Rauschen 24.8/26.2/26.6/0.0/18.3 % — 0.05-Schwelle liegt 2–3× unter der Paar-Diff-Streuung; positionsweise Paarung + ≥2/3-Vote = Ausreißer-Detektor. D=0.15s k=200 (iter-26-Trägerin) war Rauschen → k_edge=100 lokalisiert (Band inselig); 7/22 DISTINCT-Labels kippen (≈ H0-Prädiktion); D=0.05-Inseln = Zellrauschen. SPREAD_SYMMETRIC (Ratios 0.13–0.90): Tau-leap entlastet. 17/22 gebuchte DISTINCT-Zellen innerhalb 2 SE; robust: k_edge=10 (dreifach), D=0.30 k=30, D=0.15 k=5, D=0.05 k=1 — `scratch/experiments/iter-27` |
| Signal-Reclass + Deep-Replikation (iter-28) | **B** | RECLASS_SEVERE\|SE_H0_MARGINAL\|SE_RECOVERS_NONE\|SE_RULES_DIVERGE\|DEEP_REPLICATED: Re-Buchung unter SE-Kriterium (Gap ≥ 2 SE = σ_ctrl10·√(2/3), 0 GPU, rein auf iter-26/27-per-seed-Vektoren) — **17/22 (77 %) gebuchte DISTINCT kippen, exakt die iter-27-Erwartung**; 5 Überlebende = die 5 iter-27-Tiefen-Zellen; **auch die Kante k_edge=10 (D=0.05) kippt** (0.69 SE). H0(SE) 8.7/6.6/6.5/0.2/6.4 % (in-sample, ~3–4× besser als Altschwelle, aber > 5 % auf 4 Ankern); 0/21 Recovery; Regel-Kongruenz 53 %, alle 14 Divergenzen eine Richtung (Welch-t n=10 dominiert 3-Seed-SE); t-Kandidaten: D=0.25 k=1 (t=+4.60), D=0.15 k=14 (t=−3.81), D=0.05 k=1 (t=−3.42), D=0.1-Hoch-k-Plateau (t≈2.1–2.2) — nicht out-of-sample. Teil 2 (30 GPU-Läufe): **3/3 Deep-Zellen repliziert** — D=0.1 k=3 |t|=7.91 (Zelle enger gestreut als Kontrolle), D=0.3 k=300 |t|=4.05, D=0.3 k=1000 |t|=3.96; D=0.30-Hoch-k-Kanal = robustester Befund der Damköhler-Linie (n3 + SE + out-of-sample). Smoke-Test vor Lauf → 0 Abbrüche — `scratch/experiments/iter-28` |
| T-Regel-Kalibrierung + Kandidaten-Replikation (iter-29) | **B** | T_H0_CALIBRATED\|CAND_REPLICATED_ALL\|CAND_ABS_ALL\|EXPL_NOT_REPLICATED: (a) H0 der Welch-t-Regel über 126 ungeordnete disjunkte 5/5-Splits je Anker = 0.0/4.0/4.8/0.0/5.6 % — **überall unter Nominal (8 %)**; Kontrast zur Paar-Regel (18–27 %): Seed-Paarung + Vote = Ausreißer-VERSTÄRKER, t-Statistik = Ausreißer-DÄMPFER — die mächtigere Regel ist auch die sauberere. (b) **3/3 Kandidaten strict out-of-sample repliziert** (Seeds 300–309 + frische Kontrolle): D=0.05 k=1 −3.42→−5.48, D=0.15 k=14 −3.81→−8.57, D=0.25 k=1 +4.60→**+12.06** (stärkstes Einzelsignal der Damköhler-Linie) — Promotion zu Befunden; Vorzeichen block-stabil. (c) **EXPL_NOT_REPLICATED**: D=0.10-Hoch-k-Plateau verliert Vertreterin k=30 (t 2.15→1.01) — iter-26-Diskordanz-Spalte in dritter Ebene entwertet. (d) K-C: frische Kontrollen konsistent (|z| ≤ 1.29), aber 3/4 Pools Faktor 3–6 enger — **Ausreißer-Vorkommen seed-block-abhängig**; iter-27/28-H0-Inflation teils block-getragen. Smoke-Test vor Lauf → 0 Abbrüche — `scratch/experiments/iter-29` |
| Survivor-Zensus 3. Block (iter-30) | **B** | SURV_ALL\|DEEP3_FRESH_REPLICATED\|EDGE_SIGNALS: 100 GPU-Läufe, Seeds 310–319 (disjunkt zu 200–209 UND 300–309), 4 Anker frische Kontrollen + 6 Zellen. **Alle 4 SE-Überlebenden repliziert, alle positiv** (D=0.15 k=5 t=3.17, D=0.3 k=30 t=5.55, D=0.3 k=300 t=4.70, D=0.3 k=1000 t=4.84) — D=0.30-Hoch-k-Kanal in vier Ebenen getragen; D=0.1 k=3 auf voll unabhängiger Basis |t|=6.98. **EDGE_SIGNALS**: die Kante k_edge=10 (D=0.05, an 200–209 NULL) zeigt am 3. Block ein krispes negatives Signal (t=−4.21) — iter-28-Flip bleibt Block-Buchhaltung, die Zelle ist block-fluktuierend, nicht tot. **Neuer Befund**: Effektstärken NICHT seed-block-stabil (0.69 vs 4.21 SE, dieselbe Zelle); robuster Kern = 8 Zellen, alle richtungsstabil. Gate-(c)-Redesign vor Lauf (Cross-Session-Determinismus, 3 echte Läufe) — `scratch/experiments/iter-30` |
| Fröhlich-Stub | **C** | max. 5 % ATP-Einsparung, kontrovers |
| MES-Stub (L1) | **C** | Zustandsmaschine, keine echte MES-Theorie |
| CellsimMixMind programmatisch | **A** | 10 Via-Negativa-Tests, Grade A-F |
| Gesamt-Architektur | **B → A** | wenn alle Vektoren vollständig umgesetzt sind |

Ausführen:
- `python -m cellsim audit --claim "<text>" --layer <L1|L2|L3|L4>` (einzeln)
- `python -m cellsim self-audit --out-dir ./out/self_audit` (12 Kern-Claims)
- `cat ./out/self_audit/self_audit_report.md` (Markdown-Report)

**Letzter Selbst-Audit** (Stand 2026-09-21): 4× A, 0× B, 8× C, 0× F.
