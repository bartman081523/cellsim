# iter-19 — VECTOR_TURING_PROSPECTIVE

**Status**: ABGESCHLOSSEN (2026-09-21) · **Verdict**: BAND_SHIFTED_CONTINUOUS (mechanisch) — **Interpretation VOID (Registrierungsfehler)** · **Grade**: C · **Ergebnisse**: `scratch/experiments/iter-19/`

## Was der Vektor wollte

iter-17 (L=24) bestätigte Turing-Muster am künstlichen Schnakenberg-Kern,
konnte aber die zwei Linearisierungen nicht diskriminieren (Schale 0.293
existiert auf L=24 nicht). iter-19 testete prospektiv auf L=48:
exakte diskrete Abbildung (registrierte Bande [0.1038, 0.2696], Schale
0.293 stabil) gegen kontinuierliches Symbol (Bande [0.186, 0.456], Peak
0.293). P1–P5-Kriterien vor dem Lauf fixiert; 7 Konfigurationen
(Onset-Bracket, turing3/10, null3/10, L=24-Anker), base_seed 300, T bis
1600 Schritte.

## Ergebnis

**Mechanisches Verdict nach Registrierung: BAND_SHIFTED_CONTINUOUS**
(P1 ✓ 14527×, P2 ✗ out-high 3622×@800 / 6852×@1600, P3 ✓ 0.0073,
P4 ✓ 0.262, P5 ✓ Drift ≤ 1.2 %).

**Nachlauf-Korrektur (CORREKTUR-LOG B): die Diskrimination war void.**
Die registrierte exakte Abbildung hatte einen Stencil-Fehler
(`eig_max_step` setzte die RADIALE Wellenzahl auf alle drei Achsen —
das ist der Diagonalmodus-(k,k,k)-Multiplikator, nicht der einer Modus
(k,0,0)). In radialen Einheiten (×√3) liegt die registrierte Bande
[0.180, 0.467] praktisch auf dem kontinuierlichen Symbol [0.186, 0.456];
D_v=10 analog ([0.0927, 0.4927] vs [0.094, 0.490]). Die "Rivalität" war
ein Einheiten-Artefakt — falsifiziert wurde die fehlerhafte Registrierung,
nicht die exakte Abbildung.

**Korrigierte modus-aufgelöste Analyse (POST-HOC, keine Bestätigung):**
exakt ≈ kontinuierlich (Differenz +0.0006/Schritt überall), korrigierte
Bande [0.1851, 0.4534] ≈ [0.186, 0.456]; gemessene Früh-Raten (Power/2)
decken Peak-Lage und Feinstruktur innerhalb des Baseline-Bias (z. B.
Schale 0.41394: +0.00227 vorhergesagt, +0.00222 gemessen).

**Neue Anomalie (falsifizierbarer Zielvektor):** Schale 0.131 wächst
(+0.0022 Amplitude; in der Banden-Summe 14527× über null3), obwohl beide
korrigierten Analysen Abkling vorhersagen (−0.0105). Hauptkandidat:
Differenz-Kaskade aus der aktiven Bande ((2,1,0)−(1,1,0) → (1,0,0),
Quellen-Power-Rate ≈ +0.011/Schritt); OP-Drift-Quickcheck (v→0.80)
lässt die Schale stabil. → iter-19b-Kandidat VECTOR_SHELL1_CASCADE.

## Was prospektiv bleibt

Onset-Bracket (0.25/1.0 flach, 3.0 wächst), Banden-Verallgemeinerung
D_v=10 (586×), Bilanz (std_x ×24 bei Drift 0.08 %), nichtlineares Regime
(Sättigung ~5250×@1000–1200, Abkling, mean_y 520 → 319). Alles
verhältnis-/fensterbasiert, vom Stencil-Fehler unberührt.

## Konsequenz (offen bleibt)

- Musterbildung bleibt auf den künstlichen Kern beschränkt (iter-20:
  Registry trägt kein Turing-Substrat) — jetzt mit korrigierter,
  modus-aufgelöster Diskretisierungs-Theorie als Basis für künftige
  Registrierungen (`mode_correction.py::exact_rate_mode`).
- Die Diskretisierungs-"Rivalität" exakte Abbildung vs kontinuierliches
  Symbol ist für diesen Kern KEINE relevante Diskrimination mehr — der
  Splitting-Fehler O(dt·D·c) ist bei dt=0.05 klein; beide treffen die
  Bande. Interessanter ist die Schale-1-Anomalie (nichtlineare Kopplung).
- Post-hoc-Konsistenz der korrigierten Bande mit den Daten ist
  hypothese-generierend, nicht bestätigend.

## Lektion (epistemisch)

Eine Vorab-Registrierung prüft nur Selbstkonsistenz
(`verify_registration()` reproduzierte die fehlerhafte Formel exakt).
Registrierte Zahlen sind keine Garantie für die RICHTIGE Abbildung —
der Fehler (Diagonalmodus-Stencil) überlebte die Registrierungs-Integrität,
weil die Integrität dieselbe Formel benutzte. Abhilfe für künftige
Vektoren: die registrierte Abbildung gegen eine UNABHÄNGIGE zweite
Herleitung (hier: per-Modus-Produktformel) oder gegen den
Produktions-Code (`emergence.py::stochastic_jump_diffusion`) ableiten,
nicht gegen sich selbst.