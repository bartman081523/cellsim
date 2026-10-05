# TCI ↔ Xu et al. — Agreement-Test (tci_xu)

Datum: 2026-09-28. Anlass: Nutzersteuerung — „stopp. bitte tci mit Xu et al
übereinstimmungen untersuchen. keine vorabnaussagen ohne rigorose tests, es
fehlt nur ein klitzekleines bit an der tci dass es auf Xu et al passt".

Kontext: Xu et al. 2023 (Nat Hum Behav, DOI 10.1038/s41562-023-01626-5;
Research Briefing 10.1038/s41562-023-01628-3; Toolbox
github.com/BrainDynamicsUSYD/BrainVortexToolbox) detektieren Hirn-Spiralen
aus HCP-fMRI via Hilbert-Phase → Phasenfeld → curl — dieselbe
Messmathematik wie TCI-125 (Plaquette-Zirkulation der wrapped phase diffs
/ 2π). Die TCI-Wirbel-Experimente (122/124/125) sind Equilibrium-Protokolle
(Rand-Zwang + Annealing); Xu berichtet propagierende, task-rekonfigurierbare
Spiralen. Kandidat für das fehlende „Bit": persistenter Nichtgleichgewichts-
Drive. Dieser Test prüft den Kandidaten — nicht die Schutz-Claims des
Korpus (die bleiben als geloggte FALSIFIED-Verdicts stehen).

## Registrierung

Kriterien, Gates, Seeds (1000–1009 E1 / 2000–2009 E2, disjunkt zur
cellsim-Linie 200–339) fixiert im Docstring von `xu_agreement_test.py`
VOR dem ersten vollständigen Lauf. Zwei Vor-Lauf-Korrekturen dort
dokumentiert (siehe CORREKTUR-LOG 1–2).

## Gates

- **G1 Determinismus: PASS** — Konfig (E1, alt, seed 1000) zweimal,
  Vorticity-Felder bit-identisch.
- **G2 (alle Messwerte ohne NaN): verletzt nach Buchstabe, offen
  gebucht** — alle Messwerte (ratios, flip rates, quant fractions) sind
  finit (exakt 0.0); die **Welch-p-Werte sind nan** (Null-Varianz BEIDER
  Stichproben — Floor-Effekt). G2 war im Code nicht implementiert (nur
  G1); die Kriterien-Verzweigung lief konservativ (nan → False → ABSENT).
  Kein Post-hoc-Kriteriumswechsel; keine Neu-Buchung.

## Verdicts (wie registriert, Lauf vollständig, 103.4 s, kein Abbruch)

- **H1 SPIRAL_EDGE_ABSENT** — 0/10 Seeds mit r ≥ 2.0, 0/10 mit r ≥ 1.3;
  alle 20 ratios (null UND alt) exakt 0.0 — kein Kern |Zeitmittel-vort|
  > 0.3 in Interface- UND Interior-Bändern in beiden Bedingungen; p = nan.
- **H2 RECONFIG_ABSENT** — flip ctrl = 0.0, alt = 0.0, delta_flip = 0.0,
  p = nan; Kernzahlen W_A [700,750): ctrl = alt = [0,0,0,0,0,0,1,0,0,0]
  (nur seed 2006 mit 1 Kern); persistence_alt = 0.0 (der eine Kern matcht
  nicht in W_B). W_B-Kernzahlen wurden nicht persistiert (Buchhaltungs-
  Lücke, dokumentiert; Verdict-inert, da 0 matches).
- **H3 CHARGE_DEGRADED** — pooled quant fraction 0.0. VAKUOS: 0 Kerne →
  0/0-Fall per Registrierung auf 0.0 kodiert; sagt nichts über die
  Ladungsquantisierung erhaltener Kerne.

## CORREKTUR-LOG

1. **Vor dem Lauf (1)**: erste Fassung kollabierte das E1-Zeitmittel-Fenster
   [1400,1500) mit W_B [1450,1500) (elif-Bug) → korrigiert auf drei
   getrennte Akkumulatoren (vort_e1, vort_a, vort_b). Vor erster Messung.
