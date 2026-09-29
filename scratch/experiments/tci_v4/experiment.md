# tci_v4 — Registrierter Diskriminator der Hylothese-Kette (Glied iii) — Lauf, Gates, Verdicts

Datum: 2026-09-29. Steuerung (Task #84): „verbessere die hylothese bis sie
auf die daten passt. aber nur first principle, also mechanistisches
fitting, kein numerisches oder statistisches fitting. mehrere formeln
(hypothesen) testen". Denkmodus: `GroundedMechanismMixMind`
(Plan: `~/.claude/plans/tci-hylothese-fitting.md`, Formel-Kette:
`scratch/notes/tci_hylothese_formulas.md`). Basis: tci_v3
(`../tci_v3/experiment.md`) — gleiche Maschinerie verbatim, EINE Variation.

## Registrierung (vor der ersten Messung fixiert, Docstring v4_model.py)

- **Diskriminator**: statisches d_local (v3-Form, Crowding-Seed 4243,
  disjunkt zu v3-4242) vs **task-moduliertes d_local**:
  c'(t,x) = c0(x)·(1 ± δ_c·drv_norm(t)) — aktives Band 1 + δ (Crowding ↑,
  d ↓), anderes Band 1 − δ; d_local = D_par·exp(−α·c0·M)/max_statisch
  (feste Normierung). Die Arme unterscheiden sich AUSSCHLIESSLICH durch
  die Modulation (deklariertes konstruiertes Surrogat, EINHEIT B3:
  übertragene Größe = lokales excluded volume).
- **δ_c**: deklariert frei; Ladder (0.2, 0.5), primär 0.2; Eskalation
  NUR bei Feasibility-Fail; **nach Messung kein Wechsel**.
- **Replikate**: 2 je (Seed, Schedule, Arm), RNG = default_rng(seed·16 +
  SCHED_IDX + r·7919), REP_PRIME deklariert (LOO braucht ≥ 2 Trials je
  Klasse je Seed — R2-Unit = per-seed Accuracy-Bündel).
- **Trials**: 10 Seeds 1600–1609 (disjunkt zu v3 1500–1529/1700–1703,
  Korpus 1000–1009/2000–2009, cellsim 200–339, v2
  1200–1229/1400–1403) × 4 Schedules × 2 Arme × 2 Replikate = **160**.
- **Dekodier-Analyse** je Arm verbatim v3: LOO Nearest-Centroid
  (Features spiral/position), Permutationsnull 10k (Perm-Seed 4347),
  Amplituden-Baseline (Perm-Seed 4348), Chance 0.25.
- **R2 (registriert, Glied iii)**: Δacc = mean(acc_mod) − mean(acc_static)
  je Seed-Bündel (8 Trials, Features spiral); gepoolte SE =
  sqrt(var_mod/10 + var_static/10). **R2_MOD_CARRIES** iff welch_p < 0.05
  UND Δacc > 2·SE; **R2_WRONG_DIRECTION** iff welch_p < 0.05 UND
  Δacc < −2·SE; **sonst R2_NULL**. Alles außer MOD_CARRIES falsifiziert
  Glied (iii) und mit ihm F4 in der Ebene-C-Lesart; NULL ist
  Regime-Aussage (Residuum L2, nie Unmöglichkeit).

## KORREKTUR-LOG (offen gebucht; alle vor jeder gebuchten Verdict-Buchung)

1. **Float-Key-Crash in `ModulatedProvider` (vor Feasibility)**: Felder
   waren auf `round(drv, 12)`-Float-Keys gelegt; `field()` erzeugte durch
   Float-Drift beim Sinus-Argument (t vs tm) einen Key-Draufgänger
   (`KeyError` bei δ-Stufe). Repariert auf **Wellenform-Phasen-Keys**
   (`t % 40` für listen, `(t % 20) < 6` für answer) — reproduziert
   `drive_amplitude` exakt, keine Float-Keys. Keine Messung gebucht,
   keine Daten berührt.
