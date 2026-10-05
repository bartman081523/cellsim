# Vollständiges Experimentier-Protokoll — Rekonstruktion

**Stand:** 2026-10-05 · **Umfang:** 36 Experiment-Vektoren (iter-1…iter-31 mit Lücken, tci_xu/v2/v3/v4) + Produktions-/Doku-Vektoren · **Commits:** 41 (d73c4ca 2026-08-21 → 44fba75 2026-10-05) · **Tests:** 249 · **Rohdaten-LFS:** 450 Dateien

**Art dieser Datei:** REKONSTRUKTION aus den existierenden Artefakten — kein neuer Lauf. Sie ist ein **Index zweiter Ordnung** (P5 des Ledger-Minds): jedes Verdict hier trägt einen Verbatim-Label-Anker auf sein Original-Protokoll. Korrekturen zu dieser Datei werden append-only nachgetragen (style a/b des Ledger-Minds).

## 0. Basis und Methode der Rekonstruktion

- **Dateien:** alle `scratch/experiments/*/` (experiment.md, result.json, Lauf-Skripte, run_logs, korrektur_logs), `scratch/strategic_vectors/iter-1…31.md`, `scratch/notes/*` (4), `scratch/theory/*` (2), `scratch/presentation/`.
- **Commits:** vollständige `git log`-Historie (41 Commits); iter-13 hat KEIN scratch-Verzeichnis und wurde aus `git show --stat 18afed1` rekonstruiert. iter-32/33/34 = die tci_v2/v3/v4-Verzeichnisse (Commit-Namen tragen die iter-Nummern).
- **Ergebnisse:** Verdict-Labels und Grade werden VERBATIM aus den Protokollen übernommen; keine Neubewertung (Ledger P4: Einstufung statt Re-Decide).
- **Integrität:** die 450 LFS-per_seed-Dateien der tci-Linie wurden am 2026-10-05 gegen die drei `per_seed_manifest.json` SHA-256-neu verifiziert (450/450 OK, alle drei Manifest-Hashes matchen).
- **Ehrliche Grenzen:** vor iter-19 stehen in keinem Protokoll Walltimes; SHA-256-Freezes mit `per_seed_manifest.json` existieren erst in den tci-Vektoren — die frühere Regi-Form war „VORAB-REGISTRIERUNG im Docstring/Protokoll + Gates", nicht Hash-Freeze. Kein `REGISTERED_NOT_MEASURED`-Marker existiert im Repo (Grep = 0 Hits). iter-3 und iter-9 haben kein experiment.md (Hypothese im Docstring).

## 1. System-Rahmen

**Workflow** (scratch/README.md): Hypothese in `scratch/experiments/iter-N/experiment.md` → Code → result.json (Signal) → strategischer Vektor → Production-Update oder Pivot. **Seed-Konvention:** disjunkte Blöcke je Iterationsfamilie: Seed 42 (Frühphase), {100,101,102} (iter-14), {300,301,302} (iter-17), base 400 (iter-18), base 300 (iter-19), {200,201,202} (iter-24–26), 200–209 (iter-27/28), 300–309 (iter-29), 310–319 (iter-30), 320–329 + 330–339 (iter-31), 1600–1609 (tci_v4). **Regi-Evolution:** iter-1…12 Prosa-Kriterien; iter-14 ab „VORAB-REGISTRIERUNG vor dem Lauf fixiert" im Code-Header; iter-21 ff. zusätzlich `"registration"`-Gate-Blöcke in result.json und K-Gates (bit-identische Recompute-Anker gegen Vorgänger); tci-Zeile zusätzlich Roh-Commit-Buchung + SHA-256-Manifeste. **K-Evolution:** K1 = GPU-Operator-Kalibrierung (iter-24)/Artefakt-Konsistenz (später), K2 Determinismus, K4/K4a Reparametrisierungs-Freeze, K5/K5'/K5'' Bit-Identitäts-Gates (Registrierungs-Verletzung ⇒ REGISTRATION_ERROR; keinem echten Lauf ausgelöst außer tci_v3/v4-R1-ähnlichen Vorstufen, dokumentiert bei iter-23).

## 2. Master-Tabelle (alle Vektoren)