2. **Vor dem Lauf (2)**: Plaquette-Index-Algebra zweimal falsch geslicet
   (Broadcast-Fehler Form 1: (98,100) vs (99,99); Form 2: (98,99) vs
   (99,98) — beide Crashs am G1-Gate VOR jeglicher Messung). Korrekt
   (verifiziert): d_row (99,100), d_col (100,99);
   `d_row[:, :-1] + d_col[1:, :] - d_row[:, 1:] - d_col[:-1, :]` → (99,99)
   Plaquettes. Vor erster Messung; Kriteriumsfeld unverändert.
3. **Nach dem Lauf**: E2-Swap-Semantik — Code wechselt `delta_col` JEDEM
   Schritt ab t=750 (±δ0-Oszillation, Netto-Drive ≈ 0 in W_B), die
   Registrierung beschreibt EINEN sustained Vorzeichenwechsel. Verdict-
   inert: n_cores_wa ctrl == alt (identische Vorgeschichte bis t=750,
   deterministisch), 0 matches → flips 0 → ABSENT unter beiden Lesarten.
   Keine Neu-Buchung; Korrektur nur in einem ggf. v2.
4. **Nach dem Lauf**: G2 nicht implementiert (nur G1 im Code) — siehe
   Gates-Abschnitt, offen gebucht.

## Post-hoc-Diagnose (`probe_regime.py` — NICHT Teil der Registrierung, keine Verdict-Änderung)

- **Probe A (Regime, instantane Snapshots, seeds 1000–1002)**: vom
  Zufallsfeld (≈1900 Kerne ≈ 19 % der 9801 Plaquettes) annihilieren die
  Kerne binnen ~50–100 Schritte (uniform: 3/3 Seeds → 0). Mit persistentem
  counter-Drive überleben/fluktuieren Rest-Populationen in 2/3 Seeds
  (1001: 18→114 Kerne bei t=1499, max|vort| = **1.000 exakt** →
  unit-charge-Kerne; 1002: 74). **Interface-Dichte ≤ Interior-Dichte in
  allen Late-Time-counter-Snapshots** (I ≤ B, z. B. 1001 t=1499: I=0.006,
  B=0.031) — keine Interface-Anreicherung; die Kerne sind Rausch-Nukleation
  im Volumen, nicht Wand-organisiert. (Der einzige I>B-Fall ist ein
  uniform-Run — Fluktuation, kein Drive-Effekt.)
- **Probe B (Amplituden-Sweep, E1-Metrik VERBATIM, SWEEP_*-Labels, keine
  Promotion)**: δ0 ∈ {0.1, 0.2, 0.5} — alle 30 ratios_alt exakt 0.0 →
  SPIRAL_EDGE_ABSENT(sweep) bei allen Amplituden (10× über dem
  registrierten Wert hinaus). Null-Spotcheck δ0=0.5: max|vort_e1| ≈
  1.1–1.2e-17 (≈ Maschinen-Epsilon) — das Null-Feld ist exakt
  drift-invariant (uniformer Drive rotiert das Feld gemeinsam, Plaquette-
  Zirkulation unverändert) ✓.

## Interpretation (Abgeleitetes — klar getrennt von den Messungen)

1. **Der Agreement an der Messmathematik steht** (verifiziert, unabhängig
   von diesem Lauf): Xu et al. detektieren Spiralen als curl des
   (Hilbert-)Phasenfelds; TCI-125 als Plaquette-Zirkulation desselben
   Felds. Identische Operationalisierung von „Wirbel".
2. **Der Kandidat „persistenter Drive" genügt NICHT** (gemessen):
   Interface-Lokalisierung ABSENT bei allen Amplituden; Rekonfiguration
   ABSENT (keine Kerne in den Fenstern); gepinnte Ladungen ABSENT.
   Die Gegen-Trieb-Wand bleibt im Zeitmittel vortizitätsfrei; instantane
   Kerne (Probe A) sitzen NICHT an der Wand.
