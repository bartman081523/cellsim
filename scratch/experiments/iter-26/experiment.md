# iter-26 — VECTOR_EDGE_FINE_SWEEP

**Verdict: EDGE_UPPER_CONFIRMED | EDGE_NOT_LOCALIZED | EDGE_D_NONMONOTONE · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-25 `next_vectors` (MODERATE): „Feiner Sweep um die Kante +
D-Abhängigkeit der Kante" — vier Teilfragen VOR dem Lauf registriert:

- (a) Wo liegt die Metrik-Kante bei D=0.05 genau (iter-25: k_edge=10,
  Gitterabstand 3/Dezade, wahre Kante irgendwo in (10, 30))?
- (b) Wo bei D=0.15 (iter-25: k_edge=100, NULL bei k=10 INNERHALB der
  DISTINCT-Region 3 und 30 — schon dort verdächtig)?
- (c) Wie wächst k_edge mit D (iter-25: 10 → 100 → nicht lokalisiert;
  Anteil Metrik-Baseline-Effekt offen)?
- (d) Ist die nicht-monotone D=0.05-Spalte (k=1/3/10 → D/NULL/D)
  Zellrauschen (iter-24-Lektion) oder Band-Struktur?

## Struktureller Vorab-Befund (registriert, vor dem Lauf)

iter-25 K4 hat die k·dt-Äquivalenz bereits 4/4 bit-identisch gemessen —
der feine Sweep ist eine Verfeinerung desselben Damköhler-Gitters.
Überschneidungszellen MÜSSEN bit-identisch zu iter-25 sein (K5 als
REGISTRATION_ERROR-Gate, läuferübergreifender Determinismus).

## Registriertes Protokoll (Kurzfassung)

- **M1** iter-25-Harness VERBATIM (import saturation_margin: run_config,
  classify, config_classification, SEEDS unverändert; GPU-Operator,
  RNG-Split GPU-Philox/CPU-PCG64). Kein Code-Wechsel am Harness.
- **M2** Feingitter: D=0.05: k_f ∈ {1,2,3,5,7,10,14,20,30}
  (Faktor-Abstand ≤ 1.55); D=0.15: k_f ∈ {1,3,5,7,10,14,20,30,45,70,
  100,140,200}; dt=1e-5, Seeds {200,201,202}.
- **M3** Neue Anker: D ∈ {0.10, 0.25, 0.30} mit Coarse-Gitter
  {1,3,10,30,100,300,1000}; D=0.45 aus iter-25 wiederverwendet
  (rechtszensiert, OPPORTUN: bestehende Messung, korrigierte Lesung).
- **M4** Kontrolle dt=0 je Anker (5 Anker), seed-gepaart.
- **Gates**: K1 Operator-Kalibrierung (iter-24-Schwellen); K2
  Determinismus (run_config doppelt bit-identisch); K4a Äquivalenz-
  Spot-Check {(7,1e-5) vs (1,7e-5)}, {(14,1e-5) vs (1,1.4e-4)} bei
  D=0.15; K5 Übergangs-Check — 9 Überschneidungszellen (D=0.05:
  k∈{1,3,10,30}; D=0.15: k∈{1,3,10,30,100}) müssen in ALLEN
  Metrik-Feldern bit-identisch zu iter-25 result.json sein.
- **K3 (bindend)**: k_edge(D) = größtes k_f mit DISTINCT (per-Seed
  ≥2/3, VERBATIM iter-14/24/25). Oberenden-Regel (iter-25-Lektion,
  DIESMAL im Code): Gitterspitze DISTINCT ⇒ Kante nicht lokalisiert
  (untere Schranke = Gitterspitze). OBERKANTE_KLAR: alle k_f > k_edge
  NULL. BAND_ZUSAMMENHÄNGEND: kein NULL zwischen zwei DISTINCT-Zellen
  unterhalb der Kante (inkl. k=1 als Bandunterkante). Global = min der
  lokalisierten Kanten (konservativ).
