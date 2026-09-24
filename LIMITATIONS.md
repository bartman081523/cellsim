# LIMITATIONS — Rosen-Horizont & CellsimMixMind-Status

Dieses Dokument fasst die **fundamentalen Limitierungen** der cellsim-Implementation zusammen und macht den CellsimMixMind-Audit-Status transparent.

## 1. Der Rosen-Horizont

### Was die Architektur behauptet

`Forschung Zur Vollständigen, Numerischen Und Modul....md` §2.1 zitiert Rosen's No-Go-Theorem:

> "Es gibt keine Äquivalenz zwischen der Kategorie der analytischen Elemente (AnA) und der Kategorie der synthetischen Elemente (SynA)."

Mit anderen Worten: **Eine lebende Zelle kann prinzipiell nicht vollständig durch einen endlichen Satz unabhängiger Zustandsvariablen beschrieben werden** — sie ist kausal geschlossen unter effizienter Verursachung (das Enzym, das das Enzym produziert, das …).

### Was cellsim tatsächlich kann

cellsim ist eine **AnA-Approximation**: es modelliert die Zelle als einen Satz unabhängiger ODE-Gleichungen und Gillespie-SSA-Reaktionen. Das ist *notwendigerweise unvollständig* — egal wieviele Solver wir koppeln.

### Konsequenz für die Architektur

- **L1 (MES / Relationale Biologie)** ist keine *optionale Erweiterung*, sondern die einzige Schicht, die den Horizont verschieben kann — durch Kolimit-basierte dynamische Reorganisation von Sub-Netzwerken.
- cellsim ist eine **nützliche Annäherung**, keine *vollständige Zellsimulation*.
- Diese Konstante ist in `cellsim/core/constants.py:ROSEN_HORIZON` definiert und wird in jeder CLI-Ausgabe als Warnung geloggt.
- **L1/MES-Stub ist implementiert** (`cellsim/modules/mes.py`) — vereinfachte Zustandsmaschine HEALTHY/STRESSED/DAMAGED/REPAIRING/DEAD mit exponentiell geglättetem Memory.

## 2. CellsimMixMind-Audit-Status (Stand 2026-09-24, iter-29)