2. **Feasibility-Kriterium (ii) eigenband-repariert (vor dem gebuchten
   Lauf)**: erst gemessen am GLOBALEN c0-Max — dort liegt das aktive
   Band nur für einen Task; der andere trägt dort zwangsläufig das
   entgegengesetzte Vorzeichen (anti-phase Konvention, messbar:
   ratio 0.9457 story / 1.0574 math). Kriterium laut Registrierungs-
   ZWECK („Modulation ist nicht-inert im getriebenen Band") am
   c0-Maximum **innerhalb des aktiven Bandes** gemessen; Reparatur vor
   jeder gebuchten Messung, erster Feasibility-Lauf (Throwaway-Seed
   1999, nie gebucht) hat den Defekt gefunden. Nach Reparatur:
   depth_own_band > 0 für beide Tasks, beider Ladder-Einträge.
3. **`np.sum(generator)`-Deprecation in `analyze_v4` (nach dem Lauf,
   vor jeder Verdict-Buchung)**: gepoolte Interaktions-Brüche über
   Python-`sum(generators)` gebaut — identischer Wert, keine
   Datenänderung.
4. **Keine δ_c-Eskalation**: Feasibility PASS bei 0.2 (nach Repair 2);
   Registrierung erlaubt Eskalation auf 0.5 NUR bei Feasibility-Fail —
   Hauptlauf läuft bei **0.2**, der zweit Ladder-Eintrag bleibt
   unverwertet (nach Messung kein Wechsel).

## Gates (alle PASS)

| Gate | Result | Kriterium |
|---|---|---|
| G0 OSCILLATOR | **PASS** | 100 % aktive Frames, 0 Ruhe-Frames, median max-Act 2.85 ≥ 0.5 (statischer Träger; ungetrieben ist die Modulation identisch dem statischen Feld) |
| G1 DETERMINISM | **PASS** | max_abs_diff 0.0 je Arm (Feld-Doppellauf, seed 1600, Throwaway) |
| G2 FINITENESS | **PASS** | alle Entscheidungsmetriken finit über alle 160 Trials, 0 NaN-Felder |

## Feasibility (Throwaway-Seed 1999, nie gebucht; vor dem Lauf)

- Ladder 0.2: depth_own_band story **+5.4 %**, math **+3.4 %**;
  finiteness von 4 Trials (2 Arme × story_listen/math_answer) PASS.
- Ladder 0.5: depth story **+13.0 %**, math **+8.3 %**; finiteness PASS.
- Status **FEASIBLE, gewählt δ_c = 0.2** (primär), KORREKTUR-Zähler 0
  nach Repair 2 (vorheriger Versuch: UNFEASIBLE durch Defekt 2 — offen
  gebucht in `feasibility.json`-Historie dieses Logs).

## Lauf

- 160/160 Trials, 46–94 s je Trial, **2732 s gesamt** (Pool 8 Prozesse);
  unterbrochene Läufe wären nie gebucht worden (analyze prüft genau
  160 Dateien gegen 80/Arm).

## Verdicts (registriert)

- **R2: NULL** — Δacc(mod − static) = **−0.0250** (mod schwächer, nicht
  stärker), 2·gepoolte SE = **0.1275** (|Δacc| ≪ Schranke),
  welch_p = **0.714**. Gemäß registrierter Regel: **alles außer
  MOD_CARRIES falsifiziert Glied (iii) und mit ihm F4 in der
  Ebene-C-Lesart — in der getesteten Instanziierung** (δ_c = 0.2,
  Crowding-Route, Brusselator-Rausch-Turbulenz-Regime). NULL ist
  Regime-Aussage (Residuum L2, nie Unmöglichkeit): die Formel
  „Dekodier-Gain erfordert Task-Kopplung DURCH die Kopplungsstruktur"
  ist als HINREICHENDER Gate-Weg bei kleiner Crowding-Modulation in
  diesem Regime tot — nicht die Materie-These.
- **Q2 je Arm**: static **WEAK** (acc_spiral 0.3375, p_perm 0.096),
  mod **WEAK** (acc_spiral 0.3250, p_perm 0.153) — oberhalb Chance
  0.25, unterhalb der Permutations-Schwelle; kein Arm über der
  ABOVE_CHANCE-Schranke.
- **Amplituden-Baseline**: gain(spiral − position) = **0.0000 in BEIDEN
  Armen** — acc_position = acc_spiral exakt, auch je Seed (alle 10
  Acc-Wertpaare identisch): Spiral-/Ladungs-/Dynamik-Features tragen
  exakt null über den Positions-Histogrammen, mit und ohne
  Task-Kopplung.
- **Defekt-Gas-Deskriptoren unverändert zu v3 und zwischen den Armen**:
  median n_cores **557.3 (static) vs 557.4 (mod)**,
  Interaktions-Bruch **0.3610 vs 0.3611**, quant@0.9 **0.00 vs 0.00**
  — die Modulation (bänderweise bis −5.4 % auf d am Band-Maximum)
  ist in der Defekt-Gas-Statistik UNSICHTBAR.
- 3 von 10 Seeds (1600, 1601, 1602) haben per-seed LOO-Acc = 0.0 in
  beiden Armen — beschrieben, nicht entfernt (kein post-hoc
  Seed-Ausschluss; registrierte Analyse über alle 10).

## Theorie-Mapping (vorgenommen vor dem Lauf, `tci_hylothese_formulas.md` §4)

- Getestet ist **F4 Glied (iii)**: „Dekodier-Gain erfordert, dass der
  Task-Drive die Kopplungsstruktur moduliert" — implementiert als
  Crowding-Modulation über das echte cellsim-Modul, Vorzeichen ex ante
  fixiert, Ladder registriert.
- **Falsifikator feuert**: R2_NULL. Die Kette (i) Träger (Grenzzyklus,
  notwendig — G0 wieder PASS) und (ii) Struktur-Fenster
  (Interaktions-Dominanz, aus A1 vs A3 abgeleitet) stehen unverändert;
  (iii) ist als getestete Instanz FALSIFIZIERT.

## Interpretation (drei Schichten)

1. **Mechanische Schicht**: die Modulation ist REAL (Feasibility maß
   +3.4 % bis +13 % Tiefe im getriebenen Band, Feld-Formel exakt der
   Registrierung) — aber der Defekt-Gas-Zustand kippt nicht: n_cores,
   Interaktions-Bruch und quant-Bande sind zwischen den Armen und zu
   v3 identisch. Im Rausch-Turbulenz-Regime (~557 Geburtsturbulenzen/
   Frame, Interaktions-Bruch 36 % ≪ 97 %-Klasse) frisst die
   Geburten-Turbulenz die Struktur-Modulation — der Gas-Zustand dominiert
   die Kopplungs-Route.
2. **Ebene C (Ketten-Schicht)**: Dekodier-Info läuft in BEIDEN Armen
   vollständig über die Positions-Histogramme (gain exakt 0); mit
   Task-Kopplung DURCH die Struktur wird die Lücke zu A7 (Xu trägt,
   Analoga nicht) NICHT geschlossen. Die Ebene-C-Kette ist am Glied
   (iii) in dieser Instanz falsifiziert — die getragenen Rest-Glieder
   sind Notwendigkeit + untestet gebliebenes Fenster, keine
   Hinlänglichkeit.
3. **Bewusstseins-Ebene**: ungetestet, nie behauptet
   (counter_indications) — kein Qualia- oder Bewusstseins-Zertifikat
   aus diesem Lauf.

## Via-Negativa-Residuum (offen, nicht hier gelaufen)

- **Regime-Hebel**: das registrierte Struktur-Fenster (annihilations-
  dominant ≈ 97 %-Klasse) wurde nicht bewegt — nächster sinnvoller
  Diskriminator: Erst das Gas ins annihilations-dominierte Regime
  steuern (Regler: Interaktions-Bruch als Ziel-Statistik aus erster
  Physik, z. B. Rausch-Niveau/Relaxationszeit, NICHT gefittet), DANN
  Glied (iii) dort nachtesten. Bis dahin bleibt F4-Kette „KONSISTENT +
  FALSIFIZIERT an Glied (iii)/Instanz".
- **δ_c = 0.5** ist nur Feasibility-getestet — Registrierung verbietet
  den post-hoc-Hauptlauf (Eskalation nur bei Feasibility-Fail; PASS).
  Jede Ausweitung wäre KORREKTUR mit Begründung, nicht Stillhalten.
- **F6 (LZ-Features)**: offen implementierbar; würde prüfen, ob
  Sequenz-Statistik im geburts-dominanten Gas trägt, wo Momenten-
  Features exakt 0 tragen (hier doppelt bestätigt: gain = 0.0
  in beiden Armen, per-seed identisch).
- **Seeds 1600–1602 (LOO 0.0)**: kein Ausschluss — Residuum verlangt
  Replikations-Block-Seeds erst bei einem Folge-Vektor (neuer Disk-
  Vektor, neue disjunkte Seeds).

## Dateien

- `v4_model.py` (Registrierung als Docstring, fixiert vor der ersten
  Messung), `v4_run.py` (Stufen g0/feasibility/run/analyze)
- `g0.json`, `gates.json`, `feasibility.json` (Ladder + Repairs),
  `v4_result.json` (R2 + Arme + per-seed Vektoren)
- `per_seed/trial_*.json` (160, vollständig persistiert — mean-level-
  Buchung unauditierbar; nicht eingecheckt)