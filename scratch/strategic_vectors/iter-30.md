# iter-30 — VECTOR_FRESH_SURVIVOR_CENSUS

**Verdict: SURV_ALL | DEEP3_FRESH_REPLICATED | EDGE_SIGNALS · Grade: B · Status: abgeschlossen (2026-09-24)**

## Frage

Abschluss des Zensus aus iter-29: (a) Replizieren die 4 verbleibenden
SE-Überlebenden (D=0.15 k=5, D=0.3 k=30/300/1000) an einem dritten,
disjunkten Seed-Block (310-319) mit frischer Kontrolle? (b) Trägt
D=0.10 k=3 (iter-28s stärkstes Signal) auch gegen eine FRISCHE Kontrolle?
(c) Zeigt die dreifach reproduzierte Kante k_edge=10 (D=0.05, in iter-28
gekippt) an frischen Seeds irgendein Signal?

## Design

100 GPU-Läufe: 4 Anker × 10 frische Kontrollen + 6 Zellen × 10, Seeds
310-319 (disjunkt zu 200-209 UND 300-309), iter-25-Harness VERBATIM.
Gates: K1 (se_units 4/4 bit-identisch zu iter-28; welch_t D=0.1 k=3
bit-identisch; iter-29-Verankerung per Cross-Session-Determinismus seed
300 — vor dem Lauf mit 3 ECHTEN Läufen verifiziert, 3/3), K2. STRICT
(Überlebende + D=0.1 k=3): |t| ≥ 2 UND positiv; Kante berichtend
beidseitig.

## Resultat

- **Gates alle PASS** — REGISTRATION_ERROR nicht ausgelöst.
- **K-B**: alle 4 frischen Kontrollpools konsistent (|z| ≤ 0.84) — drei
  unabhängige Blöcke im Mittel einstig, nur Ausreißer-Vorkommen und
  σ-Breite variieren.
- **V1: SURV_ALL (4/4)** — alle SE-Überlebenden repliziert, alle
  positiv: D=0.15 k=5 (t=3.17), D=0.3 k=30 (5.55), D=0.3 k=300 (4.70),
  D=0.3 k=1000 (4.84); LZ +0.035 bis +0.056.
- **V2: DEEP3_FRESH_REPLICATED** — D=0.1 k=3 auf VOLL unabhängiger Basis
  |t| = 6.98 (frische Zellen UND frische Kontrolle).
- **V3: EDGE_SIGNALS (Überraschung)** — die Kante k_edge=10 (D=0.05),
  an 200-209 unter BEIDEN Regeln NULL, zeigt am dritten Block ein
  krispes negatives Signal: t=−4.21, LZ −0.0157, Zell-σ nur 0.0186.

## Lesung

- **Robust**: der robuste Kern umfasst jetzt **8 Zellen** (5 SE-Überlebende
  + 3 iter-29-Befunde), alle block-stabil in Richtung, alle dreifach
  getragen (n3-Artefakt, SE/t, out-of-sample). Der D=0.30-Hoch-k-Kanal
  ist in vier Ebenen getragen.
- **Neuer Befund**: die **Effektstärken sind NICHT seed-block-stabil** —
  dieselbe Zelle liest 0.69 SE (Block 200-209) gegen 4.21 SE (Block
  310-319). Signale real, Tiefen Block-Eigenschaften; Effektstärken ohne
  Block-Angabe unvollständig.
- **Präzisierung**: iter-28s „Kante kippt" bleibt als Block-Buchhaltung
  korrekt; die Zelle selbst ist nicht tot, sondern block-fluktuierend
  (negativ, Richtungskonsistent mit D=0.05 k=1).
- **Nicht behauptet**: Metrik-Stack-Eigenschaften; kein Claim über
  nicht-getestete Blöcke; D=0.45 rechtszensiert.

## Nächste Vektoren

1. VECTOR_EFFECT_BLOCK_STABILITY (~240 Läufe): σ_effect über ≥3 Blöcke
   je Kern-Zelle → Tiefen-Intervalle statt Punkt-Schätzungen.
2. reserviert iter-19b: VECTOR_SHELL1_CASCADE.
3. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13); VECTOR_UV_SYNC_REOPEN
   (iter-16).

Artefakte: `scratch/experiments/iter-30/{fresh_survivor_census.py,
result.json, run_log.txt, experiment.md}`