| Vektor | Linie | Commit | Verdict (VERBATIM) | Konsequenz |
|---|---|---|---|---|
| iter-1 | EM | bbd7759 | STRONG | `modules/em.py` |
| iter-2 | UV-Sync | bbd7759 | STRONG (verdächtig, r≈1.0) | iter-2-retry |
| iter-2-retry | UV-Sync | 6509396 | CONTRADICTION | Modell-Artefakt; iter-3 |
| iter-3 | Cryptochrom | 6509396 | STRONG (mit Korrektur) | `modules/cryptochrome.py` |
| iter-4 | N-Zellen-UV | ebfc467 | CONTRADICTION | Phase B aktiviert |
| iter-5 | QuQuint-VQE | ebfc467 | STRONG | `quantum/ququint.py` |
| iter-6 | Proton-Tunneling | aa913a3 | STRONG (selektiv; Bug korrigiert) | `quantum/tunneling.py` |
| iter-7 | Orch-OR | a113396 | CONTRADICTION — **später RETRAKTIERT (iter-16, Formel-Artefakt)** | Status F→C (OPEN) |
| iter-8 | UV-Sync-ATP-ODE | 0dcb49f | CONTRADICTION | UV-Sync archiviert (nicht falsifiziert) |
| iter-9 | Integration | 1573cb9 | STRONG (heuristisch) | `driver/integration.py` |
| iter-10 | Ruliad-Metriken | d0e1665 | CONTRADICTION | iter-10-retry |
| iter-10-retry | Ruliad vektorisiert | d0e1665 | CONTRADICTION (mit Substanz) | `modules/emergence.py` |
| iter-11 | Damköhler-Sweep | 04ea439 | EMERGENT (9/12 DISTINCT) | Tau-Leap-Produktion |
| iter-12 | Genesis-UVC-Brücke | 04ea439 | BRIDGE_VISIBLE (p<0.0005) | Sprung-Diffusion + Sparse-Metrics |
| iter-13 | Produktion (kein Scratch-Dir) | 18afed1 | 184 Tests grün | rdme tau-leap + emergence |
| iter-14 | Fenster-Replikation | 3fa5753 | REPLICATED_STRONG (7/9) | korrigiert iter-11 (Operator-Artefakt) |
| iter-15 | Trp-Superradianz N* | dc014ce | BRIDGE_OPEN | `modules/superradiance.py` |
| iter-16 | Orch-OR korrigiert (Hagan) | dc014ce | OPEN_SUBSTRATE | `modules/orch_or.py`; Retraktion iter-7 |
| iter-17 | Turing-RDME | aa80461 | FALSIFIZIERT (registrierte Bande) | Einheiten-Bug isoliert; `radial_power_spectrum` |
| iter-18 | OR-Kern-Diskrimination | aa80461 | SIGNATURE_ROBUST | `orch_or.py` Produktion (14 Tests) |
| iter-19 | Turing prospektiv L=48 | a685b74 | BAND_SHIFTED_CONTINUOUS — **Diskrimination VOID** (Stencil-Fehler) | iter-19b reserviert (nie gelaufen) |
| iter-20 | Registry-Turing | 29d8735 | FALSIFIED_REGISTRY_TURING_INCOMPETENT | iter-17/19-Anomalie entwertet; Selbst-Audit-Korrektur |
| iter-21 | Schild-Feld | 8fd6260 | SHIELD_UNDERIVABLE_CONFLUENCE_ONLY | `modules/shielding.py` |
| iter-22 | Kick-Kopplung | a39d63c | KICK_INERT_BOX_WIDE | `modules/kick_coupling.py` |
| iter-23 | Photonische Kopplung | 22322ff | PHOTONIC_CHANNEL_INERT_FOR_SYN3A (R1=REGISTRATION_ERROR vorab dokumentiert) | `modules/photonic_coupling.py` + Driver-Flag |
| iter-24 | Fenster-Replikation V2 | d18edfa | REPLICATED_STRONG_V2 (8/9) | GPU-Operator-Port (33–34×) |
| iter-25 | Sättigungs-Marge | 18d5f41 | SATURATION_MARGIN_MODERATE (Kante 10×) | iter-26-Korrektur der D=0.15-Kante |
| iter-26 | Feingitter-Kante | f944e75 | EDGE_UPPER_CONFIRMED\|EDGE_NOT_LOCALIZED\|EDGE_D_NONMONOTONE | motiviert iter-27 |
| iter-27 | Seed-Budget n=10 | 166d1a9 | EDGE_STATUS_CHANGED_N10\|H0_DOMINANT\|SPREAD_SYMMETRIC | 7/22 Labels kippen; Smoke-Gate etabliert |
| iter-28 | Reclass + Deep-Replikation | 96600c6 | RECLASS_SEVERE\|SE_H0_MARGINAL\|SE_RECOVERS_NONE\|SE_RULES_DIVERGE\|DEEP_REPLICATED | 17/22 Flips; 3/3 Deep repliziert |
| iter-29 | Welch-t-Kalibrierung | 6f6028d | T_H0_CALIBRATED\|CAND_REPLICATED_ALL\|CAND_ABS_ALL\|EXPL_NOT_REPLICATED | 3/3 Kandidaten promoted |
| iter-30 | Survivor-Zensus | 08a8645 | SURV_ALL\|DEEP3_FRESH_REPLICATED\|EDGE_SIGNALS | 4/4 Überlebende positiv |
| iter-31 | Block-Stabilität | c1aaa86 | SAMPLING_DOMINANT\|DEPTHS_STABLE_MAJORITY\|9/9 VORZEICHEN_STABIL | REVIDIERT iter-30-Hypothese 3 |
| tci_xu | Bewusstsein-TCI | a6e3ee7, 06bc9ef | SPIRAL_EDGE_ABSENT\|X*_REPLICATED | Xu-Formel trägt am Original; Drive allein nicht |
| tci_v2 (=iter-32) | Bewusstsein-TCI | 00e2bb2 | KETTE_VOR_DER_ERSTEN_STUFE_FALSIFIZIERT | FHN: keine Phase |
| tci_v3 (=iter-33) | Bewusstsein-TCI | f05fb2b | GRENZZYKLUS_NOTWENDIG_NICHT_HINREICHEND\|R1 SHIFTED | Brusselator: Rausch-Turbulenz-Gas |
| tci_v4 (=iter-34) | Bewusstsein-TCI | db57dee | R2_NULL — GLIED_iii_FALSIFIZIERT_IN_INSTANZ | Hylothese-Kette F1–F6; tci_v5-Hebel |
| Präsentation | SciCom | f7c579e | — | 12-Slide-Deck + 3 Manim-Videos |
| Studien-Notiz | Quellen | 2ba7908 | — | Video-Studien mit DOIs verifiziert |
| Rohdaten-LFS | Buchhaltung | 11949ec | P3-Ketten-Bruch gebooked | 450 Dateien, 797 MB |
| Doku-Runde | Buchhaltung | 44fba75 | — | Zitate/Anker/Ledger |

Signal-Ökologie über die 32 Experiment-Vektoren (30 iter-Nummern; iter-13 ohne Scratch-Dir, dafür iter-2-retry und iter-10-retry als eigene Dirs): **stützend/produktiv ×14** (iter-1, 3, 5, 6, 9, 11, 12, 14, 15, 16, 18, 24, 29, 30), **widersprechend/falsifizierend ×12** (iter-2-retry, 4, 7*, 8, 10, 10-retry, 17, 19, 20, 21, 22, 23; *iter-7 später retraktiert), **methodisch/selbstkorrigierend ×6** (iter-13, 25, 26, 27, 28, 31) — plus 4 TCI-Vektoren, sämtlich negativ/absent (xu SPIRAL_EDGE_ABSENT, v2 FALSIFIZIERT, v3 NOTWENDIG_NICHT_HINREICHEND, v4 NULL).

## 3. Phase A/B/D — Frühl-Linie (iter-1…9, 2026-08-21…27)

### iter-1 — EM-Schicht für Biophotonen
Zelle emittiert UV (200–400 nm); 1D-Maxwell-Layer + Dipolquelle aus ATP-Hydrolyse; Emission = Schwarzkörper 310 K × Extinktion + Popp-Faktor. **STRONG**: 10 Photonen/s/Zelle, Fluss @1 µm 8.0e7/cm²/s; Schwarzkörper @250 nm ≈ 2.9e-73 W/m²/nm (SB-Hypothese damit tot). Artefakte: experiment.md, result.json, em_layer.py. → `modules/em.py`. (experiment.md:3-11)

### iter-2 — UV-Phasen-Synchronisation (2 Zellen)
Zwei Zellen <10 µm synchronisieren ATP-Oszillationen über UV (Cifra/Popp); Vorhersage r>0.5. ODE mit UV-Feedback, 100 s. **STRONG (verdächtig)**: r = 0.99999 über ALLE Distanzen bis 50 µm → Artefakt-Verdacht. → iter-2-retry.

### iter-2-retry — Kopplungs-Sweep
6 Kopplungen (1e-6…1e4) × 3 Distanzen, 5 %-Rauschen, Seed 42. **CONTRADICTION**: r=0.99999 selbst bei Kopplung 1e-6/5000 nm → Eigenschaft des geteilten ODE-Gleichgewichts, keine Widerlegung der UV-Sync-Hypothese selbst. Phase A pausiert.

### iter-3 — Radikal-Paar-Cryptochrom
(kein experiment.md — Docstring) FAD + 3 Trp Radikal-Paar, Singulett↔Triplett-Mastergleichung + Hyperfein, B-Sweep 0…1 mT. **STRONG (mit Korrektur)**: yield-Spread 0.4985 (max 1.0 bei B=0, min 0.5015 bei 1 mT) — 1–5 %-Effekt konsistent mit Ritz/Wiltschko; Resonanz-Verhalten bei hohem B konservativ behandelt. → `modules/cryptochrome.py`.

### iter-4 — N=10 Zellen-Population + UV
Populations-Sync r_global>0.5 gekoppelt vs. isoliert; Seed 42. **CONTRADICTION**: isolated r=0.9999961 (trivial), uv = crypto = 0.26708 (bitidentisch — Module unterscheiden hier nichts); ATP divergiert (19.4 mM statt 2–5). Via-Negativa: 3 Iters an derselben ODE-Hürde → Phase B.

