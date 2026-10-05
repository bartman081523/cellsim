# PLAN: physikalisch korrekte Zellsimulation über alle Bereiche

## Ziel

Eine physikalisch korrekte Simulation einer JCVI-syn3A-Zelle, die
folgende Bereiche umfasst:

1. **Elektronen** — quantenmechanische Orbitale, Übergänge, Tunnel-Effekte
2. **Photonen** — UV/Vis/IR-Emission, Absorption, Biophotonen
3. **Alle Kräfte** — elektromagnetisch, schwach, stark (im Kern), Gravitation
4. **UV-Phasen-Synchronisation zwischen Zellen** — Popp/Cifra
5. **Bewusstsein über UV-Licht** — Penrose-Hameroff Orch-OR
6. **Beschleunigung durch QuQuint** — d=5 Qudit-VQE für RDME-Raten
7. **Radikal-Paar-Spin-Dynamik** — Cryptochrom-Magnetorezeption
8. **Mikrotubuli** — Fröhlich-Kohärenz (kontrovers!)

## Status (Stand 2026-08-22, nach 3 Commits)

| Bereich | Status | Datei/Modul | Evidence |
|---|---|---|---|
| **Biochemie (RDME/ODE)** | ✅ L3 | `adapters/rdme.py`, `adapters/ode.py` | Smoke grün |
| **L2-Brücke A-O** | ✅ | `modules/asakura_oosawa.py` | Crowding-aware Diffusion |
| **L4 Riemann-Geometrie** | ✅ | `modules/riemann.py` | 7 Tests |
| **EM-Schicht + Chemolumineszenz** | ✅ | `modules/em.py` | iter-1 STRONG |
| **Cryptochrom Magnetorezeption** | ✅ | `modules/cryptochrome.py` | iter-3 STRONG |
| **UV-Sync zwischen Zellen** | ⚠️ CONTRADICTION | `scratch/experiments/iter-2/` | r ≈ 1.0 Artefakt |
| **QuQuint-VQE-Beschleunigung** | ⚠️ nur Benchmark | `benchmarks/ququint_vs_qubit.py` | 1.1×–1.3× |
| **L1/MES-Kolimit** | ⚠️ Stub | `modules/mes.py` | Zustandsmaschine + Sub-Network-Reparatur |
| **Fröhlich-Kohärenz** | ⚠️ REFUTED_BY_REIMERS_2010 | `modules/frohlich.py` | max 0.1% |
| **Elektronen (QM-Orbitale)** | ❌ | — | iter-4 offen |
| **Penrose-Hameroff Orch-OR** | ❌ | — | iter offen |
| **Mikrotubuli-Anisotropie** | ❌ | — | iter offen |

## Forschungs-Methodik

Wir arbeiten **ergebnisoffen** in Iterations-Schleifen:

1. **Hypothese** in `scratch/experiments/iter-N/experiment.md`
2. **Code** in `scratch/experiments/iter-N/*.py`
3. **Result** als JSON mit Signal (STRONG/WEAK/NULL/CONTRADICTION)
4. **Strategische Vektoren** in `scratch/strategic_vectors/iter-N.md`
5. **Bei STRONG**: Übernahme in Production-Code + nächster Iter
6. **Bei WEAK/NULL**: Retry oder Pivot
7. **Bei CONTRADICTION**: Widerlegungs-Bericht + Retirement (oder Modell-Upgrade)

## Iterations-Historie

| iter | Hypothese | Signal | Konsequenz |
|---|---|---|---|
| **iter-1** | EM-Schicht + Chemolumineszenz | **STRONG** | → `modules/em.py` Production |
| **iter-2** | UV-Sync zwischen 2 Zellen | STRONG (verdächtig) | r ≈ 1.0 → Retry nötig |
| **iter-2-retry** | Sweep über Kopplung + Distanz | **CONTRADICTION** | Modell zu simpel → ODE-Upgrade nötig |
| **iter-3** | Radikal-Paar Cryptochrom | **STRONG** (subtil) | → `modules/cryptochrome.py` Production |

## Geplante Iterationen

### Phase A: EM-Schicht (laufend, weitgehend abgeschlossen)

- ✅ **iter-1**: EM-Schicht + Chemolumineszenz
- ⚠️ **iter-2** (CONTRADICTION): UV-Sync — Modell-Artefakt bestätigt
- ✅ **iter-3**: Radikal-Paar Cryptochrom (Phase-B-Komponente)
- **iter-3b**: Anisotropie-Messung der Cryptochrom-Sensitivität (offen)
- ⚠️ **iter-4** (CONTRADICTION): N=10 Zellen + UV — ODE vereinfacht
- ⚠️ **iter-8** (CONTRADICTION): Realistische ATP-ODE — fundamentaler Attraktor-Befund
- **Schlussfolgerung UV-Sync**: 4× CONTRADICTION → Hypothese archiviert

### Phase B: QM-Elektronen (✅ abgeschlossen)

- ✅ **iter-5**: QuQuint-VQE-Beschleunigung (Campbell 2012, PMC9955871)
- ✅ **iter-6**: Proton-Tunneling in MCF/AARS (Kohen 1999, Nagel 2006)
- **iter-7a**: Voll-Hamiltonian für ATP-Synthase-Site (offen, nach iter-5+6)

### Phase C: Mikrotubuli & Bewusstsein (✅ numerisch falsifiziert)

- ⚠️ Fröhlich-Kohärenz: REFUTED_BY_REIMERS_2010
- ⚠️ **iter-7** (CONTRADICTION): Penrose-Hameroff Orch-OR numerisch falsifiziert
- **Schlussfolgerung QM-Bewusstsein**: alle QM-basierten Bewusstseins-Theorien numerisch ausgeschlossen

