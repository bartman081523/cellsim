# iter-27 — VECTOR_STOCH_CONTROL_METRIC

**Verdict: EDGE_STATUS_CHANGED_N10 | H0_DOMINANT | SPREAD_SYMMETRIC · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-26 `next_vectors` (dreifach motiviert: iter-24 Zellrauschen,
iter-25 Kante ruht auf der schwächsten Anker-Zelle, iter-26 NONMONOTONE +
LZ-Straddle + 22/43-Mittel-Ebenen-Diskordanz) — drei Teilfragen VOR dem
Lauf registriert:

- (a) Wie oft liefert die registrierte Schwellen-Klassifikation DISTINCT,
  wenn nur Kontroll-Rauschen drin ist (False-DISTINCT-Rate unter H0)?
- (b) Ist die gebuchte Kanten-/Band-Landschaft der Fein-Anker stabil
  unter Verzehnfachung des Seed-Budgets (n=3 → n=10), oder verschiebt
  sich die Kante / kippt der Lokalisierungs-Status / löst sich die
  Insel-Struktur auf?
- (c) Ist die Zell-seitige per-seed-Streuung (Diffusion + Tau-leap)
  größer als die Kontroll-seitige (nur Diffusion, dt=0)?

## Struktureller Vorab-Befund (registriert, vor dem Lauf)

iter-26 `mean_vs_perseed`: die registrierte Klassifikation ist eine
per-Seed-Stimme (≥2/3), keine Mittel-Ebenen-Eigenschaft (22/43
Widersprüche); die per-seed-LZ-Streuung der Kontrollen allein beträgt bis
0.139 (D=0.05) / 0.109 (D=0.15) — dieselbe Größenordnung wie die
registrierte 0.05-Schwelle. Erwartung daher: der Floor ist **nicht klein
gegen die Schwelle**. Das war die registrierte Hypothese, nicht das
Ergebnis.

## Registriertes Protokoll (Kurzfassung)

