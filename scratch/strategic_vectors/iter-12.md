# Strategic Vectors — iter-12 (Genesis-UVC-Brücke)

## Ergebnis: VECTOR_GENESIS_UVC_BRIDGE ✅ geschlossen (BRIDGE_VISIBLE, mit Vorbehalt)

Kette: Genesis.md (232 nm, explizit heuristisch) → Sutherland 2015 →
EM-Modul-Flussdichte → iter-11-Damköhler-Fenster → RDME-Photoreaktion.

### Dreifach-Befund

1. **Licht-Gedächtnis statistisch echt** (p < 0.0005, Permutationstest
   gegen H0 'ortsfreie Events'): ortsaufgelöste 232-nm-Quelle erzeugt
   +0.29 Produkt-Kontrast im Lichtbereich (H0: 0.000, p99: 0.121) —
   thermische Kontrolle mit identischem Budget: exakt 0. Die Brücke
   ist wirkungsvoll, aber absolut schwach (588 Events/600 s).
2. **Endogene Chemolumineszenz quantitativ negativ**: Popp-Faktor
   1e-5/ATP → Turnover 4.8e-9/Schritt → 0 Events in 600 s. 5 Dekaden
   unterm Sichtbarkeitsfenster. Ultraweak-Photonen: als Reaktions-
   treiber auf Zell-Zeitskalen widerlegt; als Signal-Hypothese offen.
3. **Diskretheits-Boden** (Methodik): rint-Laplace-Diffusion rundet
   O(1)-Perturbationen weg — isolierte 7 in 8ern → rint → 8 (Verbrauch
   rückgängig!), isolierte 1er → 0. Gültig nur für Counts ≳ 5/Voxel.
   Fix: stochastische Sprung-Diffusion (Binomial pro Richtung,
   massenerhaltend exakt).

## Vektoren

### VECTOR_STOCHASTIC_DIFFUSION_PRODUCTION (offen)
Sprung-Diffusion in `modules/emergence.py` neben der rint-Variante.
Tests: Massenerhalt exakt, O(1)-Counts überleben, dichtes Regime
äquivalent (D=0.15, Counts 10–150 → gleiche Metriken ±Rauschen).

### VECTOR_SPARSE_METRICS (offen)
Permutations-Statistik (H0: ortsfreie Events) für spärliche Felder.
MI/LZ sind dichte-kalibriert — iter-12 zeigte MI 0.009 trotz
p<5e-4-Signal.

### VECTOR_ENDOGEN_UVC_TIMESCALE (offen)
Endogene UVC: Turnover 5e-9/s → 1 Event/Molekül/~6.6 Jahre. Präbiotik
(akkumulativ, Jahre) vs. Zellzyklus (Minuten) — trennt die
prebiotic-Bridge von der in-vivo-Steuerungs-Hypothese quantitativ.

### VECTOR_SATURATION_MARGIN (offen, von iter-11)
Realzellen nahe am Damköhler-Sättigungs-Kollaps? Registry-k-Faktor-
Sweep Richtung Sättigung.

## Verweise

- scratch/experiments/iter-12/{uvc_bridge.py,result.json,experiment.md}
- Genesis.md (232 nm, heuristisch); Sutherland 2015; iter-11-Fenster