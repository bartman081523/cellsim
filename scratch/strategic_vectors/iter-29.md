# iter-29 — VECTOR_T_RULE_CANDIDATES

**Verdict: T_H0_CALIBRATED | CAND_REPLICATED_ALL | CAND_ABS_ALL | EXPL_NOT_REPLICATED · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Direkte Konsequenz von iter-28 V4 = SE_RULES_DIVERGE und dem
Struktur-Vorbehalt: (a) Wie hoch ist die False-DISTINCT-Rate der
Welch-t-Regel selbst (dominant in iter-28, nie kalibriert)? (b)
Replizieren die drei stärksten iter-28-t-Kandidaten (D=0.25 k=1 t=+4.60,
D=0.15 k=14 t=−3.81, D=0.05 k=1 t=−3.42) an FRISCHEN Seeds (300-309) mit
FRISCHER Kontrolle? (c) Repliziert das D=0.10-Hoch-k-Plateau
(explorativ, Vertreterin k=30)?

## Design

Teil 1 (0 GPU): H0 der t-Regel über alle 126 ungeordneten disjunkten
5/5-Splits der 10 Kontroll-Seeds je Anker (Nominal df ≈ 8 ≈ 8 %), plus
die 2100 3/3-Tripelpaare. Gates: K1 (3 Kandidaten-t-Werte aus iter-27-
Artefakten bit-identisch zu iter-28, EXAKT dieselbe welch_t-Funktion
importiert), K2 (Determinismus doppelt). Teil 2 (80 GPU-Läufe ≈ 12 min):
4 Anker × 10 frische Kontrollen + 3 Kandidaten × 10 + 1 Explorativ ×
10, Seeds 300-309 (disjunkt zu 200-209), iter-25-Harness VERBATIM.
STRICT = |t_fresh| ≥ 2.0 UND Vorzeichen-Match; K-C berichtend:
Konsistenz frische vs iter-27-Kontrollen (z-Score).

## Resultat

- **Gates alle PASS** — REGISTRATION_ERROR nicht ausgelöst.
- **V1: T_H0_CALIBRATED** — 5/5-Split-Raten 0.0/4.0/4.8/0.0/5.6 %
  (Nominal 8 %); 3/3-Tripel 4.7-7.9 % (Nominal 11.6 %). Die t-Regel
  liegt ÜBERALL unter Nominal — der Ausreißer-Mechanismus, der die
  positionsweise Paar-Regel aufblähte (18-27 % False-DISTINCT),
  DÄMPFT die t-Statistik (Ausreißer vergrößern s und drücken t).
- **V2: CAND_REPLICATED_ALL (3/3 strict)** — alle drei Post-hoc-
  Kandidaten überleben frische Zell-Seeds UND frische Kontrolle mit
  substanziellem t: D=0.05 k=1 −3.42→**−5.48**, D=0.15 k=14
  −3.81→**−8.57**, D=0.25 k=1 +4.60→**+12.06** (das stärkste
  Einzelsignal der gesamten Damköhler-Linie). Vorzeichenstruktur
  block-stabil (zwei negativ, einer positiv — dieselben Richtungen
  wie iter-28). Per Registrierung: Promotion zu Befunden.
- **V4: EXPL_NOT_REPLICATED** — das D=0.10-Hoch-k-Plateau verliert
  seine Vertreterin (k=30: t 2.15→**1.01**). Die iter-26-Diskordanz-
  Spalte ist damit in der dritten Buchhaltungs-Ebene entwertet.
- **K-C (berichtend)**: frische Kontrollen im Mittel konsistent
  (|z| ≤ 1.29), aber 3/4 Pools um Faktor 3-6 ENGER (σ ~0.01 vs
  0.03-0.06) — die Ausreißer-Vorkommen sind SEED-BLOCK-abhängig; die
  iter-27/28-H0-Inflation wurde teils von genau diesem Block getragen.

## Lesung

- **Robust**: der robuste Kern der Landschaft ist jetzt:
  D=0.25 k=1 (+12.1), D=0.15 k=14 (−8.6), D=0.05 k=1 (−5.5),
  D=0.1 k=3 (iter-28, t=7.9), D=0.3 k=30/300/1000 (noch gegen den
  alten Block) — die t-Regel ist das erste Instrument, das
  KALIBRIERT (≤ Nominal) und MÄCHTIG zugleich ist.
- **Entwertet**: das D=0.10-Hoch-k-Plateau (dritte NULL-Ebene); die
  Rausch-Band-Breite ist selbst eine Seed-Block-Eigenschaft — alle
  gegen den 200-209-Pool normalisierten Claims tragen diesen Vorbehalt.
- **Offen**: die verbleibenden SE-Überlebenden (D=0.15 k=5, D=0.3
  k=30/300/1000) und die Kante k_edge=10 tragen noch den
  Kontroll-Seed-Vorbehalt — ein frischer Zensus (~70 Läufe) würde
  jedes überlebende Label dreifach tragen.
- **Nicht behauptet**: df-approximierte H0 (Statistik-Familie, nicht
  exakter n=10/n=10-Test); alle Labels sind Metrik-Stack-Eigenschaften;
  Post-hoc-Auswahl war der Testgegenstand, nicht eine Bestätigung.

## Nächste Vektoren

1. VECTOR_FRESH_SURVIVOR_CENSUS (~70 Läufe): frischer Zensus der 6
   verbleibenden Labels (D=0.15 k=5, D=0.3 k=30/300/1000, k_edge=10
   D=0.05, D=0.1 k=3 gegen frische Kontrolle) — Anker D=0.30 braucht
   die fehlende frische Kontrolle.
2. reserviert iter-19b: VECTOR_SHELL1_CASCADE.
3. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13); VECTOR_UV_SYNC_REOPEN
   (iter-16).

Artefakte: `scratch/experiments/iter-29/{t_rule_candidates.py,
result.json, run_log.txt, experiment.md}`