# iter-30 — VECTOR_FRESH_SURVIVOR_CENSUS

**Verdict: SURV_ALL | DEEP3_FRESH_REPLICATED | EDGE_SIGNALS · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Aus iter-29 `next_vectors` (Abschluss des Zensus): Die t-Regel ist
kalibriert, drei Kandidaten sind frisch-repliziert — aber die 4
verbleibenden SE-Überlebenden (D=0.15 k=5, D=0.3 k=30/300/1000) und die
Kante k_edge=10 trugen noch den Kontroll-Seed-Vorbehalt (Referenz =
dieselben Seeds). Drei Teilfragen VOR dem Lauf registriert:

- (a) Replizieren die 4 SE-Überlebenden an einem dritten, disjunkten
  Seed-Block (310-319) mit FRISCHER Kontrolle (STRICT: |t| ≥ 2.0 UND
  positiv — die SE-Lesung aller 5 war einseitig positiv)?
- (b) Trägt D=0.10 k=3 — iter-28s stärkstes Signal (|t|=7.91) — auch
  gegen eine FRISCHE Kontrolle?
- (c) Zeigt die dreifach reproduzierte Kante k_edge=10 (D=0.05, in
  iter-28 unter SE UND t gekippt) an frischen Seeds irgendein Signal
  (beidseitig, kein Vorzeichen registriert)?

## Registriertes Protokoll (Kurzfassung)

- **Design**: 100 GPU-Läufe — 4 Anker (0.05/0.10/0.15/0.30) × 10 frische
  Kontrollen + 6 Zellen × 10, Seeds 310-319 (disjunkt zu 200-209 UND
  300-309), dt_react = 1e-5, iter-25-Harness VERBATIM.
- **K-C (berichtend)**: Konsistenz der 4 frischen Kontrollpools gegen die
  iter-27-Pools (z-Scores) — dritte Independent-Messung der
  Block-Abhängigkeit.
- **Gates (bindend)**: K1 (a) se_units der 4 SE-Überlebenden bit-identisch
  zu iter-28 (VERBATIM-Formel aus signal_reclass); K1 (b) welch_t D=0.1
  k=3 aus iter-28-deep-per-seed vs iter-27-Kontrolle == 7.9064; K1 (c)
  iter-29-Verankerung per Cross-Session-Determinismus (seed 300); K2
  Determinismus doppelt. Verletzung ⇒ REGISTRATION_ERROR.
- **Verdict-Namen**: V1 ∈ {SURV_ALL 4/4 / SURV_PARTIAL / SURV_NONE}; V2 ∈
  {DEEP3_FRESH_REPLICATED / DEEP3_FRESH_NOT}; V3 ∈ {EDGE_SIGNALS /
  EDGE_NULL_CONFIRMED}.

## Durchführung

Vor dem Lauf: Lint (W292, gefixt), **Gate-Redesign im Smoke-Stadium**
(siehe CORREKTUR #2) und **Smoke-Test mit gemockten Läufen** (gesamtes
`main()` in-process; K1-Gates + K-B darunter real, weil artefakt-basiert;
Gate (c) ist unter Mocks notwendigerweise False — Mock-Ausgabe vs echte
Artefakte — und wurde stattdessen mit 3 ECHTEN Läufen vor dem Start
verifiziert: 3/3 bit-identisch). Danach der echte Lauf (Task b1j5qqclg):
**vollständig**, exit 0, alle Gates PASS, ~15 min Walltime (107 Läufe).
REGISTRATION_ERROR nicht ausgelöst.

## Ergebnis

### Gates — ALLE PASS

- K1: se_units 4/4 bit-identisch; welch_t D=0.1 k=3 bit-identisch;
  iter-29-Determinismus 3/3 bit-identisch
- K2: bit-identisch = True

### K-B: Frische Kontrollen (dritter Block) — vollständig konsistent

| D | frisch LZ | frisch σ | iter-27 LZ | iter-27 σ | z |
|---|---|---|---|---|---|
| 0.05 | +0.0611 | 0.0547 | +0.0391 | 0.0626 | +0.84 |
| 0.10 | −0.0508 | 0.0401 | −0.0493 | 0.0375 | −0.09 |
| 0.15 | +0.0030 | 0.0284 | +0.0153 | 0.0404 | −0.79 |
| 0.30 | −0.0309 | 0.0285 | −0.0263 | 0.0393 | −0.30 |

Alle 4 Anker konsistent (|z| ≤ 0.84) — der strengste Kontroll-Test der
Linie: drei unabhängige Blöcke (200-209, 300-309, 310-319) im Mittel
einstig; nur die Ausreißer-Vorkommen und die σ-Breite variieren.

### V1: SE-Überlebende — 4/4 repliziert (SURV_ALL)

