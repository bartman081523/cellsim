# tci_v3 — Wirbel-Träger im Zellmedium (Brusselator + Crowding) — registrierter Lauf

Datum: 2026-09-28. Steuerung: „schaue wie wir diese vortices in cellsim
bekommen, du musst die theorie konstruieren". Denkmodus:
`GroundedMechanismMixMind` (Plan: `~/.claude/plans/tci-vortices-cellsim.md`,
Theorie: `scratch/notes/tci_vortices_theory.md`).

## Registrierung (vor der ersten Messung fixiert, Docstring v3_model.py)

- **Träger**: Brusselator pro Voxel (A=1, B=3 → Grenzzyklus-Garantie
  analytisch: FP (1,3), Spur = B−1−A² = 1 > 0, Det = A² = 1 > 0 →
  instabiler Fokus → Poincaré–Bendixson), 128²-Gitter, DT=0.02,
  5000 Schritte, Snapshot alle 5 Schritte → 1000 Frames.
- **cellsim-Einbettung**: D lokal moduliert durch das echte Modul
  `cellsim.modules.crowding.compute_crowding` (6 geseedete Blobs,
  V_ex = 5e4 Å³, voxel 100 nm, α=4.0 → d = D·exp(−α·crowding),
  auf D_par normiert). α=0 → exakt uniform.
- **Gates**: G0 OSCILLATOR (neu), G1 DETERMINISM, G2 FINITENESS —
  Kriterien wörtlich; **Q1–Q5 unverändert aus v2 übernommen**.
- **Seeds**: Pilot 1700–1703, Haupt 1500–1529, Switch 1500–1509,
  Perm 4342/4343 (crowd), 4242 (crowding-Blobs) — disjunkt zu
  Korpus 1000–1009/2000–2009, cellsim 200–339, v2 1200–1229/1400–1403.
- **Registrierte Selektions-Regel**: Ecke mit median n_cores ≥ 5 &
  Dauer ≥ 3 & quant@0.9 in ≥ 80 % Kern-Frames; sonst Default hält.
- **Neu (R1)**: α=0-Kontrolle (30 Trials) am selektierten Punkt,
  einziger Unterschied zum Hauptlauf = Crowding-Modulation;
  SHIFTED iff Welch-p < 0.05 UND |Δmedian| > 2·gepoolte SE
  → sonst falsifiziert TH3 (Crowding als Nukleationsquelle).

## KORREKTUR-LOG (offen gebucht)

1. **Pilot-Launch getötet**: erster Pilot-Lauf wurde bei 580 s
   hart beendet (`timeout`, exit 143) — Trials dauern 30–60 s, nicht
   die geschätzten 5–10 s. Der unterbrochene Lauf wurde **nie gebucht**
   (pilot schreibt nur am Stufen-Ende); Wiederholung im Hintergrund
   vollständig (1454 s, alle 36 Trials, exit 0).
2. **stage_control-Fix VOR dem Kontroll-Lauf**: Kontrolle liest
   selection.json (selektierter Punkt) mit `d_local=None` statt am
   Default-Punkt zu laufen — crowd vs. control unterscheiden sich
   ausschließlich im Crowding (registrierte TH3-Diskriminierung).
   Fix ist vor der ersten Kontrolle gebucht; Kontrollen liefen danach.
3. **Selektion**: keine Ecke des 9-Punkt-Rasters erfüllt alle drei
   Kriterien (quant@0.9@80 % nirgends erreicht — Maximum 0.64 bei
   D=1.0/σ_n=0.02, aber dort n_cores 1–4, Dauer 2). Registrierte
   Fallback-Regel greift: **Default hält (D=0.6, σ_n=0.1)** — keine
   Abweichung, folglich kein KORREKTUR-Eintrag nach Regel; dokumentiert
   in `pilot_result.json`.
4. G1-Doppellauf auf dem Crowding-Feld (build_crowding_d im Loop):
   max_abs_diff = 0.0.

## Gates (alle PASS)

| Gate | Result | Kriterium |
|---|---|---|
| G0 OSCILLATOR | **PASS** | 100 % aktive Frames, 0 Ruhe-Frames, median max-Act 2.85 ≥ 0.5 |
| G1 DETERMINISM | **PASS** | max_abs_diff 0.0 (Doppellauf, Crowding-Feld) |
| G2 FINITENESS | **PASS** | alle Entscheidungsmetriken finit, 0 NaN-Felder (NaN offen gebucht, konservativ gewertet) |

## Lauf

- Pilot: 36 Trials (9 Konfigs × 4 Seeds), 1454 s.
- Kontrolle: 30 Trials (α=0, uniform D, story_listen, am selektierten
  Punkt), ~27 min.
- Haupt: 30 Seeds × 4 Schedules + 10 Switch (Crowding), 7711 s.
- per_seed/ vollständig persistiert (160 Dateien = 120 + 10 + 30).
- `analyze`-Assert: 120 + 10 + 30 = 160 ✓, Gates vorhanden ✓.

## Verdicts (registriert)