- **M1** iter-25-Harness VERBATIM (import saturation_margin: run_config,
  classify, config_classification, SEEDS unverändert; GPU-Operator
  iter-24-validiert). Kein Code-Wechsel am Solver. Output-ERWEITERung
  registriert: per-seed-Metrikvektoren vollständig persistiert (Lektion
  iter-26 CORREKTUR #1).
- **M2** Seed-Budget n=10: SEEDS_10 = (200..209). Anker
  D ∈ {0.05, 0.10, 0.15, 0.25, 0.30}. Kontrollen k=1, dt=0, 10 Seeds je
  Anker (50 Läufe).
- **M3** Zellen (n=10): alle Feingitter-Zellen der Fein-Anker (D=0.05:
  9 Zellen; D=0.15: 13 Zellen) plus die Diskordanz-/Kanten-Zellen der
  Coarse-Anker (D=0.10: {30,100,300,1000}; D=0.25: {1,30};
  D=0.30: {10,30}) — 30 Zellen × 10 Seeds = 300 Läufe, dt_react = 1e-5.
- **M4** Klassifikations-Regeln (beide persistiert): n=3-Regel VERBATIM
  (iter-14/24/25, seed-gepaart gegen die 200-202-Kontroll-Teilmenge,
  ≥2/3) zur Kontinuität und K5''-Verankerung; **n=10-Regel NEU
  registriert**: per-seed classify(run_s, ctrl_mean_10) für alle 10
  Seeds, RUNAWAY bei ≥5/10, DISTINCT bei ≥6/10, sonst NULL.
- **Gates**: K1 Operator-Kalibrierung (iter-24-Schwellen G1–G5); K2
  (bindend) Determinismus run_config doppelt bit-identisch; **K5'**
  (bindend) 3-Seed-Submittel (200-202) aller 30 Zellen bit-identisch zu
  iter-26 result.json; **K5''** (bindend) cls_n3 aller 30 Zellen ==
  iter-26-Buchung. Verletzung ⇒ REGISTRATION_ERROR.
- **Kriterien** (vor dem Lauf fixiert): K-A H0-Rate — je Anker alle
  2100 ungeordneten disjunkten Tripelpaare (A,B) aus den 10 Kontroll-
  Seeds, config_classification VERBATIM; K-B k_edge unter n=10 mit der
  registrierten Oberenden-Regel (iter-25/26), Vergleich gegen die n=3-
  Werte dieses Laufs; K-C Spread-Ratio σ_zelle/σ_kontrolle (ddof=0,
  Median je Anker); K-D Signal-Tiefe der gebuchten DISTINCT-Zellen
  (iter-26-Artefakt, ohne neue Läufe): |cell_mean3_lz − ctrl_mean10_lz|
  in Einheiten SE = σ_ctrl10·√(2/3).
- **Verdict-Namen**: V1 ∈ {EDGE_STATUS_CHANGED_N10 > EDGE_SHIFTED_N10 >
  BAND_STRUCTURE_CHANGED_N10 > EDGE_STABLE_N10} (stärkste Kategorie
  zuerst); V2 ∈ {H0_CLEAN (<5 % überall), H0_LEAKY (≥5 % auf ≥1, <20 %
  überall), H0_DOMINANT (≥20 % auf ≥2 Ankern)}; V3 ∈ {SPREAD_SYMMETRIC
  (<1.5 überall), SPREAD_CELL_DOMINATED (≥1.5 auf ≥2)}. Schwellen
  konventionell, vor dem Lauf fixiert.

## Durchführung

**Drei Startversuche** (siehe CORREKTUR-LOG): Lauf #1 brach nach K1/K2/
50 Kontrollen ab (eager `dict.get`-Default → KeyError), Lauf #2 nach
Kontrollen + erster Zelle (fehlender Seed-Filter → ValueError). Vor
Lauf #3 wurde das gesamte `main()` mit gemockten Läufen durchgespielt
(alle Buchhaltungs-Pfade, result.json-Struktur) — Lauf #3 (Task
be55dmyrj) lief dann **komplett**: 355 Läufe gesamt (3 K1-Kalibrierung
+ 2 K2 + 50 Kontrollen + 300 Zellen), Walltime ≈ 62 min, exit 0.
Alle bindenden Gates PASS; REGISTRATION_ERROR nicht ausgelöst.

## Ergebnis

### Gates — ALLE PASS

- K1: PASS (Masse ✓, Drift ✓, Varianz ✓, Beidseitigkeit ✓)
- K2: bit-identisch = True
- **K5' (Übergang): 30/30 Zellen bit-identisch** zu iter-26
- **K5'' (Klassifikation): 30/30 übereinstimmend** mit iter-26-Buchung

### Kontrollpools (10 Seeds je Anker, dt=0)

| D | LZ-Mittel | σ_within | Ausreißer-Struktur |
|---|---|---|---|
| 0.05 | +0.0391 | 0.0594 | 1 negativer Ausreißer (Seed 203: −0.089), 9 positive |
| 0.10 | −0.0493 | 0.0356 | 2 milde Ausreißer (Seeds 205/207: +0.026/+0.014), 8 ≈ −0.06 |
| 0.15 | +0.0153 | 0.0383 | 2 Ausreißer (Seeds 202/205: +0.093/+0.088), 8 ≈ 0 |
| 0.25 | −0.0262 | 0.0289 | 1 Ausreißer (Seed 203: +0.057), 9 ≈ −0.03 |
| 0.30 | −0.0263 | 0.0373 | 2 Ausreißer (Seeds 207/209: +0.046/+0.048), 8 ≈ −0.045 |

Die ersten 3 Seeds (200-202) sind bit-identisch zur iter-25/26-Recovery —
K5'-Verankerung trägt.

### K-A: False-DISTINCT-Rate unter H0 (je 2100 Tripelpaare)

