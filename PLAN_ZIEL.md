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

## Status (Stand 2026-08-21, nach Initial-Commit)

| Bereich | Status | Datei/Modul |
|---|---|---|
| **Biochemie (RDME/ODE)** | ✅ L3 implementiert | `adapters/rdme.py`, `adapters/ode.py` |
| **Thermodynamik (Crowding)** | ✅ L2-Brücke | `modules/asakura_oosawa.py` |
| **DNA-Geometrie** | ✅ L4 (Riemann) | `modules/riemann.py` |
| **EM-Schicht** (Photonen) | ✅ Iter-1 (EM + Chemolumineszenz) | `modules/em.py`, `scratch/experiments/iter-1/` |
| **UV-Synchronisation** | ✅ Iter-2 (STRONG, aber verdächtig) | `scratch/experiments/iter-2/` |
| **QuQuint-VQE-Beschleunigung** | ⚠️ nur Benchmark | `benchmarks/ququint_vs_qubit.py` |
| **Elektronen (QM-Orbitale)** | ❌ fehlt | — |
| **Schwache/starke Kraft** | ❌ fehlt (nicht relevant für Zelle) | — |
| **Gravitation** | ❌ fehlt (vernachlässigbar) | — |
| **Penrose-Hameroff Orch-OR** | ❌ fehlt | — |
| **Mikrotubuli-Fröhlich-Kopplung** | ⚠️ Stub (REFUTED_BY_REIMERS_2010) | `modules/frohlich.py` |
| **Radikal-Paar-Magnetorezeption** | ❌ fehlt (iter-3 offen) | — |

## Forschungs-Methodik

Wir arbeiten **ergebnisoffen** in Iterations-Schleifen:

1. **Hypothese** in `scratch/experiments/iter-N/experiment.md`
2. **Code** in `scratch/experiments/iter-N/*.py`
3. **Result** als JSON mit Signal (STRONG/WEAK/NULL/CONTRADICTION)
4. **Strategische Vektoren** in `scratch/strategic_vectors/iter-N.md`
5. **Bei STRONG**: Übernahme in Production-Code + nächster Iter
6. **Bei WEAK/NULL**: Retry oder Pivot
7. **Bei CONTRADICTION**: Widerlegungs-Bericht + Retirement

## Geplante Iterationen

### Phase A: EM-Schicht (laufend)

- ✅ **iter-1**: EM-Schicht + Chemolumineszenz (STRONG, in Production)
- ✅ **iter-2**: UV-Synchronisation 2 Zellen (STRONG, verdächtig)
- **iter-2-retry**: schwache Kopplung, echt Distanz-abhängige Korrelation
- **iter-3**: Radikal-Paar-Magnetorezeption (Cryptochrom, Schulten)
- **iter-4**: N>2 Zellen → populations-Synchronisation (Popp's "biocoherent")

### Phase B: QM-Elektronen

- **iter-5**: Elektronenorbitale in Schlüssel-Enzymen (ATP-Synthase)
- **iter-6**: Protonen-Tunneling in enzymatischer Katalyse (MCF, AARS)
- **iter-7**: QuQuint-VQE-Beschleunigung für Hamiltonian-Diagonalisierung

### Phase C: Mikrotubuli & Bewusstsein

- **iter-8**: Mikrotubuli-Modell mit Fröhlich-Stub (REFUTED-Status beibehalten)
- **iter-9**: Penrose-Hameroff Orch-OR als Test-Hypothese
- **iter-10**: Kritische Analyse: was bleibt empirisch übrig?

### Phase D: Integration

- **iter-11**: Alle Schichten in einer einzigen Zelle-Simulation
- **iter-12**: N=10 Zellen-Population mit UV-Kopplung
- **iter-13**: Vergleich gegen reale FCS-Daten aus Budiman et al.

## Quellordner, die wir konsultieren

| Ordner | Inhalt |
|---|---|
| `/run/media/julian/ML4/riemann/` | Riemann-Nuclear-Synthesis, QuQuint-VQE, Latore-Tension |
| `/run/media/julian/ML2/Python/MT_Sim/` | Multiscale Topological Simulation, Emergenz |
| `/run/media/julian/ML3/faizal-rebuttal-gitlab-2/experiments-new-grouped-13778/` | TCI/TRI-Rebuttal, kategorische Theorie |
| `/run/media/julian/ML3/faizal-rebuttal-gitlab/` | ältere Rebuttal-Version |
| `/run/media/julian/ML3/faizal-rebuttal/` | Original-Material |

## Constraints (bleiben gültig)

- Kein Lattice-Microbes (closed-source) → eigene Python-Solver mit numba-JIT
- Keine GPU-Anforderungen (CUDA-Skelett als Vorlage)
- Keine relative Pfade
- Keine 1000×-Behauptungen ohne Replikation (Via-Negativa-Disziplin)
- **Keine vagen 5%-Effekte ohne Quellenangabe**

## Aktuelle Aufgabe

**Selbst-Iteration**: iter-2-retry mit schwacher Kopplung, um zu prüfen,
ob die Synchronisation realistisch ist.

## Verweise

- CellsimMixMind-JsonMind: `/run/media/julian/ML3/prompts-bartman/prompts/universal/CellsimMixMind_v1.0_20260820_cellsim.json.txt`
- scratch/-Workflow: `scratch/README.md`
- Letzter Commit: siehe `git log --oneline`
