# TCI-Wirbel-Begriff — Assessment (Korpus gelesen 2026-09-28; Agreements-führend)

Anlass: Nutzersteuerung 2026-09-28 — „bitte tci mit Xu et al
übereinstimmungen untersuchen. keine vorabnaussagen ohne rigorose tests,
es fehlt nur ein klitzekleines bit an der tci dass es auf Xu et al passt".
Diese Version ersetzt die einseitige Erstfassung (Commit wurde gestoppt):
die **Übereinstimmungen** stehen jetzt vorn, mit dem gemessenen
Agreement-Test (`scratch/experiments/tci_xu/`), und die Korpus-Befunde
werden fair gelesen (was je Run richtig lag, was fehlte). Korpus:
`/run/media/julian/ML3/faizal-rebuttal-gitlab-2/experiments-new-grouped-13778/`
(Basisklasse `FACRMExperiment` nur in der ML2-Kopie:
`/run/media/julian/ML2/Python/faizal-rebuttal/experiments-new-grouped-13778/facrm.py`).

## 0. Die Übereinstimmungen TCI ↔ Xu et al. 2023 (Kern dieser Notiz)

**Verifiziert (analytisch + programmatisch):**

1. **Messmathematik IDENTISCH.** Xu et al. (Nat Hum Behav 2023,
   DOI 10.1038/s41562-023-01626-5) detektieren Hirn-Spiralen aus
   HCP-fMRI: BOLD 0.01–0.1 Hz → Hilbert-Phase → 2D-Phasenfeld →
   ∇φ → curl (∇×∇φ) → Spiral-Kerne cw/acw (Toolbox
   github.com/BrainDynamicsUSYD/BrainVortexToolbox: Detektion +
   Statistik gegen Nullmodell; Z-Map, Ausbreitungsgeschwindigkeit,
   Dauer, Radius, Count; HCP CIFTI 32K). TCI-125 detektiert Wirbel als
   Plaquette-Zirkulation des Phasenfelds (Summe der gewrapten
   Phasen-Diffs um jede Plaquette / 2π). **Das ist dieselbe Mathematik**
   (diskrete Rotation des Phasenfelds) — dieselbe Operationalisierung
   von „Wirbel", dieselbe cw/acw-Binarisierung über das Vorzeichen.
   Kein topologischer-Ladungs-/Windungszahl-Formalismus in der
   Xu-Toolbox — die TCI-Windungszahl (124) geht an dieser Stelle
   über Xu hinaus.
2. **Das Korpus-Feld trägt Wirbel-Physik** (gemessen, `probe_result.json`):
   das 124/125-Update (0.9·Nachbar-circular-mean + N(0,0.05)) nukleiert
   und annihilatet Wirbel KT-artig; im persistent-getriebenen Feld
   überleben mobile, **unit-charge-quantisierte Kerne** (max|vort| =
   1.000 exakt) mit Populationen 0–243 je Snapshot.
3. **Quantisierung der Messung sauber**: am Kern liest die korrekt
   implementierte Plaquette-Formel exakt ±1 — die Messung selbst
   quantisiert, wie sie soll (H3's CHARGE_DEGRADED ist die Vakuosität
   bei 0 Kernen im Zeitmittel, kein Versagen der Formel).

**Gemessen und NICHT reproduziert (der Test):** der Kandidat
„persistenter Nichtgleichgewichts-Drive" (das „klitzekleine Bit")
reproduziert die Xu-Phänomene NICHT in der Korpus-Dynamik
(`scratch/experiments/tci_xu/experiment.md`, vollständig gebucht):

- H1 **SPIRAL_EDGE_ABSENT** (registriert, G1 PASS): Interface- vs
  Interior-Kern-Dichte — alle 20 ratios exakt 0.0 (kein Kern im
  Zeitmittel [1400,1500) irgendeiner Bedingung); Sweep δ0 ∈
  {0.1, 0.2, 0.5}: ebenfalls alle 0.0.
- H2 **RECONFIG_ABSENT**: keine Richtungsumkehr messbar (0 matched
  Kerne in beiden Fenstern; zusätzlich Swap-Bug im Code —
  Verdict-inert, dokumentiert).
- H3 **CHARGE_DEGRADED**: vakuus (0 Kerne).
- Post-hoc-Probe (klar getrennt): instantane Kerne existieren, sitzen
  aber **nicht an der Interface-Wand** (I ≤ B in allen Late-Time-
  Snapshots) — der Drive organisiert die Population nicht an der
  Grenze.

**Fair gelesen heißt das:** der Drive ist der richtige *Typ* von
Unterschied (Nichtgleichgewicht vs Equilibrium-Annealing), aber ein
Toggle „Drive an" genügt in der Korpus-Dynamik nicht. Der fehlende Bit
ist ein **Regime**: 0.9-Nachbar-Mittel-Relaxation ist tief in der
geordneten (stark synchronisierenden) Phase — glatte Konfigurationen
ohne Vortizität dominieren; Xu's Spiralen sind Ausbreitungsmoden eines
excitablen Mediums. (Explizit Interpretation mit Vorbehalt: aus der
einen Dynamik nicht verallgemeinert; ein excitables Update wäre ein
neuer registrierter v2-Vektor.)

