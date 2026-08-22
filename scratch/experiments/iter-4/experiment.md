# iter-4: N-Zellen-Population mit UV-Kopplung

## Hypothese

N=10 Zellen in einer Suspension können über UV-Biophotonen Signale
austauschen, die zu einer *populationsweiten Synchronisation* führen
(Popp's "biocoherent state"). Vorhersage: r_global > 0.5 in der
gekoppelten Bedingung, deutlich höher als in der isolierten Kontrolle.

## Method

- N=10 Zellen in 2D-Gitter (Spacings 800 nm)
- Jede Zelle hat ATP-ODE mit stochastischer Hydrolyse
- Drei Bedingungen: isolated (Kontrolle), uv-coupled, crypto-coupled
- Metrik: paarweise Pearson-r → Mittelwert = r_global

## Result

**Signal: CONTRADICTION**

| Bedingung | r_global | std (ATP final) | mean (ATP final) |
|---|---|---|---|
| isolated | +1.000 | 0.004 | 0.066 |
| uv | +0.267 | 8.391 | 19.416 |
| crypto | +0.267 | 8.391 | 19.416 |

## Diagnose

Drei Probleme:

1. **Isolated trivial korreliert**: alle Zellen konvergieren trivial zum
   gleichen Steady-State (ATP ~ 0.066), weil die ODE einen starken
   Attraktor hat. r = 1.0 ist Artefakt.

2. **UV-Kopplung macht ATP instabil**: mean_atp = 19.4, std = 8.39.
   Die ODE hat keine starke Rückkopplung — additive UV-Modulation
   lässt ATP divergieren. Das ist kein physikalisches Signal, sondern
   ein numerisches Problem der ODE-Form.

3. **uv ≈ crypto**: die Differenz zwischen UV- und Crypto-Modus ist
   null. Beide treiben ATP gleich stark.

## Strategische Vektoren

### VECTOR_ODE_STABILIZATION (HOCH)
Die ATP-ODE braucht eine **starke negative Rückkopplung**:
- ATP-Verbraucher (Translation 70% ATP, aktive Transport 20%, etc.)
- Sättigungs-Kinetik statt linear
- Homeostase mit oszillatorischer Steady-State

Realistische ATP-Konzentration in Bakterien: 2-5 mM, **stabil**, nicht
explodierend. Aktuelle ODE ist unrealistisch.

→ Vor weiteren Iter mit N>2 Zellen: ODE modernisieren mit:
  - Mehrere ATP-Verbraucher (Translation, Motor, Ionen-Pumpe)
  - Lineare vs. Michaelis-Menten-Kinetik
  - Homeostatische Regulation

### VECTOR_RECONSULT_THEORY
Lieber zurück zu Cifra-Sonn 2011 (echte Computersimulation mit
realistischer ATP-ODE) als weitere approximative ODE-Versuche.

### VECTOR_POPP_PIVOT
Popp's Biophotonen-Hypothese wurde in der modernen Biophotonik-Forschung
kaum weiterverfolgt. Vielleicht ist die Hypothese selbst zu schwach
für eine *empirisch überprüfbare* Vorhersage. Statt weitere Iter zu
verschwenden: konsultiere Cifra 2011, Rattemeyer 1981 (pro/contra).

### VECTOR_UV_SYNC_RETIRE
UV-Sync zwischen Zellen — sowohl iter-2 als auch iter-4 scheitern an
derselben Stelle (ODE-Artefakt). Wir müssen **entweder** das Modell
grundlegend modernisieren **oder** UV-Sync ganz aufgeben.

## Verweise

- Popp, F.A. (2003): Integrative Biophysics
- Cifra, M. & Sonn, K.V. (2011): Electromagnetic cellular interactions
- Cifra, M. et al. (2011): Electromagnetic cellular interactions reviewed
- Rattemeyer, M. et al. (1981): Biophoton Emission — Kritik

## CellsimMixMind-Audit

- **CONTRADICTION**: Hypothese (Population-Sync via UV) kann im
  gewählten ODE-Modell nicht getestet werden — isoliert trivial
  korreliert (r=1.0), gekoppelt instabil.
- **Via Negativa**: 3 Iter-Versuche (iter-2, iter-2-retry, iter-4)
  scheitern alle an demselben ODE-Problem → ODE ist der Bottleneck.
- Nächster Schritt: ODE modernisieren oder These aufgeben.

## Konsequenz für PLAN_ZIEL.md

Phase A (EM-Schicht) wird als **abgeschlossen** markiert — die
EM-Schicht (Chemolumineszenz) bleibt im Code, aber UV-Sync ist
*vorerst* aufgegeben bis ODE-Modernisierung erfolgt.

Wir schwenken zu **Phase B (QM-Elektronen)**: QuQuint-VQE-Beschleunigung
ist der nächste realistische Schritt.