### iter-5 — QuQuint-VQE
QuQuint d=5-Qudit-VQE (GF(5)) vs. konventionelle 4×4-Bild, 5 γ-Kopplungen. **STRONG**: threshold_factor **36.3** (Distillation 36.3 % vs ~1 %); Grundzustand 0.9999→0.7746 (γ 0.01→0.5). Korrektur-Begrenzung: keine „1000×"-Vermutung; diskrepante CCZ-Ratio (1.75× in md vs 1 in result.json) als Buchungslücke vermerkt. → `quantum/ququint.py` (Benchmark L4 repliziert 1.1×–1.3×).

### iter-6 — Proton-Tunneling MCF/AARS
Wigner + Bell-Korrektur; Sweeps T 77–400 K, Breite 0.3–2.0 Å. **STRONG (selektiv)**: Enhancement @310 K 2.046 bei d=0.3 Å; ~1 bei d≥0.5 Å. **KORREKTUR im Protokoll**: ein 4.18e9×-Wert bei 77 K war ein Berechnungsfehler (klassisches Verhältnis statt Enhancement); korrekt ≈1. Zahlen-Spalt md (1.0000902) vs result.json (2.0457) @0.3 Å offen vermerkt. → `quantum/tunneling.py` (Gate d ≤ 0.3 Å).

### iter-7 — Penrose-Hameroff Orch-OR (ERSTFASSUNG)
E_G = ħ²/(G·m²·τ), Tegmark-Dekohärenz; Tubulin-Dimer, 310 K. **CONTRADICTION**: τ_collapse 5.656e-37 s vs τ_dec 2.464e-10 s (Ratio 2.3e-27) — „Orch-OR numerisch falsifiziert", Phase C reduziert. **RETRACTION (iter-16, 2026-09-02)**: E_G-Formel dimensional invalid UND Kriterium invertiert — die 27-Dekaden-CONTRADICTION ist ein Formel-Artefakt; LIMITATIONS-Status F→C (OPEN). Die Retraktion steht als Nachtrag im iter-7-Protokoll (historische Zeilen bleiben).

### iter-8 — UV-Sync final (realistische ATP-ODE)
5 Kopplungen × 4 Distanzen = 20 Läufe, Michaelis-Menten mit 3 Verbrauchern, Seed 42. **CONTRADICTION**: r_steady 0.99987–0.99999 in ALLEN 20 Läufen — „kein ODE-Artefakt mehr, Eigenschaft des 2-Zellen-Gleichgewichts". **VECTOR_UV_SYNC_RETIRE_FINAL**: Hypothese archiviert (nicht falsifiziert), aus Scope entfernt.

### iter-9 — Integration
(kein experiment.md — Docstring) Alle 5 Production-Module in EINER Zelle (`driver/integration.py`), 5 s, 5000 Steps, Seed 42. **STRONG (heuristisch — Kriterium 0.01<ATP<100 ohne Test)**: ATP 2.95 mM, 5 Module aktiv, rdme_final 83200 Partikel. → Standard-Schnittstelle; Phase D abgeschlossen.

## 4. Ruliad- und Damköhler-Genesis (iter-10…16, 2026-08-28…09-02)

### iter-10 — Ruliad-Emergenz-Metriken
Origin_Ruliad-Metriken (MI, LZ) auf RDME-Voxelfeldern; reaktiv vs k=0, 6³, 3000 Schritte, Seed 42. **CONTRADICTION**: ΔMI = 0.0 — 1 Gillespie-Event/Schritt lässt das Feld statisch. Kein Produktionsertrag.

### iter-10-retry — vectorisierte Diffusion
Hybrid: vektorisierter 3D-Laplace + 1 Gillespie-Event, 16³, 2000 Schritte. **CONTRADICTION (mit Substanz)**: LZ-Growth −0.0029 (reaktiv) vs +0.0674 (diffusiv) — Diffusion erzeugt mehr Komplexität als Chemie; als Rate-Problem gerahmt, nicht Framework-Widerlegung. → `modules/emergence.py` (8 Tests).

### iter-11 — Damköhler-Regime-Sweep
Lokales Tau-Leaping (λ=k·dt·n) × Laplace, Sweep dt_react {0,1e-6,1e-5,1e-4,1e-3} × D {0.05,0.15,0.45}, Seeds 42/43/44, Mehrheitsentscheid. **EMERGENT**: 9/12 DISTINCT, 0 Runaway; Fenster Turnover ~1e-4…0.1/Molekül/Schritt; zwei LZ-Fenster (D=0.45/dt=1e-5: +0.457 mit corr(Glc,ATP) −0.249; D=0.05/dt=1e-4: +0.245, corr 0.567). KORREKTUREN im Protokoll: INT64-Overflow bei D=0.45 (Guard fixiert), Stabilitätsgrenze d ≤ 1/6 (nicht 1/3), Massendrift ~2 %. → Empfehlung Tau-Leap im Produktionssolver.

### iter-12 — Genesis-UVC-Brücke
232-nm-UVC-Fluss → Iter-11-Fenster → Photoreaktion. Vor-Simulations-Vorhersagetabelle registriert: endogener Popp-Fluss 5 Dekaden unterm Fenster. Seeds (42,43)/Arm, Permutationstest Seed 7. **BRIDGE_VISIBLE**: Licht-Kontrast +0.29 vs **0.00** thermo (gleiches Event-Budget 588/596), p<0.0005 (0/2000); endogen 0 Events (Turnover 4.83e-9). Methoden-Befund: rint-Diffusion hat Diskretheits-Boden (Fix → iter-13); MI/LZ-Schwellwerte dichte-abhängig → Permutationstest als Anti-Texas-Sharpshooter.

### iter-13 — Produktions-Sprint (KEIN Scratch-Dir, rekonstruiert aus Commit 18afed1)
Drei Pakete: (1) `RDMEAdapter(use_tau_leap=True)` — per-Voxel-Propensität, Poisson-Firings, Feasibility-Cap, `state.tau_leap_events`; (2) `stochastic_jump_diffusion()` — Binomial-Sprünge pro Richtung, massenerhaltend, O(1)-Counts überleben; (3) `permutation_contrast_test()` — pure-index H0-Statistik. +220 Zeilen Produktion, +233 Tests-Zeilen; **184 Tests grün**, ruff clean; iter-11/12 CANDIDATE→CANDIDATE+.

### iter-14 — Fenster-Replikation auf Produktionstack (Falsifikator)
„VORAB-REGISTRIERUNG vor dem Lauf fixiert" im Code-Header: REPLICATED_STRONG = ≥6/9 DISTINCT + Sättigungs-Rückkehr + Fenster-Ordnung; Seeds {100,101,102} (disjunkt), 24³. **REPLICATED_STRONG**: 7/9 DISTINCT, Sättigung ✓, Ordnung 3/3, U-Form überall. **Gewichtige KORREKTUR**: iter-11s Kontrolle corr≡1.000 war ein Determinismus-Artefakt des geteilten rint-Operators — ~90 % des iter-11-Drops war Operator, nicht Chemie; Magnituden operator-kalibriert. Plus Kalibrierungs-Fix: p_dir = 𝒟 statt 𝒟/6. → VECTOR_STOCH_CONTROL_METRIC offen.