- **Verdict-Namen**: V1a/V1b ∈ {EDGE_UPPER_CONFIRMED (k_edge ==
  iter-25), EDGE_UPPER_SHIFTED (≠), EDGE_UPPER_UNCLEAR, 
  EDGE_NOT_LOCALIZED}; V2 ∈ {EDGE_D_MONOTONE (Intervall-Konsistenz mit
  Zensur: lb_i ≤ ub_{i+1} ∧ lb_{i+1} ≤ ub_i für jedes benachbarte
  Paar), EDGE_D_NONMONOTONE}; REGISTRATION_ERROR bei Gate-Verletzung.

## Durchführung

Registrierter Lauf komplett: 43 Treatment-Zellen (9 fein D=0.05 +
13 fein D=0.15 + 21 neue Anker) + 15 Kontroll-Zellen (5 Anker × 3
Seeds) + K1/K2/K4a/K5, exit 0. Ein Lauf, kein Abbruch, keine
Zwischenverdikte.

## Ergebnis

### Gates — ALLE PASS, REGISTRATION_ERROR nicht ausgelöst

- **K1** PASS (Masse/Drift/Varianz/Beidseitigkeit, iter-24-Schwellen).
- **K2** bit-identisch (run_config(1.0, 1e-5, 0.15, 200) doppelt).
- **K4a** 2/2 bit-identisch (k=7 und k=14 bei D=0.15) — die k·dt-
  Äquivalenz trägt auch auf dem Feingitter (λ = k·dt·n linear).
- **K5 9/9 bit-identisch zu iter-25** — alle neun Überschneidungszellen
  in ALLEN Metrik-Feldern. Läuferübergreifender Determinismus zweier
  unabhängiger Prozesse (iter-25-Lauf vs iter-26-Lauf) exakt bestätigt;
  die Klassifikations-Abfolgen unten sind damit NICHT
  Implementierungsrauschen, sondern registrierte Metrik-Wirkung.

### Feiner Anker D=0.05 (9 Zellen; Konfig-Mittel)

| k_f | class | LZgrw | events |
|---|---|---|---|
| 1 | DISTINCT | −0.028 | 9.50e6 |
| 2 | DISTINCT | −0.003 | 1.90e7 |
| 3 | NULL | +0.055 | 2.86e7 |
| 5 | NULL | +0.077 | 4.82e7 |
| 7 | NULL | +0.055 | 6.81e7 |
| 10 | DISTINCT | +0.006 | 9.85e7 |
| 14 | NULL | +0.041 | 1.39e8 |
| 20 | NULL | +0.075 | 2.01e8 |
| 30 | NULL | +0.064 | 3.01e8 |

**k_edge = 10** (== iter-25 exakt), OBERKANTE_KLAR (14/20/30 alle NULL),
aber **band_connected = FALSE** — interne NULLs bei k=3/5/7. Die
„Kante" ist als größtes-DISTINCT-k_f reproduzierbar, als Region nicht:
DISTINCT/NULL wechseln zwischen benachbarten k_f (Frage (d): Zellflips,
nicht glatte Bandkante).

### Feiner Anker D=0.15 (13 Zellen; Konfig-Mittel)

| k_f | class | LZgrw | events |
|---|---|---|---|
| 1 | DISTINCT | +0.062 | 9.51e6 |
| 3 | DISTINCT | +0.026 | 2.87e7 |
| 5 | DISTINCT | +0.081 | 4.82e7 |
| 7 | DISTINCT | +0.051 | 6.81e7 |
| 10 | NULL | +0.007 | 9.85e7 |
| 14 | NULL | −0.036 | 1.40e8 |
| 20 | DISTINCT | +0.012 | 2.01e8 |
| 30 | DISTINCT | −0.008 | 3.01e8 |
| 45 | NULL | −0.004 | 4.52e8 |
| 70 | DISTINCT | −0.007 | 7.03e8 |
| 100 | DISTINCT | +0.039 | 1.00e9 |
| 140 | NULL | −0.033 | 1.40e9 |
| 200 | DISTINCT | +0.019 | 1.67e9 |

**k_edge = 200 = Gitterspitze → EDGE_NOT_LOCALIZED** (registrierte
Oberenden-Regel). iter-25s Kante 100 ist im Feingitter NICHT bestätigt
— die DISTINCT-Region zieht sich bis mindestens 200 durch, mit internen
NULLs bei 10/14/45/140. iter-25s „Kante 100" war eine
Gitterauflösungs-Eigenschaft (NULL bei k=300 auf 3-Punkte/Dezade), keine
physikalische Kante; das interne NULL-Muster (k=10 NULL zwischen 7 und
20 DISTINCT) war in iter-25 sichtbar und wiederholt sich hier exakt.