| D | DISTINCT | Rate | q95 \|ΔLZ\| | σ_within |
|---|---|---|---|---|
| 0.05 | 520/2100 | **24.8 %** | 0.1598 | 0.0594 |
| 0.10 | 550/2100 | **26.2 %** | 0.0961 | 0.0356 |
| 0.15 | 559/2100 | **26.6 %** | 0.1039 | 0.0383 |
| 0.25 | 0/2100 | 0.0 % | 0.0977 | 0.0289 |
| 0.30 | 385/2100 | **18.3 %** | 0.1001 | 0.0373 |

**H0_DOMINANT**: ≥20 % auf 3 Ankern (0.05/0.10/0.15), 18.3 % auf dem
vierten. Nur D=0.25 ist sauber — und das ist **strukturell** erklärbar,
kein Qualitätsmerkmal: bei nur EINEM Ausreißer-Seed in einem
einstreudimensionalen Pool kann keine positionsgepaarte Tripel-Vergleichs-
Konstellation 2 von 3 Positionen gleichzeitig > 0.05 trennen.

**Mechanismus (Interpretation)**: die positionsweise Seed-Paarung +
≥2/3-Vote macht die Klassifikation unter H0 zu einem **Ausreißer-Detektor,
nicht zu einem Mittel-Differenz-Test**: Tripel, deren A- und B-Seite an
verschiedenen Positionen je einen Ausreißer tragen, liefern 2 garantiert
große Differenzen → DISTINCT. Ein Pool mit 2 Ausreißern (D=0.10/0.15/
0.30) produziert daraus systematisch 18–27 % false-DISTINCT. Die
registrierte 0.05-Schwelle liegt bei |ΔLZ|-q95 = 0.10–0.16, also Faktor
2–3 **unter** der natürlichen Paar-Diff-Streuung.

### K-B: Kantenlandschaft unter n=10 (Fein-Anker)