### iter-15 — Trp-Superradianz, N*-Gesetz
Kriterien vorab im Code-Header (BRIDGE_OPEN / FALSIFIED_BRIDGE / CONTRADICTION_ITER12); MC 200k Bursts, Seed 42. **BRIDGE_OPEN**: Φ* = 2.07e8…2.07e11 Photonen/s (r=100 nm, dt=1 ms); 9 Konfigs im Fenster, **syn3A in keiner**, neuronale Skala in 5; Fenster-Eintritt N·f ≳ 2e8/s; MC rel. Fehler 0.0097; dynamischer Check p<0.0005. → `modules/superradiance.py` (9 Tests), Fenster-Konstanten eingebettet.

### iter-16 — Orch-OR unter Hagan-Parametrisierung (korrigierte Nachrechnung)
Vorab-Kriterien (OPEN_SUBSTRATE: τ_OR ∈ [1e-5,1e-1] s in HYPOTHESE-Grenzen f≤5e-2, a≤8nm, N≤1e11, S≤1e6); 288 Konfigs deterministisch. **OPEN_SUBSTRATE**: iter-7-Artefakt E_G=186.58 J (invalid) korrekt → Dimer: τ_OR = 3.77e11 s (~12000 Jahre, kein Kollaps); Hagan f=1 % → ~1.2e-3 s (Ballpark ✓); **7 viable Konfigs** — alle in der Ecke (f=5e-2, a=8 nm, N=1e9, korreliert, S=1e6); **0 viable ohne Shielding**. **Retraktion iter-7** (Formel-Artefakt). → `modules/orch_or.py`; Tegmark-Dekohärenz bleibt für Bulk-Wasser (S=1) gültig.

## 5. Turing- und QM-Grenze (iter-17…20, 2026-09-21)

### iter-17 — Turing-Muster im RDME (registrierte Falsifikation)
Schnakenberg-Kern; vorab registrierte diskrete Banden (durch D_k korrigiert); 24³, dt=0.05, Seeds {300,301,302}; Nulls (matched/diffusion-only/mean-field). **Registrierte Banden-Vorhersage FALSIFIZIERT**: D_v=3.0 FALSIFIED_NO_PATTERN (peak_excess 23349, k_peak 0.262 = Box-Grundmode, band_ratio 0.010), D_v=10.0 ebenso (769365, 0.178); D_v=0.25/1.0 STABLE_AS_PREDICTED; Matched-Null selbst peak_excess 5.64 → ARTIFACT_PATTERN (Metrik defekt). **Einheiten-Bug isoliert**: D als Rate pro Zeiteinheit registriert, Operator liefert pro Schritt — Bande ~4.5× zu hoch; korrigierte Dispersion als post-hoc-Konsistenz NICHT als Bestätigung gebucht. Entdeckung (außerhalb Regi): genuine Rausch-strukturierte kohärente Box-Skalen-Ordnung λ≈24. → `radial_power_spectrum` (+5 Tests).

### iter-18 — OR-Kern-Diskrimination
Vorab registriert (DISTINGUISHED_q / SIGNATURE_ROBUST / INDISTINGUISHABLE; C2-Claim-Deckel); 3 Seeds base 400 × 3 Arme (or_kernel/classical/shuffled); Permutationen 2000/200. **SIGNATURE_ROBUST**: S1 Fano 5.31–5.46 gegen Theorie 5.40 (±2 %), S2 korrekt untrennbar (0.88–1.01), S3 corr 1.00/0.49/0.10 (z 506/250/48–53); q=0.1: nur S3 trägt. KORREKTUR (vorab dokumentiert, nicht stillschweigend): S2/S3-Formeln in der Registrierung fehlerhaft (1−h bzw. h statt 1−p) — Messung traf die korrigierte Formel exakt. → `orch_or.py` Produktion (14 Tests, 213 Suite).

### iter-19 — Turing prospektiv L=48 (VOID)
7 Konfigs, Diskrimination registrierter diskreter gegen kontinuierliche Linearisierung; ~2.3 h, exit 0. **BAND_SHIFTED_CONTINUOUS** mechanisch — **Interpretation VOID**: zentraler Stencil-Fehler in `eig_max_step` (Radialwellenzahl im Diagonalmodus-Multiplikator); Integritätsnachweis reproduziert alle 5 registrierten Zahlen exakt mit der fehlerhaften Formel; Schale 0.131 bleibt die eine saubere Diskrepanz. Vektor VECTOR_SHELL1_CASCADE reserviert, NIE registriert/gelaufen.

### iter-20 — Registry-Turing (Falsifikator)
Deterministisch; vorab registrierte Erwartung IST die Falsifikation. **FALSIFIED_REGISTRY_TURING_INCOMPETENT**: 0/20 Autokatalyse-Zyklen in Nettoform; 48 Konversions-Zyklen ohne Verstärkung; 26×26-Jacobian zeigt Diffusions-Signatur −(d/DT)·D_min statt Instabilität; Attraktor = Totzustand ATP=0. Konsequenz: Turing-Muster in der Zellsim nur auf künstlichem Kern; iter-17/19-Signal ist nicht Registry-abhängig. CORREKTUREN: Docstring-Zählung 21→20; CLAUDE.md + Selbst-Audit-Claim korrigiert (26 Spezies/20 Reaktionen), Selbst-Audit neu: 12 Claims, 4×A, 8×C.

## 6. QM-Kanäle-Umschließung (iter-21…23, 2026-09-23)

Drei Vektoren schließen die Orch-OR-Ecke in syn3A dreifach ein (Schild → Kick → Photonen); alle mit `"registration"`-Gate-Block in result.json und K1–K5, alle C-Grade:

### iter-21 — Schild-Feld
S_max(Box) = 9.90e3 vs S_need = 6.128e5 → **62× zu kurz**; S=1e6 ⟺ φ≈1e-6 (100× unterm Floor); Corner stirbt in beiden Regimen (bound-water allein 4.1e7 s⁻¹ ≫ 6.6e3 s⁻¹); Überleben nur in Konfluenz (Δm/m ≲ 1.3e-3 UND ε_res ≲ 1e-6). MC-Abgleich rel 1.9e-5. **SHIELD_UNDERIVABLE_CONFLUENCE_ONLY**. → `modules/shielding.py` (10 Tests). Ketten-Gegenstück: der Weg ε_res=1e-6 frei zu bekommen ist Fröhlich-Kohärenz = REFUTED_BY_REIMERS_2010.

### iter-22 — Kick-Kopplung
N* = 1.744e11 bei τ_relax=1 ms (**1.74× über Hameroff-Decke 1e11**); Box braucht τ_relax* = 9.25e-3 s; pro Event 1.63e-10 k_B·T (Ecke) — 10 Größenordnungen unterm thermischen Quantum; Gate-Map: ohne Schild N 7.83e11 außerhalb Box, mit ableitbarem Schild 7.87e9. **KICK_INERT_BOX_WIDE** — der OR-Kernel ist in der Box ein reiner Muster-Generator. → `modules/kick_coupling.py` (11 Tests).

