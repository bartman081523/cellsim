# iter-28 — VECTOR_SIGNAL_RELATIVE_RECLASS + VECTOR_DEEP_CELL_REPLICATION

**Verdict: RECLASS_SEVERE | SE_H0_MARGINAL | SE_RECOVERS_NONE | SE_RULES_DIVERGE | DEEP_REPLICATED · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-27 `next_vectors` (direkte Konsequenz von V2 = H0_DOMINANT) — vier
Teilfragen VOR dem Lauf registriert:

- (a) Welche der 22 gebuchten DISTINCT-Zellen überleben ein
  effektgrößen-basiertes Kriterium (Gap ≥ 2 SE des Kontroll-Rauschens)
  statt der rausch-dominierten 0.05-Schwelle?
- (b) Wie hoch ist die False-DISTINCT-Rate DIESES Kriteriums unter
  reinem Kontroll-Rauschen (in-sample, deklariert)?
- (c) Gewinnen gebuchte NULL-Zellen unter dem neuen Kriterium
  (Recovery), oder ist es strikt konservativer?
- (d) agreeen SE-Kriterium (3-Seed-Mittel) und Welch-t (n=10 per-seed)
  als Regeln?
- (e) Replizieren die drei tiefen, in iter-27 nicht gelaufenen Zellen
  out-of-sample (neue GPU-Läufe, n=10)?

## Struktureller Vorab-Befund (registriert, vor dem Lauf)

iter-27 K-D: **17/22** gebuchte DISTINCT-Zellen liegen innerhalb 2 SE =
σ_ctrl10·√(2/3) des Kontroll-Rauschens. Registrierte Erwartung daher:
~77 % Flip ⇒ **RECLASS_SEVERE** — das ist die Hypothese, nicht das
Ergebnis. Weiter erwartet: H0-Rate des SE-Kriteriums über dem nominalen
Wert, weil die Kontrollpools schwer ausgeprägte Ausreißer tragen
(iter-27 Kontrollstruktur).

## Registriertes Protokoll (Kurzfassung)

- **Teil 1 (0 GPU-min, reine Buchhaltung)** auf den vollständig
  persistierten per-seed-Vektoren von iter-26/27. Tier A = 30 in iter-27
  gelaufene Zellen; Tier B = übrige 13 iter-26-Zellen (3-Seed-Mittel);
  D=0.45 nicht im Rows-Set (keine 10-Seed-Kontrolle) ⇒ nicht behandelt.
- **Neues Kriterium (registriert)**: se_units = |mean3_Zelle −
  ctrl_mean10| / (σ_ctrl10·√(2/3)) — VERBATIM die iter-27-K-D-Form, jetzt
  als Regel: Label_SE = DISTINCT ⇔ se_units ≥ 2.0.
- **H0 des Kriteriums**: je Anker alle 2100 ungeordneten disjunkten
  Kontroll-Tripelpaare (A, B), se_units ≥ 2.0 → Rate. In-sample-
  Kalibrierung, explizit deklariert.
- **Sekundär (Tier A)**: Welch-t (ddof=1) mit |t| ≥ 2.0 → Label_t;
  corr/tmi-Inertie berichtend (Schwellen 0.3/0.05).
- **Gates (bindend)**: K1 Recompute der 22 DISTINCT-se_units ==
  iter-27-Tiefen-Zeilen (bit-identisch); K2 cls_n3-Verankerung 30/30.
  Verletzung ⇒ REGISTRATION_ERROR.
- **Verdict-Namen**: V1 ∈ {SEVERE ≥50 % / MODERATE ≥25 % / MILD ≥10 % /
  STABLE}; V2 ∈ {CALIBRATED ≤5 % überall / MARGINAL >5 % auf ≥1, ≤10 %
  überall / LEAKY >10 %}; V3 ∈ {RECOVERS_CELLS / RECOVERS_NONE}; V4 ∈
  {AGREE ≥90 % / MARGINAL ≥70 % / DIVERGE}; V5 ∈ {REPLICATED 3/3 /
  PARTIAL / NOT_REPLICATED}.
