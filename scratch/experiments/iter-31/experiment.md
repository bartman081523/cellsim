# iter-31 — VECTOR_EFFECT_BLOCK_STABILITY

**Verdict: SAMPLING_DOMINANT | DEPTHS_STABLE_MAJORITY | 9/9 VORZEICHEN_STABIL · Grade: B · Status: abgeschlossen (2026-09-28)**

## Frage

Aus iter-30 `next_vectors`: iter-30s Hypothese 3 sagte „Effektstärken
NICHT seed-block-stabil" — gestützt auf EINEN Anekdoten-Vergleich
(0.69 vs 4.21 SE, dieselbe Zelle). Alle 8 Kern-Zellen trugen
Punkt-Schätzungen aus 1–2 Blöcken. Dieser Vektor misst die
Block-Stabilität systematisch: je Kern-Zelle 4 Seed-Blöcke, Gap in
LZ-Einheiten als primäre Metrik, plus Varianz-Zerlegung
(within-Block-Sampling-Rauschen vs echte Block-Varianz).

## Registriertes Protokoll (Kurzfassung)

- **Zellen (9)**: die 5 SE-Überlebenden (D=0.10 k=3, D=0.15 k=5,
  D=0.30 k=30/300/1000), die 3 iter-29-Befunde (D=0.05 k=1, D=0.15 k=14,
  D=0.25 k=1) plus die Kante k_edge=10 (D=0.05, iter-30s paradigmatischer
  Block-Fluktuierer) als motivierter Fall.
- **Design (280 GPU-Läufe ≈ 46 min)**: 2 neue Blöcke (Seeds 320-329,
  330-339 — disjunkt zu 200-209/300-309/310-319) × [5 Anker × 10
  Kontrollen + 9 Zellen × 10]. Die je-Zelle bereits vorliegenden alten
  Blöcke werden aus den Artefakten eingelesen (Block 1 iter-26-n3 /
  iter-28-deep + iter-27-Kontrolle; Block 2 iter-29-Kandidaten; Block 3
  iter-30) — KEINE teuren Nachläufe alter Zellen. iter-25-Harness
  VERBATIM. **Per-seed-Vektoren VOLL persistiert (Zellen UND
  Kontrollen) — erstmals für alle Blöcke eines Vektors der Linie.**
- **Metrik**: primär signiertes Gap g_b = mean_cell,b − mean_ctrl,b
  (LZ-Einheiten) je Block; deskriptiv je Zelle über 4 Blöcke: mean_g,
  sigma_g (ddof=1), CV, Intervall. Sekundär welch_t je Block.
- **Dekomposition** (primär, über „informierte" Blöcke = Blöcke mit
  within-Block-Sigmas BEIDER Seiten): Var_obs = Var(g) (ddof=1);
  Var_samp = mean_b(s²_cell/n + s²_ctrl/n); f_block =
  max(0, Var_obs − Var_samp)/Var_obs; BLOCK_REAL falls f_block ≥ 0.5.
  Informierte Sets: deep3/k300/k1000 → {1,3,4,5}; D=0.15 k=5, D=0.3
  k=30, Kante → {3,4,5} (Block 1 der n=3-Zellen nicht informiert —
  iter-26 persistiert keine per-seed-Sigmas); Kandidaten → {2,4,5}.
- **Gates (bindend)**: K1a se_units der 5 SE-Überlebenden bit-identisch
  zu iter-28 (VERBATIM via signal_reclass-Import); K1b welch_t D=0.1 k=3
  == 7.9064 bit-identisch; K1c iter-29-Verankerung (seed 300, 3/3) per
  Cross-Session-Determinismus — **vor dem Lauf mit 4 ECHTEN GPU-Läufen
  verifiziert (4/4 bit-identisch)**; K1d iter-28-Verankerung (seed 200,
  deep3, NEU in dieser Iteration); K2 Determinismus doppelt. Verletzung
  ⇒ REGISTRATION_ERROR.
- **Verdict-Namen**: V1 ∈ {BLOCK_VAR_DOMINANT ≥6/9 / MIXED 3–5 /
  SAMPLING_DOMINANT ≤2}; V2 ∈ {DEPTHS_STABLE_MAJORITY ≥6/9 CV≤0.5 /
  DEPTHS_MIXED / DEPTHS_UNSTABLE_MAJORITY}; V3 berichtend n_signstable/9.