### iter-23 — Photonische Kopplung
Φ_cap = P_ATP/E_photon = 1.17e5 Photonen/s (kollektiv-unabhängiges Pump-Cap); Turnover am Cap bei r=100 nm 5.65e-5/s = **1.77e3× unter** der Fenster-Unterkante 0.1/s; Burst-Argument strukturell tot (N kürzt sich: f = Φ_cap/N). **PHOTONIC_CHANNEL_INERT_FOR_SYN3A** — R1 war korrekt **REGISTRATION_ERROR** (registriertes N-Gitter enthielt 1e9 außerhalb der Lemma-Domäne; K3v2 vor R2 fixiert, R1 dokumentiert, nie als Bestätigung gelesen). → `modules/photonic_coupling.py` + Driver-Wiring (`--superradiance`, run.csv +4 Spalten), 249 Tests grün.

## 7. Damköhler-Robustheits-Batterie (iter-24…31, 2026-09-23…28, GPU seit iter-24)

### iter-24 — Fenster-Replikation V2 + GPU-Operator
Operator-Archäologie gegen git 3fa5753 → der alte Operator war einseitig drift-behaftet (3𝒟+Drift), der beidseitige driftfreie Operator wird jetzt geprüft; Protokoll VERBATIM wie iter-14, Seeds {200,201,202}, ~1 h 45 min CPU. **REPLICATED_STRONG_V2**: K1 (unabhängige Operator-Kalibrierung: Symmetrie/Drift/Varianz/alter Operator 20×–180× fail) PASS, DISTINCT **8/9**, Sättigungs-Rückkehr ✓, Ordnung 3/3, 0 Runaway. Strukturell: corr-Kriterium feuert NIE — Fenster ist **LZ-Einheiten-getrieben**. GPU-Port (Nacharbeit, nicht Teil der Regi): 7.8–8.0 ms/Schritt vs CPU 263.9 ms → **33–34×** (G1–G5). → Replikationskette auf 3 Operator-Substraten.

### iter-25 — Sättigungs-Marge
k_f-Sweep {1…10000} × D-Anker {0.05,0.15,0.45}, GPU, 27 Zellen + 9 Kontrollen; K4 = exakte Reparametrisierung vorab registriert. **SATURATION_MARGIN_MODERATE**: globale Kante **10×** (exakt an der NARROW-Grenze); Substrat-Sperre 2.5–3 Dekaden über der Metrik-Kante (Events-Plateau k-invariant); Kontroll-LZ dreht negativ bei D=0.45; K5 2/3 (GPU/CPU-Flip D=0.45 an exakt der 0.05-Schwelle). CORREKTUREN: Oberenden-Regel fehlte im Code (Verdict-unabhängig), Kontroll-Persistenz via deterministischem Recovery, extern gestoppter Lauf #1 nicht gebucht. iter-11-Hypothese nur schwach getragen (1–2 Dekaden Reserve).

### iter-26 — Feingitter-Kante + D-Abhängigkeit
43 Zellen GPU, Oberenden-Regel ab Lauf im Code (Lektion iter-25); K5 = 9 Überschneidungszellen BIT-IDENTISCH zu iter-25. **EDGE_UPPER_CONFIRMED | EDGE_NOT_LOCALIZED | EDGE_D_NONMONOTONE**: D=0.05-Kante 10 exakt (Band nicht zusammenhängend — NULLs bei k=3/5/7); D=0.15 nicht lokalisiert (≥200, Gitterspitze) — iter-25s Kante 100 war Auflösungs-Artefakt; neue Anker D=0.10→3, D=0.25→30, D=0.30→1000 (nicht lokalisiert); Kantenfolge nicht monoton (4/5 Paare verletzen Intervall-Konsistenz); LZgrw straddelt ±0.05; `mean_vs_perseed`: 22/43 Labels widersprechen der Mittel-Ebene ⇒ dreifache Motivation VECTOR_STOCH_CONTROL_METRIC.

### iter-27 — Seed-Budget n=10 + Kontroll-Rausch-Floor
355 Läufe GPU (~62 min), Seeds 200–209; n=3-Regel VERBATIM parallel; K5' (Submittel bit-identisch) + K5'' je 30/30. **EDGE_STATUS_CHANGED_N10 | H0_DOMINANT | SPREAD_SYMMETRIC**: False-DISTINCT unter Kontroll-Rauschen 24.8/26.2/26.6/18.3 % (nur D=0.25: 0 %) — 0.05-Schwelle liegt 2–3× unterm Paar-Diff-Rauschen; Seed-Paarung + Vote = **Ausreißer-VERSTÄRKER**; 7/22 DISTINCT-Labels kippen (≈ H0-Prädiktion ~5.5); Insel-Struktur D=0.05 löst sich auf; robust: Kante k=10, D=0.30 k=30, D=0.15 k=5. Erste VOLL-Persistierung per-seed (Zellen UND Kontrollen). Smoke-Gate-Methodik etabliert (2 Abbrüche zuvor: eager-Default-KeyError, zip-ValueError; Lektion: Buchhaltungs-Pfade mocken, Exit-Codes nicht per Pipe maskieren).

### iter-28 — Signal-Reclass (SE-Kriterium) + Deep-Replikation
Teil 1 rein rechnend (0 GPU) auf iter-26/27-Vektoren; Teil 2: 30 GPU-Läufe (~6 min). **RECLASS_SEVERE | SE_H0_MARGINAL | SE_RECOVERS_NONE | SE_RULES_DIVERGE | DEEP_REPLICATED**: 17/22 (77 %) gebuchte DISTINCT-Labels kippen — exakt die iter-27-Erwartung; auch die dreifach getragene Kante k_edge=10 kippt (0.69 SE); SE-H0 6.4–8.7 % (~3–4× besser als Alt, aber >5 %); SE/t-Regel divergieren 14× in EINE Richtung (t dominiert); 0/21 NULL-Recovery; Deep 3/3: D=0.1 k=3 |t|=7.91 (streut enger als Kontrolle), D=0.3 k=300 |t|=4.05, k=1000 |t|=3.96.

### iter-29 — Welch-t-Kalibrierung + Kandidaten-Replikation
126 5/5-Splits je Anker (0 GPU); 80 GPU-Läufe (~12 min); frischer Block 300–309 mit frischer Kontrolle. **T_H0_CALIBRATED | CAND_REPLICATED_ALL | CAND_ABS_ALL | EXPL_NOT_REPLICATED**: t-H0 0.0/4.0/4.8/0.0/5.6 % — **unter Nominal** im Kontrast zur Paar-Regel (18–27 %): t = Ausreißer-DÄMPFER; **3/3 Kandidaten STRICT repliziert**: D=0.25 k=1 +4.60→**+12.06** (stärkstes Einzelsignal der Linie), D=0.15 k=14 −3.81→−8.57, D=0.05 k=1 −3.42→−5.48; Kontroll-σ 3/4 Blöcke Faktor 3–6 enger (Ausreißer block-abhängig); Explorativzeile D=0.10 k=30 entwertet (2.15→1.01).