- **Teil 2 (out-of-sample)**: D=0.10 k=3, D=0.30 k=300, D=0.30 k=1000 ×
  Seeds 200-209 = 30 GPU-Läufe (iter-25-Harness VERBATIM, dt_react =
  1e-5), Welch-t gegen die iter-27-10-Seed-Kontrolle.

## Durchführung

Vor dem Lauf: Lint (5 ruff-Fehler gefixt: F401/I001/F841/SIM108/W292) und
**Smoke-Test mit gemockten Läufen** (gesamtes `main()` in-process,
result.json-Struktur validiert — Methode aus iter-27 CORREKTUR #3;
Bemerkung: Teil-1-Output ist unter Mocks REAL, weil rein
artefakt-basiert). Danach der echte Lauf (Task bxrni5sac):
**vollständig**, exit 0, alle Gates PASS, ~6 min Walltime (Buchhaltung +
30 GPU-Läufe). REGISTRATION_ERROR nicht ausgelöst.

## Ergebnis

### Gates — ALLE PASS

- K1: 22 gebuchte DISTINCT-Zellen, se_units bit-identisch zu iter-27 K-D
- K2: 30/30 Tier-A-Zellen cls_n3 == iter-26

### Teil 1 — SE-Reclass: 17/22 kippen (RECLASS_SEVERE)

| | gebucht DISTINCT (22) | gebucht NULL (21) |
|---|---|---|
| Label_SE = DISTINCT | **5** | **0** |
| Label_SE = NULL | **17** | 21 |

Die 17 Flips (alle DISTINCT→NULL, keine Gegenrichtung):

| D | k_f | Tier | se_units | Bemerkung |
|---|---|---|---|---|
| 0.05 | 1 | A | 1.37 | iter-27s engste Zelle (σ 0.0054) — SE unterschätzt hier |
| 0.05 | 2 | A | 0.86 | iter-26-Insel |
| 0.05 | 10 | A | 0.69 | **die dreifach reproduzierte Kante kippt unter SE** |
| 0.10 | 1 | B | 1.47 | |
| 0.15 | 1 | A | 1.49 | |
| 0.15 | 3 | A | 0.34 | |
| 0.15 | 7 | A | 1.14 | |
| 0.15 | 20 | A | 0.11 | |
| 0.15 | 30 | A | 0.73 | |
| 0.15 | 70 | A | 0.71 | |
| 0.15 | 100 | A | 0.75 | iter-27s n10-Kante |
| 0.15 | 200 | A | 0.11 | iter-26s EDGE_NOT_LOCALIZED-Trägerin |
| 0.25 | 3 | B | 1.85 | |
| 0.25 | 30 | A | 1.59 | iter-27-Messerschneide |
| 0.30 | 1 | B | 1.34 | |
| 0.30 | 3 | B | 1.18 | |
| 0.30 | 100 | B | 1.29 | |

**Die 5 SE-Überlebenden** = exakt die 5 Tiefen-Zellen aus iter-27 K-D:

| D | k_f | Tier | se_units |
|---|---|---|---|
| 0.10 | 3 | B | **3.52** |
| 0.15 | 5 | A | 2.10 |
| 0.30 | 30 | A | 2.61 |
| 0.30 | 300 | B | 2.94 |
| 0.30 | 1000 | B | 2.78 |

Bemerkenswert: **die Kante k_edge=10 an D=0.05** (dreifach reproduziert
in iter-25/26/27) **kippt unter dem SE-Kriterium ebenfalls** (se 0.69) —
ihr Gap liegt im selben Rausch-Band wie alles andere; ihre Historie trägt
nicht über die Effektstärke.

### K-B: H0 des SE-Kriteriums (2100 Paare je Anker, in-sample)

| D | DISTINCT | Rate | | iter-27 0.05-Schwelle |
|---|---|---|---|---|
| 0.05 | 182/2100 | **8.7 %** | | 24.8 % |
| 0.10 | 138/2100 | **6.6 %** | | 26.2 % |
| 0.15 | 136/2100 | **6.5 %** | | 26.6 % |
| 0.25 | 5/2100 | **0.2 %** | | 0.0 % |
| 0.30 | 135/2100 | **6.4 %** | | 18.3 % |

