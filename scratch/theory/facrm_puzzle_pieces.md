# FACRM-Korpus (faizal-rebuttal) → Puzzle-Teile für cellsim

Quelle: `/run/media/julian/ML3/faizal-rebuttal-gitlab-2/experiments-new-grouped-13778/`
(Kontext: Gruppe 5 = biology, Gruppe 3 = psychology). Stand: 2026-09-21.

Der Korpus benutzt dieselbe Disziplin wie cellsim: Null- vs. Alternativ-
Hypothese, vorab registrierte Erfolgskriterien, Evidence Grades A–F, p-Werte.
Viele Experimente sind EHRLICH FALSIFIZIERT — der Korpus ist eine
Negativ-Wissens-Tabelle, nicht nur ein Fundus.

## Verdicts (geprüft aus den Logs)

| Experiment | Grade | Befund |
|---|---|---|
| 99_swift_hohenberg | A | Musterbildung durch Skalenselektion, 56× Varianz-Trennung |
| 204_molecular_turing | A | Chemie-Netzwerke evolvieren zu NAND (acc 1.0) |
| 205_topological_nand | A | chemisches NAND via Topologie |
| 185_genetic_resilience | A* | holographische Encodierung > seriell unter Deletion (*schwacher Null, s.u.) |
| 02_resonance_hypothesis | A* | Fenster-Matching findet Struktur in Rule 30 (*inflatierter Grade, s.u.) |
| 16_strange_loop | B | „Selbst als Insel der Ordnung", 0.49 vs 0.37 |
| 184_axolotl_regeneration | B | **FALSIFIED** — Feld-Minimierung schlechter als klassisch |
| 206_holographic_embryo | C | **FALSIFIED** (p=0.38) — spektral vs. seriell: kein Unterschied |
| 98_self_cultivating_dialectic | C | **FALSIFIED** — Law/Chaos-Koevolution schlägt statisches Rauschen nicht |
| 122_topological_qualia | C | **FALSIFIED** — kein Topologie-Schutz-Vorteil |
| 81_quantum_psychopathology | C | **FALSIFIED** |

## Puzzle-Teile, die in cellsim gehen (rangiert)

### 1. Swift-Hohenberg/Turing → VECTOR_PATTERN_FORMATION (der große Teil)

iter-11/14 sagen **wann** Chemie im Fenster sichtbar wird (Damköhler-
Fenster [1e-4, 0.1]/Schritt). Sie sagen nicht, **was** sich im sichtbaren
Regime selbst organisiert. Das SH-Experiment liefert die Observablen:

- Alternative: Aktivator-Inhibitor-Kinetik mit Skalenselektion
  (Turing-Instabilität / SH-Operator (1+∇²)² wählt endliches k)
- **Doppel-Null**: (a) diffusion-only → flach; (b) mean-field-Chemie ohne
  räumliche Kopplung (fairer als der schwache random-walk-Null des Korpus)
- Observablen: spektraler Peak bei endlichem k, Muster-Varianz-Wachstum,
  Persistenz der Wellenlänge
- Brücke zum photischen Kanal: superradianter Burst-Zug am Cluster könnte
  Muster keimen/synchronisieren (licht-organisierte Chemie)

Damit wird Emergenz-Detektion von „Ereignis-Lokalisierung" (iter-12/15)
zu „selbst-organisierter Struktur" — exakt das Ziel „Emergenz-Reaktionen
sichtbar werden".

### 2. Matched-Null-Lektion (methodisch, aus den *Fehlern* des Korpus)

- **02_resonance (A, inflated)**: Rule 30 IST eine lokale deterministische
  Regel; Fenster-Matching lernt exakt f(lokal) → 1.0 ist trivial, der Null
  (Münzwurf) unfair. Lektion: Null muss **matched-capacity** sein, nicht
  ratend — dieselbe Lektion wie iter-14 (gematchte Kontrollen).
- **185_resilience (A, schwacher Null)**: Null-Stichproben bimodal
  0.09–0.93 — die 1.0 der Alternative kann an der fragilen Implementierung
  des Nulls liegen.
- **SH-Null schwach**: gedämpftes Rauschen statt diffusion-only UND
  mean-field — unsere Version braucht den Doppel-Null.

### 3. Do-not-import-Liste (aus den FALSIFIED-Ergebnissen)

- Feld-Minimierung als Morphogenese-Mechanismus (184 falsifiziert)
- „Holographische" Morphogenese-Robustheit (206: kein Unterschied)
- Quanten-Psychopathologie-Qubit-Charaktere (81 falsifiziert)
- Topologie-Schutz ohne matched thermischen Null (122 falsifiziert —
  **Warnung für L4/Riemann**: topologische Robustheits-Claims müssen
  gegen gematchtes thermisches Rauschen geprüft werden)

### 4. Optional, niedrige Priorität

- VECTOR_CHEM_COMPUTATION: hat das 21-Reaktionen-Registry Rechen-Kapazität?
  (204/205, Grade A — aber FACRM-Implementierung ist evolutionäre Spielzeug-
  Suche, nicht unsere Physik; nur die *Frage* ist übertragbar)

## Verweise

- cellsim iter-11/14 (Fenster), iter-12/15 (Licht-Gedächtnis/Superradianz),
  scratch/strategic_vectors/iter-16.md (offene Vektoren)
- FACRM-Framework: parent dir `facrm.py` (Grades A–F, Null/Alternative,
  pre-registered success criteria)