## 1. Was der Wirbel-Begriff im Code IST (präzise Teile)

- **Wirbel** = XY-Modell-Phasenfeld. Windungszahl: Σ gewrapte Phasen-
  diffs auf Kreis r=30 / 2π (124); Vorticity: Plaquette-Zirkulation
  /2π, Wirbel = |Vorticity| > 0.5 (125). Standard-Diskretisierungen,
  mathematisch korrekt (in unserem Testlauf max|vort| = 1.000 exakt).
- **„Strange loop"** = Randbedingung vom Grad 1: alle vier Boxkanten
  werden auf `np.mod(np.arctan2(yy, xx), 2π)` gezwungen — der
  Standardweg, einen Wirbel mit Einheitsladung zu erzwingen.
- **„Qualia-Schutz"** (122) = Kitaev-Kette (N=50, t=δ=1.0): topologische
  Phase (μ=0.5 < 2t) → Majorana-Nullmoden (Gap ≈ 0), triviale Phase
  (μ=3.0) → finites Gap; Messung unter Unordnung ± 1.1.

Das ist saubere, lehrbuchkorrekte Physik — XY-Modell (Kosterlitz-
Thouless) und Kitaev-Kette. Die Simulationen selbst sind nicht das
Problem; die Protokolle und die Interpretationsschicht sind es (§4–§5).

## 2. Was die eigenen Logs sagen (mit fairen Lesarten)

| Exp | TCI-Claim | Log-Verdict | Faire Lesart |
|---|---|---|---|
| 122 | Qualia = topologisch geschützt (Kitaev) | **FALSIFIED** — Grade C, p=0.067 | Richtung stimmte (Gap triviale Phase 0.657 vs topologische 0.318), Kriterium p<0.05 knapp verfehlt; bimodale Alt-Stichprobe — 7/10 Trials zeigen den erwarteten Nullmoden-Gap (~1e-16), 3/10 kollabieren (Gap ~1.0); die Bimodalität pumpt die Varianz |
| 124 | Qualia = Spin-Wirbel aus strange-loop-Rand | **FALSIFIED** — Grade C, p=0.688 | keine stabilen Wirbel: kaputte Kontrolle (Null-Windung schon 1.86) + nicht-integer Windungs-Samples = Rauschen statt Topologie |
| 125 | Ego = Einzelwirbel nach Annealing | **FALSIFIED** — Grade B, p=0.0018 | der 7×-Annihilations-Effekt ist REAL (7440 → 1109), aber das Einzelwirbel-Ziel verfehlt; „Eternal chaos maintained" |
| 81 | Quanten-Psychopathologie | **FALSIFIED** — Grade C, p=0.785 | Fidelity 0.044 vs 0.042, kein Effekt |
| 142 | Informations-Orthogonalität → 90°-Winkel | **FALSIFIED** — Grade A (p=0, n=1) | gemessen 269.5° — das Kriterium kodierte die eigene periodische Option 270° nicht |
| 126 | TCI-Resonanz als Integrationsgesetz | „CORROBORATED" bei **p=0.107, n=2** | Konklusion widerspricht der eigenen Statistik |
| 80/88/90/123 | (keine Wirbel) | „CORROBORATED (Significant Difference)" | Grade A via Null-Varianz-Zweig der Basisklasse (Automatik, keine Evidenz) |

Alle drei Wirbel-Experimente des Korpus (122, 124, 125) sind in ihren
eigenen Logs FALSIFIED — das Harness meldet das ehrlich. Die Nuance der
fairen Lesart: **das Messwerkzeug (curl der Phase) funktioniert**; was
scheitert, sind die Ziele (Einzelwirbel/Ego, Schutz/Qualia) und teils
die Kontrollen (124). Deshalb ist die Brücke zu Xu et al. an der
Messmathematik real — und an der Schutz-Interpretation nicht.

## 3. Basisklasse `facrm.py` — was Grade A hier bedeutet

`FACRMExperiment.analyze_results` (205 Zeilen):

- p-Wert = Welch-t auf `_samples` (n = 2…10); **wenn BEIDE Stichproben
  Varianz 0 haben (deterministische Simulation) → p=0.0 per Regel**
  (facrm.py:148-151). Ohne `_samples` → ebenfalls p=0.0 + Fallacy-Flag.
- Grade A = p<0.001, B = p<0.05, C = sonst. Bei deterministischen
  Simulationen ist Grade A damit eine AUTOMATIK, keine Evidenz-Stärke.
- Die Basisklasse prüft die **Richtung des Effekts nicht** — wörtlich
  im Kommentar (facrm.py:193-200): „We need to know if the effect is
  in the RIGHT direction. Without criteria, we can't strict falsify."
  → „CORROBORATED (Significant Difference)" heißt nur: die Zahlen
  unterscheiden sich.