| D | k_f | SE (iter-28) | t_fresh | LZ frisch | σ frisch |
|---|---|---|---|---|---|
| 0.15 | 5 | 2.10 | **3.17** | +0.0563 | 0.0451 |
| 0.30 | 30 | 2.61 | **5.55** | +0.0463 | 0.0335 |
| 0.30 | 300 | 2.94 | **4.70** | +0.0348 | 0.0339 |
| 0.30 | 1000 | 2.78 | **4.84** | +0.0355 | 0.0328 |

Alle vier überleben den dritten Block mit frischer Kontrolle, alle
positiv (oberhalb ihrer Kontrollen), LZ-Mittel +0.035 bis +0.056 —
dieselbe Richtung wie die SE-Schätzungen. Der D=0.30-Hoch-k-Kanal ist
jetzt in VIER Ebenen getragen (n3-Artefakt, SE, out-of-sample-t,
dritter Block).

### V2: D=0.10 k=3 gegen FRISCHE Kontrolle — repliziert

| D | k_f | t_fresh | LZ frisch | σ frisch |
|---|---|---|---|---|
| 0.10 | 3 | **6.98** | +0.0578 | 0.0286 |

Iter-28s stärkstes Signal (7.91 gegen den alten Block) bestätigt auf
VOLL unabhängiger Basis (frische Zell-Seeds UND frische Kontroll-Seeds).
Die Zelle bleibt das stärkste Einzelsignal der SE-Menge.

### V3: Kante k_edge=10 — EDGE_SIGNALS (die Überraschung)

| D | k_f | t_fresh | LZ frisch | σ frisch | Verdict |
|---|---|---|---|---|---|
| 0.05 | 10 | **−4.21** | −0.0157 | 0.0186 | **EDGE_SIGNALS** |

Die Kante zeigt am dritten Block ein KRISPES NEGATIVES Signal (Zelle
UNTER der Kontrolle, Zell-σ nur 0.0186) — nachdem sie am 200-209-Block
unter BEIDEN Regeln NULL war (SE 0.69, Welch-t < 2). Die iter-28-Flip-
Lesung bleibt als Buchhaltung stehen; ihr Inhalt war
„Gap liegt im Rausch-Band DIESES Blocks", nicht „die Kante ist tot".
Richtungskonsistent mit D=0.05 k=1 (frisch t=−5.48, ebenfalls unter der
Kontrolle): an D=0.05 sitzen die nominal-Dosis-Zellen k=1 UND k=10
systematisch UNTER ihrer Kontrolle.

### Verdicte

- **V1 (SE-Überlebende): SURV_ALL** — 4/4, alle positiv.
- **V2 (D=0.10 k=3): DEEP3_FRESH_REPLICATED** — |t| = 6.98.
- **V3 (Kante): EDGE_SIGNALS** — |t| = 4.21, negativ.

**VERDICT: SURV_ALL | DEEP3_FRESH_REPLICATED | EDGE_SIGNALS**

## Hypothesen-Lesung

1. **Der Zensus schließt die Buchhaltungs-Linie**: nach iter-30 ist JEDE
   überlebende Label-Position der Damköhler-Linie auf drei Ebenen
   getragen (n3-Artefakt-Buchhaltung, SE/t-Buchhaltung,
   out-of-sample-Replikation an einem disjunkten Block mit frischer
   Kontrolle). Der robuste Kern umfasst jetzt **8 Zellen**: die 5
   SE-Überlebenden (D=0.1 k=3, D=0.15 k=5, D=0.3 k=30/300/1000) plus die
   3 iter-29-Befunde (D=0.05 k=1, D=0.15 k=14, D=0.25 k=1).
2. **Die Vorzeichenstruktur ist block-stabil**: alle 8 Zellen behalten
   ihre Richtung über alle getesteten Blöcke. Die Landschaft hat eine
   gemischte, aber konsistente Geometrie: D=0.25 k=1 und der
   D=0.30-Hoch-k-Kanal positiv; D=0.05 k=1, D=0.05 k=10 (Kante) und
   D=0.15 k=14 negativ.
3. **Die Effektstärken sind NICHT seed-block-stabil** — der Befund der
   Iteration: dieselbe Zelle (k_edge=10) liest 0.69 SE (Block 200-209)
   gegen 4.21 SE (Block 310-319). Der Kontroll-Floor ist im Mittel
   stabil (alle 12 Anker-Messungen über 3 Blöcke konsistent), aber die
   Zell-Abstände variieren blockweise um Faktor ~6. Effektstärken-Angaben
   ohne Block-Angabe sind damit unvollständig; die SIGNALE sind real,
   ihre Tiefen sind Block-Eigenschaften.
4. **Die Kanten-Lesung von iter-28 wird präzisiert, nicht revidiert**:
   iter-28s „die Kante kippt unter SE" bleibt als Block-200-209-Befund
   korrekt; iter-30 zeigt, dass die Kante an frischen Seeds ein
   negatives Signal trägt. Die Historie (dreifach reproduziert) trug
   nicht über die Effektstärke — aber die Zelle selbst ist nicht tot,
   sie ist block-fluktuierend.
