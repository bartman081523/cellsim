# iter-26 — VECTOR_EDGE_FINE_SWEEP

**Verdict: EDGE_UPPER_CONFIRMED | EDGE_NOT_LOCALIZED | EDGE_D_NONMONOTONE · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-25 next_vectors (MODERATE): „Feiner Sweep um die Kante +
D-Abhängigkeit der Kante" — (a) exakte Kante bei D=0.05, (b) Kante bei
D=0.15 (iter-25: 100, internes NULL schon sichtbar), (c) Wachstum der
Kante mit D, (d) Zellrauschen oder Band-Struktur in der
nicht-monotonen D=0.05-Spalte.

## Design

iter-25-Harness VERBATIM auf GPU; Feingitter (Faktor-Abstand ≤ 1.55)
für die Anker D=0.05/0.15, drei neue Anker D ∈ {0.10, 0.25, 0.30} auf
Coarse-Gitter, D=0.45 aus iter-25 rechtszensiert übernommen. K5-Gate:
9 Überschneidungszellen müssen bit-identisch zu iter-25 sein
(läuferübergreifender Determinismus). Registrierte Oberenden-Regel
(iter-25-Lektion, diesmal im Code): Gitterspitze DISTINCT ⇒ Kante
nicht lokalisiert.

## Resultat

- **Gates alle PASS**: K1, K2 bit-identisch, K4a 2/2 bit-identisch,
  **K5 9/9 bit-identisch zu iter-25** — REGISTRATION_ERROR nicht
  ausgelöst.
- **V1a (D=0.05): EDGE_UPPER_CONFIRMED** — k_edge = 10 exakt wie
  iter-25, OBERKANTE_KLAR; aber band_connected = FALSE (interne NULLs
  bei 3/5/7): Kante als größtes-DISTINCT-k_f ja, als Region nein.
- **V1b (D=0.15): EDGE_NOT_LOCALIZED** — DISTINCT bis zur Gitterspitze
  200; iter-25s „Kante 100" war ein Gitterauflösungs-Artefakt
  (interne NULLs 10/14/45/140).
- **V2: EDGE_D_NONMONOTONE** — vier der fünf benachbarten
  D-Paare verletzen die registrierte Intervall-Konsistenz
  (D=0.10: Kante 3, unter D=0.05: 10; D=0.25: 30, unter D=0.15: ≥ 200).
- **LZgrw −0.049…+0.081 straddelt die ±0.05-Schwelle**; 4/5 Anker mit
  internen NULLs (Zellflips zwischen benachbarten k_f).
- Events-Plateau (Substrat-Sperre) auf allen Ankern: k-invariante
  Trajektorien ab k_f ≈ 300–1000.

## Lesung

- **Robust**: die D=0.05-Kante (10), die k·dt-Äquivalenz, der
  läuferübergreifende Determinismus (K5 9/9), die harte
  Substrat-Sperre.
- **Tot**: iter-25s Lesung „Kante wächst mit D" als Ordnungs-Behauptung
  (teilweise Metrik-Baseline-Effekt, Rest nicht monoton); D=0.15-Kante
  100 (Gitterauflösungs-Artefakt).
- **Offen**: Rauschen vs Struktur an der 0.05-Schwelle — die
  registrierte Schwellen-Klassifikation kann das mit 3 Seeds nicht
  entscheiden. VECTOR_STOCH_CONTROL_METRIC jetzt DREIFACH motiviert
  (iter-24 Zellrauschen, iter-25 schwache Kante, iter-26 NONMONOTONE +
  Straddle).
- **Nicht behauptet**: reale syn3A-Enzymdichten; Absolut-Magnituden;
  „kein Effekt" bei nicht lokalisierter Kante (nur: keine
  Oberkante lokalisiert).

## CORREKTUR-LOG (Kurzfassung; voll in experiment.md)

1. Kontroll-Persistenz-Lücke (5 Anker × 3 Seeds, dt=0, in-run
   klassifiziert, nicht persistiert) — deterministischer
   Recovery-Lauf (`recover_controls.py`); Cross-Check D=0.05/0.15
   gegen iter-25: bit-identisch.
2. iter-25-D=0.15-Kante korrigiert (100 → nicht lokalisiert, ≥ 200);
   kein iter-25-Codefehler — Grobgitter-Auflösung; iter-25-Lesung
   „Kante wächst mit D" als VORBEHALT dort, hier FALSIFIZIERT.
3. Harness-Lektion: per-seed-Metrikvektoren persistieren (die
   per-Seed-≥2/3-Entscheidung ist aus den Artefakten allein nicht
   rekonstruierbar — quantifiziert: naive Mittel-Ebenen-Reklassifikation
   widerspricht 22/43 gebuchten Labels, `mean_vs_perseed.json`).

## Nächste Vektoren

1. VECTOR_STOCH_CONTROL_METRIC (dreifach motiviert, Harness mit
   per-seed-Persistenz)
2. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13)
3. reserviert iter-19b: VECTOR_SHELL1_CASCADE
4. VECTOR_UV_SYNC_REOPEN (iter-16)

Artefakte: `scratch/experiments/iter-26/{edge_fine.py, result.json,
run_log.txt, recover_controls.py, controls_recovery.json,
controls_recovery_log.txt, experiment.md}`