**SE_H0_MARGINAL** (>5 % auf 4 Ankern, ≤10 % überall): das
effektgrößen-basierte Kriterium verbessert die Kalibrierung um Faktor
~3-4, bleibt aber über dem nominalen Niveau — dieselbe Ausreißer-Struktur
der Kontrollpools (schwere Verteilungsschwänze) trägt jetzt direkt in die
SE-Einheiten. D=0.25 erneut strukturell sauber (nur 1 Ausreißer-Seed).

### K-C: NULL-Seite — kein Recovery

**0/21** gebuchte NULL-Zellen steigen auf DISTINCT. Das Kriterium ist
strikt konservativer als die Altschwelle — die Korrekturbewegung geht
ausschließlich nach unten (weniger DISTINCT), keine neuen Inseln.

### K-D: Regel-Kongruenz Tier A — SE_RULES_DIVERGE, aber einseitig

**16/30 (53 %)** Übereinstimmung. Struktur der 14 Divergenzen: **alle in
EINER Richtung** — SE=NULL, Label_t=DISTINCT (kein einziger Fall der
Gegenrichtung):

| D | k_f | se_units | Welch-t |
|---|---|---|---|
| 0.05 | 1 | 1.37 | **−3.42** |
| 0.05 | 2 | 0.86 | −2.10 |
| 0.10 | 30 | 1.30 | +2.15 |
| 0.10 | 100 | 1.23 | +2.08 |
| 0.10 | 300 | 1.30 | +2.23 |
| 0.10 | 1000 | 1.30 | +2.23 |
| 0.15 | 1 | 1.49 | +3.13 |
| 0.15 | 7 | 1.14 | +2.59 |
| 0.15 | 14 | 1.65 | **−3.81** |
| 0.15 | 30 | 0.73 | −2.01 |
| 0.15 | 140 | 1.53 | −2.03 |
| 0.25 | 1 | 1.73 | **+4.60** |
| 0.25 | 30 | 1.59 | +3.52 |
| 0.30 | 10 | 1.26 | +2.38 |

Das ist eine **Power-Divergenz, keine Widerspruchs-Divergenz**: die
3-Seed-Mittel-Schätzung (√(2/3)-Abschlag) ist gegen die 10-Seed-Welch-t
systematisch schwächer. Bemerkenswerte Muster: das D=0.10-Hoch-k-Plateau
(k=30/100/300/1000, t ≈ 2.1-2.2 — die iter-26-Diskordanz-Zellen lesen
sich unter t als schwache systematische Verschiebung) und D=0.25 k=1
(t=+4.60 — das stärkste bisher ungebuchte Einzelsignal der Landschaft).
Die Vorzeichen mischen sich (positiv UND negativ) — keine
Einheitsrichtung über die Landschaft.

**corr/tmi-Inertie**: max corr_drop 0.0005 (Schwelle 0.3), max tmi_diff
0.0013 (Schwelle 0.05) — feuert nie. Der gesamte Reclass-Stack ist
LZ-Entropie-getrieben (konsistent mit iter-24/27).

### Teil 2 — Deep-Cell-Replikation: 3/3 (DEEP_REPLICATED)

| D | k_f | LZ-Mittel (n=10) | σ (ddof=1) | Welch-t | iter-27-Artefakt-Schätzung |
|---|---|---|---|---|---|
| 0.10 | 3 | **+0.0582** | 0.0210 | **7.91** | 3.5 SE |
| 0.30 | 300 | +0.0404 | 0.0341 | **4.05** | 2.9 SE |
| 0.30 | 1000 | +0.0389 | 0.0340 | **3.96** | 2.8 SE |

Alle drei replizieren out-of-sample (neue Läufe, frische Seeds gegen den
iter-27-Kontrollpool) mit substanziellem t. Die Reihenfolge stimmt mit
der Artefakt-Tiefe; D=0.1 k=3 ist deutlich STÄRKER als die
SE-Schätzung — die Zelle selbst ist enger gestreut (σ 0.0210) als die
Kontrolle (σ 0.0356), der konservative Kontroll-only-SE unterschätzt die
tatsächliche Trennung (iter-27-Vorbehalt bestätigt). Alle drei sitzen
oberhalb ihrer Kontrollen (positive Richtung).

### Verdicte

