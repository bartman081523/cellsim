# iter-27 — VECTOR_STOCH_CONTROL_METRIC

**Verdict: EDGE_STATUS_CHANGED_N10 | H0_DOMINANT | SPREAD_SYMMETRIC · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Dreifach motiviert (iter-24 Zellrauschen, iter-25 schwächste Anker-Zelle,
iter-26 NONMONOTONE + 22/43-Diskordanz): (a) False-DISTINCT-Rate der
registrierten Schwellen-Klassifikation unter reinem Kontroll-Rauschen,
(b) Stabilität der Kanten-/Band-Landschaft unter Verzehnfachung des
Seed-Budgets (n=3 → n=10), (c) Zell-seitige vs Kontroll-seitige
per-seed-Streuung.

## Design

iter-25-Harness VERBATIM (GPU); Seed-Budget n=10 (Seeds 200-209) auf 5
Ankern; 30 Zellen × 10 Seeds + 50 Kontrollen (355 Läufe gesamt). Zwei
Klassifikations-Regeln registriert: n=3 VERBATIM (iter-14/24/25,
seed-gepaart) zur K5''-Verankerung; n=10 NEU (per-seed classify gegen
ctrl_mean_10, DISTINCT ≥6/10, RUNAWAY ≥5/10). H0-Test als reine
Buchhaltung: alle 2100 ungeordneten disjunkten Tripelpaare der
Kontroll-Seeds je Anker. Bindende Gates K5'/K5'': 3-Seed-Submittel
bit-identisch und cls_n3 identisch zu iter-26 (30/30).

## Resultat

- **Gates alle PASS**: K1, K2 bit-identisch, K5' 30/30 bit-identisch,
  K5'' 30/30 übereinstimmend — REGISTRATION_ERROR nicht ausgelöst.
- **V2: H0_DOMINANT** — False-DISTINCT unter H0: 24.8 % (D=0.05),
  26.2 % (0.10), 26.6 % (0.15), 0.0 % (0.25), 18.3 % (0.30). Die
  registrierte 0.05-Schwelle liegt 2–3× UNTER der natürlichen
  Paar-Diff-Streuung (q95 |ΔLZ| 0.10–0.16). Mechanismus: positionsweise
  Seed-Paarung + ≥2/3-Vote = Ausreißer-Detektor, kein
  Mittel-Differenz-Test; D=0.25s 0 % ist strukturell (nur 1 Ausreißer-
  Seed — 2/3-Vote unmöglich), kein Qualitätsmerkmal.
- **V1: EDGE_STATUS_CHANGED_N10** — D=0.15: k=200 (iter-26s Trägerin
  von EDGE_NOT_LOCALIZED) kippt auf NULL; k_edge=100, lokalisiert,
  aber Band weiter inselig (interne NULLs 7/10/20/45). 7 der 22
  gebuchten DISTINCT-Labels kippen auf NULL (k=2 D=0.05; k=1/3/7/20/200
  D=0.15; k=30 D=0.25) — konsistent mit der H0-Prädiktion (~5.5
  erwartete Rausch-Labels); 1 neue Insel (D=0.15 k=14). Die D=0.05-
  Insel-Struktur (iter-26 interne NULLs 3/5/7) löst sich auf —
  iter-26-Frage (d) beantwortet: Zellrauschen, nicht Band-Struktur.
- **V3: SPREAD_SYMMETRIC** — Median-Ratios σ_zelle/σ_kontrolle
  0.13/0.79/0.90/0.89/0.72: Tau-leap entlastet, der Rausch-Floor ist
  ein Diffusions-/Initialbedingungs-Floor.
- **Signal-Tiefe**: 17/22 gebuchte DISTINCT-Zellen innerhalb 2 SE des
  Kontroll-Rauschens. Tiefste: D=0.10 k=3 (3.5 SE), D=0.30 k=300/1000
  (2.9/2.8), D=0.30 k=30 (2.6, überlebt n=10), D=0.15 k=5 (2.1,
  überlebt n=10).

## Lesung

- **Robust** (über n=10 + H0-Messung): Kante k_edge=10 an D=0.05
  (dreifach reproduziert); D=0.30 k=30; D=0.15 k=5; D=0.05 k=1
  (σ 0.0054, Gap 0.068 unter der Kontrolle; post-hoc t ≈ 3.6 mit
  n=10-Mitteln — nicht gebucht); Events-Plateau/Substrat-Sperre.
- **Tot**: die DISTINCT/NULL-Feinstruktur der Iterationen 11→26 als
  n=3-Schwellen-Landschaft (18–27 % false-DISTINCT auf 4/5 Ankern);
  iter-26s EDGE_NOT_LOCALIZED an D=0.15 (k=200 war Rauschen); die
  D=0.05-Inseln.
- **Korrekturkette geschlossen**: iter-25 (Kante 100) → iter-26
  (nicht lokalisiert) → iter-27 (wieder 100, lokalisiert; scharfe
  Kante existiert an D=0.15 unter keiner Regel).
- **Nicht behauptet**: Revision gebuchter n=3-Labels (n=10 ist NEUE
  Regel); H0-Rate als Zell-Eigenschaft (Metrik-Stack-Eigenschaft);
  n=10-Regel als rauschfrei (eigene H0-Rate mit 10 Seeds nicht
  messbar).

## CORREKTUR-LOG (Kurzfassung; voll in experiment.md)

1. Lauf #1: Abbruch nach K1/K2/50 Kontrollen — eager `dict.get`-Default
   (KeyError 0.05); `| tee` maskierte den Exit-Code.
2. Lauf #2: Abbruch nach erster Zelle — fehlender Seed-Filter in ctrl3
   (10 statt 3 Kontrollen, zip-strict ValueError).
3. Vor Lauf #3: gesamtes main() mit gemockten Läufen smoke-getestet
   (alle Buchhaltungs-Pfade + result.json-Struktur) — Methode bleibt
   stehen: vor GPU-Läufen mock-smoken.
4. Lauf #3: vollständig, exit 0, alle Gates PASS; ~62 min Walltime.

## Nächste Vektoren

1. VECTOR_SIGNAL_RELATIVE_RECLASS (0 GPU-min; effektgrößen-basierte
   Re-Buchung auf den persistierten per-seed-Vektoren)
2. VECTOR_DEEP_CELL_REPLICATION (~30 Läufe; D=0.10 k=3, D=0.30
   k=300/1000)
3. reserviert iter-19b: VECTOR_SHELL1_CASCADE
4. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13); VECTOR_UV_SYNC_REOPEN
   (iter-16)

Artefakte: `scratch/experiments/iter-27/{seed_budget.py, result.json,
run_log.txt, experiment.md}`