### Phase D: Integration (✅ abgeschlossen)

- ✅ **iter-9**: Integrations-Adapter in EINER Zelle (5 Module koexistieren)
- **iter-9b**: 10 integrierte Zellen mit realistischer UV-Kopplung (offen)
- **iter-9c**: Vergleich gegen reale FCS-Daten aus Budiman et al. (`data/diffusion_experimental.py`, offen)

## cellsim-Scope (final, 2026-08-27)

**9 Iterationen, 160 Tests, 10 Commits**.

cellsim ist eine **biochemisch-numerische Simulation** einer JCVI-syn3A-Zelle
mit:
- 4 Architektur-Schichten (L1/L2/L3/L4) + 4 Spezialmodule (EM, Crypto, QuQuint, Tunneling)
- 5× STRONG-Signale + 4× CONTRADICTION (UV-Sync, Orch-OR)
- Keine Bewusstseins-Behauptungen
- Bewusst als ergebnisoffene Forschungsplattform mit transparenter Via-Negativa-Disziplin

## Verweise

- CellsimMixMind-JsonMind: `/run/media/julian/ML3/prompts-bartman/prompts/universal/CellsimMixMind_v1.0_20260820_cellsim.json.txt`
- scratch/-Workflow: `scratch/README.md`
- scratch/SUMMARY.md: vollständige Iterations-Historie
- Letzte Commits: siehe `git log --oneline`
- LIMITATIONS.md (12 Vektoren dokumentiert)

## Quellordner

| Ordner | Inhalt | Relevanz für nächste Iterationen |
|---|---|---|
| `/run/media/julian/ML4/riemann/` | Riemann-Nuclear-Synthesis, QuQuint-VQE | iter-7 (QuQuint-VQE) |
| `/run/media/julian/ML2/Python/MT_Sim/` | Multiscale Topological, Emergenz | iter-3b (Anisotropie) |
| `/run/media/julian/ML3/faizal-rebuttal-gitlab-2/experiments-new-grouped-13778/` | TCI/TRI-Rebuttal | iter-10 (kritische Theorie-Analyse) |

## Constraints (bleiben gültig)

- Kein Lattice-Microbes (closed-source) → eigene Python-Solver mit numba-JIT
- Keine GPU-Anforderungen (CUDA-Skelett als Vorlage)
- Keine relative Pfade
- Keine 1000×-Behauptungen ohne Replikation (Via-Negativa-Disziplin)
- **Keine vagen 5%-Effekte ohne Quellenangabe**

## Aktuelle Aufgabe

**iter-4** (Phase A → B Übergang): JCVI-spezifische Cryptochrom-Proteine
nach genomischer Annotation. Falls vorhanden → realistische Resonanz-Berechnung.
Falls nicht → Cryptochrom als generisches UV-/B-Feld-Sensor behandeln.

## Verweise

- CellsimMixMind-JsonMind: `/run/media/julian/ML3/prompts-bartman/prompts/universal/CellsimMixMind_v1.0_20260820_cellsim.json.txt`
- scratch/-Workflow: `scratch/README.md`
- Letzte Commits: siehe `git log --oneline`
- `LIMITATIONS.md` (CellsimMixMind-Status nach jeder Iter aktualisieren)

## Status-Nachtrag 2026-10-05 — TCI-Wirbel-Linie

Der Plan selbst (2026-08-22, „Aktuelle Aufgabe" iter-4) bleibt als
Geschichte stehen; seitdem liefen mehrere Linien, zuletzt die
Bewusstseins-Wirbel-Kette `tci_xu → tci_v2 → tci_v3 → tci_v4`
(Protokolle `scratch/experiments/tci_*/experiment.md`, Bewertung
`scratch/notes/tci_vortex_assessment.md`, Formel-Kette
`tci_hylothese_formulas.md`):

- **tci_xu**: Agreement-Test + Source-Data-Re-Analyse — persistenter
  Drive allein reproduziert Xu-Spiralen NICHT; die publizierten
  Phasenfelder lesen sich mit der eigenen Plaquette-Formel als
  unit-charge-Kerne (quant 1.000, max|v| exakt 1.000).
- **tci_v2 (FHN) / tci_v3 (Brusselator+Crowding)**: die Ebene-C-Kette
  ist in beiden Analoga-Medien falsifiziert (Q1 ABSENT, quant@0.9
  = 0.00; Grenzzyklus notwendig, nicht hinreichend; R1 SHIFTED —
  Crowding as schwache, systematische Nukleationsquelle).
- **tci_v4**: Hylothese-Diskriminator **R2_NULL** — Glied (iii) in der
  Instanz falsifiziert (Δacc −0.0250 vs 2·SE 0.1275, welch_p 0.714;
  gain exakt 0.0 in beiden Armen; Gas-Deskriptoren arminvariant).
- **Rohdaten**: `per_seed/` (v2/v3/v4) seit 2026-10-05 als Git LFS
  (Roh-Commit `11949ec`, SHA-256-Manifeste).

Offene Queue-Hebel: (1) das Defekt-Gas erst ins annihilations-dominierte
Regime steuern (Interaktions-Bruch als Ziel-Statistik aus erster Physik,
nicht gefittet; tci_v5, neue disjunkte Seeds ≠ 1600–1609), DANN Glied
(iii) nachtesten; (2) δ_c = 0.5 unverwertet; (3) F6 LZ-Sequenz-Features
implementieren; (4) Lizenzklärung der Xu-Supplement-Daten (bleibt lokal).