5. **Damköhler-Linie konsolidiert**: nach fünf Korrektur-Iterationen
   (25→26→27→28→29→30) steht ein kleiner, mehrfach getragener Kern; die
   DISTINCT/NULL-Feinstruktur der Iterationen 11→26 bleibt entwertet.

## Nicht behauptet

- Alle Labels sind Eigenschaften DES METRIK-STACKS (LZ/corr/tMI +
  Kontrollpools + Registry-Subsets + Gitter), nicht der Zelle und nicht
  von syn3A; keine Aussage über reale Enzymdichten.
- Für k_edge=10 wird nur der Block 310-319 als Signal-Träger gemeldet —
  kein Claim, dass das Signal an allen Blöcken vorhanden ist (an
  200-209 war es unter beiden Regeln NULL); die Block-Fluktuation SELBST
  ist der Befund.
- D=0.45 bleibt rechtszensiert; die 3 iter-29-Zellen wurden hier nicht
  erneut gelaufen (ihre dritte Ebene ist die iter-29-Replikation selbst).
- Kein rückwirkender Eingriff in frühere Buchungen; die iter-28-Flip-
  Tabelle bleibt als Block-Buchhaltung stehen.

## Epistemischer Status / Vorbehalte

- Der Zensus testet 6 von 8 Kern-Zellen; die 3 iter-29-Befunde sind
  einmal out-of-sample getragen (ein frischer Block), die 5 SE-Zellen
  zweimal (iter-28-Tier-A-Buchhaltung + iter-30-dritter-Block; D=0.1 k=3
  dreimal inkl. iter-28-Teil-2). Ein vollständiger Vier-Block-Zensus
  (~240 Läufe) wäre die nächste Konsolidierungsstufe.
- Die Effektstärken-Variation (0.69 vs 4.21 SE für dieselbe Zelle) ist
  auf n=1-Block-Vergleichen gemessen — eine systematische
  Block-Stabilitäts-Messung (σ_effect über ≥3 Blöcke je Zelle) steht
  aus.
- Walltime ~15 min; Smoke-Phase inkludierte 3 echte Verifikations-Läufe
  (~10 s) für Gate (c).

## CORREKTUR-LOG

1. **Lint**: W292 (fehlendes Newline) in der Erstfassung — vor dem Lauf
   per ruff --fix behoben; danach clean.
2. **Gate-(c)-Redesign (vor dem echten Lauf, im Smoke-Stadium)**: die
   ursprüngliche Registrierung verlangte, die iter-29-`t_fresh`-Werte aus
   Artefakten bit-identisch zu recomputen — unmöglich, weil die iter-29-
   t_Referenzen gegen die frische 300-309-Kontrolle gerechnet wurden und
   deren per-seed-Vektoren vom iter-29-Harness nicht persistiert wurden.
   Ersatz (gleiche Stärke): Cross-Session-Determinismus — Reproduktion
   des Laufs seed 300 je Kandidaten-Zelle und Vergleich gegen die
   persistierte per-seed-Zeile. VOR dem echten Lauf mit 3 ECHTEN Läufen
   verifiziert: 3/3 bit-identisch. Registrierungstext entsprechend
   aktualisiert (vor dem Lauf, nicht danach).
3. **Smoke-Test mit gemockten Läufen** (Methode iter-27…29): gesamtes
   `main()` in-process — Struktur, Konsistenz-Tabelle, Verdict-Pfade und
   result.json validiert. Gate (c) zeigt unter Mocks notwendigerweise
   False (Mock-Ausgabe vs echte Artefakte); seine Verifikation erfolgte
   real (siehe #2).
4. **Echter Lauf** (Task b1j5qqclg): vollständig, exit 0, alle Gates
   PASS, 0 Abbrüche (vierte Iteration in Folge ohne Crash).

## Nächste Vektoren

1. **VECTOR_EFFECT_BLOCK_STABILITY** (~240 Läufe): σ_effect über ≥3
   Blöcke je Kern-Zelle — quantifiziert die in Hypothese 3 gefundene
   Block-Fluktuation der Effektstärken; danach wären die 8 Kern-Zellen
   mit Tiefen-Intervallen statt Punkt-Schätzungen gebucht.
2. Reserviert: iter-19b **VECTOR_SHELL1_CASCADE** (Schale-1-Anomalie,
   Turing-Linie).
3. **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13);
   **VECTOR_UV_SYNC_REOPEN** (iter-16).

## Artefakte

- `fresh_survivor_census.py` — Registrierung + Harness (lint-clean)
- `result.json` — Gates, Konsistenz, 6 Zellen mit Verdicts, Verdicte
- `run_log.txt` — vollständiges Laufprotokoll
- `experiment.md` — diese Buchung