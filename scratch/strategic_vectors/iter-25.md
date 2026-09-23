# iter-25 — VECTOR_SATURATION_MARGIN

**Verdict: SATURATION_MARGIN_MODERATE · Grade: B · Status: abgeschlossen (2026-09-23)**

## Frage

iter-11/14: „Realzellen betreiben hohe Enzymdichte → nahe am
Sättigungs-Kollaps?" — bei welchem k-Faktor (alle Registry-k × k_f)
verliert das Damköhler-Fenster seine Präsenz, und wie weit ist das
nominale Regime (k_f=1) von dieser Kante entfernt?

## Design

iter-24-Harness VERBATIM auf GPU; k_f-Sweep {1…1e4} (3/Dezade) bei
dt=1e-5, Anker D ∈ {0.05, 0.15, 0.45}, Seeds {200,201,202} (= iter-24
R1). Struktureller Kern: tau-leap λ = k·dt·n ist linear → (k_f, dt) ist
EXAKTE Reparametrisierung von (1, k_f·dt) — der Sweep ist ein feines
Damköhler-Gitter; K4 verifiziert die Äquivalenz bit-genau.

## Resultat

- **K1/K2 PASS** (Operator-Kalibrierung identisch zu iter-24;
  bit-reproduzierbar) · **K4 EQUIVALENT** (4/4 Paare bit-identisch)
- Kanten: D=0.05 → k_f 10; D=0.15 → 100; D=0.45 → nicht lokalisiert
  (Oberende 1e4 selbst DISTINCT). Globale Kante = min = **10**.
- **Events-Plateau** (Substrat-Sperre, zweiter Rand): ab k_f≈300
  (D≤0.15) bzw. ≈1000 (D=0.45) werden Trajektorien k-invariant
  (identische Events, identische Metriken) — substrat-limitiert.
- **K5 2/3**: D=0.45 k=1 grenzwertig NULL auf GPU (iter-24: DISTINCT).

## Lesung

- **MODERATE** (Band 10 ≤ Kante < 100; exakt an der NARROW-Grenze):
  iter-11-Hypothese schwach getragen — das nominale Regime liegt
  1–2 Dekaden unter der Metrik-Kante, 2.5–3 Dekaden unter der harten
  Substrat-Sperre. Die Metrik-Kante VORAUS der Sättigung; am Plateau
  bleibt D=0.45 DISTINCT (Kontroll-LZ dreht dort negativ), D≤0.15 NULL.
- Kante wächst mit D (10 → 100 → >1e4); Teil davon ist
  Metrik-Baseline-Effekt (Kontroll-LZ-Vorzeichenwechsel).
- **Nicht behauptet**: reale syn3A-Enzymdichten (Registry-k sind
  MGENITALIUM/HYPOTHESE); Marge gilt für DIESES Registry-Subset + Metrik.
- corr feuert im 4. Lauf in Folge nie — LZ-Entropie-Trägerschaft
  weiter bestätigt.

## CORREKTUR-LOG (Kurzfassung; voll in experiment.md)

1. assess_margin implementiert die registrierte Oberenden-Regel nicht
   (D=0.45 fälschlich localized=true) — Verdict unter beiden Lesungen
   identisch (MODERATE); zusätzlicher ABSENT-Zweig unregistriert
   (toter Zweig).
2. Kontroll-Baselines nicht persistiert → deterministischer
   Recovery-Lauf (`recover_controls.py`), kein neuer Befund.
3. Interim-Remark „Kante 10 → NARROW" korrigiert (10.0 liegt in
   MODERATE; Registrierung bindend).
4. Lauf 1 extern gestoppt (EINTR, Nutzerschicht; kein Systemfehler) —
   Teillog erhalten, nichts gebucht; Lauf 2 komplett.

## Nächste Vektoren

1. Feiner Sweep um die Kante (10–30) + D-Abhängigkeit der Kante
2. VECTOR_STOCH_CONTROL_METRIC (doppelt motiviert: Baseline-Effekt)
3. VECTOR_ENDOGEN_UVC_TIMESCALE (offen, iter-12/13)
4. reserviert iter-19b: VECTOR_SHELL1_CASCADE

Artefakte: `scratch/experiments/iter-25/{saturation_margin.py,
result.json,run_log.txt,run_log_interrupted.txt,recover_controls.py,
controls_recovery.json,experiment.md}`