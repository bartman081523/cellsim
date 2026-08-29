# Strategic Vectors — iter-13 (Produktions-Sprint, gemäß CellsimMixMind-Audit)

## Drei Vektoren produktionell geschlossen

### VECTOR_TAULEAP_PRODUCTION ✅
`RDMEAdapter(use_tau_leap=True)` — lokales Tau-Leaping als Option im
Basis-Adapter (nicht rdme_optimized: orthogonal zum JIT-Pfad).

- Propensität pro Voxel `λ = k · dt · n_reaktant(voxel)`, Poisson,
  Feasibility-Cap über ALLE negativen Stöchiometrien → hartes
  Potenzial-Wand (0/12 Runaway in iter-11)
- Damköhler-Fenster dokumentiert: Turnover k·dt ∈ [1e-4, 0.1] für
  Sichtbarkeit (iter-11); Sättigung oberhalb
- `state.tau_leap_events` Zähler + Snapshot/Restore-Roundtrip
- Tests (7): Feasibility ≥ 0, Determinismus, Sättigungs-Kollaps,
  Fenster-Umsatz vs. dt=0-Kontrolle, Null-Stöchiometrie-no-op,
  Default-Mode unverändert, Snapshot-Roundtrip

**Steelman-Begegnung im Test**: Sättigungs-Collapse ist NICHT
"Substrat → 0" — die Hauswirtschafts-ATPasen (Gyrase k=20, FtsZ k=10,
GroEL, …) akkumulieren ATP-Schuld, Pi wird von der Synthase
(k·dt=88·n) sofort re-eingesammelt. Die Registry ist ein Netzwerk,
kein Einzelkanal.

### VECTOR_STOCHASTIC_DIFFUSION_PRODUCTION ✅
`modules/emergence.py:stochastic_jump_diffusion()` — Binomial-Sprünge
pro Richtung (p = D/6), massenerhaltend exakt, Counts O(1) überleben.
`laplacian_3d` (rint) bleibt für dichte Felder (Counts ≳ 10) —
Gültigkeitsgrenze docstring-dokumentiert.
Tests (4): exakter Massenerhalt, Delta-Funktion überlebt 50 Schritte,
Determinismus, dichtes Feld ohne Mittelwerts-Drift.

### VECTOR_SPARSE_METRICS ✅
`modules/emergence.py:permutation_contrast_test(...)` — pure-index
H0-Statistik (ortsfreie Events, Vektorisiert über 2000 Permutationen),
p-Wert + H0-Quantile. Ersetzt dichte-kalibrierte MI/LZ-Schwellwerte
für spärliche Felder (iter-12: MI 0.009 trotz p<5e-4).
Tests (5): Uniformität → p hoch, Lokalisierung → p klein,
Determinismus, Zero-Events, Input-Validierung.

## Status

- **184 Tests grün** (168 + 16 neu), `ruff check src/` clean
- Evidenz-Fortschritt iter-11/12-Befunde: CANDIDATE → CANDIDATE+
  (Produktionalisiert + invariant-getestet; Fenster-Reproduktion auf
  anderem Gitter/Seed-Raum steht noch aus = Falsifikator)

## Offene Vektoren

- **VECTOR_WINDOW_REPLICATION** (Falsifikator für das Damköhler-
  Fenster): Fenster auf 24³ und neuem Seed-Raum reproduzieren — wenn
  nicht, war es ein Gitter-Artefakt (Steelman aus dem Audit)
- **VECTOR_ENDOGEN_UVC_TIMESCALE** (offen): 1 Event/Molekül/~6.6 Jahre
  — präbiotisch vs. in-vivo trennen
- **VECTOR_SATURATION_MARGIN** (offen): Registry-k-Sweep Richtung
  Sättigung mit dem jetzt produktionellen Tau-Leap