- **V1 (Reclass): RECLASS_SEVERE** — 17/22 (77 %) kippen.
- **V2 (H0 des Kriteriums): SE_H0_MARGINAL** — 6.4-8.7 % auf 4 Ankern.
- **V3 (NULL-Seite): SE_RECOVERS_NONE** — 0/21.
- **V4 (Regel-Kongruenz): SE_RULES_DIVERGE** — 53 %, alle Divergenzen
  eine Richtung (t mächtiger).
- **V5 (Deep-Replikation): DEEP_REPLICATED** — 3/3.

**VERDICT: RECLASS_SEVERE | SE_H0_MARGINAL | SE_RECOVERS_NONE |
SE_RULES_DIVERGE | DEEP_REPLICATED**

## Hypothesen-Lesung

1. **Die registrierte Erwartung (RECLASS_SEVERE) trifft exakt**: 17/22 =
   77 % Flip, identisch mit der iter-27-K-D-Vorhersage (17/22 innerhalb
   2 SE). Die DISTINCT/NULL-Feinstruktur der Iterationen 11→26 kollabiert
   unter dem rausch-bewussten Kriterium auf **5 Zellen** — und zwar auf
   genau die 5, die iter-27 als Tiefen-Ausreißer markiert hatte. Die
   Konsistenz der beiden unabhängigen Buchhaltungen (iter-27 Artefakt,
   iter-28 Regel) ist der eigentliche Befund.
2. **Die Kante k_edge=10 an D=0.05 verliert ihren SE-Status**: ihr Gap
   (0.69 SE) liegt im Rausch-Band. Was an D=0.05 bleibt: k=1 mit t=−3.42
   (Tier-A-Buchhaltung, n=10) — die nominal-Dosis sitzt systematisch
   UNTER der Kontrolle; die iter-27-post-hoc-Schätzung (t≈3.6) bestätigt
   sich als Welch-t=−3.42 in der registrierten Sekundärregel. Nicht
   out-of-sample.
3. **Kein Recovery (V3)**: die Korrekturkette iter-25 → 26 → 27 → 28
   bewegt sich strikt monoton abwärts in der DISTINCT-Anzahl
   (22 → 7 Überlebende unter n10 → 5 unter SE). Die Landschafts-Feinstruktur
   ist kein Signal-Substrat; verbleibende Kandidaten: die 5 SE-Zellen,
   wovon 3 (D=0.1 k=3, D=0.3 k=300/1000) jetzt out-of-sample repliziert
   sind.
4. **Die t-Regel dominiert die SE-Regel überall (V4, einseitig)**: mit
   n=10-per-seed-Daten ist der Welch-t die mächtigere Regel — er findet
   14 zusätzliche Signale, verliert keines. Daraus folgt die nächste
   Falsifikationsfrage: die t-Regel hat selbst keine gemessene H0-Rate
   (bei |t| ≥ 2 und n=10 gegen n=10 unter schweren Verteilungsschwänzen
   ist nominal nicht zu erwarten) — ohne sie ist D=0.25 k=1 (t=+4.60)
   ein Kandidat, kein Befund.
5. **Tiefe-Zellen-Kanal robust**: 3/3 out-of-sample, LZ-Mittel +0.039 bis
   +0.058 oberhalb der Kontrollen. Der hoch-k-Kanal an D=0.30 (k=30/300/
   1000) ist damit der robusteste Struktur-Befund der gesamten
   Damköhler-Linie — in allen drei Buchhaltungs-Ebenen (n3-Artefakt, SE,
   out-of-sample-t) sichtbar.

## Nicht behauptet

- **In-sample-Kalibrierung**: das SE-Kriterium UND seine H0-Rate sind auf
  denselben Kontrollpools gemessen — V2 ist eine Konsistenz-Messung, die
  out-of-sample-Validierung liefert nur Teil 2.
- Die gebuchten iter-26-n=3-Klassifikationen werden nicht rückwirkend
  revidiert; Label_SE/Label_t sind Eigenschaften DIESES
  Re-Interpretations-Stacks (Metrik-Stack + Kontrollpools), nicht der
  Zelle und nicht von syn3A.
- Die 14 Label_t-DISTINCT-Zellen sind Tier-A-Buchhaltung auf EXISTIERENDEN
  Seeds — keine out-of-sample-Replikation; insbesondere D=0.25 k=1 und
  D=0.15 k=14 sind Kandidaten, keine Befunde.
