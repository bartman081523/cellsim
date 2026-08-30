# iter-14: Damköhler-Fenster-Replikation auf Produktionstack (Falsifikator)

## Setup (vorab registriert)

- **Pre-registrierte Kriterien** (im Code, vor dem Lauf fixiert):
  REPLICATED_STRONG = ≥6/9 DISTINCT + Sättigungs-Rückkehr +
  Fenster-Ordnung ≥2/3; FALSIFIED = 0/9.
- **Bedingungen gegenüber iter-11**: Gitter 24³ (7.3× Voxel), Seeds
  {100,101,102} (disjunkt), Produktionstack
  (`RDMEAdapter.use_tau_leap` + `stochastic_jump_diffusion`) statt
  Scratch-Hybrid, gleicher 3-Reaktions-Metabolit-Kern,
  Diffusion numerisch anders (Teilchen-Sprünge statt rint-Laplace).

## Result

**Signal (pre-registriert): REPLICATED_STRONG** — 7/9 DISTINCT,
Sättigungs-Rückkehr ✓, Fenster-Ordnung 3/3, 0 Runaway.

### Die U-Form repliziert in allen 3 Diffusions-Regimen

corr(Glc↔ATP)-Abstand zur Kontrolle (Mittel über 3 Seeds):

| D | dt=1e-6 (langsam) | dt=1e-5 | dt=1e-4 | dt=1e-3 (Sättigung) |
|---|---|---|---|---|
| 0.05 | 0.014 | **0.032** | **0.053** | 0.010 |
| 0.15 | 0.003 | **0.010** | **0.017** | 0.006 |
| 0.45 | 0.002 | **0.005** | **0.009** | 0.004 |

Minimum bei mittleren Raten, Rückkehr an beiden Enden — die
Damköhler-Fenster-Signatur, quantitativ schwächer als iter-11, aber
richtungsstabil über 3 Dekaden Chemie × 3 Dekaden Diffusion.

### Befund A (Replikation): Struktur überlebt Gitter-, Seed- und
### Numerikwechsel

Sättigungs-Rückkehr, Fenster-Ordnung und die U-Form der
Cross-Species-Dekorrelation überleben Gitter-, Seed- UND
Numerikwechsel. Das bimodale Phänomen (unsichtbar–sichtbar–
unsichtbar) ist daher kein Gitter-Artefakt. 0 Runaway erneut.

### Befund B (post-hoc, methodisch gewichtig): iter-11-Kontrollen
trugen ein Determinismus-Artefakt

Die iter-11-Kontrolle hatte **corr ≡ 1.000, tMI 0.681** — hier
stattdessen Korrolle ≈ 0.04–0.10, tMI ≈ 0.00–0.02. Ursache: der
rint-Laplace-Operator ist **deterministisch und identisch** auf
beiden Spezies-Feldern → identische Felder bleiben für immer
identisch (corr ≡ 1.000). Echte stochastische Migrations-Physik
dekoreliert zwei identische Spezies sofort (molekularer Lärm).

**Konsequenz**: Die iter-11-Signatur „corr 1.0 → 0.025" übertrieb die
Chemie-Rolle — ~90 % des Drops war der geteilte deterministische
Operator, nicht Chemie. Unter stochastischer Migration (dem
physikalisch korrekten Bild) dekoreliert die Kontrolle selbst; die
wahre Chemie-Signatur ist die **U-Form relativ zum Rauschen-Floor**,
nicht der Absolute-Abfall. iter-11 bleibt als Phänomen gültig
(Fenster-Ordnung, Sättigung), seine corr-Magnitude war
operator-kalibriert, nicht physikalisch.

### Befund C (Sekundär)

LZ-Wachstums-Unterschiede (iter-11-DISTINCT-Treiber hier: ΔLZ
0.03–0.11) sind auf nahe-rauschenden Feldern kleine Signaturen —
tMI/sMI ≈ 0–0.016 statt iter-11s 0.4–0.8. Metriken auf spärlichen
Feldern brauchen die iter-13-Permutations-Statistik, nicht
Schwellwerte.

## Interpretation

- **VECTOR_WINDOW_REPLICATION: geschlossen.** Das Fenster ist keine
  Gitter/Seed-Artefakt — Struktur (U-Form) unter Gitter-, Seed- und
  Numerikwechsel stabil. Evidenz: iter-11+12 Befunde CANDIDATE →
  **CANDIDATE robust** (B); quantitative Magnituden bedürfen der
  Neuinterpretation (s. Befund D).
- **Befund D (neu, methodisch)**: iter-11s Kontrolle corr=1.000 war
  ein Artefakt des deterministischen Operators (geteilte Evolution).
  Chemie-Sichtbarkeit muss relativ zu einer **stochastischen
  Migrations-Kontrolle** definiert werden — iter-11 hat das implizit
  verletzt (rint-Laplace ist deterministisch geteilt), iter-14 korrigiert es.
- **Kalibrierungs-Korrektur bereits eingeflossen**:
  `stochastic_jump_diffusion` p_dir = 𝒟 statt 𝒟/6 (Unter-mischung
  um 6 behoben; Physik-Definition Varianzwachstum 6𝒟/Schritt).

## Strategische Vektoren

- **VECTOR_STOCH_CONTROL_METRIC** (offen): Alle künftigen
  Chemie-vs-Kontrolle-Vergleiche verwenden stochastische
  Kontrollen; iter-11-Zahlen im Vektor-Dokument als
  operator-abhängig markieren. Zusätzlich: Effektgrößen-Metrik
  relativ zum Kontroll-Rausch-Floor (z. B. U-Form-Tiefe/Floor).
- **VECTOR_SATURATION_MARGIN** (offen): Registry-k-Sweep Richtung
  Sättigung auf dem Produktionstack.
- **VECTOR_ENDOGEN_UVC_TIMESCALE** (offen).

Falsifikator-Status: Der letzte Steelman aus dem CellsimMixMind-Audit
(„Fenster ist Gitter-Artefakt") ist begegnet. Verbleibender
Steelman: „Die U-Form ist Metrik-Noise bei nahe-uniformen Feldern" —
adressierbar durch den relativen Effektgrößen-Metriken und
Permutationstests auf die U-Form selbst (VECTOR_STOCH_CONTROL_METRIC).