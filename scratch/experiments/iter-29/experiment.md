# iter-29 — VECTOR_T_RULE_CANDIDATES

**Verdict: T_H0_CALIBRATED | CAND_REPLICATED_ALL | CAND_ABS_ALL | EXPL_NOT_REPLICATED · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-28 `next_vectors` (direkte Konsequenz von V4 = SE_RULES_DIVERGE
und dem Struktur-Vorbehalt) — drei Teilfragen VOR dem Lauf registriert:

- (a) Wie hoch ist die False-DISTINCT-Rate der Welch-t-Regel selbst
  (die in iter-28 als Sekundärregel dominierte, aber nie kalibriert
  wurde)?
- (b) Replizieren die drei stärksten iter-28-t-Kandidaten
  (D=0.25 k=1 t=+4.60, D=0.15 k=14 t=−3.81, D=0.05 k=1 t=−3.42) an
  FRISCHEN Seeds mit FRISCHER Kontrolle — d. h. wird der Kontroll-Seed-
  Vorbehalt (Referenz = dieselben Seeds 200-209) entfernt?
- (c) Repliziert das D=0.10-Hoch-k-Plateau (explorativ, Vertreterin
  k=30)?

## Struktureller Vorab-Befund (registriert, vor dem Lauf)

Die iter-28-t-Signale wurden gegen die 200-209-Kontrolle gerechnet —
derselbe Seed-Block, dessen Ausreißer-Struktur die H0-Inflation der
Altschwelle trug. Erwartung: wenn die t-Kandidaten real sind, überleben
sie den frischen Block; wenn sie vom Ausreißer-Kontingent getragen
wurden, sterben sie. Die H0-Rate der t-Regel liegt nominal bei ~8 %
(5/5-Splits, df ≈ 8) — gemessen wird, ob der Stack darüber oder darunter
liegt.

## Registriertes Protokoll (Kurzfassung)

- **Teil 1 (0 GPU, Buchhaltung)**: alle 126 ungeordneten disjunkten
  5/5-Splits der 10 Kontroll-Seeds je Anker (5 Anker), Welch-t ddof=1,
  Rate |t| ≥ 2.0. Sekundär die 2100 3/3-Tripelpaare (h0_pairs VERBATIM).
- **Teil 2 (out-of-sample)**: 3 Kandidaten + 1 Explorativ-Zelle × Seeds
  300-309 (disjunkter Block), dt_react = 1e-5, iter-25-Harness VERBATIM;
  Referenz = frische Kontrollen (k=1, dt=0, Seeds 300-309) je Anker.
  Kriterium STRICT = |t_fresh| ≥ 2.0 UND Vorzeichen-Match zur Tier-A-
  Stimme; ABS = |t_fresh| ≥ 2.0 ohne Richtung.
- **K-C (berichtend)**: Konsistenz frische vs iter-27-Kontrollen
  (z-Score der Mittel bei ddof=1).
- **Gates (bindend)**: K1 Recompute der 3 Kandidaten-t-Werte aus den
  iter-27-Artefakten bit-identisch zu iter-28 (EXAKT dieselbe
  welch_t-Funktion, importiert aus signal_reclass); K2 Determinismus
  doppelt. Verletzung ⇒ REGISTRATION_ERROR.
- **Verdict-Namen**: V1 ∈ {T_H0_CALIBRATED ≤8 % überall / T_H0_INFLATED
  >8 % auf ≥1, ≤15 % überall / T_H0_LEAKY >15 %}; V2 ∈
  {CAND_REPLICATED_ALL 3/3 / CAND_PARTIAL / CAND_NONE}; V3 ∈ {CAND_ABS_*
  }; V4 ∈ {EXPL_REPLICATED / EXPL_NOT_REPLICATED}.

## Durchführung

Vor dem Lauf: Lint (W292, gefixt), **Smoke-Test mit gemockten Läufen**
(gesamtes `main()` in-process; Teil 1 darunter real, weil
artefakt-basiert). Danach der echte Lauf (Task b5yazpvyu): **komplett**,
exit 0, alle Gates PASS, ~12 min Walltime (Buchhaltung + 80 GPU-Läufe).
REGISTRATION_ERROR nicht ausgelöst.

## Ergebnis

