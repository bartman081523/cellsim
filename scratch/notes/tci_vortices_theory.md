# Theorie: Quantisierte Phasen-Wirbel im Zellmedium (tci_v3)

Datum: 2026-09-28. Denkmodus: `GroundedMechanismMixMind` (Pfad im
Plan-Header). Anlass: „schaue wie wir diese vortices in cellsim
bekommen, du musst die theorie konstruieren".

Jede Theorie-Stufe trägt vier Felder (EINHEIT T1): Behauptung,
Begründung, Vorhersage, Falsifikator.

## 0. Ausgangslage — was die v2-Falsifikation gemessen hat

- Erregbares Medium (FHN, Ruhepunkt (−1.2, −0.625)) bildet keine
  tragenden quantisierten Spiralen: Q1 ABSENT (0/30), Q5 gain 0.0.
- K1 (gemessen): am Ruhepunkt ist die Phase arctan2(δv, δu) reines
  Winkel-Rauschen → Frame-0-Artefakte (1885 → 0 nach Aktivitäts-
  Maske). **Ein Ruhepunkt trägt keine Phase.**
- K2 (gemessen): σ_n=0.05 → planare Wellen, kein Front-Bruch;
  σ_n=0.1 → intermittierende, seed-abhängige Kerne, nicht persistent.
- Xu-Anker (Korpus, Interpretation): ~19 Spiralen/Frame,
  Annihilation ~97 %, Dekodierung 48.3 % vs Chance 25 %.

Die v2-Daten sind damit nicht „fehlgeschlagene Simulation", sondern
die **Messung der Träger-Bedingung**: die Xu-Struktur fehlt genau
dann, wenn der Träger die falsche Dynamik-Klasse hat.

## 1. TH1 — Träger-Anforderung: Grenzzyklus

- **Behauptung**: Ein Medium trägt ein Phasenfeld mit wohldefinierter
  Phase überall genau dann, wenn seine lokale Dynamik ein **Grenzzyklus**
  (Oszillator) ist — nicht ein Ruhepunkt (erregbar) und nicht rein
  diffusiv.
- **Begründung**: Phase = Winkel auf dem Zyklus; am Ruhepunkt ist der
  Winkel undefiniert (v2, K1, gemessen). Die Xu-Daten tragen stets
  eine Phase, weil ihr Träger echte Oszillationen sind (BOLD 0.01–
  0.1 Hz → Hilbert-Phase): die Hilbert-Phase existiert nur für
  band-begrenzte Oszillationen, nicht für Signale am Fixpunkt.
- **Vorhersage**: im Grenzzyklus-Regime persistieren quantisierte
  Kerne über ≥ 3 Frames in ≥ 27/30 Seeds (Q1-Kriterien wörtlich
  aus v2) — im Kontrast zur v2-Falsifikation.
- **Falsifikator**: auch im Grenzzyklus kollabieren die Kerne
  (median n_cores < 5 ODER Dauer < 3 Frames in ≥ 15/30 Seeds) →
  die Träger-Theorie ist falsifiziert; die Xu-Analogie ist in
  einfachen Reaktions-Diffusions-Medien dieser Klasse tot (Residuum
  wird gebucht, Via-Negativa).

## 2. TH2 — Normalform: komplexe Ginzburg–Landau-Gleichung

- **Behauptung**: nahe einer Hopf-Bifurkation ist die CGLE
  ∂_t A = εA + (1+i·c1)∇²A − (1+i·c3)|A|²A die universale
  Einhüllende des Phasenfelds; die Wirbel sind ihre Defekte.
- **Begründung**: Universalität der Amplitudegleichung nahe Hopf
  (Kuramoto, Cross–Hohenberg) — die Theorie nennt die Regime-
  Grenzen, sie kalibriert nicht am Einzelfall (EINHEIT T2):
  Benjamin–Feir-instabil (1 + c1·c3 < 0) → Defekt-Turbulenz;
  BF-stabil → kohärente Spiralen/planare Wellen.