3. **Der fehlende Bit ist kein Toggle, sondern ein Regime**: die
   Korpus-Dynamik (0.9·Nachbar-circular-mean-Relaxation + σ=0.05-Rauschen)
   ist stark synchronisierend (tiefe Ordnungsphase, annihiliert
   KT-artig); Xu's propagierende Spiralen leben in einem
   excitablen/ausbreitungsfähigen Regime. Das ist eine
   dynamische-Regime-Lücke, nicht ein fehlender Parameter — explizit
   offene Frage, NICHT aus dieser einen Dynamik verallgemeinert.
4. **Was die TCI-Experimente dennoch an Vortex-Physik zeigen**: das
   Korpus-Feld kann Wirbel nukleieren und annihilieren (Probe A:
   mobile unit-charge-Kerne, Population fluktuiert 0–243); die
   Ladungsquantisierung der MESSUNG ist sauber (max|vort| = 1.000 exakt
   am Kern) — H3's DEGRADED ist die Vakuosität bei 0 Kernen, nicht ein
   Quantisierungs-Versagen der Formel.
5. **Der Korpus bleibt, was seine eigenen Logs sagen**: 122/124/125
   FALSIFIED (eigene Kriterien), 126/142 inkonsistent gebucht. Diese
   Buchung ändert daran nichts.
6. **Nicht getestet (offen)**: (a) excitables Korpus-Update (v2:
   korrigierter Single-Swap + Xu-Toolbox-Metriken count/duration/speed/
   radius/direction je Frame); (b) die Xu-Daten-Verankerung (Spiral-
   Dichte an Netzwerk-Grenzen in echten Kohorten) gegen eine
   TCI-ähnliche BC-Geometrie. Keine Vorabaussagen dazu.

## Dateien

- `xu_agreement_test.py` — pre-registrierter Test (Registrierung im
  Docstring inkl. Vor-Lauf-Korrekturen 1–2)
- `result.json`, `run_log.txt` — der registrierte Lauf (G1 PASS, vollständig)
- `probe_regime.py`, `probe_result.json`, `probe_log.txt` — Post-hoc-Diagnose
- gebucht in `scratch/notes/tci_vortex_assessment.md` (revidiert,
  Agreements-führend)

---

# Re-Analyse der publizierten Source Data (EXPLORATORY_REANALYSIS, tci_xu_data)

Datum: 2026-09-28. Anlass: Nutzersteuerung — die echten Messdaten der Studien
laden und die Verbindung Qualia ↔ Messdaten ↔ TCI-Theorie prüfen. Status wie
registriert: **EXPLORATORY_REANALYSIS** — Post-hoc-Re-Analyse der
publizierten Summary-Daten; KEINE Promotion zu TCI-Verdicts (das
pre-registrierte Verdict-Buch der Korpus-Linie bleibt unberührt).

## Daten

17 Source-Data-xlsx (MOESM9–25, Fig 2–8 + Extended Data 1–10), ~41 MB,
`data/` (NICHT committet — Drittanbieter-Daten; Download-URL-Pattern im
Docstring von `xu_data_analysis.py`):
`https://media.springernature.com/full/springer-static/esm/art%3A10.1038%2Fs41562-023-01626-5/MediaObjects/41562_2023_1626_MOESM{i}_ESM.xlsx`.
Paper-Volltext (Fig 5/6-Methoden-Chance-Level) gegen-gelesen via
`data/paper/NHB_wave_2023.pdf` (Warwick-Mirror, ebenfalls nicht committet).

## Registrierung + Korrektur-Log

Kriterien X1–X5 im Docstring von `xu_data_analysis.py` VOR dem ersten
Lauf fixiert; Labels X*_*. Korrektur-Log (Daten-Extraktion, nach dem
ersten Lauf, VOR Buchung — registrierte Kriterien unveraendert ausser B):

- **A(1) X2-Zeilen-Offset**: erster Lauf las Zeilen 3+ (Iterationen 2–100
  PLUS 'Iteration Mean'-Zeile PLUS 's.e.m.'-Zeile; Iteration 1 fehlte).
  Verifiziertes Layout: Zeilen 2–101 = Iterationen 1–100, Zeile 102 =
  'Iteration Mean', Zeile 103 = 's.e.m.'.