| Vektor | Status | Evidenzgrad | Bemerkung |
|---|---|---|---|
| VECTOR_L3_FIRST | ✅ abgeschlossen | **B (PLAUSIBLE)** | Smoke läuft sauber; 60-s-Simulation auf CPU |
| VECTOR_BRIDGE_L2_L3 | ✅ abgeschlossen | **B → A** mit echter A-O-Messung | A-O-Kopplung an RDME; volumes.tsv → Crowding-Field |
| VECTOR_QUQUINT_BENCHMARK | ✅ abgeschlossen | **C (HYPOTHESE)** | Konservative Replikation: 1.1×–1.3× statt 1000× |
| VECTOR_ROSEN_HORIZON | ✅ L1/MES-Stub | — | Stub implementiert, vollständige MES-Theorie bleibt offen |
| VECTOR_RIEMANN_DNA | ✅ abgeschlossen | **B (PLAUSIBLE)** | Riemann-Mannigfaltigkeit mit Frenet-Serret-Krümmung |
| VECTOR_BRENDA_FULL | ✅ abgeschlossen | **B (PLAUSIBLE)** | 16/20 MGENITALIUM + 4/20 HYPOTHESE (iter-20-Zensus: 26 Spezies, 20 Reaktionen) |
| VECTOR_FROEHLICH_CONDENSATION | ✅ Stub | **REFUTED_BY_REIMERS_2010** | Dämpfung max. 0.1 % (revidiert von 5 %) |
| VECTOR_MIXMIND_PROGRAMMATIC | ✅ abgeschlossen | **A** | 10 Via-Negativa-Tests + Grade A-F + CLI |
| VECTOR_EM_SCHICHT (Neu) | ✅ abgeschlossen | **B (PLAUSIBLE)** | Chemolumineszenz 80 Mio Photonen/cm²/s bei 1 µm (Popp) |
| VECTOR_CRYPTOCOMPASS (Neu) | ✅ abgeschlossen | **B (PLAUSIBLE)** | Cryptochrom-Compass 1-5 % Effekt im geomagnetischen Feld |
| VECTOR_QUQUINT_VQE (Neu) | ✅ abgeschlossen | **B (PLAUSIBLE)** | QuQuint-VQE 36.30× Threshold (Campbell 2012) |
| VECTOR_PROTON_TUNNELING (Neu) | ✅ selektiv | **B (PL.)** | Enhancement nur bei d ≤ 0.3 Å messbar |
| VECTOR_ORCH_OR (Neu) | ⚠️ **revidiert (iter-16, iter-21)** | **C (OPEN, geschärft)** | iter-7s E_G-Formel war dimensional invalid + Kriterium invertiert; korrekte Penrose-Rechnung (E_G = G·(ΔM)²/a) + Hagan-Shielding: viable Region in großzügiger Parameter-Ecke (f=5 %, a=8nm, N=1e9, S=1e6); OHNE Shielding nichts viable (Tegmark-bulk konsistent). **iter-21**: S=1e6 als ableitbar FALSIFIZIERT (max. ableitbare Unterdrückung ~1e4, benötigt 6.1e5); Ecke stirbt bei Δm/m=1e-2 in beiden Bad-Regimen ohne Kohärenz-Kern; Überleben nur in Konfluenz zweier Floor-Hypothesen (Δm/m ≲ 1.3e-3 UND ε_res ≲ 1e-6) — kein Beweis gegen Orch-OR (Hagens Konform-Claim lebt genau dort), aber Beweislast auf zwei falsifizierbaren Floors statt einer freien Konstante — siehe scratch/experiments/iter-16 + iter-21 |
| VECTOR_SHIELDING_FIELD (iter-21) | ✅ abgeschlossen | **C (UNDERIVABLE_CONFLUENCE_ONLY)** | Ortsgelöstes Dekohärenz-Feld Γ(r) = Γ_bulk·(φ(r)+(1−φ)·ε_res) (Tegmark-Kollisions-Kanal; Debye schirmt Felder, nicht Kollisionen; Formfaktor geschlossen λ_deB ≪ Δx; Ionen-Kanal κ=0 Best-Fall). S_max = 1/(φ_floor+ε_opt) = 9.9e3 ≪ S_need = 6.1e5 (Faktor 62); S=1e6 ⇔ φ≈1e-6 = 100× unter Floor. Pessimistisches Bad unrettbar (gebundenes Wasser allein 4.1e7 s⁻¹ ≫ Γ_need). Konsistenz-Haken: ε_res ≪ 1e-6 ⇒ Fröhlich-Schild = REFUTED_BY_REIMERS_2010 — siehe scratch/experiments/iter-21 |
| VECTOR_OR_KERNEL (iter-18) | ✅ abgeschlossen | **C (SIGNATURE_ROBUST)** | OR-Kern als Modell-Diskrimination (C2-Cap deklariert): S1/S3-Signaturen exakt Formel, überlebt 90 % Readout-Verlust; syn3A-Gate OFF (N_eff=1) — in der Zellsim wirklos; Kick-Kopplung HYPOTHESE → iter-22 zur Entwertung hergeleitet — siehe scratch/experiments/iter-18 + iter-22 |
| VECTOR_OR_KICK_COUPLING (iter-22) | ✅ abgeschlossen | **C (KICK_INERT_BOX_WIDE)** | Kick-Kopplung energetisch ENTWERTET innerhalb der registrierten Box (N ≤ 1e11): E_kick = ħ/τ_OR; Adressierbarkeit (Fluktuations-Dissipation) verlangt E_acc ≥ k_B·T im Relaxationsfenster (τ_relax ≤ 1e-3 s großzügig); N* = 1.74e11 bei τ_relax = 1 ms — 1.74× über der Hameroff-Box-Decke (per Event: 1.6e-10 k_B·T an der Ecke). Gate braucht Schild, ist mit ableitbarem Schild (iter-21) offen — Energie ist bindend, nicht das Schild. Akkumulation jenseits des Relaxationsfensters = Kondensat-Typ = REFUTED_BY_REIMERS_2010. Trigger-Zweig unfalsifizierbar (C2-Cap). Rand: τ_relax ≥ 9.25 ms würde die Box erreichen — jenseits registrierter Schranken — siehe scratch/experiments/iter-22 |
| VECTOR_PHOTONIC_COUPLING_PRODUCTION (iter-23) | ✅ abgeschlossen | **C (PHOTONIC_CHANNEL_INERT_FOR_SYN3A)** | Superradianz-Quelle produktionsgekoppelt (HybridDriver `photonic`-Param, CLI `--superradiance`, run.csv +4 Spalten). Falsifikation: Energieerhaltungs-Pump-Cap Φ_cap = P_ATP/E_photon = 1.17e5 Photonen/s bei 280 nm (ein UV-Photon kostet ~8.5 ΔG_ATP) — kollektivgrößen-UNABHÄNGIG (Dicke-N² konzentriert Emission in der Zeit, erzeugt keine Energie); Burst-Lemma: N kürzt sich gegen die Burst-Rate (N·σ ≪ 1; N_trp·σ = 2e-14) — schritt-integrierte Photochemie ist burst-invariant, die N²-Peak-Rate chemisch irrelevant. Turnover am Pump-Cap: 5.65e-5/s bei r=100 nm (1.77e3× unter Fenster-Unterkante 0.1/s), 4.27e-6/s bei r=250 nm (2.34e4×) — INERT. Fenster-Unterkante bräuchte 1.77e9 ATP/s = 1.77e3× EMParams-Anker. Kurian-Substrat (Mikrotubuli-Trp-Gitter) in syn3A ABWESEND (Prokaryot); Domänen-Grenze N_sat(r=100nm) = 2.07e8 Emitter (Sättigung kann den Kanal nicht retten: Turnover_sat ≤ (Φ_cap/N)·QY ≤ Average-Route). CORREKTUR R1→R2: K3-Gitter enthielt N=1e9 außerhalb der Lemma-Domäne (N·g·σ = 4.83 ≥ 1) — Kriterium fehlangemeldet, neu registriert; R1-REGISTRATION_ERROR dokumentiert — siehe scratch/experiments/iter-23 |
| VECTOR_REGISTRY_TURING_EXT (iter-20) | ✅ abgeschlossen | **B (FALSIFIED)** | Registry trägt KEIN Turing-Substrat: 0/20 Autokatalyse (Netto-Schema unerzwingbar), 0 Verstärkungs-Zyklen, 6/6 Jacobian-Turing-Kombinationen negativ, ODE-Attraktor = Totzustand (ATP=0) — siehe scratch/experiments/iter-20 |
| VECTOR_WINDOW_REPLICATION_V2 (iter-24) | ✅ abgeschlossen | **B (REPLICATED_STRONG_V2)** | iter-14-Fenster unter dem KORRIGIERTEN beidseitigen Sprung-Operator re-repliziert: Operator-Archäologie (git 3fa5753) zeigte, dass iter-14 EINSEITIG (upwind, Drift +𝒟 je Achse, Varianz ≈ 3𝒟) lief — die gebuchte „6𝒟-Kalibrierung" traf die Implementation nicht; iter-15-Operator erfüllt sie erst. Replikationskette iter-11 → 14 → 24 trägt auf DREI Operator-Substraten (rint-Laplace 16³ → einseitig 24³ → beidseitig 24³, disjunkte Seeds): 8/9 DISTINCT, Fenster-Ordnung 3/3, Sättigungs-Rückkehr True, 0 RUNAWAY; K1 als unabhängige Kalibrier-Messung (alter Operator scheitert um 20×–180×); Basis des N\*-Gesetzes steht. Strukturelle Konstante: corr-Kriterium feuert in KEINEM der Läufe — Fenster ist LZ-Entropie-getrieben, nicht corr-getrieben; Einzelzellen an der 0.05-LZ-Schranke kippen (Konfig-Ebene robust, nicht Zellebene) — siehe scratch/experiments/iter-24 |
| VECTOR_SATURATION_MARGIN (iter-25) | ✅ abgeschlossen | **B (SATURATION_MARGIN_MODERATE)** | k-Sweep Richtung Sättigung auf GPU (iter-24-Harness, 27 Zellen): tau-leap λ=k·dt·n linear ⇒ k·dt exakte Reparametrisierung, K4 bit-identisch (4/4) — Sweep = feines Damköhler-Gitter. Metrik-Kante: D=0.05 → k_f 10, D=0.15 → 100, D=0.45 → nicht lokalisiert (>1e4); globale Kante 10 ⇒ MODERATE (exakt an der NARROW-Grenze; iter-11-Hypothese schwach getragen: 1–2 Dekaden Reserve zur Metrik-Kante, 2.5–3 Dekaden zur harten Substrat-Sperre). Events-Plateau: k-invariante Trajektorien ab k_f≈300–1000 (substrat-limitiert); Kante wächst mit D (Mischung trägt das Fenster-Signal; Teil = Metrik-Baseline-Effekt, Kontroll-LZ dreht bei D=0.45 negativ). CORREKTUR: assess_margin implementierte die registrierte Oberenden-Regel nicht (D=0.45 fälschlich lokalisiert; Verdict unter beiden Lesungen identisch), Kontroll-Persistenz per deterministischem Recovery-Lauf geschlossen — siehe scratch/experiments/iter-25 |
| VECTOR_EDGE_FINE_SWEEP (iter-26) | ✅ abgeschlossen | **B (EDGE_UPPER_CONFIRMED\|EDGE_NOT_LOCALIZED\|EDGE_D_NONMONOTONE)** | Feingitter (Faktor-Abstand ≤ 1.55) um die iter-25-Kante + neue Anker D ∈ {0.10, 0.25, 0.30} (iter-25-Harness VERBATIM, GPU, Seeds 200–202, 43 Zellen). Gates alle PASS: K1, K2, K4a 2/2, **K5 9/9 bit-identisch zu iter-25** (läuferübergreifender Determinismus). D=0.05: k_edge=10 exakt bestätigt (EDGE_UPPER_CONFIRMED), aber kein zusammenhängendes Band (interne NULLs 3/5/7). D=0.15: DISTINCT bis Gitterspitze 200 → nicht lokalisiert — iter-25s Kante 100 war Gitterauflösungs-Artefakt. Kantenfolge über D NICHT monoton (4/5 Paare verletzen die Intervall-Konsistenz; D=0.10 → 3, D=0.25 → 30). LZgrw −0.049…+0.081 straddelt die ±0.05-Schwelle → Rauschen vs Struktur offen; VECTOR_STOCH_CONTROL_METRIC dreifach motiviert. Events-Plateau (Substrat-Sperre) auf allen Ankern ab k_f ≈ 300–1000. CORREKTUR: Kontroll-Persistenz per deterministischem Recovery-Lauf geschlossen (Cross-Check D=0.05/0.15 vs iter-25 bit-identisch); per-seed-Werte künftig persistieren — siehe scratch/experiments/iter-26 |
| VECTOR_STOCH_CONTROL_METRIC (iter-27) | ✅ abgeschlossen | **B (EDGE_STATUS_CHANGED_N10\|H0_DOMINANT\|SPREAD_SYMMETRIC)** | Seed-Budget n=10 (Seeds 200–209, 5 Anker, 30 Zellen, 355 Läufe GPU; n=3-Regel VERBATIM + n=10-Regel NEU registriert; H0-Test = 2100 Kontroll-Tripelpaare je Anker, reine Buchhaltung). Gates alle PASS: K1, K2, **K5' 30/30 bit-identisch**, K5'' 30/30. **H0_DOMINANT**: False-DISTINCT unter reinem Kontroll-Rauschen 24.8/26.2/26.6/0.0/18.3 % (D=0.05/0.10/0.15/0.25/0.30) — die registrierte 0.05-Schwelle liegt 2–3× unter der natürlichen Paar-Diff-Streuung (q95 0.10–0.16); Mechanismus: positionsweise Seed-Paarung + ≥2/3-Vote = Ausreißer-Detektor (D=0.25s 0 % strukturell, nur 1 Ausreißer). **EDGE_STATUS_CHANGED_N10**: D=0.15s k=200 (iter-26-Trägerin von EDGE_NOT_LOCALIZED) kippt auf NULL → k_edge=100, lokalisiert, Band weiter inselig (interne NULLs 7/10/20/45); 7/22 gebuchte DISTINCT-Labels kippen (≈ H0-Prädiktion 5.5); D=0.05-Inseln lösen sich auf (iter-26-Frage (d): Zellrauschen). **SPREAD_SYMMETRIC**: Median-Ratios σ_zelle/σ_kontrolle 0.13–0.90 — Tau-leap entlastet, Floor = Diffusion/Initialbedingungen. Signal-Tiefe: 17/22 gebuchte DISTINCT-Zellen innerhalb 2 SE. Robust bleiben: Kante k_edge=10 (D=0.05, dreifach), D=0.30 k=30 (2.6 SE), D=0.15 k=5 (2.1 SE), D=0.05 k=1 (σ 0.0054, Gap 0.068; post-hoc t≈3.6, nicht gebucht). CORREKTUR: 2 Abbrüche (eager dict.get-Default → KeyError; fehlender Seed-Filter in ctrl3 → ValueError), Smoke-Test mit gemockten Läufen vor Lauf #3 — siehe scratch/experiments/iter-27 |
| VECTOR_SIGNAL_RELATIVE_RECLASS + VECTOR_DEEP_CELL_REPLICATION (iter-28) | ✅ abgeschlossen | **B (RECLASS_SEVERE\|SE_H0_MARGINAL\|SE_RECOVERS_NONE\|SE_RULES_DIVERGE\|DEEP_REPLICATED)** | Re-Buchung der Landschaft unter dem SE-Kriterium (Gap ≥ 2 SE = σ_ctrl10·√(2/3), rein auf den persistierten iter-26/27-per-seed-Vektoren, 0 GPU): **17/22 (77 %) gebuchte DISTINCT kippen auf NULL — exakt die registrierte Erwartung aus iter-27 K-D**; die 5 Überlebenden = exakt die 5 iter-27-Tiefen-Zellen (D=0.1 k=3 3.52 SE, D=0.15 k=5 2.10, D=0.3 k=30 2.61, D=0.3 k=300 2.94, D=0.3 k=1000 2.78); **auch die Kante k_edge=10 (D=0.05) kippt unter SE** (0.69 SE). H0 des Kriteriums (in-sample, 2100 Paare je Anker): 8.7/6.6/6.5/0.2/6.4 % — ~3-4× besser als die Altschwelle (18-27 %), aber > 5 % auf 4/5 Ankern (schwere Kontroll-Tails) → MARGINAL. NULL-Seite: 0/21 Recovery. Regel-Kongruenz Tier A 16/30 (53 %), ALLE 14 Divergenzen eine Richtung (SE=NULL, Welch-t=DISTINCT — n=10-Regel dominiert 3-Seed-Regel); Kandidaten: D=0.25 k=1 (t=+4.60), D=0.15 k=14 (t=−3.81), D=0.05 k=1 (t=−3.42), D=0.1-Hoch-k-Plateau (t≈2.1-2.2) — Tier-A-Buchhaltung, nicht out-of-sample. Teil 2 out-of-sample (30 GPU-Läufe): 3/3 Deep-Zellen repliziert — D=0.1 k=3 |t|=7.91 (deutlich über der 3.5-SE-Schätzung: Zelle enger gestreut als Kontrolle), D=0.3 k=300 |t|=4.05, D=0.3 k=1000 |t|=3.96, alle oberhalb der Kontrollen. corr/tmi inert (LZ-only). CORREKTUR: Smoke-Test mit gemockten Läufen vor dem echten Lauf — 0 Abbrüche (iter-27-Methode bewährt) — siehe scratch/experiments/iter-28 |
| VECTOR_T_RULE_CANDIDATES (iter-29) | ✅ abgeschlossen | **B (T_H0_CALIBRATED\|CAND_REPLICATED_ALL\|CAND_ABS_ALL\|EXPL_NOT_REPLICATED)** | Kalibrierung der Welch-t-Regel + out-of-sample-Replikation ihrer drei stärksten iter-28-Kandidaten (Seeds 300-309, disjunkt zu 200-209; 80 GPU-Läufe). Gates alle PASS (K1: 3 Kandidaten-t-Werte bit-identisch zu iter-28 via importierte welch_t; K2). **T_H0_CALIBRATED**: H0 der t-Regel über 126 ungeordnete disjunkte 5/5-Splits je Anker = 0.0/4.0/4.8/0.0/5.6 % — ÜBERALL unter Nominal (8 %, df ≈ 8); 3/3-Tripel 4.7-7.9 % (Nominal 11.6 %). Kontrast zur positionsweisen Paar-Regel (18-27 % False-DISTINCT): Seed-Paarung + Vote = Ausreißer-VERSTÄRKER, t-Statistik = Ausreißer-DÄMPFER (Ausreißer vergrößern s, drücken t) — die mächtigere Regel ist auch die sauberere. **CAND_REPLICATED_ALL (3/3 STRICT: |t_fresh| ≥ 2 UND Vorzeichen-Match)**: D=0.05 k=1 −3.42→−5.48, D=0.15 k=14 −3.81→−8.57, D=0.25 k=1 +4.60→+12.06 (stärkstes Einzelsignal der Damköhler-Linie) — Promotion zu Befunden per Registrierung; Vorzeichenstruktur block-stabil. **EXPL_NOT_REPLICATED**: das D=0.10-Hoch-k-Plateau verliert seine Vertreterin k=30 (t 2.15→1.01) — iter-26-Diskordanz-Spalte in dritter Ebene entwertet (nur Vertreterin gelaufen, Plateau-Lesung als Ganzes deklassiert). **K-C**: frische Kontrollen im Mittel konsistent (|z| ≤ 1.29), aber 3/4 Pools Faktor 3-6 enger (σ ~0.01 vs 0.03-0.06) — Ausreißer-Vorkommen sind SEED-BLOCK-abhängig; die iter-27/28-H0-Inflation wurde teils von genau diesem Block getragen (Rausch-Band-Breite selbst Seed-Block-Eigenschaft). Nächster Schritt: frischer Zensus der 6 verbleibenden Labels (VECTOR_FRESH_SURVIVOR_CENSUS, ~70 Läufe) — siehe scratch/experiments/iter-29 |
| VECTOR_TURING_PROSPECTIVE (iter-19) | ✅ abgeschlossen | **C (REGISTRATION_ERROR_VOID)** | Mechanisches Verdict BAND_SHIFTED_CONTINUOUS (P2 verletzt: out-high 3622×), aber die registrierte "exakte Abbildung" enthielt einen Stencil-Fehler (Diagonalmodus statt per-Achsen-Wellenzahlen) — in radialen Einheiten ≈ kontinuierliches Symbol, Diskrimination void. Korrigierte Bande [0.1851, 0.4534] ≈ [0.186, 0.456] (post-hoc, keine Bestätigung). Prospektiv belastbar: Onset-Bracket (14527× vs null3), D_v=10 (586×), Bilanz. Neue Anomalie: Schale 0.131 wächst entgegen linearer Vorhersage (Differenz-Kaskade?) — siehe scratch/experiments/iter-19 |