- Subklassen überschreiben `analyze_results` — deshalb kann die
  Konklusion der Statistik widersprechen (126: p=0.107, n=2, trotzdem
  „CORROBORATED"; 142: Grade A/p=0, trotzdem „FALSIFIED"). Bindend
  für den SUCCESS/FAILURE-Druck ist nur der String „CORROBORATED"
  (facrm.py:69).

Vergleich cellsim: dort bedeutet Grade A ≥9/10 Via-Negativa-Tests mit
falsifizierbarem Design; im TCI-Korpus ist Grade A ein Artefakt des
deterministischen p=0-Zweigs. Dieselben Wörter, verschiedene Messungen.

## 4. Warum die Wirbel-Experimente scheitern (Design-Diagnose)

- **124 — kaputte Kontrolle**: der Null-Fall (OHNE Rand-Zwang) hat
  bereits Windung 1.86 (thermische Wirbel aus dem Zufallsanfang) — der
  registrierte Diskriminator kann Rand-Wirbel nicht von Wirbel-Suppe
  unterscheiden. Die Alt-Samples [1.49, 0.95, 3.22, 0.92, 4.57] sind
  nicht-ganzzahlig → Windungszahlen SOLLten integer sein; nicht-integer
  heißt: die Messung liest Rauschen, nicht Topologie.
