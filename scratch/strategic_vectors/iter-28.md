# iter-28 — VECTOR_SIGNAL_RELATIVE_RECLASS + VECTOR_DEEP_CELL_REPLICATION

**Verdict: RECLASS_SEVERE | SE_H0_MARGINAL | SE_RECOVERS_NONE | SE_RULES_DIVERGE | DEEP_REPLICATED · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Direkte Konsequenz von iter-27 H0_DOMINANT: (a) Welche der 22 gebuchten
DISTINCT-Zellen überleben ein effektgrößen-basiertes Kriterium
(se_units ≥ 2.0, Gap in Einheiten von σ_ctrl10·√(2/3)) statt der
rausch-dominierten 0.05-Schwelle? (b) H0-Rate dieses Kriteriums
(in-sample, deklariert)? (c) Recovery auf der NULL-Seite? (d) Kongruenz
SE-Regel vs Welch-t-Regel (n=10)? (e) Out-of-sample-Replikation der drei
tiefen, in iter-27 nicht gelaufenen Zellen?

## Design

Teil 1 (0 GPU-min): reine Buchhaltung auf den persistierten per-seed-
Vektoren von iter-26/27 — SE-Reclass über alle 43 Zellen (Tier A = 30
iter-27-Zellen, Tier B = 13), H0 über 2100 Kontroll-Tripelpaare je
Anker, Welch-t als registrierte Sekundärregel, corr/tmi-Inertie
berichtend. Gates: K1 (22 DISTINCT-se_units bit-identisch zu iter-27
K-D), K2 (cls_n3 30/30). Teil 2 (~30 GPU-Läufe): D=0.10 k=3,
D=0.30 k=300, D=0.30 k=1000 × Seeds 200-209, Welch-t gegen die
iter-27-10-Seed-Kontrolle.

## Resultat

- **Gates alle PASS** — REGISTRATION_ERROR nicht ausgelöst.
- **V1: RECLASS_SEVERE** — 17/22 (77 %) gebuchte DISTINCT kippen auf
  NULL, exakt die registrierte Erwartung aus iter-27 K-D. Die 5
  SE-Überlebenden = exakt die 5 iter-27-Tiefen-Zellen: D=0.1 k=3
  (3.52 SE), D=0.15 k=5 (2.10), D=0.3 k=30 (2.61), D=0.3 k=300 (2.94),
  D=0.3 k=1000 (2.78). **Auch die dreifach reproduzierte Kante
  k_edge=10 (D=0.05) kippt** (0.69 SE) — ihre Historie trägt nicht über
  die Effektstärke.
- **V2: SE_H0_MARGINAL** — False-DISTINCT 8.7/6.6/6.5/0.2/6.4 %
  (D=0.05/0.10/0.15/0.25/0.30): Verbesserung ~3-4× gegenüber der
  Altschwelle (18-27 %), aber > 5 % auf 4/5 Ankern — dieselbe
  Ausreißer-Struktur trägt jetzt in die SE-Einheiten.
- **V3: SE_RECOVERS_NONE** — 0/21 NULL-Zellen steigen auf; strikt
  konservativer, keine neuen Inseln.
- **V4: SE_RULES_DIVERGE** — 16/30 (53 %); ALLE 14 Divergenzen in EINER
  Richtung (SE=NULL, t=DISTINCT): die Welch-t-Regel (n=10) dominiert die
  3-Seed-SE-Regel. Stärkste neue Kandidaten: D=0.25 k=1 (t=+4.60),
  D=0.15 k=14 (t=−3.81), D=0.05 k=1 (t=−3.42), D=0.1-Hoch-k-Plateau
  (t≈2.1-2.2 — die iter-26-Diskordanz-Spalte liest sich als schwache
  systematische Verschiebung). Tier-A-Buchhaltung auf existierenden
  Seeds, NICHT out-of-sample.
- **V5: DEEP_REPLICATED** — 3/3 out-of-sample: D=0.1 k=3 |t|=7.91
  (deutlich stärker als die SE-Schätzung 3.5 — Zelle enger gestreut als
  Kontrolle, konservativer Vorbehalt von iter-27 bestätigt), D=0.3
  k=300 |t|=4.05, D=0.3 k=1000 |t|=3.96; alle oberhalb ihrer Kontrollen.
- **corr/tmi-Inertie** feuert nie (max 0.0005/0.0013) — der gesamte
  Reclass-Stack ist LZ-getrieben.

## Lesung

- **Robust**: der D=0.30-Hoch-k-Kanal (k=30/300/1000) als robustester
  Struktur-Befund der Damköhler-Linie — in allen drei Ebenen sichtbar
  (n3-Artefakt, SE, out-of-sample-t); D=0.15 k=5 (2.1 SE); die
  Korrekturbewegung ist monoton abwärts (22 → 7 → 5 DISTINCT-Überlebende).
- **Entwertet**: die DISTINCT/NULL-Feinstruktur der Iterationen 11→26;
  auch die Kante k_edge=10 an D=0.05 trägt nicht unter SE (was bleibt:
  k=1 mit t=−3.42, nicht out-of-sample).
- **Offen**: die t-Regel hat selbst keine gemessene H0-Rate — D=0.25 k=1
  ist Kandidat, kein Befund; der Kontroll-Seed-Vorbehalt von Teil 2
  (dieselben 10 Seeds) erst mit frischen Kontroll-Seeds entfernbar.
- **Nicht behauptet**: In-sample-Kalibrierung von Kriterium + H0;
  keine rückwirkende Revision der n=3-Buchungen.

## Nächste Vektoren

1. VECTOR_T_RULE_CANDIDATES (~40 Läufe): t-Regel-H0 über 5/5-Splits
   (126 je Anker, 0 GPU) + out-of-sample-Replikation von D=0.25 k=1,
   D=0.15 k=14, D=0.05 k=1 an frischen Seeds (300-309).
2. reserviert iter-19b: VECTOR_SHELL1_CASCADE.
3. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13); VECTOR_UV_SYNC_REOPEN
   (iter-16).

Artefakte: `scratch/experiments/iter-28/{signal_reclass.py, result.json,
run_log.txt, experiment.md}`