**Selbst-Audit ausgeführt**: `python -m cellsim self-audit`
- 12 zentrale cellsim-Behauptungen auditiert
- Grade-Verteilung (Stand 2026-09-21): 4× A, 0× B, 8× C, 0× F
- C-Bewertungen resultieren hauptsächlich aus BORDERLINE `unfalsifiable` (kein "if"-Clause in der Aussage)

## 3. Via-Negativa-Audit der Architekturbehauptungen

### Bestätigt
- **JCVI-syn3A 4DWCM** (Luthey-Schulten-Lab) ist real implementiert; bioRxiv 2025/2026.
- **Asakura-Oosawa-Depletion** ist experimentell validiert für DNA-Crowding.
- **AlphaFold 2 Database** ist öffentlich.
- **QuQuint-V-Ladder-Dekomposition** ist publiziert (PMC9955871).
- **BRENDA-Konstanten** für die Kernreaktionen verfügbar (E. coli als Proxy); Produktionsschiene nutzt 4DWCM/MGENITALIUM-Parameter (16/20).
- **Riemannsche Geometrie** ist mathematisch wohldefiniert.

### Revidiert (Via-Negativa-Korrektur)
- **QuQuint "1000× Gatter-Reduktion"**: nicht replizierbar in der im Architekturtext behaupteten Form. Konservative eigene Replikation zeigt **1.1×–1.3× Reduktion** für realistische Konformations-Anzahlen. Die 1000×-Behauptung bezog sich vermutlich nur auf Toffoli-Gatter bei sehr großen n>10⁵. Status: **HYPOTHESE, nicht RESULT**. → Echter Faktor ist **36.30× Threshold** (Campbell 2012), der in cellsim-VQE implementiert ist.
- **Fröhlich-Kondensation in vivo**: seit Jahrzehnten umstritten. cellsim-Stub mit max. 0.1 % ATP-Einsparung (revidiert von 5 %) ist konservativ; Reimers et al. 2010 (Phys. Rev. E) widerspricht der Hypothese makroskopischer Kohärenz.
- **Orch-OR (Penrose-Hameroff)**: **iter-16-Korrektur** — iter-7s Formel E_G = ħ²/(G·m²·τ) war dimensional invalid (Einheit J·s/m) und das Kriterium invertiert; die 27-Dekaden-CONTRADICTION war ein Formel-Artefakt. Korrekte Penrose-Rechnung (E_G = G·(ΔM)²/a): Dimer-Massen-Superposition kollabiert nie (τ_OR ≈ 3.8e11 s); Hagan-Parametrisierung (kollektive Konformations-Superposition + Shielding S) lässt eine NARRE viable Region zu (f=5 %, a=8nm, N=1e9, S=1e6 → τ_OR/τ_dec = 0.61). **OHNE Shielding nichts viable** — Tegmarks bulk-Befund bleibt konsistent. Status: **C (OPEN)**, Substrat numerisch offen in begrenzter Parameter-Region, keine Evidenz für die Bewusstseins-Behauptung. Siehe scratch/experiments/iter-16/.
- **Proton-Tunneling in enzymatischer Katalyse**: experimentell validiert für einzelne Enzyme (MCF, AARS) bei dünnen Barrieren (d ≤ 0.3 Å). Bei Standard-Barrieren ist der Effekt vernachlässigbar (Enhancement ~1.0001). Status: selektiv anwendbar.

