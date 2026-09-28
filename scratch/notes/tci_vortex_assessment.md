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