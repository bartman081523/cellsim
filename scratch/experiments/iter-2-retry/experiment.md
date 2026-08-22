# iter-2-retry: Sweep über Kopplungsstärke

## Hypothese

Aus iter-2: r ≈ 1.0 über alle Distanzen ist verdächtig. Hier prüfen wir,
ob der Effekt mit *Kopplungsstärke* zusammenhängt oder ob er ein
Artefakt der einfachen ODE ist.

## Method

- Sweep über 6 Kopplungsstärken (1e-6 bis 1e4)
- Sweep über 3 Distanzen (500, 1000, 5000 nm)
- Stochastische ATP-ODE mit weißem Rauschen (noise_level = 5%)
- Subsample alle 10 Schritte für Korrelation
- Steady-state: nur zweite Hälfte der Zeitreihe

## Result

**Signal: CONTRADICTION**

| Kopplung | Distanz | r_steady | Diff final |
|---|---|---|---|
| 1e-6 | 500 | +1.000 | 0.009 |
| 1e-6 | 1000 | +1.000 | 0.009 |
| 1e-6 | 5000 | +1.000 | 0.009 |
| 1e-2 | 5000 | +1.000 | 0.009 |
| 1.0 | 5000 | +1.000 | 0.009 |
| 1.0 | 500 | +0.800 | 0.220 |
| 1.0 | 500 | +0.890 (bei 1e2) | 21.083 |

**Befund**: r ≈ 1.0 selbst bei Kopplung 1e-6 und Distanz 5 µm.
Das ist **nicht physikalisch** — eine 1/r²-Ausbreitung mit 5 µm
Distanz und Kopplung 1e-6 dürfte keinerlei messbaren ATP-Effekt haben.

## Diagnose

Das Problem liegt im **ATP-ODE-Modell**: Glucose → ATP mit konstantem
ATP-Pool. Bei einer einzigen ATP-Spezies und nur Glucose-Quelle
sind beide Zellen **trivial korreliert**, weil sie zum gleichen
Gleichgewicht relaxieren.

**Echte ATP-Dynamik braucht**:
- Mindestens 2 ATP-verbrauchende Prozesse (Translation + Motor)
- ATP-Synthase-Rate als Funktion des elektrochemischen Gradienten
- Zell-Zyklus (Wachstum + Teilung)
- Mehrere Glukose-Inputs (Glucose-Aufnahme als separater Prozess)

## Strategic Vectors

### VECTOR_ODE_UPGRADE
→ **iter-3-bridge**: ATP-ODE um 3+ Prozesse erweitern, dann iter-2
mit diesem realistischeren Modell wiederholen.

### VECTOR_EXPERIMENTAL_VALIDATION
→ Bevor wir weiter modellieren: gibt es experimentelle Daten für
UV-Synchronisation zwischen Bakterien? Cifra & Sonn (2011) berichten
über Pflanzen-UV-Signale — Bakterien sind unklar. Wenn keine Daten
→ "null hypothesis, hypothetisch".

### VECTOR_RADIKAL_PAAR_PRIORITY
Da UV-Sync im 2-Spezies-Modell nicht entscheidbar ist: direkt zu
Radikal-Paar-Cryptochrom übergehen (iter-3) — dort gibt es echte
experimentelle Hinweise (Ritz 2000, Maeda 2008, Wiltschko 2010).

## Verweise

- Cifra & Sonn (2011): EMF cellular interactions
- Ritz et al. (2000): A model for photoreceptor-based magnetoreception
- Maeda et al. (2008): Magnetic compass of birds

## CellsimMixMind-Audit

- **CONTRADICTION**: Hypothese (UV-Sync zwischen 2 Zellen) kann im
  gewählten Modell nicht falsifiziert werden — das Modell ist zu
  trivial. Dies ist *keine* Widerlegung der UV-Sync-Hypothese, sondern
  ein Hinweis, dass die Experiment-Architektur ungeeignet ist.
- Steelman: Modell mit konstantem ATP-Pool hat trivialerweise r ≈ 1.0
  im Steady-State — beide Zellen konvergieren zum gleichen Punkt.
- Nächster Iter: iter-3 (Radikal-Paar) bevorzugen, weil dort echte
  experimentelle Hinweise existieren.