### Neue Anker (Kanten-Verlauf; Konfig-Mittel)

| D | Kanten-Abfolge (k_f: class) | k_edge | lokalisiert | interne NULLs |
|---|---|---|---|---|
| 0.10 | 1 D, 3 D, 10 N, 30 N, 100 N, 300 N, 1000 N | 3 | ja (OBERKANTE_KLAR) | — (Band zusammenhängend) |
| 0.25 | 1 N, 3 D, 10 N, 30 D, 100 N, 300 N, 1000 N | 30 | ja (OBERKANTE_KLAR) | [10] (k=1 NULL: Bandunterkante) |
| 0.30 | 1 D, 3 D, 10 N, 30 D, 100 D, 300 D, 1000 D | 1000 = Gitterspitze | nein | [10] |

Events-Plateau auch auf den neuen Ankern: D=0.10 und D=0.25 sind bei
k=300 vs k=1000 events-identisch (1.672734065e9 bzw. 1.672886089e9 —
k-invariante Trajektorien, Substrat-Sperre); D=0.30 liegt am Plateau-
Rand (k=300: 1.672902645e9 vs k=1000: 1.672902429e9, rel. Differenz
1.3e-7).

### D-Abhängigkeit — EDGE_D_NONMONOTONE

Registrierte Intervall-Konsistenz (lb/ub mit Zensur) über
{0.05, 0.10, 0.15, 0.25, 0.30} + iter-25-0.45 (rechtszensiert):

| D | lb | ub | lokalisiert |
|---|---|---|---|
| 0.05 | 10 | 10 | ja |
| 0.10 | 3 | 3 | ja |
| 0.15 | 200 | ∞ | nein |
| 0.25 | 30 | 30 | ja |
| 0.30 | 1000 | ∞ | nein |
| 0.45 (iter-25, korrigiert) | 10000 | ∞ | nein |

**Vier der fünf benachbarten Paare verletzen die Konsistenz**:
[10,10] vs [3,3] disjunkt; [3,3] vs [200,∞) disjunkt; [200,∞) vs
[30,30] disjunkt; [30,30] vs [1000,∞) disjunkt. Es existiert KEINE
monoton wachsende Kanten-Funktion, die diese Intervalle schneidet —
auch keine monoton fallende. Das Bild „schnellere Mischung trägt das
Signal tiefer in die Sättigung" (iter-25-Lesung) ist als Ordnungs-
Behauptung tot; übrig bleibt eine nicht-monotone, an der
LZ-Schwelle rauschdominierte Klassifikations-Landschaft.

### Klassifikations-Schärfe: LZgrw straddelt die registrierte Schwelle

LZgrw über alle 43 Zellen: **−0.049 … +0.081** — die ±0.05-Schwelle
liegt MITTEN im Verteilungsbereich der Konfig-Mittel. Die
DISTINCT/NULL-Abfolgen sind daher Grenznähe-Urteile, keine
Abstands-Urteile. K1–K5 belegen, dass die Urteile deterministisch
reproduzierbar sind (K5 9/9 bit-identisch) — das Problem ist nicht
Reproduzierbarkeit, sondern dass die registrierte Metrik an dieser
Schwelle zwischen Rauschen und Struktur nicht unterscheiden kann.

## Hypothesen-Lesung

- **(a) D=0.05: k_edge = 10 exakt bestätigt** (EDGE_UPPER_CONFIRMED) —
  der einzige robuste Teil des iter-25-Bildes, nun auf halbem
  Gitterabstand (Faktor ≤ 1.55) repliziert. Aber: das Band darunter ist
  NICHT zusammenhängend (NULLs bei 3/5/7) — es gibt eine DISTINCT-Zelle
  bei 10 und eine „Inseln-Struktur" darunter, keine Kante.
