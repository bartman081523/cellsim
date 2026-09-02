# Rekonstruktion: Orch-OR's quantenoptischer Kanal — Tegmark nicht zielführend

**Status: REKONSTRUKTION aus Vorlage-Projekten (2026-09-02). Quellen:
cellsim iter-7, MT_Sim (mt_quantum, neuro_emergent phase 1–3,
Experimentum Crucis, PGSO-Manuskript), Origin_Ruliad §4.2,
Kurian et al. 2024 (experimentell, per User als "bewiesen" eingeordnet).**

---

## 1. Der Befundstand in cellsim (iter-7) — was GENAU falsifiziert wurde

iter-7 berechnete mit einer **spezifischen Parametrisierung**:

| Größe | Wert | Annahme |
|---|---|---|
| τ_collapse (Penrose E_G) | 5.66e-37 s | **Tubulin-Dimer-Masse** (110 kDa) als Superposition, 8 nm Verschiebung |
| τ_decoherence (Tegmark) | 2.46e-10 s | **bulk water**, isotrop, 310 K |
| Ratio | 2.3e-27 | — |
| Hagan-Steelman (ordered water) | Ratio ~10⁻²⁹ | großzügige 10⁻⁸-s-Schätzung |

**Wichtig**: Diese Falsifikation gilt für genau dieses Substrat-Modell
(Massen-Superposition des ganzen Dimers in bulk-thermal Umwelt). Sie
ist korrekt GERECHNET — aber ihr Gegenstand ist eine Parameterwahl.

## 2. Die Vorlage-Projekte: die Bausteine des Weges

### (a) MT_Sim mt_quantum (ACD-Paper): Tegmark als Grenzmodell, nicht als Henker
Die mt_quantum-Implementierung (`Extra/improvements.py` +
`supplemental-2.tex`) benutzt Tegmarks thermische Dekohärenz **als
lokales Feld** Γ(r,z,t) — Dekohärenz erzeugt räumliche
"Event-Horizonte" um Kohärenz-Kerne im Mikrotubulus. Das ist die
Hagan-Pattern: Dekohärenz wird **ortsaufgelöst** (ordered water,
Debye-Screening, Zytokin-Felder), nicht global-fatal. Coherence
survives where coupling is low.

### (b) MT_Sim superradiance-Serie (Experimentum Crucis → PGSO): der
photische Kanal mit eigener Uhr

- Dicke sech²-Burst: `τ_SR = τ_sp/N`, Intensität ∝ N²·E/τ (λ=280 nm,
  τ_sp=1 ns) — **der Burst wird schneller, je größer das Netz**.
- PGSO-Manuskript-Konklusion: *"reframing the potential role of
  quantum effects in biology from a speculative possibility to a
  testable information-theoretic principle"* — die zeitliche Kohärenz
  des Bursts ist der Kausal-Faktor, nicht seine Energie.
- Ehrliche Nebennote (phase 3): als Lern-Gate zeigte Superradiance
  **keinen signifikanten Vorteil** gegenüber Gamma-Oszillation — die
  Hypothese ist nicht überall Sieger; ihr Wert liegt im Kanal, nicht
  im Lern-Gate.

### (c) Origin_Ruliad §4.2: die Behauptung mit Ankern

"UV superradiance in proteins confirms quantum effects in
bio-systems" + UPEs als Kollaps-Signaturen. Ontologie NICHT übernommen
(iter-10-Vorbehalt), aber der Anker ist derselbe.

### (d) Kurian et al. 2024: der experimentelle Beweis

UV-Superradianz aus Tryptophan-Mega-Netzwerken in biologischen
Architekturen — **gemessen** (Tryptophan-Röhrchen/Tubulin-Architekturen
bei 310 K). Der Nutzerstatus "bewiesen" wird hier angesetzt: das
photonische Phänomen existiert; strittig ist nur seine kausale Rolle.

## 3. Die Rekonstruktion des Weges (Argumentkette)

**T1 (Ziel-Verwechslung)**: Tegmarks Rechnung adressiert
Massen-Positions-Superpositionen (Δm/m) in thermischem bulk. Der
experimentell belegte Substrat-Kanal ist **elektronisch/photonisch**
(Frenkel-Exzitonen über Tryptophan-Chromophoren). Tegmarks
Dekohärenz-Kanal (thermische Streuung einer Massen-Superposition) ist
kein anwendbarer Kanal für photonen-getragene Kohärenz. → Tegmark hat
**auf diesen Kanal keinen Einfluss** — nicht, weil seine Rechnung
falsch wäre, sondern weil sie das falsche Freiheitsgrad-Modell
adressiert.

