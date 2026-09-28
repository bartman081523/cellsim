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