### iter-30 — Survivor-Zensus (dritter Block)
100 geplante Läufe (107 inkl. 3 Gate-Verifikationen), ~15 min, Block 310–319. **SURV_ALL | DEEP3_FRESH_REPLICATED | EDGE_SIGNALS**: 4/4 SE-Überlebende repliziert, alle positiv (0.15\|5 t=3.17; 0.3\|30 t=5.55; 0.3\|300 t=4.70; 0.3\|1000 t=4.84); D=0.10 k=3 voll unabhängig |t|=6.98; Kante k_edge=10 zeigt am neuen Block ein krispes negatives Signal (t=−4.21) — iter-28-Flip bleibt Block-Buchhaltung, die Zelle ist block-fluktuierend, nicht tot. Neue Hypothese 3 („Effektstärken nicht block-stabil") — durch iter-31 REVIDIERT. **Persistence-Lücke**: iter-30s result.json trug KEINE per-seed-Vektoren → erzwang Gate-Umbau (Cross-Session-Determinismus, 3 echte Läufe 3/3 bit-identisch vor dem Lauf).

### iter-31 — Block-Stabilität der Effektstärken
280 GPU-Läufe (~46 min), Blöcke 320–329 + 330–339; 9 Kern-Zellen über 4 Blöcke; per-seed voll persistiert (erstmals alle Blöcke). **SAMPLING_DOMINANT | DEPTHS_STABLE_MAJORITY | 9/9 VORZEICHEN_STABIL**: 0/9 BLOCK_REAL (Block-Varianz = Sampling-Rauschen, mehrfach Var_samp > Var_obs); 9/9 CV ≤ 0.5 (engste 0.3\|30 CV 0.05; 0.05\|1 CV 0.05; 0.1\|3 CV 0.08 = stärkstes UND stabilstes Signal +0.1102); erste Tiefen-INTERVALLE. **REVIDIERUNG iter-30-Hypothese 3**: der 0.69-vs-4.21-Vergleich mischte se_units gegen welch_t (Nenner-Inkonsistenz) — like-for-like liest die Kante 0.69/1.58/1.18/1.51 se_units (Faktor ≤2.3); Effektstärken SIND block-stabil, Kante in ALLEN 4 Blöcken negativ (auch Block 1, wo NULL = Signifikanz-, nie Vorzeichen-Aussage). Schema-Fix im Smoke-Stadium (heterogenes t_fresh/welch_t — Crash abgefangen); 2 extern getötete Launches nicht gebucht, dritter (`setsid nohup … & disown`) vollständig.

## 8. Bewusstseins-TCI-Linie (tci_xu → v2 → v3 → v4, 2026-09-26…10-05)

### tci_xu — Agreement-Test gegen Xu et al. (commits a6e3ee7, 06bc9ef)
Vorab-registrierter Agreement-Test: kann der persistente Drive allein Xu-Hirn-Spiralen erzeugen? **SPIRAL_EDGE_ABSENT | X*_REPLICATED**: (a) Drive allein reproduziert Xu-Spiralen NICHT; (b) Source-Data-Re-Analyse — die eigene Plaquette-Formel liest die publizierten Phasenfelder als unit-charge-Kerne (quant 1.000, max|v| exakt 1.000) und repliziert die Paper-Ziffern aufs Digit. Konsequenz: Xu-Formel trägt am Originalmedium; Zellsim-Drive ist noch kein Träger. Daten lokal `scratch/experiments/tci_xu/data/` (Lizenzklärung offen, NICHT committet).

### tci_v2 (= iter-32, commit 00e2bb2) — registrierte FHN-Vektor-Batterie
Ebene-C-Kette im Analog-Medium FHN; 130 Trials, per-seed persistiert. **KETTE_VOR_DER_ERSTEN_STUFE_FALSIFIZIERT**: FHN am Ruhepunkt hat keine Phase ⇒ keine Spiralen — die Kette scheitert vor dem ersten Glied (Q1 ABSENT).

### tci_v3 (= iter-33, commit f05fb2b) — Wirbel-Träger-Theorie TH1–TH4
Brusselator mit Grenzzyklus (Phase vorhanden) + Crowding-Kopplung; registrierter Lauf, 160 per-seed. **GRENZZYKLUS_NOTWENDIG_NICHT_HINREICHEND | R1 SHIFTED**: ~550 Defekt-Kerne/Frame, aber Rausch-Turbulenz-Gas (quant@0.9 = 0.00, gain 0.0); Crowding nukleiert schwach systematisch (+5.9 %, p=0.0013). Phase ist notwendig, nicht hinreichend.

### tci_v4 (= iter-34, commit db57dee) — Hylothese-Kette F1–F6
Struktur-Fitting first-principles (mechanistisch, kein numerisches/statistisches Fitting); 6 Glieder als Formelkette, δ_c = 0.2 Crowding-Route; registrierte Diskrimination, Seeds 1600–1609, 160 per-seed. **R2_NULL — GLIED_iii_FALSIFIZIERT_IN_INSTANZ**: Δacc −0.0250 vs 2·SE 0.1275, welch_p 0.714; gain exakt 0.0 in beiden Armen; Gas-Deskriptoren arminvariant (n_cores 557.3/557.4). Glied (iii) in dieser Instanz falsifiziert; Hebel für tci_v5: Defekt-Gas erst ins annihilations-dominierte Regime steuern, DANN Nachtest.

### Begleitdokumente (Doku-Runde 44fba75)
`scratch/notes/tci_vortex_assessment.md` (§10 Quellen+Anker), `tci_hylothese_formulas.md` (§9 Mermaid-Formelbaum), `tci_vortices_theory.md`, `neuro_vortices_studies.md` (2ba7908, 5 Studien mit verifizierten DOIs). Rohdaten per_seed: LFS Roh-Commit **11949ec** mit drei SHA-256-Manifesten.

## 9. Testsuite als Regressions-Protokoll

- **Stand:** 249 Tests (CLAUDE.md, pytest ~11 s); statisch gezählt 239 `def test_` Definitionen (pytest collect-only listet je-Datei ohne Gesamtzeile); `tests/unit/` 28 Dateien, `tests/integration/` 7 Dateien; Smoke-Marker (`-m smoke`); ruff clean als Lint-Gate.
- **Wachstums-Anker:** 116 (d73c4ca, 2026-08-21) → 144 (6630d65, 2026-08-22) → 160 (iter-9, 2026-08-27) → 184 (iter-13, 2026-08-29) → 213 (iter-18, 2026-09-21) → 249 (iter-23, 2026-09-23).
- **Je-VEKTOR-Neuzuwachs (bekannt):** iter-5 → ququint 16 Tests; iter-13 → +7 (tau-leap) +4 (Sprung-Diffusion) +5 (Sparse-Metrics); iter-15 → superradiance 9; iter-18 → orch_or 14; iter-21 → shielding 10; iter-22 → kick_coupling 11; iter-23 → photonic_coupling (+ Suite 249).
- Jeder Produktion-Übertritt (STRONG/REPLICATED) schlägt Tests nieder; jeder CON­TRA­DIC­TION-Vector hinterlässt keine Tests außer wenn ein Operator-Defekt zum Produktionsfix wurde (iter-13).

## 10. Produktion-Registry (Experiment → Code)

| Modul | Quelle | Tests | Grad-Effekt |
|---|---|---|---|
| `modules/em.py` | iter-1 | — | EM/L3-Brücke |
| `modules/cryptochrome.py` | iter-3 | — | Magnetorezeption |
| `quantum/ququint.py` | iter-5 | 16 | L4; Benchmark repliziert nur 1.1×–1.3× (Grade C) |
| `quantum/tunneling.py` | iter-6 | — | Gate d ≤ 0.3 Å |
| `driver/integration.py` | iter-9 | — | 5 Module in einer Zelle |
| `modules/emergence.py` | iter-10-retry / 13 | 8 + 5 | Sprung-Diffusion + Sparse-Metrics |
| `adapters/rdme.py` (tau-leap) | iter-13/14 | 7 | Damköhler-Fenster im Docstring |
| `modules/superradiance.py` | iter-15 | 9 | N*-Gesetz, Fenster-Konstanten |
| `modules/orch_or.py` | iter-16 / 18 | 14 | Hagan-Parametrisierung, C2-Cap |
| `modules/shielding.py` | iter-21 | 10 | S_max-Metrik |
| `modules/kick_coupling.py` | iter-22 | 11 | N*-Kick-Metrik |
| `modules/photonic_coupling.py` | iter-23 | — | Driver-Flag `--superradiance`, run.csv +4 Spalten |
| `radial_power_spectrum` | iter-17 | 5 | Metrik-Korrektur |
| `scratch/experiments/iter-24/gpu_operator.py` | iter-24 | G1–G5 | 33–34×, experimentell |

## 11. Korrektur-Netz (quer über alle Vektoren)

| # | Fehler | Entdeckt | Korrektur |
|---|---|---|---|
| 1 | 4.18e9×-Enhancement @77 K | iter-6 selbst | im Protokoll als Berechnungsfehler markiert (klassisches Verhältnis statt Enhancement); Wert bleibt in result.json |
| 2 | Orch-OR 27-Dekaden-CONTRADICTION | iter-16 | **RETRACTION**: E_G-Formel dimensional invalid + Kriterium invertiert; iter-7 F→C (OPEN) |
| 3 | iter-11-Kontrolle corr≡1.000 | iter-14 | Determinismus-Artefakt des geteilten rint-Operators; ~90 % des iter-11-Drops = Operator |
| 4 | Operator einseitig drift-behaftet | iter-24 | alter Operator = 3𝒟+Drift; beidseitig driftfrei ab iter-15; iter-14-Buchung präzisiert |
| 5 | Einheiten-Bug D (pro Schritt statt pro Zeit) | iter-17 | Bande ~4.5× zu hoch; korrigierte Dispersion nur post-hoc-Konsistenz, nicht Bestätigung |
| 6 | Metrik-Defekt peak_excess (matched-Null feuert) | iter-17 | ARTIFACT_PATTERN gebucht; Metrik neu |
| 7 | Stencil-Fehler `eig_max_step` (Diagonalmodus) | iter-19 | Diskrimination **VOID**; Integritätsnachweis (5/5 registrierte Zahlen exakt reproduziert) |
| 8 | Registry-Zählung 21 Reaktionen + CLAUDE.md-Stand | iter-20 | 20 Reaktionen/26 Spezies korrigiert (Code + CLAUDE.md + Selbst-Audit) |
| 9 | K3-Gitter außerhalb Lemma-Domäne | iter-23 | **REGISTRATION_ERROR** als R1 dokumentiert (R1-File unangetastet), K3v2 vor R2 |
| 10 | D=0.15-Kante 100 | iter-26 | Gitter-Auflösungs-Artefakt; Kante nicht lokalisiert (≥200) |
| 11 | Oberenden-Regel fehlte im Code | iter-25 | in iter-26 ab Lauf im Code; iter-25-Verdict robust |
| 12 | 17/22 DISTINCT-Labels False-Positives | iter-27/28 | Paar-Regel = Ausreißer-VERSTÄRKER; SE-Kriterium; Welch-t-Regel (H0 unter Nominal, iter-29) |
| 13 | per-seed-NICHT-Persistierung | iter-30 | Persistence-Lücke; ab iter-31 voll (Zellen UND Kontrollen, alle Blöcke) |
| 14 | Effektstärken-Vergleich mischte Nenner | iter-31 | **REVIDIERUNG iter-30-Hypothese 3**; like-for-like: block-stabil (Faktor ≤2.3) |
| 15 | `scratch/SUMMARY.md:45` nennt Orch-OR „FALSIFIED numerisch" | Rekonstruktion 2026-10-05 | **OFFEN** — nach Retraktion (iter-16) dort nie aktualisiert |
| 16 | iter-5 md (1.75×) vs result.json (1) CCZ-Ratio; iter-6 md (1.0000902) vs result.json (2.0457) @0.3 Å | Rekonstruktion 2026-10-05 | **OFFEN** — Zahlenspalten md/JSON gespalten |

Registrierungs-Disziplin-Fazit: keinem genuine Lauf wurde ein K5-Bit-Identitäts-Gate-Verstoß als Verdict untergeschoben; der einzige Regi-Bruch (iter-23 R1) wurde VOR dem Ergebnis-Lauf entdeckt, dokumentiert und nie als Bestätigung gelesen.

## 12. Rohdaten & Integritäts-Anker

- **LFS:** 450 per_seed-JSONs (~792 MB) aus tci_v2/v3/v4 — Roh-Commit `11949ec` (2026-10-05, VOR der Doku-Runde 44fba75 = P3-Ketten-Ordnung: Roh vor Auswertung war hier nachgeholt und als Ketten-Bruch gebooked).
- **Manifeste:** `{dir (repo-root-relative), n_files, manifest_sha256, files:{name:{sha256,bytes}}}`; Manifest-Hash = sha256 von `json.dumps(files, sort_keys=True)`.
- **Re-Verifikation 2026-10-05 (heute):** 450/450 Dateien Byte-exakt, alle drei Manifest-Hashes matchen — ALLE OK.
- **Nicht committet (bewusst):** `scratch/experiments/tci_xu/data/` (Xu-Supplement, Lizenz offen), `neuro_vortices.txt` (Chat-Dump).

## 13. Notiz-, Theorie- und Präsentations-Vektoren

- `scratch/theory/facrm_puzzle_pieces.md` (79 Z., 2026-09-21) — Faizal-Rebuttal-Corpus-Verdict-Log. · `orchor_tegmark_rekonstruktion.md` (127 Z., 2026-09-02) — Orch-OR-Rekonstruktion aus iter-7/16, MT_Sim, Origin_Ruliad, Kurian 2024.
- `scratch/notes/neuro_vortices_studies.md` (110 Z., 2ba7908) — 5 Studien mit verifizierten DOIs (Transkript-Korrekturen: Verzhbinsky, Naqvi-DOI).
- `scratch/notes/tci_vortex_assessment.md` (506 Z.), `tci_hylothese_formulas.md` (364 Z., §9 Mermaid), `tci_vortices_theory.md` (174 Z.), `full_experiment_protocol.md` (diese Datei).
- `scratch/presentation/` (f7c579e, 2026-09-24, SciComPresentationMind) — build_deck.py, scenes.py, design.py, extract_claims.py, claims.json, audit_report.md, cellsim_findings.pptx, deck_manifest.json, media/; 12-Slide-Deck + 3 Manim-Videos über iter-11…26.
- `scratch/SUMMARY.md` (2026-08-21…27 — Phase A/B/D-Ära, Zeile 45 stale), `scratch/README.md` (Workflow), `scratch/results/` (leer), `scratch/strategic_vectors/iter-1…31.md`.

## 14. Offene Queue (Stand 2026-10-05)

1. **tci_v5** — Defekt-Gas ins annihilations-dominierte Regime steuern (Interaktions-Bruch als Ziel-Statistik aus erster Physik, nicht gefittet; disjunkte Seeds ≠ 1600–1609), DANACH Glied-(iii)-Nachtest.
2. **δ_c = 0.5** unverwertet (Crowding-Route).
3. **F6** LZ-Sequenz-Features implementieren.
4. **Xu-Supplement-Lizenz** klären (Daten bleiben lokal).
5. **VECTOR_SHELL1_CASCADE** — seit iter-19 reserviert, nie registriert/gelaufen (Schale-0.131-Anomalie offen).
6. **Buchungs-Offene** — SUMMARY.md:45-Stale-Zeile; iter-5/6-Zahlenspalten md vs result.json.
7. **Damköhler-Linie** — kein offener Vektor registriert; robuster Kern 8 Zellen richtungsstabil (iter-30/31); LINE ENDED bei Block-Stabilität.

## 15. Diff-Audit dieser Rekonstruktion

Reine **Neuanlage** (diese Datei) + Append eines Verweis-Eintrags in `scratch/README.md`: **0 ersetzte Zeilen, 0 in-situ-Mutationen an bestehenden Protokollen/Ergebnissen**. Alle Verdicts VERBATIM; alle Discrepancy-Items (§11 #15/#16) als OFFEN gebucht statt stillschweigend korrigiert.

## Anhang A — Commit-Ledger (41 Commits, chronologisch)

```
d73c4ca 2026-08-21 Initial cellsim: L1-L4 + alle 5 Limitations adressiert (116 Tests grün)
bbd7759 2026-08-21 iter-1 (EM-Schicht) + iter-2 (UV-Sync, verdächtig) + PLAN_ZIEL.md
6509396 2026-08-22 iter-2-retry (CONTRADICTION) + iter-3 STRONG + Cryptochrom-Schicht
c9e6ad2 2026-08-22 PLAN_ZIEL.md: Phase A → B Übergang, 3 Iters dokumentiert
ebfc467 2026-08-22 iter-4 (CONTRADICTION N-Zellen) + iter-5 (QuQuint-VQE STRONG)
6630d65 2026-08-22 SUMMARY.md: 5 Iters, 144 Tests, 5 Commits, Phasen-Empfehlung
aa913a3 2026-08-27 iter-6 (Proton-Tunneling STRONG selektiv) + Production-Modul
a113396 2026-08-27 iter-7 (Orch-OR CONTRADICTION) + LIMITATIONS.md erweitert
0dcb49f 2026-08-27 iter-8 (UV-Sync CONTRADICTION final) + UV-Sync-Hypothese archiviert
1573cb9 2026-08-27 iter-9 (Integration STRONG) + Phase D + final Summary
d0e1665 2026-08-28 iter-10 (Origin_Ruliad-Integration): Ruliad-Emergenz-Metriken im RDME
04ea439 2026-08-28 iter-11+12: Damköhler-Fenster (Rate-Sweep) + Genesis-UVC-Brücke
18afed1 2026-08-29 iter-13 (Produktions-Sprint): Tau-Leap + Sprung-Diffusion + Sparse-Metrics
3fa5753 2026-08-30 iter-14 (Falsifikator): Damköhler-Replication on Production Stack
17c2dd6 2026-08-30 iter-14 Nachtrag: Vorbehalt in iter-11-Vektoren + Lint
84b26d6 2026-09-02 iter-15 (Plan + Rekonstruktion): Orch-OR/Trp-Superradianz-Kanal
dc014ce 2026-09-02 iter-15+16: Superradianz-Brücke (N*-Gesetz) + Orch-OR-Korrektur (Formel-Artefakt)
88dd5e2 2026-09-02 iter-15/16 Lint
aa80461 2026-09-21 iter-17+18: Turing-RDME-Falsifikator (Einheiten-Bug isoliert) + OR-Kollaps-Kern
29d8735 2026-09-21 iter-20 (Falsifikator): Registry trägt kein Turing-Substrat
a685b74 2026-09-21 iter-19 (abgeschlossen): L=48-Lauf sauber, Diskrimination VOID — Stencil-Fehler
8fd6260 2026-09-23 iter-21 (VECTOR_SHIELDING_FIELD): S=1e6-Schild nicht ableitbar
a39d63c 2026-09-23 iter-22 (VECTOR_OR_KICK_COUPLING): Kick energetisch entwertet in der Box
22322ff 2026-09-23 iter-23: Photonische Kopplung produziert + Falsifikator
d18edfa 2026-09-23 iter-24: WINDOW_REPLICATION_V2 (8/9) + GPU-Operator-Port
18d5f41 2026-09-23 iter-25: VECTOR_SATURATION_MARGIN (Kante 10×)
f944e75 2026-09-24 iter-26 (VECTOR_EDGE_FINE_SWEEP): Feingitter-Kante + D-Abhängigkeit
f7c579e 2026-09-24 Präsentation (SciComPresentationMind): 12-Slide-Deck + 3 Manim-Videos
166d1a9 2026-09-24 iter-27 (VECTOR_STOCH_CONTROL_METRIC): Seed-Budget n=10
96600c6 2026-09-24 iter-28: Signal-Reclass (SE-Kriterium) + Deep-Cell-Replikation
6f6028d 2026-09-24 iter-29 (T-Regel-Kalibrierung + Kandidaten-Replikation)
08a8645 2026-09-24 iter-30 (Survivor-Zensus, dritter Block)
c1aaa86 2026-09-28 iter-31: Block-Stabilität der Effektstärken
2ba7908 2026-09-28 Neuro-Vortices: verifizierte Studien + DOIs
a6e3ee7 2026-09-28 TCI↔Xu Agreement-Test (pre-registriert)
06bc9ef 2026-09-28 tci_xu_data Re-Analyse: Xu-Source-Data mit der registrierten Formel gelesen
00e2bb2 2026-09-28 iter-32 (tci_v2): registrierte FHN-Vektor-Batterie — Ebene C falsifiziert
f05fb2b 2026-09-28 iter-33 (tci_v3): Wirbel-Träger-Theorie TH1-TH4 — R1 SHIFTED
db57dee 2026-09-29 iter-17 Nachtrag + iter-34: Hylothese-Kette F1-F6 + tci_v4-Lauf (R2_NULL)
11949ec 2026-10-05 Rohdaten tci_v2/v3/v4 per_seed als Git LFS + SHA-256-Manifeste
44fba75 2026-10-05 Doku-Runde TCI-Wirbel-Linie: Zitate (DOIs), LFS-Anker, Ledger-Nachträge
```