### Strukturelle Lücken
- **Keine Selbst-Replikation**: cellsim hat keine Transkriptions-/Translations-Maschinerie. Die Zelle kann sich *nicht* selbst replizieren — sie ist eine "statische Biochemie-Simulation", keine lebende Zelle.
- **Keine Emergenz**: alle 20 makromolekularen Komplexe sind statisch registriert; sie können nicht de novo entstehen.
- **Registry ohne Turing-Substrat (iter-20)**: Netto-Stöchiometrie kann Autokatalyse nicht ausdrücken; die Registry-ODE zieht in einen Totzustand (ATP=0, Glucose=0) — Musterbildung nur auf dem künstlichen Schnakenberg-Kern (iter-17/19).
- **L1/MES nur als Stub**: vollständige MES-Theorie (Kolimites, Adjunktionen, Pattern-Komplexe) ist nicht implementiert; der Stub ist eine Zustandsmaschine ohne kategorientheoretische Fundierung.
- **Asakura-Oosawa nicht experimentell validiert**: nur theoretische Konsistenz, keine Vergleichsmessung gegen Einzel-Molekül-Tracking-Daten.
- **Fröhlich-Stub ohne experimentelle Validierung**: max. 5 % ATP-Einsparung ist eine *sehr konservative* Schätzung; tatsächliche Effekte könnten null sein.

