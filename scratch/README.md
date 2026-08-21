# scratch/ — Ergebnisoffene Iterations-Forschung

## Zweck

Dieser Ordner ist die **empirische Forschungsschleife** der cellsim-Architektur.
Hier werden Experimente abgelegt, die *ergebnisoffen* sind — d.h. wir
erlauben dem System, uns zu widerlegen.

**Workflow**:
1. **Experiment** (`scratch/experiments/iter-N/`) — Hypothese, Code, Output
2. **Auswertung** (`scratch/results/iter-N/`) — automatische Analyse
3. **Strategische Vektoren** (`scratch/strategic_vectors/iter-N.md`) — was lernen wir?
4. **Verbesserung** — neue Solver, neue Schichten, neue Theorie
5. **Nächste Iteration** — verbessertes Experiment

## Was hier NICHT gehört

- Production-Code (gehört in `src/cellsim/`)
- Dokumentation (gehört in `CLAUDE.md`/`LIMITATIONS.md`)
- Tests (gehören in `tests/`)

## Theorien, die wir der Physik geben wollen

| Theorie | Quelle | Status in cellsim |
|---|---|---|
| Fröhlich-Kohärenz | riemann/ (REFUTED_BY_REIMERS_2010) | Stub mit 0.1% Effekt |
| Penrose-Hameroff Orch-OR | extern (noch nicht konsultiert) | nicht implementiert |
| Radikal-Paar-Mechanismus | extern (Vogel/Schulten) | nicht implementiert |
| Microtubuli-Fröhlich | extern | nicht implementiert |
| Biophotonen (UV-Synchronisation) | F.A. Popp, Cifra-Sonn | nicht implementiert |
| Zell-Zell-UV-Phasenkopplung | Cifra 2011 | nicht implementiert |
| Qubit-Mikrotubuli-Kopplung | Bandyopadhyay 2014 | nicht implementiert |

## Iterationen

| Iter | Hypothese | Status |
|---|---|---|
| 0 | Initial-Stand: L1-L4 implementiert, Lücken: EM/Photonen, UV, Orch-OR | baseline |
| 1 | EM-Schicht (Elektronen, Photonen, Maxwell) | offen |
| 2 | Biophotonen + UV-Synchronisation zwischen Zellen | offen |
| 3 | Radikal-Paar-Magnetorezeption + Flavoprotein-Spin | offen |
| 4 | QuQuint-Beschleunigung für RDME-Ratenberechnung | offen |
| 5 | Orch-OR (Penrose-Hameroff) Test gegen cellsim | offen |
| ... | ... | offen |

## Constraints

- **Kein Setup.sh**, nur `pyproject.toml`
- **Keine relativen Pfade** außerhalb von scratch/
- **Jedes Experiment hat einen** `experiment.md` mit Hypothese + Method + Result
- **Jeder Iter erzeugt eine** `strategic_vector.md` mit konkreten nächsten Schritten
- **Bei Trockenheit** (kein neues Signal in 2 Iters) → Konsultiere externe Quellordner neu