| Vektor | Verdict | Zahlen |
|---|---|---|
| Q1 SPIRAL_PROPAGATION | **ABSENT** (0/30) | pro Trial: n_cores ≥ 5 ✓ (median ~480–640), Dauer ≥ 3 ✓ (exakt 3.0), **quant@0.9@80 % ✗ (0.00 überall)** — Kriterium scheitert allein an der Quantisierungs-Bande |
| Q2 DECODE | **WEAK** | 0.275 vs Chance 0.25; gain 0.0; Nullmodell 0.2503; p_perm 0.4345; paired_p 1.0 |
| Q3 DIRECTION_RECONFIG | **REALIZED** (10/10) | \|Δp_cw\| > 2·SE in 10/10 Seeds — **in Q1-ABSENT-Regime**: Asymmetrie ist ein schedule-gekoppeltes Feature des rauschdominierten Felds (~550 unquantisierte Kerne/Frame), NICHT von gerouteten Spiralen; nicht promotet |
| Q4 INTERACTION | **NOT_DOMINANT** | 36.1 % (5.03e6/1.39e7 Terminations) vs ≥ 80 % |
| Q5 CHARGE_INFO | **NOT_BEYOND_POSITION** | gain exakt 0.0 (acc_spiral = acc_position = 0.275) |
| R1 CROWDING_NUCLEATION | **SHIFTED** | crowd 555 vs control 524 (Δ +31 ≈ +5.9 %), Welch p = 0.0013, \|Δmedian\| > 2·gepoolte SE → **TH3-Falsifikator feuert NICHT** |

Xu-Anker bleiben Interpretations-Vergleich (Registrierung): ~19
Spiralen/Frame, 48.3 % Dekodierung vs 25 %, ~97 % Annihilation — hier:
550 Kerne/Frame (Rausch-Turbulenz), 0.275 Dekodierung, 36 % Interaktion.

## Theorie-Mapping (vorgenommen VOR dem Lauf, `tci_vortices_theory.md` §7)

1. **G0 scheitert?** Nein — Grenzzyklus trägt Phase (v2-K1-Lektion
   analytisch + numerisch bestätigt: Ruhepunkt trägt KEINE Phase,
   Grenzzyklus tut es).
2. **G0 besteht + Q1 falsifiziert → Träger-Theorie tot in dieser
   Medium-Klasse** ← **dieser Ausgang ist eingetreten**. Präzise:
   hinreichend ist der Grenzzyklus NICHT — er erzeugt abundant
   Kerne (~550/Frame, Dauer 3 Frames), aber **keine persistenten
   quantisierten** (quant@0.9 = 0.00 in allen 130 Haupt-Trials; im
   Pilot auch in der leisesten Ecke nur 0.64). Die Quantisierungs-
   Bande (v2-wörtlich) ist im registrierten 9-Punkt-Raster
   unerreichbar.
3. TH3-Falsifikator (unabhängig registriert): **feuert nicht** —
   Crowding-Heterogenität (echtes cellsim-Modul) ist eine schwache,
   aber systematische Nukleationsquelle (R1 SHIFTED). In einem
   Q1-ABSENT-Regime ist das Nukleation von Rausch-Turbulenz-Kernen,
   nicht von Spiralen.
4. TH4 (Dekodierung): **nicht interpretierbar** (registriert: nur
   bei Q1 REALIZED) — Q2/Q5 scheitern an Chance/gain 0, konsistent.

## Interpretation (drei Schichten)

- **Gemessen**: Grenzzyklus → Phase überall (G0), dichte
  Kern-Population (~550/Frame) mit Dauer 3 Frames, quant@0.9 = 0.00
  (Kerne im Rausch-Band, nicht in der ±1-Topologie-Bande), Interaktion
  36 %, Dekodierung auf Chance, gain 0; R1: Crowding verschiebt
  Kernzahl systematisch (+31 median, p = 0.0013).
- **Was das bedeutet**: der Brusselator-Träger mit Crowding-Brücke
  produziert Rausch-dominierte, kurzlebige Phasen-Turbulenz, nicht
  Xu-artige persistente Spiralen.
  Die registrierte Träger-Theorie (Grenzzyklus als hinreichende
  Bedingung) ist in dieser Medium-Klasse falsifiziert. Was
  korroboriert wurde: (a) die Träger-*notwendigkeit* aus v2 (K1:
  Ruhepunkt trägt keine Phase) — der Grenzzyklus trägt Phase; (b)
  Crowding-Heterogenität als messbare Nukleationsquelle (R1) — die
  echte cellsim-Brücke wirkt, schwach (+6 %) aber systematisch.
- **Verdict-ändernd**: ein Regime außerhalb des registrierten
  Rasters (z. B. σ_n ≪ 0.02, D > 1, andere A/B, oder Nichtlokalität)
  könnte die Quantisierungs-Bande tragen — das ist eine NEUE
  Hypothese mit NEUER Registrierung, keine Nachbesserung dieses
  Vektors.

## Via-Negativa-Residuum

Der Q1-Realisierungs-Window liegt — falls er für Brusselator-Klasse-
Medien existiert — außerhalb des registrierten (D × σ_n)-Gitters
(gemessen im Pilot: quant@0.9 ≤ 0.64 überall; Schwellen v2-wörtlich).
Das ist eine Aussage über Measure + Modell (L2), nie über
Unmöglichkeit. Die Xu-Ebene-C-Struktur bleibt am Original getragen
(X2–X5), in beiden Analog-Medien (FHN v2, Brusselator v3) nicht
reproduziert.

## Dateien

- `v3_model.py` (Registrierung + Analyse), `v3_run.py` (Stufen)
- `g0.json`, `gates.json`, `selection.json`, `pilot_result.json`,
  `v3_result.json`, `per_seed/*.json` (persistiert, nicht committed)