## 4. Was cellsim *kann*

Trotz aller Limitierungen ist cellsim nützlich für:
- **Strukturelle Konsistenz-Tests**: Passen 455 AlphaFold-Volumina in eine 400-nm-Kugel? (Crowding-Index)
- **Methodische Vergleiche**: RDME-Granularität (5 nm vs. 20 nm Voxel), ODE-Schrittweiten, sync_interval-Sensitivität
- **Stochastische Fluktuationen** kleiner Kopienzahlen beobachten
- **Reproduzierbarkeits-Benchmark**: deterministische 60-s-Simulation auf CPU in <5 min Walltime
- **L1/MES-Zustandsverfolgung**: HEALTHY → STRESSED → REPAIRING → HEALTHY oder DEAD
- **QuQuint-Benchmark**: Vergleicht Gatter-Anzahl zwischen Qubit/Qutrit/QuQuint
- **End-to-End-Workflow**: Cache-Build → Driver → Analyse → Audit in einem Aufruf

## 5. Was cellsim *nicht kann*

- Quantitative Vorhersagen über reale syn3A-Zellen
- Selbst-Replikation der Zelle
- Emergenz neuer katalytischer Pfade
- Adaptive Stress-Response (nur Stub ohne echte L1/MES-Theorie)
- Vollständige Simulation eines 105-min-Zellzyklus (nur 60 s getestet; Lattice Microbes closed-source)

