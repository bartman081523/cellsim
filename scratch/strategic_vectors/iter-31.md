# iter-31 — VECTOR_EFFECT_BLOCK_STABILITY

**Verdict: SAMPLING_DOMINANT | DEPTHS_STABLE_MAJORITY | 9/9 VORZEICHEN_STABIL · Grade: B · Status: abgeschlossen (2026-09-28)**

## Frage

iter-30s Hypothese 3 („Effektstärken NICHT seed-block-stabil", gestützt
auf 0.69 vs 4.21 SE, dieselbe Zelle) systematisch prüfen: je Kern-Zelle
4 Seed-Blöcke, Gap in LZ-Einheiten, plus Varianz-Zerlegung
(within-Block-Sampling-Rauschen vs echte Block-Varianz). Ziel:
Tiefen-Intervalle statt Punkt-Schätzungen für den robusten Kern.

## Design

280 GPU-Läufe ≈ 46 min: 2 neue Blöcke (Seeds 320-329, 330-339, disjunkt
zu allen bisherigen) × [5 Anker × 10 Kontrollen + 9 Zellen × 10]; die
je Zelle bereits vorliegenden alten Blöcke (1: iter-26/28, 2: iter-29,
3: iter-30) aus Artefakten eingelesen — keine Nachläufe. Per-seed-
Vektoren VOLL persistiert (Zellen UND Kontrollen, erstmals für alle
Blöcke eines Vektors der Linie). Dekomposition über „informierte"
Blöcke: f_block = max(0, Var_obs − Var_samp)/Var_obs, BLOCK_REAL bei
f_block ≥ 0.5. Gates K1a-d (se_units 5/5, welch_t 7.9064, iter-29-
Verankerung 3/3 — vor dem Lauf mit 4 ECHTEN Läufen verifiziert —,
iter-28-Verankerung) + K2, alle PASS.

## Resultat

- **V1: SAMPLING_DOMINANT (0/9 BLOCK_REAL)** — die Block-zu-Block-
  Varianz der Gaps ist in allen 9 Zellen durch within-Block-Sampling-
  Rauschen dominiert (max. f_block 0.28; bei mehreren Zellen sogar
  Var_samp > Var_obs).
- **V2: DEPTHS_STABLE_MAJORITY (9/9 CV ≤ 0.5)** — engste Zellen:
  D=0.3 k=30 (CV 0.05, mean_g +0.0758), D=0.05 k=1 (CV 0.05,
  mean_g −0.0714), D=0.1 k=3 (CV 0.08, mean_g +0.1102 — das stärkste
  und zugleich stabilste Signal). Breiteste: 0.15|5 (CV 0.47) und die
  Kante (CV 0.33).
- **V3: 9/9 VORZEICHEN_STABIL** — keine Zelle wechselt in irgendeinem
  Block die Richtung; die Kante k_edge=10 ist in ALLEN 4 Blöcken
  negativ (auch Block 1 n=3, wo beide Regeln NULL lasen — das NULL war
  Signifikanz bei n=3, nie Vorzeichen).

## Lesung

- **iter-30 Hypothese 3 REVIDIERT**: (a) der 0.69-vs-4.21-Vergleich
  mischte se_units (Nenner σ_within·SE_FACTOR) mit welch_t (Nenner
  per-seed-Sigmas) — like-for-like liest die Kante 0.69/1.58/1.18/1.51
  se_units über 4 Blöcke (Faktor ≤ 2.3, nicht ~6); (b) die Dekomposition
  zeigt 0/9 BLOCK_REAL — Block-Varianz ist kein eigenständiges Phänomen.
- **Effektstärken SIND seed-block-stabil** innerhalb der Messpräzision;
  die 9 Kern-Zellen sind mit Tiefen-Intervallen gebucht (mean_g ± σ_g
  über 4 Blöcke). Künftige Buchungen tragen CV-Angaben statt
  Punkt-Schätzungen.
- **Nicht behauptet**: Metrik-Stack-Eigenschaften; f_block ist eine
  Größenordnung-Schätzung aus 3–4 Blockwerten; asymmetrische
  Block-Coverage (Kandidaten {1,2,4,5}, übrige {1,3,4,5}) als
  Design-Vorbehalt; kein Claim über nicht-getestete Blöcke; D=0.45
  rechtszensiert.

## Nächste Vektoren

1. Reserviert iter-19b: VECTOR_SHELL1_CASCADE.
2. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13); VECTOR_UV_SYNC_REOPEN
   (iter-16).

Artefakte: `scratch/experiments/iter-31/{effect_block_stability.py,
result.json, run_log.txt, experiment.md}`