- **(b) D=0.15: iter-25-Kante 100 korrigiert** — nicht lokalisiert
  (≥ 200, Gitterspitze DISTINCT). Die iter-25-Kante war ein
  Gitterauflösungs-Artefakt; die interne Nicht-Monotonie (NULL bei 10)
  war bereits dort sichtbar und verstärkt sich im Feingitter.
- **(c) „Kante wächst mit D" FALSIFIZIERT als Ordnung**: D=0.10 hat die
  NIEDRIGSTE Kante (3), unter D=0.05 (10); D=0.25 (30) unter D=0.15
  (≥ 200). Teil des iter-25-Effekts war Metrik-Baseline (Kontroll-LZ-
  Vorzeichenwechsel bei hohem D); der Rest ist keine monotone
  Physik-Behauptung wert.
- **(d) Zellrauschen vs Band-Struktur: UNENTSCHIEDEN, und die
  registrierte Metrik kann es mit 3 Seeds nicht entscheiden** —
  LZgrw straddelt die Schwelle, 4/5 Anker haben interne NULLs
  (Zellflips zwischen benachbarten k_f). Das ist der stärkste
  bisherige Hinweis darauf, dass die DISTINCT/NULL-Klassifikation an
  der 0.05-Schwelle einen Rausch-Floor hat (iter-24-Lektion, jetzt auf
  Konfig-Ebene).
- **Unverändert robust**: K4a-Äquivalenz (2/2 bit-identisch), K5 (9/9),
  Events-Plateau/Substrat-Sperre (k-invariante Trajektorien ab
  k_f ≈ 300–1000 auf allen Ankern). Die HARDWARE-Ebene des
  Damköhler-Gitters ist exakt; weich ist nur die Klassifikations-Metrik.

## Nicht behauptet

- Keine Aussage über reale syn3A-Enzymdichten (Registry-k sind
  MGENITALIUM/HYPOTHESE); alle Kanten sind Eigenschaften DIESES
  Registry-Subsets + der LZ-Metrik.
- Keine Absolut-Magnituden, keine U-Form; nur Klassifikations-Präsenz
  gegen die seed-gepaarte Kontrolle.
- Die Nicht-Lokalisierbarkeit (D=0.15, D=0.30, D=0.45) heißt nicht
  „kein Effekt" — sie heißt: die registrierte Schwellen-Klassifikation
  lokalisiert bei diesem Seed-Budget keine Oberkante (Entscheidung
  Rauschen vs Struktur offen, s. VECTOR_STOCH_CONTROL_METRIC).

## Epistemischer Status / Vorbehalte

- **Per-Seed-Metrikvektoren nicht persistiert** (nur Konfig-Mittel +
  Klassifikation): die per-Seed-≥2/3-Entscheidung ist aus den
  Artefakten nicht rekonstruierbar; K5 (9/9 Mittel bit-identisch)
  sichert die Reproduzierbarkeit der Mittel, nicht die Nachrechenbarkeit
  der Einzel-Entscheidung. Harness-Lektion für iter-27+: per-seed-Werte
  persistieren (oder in den VECTOR_STOCH_CONTROL_METRIC-Harness
  übernehmen).
  **Quantifiziert** (`mean_vs_perseed.py` → `mean_vs_perseed.json`):
  wendet man dieselbe registrierte Schwellen-Regel (alle drei
  Kriterien) auf die Konfig-Mittel statt auf die per-Seed-Diffs an,
  widerspricht das **22 von 43** gebuchten Labels. Extremfälle:
  D=0.15 k=3 ist gebucht DISTINCT bei Mittel-Ebenen-lz_diff 0.001
  (≥2/3-Stimme, eine Seed-Differenz kompensiert die anderen — plausibel,
  denn die per-seed-LZ-Streuung der Kontrollen allein beträgt bis
  0.139 bei D=0.05 / 0.109 bei D=0.15); umgekehrt sind D=0.10
  k=30/100/300/1000 gebucht NULL, aber auf Mittel-Ebene DISTINCT
  (lz_diff 0.058–0.060, knapp über der Schwelle). Das ist KEIN Fehler:
  die gebuchten Labels folgen der registrierten per-Seed-Regel; die
  Diskordanz zeigt, dass DISTINCT/NULL eine Stimm-Eigenschaft ist, keine
  Mittel-Ebenen-Eigenschaft — die 22/43 sind die harte Zahl hinter der
  Persistenz-Lektion und der stärkste quantitative Antrieb für
  VECTOR_STOCH_CONTROL_METRIC (Klassifikationstiefe relativ zum
  Rausch-Floor statt Schwellen-Crossing).