- **A(2) Label-Extraktion**: Header-Texte via Text-Grid (numerisches
  Array konvertiert Strings → NaN → leere Labels).
- **A(3) X3-n**: 100 Subject-Zeilen, 7 ohne Events (16/28/62/75/77/90/100),
  **93 mit allen 3 Spalten, Zeilensumme exakt 1.0000** — das
  Sheet-Label „(single-subject, n = 93)" ist korrekt; der erste Lauf
  (n=95) zählte 2 Nicht-Subject-Zeilen.
- **A(4) X5**: 5a/5c enthielten je 1 Summary-Zeile → Mittel kontaminiert;
  Subject-Filter (n=99/98 je Spalte).
- **B Code-vs-Registrierung**: Fig_6c-Chancen waren im CODE pro-Sheet
  (0.25 für alle 3 Spalten), die Registrierung sagt PER-SPALTE (4-Typen
  0.25, Load 0.5, Performance 0.5). Der erste Lauf testete
  Load/Performance gegen die falsche Chance; korrigiert auf die
  registrierten per-Spalte-Chancen. Registrierte Kriterien unveraendert.
- **C Nach Paper-Lektüre, VOR Buchung (Chance-Level)**: die registrierte
  Chance 0.5 für Fig_6b ging von einer 2-Klassen-Zielgröße (Story vs
  Math) aus. Paper (Volltext, Methods + Fig-6-Caption): die
  Language-Klassifikation ist **4-kanalig** (math listening/answering,
  story listening/answering), Chance **25%**. Der registrierte Test (vs
  0.5) bleibt wie registriert gebucht; die korrigierte Lesart (vs 0.25)
  war im zweiten Lauf bereits als POST-HOC-Zusatz (klar gelabelt,
  kein registriertes Kriterium) mitgelaufen und wird hier als
  paper-konforme Lesart dokumentiert — KEIN Post-hoc-Kriteriumswechsel
  des registrierten Labels.

## Resultate (zweiter Lauf, vollständig, 1.7 s, kein Abbruch; xu_data_result.json)

- **X1 X1_FLIP_WEAK** (registriert): flip = 3.047 rad (174.6°),
  R_listen = 0.34, R_answer = 0.16, zirkulaerer Permutationstest
  (10 000 Shuffles, seed 42) p = 0.0000 (0/10 000 ≥ obs). WEAK statt
  REALIZED, weil R_answer = 0.16 < 0.3 (registrierte Blockbedingung).
  Deskriptiv: step_props_pos listening 33.6→38.6 % vs answering
  54.1→57.2 %; Within-Trial-Konsistenz 0.754/0.730.
- **X2 Fig_6b Language, n=100 Iterationen** (Iteration-1-Wert 0.47917 ist
  korrekt als Iteration 1 gelesen, Mittel = gespeichertes
  'Iteration Mean' 0.4833333):
  - registriert (Chance 0.5): spiral original 0.4833 (p=1.6e-08)
    **X2_BELOW_CHANCE**; spiral additional 0.5035 (p=0.241)
    X2_AT_CHANCE; amplitude 0.3020 (p=6.0e-87) X2_BELOW_CHANCE.
  - **Paper-Chance 25% (4-Klassen, korrigierte Lesart)**: alle drei
    Spalten signifikant DARÜBER (t = 86.16 / 84.96 / 18.72,
    p = 6.4e-95 / 2.6e-94 / 2.7e-34) — Replikation der Paper-Zahlen
    48.33 ± 0.31 % / 50.35 ± 0.41 % / 30.2 ± 0.29 % auf das Digit.
    Paper-Nullmodell (randomisierte Phasen): 24.32 ± 0.24 %.
  - spiral-vs-amplitude (original): 0.4833 vs 0.3020, Welch p = 6.2e-109
    — Replikation der Paper-Claim „significantly lower … with brain
    spirals as information carriers".
  - Cross-Check SEM: berechnete SEM (0.0027/0.0030/0.0028) vs
    gespeicherte 's.e.m.'-Zeilen (0.0031/0.0041/0.0029) — Faktor
    0.74–1.35; Mittel matchen auf <1e-6. Die gespeicherten s.e.m.-Zeilen
    sind die Paper-eigenen Angaben (Memory Load: 0.0269 = die 2.69 %
    des Papers), nicht SD/√100 der 100 Iterationswerte — als
    Quellen-Discrepanz dokumentiert.