**T2 (1/N-Flucht)**: Der superradiante Zustand dekohäriert
nicht-thermisch, sondern **emissions-getrieben**: τ_SR = τ_sp/N schrumpft
mit der Netzwerk-Größe. Der Burst entkommt, BEVOR thermische Kanäle
greifen — Kooperation beschleunigt die kohärente Emission. Das ist
der qualitative Gegensatz zu Tegmarks Szenario, in dem größerer
Verband = schnellerer thermischer Zerfall.

**T3 (Ortsaufgelöste Kohärenz-Kerne)**: Hagan 2002 + mt_quantum:
Kohärenz überlebt in geschützten Kernen (ordered water,
Debye-Länge, Gel-Zustand); Dekohärenz ist Grenzfläche, nicht
Auslöschung.

**T4 (Was von iter-7 übrig bleibt, ehrlich)**: Penrose' E_G-Collapse
für Massen-Superpositionen bleibt unter der Dimer-Parametrisierung
numerisch problematisch (iter-7 gültig für diese Parametrisierung).
Die Hagan-Parametrisierung (Proton-Displacement über 10⁹⁻¹¹ Tubuline)
wurde in cellsim noch NICHT nachgerechnet → offener Test.

## 4. Evidenz-Grading der rekonstruierten Kette

| Behauptung | Status | Basis |
|---|---|---|
| Tryptophan-Netzwerke zeigen UV-Superradianz (experimentell) | **CONFIRMED (extern)** | Kurian 2024, gemessen |
| Superradianz entkommt thermischer Dekohärenz (1/N-Emission) | **CANDIDATE (B)** — theoretisch begründet, im MT_Sim-Code implementiert, noch nicht in cellsim repliziert |
| Tegmark-Masse-Dekohärenz ist kein anwendbarer Kanal auf den photonischen Substrat | **logisch valid (A)** — unterschiedliche Freiheitsgrade; kein Transfer ohne Isomorphismus |
| Orch-OR (Penrose E_G, Dimer-Parametrisierung) | **CONTRADICTION (iter-7 bleibt)** — für dieses Modell |
| Penrose E_G mit Hagan-Parametrisierung (Proton-Displacement, 10¹⁰ Tubuline) | **HYPOTHESIS** — in cellsim offen nachzurechnen |
| Superradiante endogene UVC → Damköhler-Fenster | **HYPOTHESIS mit Zahlen** — iter-16-Test (s. Plan) |

## 5. Was daraus folgt (nicht-metaphorisch)

"Orch-OR bleibt wahr und Tegmark keinen Einfluss" — in der
rekonstruierten, ehrlichen Form:

- **Der quantenoptische Kanal** (Trp-Netzwerke, superradiante UV-Bursts)
  ist experimentell belegt und durch Tegmarks Massen-Dekohärenz-Rechnung
  **nicht getroffen** — anderes Freiheitsgrad, anderer Kanal, 1/N-Emission.
- **Orch-OR's Bewusstseins-Behauptung** (E_G-Kollaps als
  Bewusstseins-Mechanismus) ist damit NICHT bewiesen — sie wird von
  der Falsifikation iter-7 nur in der Dimer-Parametrisierung getroffen;
  in der Hagan-Parametrisierung offen. Status: offen, mit zwei
  numerischen Prüfsteinen (Hagan-Rechnung; Fenster-Skalierung).

## Verweise

- cellsim iter-7 (experiment.md, orch_or.py, strategic_vectors/iter-7.md)
- MT_Sim: mt_quantum/Extra/improvements.py (Γ-Feld, Event-Horizont-Radius),
  supplemental-2.tex, run_experimentum_crucis.py (Dicke sech²),
  neuro_emergent_system_phase_2/3 (ehrliche Negative),
  final_manuscript.tex (PGSO-These)
- Origin_Ruliad §4.2 (Trp-Superradianz als Bio-Quantum-Anker)
- Kurian et al. 2024, J. Phys. Chem. B: UV-Superradianz aus
  Tryptophan-Mega-Netzwerken (experimentell)
- Tegmark 2000 (Phys. Rev. E 61, 4194); Hagan et al. 2002 (Phys. Rev. E 65, 061901)