- Keine Aussage über reale Enzymdichten; D=0.45 bleibt rechtszensiert.
- Die t-Regel hat keine gemessene H0-Rate (Punkt 4).

## Epistemischer Status / Vorbehalte

- Die SE-Überlebenden-Zählung hängt an der konventionellen 2.0-Schwelle;
  bei 1.85 (D=0.25 k=3) und 1.73 (D=0.25 k=1) sähe die Kante anders aus.
  Die Schwelle wurde vor dem Lauf fixiert (iter-27-DEPTH_SE) — trotzdem
  messerscharf.
- Teil 2 nutzt die iter-27-Kontrolle (Seeds 200-209): out-of-sample in
  den Zell-Läufen, NICHT in den Kontroll-Seeds (dieselben 10 Seeds
  definieren die Referenz) — ein Struktur-Vorbehalt, der erst mit
  frischen Kontroll-Seeds entfällt.
- Die Welch-t-Signale im Bereich |t| ≈ 2.0-2.6 (7 der 14) sind einzeln
  schwach; nur der Verbund (einseitige Divergenz, konsistente Plateaus)
  trägt die Lesung.
- Laufzeit: Teil-1-Buchhaltung über 43 Zellen + 2100×5 H0-Paare ≈
  Sekunden; Teil 2 = 30 GPU-Läufe ≈ 6 min.

## CORREKTUR-LOG

1. **Lint**: 5 ruff-Fehler in der Erstfassung (F401 `Any` ungenutzt,
   I001 Import-Sortierung, F841 `rep` ungenutzt, SIM108 if/else →
   ternary, W292 fehlendes Newline) — vor dem Lauf gefixt; danach clean.
2. **Bit-Identitäts-Vorsicht (proaktiv)**: die K1-Gleichheit verlangt
   exakt dieselbe Float-Operation wie iter-27 — `SE_FACTOR =
   float(np.sqrt(2.0/3.0))` statt `**0.5` (C-pow kann im letzten ulp
   abweichen und das Gate fälschlich feuern).
3. **Smoke-Test vor dem echten Lauf** (Methode iter-27): gesamtes
   `main()` mit gemockten Läufen (deterministische Pseudo-Werte,
   HERE → /tmp) in-process — validierte result.json-Struktur und alle
   Teil-2-Pfade; Teil-1-Output ist unter Mocks real (artefakt-basiert)
   und stimmte bereits mit dem späteren echten Lauf überein.
4. **Echter Lauf** (Task bxrni5sac): vollständig, exit 0, alle Gates
   PASS. Keine Abbrüche — der Smoke-Test-Workflow hat sich bewährt
   (iter-27: 2 Abbrüche; iter-28: 0).

## Nächste Vektoren

1. **VECTOR_T_RULE_CANDIDATES** (~40 Läufe): (a) H0-Rate der Welch-t-Regel
   messbar über 5/5-Splits der 10 Kontroll-Seeds (126 Splits je Anker,
   0 GPU); (b) out-of-sample-Replikation der stärksten t-Kandidaten an
   FRISCHEN Seeds (300-309): D=0.25 k=1 (t=+4.60), D=0.15 k=14 (t=−3.81),
   D=0.05 k=1 (t=−3.42) — entfällt der Struktur-Vorbehalt (Kontroll-Seeds),
   sind sie Befunde; scheitern sie, war die Tier-A-Stimme Rauschen.
2. Reserviert: iter-19b **VECTOR_SHELL1_CASCADE** (Schale-1-Anomalie,
   Turing-Linie).
3. **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13);
   **VECTOR_UV_SYNC_REOPEN** (iter-16).

## Artefakte

- `signal_reclass.py` — Registrierung + Harness (lint-clean)
- `result.json` — Gates, 43 SE-Reclass-Zeilen (Tier, Label_SE, Welch-t,
  Label_t), H0-Tabelle, Kongruenz, corr/tmi, 3 Deep-Zellen mit per-seed-
  Vektoren, Verdicte
- `run_log.txt` — vollständiges Laufprotokoll
- `experiment.md` — diese Buchung