**D=0.05** — k_edge stabil:
- n3: k_edge=10, lokalisiert, Band **nicht** zusammenhängend (interne
  NULLs k=3/5/7; iter-26-„Inseln").
- n10: k_edge=10, lokalisiert, Band zusammenhängend = True, interne
  NULLs [] — aber **nur weil k=2 (n3: DISTINCT) auf NULL kippt** und die
  Insel-Unterkante damit verschwindet (Konvention: k=1 als Bandunterkante
  zählt nicht als Paar-Partner). Distinct (k>1) unter n10: {10} allein.
- **Die iter-26-Insel-Struktur an D=0.05 löst sich unter n=10 auf** —
  sie war Seed-Budget-Artefakt (Frage (d) aus iter-26 damit
  beantwortet: Zellrauschen, nicht Band-Struktur).
- Robust survivors: k=1 (mean10 LZ −0.0290, **σ 0.0054** — sehr eng)
  und k=10 (−0.0001, σ 0.0300).

**D=0.15 — STATUS-WECHSEL** (Trägerin von V1):
- n3: k_edge=200 (= Gitterspitze) ⇒ **nicht lokalisiert** (iter-26-
  Buchung, getragen allein durch k=200).
- n10: k=200 → NULL; k_edge=100, **lokalisiert**, Band **nicht**
  zusammenhängend (interne NULLs 7/10/20/45). Distinct unter n10:
  {5, 14, 30, 70, 100}.
- Flips: k=1/3/7/20/200 DISTINCT→NULL; k=14 NULL→**DISTINCT** (neue
  Insel). Stabil: k=5/30/70/100.
- **Der iter-26-Verdict EDGE_NOT_LOCALIZED (D=0.15) trägt nicht über
  das Seed-Budget**: die Gitterspitze k=200 war Rauschen.

**Coarse-Anker** (nur Zell-Ebene, kein k_edge-Claim):
- D=0.10: {30,100,300,1000} alle NULL unter n3 **und** n10 — die
  iter-26-Mittel-Ebenen-Diskordanz-Zellen bleiben per-seed NULL
  (bestätigt: Seed-Rauschen).
- D=0.25: k=30 DISTINCT→**NULL** (mean10-Gap 0.0587 ≈ 1.2 σ_pair —
  Messerschneide; die n=3-Buchung hing an 3/3 Votes, die n=10-Stimme
  bleibt knapp unter 6/10). Bemerkenswert: geschieht am EINZIGEN Anker
  mit H0-Rate 0 % — der Effekt ist real knapp über dem Rauschen, aber
  unter der registrierten Schwelle nicht auflösbar.
- D=0.30: k=30 DISTINCT **stabil** (tiefste Zelle unter den neu gelaufenen,
  2.6 SE); k=10 NULL stabil.

### K-C: Spread-Ratio (σ_zelle/σ_kontrolle, Median je Anker)

| D | 0.05 | 0.10 | 0.15 | 0.25 | 0.30 |
|---|---|---|---|---|---|
| Median-Ratio | **0.13** | 0.79 | 0.90 | 0.89 | 0.72 |

Alle < 1.5 ⇒ **SPREAD_SYMMETRIC**. Die Zell-seitige Streuung übersteigt
die Kontroll-seitige nirgends — bei D=0.05 ist sie um Faktor ~8 KLEINER
(die Treatment-Läufe klustern eng, während die dt=0-Kontrolle bimodal
±0.07 streut). Tau-leap ist damit **entlastet**: der Rausch-Floor ist
ein Diffusions-/Initialbedingungs-Floor beider Seiten, kein
Tau-leap-Produkt.

### K-D: Signal-Tiefe der gebuchten DISTINCT-Zellen

**17/22** gebuchten DISTINCT-Zellen (ohne D=0.45) liegen innerhalb von
2 SE = σ_ctrl10·√(2/3) des Kontroll-Rauschens. Die 5 tieferen:

| D | k_f | lz_gap | SE |
|---|---|---|---|
| 0.10 | 3 | 0.1023 | **3.5** |
| 0.30 | 300 | 0.0896 | 2.9 |
| 0.30 | 1000 | 0.0846 | 2.8 |
| 0.30 | 30 | 0.0797 | 2.6 |
| 0.15 | 5 | 0.0656 | 2.1 |

Von den neu unter n=10 gelaufenen davon: D=0.30 k=30 und D=0.15 k=5
**überleben**; D=0.10 k=3, D=0.30 k=300/1000 waren nicht Teil des
registrierten iter-27-Zellen-Sets (Tiefe rein aus iter-26-Artefakt +
neuen Kontrollen berechnet).

### Verdicte

- **V1 (Seed-Budget): EDGE_STATUS_CHANGED_N10** — D=0.15 wechselt
  lokalisiert ↔ nicht lokalisiert. (D=0.05s Band-Struktur kippte
  ebenfalls — Insel-Auflösung —, wird aber von der stärkeren Kategorie
  subsumiert.)
- **V2 (H0-Rate): H0_DOMINANT** — ≥20 % auf 3 Ankern.
- **V3 (Spread): SPREAD_SYMMETRIC** — alle Median-Ratios ≤ 0.90.

**VERDICT: EDGE_STATUS_CHANGED_N10 | H0_DOMINANT | SPREAD_SYMMETRIC**

## Hypothesen-Lesung

1. **Die registrierte Klassifikation ist unter H0 dominiert.** Auf 4 von
   5 Ankern liefert sie zu 18–27 % DISTINCT auf reinem Kontroll-Rauschen.
   Erwartung aus der Registrierung (Floor nicht klein gegen Schwelle)
   bestätigt und übertroffen: der Floor ist nicht klein, er ist
   **tragend**. Damit ist die gesamte DISTINCT/NULL-Feinstruktur der
   Iterationen 11→26 (die primäre Metrik der Damköhler-Linie) auf n=3
   als rausch-kontaminiert ausgewiesen — quantitativ, nicht spekulativ.
2. **Die Korrekturkette iter-25 → 26 → 27 schließt sich**: Kante D=0.15
   = 100 (iter-25, n=3 coarse) → nicht lokalisiert (iter-26, n=3 fein,
   getragen von k=200) → wieder 100, lokalisiert (iter-27, n=10 —
   k=200 war Rauschen). Der k=200-DISTINCT-Punkt des iter-26-Verdicts
   EDGE_NOT_LOCALIZED ist als Seed-Artefakt entwertet. Gleichzeitig
   bleibt auch die n=10-Bande bei D=0.15 **inselig** (interne NULLs
   7/10/20/45) — eine scharfe Kante existiert an diesem Anker unter
   keiner der beiden Regeln.
3. **Die Insel-Auflösung an D=0.05 beantwortet iter-26-Frage (d)**: die
   nicht-monotone Spalte war Zellrauschen. Unter n=10 bleibt an
   D=0.05: k=1 DISTINCT (σ 0.0054 — die nominal-Dosis sitzt
   systematisch UNTER der Kontrolle, Gap 0.068) und k=10 DISTINCT (die
   iter-25/26/27-dreifach reproduzierte Kante). Post-hoc-Beobachtung
   (nicht gebucht): mit n=10-Mitteln trägt der k=1-Gap einen t ≈ 3.6 —
   die einzige feinstrukturierte Stelle mit potentiellem Real-Signal
   neben der Kante selbst.
4. **Tau-leap entlastet (V3)**: SPREAD_SYMMETRIC — die Zell-Streuung
   übersteigt die Kontroll-Streuung nirgends (Median-Ratios 0.13–0.90).
   Das Rausch-Problem liegt im Diffusions-/Initialbedingungs-Floor und
   in der Klassifikations-Architektur (positionsweise Paarung +
   Ausreißer-Sensitivität), nicht im Zeitschritt-Schema.
5. **Was robust bleibt** (über n=10 und die H0-Messung hinweg): die
   Kante k_edge=10 an D=0.05; die tiefen Zellen D=0.30 k=30 (2.6 SE)
   und D=0.15 k=5 (2.1 SE); die Events-Plateau/Substrat-Sperre
   (iter-11/24, hier nicht angetastet). Was fällt: 7 der 22 gebuchten
   DISTINCT-Labels (k=2 D=0.05; k=1/3/7/20/200 D=0.15; k=30 D=0.25) —
   konsistent mit der H0-Prädiktion (~25 % von 22 ≈ 5.5 erwartete
   Rausch-Labels, 7 beobachtet).

## Nicht behauptet

- Die n=10-Werte sind eine **NEUE registrierte Regel** — sie revidieren
  die gebuchten n=3-Klassifikationen nicht rückwirkend; die Buchung
  dieses Laufs ist der Statuswechsel + die H0-Rate, keine neue Kante.
- Die H0-Rate ist eine Eigenschaft DIESES Metrik-Stacks (LZ/corr/tMI,
  Schwellen 0.05/0.3/0.05, positionsweise Paarung, ≥2/3-Vote),
  Registry-Subsets und Gitter — nicht der Zelle und nicht von syn3A.
- Keine Aussage über reale Enzymdichten; keine Revision der
  Events-Plateau-/Substrat-Sperre-Befunde.
- Die unter 3. genannte t ≈ 3.6-Beobachtung ist post-hoc und wird
  ausdrücklich nicht als Bestätigung gebucht.

## Epistemischer Status / Vorbehalte

- Die n=10-Regel hat selbst keine direkt gemessene H0-Rate (mit 10
  Kontroll-Seeds ist der Vergleich aller 10 gegen ihr eigenes Mittel
  degeneriert) — sie reduziert das Ausreißer-Problem, eliminiert es
  aber nicht nachweislich.
- Die K-D-Tiefe benutzt konservativ nur die Kontroll-Streuung
  (SE = σ_ctrl10·√(2/3)); für Zellen mit deutlich kleinerer eigener
  Streuung (D=0.05 k=1: σ 0.0054) unterschätzt sie die tatsächliche
  Trennung.
- D=0.45 bleibt ohne 10-Seed-Kontrolle (rechtszensiert, wie iter-25/26).
- Lauf #1/#2-Abbrücke kosteten ~35 min Walltime; ihre Kontroll-Läufe
  sind deterministisch bit-identisch zu Lauf #3 — kein Datenverlust,
  nur Zeit.

## CORREKTUR-LOG

1. **Lauf #1** (Task b1z9syir9): Abbruch nach K1/K2/50 Kontrollen —
   `KeyError: 0.05` an `FINE_GRIDS.get(d, COARSE_CELLS[d])`: Python
   wertet das Default-Argument **auch dann eager aus, wenn der
   Schlüssel existiert**. Fix: explizite Bedingung
   (`FINE_GRIDS[d] if d in FINE_GRIDS else COARSE_CELLS[d]`). Zudem
   maskierte die `| tee run_log.txt`-Pipe den Exit-Code (Task meldete
   exit 0 trotz Traceback) → umgestellt auf `> run_log.txt 2>&1`.
2. **Lauf #2** (Task bif1zpgpf): Abbruch nach Kontrollen + erster Zelle
   — `ValueError: zip() argument 2 is longer than argument 1` in
   `sm.config_classification(sub3, ctrl3)`: ctrl3 fehlte der
   Seed-Filter (`if s in sm.SEEDS`) → 10 statt 3 Kontrollen.
3. **Smoke-Test vor Lauf #3**: gesamtes `main()` mit gemockten Läufen
   (`sm.run_config` → deterministische Pseudo-Werte,
   `sm.validate_gpu` → PASS, HERE → /tmp) in-process ausgeführt —
   reproduzierte Crash #2 und validierte alle zuvor nie ausgeführten
   Buchhaltungs-Pfade (H0-Paare, Kanten, Spread, Tiefe, Verdicte,
   result.json-Struktur). Unter Mocks ist K5'-Verletzung ⇒
   REGISTRATION_ERROR das **erwartete** Mock-Signal.
4. **Lauf #3** (Task be55dmyrj): vollständig, exit 0, alle Gates PASS.
5. **Harness-Lektionen** (in Memory persistiert): Buchhaltungs-Pfade
   vor GPU-Läufen mock-smoken (jeder Crash kostet ~15-20 min); Exit-
   Codes nicht durch Pipes maskieren.

## Nächste Vektoren

1. **VECTOR_SIGNAL_RELATIVE_RECLASS** (kostet 0 GPU-min): Re-Buchung
   der Landschaft mit effektgrößen-basiertem Kriterium (Gap in
   SE-Einheiten, n=10) statt 0.05-Schwelle — reine Buchhaltung auf den
   VOLLSTÄNDIG persistierten per-seed-Vektoren dieses Laufs (300 Zellen
   + 50 Kontrollen). Beantwortet, welche Zellen unter einem
   rausch-bewussten Kriterium überleben.
2. **VECTOR_DEEP_CELL_REPLICATION** (~30 Läufe ≈ 6 min): n=10-Replikation
   der tiefen, in iter-27 nicht gelaufenen Zellen D=0.10 k=3 (3.5 SE —
   tiefste Zelle der gesamten Landschaft), D=0.30 k=300, D=0.30 k=1000.
3. Reserviert: iter-19b **VECTOR_SHELL1_CASCADE** (Schale-1-Anomalie,
   Turing-Linie); **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13);
   **VECTOR_UV_SYNC_REOPEN** (iter-16).

## Artefakte

- `seed_budget.py` — Registrierung + Harness (lint-clean)
- `result.json` — Gates, Kontrollpools (10 Seeds, vollständige
  per-seed-Vektoren), 30 Zellenzeilen (cls_n3/cls_n10/mean_3/mean_10/
  per_seed), H0-Tabelle, Kanten n3 vs n10, Spread, Signal-Tiefe,
  Verdicte
- `run_log.txt` — vollständiges Laufprotokoll von Lauf #3
- `experiment.md` — diese Buchung