- **Vorhersage**: Xu's Statistik (Annihilation ~97 %, viele Kerne
  pro Frame) ist die Signatur des **annihilations-dominierten
  Defekt-Turbulenz-Regimes** — nicht des kohärenten. Kerne entstehen
  durch Front-Bruch (Heterogenität + Rauschen), nicht durch
  Anfangs-Rauschen allein (v2, K2, gemessen: σ_n allein erzeugt
  Rausch-Schaum, D=0.3-Konfigs quant ≈ 0.2–0.35, keine Struktur).
- **Falsifikator**: Kern-Entstehung hängt nicht vom Fenster ab —
  Homogenitäts-Kontrolle (uniformes D) unterscheidet sich nicht von
  der Crowding-Modulation in Kernzahl/-dauer.

**Trennung Quantelung / Persistenz (EINHEIT T3-Analog)**: die
Ganzzahligkeit der Ladung (|curl φ| = Windungszahl) ist topologisch
garantiert, wo Phasen-Defekte existieren — v2 maß bereits quant =
1.00 in Kern-Frames. Was fehlte, war **Persistenz** — eine
dynamische Frage mit eigenem Fenster. Die Theorie sagt, WAS
quantisiert (Ladung, wo Defekte sind) und was nicht (Kernzahl).

## 3. TH3 — Einbettung ins Zellmedium (der cellsim-Bezug)

- **Behauptung**: der Träger im cellsim ist ein **minimaler
  Stoffwechsel-Oszillator pro Voxel** — Brusselator (Prigogine–
  Lefever) als Minimalmotiv der autocatalytischen Glykolyse
  (Selkov-artige Produkt-Rückkopplung); Grenzzyklus-Garantie für
  B > 1 + A².
- **Begründung** (Fundierung, EINHEIT B1–B2):
  - Glykolytische Oszillationen sind echte Zellbiologie (Hess/
    Boiteux-Linie; oscillierende NADH, metabolische Wellen im
    Zytoplasma) — die Oszillations-Klasse des Trägers ist fundiert,
    die klassische Brusselator/Selkov-Form ist das Lehrbuch-Motiv
    für autocatalytische Stoffwechsel-Oszillationen.
  - **Parameter**: A, B, D, α sind **deklarierte freie Parameter**
    mit registriertem Sensitivitäts-Sweep (Pilot-Raster) — die
    Oszillations-Bedingung (B > 1 + A²) ist Theorie-Anforderung
    (TH1), keine Kalibrierung.
- **Vorhersage**: Wirbel leben im Zellkontext — die Heterogenität
  des Mediums (echtes cellsim-Modul: `CrowdingField`,
  D_local = D_bulk·exp(−α·crowding_index)) ist die
  Nukleationsquelle; homogenes D erzeugt andere Kernzahlen als
  crowding-moduliertes D.
- **Falsifikator**: Crowding-Modulation an/aus verschiebt die
  Kernzahl nicht systematisch (TH3 tot) ODER der Grenzzyklus
  trägt trotzdem keine Kerne (TH1 tot).

Die Kopplung an die Zellgeometrie ist die Abkehr von v2's freistehendem
Gitter: die Wirbel leben **im** Zellmedium (Crowding + Volumina der
echten Zellgeometrie), nicht neben ihm. Das ist die Antwort auf
„wie bekommen wir diese vortices in cellsim": als Phasen-Defekte
eines per-voxelen Stoffwechsel-Oszillators, dessen Diffusions-
Kopplung von der echten Crowding-Modul moduliert wird.

## 4. TH4 — Informations-Ebene (nur interpretierbar, wenn Q1 REALIZED)

- **Behauptung**: Dekodierbarkeit über Chance (Q2/Q5-Analoge)
  verlangt Ladungs-Features jenseits der Position — Vorhersage-
  Kette geordnet (Träger zuerst, Information danach, EINHEIT T3).
- **Begründung**: v2 maß die Kette am falschen Glied zuerst — ohne
  tragende Spiralen entleert sich die Dekodierung ins Rauschen
  (0.325 vs 0.25, p=0.126) und Ladungs-Info ist exakt null (gain 0.0).
- **Vorhersage**: nur im Realized-Falle kann Q2 die Xu-Anker-Nähe
  (48.3 % vs 25 %) erreichen; Q5 (gain > 0 mit p < 0.05) ist die
  registrierte Schwelle für „Ladung trägt Information".