- **X2 Fig_6c WM (per-Spalte-Chancen wie registriert)**: 4 stimulus
  types 0.4373 vs 0.25 (p=8.5e-58) X2_ABOVE_CHANCE; Memory Load 0.6671
  vs 0.5 (p=1.9e-49) X2_ABOVE_CHANCE; Memory Performance 0.5896 vs 0.5
  (p=8.5e-30) X2_ABOVE_CHANCE — Replikation der Paper-Zahlen 43.72 ±
  0.54 % / 66.72 ± 2.69 % / 58.96 ± 0.61 %.
- **X3 Interaktions-Typen (n=93)**: Full Annihilation 0.5104, Partial
  Annihilation 0.4640, Repulsion 0.0255 — **Annihilation dominiert
  (~97.4 %)**, konsistent mit KT-artiger Wirbel-Physik und dem
  Korpus-Probe-A-Befund; Zeilensumme exakt 1.0000.
- **X4 EIGENE FORMEL AUF ECHTER PHASE** (die Kern-Replikation): exakt die
  registrierte plaquette_vorticity auf den drei publizierten
  Phasenfeldern (ED Fig 6c left/mid/right, 176×251 Flatmap, [−π,π],
  22712 gültige Plaquettes):
  - left: 50 Kerne (25 pos / 25 neg), quant_fraction **1.000**,
    max|v| = **1.000 exakt**, p99|v| = 0.000
  - mid: 1297 Kerne (650/647), quant **1.000**, max|v| = 1.000, p99 = 1.000
  - right: 2121 Kerne (1057/1064), quant **1.000**, max|v| = 1.000,
    p99 = 1.000
  - **Alle** detektierten Kerne liegen im H3-Quantiesierungs-Fenster
    [0.75, 1.25] — die Publikationsspitzen lesen sich mit unserer
    Formel als **unit-charge-Kerne**. Das ist direkt die Paper-Grundgröße:
    der Paper-Klassifikator dekodiert aus „instantaneous locations and
    **topological charges (1 or −1) of phase singularities**" (Methods:
    „−1 if the spiral is clockwise, and 1 if the spiral is anticlockwise").
- **X5 Richtungs-Proportionen (n=99/98 Subjects je Sheet)**:
  - Fig_5a_4th (Listen): Story Listen cw 0.0202 / acw 0.3266; Math Listen
    cw 0.184 / acw 0.0768 → Story-acw-dominant, Math-cw-dominant
  - Fig_5b_4th (Listen): Story cw 0.3265 / acw 0.034; Math cw 0.0456 /
    acw 0.1668 → **entgegengesetzt zu 5a**
  - Fig_5c_4th (Answer): Story cw 0.2298 / acw 0.0303; Math cw 0.0462 /
    acw 0.1727 → Story-cw-dominant
  - Fig_5d_4th (Answer): Story cw 0.0255 / acw 0.1811; Math cw 0.1811 /
    acw 0.1437 → **entgegengesetzt zu 5c**
  - Cross-Check 5a(col2) vs 5b(col1): n_common=99, nur 67/99 element-
    identisch (max |diff| 0.667) — nahe beieinander im Mittel
    (0.3266/0.3265), aber nicht Klon-Zeilen.
  - Paper-Zuordnung (Caption Fig 5): die Reversal ist **inter-
    hemisphärisch** — cw-Spiralcluster im IPC der linken Hemisphäre bei
    story answering, acw bei math answering (Fig 5c), dieselbe Reversal
    im rechten Kortex (Fig 5d); analog Listen (5a/5b).