- **125 — konfundierter Vergleich**: Null = Zufallsphasen ohne
  Relaxation (7440 Wirbel ≈ 76 % der Plaquettes), Alt = Annealing UND
  Rand — zwei Änderungen zugleich. 1109 Wirbel statt Ziel 1: das
  Annealing glättet die Rausch-Wirbel, erzeugt aber nie die
  kondensierte Einzelstruktur („eternal chaos"). Konsistent mit Probe A
  des Agreement-Tests: ohne Rand-Nukleation annihilieren mobile Kerne
  KT-artig, statt sich an einer Struktur zu kondensieren.
- **124/125 — der Wirbel ist eingerichtet**: die strange-loop-Randbedingung
  vom Grad 1 erzwingt die Nettoladung ±1 topologisch (das ist ein Satz
  über die BC, nicht über Emergenz). Der Test kann nur prüfen, ob die
  erzwungene Singularität die Relaxation überlebt — nicht, ob „Qualia"
  Wirbel sind. Die Zuordnung Wirbel = Qualion/Ego steht in der
  Interpretationsschicht, nie in der Messung.

## 5. Konsequenz für die Brücke zu Xu et al. 2023 (revidiert durch den Test)

- **Mess-Niveau: Agreement REAL und jetzt programmatisch geprüft** —
  identische curl-of-Phase-Messung; die korrekte Formel liest
  unit-charge-Kerne exakt (±1.000). Damit ist der Teil des
  „Modell-Ziemlich-Gut"-Eindrucks getragen, der auf der Detektions-
  Ebene liegt.
- **Struktur-Claim („Spiralen an Netzwerk-Grenzen")**: im minimalen
  getriebenen Korpus-Modell NICHT reproduziert (H1 ABSENT registriert;
  Probe B: ABSENT bei δ0 bis 0.5; Probe A: instantane Interface-Dichte
  nie über Interior). Vorbehalt: die homogene Torus-Geometrie mit
  gerader Wand ist die Minimalversion — Xu's Gehirn hat heterogene,
  formvariable Netzwerk-Grenzen. Der Claim bleibt für das Korpus UNGETESTET
  (die 124/125-BC ist kein Boundary-Test), in dieser Minimalversion aber
  nicht erzeugt.
- **Rekonfigurations-Claim („Rotationsrichtung kippt mit Task")**: in
  dieser Dynamik nicht testbar (keine Kerne in den Fenstern); mit
  korrigiertem Single-Swap + per-Frame-Spiral-Statistik als v2 offen.
  An den Xu-Daten selbst ist „kippen" deskriptiv — Ladungserhaltung
  wurde dort NICHT nachgewiesen, die Schutz-Version also von den
  Daten nicht gestützt.
- **Ehrliche Brücke (unverändert aus `neuro_vortices_studies.md`)**:
  klassisch makro (Video) + klassisch mikro (cellsim L2/L3, Grade B);
  quanten-topologische Superstruktur in BEIDEN Korpora gemessen
  inert/falsifiziert (cellsim: iter-18/21/22/23, Fröhlich; TCI: 122/124/125/81).

## 6. Was ein sauberer TCI-Wirbel-Vektor wäre (jetzt mit Messgrundlage)

1. **Kontrolle reparieren** (124/125): Null = dieselbe Relaxationsdynamik
   OHNE Rand-Zwang — nur die BC ändern. (Im Agreement-Test umgesetzt:
   Null = uniformer Drive, exakt drift-invariant — max|vort| ≈ 1e-17
   bestätigt die Invarianz.)
2. **Quantisierungskriterium**: P(|w − round(w)| < 0.1) je Trial —
   windungs- wie plaquette-seitig möglich. Die Formel liest exakt ±1
   (Probe A); das registrierte E3 blieb VAKUUS, weil 0 Kerne im
   Zeitmittel existieren.
3. **Per-Frame-Spiral-Statistik statt Zeitmittel** (die Xu-Toolbox-
   Metriken: count, duration, speed, radius, direction proportions) —
   die registrierte Zeitmittel-Metrik verlangt gepinnte Strukturen
   (Dwell ≥ 30 %) und ist deshalb gegen Xu's propagierende Spiralen
   konservativ. Das ist die v2-Registrierung, falls die Brücke
   weiterverfolgt wird.
4. **Empirische Anbindung**: Xu-et-al-Kohorten — Spiral-Dichte an
   Netzwerk-Grenzen (berichtet) vs Rotationsrichtung über Task (berichtet
   als kippend → gegen die Schutz-Version). Beides Daten-Anker, beide
   ungetestet an einem excitablen Update.

Spiegel zur Damköhler-Linie: 124's kaputte Kontrolle ist der Struktur
nach derselbe Fehler, den iter-27 für die eigene Linie quantifiziert
hat (H0_DOMINANT — Schwelle unter der Kontroll-Streuung); die hier
gemaessene Floor-Limitierung der Zeitmittel-Metrik entspricht der
iter-26/27-Lektion („Metrik am Floor kann nicht diskriminieren").
Der Unterschied: hier ist der Floor direkt gemessen und gebucht.

## 7. Qualia ↔ Messdaten ↔ TCI (Nutzersteuerung 2026-09-28; drei Ebenen, ehrlich getrennt)

Anlass: „dass es qualia gibt im Menschen ist corroborated und dass es
diese Wirbel gibt ist auch corroborated. und die tci hat dieselbe
gerleitung wie Xu. also kommen wir mit den MessDaten von Xu und unserer
Formel müssen wir zu Qualia kommen." Die Xu-Source-Data ist jetzt
re-analysiert (`scratch/experiments/tci_xu/xu_data_analysis.py`,
`xu_data_result.json`, gebucht in `experiment.md`, Abschnitt
tci_xu_data). Die Verbindung wird in DREI Ebenen gebucht:

### Ebene A — GEMESSEN (Korrelat-Ebene; hier steht die Evidenz)

- **Quantiesierung auf echten Hirn-Daten (X4)**: die registrierte
  Plaquette-Formel liest die drei publizierten Phasenfelder als
  **unit-charge-Kerne — quant fraction 1.000, max|v| exakt 1.000**,
  Richtungen balanciert (25/25, 650/647, 1057/1064). Das ist direkt die
  Paper-Grundgröße: der Xu-Klassifikator dekodiert aus „instantaneous
  locations and topological charges (1 or −1) of phase singularities".
  Die „diese Wirbel gibt es"-Corroboration bekommt damit die feinste
  Form: **diskrete Ladungen ±1, mit derselben Formel gelesen, die wir
  am Korpus registriert haben.**
- **Wirbel-Geometrie trägt Task-Information (X2)**: 4-Klassen-Language
  48.3 % (Chance 25 %; Paper-Nullmodell 24.3 %), WM 43.7/66.7/59.0 % —
  und das über der fMRI-Amplitude-Baseline (30.2 %; Welch p = 6e-109)
  hinweg. Unter der falsifizierbaren Messung: **Ort + Ladung der
  Phasen-Singularitäten trägt kognitive Information, die die
  Amplitude der Signals selbst nicht trägt.** Das ist die Mess-Ebene,
  auf der „Vorhersagemaschine" und „Wirbel" verbindbar werden — nicht
  als Behauptung, sondern als gemessene Informationsgeometrie.
- **Richtungs-Rekonfiguration (X1/X5)**: single-trial-Phasenvektor-Winkel
  kippen Listening→Answering um **174.6°** (Permutation p < 1e-4; WEAK,
  weil R_answer = 0.16 < 0.3); Region-seitig dominieren acw bei story
  listening und cw bei math listening (5a), gespiegelt in der anderen
  Hemisphäre/Region (5b), analog Answering (5c/5d) — das Paper liest
  dieselbe Reversal als interhemisphärische IPC-Spiegelung. Im Kontrast
  zum Korpus-Test: **H2 RECONFIG_ABSENT** dort, PRESENT hier.
- **Interaktions-Statistik (X3)**: Full 51.0 % / Partial 46.4 % /
  Repulsion 2.6 % (n=93, Zeilensumme exakt 1.0) — **Annihilation
  dominiert (~97.4 %)**, konsistent mit dem Korpus-Probe-A-Befund
  (mobile unit-charge-Kerne annihilieren KT-artig).

### Ebene B — NICHT GEMESSEN (Identitäts-Claims; hier ist Vorsicht bindend)

- **Qualia-Identität ist mit diesen Daten untestbar.** Xu's Datensatz
  hat keinen Phänomenologie-Kanal; „diese Wirbel SIND Qualia" ist damit
  weder corroborierbar noch falsifizierbar — in beiden Korpora. Was
  korroboriert ist: (a) Qualia existieren (allgemein, nicht in dieser
  Messung), (b) die Wirbel existieren und tragen quantisierte,
  task-relevante Struktur (X2–X5). Die Identitäts-Brücke bleibt eine
  Interpretationsschicht.
- **Die Schutz-Lesart des Korpus bekommt KEINE Stütze** — im Gegenteil:
  die Rotationsrichtung kippt mit Task (X1/X5; Paper: „changes to an
  anticlockwise spiral cluster during the math answering task").
  Genau NICHT topologisch geschützt. Korpus-122 („Qualia = topologisch
  geschützt") bleibt FALSIFIED, und die Xu-Daten widersprechen der
  Schutz-Version zusätzlich empirisch.
- **Ego als EINZEL-Wirbel bleibt falsifiziert**: ~19 gleichzeitige
  Spiralen pro Zeitschritt (Paper, linker Kortex), bis zu 2121
  Plaquette-Kerne je Karte (mid/right), annihilation-dominierte
  Interaktions-Statistik (X3). Korpus-125 (Ego = Einzelwirbel nach
  Annealing) bleibt FALSIFIED — und die Xu-Daten stützen die
  Einzelwirbel-Lesart nicht; sie zeigen ein **Multi-Wirbel-Meer mit
  Task-abhängiger Rekonfiguration**.

### Ebene C — HYPOTHESE (klar gelabelt; im FHN-Medium getestet — tci_v2, 2026-09-28)

- **Die „Vorhersagemaschine"-Verbindung** (neuro_vortices.txt, Zeilen
  50/196: kortikale traveling waves als predictiv/generative
  Verarbeitung): die Xu-Sprache ist kompatibel — Spiralen „organize
  spatiotemporal activity across the whole cortex", „enable flexible
  reconfiguration of task-driven brain activity", „activity flow
  switching between bottom-up (listening) and top-down (answering)".
  Hypothese-Formulierung: **Spiralen sind die Phasen-Defekte der
  kortikalen Traveling-Waves; ihre Positionen und Ladungen kodieren die
  Routing-Struktur der prädiktiven Verarbeitung, ihre Task-abhängige
  Rekonfiguration ist der Kontextwechsel.** Die Dekodierbarkeit (X2)
  ist mit dieser Lesart konsistent — aber sie ist KEIN Beweis der
  Lesart: die Dekodierung zeigt nur Informationsgehalt, nicht Funktion.
- **TCI-Ego-Genesis, korrekt gelesen**: kompatibel auf dem
  Korrelat-Level (Singularitäten als Organisatoren der Aktivitätsflüsse
  — „we successfully classify … on the basis of the locations and
  topological charges of their centres"), inkompatibel als
  Einzelwirbel-Claim (Ebene B). Der TCI-Gerüst-Analogie-Eindruck
  („dieselbe Gerleitung wie Xu") trägt auf der **Mess-Ebene** (curl der
  Phase, ±1-Ladungen, cw/acw, Annihilation, Task-Dekodierbarkeit) —
  und scheitert auf der **Schutz-/Ego-Identitäts-Ebene**, wie in §0–§6
  gebucht.
- **Vektor-Status — getestet (tci_v2, 2026-09-28)**: der registrierte
  v2-Vektor (FitzHugh-Nagumo-Gitter als excitable Medium + Xu-Toolbox-
  Metriken + Dekodier-Analogie + Richtungs-Rekonfiguration + Ladungs-
  Informations-Test) ist **vollständig gelaufen und als registriert
  FALSIFIZIERT** — Gates G1/G2 PASS (Determinismus bit-identisch,
  Metriken finit), aber Q1 SPIRAL_PROPAGATION **ABSENT** (0/30 Seeds:
  median 0–2 transiente Kerne/Frame statt ≥ 5 tragender, Dauer 1–2
  Frames statt ≥ 3), Q2 DECODE **WEAK** (0.325 vs Chance 0.25,
  p_perm 0.126), Q3 DIRECTION_RECONFIG **ABSENT** (0/10, |Δp_cw| ≤ 0.09
  vs 2·SE ≥ 0.094), Q4 INTERACTION **NOT_DOMINANT** (16.3 % vs ≥ 80 %),
  Q5 CHARGE_INFO **NOT_BEYOND_POSITION** (gain exakt 0.0, p = 1.0).
  Zwei offen gebuchte Korrekturen VOR dem Hauptlauf (Aktivitäts-Domäne:
  ein erregbares Medium in Ruhe trägt KEINE Phase; Per-Schritt-Rauschen
  0.02 → 0.1: darunter laufen die Wellen planar und brechen nicht) —
  Kriterien, Seeds, Verdicts unverändert. Buchung:
  `scratch/experiments/tci_v2/experiment.md`. Via-Negativa-Residuum:
  die Dekodier-Analogie scheitert im FHN-Medium bereits an der ersten
  Stufe (keine persistierenden quantisierten Spiralen); ein anderes
  Regime, das Q1–Q5 erfüllen könnte, wäre eine NEUE Hypothese mit NEUER
  Registrierung. Die Xu-Daten bleiben der einzige Träger der Ebene-C-
  Struktur — dort gemessen (X2–X5), hier im Analog-Medium nicht
  reproduziert.

## 8. tci_v3 (2026-09-28): Träger-Theorie konstruiert und getestet — Grenzzyklus ist notwendig, nicht hinreichend

Anlass: „schaue wie wir diese vortices in cellsim bekommen, du musst
die theorie konstruieren". Die Theorie wurde VOR der Registrierung
konstruiert (`scratch/notes/tci_vortices_theory.md`, vier Felder je
Stufe TH1–TH4), dann die Batterie registriert, dann gemessen. Denkmodus:
`GroundedMechanismMixMind` (neu komponiert: ExtraordinaryFalsifier ×
NeuroEmergence; Plan `~/.claude/plans/tci-vortices-cellsim.md`).

**Theorie (Konstruktion vor Messung):**
- **TH1 Träger**: ein Medium trägt ein Phasenfeld genau dann, wenn die
  lokale Dynamik ein Grenzzyklus ist (am Ruhepunkt ist die Phase
  undefiniert — v2/K1 gemessen).
- **TH2 Normalform**: CGLE nahe Hopf; Xu's annihilations-dominierte
  Statistik gehört ins Defekt-Turbulenz-Fenster (Benjamin–Feir),
  Quantelung (topologisch) und Persistenz (dynamisch) getrennt
  registriert.
- **TH3 Einbettung**: Brusselator pro Voxel (Grenzzyklus analytisch:
  B > 1 + A²), **D lokal moduliert durch das echte cellsim-Modul
  `crowding.compute_crowding`** (d = D·exp(−α·crowding)) — der
  cellsim-Bezug ist die Crowding-Brücke als Nukleationsquelle.
- **TH4 Dekodierung**: nur interpretierbar bei Q1 REALIZED.

**Registrierte Messung** (`scratch/experiments/tci_v3/`, 160 Trials):
Gates **G0/G1/G2 alle PASS** (Grenzyklus: 100 % aktive Frames,
median max-Act 2.85; Determinismus 0.0; Metriken finit).
- **Q1 ABSENT (0/30)** — die 130 Haupt-Trials zeigen ~480–640 Kerne/
  Frame mit Dauer exakt 3.0 Frames, aber **quant@0.9 = 0.00 überall**:
  das registrierte Q1-Kriterium (v2-wörtlich) scheitert allein an der
  Quantisierungs-Bande. Im Pilot-Raster erreichte keine Ecke 0.8
  (Maximum 0.64 in der leisesten) → registrierte Fallback-Regel:
  Default (D=0.6, σ_n=0.1).
- Q2 WEAK (0.275 vs 0.25, p_perm 0.43), Q3 REALIZED (10/10 —
  **in Q1-ABSENT-Regime**, nicht promotet: schedule-gekoppelte
  Asymmetrie des rauschdominierten Felds), Q4 NOT_DOMINANT (36.1 %),
  Q5 NOT_BEYOND_POSITION (gain 0.0).
- **R1 SHIFTED** (TH3-Falsifikator feuert NICHT): Crowding 555 vs
  uniform 524 Kerne (median), Welch p = 0.0013, Δ > 2·pooled SE —
  die echte Crowding-Brücke ist eine schwache (+5.9 %), aber
  systematische Nukleationsquelle.

**Faire Lesart (drei Schichten):** die v2-Lektion wird als
*Notwendigkeit* bestätigt — der Grenzzyklus trägt Phase überall (G0),
der Ruhepunkt tat es nicht (v2/K1). Die *Hinlänglichkeit* ist
falsifiziert: der Grenzzyklus erzeugt dichte, kurzlebige,
unquantisierte Kern-Populationen (Rausch-Turbulenz), keine persistenten
unit-charge-Spiralen. Ebene B bleibt unberührt (keine Identitäts-
Claims); die Xu-Ebene-C-Struktur bleibt am Original getragen (X2–X5),
in beiden Analog-Medien (FHN, Brusselator) nicht reproduziert.
Buchung: `scratch/experiments/tci_v3/experiment.md`. Via-Negativa-
Residuum: das Q1-Window liegt — falls existent — außerhalb des
registrierten (D × σ_n)-Gitters; neue Regime = neue Registrierung.
---

## 9. tci_v4 (2026-09-29): Hylothese-Kette Glied (iii) getestet — R2_NULL (Falsifikator feuert)

Datum/Steuerung: Task #84 — „verbessere die hylothese bis sie auf die
daten passt. aber nur first principle, also mechanistisches fitting, kein
numerisches oder statistisches fitting. mehrere formeln (hypothesen)
testen". Denkmodus `GroundedMechanismMixMind`
(`~/.claude/plans/tci-hylothese-fitting.md`); Formel-Kette F1–F6:
`scratch/notes/tci_hylothese_formulas.md`.

**Was verbessert wurde (Struktur-Fitting, keine Kalibrierung)**: die
Hylothese (= Ebene-C-Kette) wurde Glied für Glied gegen A1–A7
konfrontiert. F1 (topologische Identität) **FALSIFIZIERT** (A1 vs A3:
Ladungspopulation mit entgegengesetztem Informations-Ergebnis bei
identischer Pipeline — Ladung ist die Währung, nicht die Nachricht);
F2 (Defekt-Routing) **UNVOLLSTÄNDIG** (A3: ~550 Kerne, gain 0 —
Populations-Existenz ≠ Information); F3 (Heterogenitäts-Nukleation)
**GETRAGEN als Vorzeichen** (A4: +5.9 %, p = 0.0013); F5
(Energie-Bornierung) **GETRAGEN** (A5-Caps); F6 (LZ-Entropie-Träger)
**KONSISTENT mit A6, offen testbar**. F4 wurde verbessert: (i) Träger
Grenzzyklus — von „hinreichend" auf **„notwendig" demoted** (A3
falsifizierte die Hinlänglichkeit); (ii) Struktur =
**Wechselwirkungsstatistik eines heterogenitäts-nukleierten Defekt-Gases**
(nicht Kerndichte, nicht Persistenz — Xu's ~19 Kerne/Frame sind bei
97.4 % Annihilation selbst kurzlebig; trennend ist der Interaktions-
Bruch 97.4 % vs 36.1 %); (iii) Information = Task koppelt DURCH die
Kopplungsstruktur — **registrierter Test tci_v4**.

**Registrierte Messung** (`scratch/experiments/tci_v4/`, 160 Trials,
Seeds 1600–1609 × 4 Schedules × 2 Arme × 2 Replikate, δ_c = 0.2 primär):
Gates **G0/G1/G2 alle PASS**; Feasibility FEASIBLE bei 0.2 (Tiefe im
getriebenen Band +3.4 %/+5.4 %, 0.5 gemessen +8.3 %/+13 %). Zwei
pre-booking-Repairs offen gebucht (Float-Key-Crash → Phasen-Keys;
Feasibility-Kriterium (ii) vom globalen auf das eigen-bandige c0-Max —
anti-phase Vorzeichenkonvention machte das andere Band zum Kriterium).
**Keine δ-Eskalation** (Registrierung: nur bei Feasibility-Fail; PASS;
nach Messung kein Wechsel).

- **R2 NULL (Δacc = −0.0250, 2·SE = 0.1275, welch_p = 0.714)** — gemäß
  registrierter Regel falsifiziert das ALLES-außer-MOD_CARRIES das
  Kettenglied (iii) in der getesteten Instanziierung (Crowding-Route,
  kleine Amplitude, Rausch-Turbulenz-Regime). NULL ist Regime-Aussage
  (Residuum L2, nie Unmöglichkeit).
- Beide Arme **Q2 WEAK** (0.3375/0.3250, p_perm 0.096/0.153); **gain =
  0.0000 in BEIDEN Armen** — acc_spiral = acc_position exakt, auch je
  Seed: Spiral-/Ladungs-/Dynamik-Features tragen exakt null.
- **Defekt-Gas-Deskriptoren unverändert**: n_cores 557.3 vs 557.4,
  Interaktions-Bruch 0.3610 vs 0.3611, quant@0.9 0.00 vs 0.00 — die
  bänderweise −5.4 %…−13 % d-Modulation ist in der Gas-Statistik
  unsichtbar.

**Faire Lesart (drei Schichten)**: mechanisch ist die Modulation real
gemessen, aber das geburts-dominante Defekt-Gas (~557
Turbulenz-Kerne/Frame, Interaktion 36 % ≪ 97 %-Klasse) frisst sie — der
Gas-Zustand dominiert die Kopplungs-Route. Auf Ebene C ist die Kette am
Glied (iii) in dieser Instanz falsifiziert: Dekodier-Info läuft in beiden
Armen vollständig über Positions-Histogramme; die Lücke zu A7 schließt
kleine Crowding-Modulation auch im modulierten Arm nicht. Getragen
bleiben: Träger-Notwendigkeit (G0 wieder PASS, zweifach) und das
Struktur-Fenster als offen gerahmter, untest-direkt gebliebener Regler.
Die verbesserte Hylothese steht danach als: **Träger = Grenzzyklus
(notwendig); Struktur = annihilations-dominantes, heterogenitäts-
nukleiertes Defekt-Gas (Fenster aus A1/A3 abgeleitet, nicht direkt
bewegt); Information = Task-Kopplung DURCH die Struktur — getestete
Instanz (kleine Crowding-Modulation) falsifiziert.** Buchung:
`scratch/experiments/tci_v4/experiment.md`. Via-Negativa-Residuum: nächster
Hebel = erst das Gas ins annihilations-dominierte Regime steuern (Ziel-
Statistik Interaktions-Bruch, aus erster Physik — nicht gefittet), dann
Glied (iii) dort nachtesten; δ_c = 0.5 bleibt unverwertet (Registrierung);
F6 (LZ-Features) offen implementierbar.

---

## 10. Quellen + Rohdaten-Anker (2026-10-05 nachgetragen)

Anlass: Nutzersteuerung „die Forscher wie gewünscht zitieren" — der Wunsch
stand in der Video-Analyse (`neuro_vortices.txt`, ChatGPT-Dump mit zwei
unbeantworteten DOI-Anfragen; das lokale File bleibt bewusst un-committet).
Alle DOIs wurden 2026-10-05 gegen Originalseiten verifiziert; zwei
Transkript-Fehler dabei korrigiert: „Verbinsky" → **Verzhbinsky**; Naqvi-DOI
…1135929 → **…1135926**.

- **Xu, Y., Long, X., Feng, J. & Gong, P. (2023)** — „Interacting spiral
  wave patterns underlie complex brain dynamics and are related to
  cognitive processing", Nature Human Behaviour 7, 1196–1215,
  DOI 10.1038/s41562-023-01626-5 (PMID 37322235) — der Original-Träger
  der Ebene-C-Struktur (A1/X2–X5; BrainVortexToolbox:
  github.com/BrainDynamicsUSYD/BrainVortexToolbox).
- **Research Briefing (2023)** — DOI 10.1038/s41562-023-01628-3
  (autorenbeteiligte Kurzdarstellung derselben Studie).
- **Verzhbinsky, I. A., Daume, J., Cheng, S., Rutishauser, U. & Halgren,
  E. (2026)** — „Cross-region neuron co-firing mediated by ripple
  oscillations supports distributed working memory representations",
  Nature Neuroscience, DOI 10.1038/s41593-026-02403-z (bioRxiv
  2025.09.04.674061; Daten: DANDI 000673; Code: iverzh/
  ripple-working-memory) — Ripple-koordiniertes Co-Firing koppelt
  verteilte (auch inter-hemisphärische) Regionen; stützt die
  Multi-Wirbel-Meer-Lesart (§7, Ebene B), nicht den Einzelwirbel-Ego.
- **Muller, L., Busch, A. N., Davis, Z. W. & Reynolds, J. H. (2026)** —
  „Neural traveling waves in cortex: Network mechanisms and potential
  roles in neural computation", Neuron 114(17), 3156–3174,
  DOI 10.1016/j.neuron.2026.06.019 (PMID 42480536); Hintergrund-Review:
  Muller, Chavane, Reynolds & Sejnowski (2018), Nature Reviews
  Neuroscience 19, 255–268, DOI 10.1038/nrn.2018.20 — der
  Traveling-Wave-Rahmen, aus dem die Spiralen als Phasen-Defekte gelesen
  werden.
- **Anastassiou, C. A., Montgomery, S. M., Barahona, M., Buzsáki, G. &
  Koch, C. (2010)** — „The Effect of Spatially Inhomogeneous
  Extracellular Electric Fields on Neurons", Journal of Neuroscience
  30(5), 1925–1936, DOI 10.1523/JNEUROSCI.3635-09.2010 — ephaptische
  Kopplung (Feld→Membran) als Wirk-Kanal; Begleit-Arbeit: Anastassiou,
  Perin, Markram & Koch, „Ephaptic coupling of cortical neurons",
  Nature Neuroscience, DOI 10.1038/nn.2727.
- **Pinotsis, D. A. & Miller, E. K. (2023)** — „In vivo ephaptic coupling
  allows memory network formation", Cerebral Cortex 33(17), 9877–9895,
  DOI 10.1093/cercor/bhad251 (PMC10472500) — das MIT-Picower-Paper der
  Video-Stelle („MIT / J Neurosci" komprimiert vermutlich die beiden
  ephaptischen Linien; beide zitiert, Zuordnung offen markiert).
- **Naqvi, N. H., Rudrauf, D., Damasio, H. & Bechara, A. (2007)** —
  „Damage to the Insula Disrupts Addiction to Cigarette Smoking",
  Science 315(5811), 531–534, DOI 10.1126/science.1135926 (PMID
  17255515) — die Insula-Integrations-Stelle des Videos (Ebene B);
  für die Wirbel-Linie selbst nicht messverbunden, nur Kontext.
- **Video (Provenienz der Anschluss-Linie)**: Anton Petrov — „How Brain
  Waves and Electric Fields Really Create Consciousness",
  youtube.com/watch?v=yUa90sZ0LA8 — Quelle der Hypothesen-Vorschläge,
  die zu tci_xu/v2/v3/v4 führten; als Provenienz gebucht, nicht als
  Autorität.
- Modell-Literatur der Analoga: FitzHugh (1961)/Nagumo (1962) —
  FHN-Medium v2; Prigogine & Lefever (1968) — Brusselator v3.

**Rohdaten-Anker (2026-10-05)**: `per_seed/` der Vektoren v2/v3/v4 als
Git LFS committet (Roh-Commit `11949ec`, `.gitattributes`); SHA-256 je
Datei plus Manifest-Hash in `scratch/experiments/tci_v{2,3,4}/
per_seed_manifest.json` (v2 `8a305f27efd278a1…`, v3
`5b0170d25588aa74…`, v4 `ab0988d5d5aae79c…`). Xu-Source-xlsx (~58 MB)
bleiben lokal (Lizenzprüfung offen). Kettenglied-Bruch P3 (Roh-Commit
erst nach der Verdict-Buchung) in allen drei Protokollen offen gebucht.