### Gates — ALLE PASS

- K1: alle 3 Kandidaten-t-Werte bit-identisch zu iter-28
- K2: bit-identisch = True

### K-A: H0 der Welch-t-Regel — gut kalibriert

| D | 5/5-Splits (126) | 3/3-Tripel (2100) | Nominal |
|---|---|---|---|
| 0.05 | **0.0 %** | 6.7 % | 5/5: 8.0 % |
| 0.10 | **4.0 %** | 7.9 % | 3/3: 11.6 % |
| 0.15 | **4.8 %** | 7.8 % | |
| 0.25 | **0.0 %** | 4.7 % | |
| 0.30 | **5.6 %** | 6.8 % | |

**T_H0_CALIBRATED**: alle 5/5-Raten ≤ 8 % (Max 5.6 %), alle 3/3-Raten
unter dem Nominal 11.6 %. Der scharfe Kontrast zur alten
Schwellen-Klassifikation (iter-27/28: 18-27 % False-DISTINCT auf 4/5
Ankern): die positionsweise Seed-Paarung + ≥2/3-Vote ist ein
Ausreißer-VERSTÄRKER, die t-Statistik ist unter denselben schweren
Verteilungsschwänzen ein Ausreißer-DÄMPFER (Ausreißer in einer Hälfte
vergrößern s und drücken t). Die mächtigere Regel ist auch die sauberere.

### K-B: Frische Kontrollen — Floor im Mittel stabil, Ausreißer block-abhängig

| D | frisch LZ | frisch σ | iter-27 LZ | iter-27 σ | z |
|---|---|---|---|---|---|
| 0.05 | +0.0597 | **0.0125** | +0.0391 | 0.0626 | +1.02 |
| 0.10 | −0.0448 | 0.0424 | −0.0493 | 0.0375 | +0.25 |
| 0.15 | −0.0018 | **0.0113** | +0.0153 | 0.0404 | −1.29 |
| 0.25 | −0.0320 | **0.0101** | −0.0262 | 0.0305 | −0.58 |

Alle 4 Anker konsistent (|z| ≤ 1.3). Auffällig: DREI der vier frischen
Pools sind um Faktor 3-6 ENGER gestreut als der 200-209-Pool — die
Ausreißer-Vorkommen sind block-abhängig, nicht ein fester
Streuboden-Anteil. Die iter-27/28-H0-Inflation (8.7 % bzw. die
Paar-Diff-q95 0.10-0.16) wurde damit teilweise von den Ausreißern
GERADE DIESES Blocks getragen. Konsequenz für alle iter-26/27/28-Claims,
die gegen den 200-209-Pool normalisiert sind: die Rausch-Band-Breite ist
selbst eine Seed-Block-Eigenschaft.

### K-C: Kandidaten-Replikation — 3/3 STRICT

| D | k_f | t (iter-28, 200-209) | t (frisch, 300-309) | LZ frisch | σ frisch | STRICT |
|---|---|---|---|---|---|---|
| 0.05 | 1 | −3.42 | **−5.48** | −0.0111 | 0.0389 | ✓ |
| 0.15 | 14 | −3.81 | **−8.57** | −0.0377 | 0.0070 | ✓ |
| 0.25 | 1 | +4.60 | **+12.06** | +0.0268 | 0.0116 | ✓ |

**CAND_REPLICATED_ALL (3/3) und CAND_ABS_ALL (3/3)**: alle drei
Post-hoc-Kandidaten überleben den frischen Seed-Block UND die frische
Kontrolle mit substanziellem t — die Tier-A-Stimmen werden zu Befunden
gehoben. Die Reihenfolge der Stärke bleibt erhalten (D=0.25 k=1 ist mit
|t| = 12.06 das stärkste Einzelsignal der gesamten Damköhler-Linie).
Die Vorzeichenstruktur ist block-stabil: D=0.05 k=1 und D=0.15 k=14
sitzen UNTER ihrer Kontrolle, D=0.25 k=1 ÜBER seiner — dieselben
Richtungen wie in iter-28.

### K-D: Explorativ — das D=0.10-Plateau repliziert NICHT

| D | k_f | t (iter-28) | t (frisch) | Verdict |
|---|---|---|---|---|
| 0.10 | 30 | +2.15 | **1.01** | **EXPL_NOT_REPLICATED** |