- Vorbehalte X4 (offen dokumentiert): Flatmap ist 2D-Projektion (keine
  wahre kortikale Nachbarschaft — die Xu-Toolbox arbeitet selbst auf dem
  Flatgrid); die drei Frames unterscheiden sich drastisch in der
  Kernzahl (50 vs 1297 vs 2121) — Zeitpunkt/Filterung, nicht im
  Sheet dokumentiert; ~19 gleichzeitige Spiralen pro Zeitschritt (Paper,
  linker Kortex) vs bis zu 2121 detektierten Plaquette-Kernen je Karte
  im mid/right — unterschiedliche Granularität (Kern-Detektion über
  Schwelle vs Spiral-Objekte mit Boundary).

## Interpretation (Abgeleitetes — klar getrennt von den Messungen)

1. **Die Messmathematik liest auf echten Hirn-Daten quantisiert**: unsere
   Formel liest die publizierten Phasenfelder als unit-charge-Kerne
   (100 % im ±1-Fenster, max|v| exakt 1.000) — dieselbe Operationali-
   sierung, die das Paper als „topological charges (1 or −1)" benutzt.
   Das ist das stärkste neue Agreement-Datum der Linie: dieselbe Formel,
   dieselbe Quantiesierung, echte Messung.
2. **Richtungs-Rekonfiguration ist in den echten Daten PRESENT** (X1
   flip 174.6°, p < 1e-4; X5 Task-Epoch- und Hemisphären-Mirrors) — im
   Kontrast zum Korpus-Test (H2 RECONFIG_ABSENT). Die echten Daten HABEN
   die Rekonfiguration, die das minimale getriebene Korpus-Modell nicht
   erzeugt.
3. **Dekodier-Stärke**: spiral features dekodieren die 4 Language-
   Bedingungen (48.3 %) und die WM-Größen (43.7/66.7/59.0 %) signifikant
   über Chance UND über den amplitude-Baseline-Klassifikator (30.2 %) —
   die Paper-Claim „brain spirals as information carriers" repliziert
   exakt in den Source Data. Unter der FALSIFIZIERBAREN Messung:
   Phasen-Singularitäts-Geometrie (Ort + Ladung) trägt Task-Information
   über Amplitude-Höhen-Information hinaus.
4. **Interaktions-Statistik annihilation-dominiert (97.4 %)** — konsistent
   mit der Korpus-Probe-A-Physik (mobile Kerne annihilieren KT-artig).
5. **Was die Daten NICHT zeigen** (klar getrennt, siehe Notiz §7):
   Qualia-Identität (keine Phänomenologie-Kanal), Ladungserhaltung/
   -Schutz (Richtungen kippen mit Task — gerade NICHT geschützt im
   topologischen Sinne), Ego als EINZEL-Wirbel (~19 gleichzeitige
   Spiralen; Korpus-125 FALSIFIED bleibt stehen).

## Nachtrag 2026-10-05 — Daten-Provenienz + Quellen

- `data/` (17 Source-Data-xlsx, ~58 MB) bleibt **lokal und un-committet**
  — Drittanbieter-Supplement zu Xu et al. 2023; Lizenzprüfung für
  öffentliches Hosting offen. Reproduktion über das URL-Pattern im
  Docstring von `xu_data_analysis.py` (MOESM9–25). Der Paper-Volltext
  (`data/paper/NHB_wave_2023.pdf`, Warwick-Mirror) bleibt ebenso lokal.
- Vollzitat (wie gewünscht mit DOI): **Xu, Y., Long, X., Feng, J. &
  Gong, P.** — „Interacting spiral wave patterns underlie complex brain
  dynamics and are related to cognitive processing", Nature Human
  Behaviour 7, 1196–1215 (2023), DOI 10.1038/s41562-023-01626-5, PMID
  37322235; Research Briefing: DOI 10.1038/s41562-023-01628-3.
- Die Rohdaten der EIGENEN Analoga-Linie (tci_v2/v3/v4, `per_seed/`) sind
  seit 2026-10-05 als Git LFS committet (Roh-Commit `11949ec`,
  SHA-256-Manifeste) — Quellen-Anker für die ganze Wirbel-Linie:
  `../../notes/tci_vortex_assessment.md` §10 (Video-Papers Verzhbinsky
  2026, Muller 2026, Anastassiou 2010, Pinotsis & Miller 2023, Naqvi
  2007, jeweils mit DOI).