## Durchführung

Vor dem Lauf: Lint (F841/F821/W292, gefixt — siehe CORREKTUR #1),
**Smoke-Test mit gemockten Läufen** (gesamtes `main()` in-process) — der
Smoke fand einen echten Schema-Crash VOR dem echten Lauf (CORREKTUR #2)
— und 4 echte Gate-Verifikations-Läufe (CORREKTUR #4). Zwei Launches
wurden extern getötet (CORREKTUR #3, NICHT gebucht); der dritte, mit
`setsid nohup` vollständig detachierte Lauf überlebte und lief **vollständig**: exit 0, alle Gates PASS, ~46 min Walltime (280 Läufe +
Gates), 0 Abbrüche. REGISTRATION_ERROR nicht ausgelöst.

## Ergebnis

### Gates — ALLE PASS (11 True-Zeilen im run_log)

- K1a: se_units 5/5 bit-identisch (3.5249 / 2.0967 / 2.6142 / 2.9407 /
  2.7775)
- K1b: welch_t D=0.1 k=3 = 7.9064 bit-identisch
- K1c: iter-29-Determinismus 3/3 bit-identisch
- K1d: iter-28-Determinismus (seed 200, deep3) bit-identisch
- K2: bit-identisch = True

### Neue Kontrollblöcke — konsistent

| D | Block 4 LZ (σ) | Block 5 LZ (σ) |
|---|---|---|
| 0.05 | +0.0502 (0.0693) | +0.0645 (0.0099) |
| 0.10 | −0.0442 (0.0342) | −0.0603 (0.0284) |
| 0.15 | +0.0205 (0.0363) | +0.0068 (0.0288) |
| 0.25 | −0.0258 (0.0301) | −0.0074 (0.0424) |
| 0.30 | −0.0305 (0.0291) | −0.0221 (0.0370) |

Damit liegen für alle 5 Anker Kontrollpools aus VIER unabhängigen
Seed-Blöcken vor (200-209, 300-309, 310-319, 320-329, 330-339) — im
Mittel weiter einstig, σ-Breite blockweise variierend.

### V2: Tiefen — ALLE 9 ZELLEN CV-STABIL (DEPTHS_STABLE_MAJORITY 9/9)

| Zelle | Gaps über Blöcke (LZ) | mean_g | σ_g | CV | Intervall | f_block |
|---|---|---|---|---|---|---|
| D=0.10 k=3 | +0.1075 / +0.1087 / +0.1016 / +0.1230 | +0.1102 | 0.0091 | **0.08** | [+0.102, +0.123] | 0.00 |
| D=0.15 k=5 | +0.0656 / +0.0533 / +0.0173 / +0.0406 | +0.0442 | 0.0206 | 0.47 | [+0.017, +0.066] | 0.28 |
| D=0.30 k=30 | +0.0797 / +0.0772 / +0.0753 / +0.0711 | +0.0758 | 0.0036 | **0.05** | [+0.071, +0.080] | 0.00 |
| D=0.30 k=300 | +0.0667 / +0.0658 / +0.0693 / +0.0565 | +0.0646 | 0.0056 | 0.09 | [+0.057, +0.069] | 0.00 |
| D=0.30 k=1000 | +0.0652 / +0.0665 / +0.0633 / +0.0442 | +0.0598 | 0.0105 | 0.18 | [+0.044, +0.067] | 0.00 |
| D=0.05 k=1 | −0.0666 / −0.0708 / −0.0745 / −0.0734 | −0.0714 | 0.0035 | **0.05** | [−0.075, −0.067] | 0.00 |
| D=0.15 k=14 | −0.0515 / −0.0359 / −0.0460 / −0.0291 | −0.0406 | 0.0100 | 0.25 | [−0.052, −0.029] | 0.00 |
| D=0.25 k=1 | +0.0408 / +0.0588 / +0.0498 / +0.0352 | +0.0462 | 0.0104 | 0.22 | [+0.035, +0.059] | 0.24 |
| D=0.05 k=10 (Kante) | −0.0335 / −0.0768 / −0.0572 / −0.0730 | −0.0601 | 0.0197 | 0.33 | [−0.077, −0.034] | 0.00 |

Bei mehreren Zellen übersteigt Var_samp das Var_obs — das
within-Block-Sampling-Rauschen allein reicht aus, um die beobachtete
Block-zu-Block-Varianz der Gaps zu erklären (extrem: D=0.3 k=30,
Var_samp 2.0e-4 gegen Var_obs 1.0e-5; D=0.05 k=1, 2.6e-4 gegen 4e-6 —
die Gaps dieser Zellen sind über drei unabhängige Seed-Sets fast
identisch).

### V3 — Vorzeichen: 9/9 über ALLE 4 Blöcke stabil

Keine einzige Zelle wechselt in irgendeinem Block die Richtung. Die
Landschafts-Geometrie ist 4-Block-robust: positiv {0.10|3, 0.15|5,
0.30|30, 0.30|300, 0.30|1000, 0.25|1}, negativ {0.05|1, 0.15|14,
0.05|10}. Die Kante k_edge=10 ist **in ALLEN VIER Blöcken negativ** —
auch an Block 1 (n=3, gap −0.0335), wo beide Regeln NULL lasen: das
NULL war eine Signifikanz-Aussage bei n=3, nie eine Vorzeichen-Aussage.

### Verdicte

- **V1 (Dekomposition): SAMPLING_DOMINANT** — 0/9 BLOCK_REAL (max.
  f_block 0.28 bei D=0.15 k=5, gefolgt von 0.24 bei D=0.25 k=1; beide
  unter der registrierten 0.5-Schwelle).
- **V2 (Deskriptiv): DEPTHS_STABLE_MAJORITY** — 9/9 CV ≤ 0.5; nur zwei
  Zellen über CV 0.25 (0.15|5 mit 0.47, Kante mit 0.33).
- **V3 (Vorzeichen): 9/9 VORZEICHEN_STABIL**.

**VERDICT: SAMPLING_DOMINANT | DEPTHS_STABLE_MAJORITY | 9/9 VORZEICHEN_STABIL**

## Hypothesen-Lesung

1. **iter-30 Hypothese 3 wird REVIDIERT**: die Behauptung „Effektstärken
   sind NICHT seed-block-stabil" trägt nicht. Zwei Gründe, beide
   dokumentiert:
   - **Statistik-Vermischung (CORREKTUR)**: der 0.69-vs-4.21-Vergleich
     setzte se_units (iter-28; Nenner σ_within·SE_FACTOR) gegen |welch_t|
     (iter-30; Nenner aus per-seed-Sigmas von Zelle UND Kontrolle) — zwei
     Statistiken mit verschiedenen Nennern. Like-for-like in
     LZ-Gap-Einheiten liest die Kante 0.69 / 1.58 / 1.18 / 1.51
     se_units über die 4 Blöcke — Faktor ≤ 2.3, nicht ~6.
   - **Block-Varianz ist Rauschen**: die systematische Dekomposition
     zeigt 0/9 Zellen mit f_block ≥ 0.5 — die beobachtete
     Block-zu-Block-Varianz ist in allen 9 Zellen durch
     within-Block-Sampling-Rauschen dominiert (bei mehreren Zellen sogar
     Var_samp > Var_obs).
2. **Die Tiefen sind stabil**: alle 9 Kern-Zellen haben CV ≤ 0.5 (6/9
   unter 0.25) und über 4 Blöcke (drei davon über vier VOLL unabhängige
   Seed-Sets) konstante Richtung und Größenordnung. Die Damköhler-Linie
   ist damit zum ersten Mal mit Tiefen-INTERVALLEN statt
   Punkt-Schätzungen gebucht. Robuster Kern: unverändert 9 Zellen
   (8 Kern-Zellen + Kante als richtungsstabile Zelle).
3. **Die Kanten-Lesung wird zweifach präzisiert**: (a) die iter-30-
   „EDGE_SIGNALS"-Botschaft (krispes Signal an Block 3) ist als
   RICHTUNG über alle 4 Blöcke getragen — die Zelle war nie im
   Vorzeichen fluktuierend, nur in der Signifikanz (n=3 an Block 1);
   (b) die Magnituden-Fluktuation (CV 0.33) ist selbst
   sampling-dominiert. „Block-fluktuierend" gilt damit nur für die
   SIGNIFIKANZ, nicht für das Signal selbst.
4. **Methodische Schlussfolgerung für die Linie**: Effektstärken-Angaben
   ohne Block-Angabe sind NICHT unvollständig (iter-30-These), sie sind
   mit CV-Angabe ausreichend spezifiziert — die Block-Varianz ist kein
   eigenständiges Phänomen, sondern Sampling-Rauschen plus in zwei
   Fällen (0.15|5, 0.25|1) ein Rest unter der Schwelle. Künftige
   Buchungen tragen mean_g ± σ_g über Blöcke statt Punkt-Schätzungen.

## Nicht behauptet

- Alle Gaps sind Eigenschaften DES METRIK-STACKS (LZ + Kontrollpools +
  Registry-Subsets + Gitter), nicht der Zelle und nicht von syn3A.
- f_block ist eine Schätzung aus 3–4 Block-Werten mit verrauschten
  within-Block-Sigmas — die Zerlegung quantifiziert die Größenordnung,
  sie ist keine präzise Varianz-Komponenten-Schätzung.
- Die Block-Coverage ist asymmetrisch (Kandidaten {1,2,4,5}, übrige 6
  {1,3,4,5}); Block 1 der n=3-Zellen geht nur in die Deskriptik ein.
  Zellübergreifende Block-Vergleiche tragen diesen Vorbehalt.
- Keine Aussage über Blöcke jenseits der 5 gemessenen; D=0.45
  rechtszensiert; kein rückwirkender Eingriff in frühere Buchungen (die
  Revision von iter-30 Hypothese 3 ist eine NEUE Buchung, die alte
  Iteration bleibt als historischer Stand stehen).

## CORREKTUR-LOG

1. **Lint (vor dem Lauf)**: F841 (`iter26` unbenutzt) + F821
   (`i26_rows` undefiniert — der se_units-Gate braucht ihn) und W292 in
   der Erstfassung; gefixt, danach clean.
2. **Schema-Fix im Smoke-Stadium (vor dem echten Lauf)**: der Smoke-Test
   fand einen KeyError 't_fresh', der den ECHTEN Lauf geknackt hätte —
   iter-30s deep3/edge-Einträge tragen `welch_t`, die survivors-Zeilen
   `t_fresh` (heterogenes Schema). Ersatz:
   `c["t_fresh"] if "t_fresh" in c else c["welch_t"]`. Der Smoke-Test
   hat damit exakt seine Aufgabe erfüllt.
3. **Zwei extern getötete Launches (NICHT gebucht)**: der erste
   Hintergrund-Lauf starb ~3–4 min nach Start, der zweite ~2 min nach
   Start (cleaner Stopp, kein Traceback, kein OOM; parallel lief eine
   externe Manim-Render-Last auf der Maschine). Der dritte Launch wurde
   mit `setsid nohup … & disown` vollständig detachiert und überlebte —
   280 Läufe + Gates, ~46 min, 0 Abbrüche. Die gekillten Launches sind
   nicht gebucht; es existiert genau ein result.json.
4. **Gate-Verifikation vor dem echten Lauf**: K1c (seed 300, 3
   Kandidaten) und K1d (seed 200, deep3) mit 4 ECHTEN GPU-Läufen
   verifiziert — 4/4 bit-identisch (−0.025870014109971917,
   −0.027860015195354304, +0.027860015195354082, 0.06766003690300315).
5. **Echter Lauf**: vollständig, exit 0, alle Gates PASS.

## Nächste Vektoren

1. Reserviert: iter-19b **VECTOR_SHELL1_CASCADE** (Schale-1-Anomalie,
   Turing-Linie).
2. **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13);
   **VECTOR_UV_SYNC_REOPEN** (iter-16).
3. Die Damköhler-Buchhaltung ist konsolidiert; offene Anschlussfragen
   (z. B. Kandidat 0.15|5 als einziger CV>0.25-Ausreißer außerhalb der
   Kante) sind optional, nicht kritisch.

## Artefakte

- `effect_block_stability.py` — Registrierung + Harness (lint-clean)
- `result.json` — Gates, neue Blöcke mit per-seed-Vektoren, alte Blöcke,
  per_cell (Gaps/CV/f_block/Intervalle), Verdicte
- `run_log.txt` — vollständiges Laufprotokoll
- `experiment.md` — diese Buchung