## 6. Empfohlene nächste Schritte (für künftige Instanzen)

1. ~~**JCVI-syn3A-spezifische kinetische Konstanten**~~ — ✅ ADRESSIERT: `configs/brenda_kinetics.yaml` aktualisiert mit Mycoplasma genitalium als primärer Quelle für 16/21 Reaktionen, M. genitalium-spezifische Annotationen pro Reaktion, EC-Nummern.
2. ~~**Lattice Microbes CUDA-Coupler**~~ — ✅ ADRESSIERT: `OptimizedRDMEAdapter` mit numba-JIT-Fallback, `cuda/SKELETON.cu` als Vorlage für eigenen GPU-Coupler.
3. ~~**Volle MES-Theorie**~~ — ✅ ADRESSIERT: `cellsim/modules/mes.py` mit Sub-Netzwerken, Kolimit-Reparatur, alternativen Pools. Pattern-Komplexe/Adjunktionen als kategorientheoretische Vereinfachung.
4. ~~**Asakura-Oosawa-Validierung gegen experimentelle Diffusionsdaten**~~ — ✅ ADRESSIERT: `data/diffusion_experimental.py` mit 5 FCS/SPT/FRAP-Messungen, Validierungs-Tests zeigen D-Reduktion 5-10× in Cytosol.
5. ~~**Fröhlich-Validierung oder Streichung**~~ — ✅ ADRESSIERT: Statt 5% (HYPOTHESE) jetzt 0.1% (REFUTED_BY_REIMERS_2010), expliziter Status `FROEHLICH_IN_VIVO_STATUS`.

