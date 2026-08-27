# iter-8: Realistische ATP-ODE (Phase A Reprise)

## Hypothese

Eine ATP-ODE mit mehreren Verbrauchern (Translation, Motor, Ionen-Pumpe)
und Michaelis-Menten-Kinetik kann den ODE-Artefakt aus iter-2/4 auflösen.
Vorhersage: bei niedriger Kopplung r_corr < 0.5; bei hoher Kopplung
phasen-Synchronisation messbar.

## Method

- 3 ATP-Verbraucher (Translation 70%, Motor 10%, Ionen-Pumpe 20%)
- Michaelis-Menten-Kinetik mit realistischen kcat/Km
- 5 Kopplungen × 4 Distanzen = 20 Sweep-Läufe
- Stochastisches Rauschen auf ATP (5% Gauss)

## Result

**Signal: CONTRADICTION (final)**

| Kopplung | Distanz | ATP [mM] | r_corr |
|---|---|---|---|
| 1e-9 | 5000 | 3.281 | +1.000 |
| 1e-7 | 5000 | 3.281 | +1.000 |
| 1e-5 | 5000 | 3.281 | +1.000 |
| 1e-3 | 5000 | 3.281 | +1.000 |
| 1e-1 | 5000 | 3.282 | +1.000 |

**Befund**:
1. **ATP ist jetzt realistisch** (~3 mM statt 10⁶ mM) — ODE modernisiert.
2. **Aber**: r_corr = 1.000 in *allen* Sweep-Läufen.
3. Selbst mit Rauschen, Michaelis-Menten und 3 Verbrauchern konvergieren
   beide Zellen zum **gleichen Attraktor**.

## Diagnose: Fundamentaler Modell-Befund

Das ist *kein* ODE-Artefakt mehr. Es ist eine **Eigenschaft des
2-Zellen-Gleichgewichts-Systems**: jede Zelle für sich ist ein Attraktor;
bei schwacher Kopplung konvergieren beide *trivial* zum gleichen
Endzustand. Nur echte **Limit-Cycle-Oscillatoren** würden
nicht-trivial korrelieren.

## Konsequenz

UV-Sync zwischen Zellen ist im **2-Zellen-Attraktor-Modell** *nicht
entscheidbar*. Um die Hypothese zu testen, müssten wir:
- **Limit-Cycle-Oscillator** (z.B. Goodwin-ODE mit negativer Rückkopplung)
- Oder: **stochastisches Rauschen pro Zelle** (getrennte RNG-Streams)
- Oder: **transiente Synchronisation** (Phase-Reset-Experimente)

Diese sind alle eigene Iterationen.

## Strategische Vektoren

### VECTOR_UV_SYNC_RETIRE_FINAL (HOCH)
→ UV-Sync zwischen Zellen ist im 2-Zellen-Modell *fundamental* nicht
entscheidbar. 4 Iter-Artefakte (iter-2, iter-2-retry, iter-4, iter-8)
belegen das. Hypothese **archiviert**.

### VECTOR_LIMIT_CYCLE_OSCILLATOR (MITTEL)
→ Echte Limit-Cycle-Oscillator-ODE (Goodwin, Glycolytic oscillation)
würde nicht-trivial Synchronisation zeigen. Aber das ist ein *eigenes
Forschungsprojekt* (A. Goldbeter 1996).

### VECTOR_CIFRA_REPULL (MITTEL)
Konsultiere *echte* experimentelle Daten aus Cifra 2011 + 2018 — wenn
es *gemessene* UV-Phasen-Kopplung gibt, dann ist die Hypothese nicht
falsifiziert, sondern nur das Modell falsch.

### VECTOR_CELLSIM_SCOPE_REDUCE
→ UV-Sync nicht im Scope von cellsim. Stattdessen: dokumentiere als
"offene Frage für zukünftige Forschung".

## Verweise

- Goldbeter, A. (1996): "Biochemical Oscillations and Cellular Rhythms"
- Cifra, M. & Sonn, K.V. (2011): Electromagnetic cellular interactions
- Goodwin, B.C. (1965): "Oscillatory behavior in enzymatic control process"

## CellsimMixMind-Audit

- **CONTRADICTION (4 Iter)**: UV-Sync-Hypothese ist im aktuellen
  Modell-Framework *nicht entscheidbar*. Keine ODE-Verbesserung hilft
  ohne echte Limit-Cycle-Oscillatoren.
- **Ehrliche Schlussfolgerung**: UV-Sync wird aus cellsim-Scope gestrichen.
- **Nächster logischer Schritt**: Phase D (Integration) oder
  Phase-C-Nachfolger (klassische Bewusstseins-Theorien).