Das iter-28-Hoch-k-Plateau an D=0.10 (k=30/100/300/1000, t ≈ 2.1-2.2,
als „schwache systematische Verschiebung" gelesen) verliert seinen
Vertreter: |t| fällt von 2.15 auf 1.01. Die iter-26-Diskordanz-Spalte
(k=30/100/300/1000 an D=0.10) ist damit in der dritten Buchhaltungs-Ebene
ebenfalls entwertet (nach n=10-Regel NULL in iter-27, Tier-A-t knapp in
iter-28, jetzt frisch NICHT repliziert). Angemeldete Einschränkung: nur
k=30 wurde frisch gelaufen — die Aussage gilt für die Vertreterin; das
gesamte Plateau trägt keine Bestätigung und wird als Rauschen-gelesen
deklariert.

### Verdicte

- **V1 (H0 der t-Regel): T_H0_CALIBRATED** — 0.0-5.6 %, unter Nominal.
- **V2 (STRICT): CAND_REPLICATED_ALL** — 3/3.
- **V3 (ABS): CAND_ABS_ALL** — 3/3.
- **V4 (explorativ): EXPL_NOT_REPLICATED** — Plateau-Vertreterin fällt.

**VERDICT: T_H0_CALIBRATED | CAND_REPLICATED_ALL | CAND_ABS_ALL |
EXPL_NOT_REPLICATED**

## Hypothesen-Lesung

1. **Die t-Regel ist das erste kalibrierte AND mächtige Instrument des
   Stacks.** iter-27 zeigte: die n=3-Schwellen-Regel produziert 18-27 %
   False-DISTINCT. iter-28 zeigte: die t-Regel findet mehr Signale und
   verliert keines. iter-29 schließt den Kreis: die t-Regel liegt unter
   ihrem Nominal (max 5.6 % bei Nominal 8 %) — der Ausreißer-Mechanismus,
   der die Paar-Regel aufblähte, dämpft die t-Statistik. Mächtigkeit und
   Kalibrierung fallen hier in dieselbe Richtung.
2. **Drei von drei Post-hoc-Kandidaten überleben den vollen
   Out-of-Sample-Test** (frische Zell-Seeds UND frische Kontroll-Seeds).
   Das ist die erste Befund-Promotion der Damköhler-Linie, die
   registriert gegen beide Rausch-Quellen abgesichert ist: D=0.25 k=1
   (+12.1), D=0.15 k=14 (−8.6), D=0.05 k=1 (−5.5). Post-hoc-Auswahl ist
   damit NICHT entwertet — sie war der Testgegenstand.
3. **Die Ausreißer-Block-Abhängigkeit schärft die gesamte
   Rausch-Lesung**: die frischen Kontrollpools sind bei 3/4 Ankern um
   Faktor 3-6 enger (σ ~0.01). Der iter-27-Floor war teils ein
   Ausreißer-Kontingent genau dieses Blocks. Konsequenz für die
   SE-Kalibrierung (2 SE = σ_ctrl10·√(2/3)): die Schwelle selbst hängt
   am Block — die 8.7 %-Inflation von iter-28 ist eine Obergrenze für
   Blöcke mit Ausreißern, nicht ein universelles Niveau.
4. **Das D=0.10-Hoch-k-Plateau ist entwertet** (dritte Ebene: NULL) —
   was nach drei Entwertungen bleibt, ist die 5-Zellen-SE-Menge aus
   iter-28, wovon jetzt 3 frisch-repliziert sind (D=0.1 k=3 iter-28; die
   drei Kandidaten hier) — der robuste Kern der Landschaft umfasst:
   D=0.25 k=1, D=0.15 k=14, D=0.05 k=1, D=0.1 k=3, D=0.3 k=30/300/1000
   (letztere noch gegen den alten Block).
5. **Offen**: die verbleibenden SE-Überlebenden (D=0.15 k=5, D=0.3
   k=30/300/1000) und die Kante k_edge=10 tragen noch den
   Kontroll-Seed-Vorbehalt — ein vollständiger frischer Zensus dieser 6
   Zellen (2 Anker, ~70 Läufe) wäre der nächste Schritt; danach wäre
   jedes überlebende Label auf drei Ebenen (n3-Artefakt, SE/t,
   out-of-sample) getragen.

## Nicht behauptet

- Die t-H0-Rate ist eine df-approximierte Messung der Statistik-Familie
  (5/5-Splits, df ≈ 8), nicht des exakten registrierten n=10/n=10-Tests —
  deklariert in der Registrierung.
- Alle Labels sind Eigenschaften DIESES Metrik-Stacks (LZ/corr/tMI +
  Kontrollpools + Registry-Subsets + Gitter), nicht der Zelle und nicht
  von syn3A; keine Aussage über reale Enzymdichten.
- D=0.45 bleibt rechtszensiert; das D=0.10-Plateau wird nur über die
  Vertreterin k=30 entwertet (kein Claim über die nicht gelaufenen
  k=100/300/1000 einzeln — nur über die Plateau-Lesung als Ganzes).
- Die frisch-replizierten Kandidaten sind Befunde IM STACK, keine
  biophysikalischen Befunde; „Post-hoc-Konsistenz wird NIE als
  Bestätigung gebucht" gilt weiter — die Promotion geschieht über den
  frischen Block, nicht über Konsistenz.

## Epistemischer Status / Vorbehalte

- Die Kandidaten sind POST-HOC gewählt — genau das deklariert das
  Protokoll; der Test ist ihre out-of-sample-Replikation, nicht ihre
  Bestätigung im multiplen-Testing-Sinne (mit 43 Zellen × Auswahl des
  Maximums bleibt ein Restrisiko, das die Vorzeichen-Stabilität über
  Blöcke abschwächt, aber nicht auf n=10-Ebene quantifizierbar ist).
- Teil 2 misst pro Zelle n=10 gegen n=10 — die t-Werte alter/neuer Block
  sind wegen unterschiedlicher Kontroll-σ nicht direkt vergleichbar; die
  STRICT-Lesung nutzt nur Richtung + Schwelle.
- Die 3/3-Tripel-H0-Raten (4.7-7.9 %) liegen ebenfalls unter Nominal —
  konsistent mit der Dämpfungs-Lesung, aber bei df ≈ 4 mit 2100
  abhängigen Paaren (gleiche Seeds in vielen Tripeln) ist die effektive
  Stichprobengröße deutlich kleiner als 2100.
- Walltime: ~12 min (80 Läufe); K1 ist reine Artefakt-Buchhaltung.

## CORREKTUR-LOG

1. **Lint**: W292 (fehlendes Newline) in der Erstfassung — vor dem Lauf
   per ruff --fix behoben; danach clean.
2. **Smoke-Test vor dem echten Lauf** (Methode iter-27/28): gesamtes
   `main()` mit gemockten Läufen in-process — alle Pfade inkl.
   Explorativ-Zweig und result.json-Struktur validiert; Teil 1 real.
3. **Echter Lauf** (Task b5yazpvyu): vollständig, exit 0, alle Gates
   PASS — 0 Abbrüche (dritte Iteration in Folge ohne Crash nach
   Smoke-Workflow).

## Nächste Vektoren

1. **VECTOR_FRESH_SURVIVOR_CENSUS** (~70 Läufe): frischer Zensus der 6
   verbleibenden Labels (SE-Überlebende D=0.15 k=5, D=0.3 k=30/300/1000;
   Kante k_edge=10 D=0.05; D=0.1 k=3 gegen frische Kontrolle) — Anker
   D=0.30 braucht die fehlende frische Kontrolle. Danach wäre jedes
   überlebende Label dreifach getragen.
2. Reserviert: iter-19b **VECTOR_SHELL1_CASCADE** (Schale-1-Anomalie,
   Turing-Linie).
3. **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13);
   **VECTOR_UV_SYNC_REOPEN** (iter-16).

## Artefakte

- `t_rule_candidates.py` — Registrierung + Harness (lint-clean)
- `result.json` — Gates, H0-Tabelle (5/5 + 3/3), Konsistenz, 3
  Kandidaten-Zeilen mit per-seed-Vektoren, Explorativ, Verdicte
- `run_log.txt` — vollständiges Laufprotokoll
- `experiment.md` — diese Buchung