- Grenznähe: die globale iter-25-Kante (10) ruht weiterhin auf
  grenznahen Zellen; robust ist die Existenz einer Sättigungs-Sperre
  (Events-Plateau), nicht die Kanten-Feinstruktur.

## CORREKTUR-LOG

1. **Kontroll-Persistenz-Lücke** (gleiches Muster wie iter-25
   CORREKTUR #2): die 15 in-run-Kontrollen (dt=0, 5 Anker × 3 Seeds,
   M4) wurden klassifiziert, aber nicht in result.json persistiert —
   für die NEUEN Anker D ∈ {0.10, 0.25, 0.30} wäre die Klassifikation
   ohne Nachmessen aus den Artefakten nicht nachrechenbar gewesen.
   Recovery-Lauf (`recover_controls.py`, deterministisch, NUR zur
   Persistenz; KEIN neuer Befund, KEINE Änderung der gebuchten
   Klassifikation) → `controls_recovery.json`. Cross-Check D=0.05/0.15
   gegen iter-25 `controls_recovery.json`:
   **bit-identisch=True (beide)** — läuferübergreifender Determinismus
   ein weiteres Mal bestätigt.
2. **iter-25-Kante D=0.15 korrigiert**: iter-25 buchte „k_edge=100,
   lokalisiert" (Grobgitter); das Feingitter zeigt DISTINCT bis zur
   Gitterspitze 200 → nicht lokalisiert. Kein iter-25-Codefehler —
   Grobgitter (3 Punkte/Dezade) + dieselbe interne NULL-Struktur; die
   registrierte Oberenden-Regel (in iter-25 nach CORREKTUR #1
   ergänzt, hier ab Lauf im Code) macht die Zensur explizit. Die
   iter-25-Dokumentation (experiment.md, strategic_vectors, 
   LIMITATIONS/CLAUDE-Zeile) bleibt inhaltlich stehen, mit Verweis
   hierher; die D-Abhängigkeits-Lesung „Kante wächst mit D" ist in
   iter-25 als VORBEHALT (Metrik-Baseline-Anteil offen) und nun hier
   als FALSIFIZIERT (Ordnung) gebucht.
3. **Keine weiteren Abweichungen**: Harness VERBATIM (M1), alle
   registrierten Gates in-run PASS, Oberenden-Regel im Code
   umgesetzt (iter-25-Lektion umgesetzt).

## Nächste Vektoren

1. **VECTOR_STOCH_CONTROL_METRIC** — Klassifikationstiefe relativ zum
   Kontroll-Rausch-Floor statt Schwellen-Crossing; JETZT DREIFACH
   motiviert: iter-24 (Zellgrenzen kippen), iter-25 (globale Kante
   ruht auf der schwächsten Anker-Zelle), iter-26 (Kantenfolge
   NONMONOTONE + LZgrw straddelt die Schwelle + 4/5 Anker mit
   internen NULLs). Der Harness persistiert per-seed-Werte (Lektion
   aus iter-26 CORREKTUR-Log).
2. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13, offen)
3. reserviert iter-19b: VECTOR_SHELL1_CASCADE (Schale-1-Anomalie)
4. VECTOR_UV_SYNC_REOPEN (iter-16)

## Artefakte

- `edge_fine.py` (registriertes Protokoll + Implementation)
- `result.json` (43 Zellen, Kanten, Anker-Verdicte, D-Abhängigkeit,
  K1/K2/K4a/K5)
- `run_log.txt` (vollständiger Lauf)
- `recover_controls.py`, `controls_recovery.json`,
  `controls_recovery_log.txt` (Kontroll-Persistenz, post-hoc Recovery)
- `mean_vs_perseed.py`, `mean_vs_perseed.json` (Mittel-Ebenen- vs
  per-Seed-Diskordanz, 22/43 — Interpretations-Beobachtung, keine neue
  Klassifikation)
- Vorlage: `scratch/experiments/iter-25/` (Harness VERBATIM)