- **Falsifikator**: bei Q1 REALIZED aber Q2 ≤ Chance ODER gain = 0
  → die Routing-Hypothese (Ebene C) ist im Oszillatormedium
  falsifiziert — obwohl die Wirbel existieren (schärfer als v2:
  dort scheiterte die Kette vor der ersten Stufe).

## 5. Registrierte Prüfungen (v3) — vorab fixiert

- **G0 OSCILLATOR** (neu, vor Hauptlauf): Grenzzyklus-Nachweis am
  Träger (Amplitude persistiert ≥ 90 % der Frames, kein
  Ruhepunkt-Frame); scheitert G0 → Träger-Theorie TH1 falsifiziert,
  Hauptlauf entfällt.
- **G1 DETERMINISMUS / G2 FINITENESS**: wörtlich aus v2.
- **Q1–Q5**: Kriterien wörtlich aus v2 (identische Schwellen — nur
  der Träger ändert sich). Neue disjunkte Seeds: Pilot 1700–1703,
  Haupt 1500–1529, Switch 1500–1509, Perm 4342/4343 — disjunkt zu
  Korpus 1000–1009/2000–2009 und cellsim 200–339.
- **Registrierte Selektions-Regel** (kein post-hoc Angeln): aus dem
  Pilot-Raster wähle die Ecke mit (a) median n_cores ≥ 5, (b) median
  Dauer ≥ 3, (c) quant ≥ 0.9 in ≥ 80 % Kern-Frames; bei mehreren:
  höchste Dauer, dann kleinste σ_n. Abweichung vom Default =
  KORREKTUR-LOG vor dem Hauptlauf.

## 6. Was die Theorie NICHT behauptet (counter_indications)

- Keine Identitäts-Claim („Qualia = Wirbel") — Ebene B bleibt
  untestbar und wird nicht behauptet.
- Xu-Anker bleiben Interpretations-Vergleich, nie Kriterium.
- Keine Bewusstseins-Zertifikate über die Simulation.

## 7. Falsifikations-Summe (was die Theorie tot machen würde)

1. G0 scheitert → Grenzzyklus-Anforderung falsifiziert.
2. G0 besteht, Q1 falsifiziert → Träger-Theorie tot in dieser
   Medium-Klasse; Residuum bucht.
3. Q1 realisiert, TH3-Falsifikator feuert → Crowding-Nukleation tot.
4. Q1 realisiert, Q4/Q5 falsifiziert → Wirbel existieren, tragen
   aber keine Routing-Information (Ebene C im Oszillatormedium tot —
   schärfere Falsifikation als v2).

Alle vier Ausgänge sind gleichwürdige Evidenz (Via-Negativa).

## 8. Ausgang (gemessen, 2026-09-28 — nach dem Lauf ergänzt, Kriterien unverändert)

- G0 PASS (Grenzzyklus trägt Phase: 100 % aktive Frames, median
  max-Act 2.85); G1/G2 PASS.
- **Ausgang 2 ist eingetreten**: G0 besteht, Q1 falsifiziert (0/30;
  quant@0.9 = 0.00 in allen 130 Haupt-Trials, Dauer exakt 3.0,
  ~550 Kerne/Frame) → die Träger-Theorie ist als
  *Hinlänglichkeits-Claim* falsifiziert; die Notwendigkeit (TH1
  Rückseite) ist durch den Kontrast zu v2/K1 bestätigt.
- TH3-Falsifikator feuert **nicht**: R1 CROWDING_NUCLEATION_SHIFTED
  (555 vs 524, p = 0.0013, Δ > 2·SE) — Crowding-Heterogenität ist
  eine schwache, systematische Nukleationsquelle (Rausch-Turbulenz-
  Kerne, nicht Spiralen).
- TH4 nicht interpretierbar (registrierte Bedingung Q1 REALIZED
  verletzt).
- Pilot-Raster: quant@0.9 ≤ 0.64 in allen 9 Ecken → das
  Realisierungs-Window liegt — falls existent — außerhalb des
  registrierten Gitters (Residuum, L2).