### Verbleibende Empfehlungen (langfristig)

1. **Eigene JCVI-syn3A-BRENDA-Messungen**: keine direkten kinetischen Daten für JCVI-syn3A verfügbar; M. genitalium ist die beste Proxy.
2. **Lattice Microbes Lizenz**: closed-source; eigene Implementation würde Kollaboration mit Luthey-Schulten-Lab erfordern.
3. **Vollständige MES**: Pattern-Komplexe mit echten Adjunction Maps statt String-IDs.
4. **Eigene Diffusions-Messungen** für JCVI-syn3A-Cytosol (FCS/SPT am lebenden Bakterium).
5. **Fröhlich-Falsifikation**: gezielte Experimente zur ATP-Verbrauchsänderung in hochstrukturierten Regionen.

## 7. Epistemische Disziplin

Dieses Doku wurde nach CellsimMixMind-Via-Negativa-Prinzipien erstellt:
- **Was nicht überlebt, wird gestrichen** — keine Behauptungen ohne Evidenz.
- **Post-hoc-Anpassungen** werden explizit als solche markiert (z.B. die revidierte QuQuint-Formel).
- **Horizont-Linien** (Rosen) werden offen anerkannt, nicht versteckt.
- **Selbst-Audit programmatisch** ausführbar — `python -m cellsim self-audit`.

## Verweise

- CellsimMixMind-JsonMind: `/run/media/julian/ML3/prompts-bartman/prompts/universal/CellsimMixMind_v1.0_20260820_cellsim.json.txt`
- CellsimMixMind Sub-Skill: `/home/julian/.claude/skills/cellsim-mixmind/SKILL.md`
- Architekturtext: `Forschung Zur Vollständigen, Numerischen Und Modul....md` §2.1, §4.2, §7
- SciMind5_ViaNegativa: `/run/media/julian/ML3/prompts-bartman/prompts/universal/SciMind5_ViaNegativa.txt`
