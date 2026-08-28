# Strategic Vectors — iter-11 (Rate-Sweep / Damköhler)

## Ergebnis: VECTOR_RDME_TAU_LEAP_RATE_SWEEP ✅ geschlossen (EMERGENT)

Lokales Tau-Leaping (per-Voxel-Propensität λ = k·dt_react·n,
Poisson-Firings, Feasibility-Cap) + vektorisierte 3D-Laplace-Diffusion.
Sweep dt_react × D auf 16³, 600 Schritte, 3 Seeds.

### Das Damköhler-Fenster (Zentralbefund)

Chemie ist in den Emergenz-Metriken **bimodal unsichtbar**:

```
unsichtbar          SICHTBAR (Damköhler-Fenster)        unsichtbar
◄────────────────┬────────────────────────────────┬──────────────►
zu langsam       ~1e-4 … ~0.1 Turnover/Molekül/     zu schnell
(iter-10-retry)  Schritt: corr(Glc,ATP) 1.0→0.0,    (Sättigungs-
                 LZ teils POSITIV (+0.46)           Kollaps)
```

- Zu langsam: Feld quasi-statisch (iter-10-retry: reaktiv ≡ diffusiv)
- Zu schnell (dt=1e-3): Substrat instant erschöpft → uniformer
  Absorbing-State → Metriken ≡ Kontrolle (Sättigungs-Kollaps)
- Im Fenster: Chemie dekoreliert Glucose↔ATP (corr 1.0 → −0.25),
  kollabiert temporale MI (0.81 → 0.015) und erzeugt an zwei Stellen
  **positives LZ-Wachstum** — aktiver Komplexitätsaufbau

### Runaway strukturell gelöst

Origin_Ruliad Phase 7: "FIX: Tuned chemistry parameters to prevent
runaway". Antwort (iter-11): Feasibility-Capping
`fire = min(Poisson(λ), verfügbare Reaktanten)` — 0/12 Konfigs
 runaway. Das ist ein hanges chemisches Potenzial-Wand, kein Tuning.

### Numerik-Lektion (wiederverwendbar)

3D-7-Punkt-Laplacian: Spektrum λ ∈ [−12, 0] → explizite Stabilität
**d ≤ 1/6** (nicht 1/3). D=0.45 divergierte zunächst → INT64-Overflow
via invalid-cast → negative Counts → Poisson-Crash. Substepping mit
d_sub ≤ 0.15 löst es. Diagnose: lam-Guard + Config-Isolation.

## Vektoren

### VECTOR_TAULEAP_PRODUCTION (offen)
Lokales Tau-Leaping + Feasibility-Cap als Option in `RDMEAdapter`.
Tests: Stabilitätsgrenze 1/6, Feasibility-Einhaltung, Determinismus,
Fenster-Reproduktion (D=0.15, dt=1e-5 → corr < 0.4).

### VECTOR_GENESIS_UVC_BRIDGE (offen → iter-12)
Genesis.md 232 nm UVC → EM-Schicht → ortsaufgelöste Photoreaktion.
Jetzt mit bekanntem sichtbaren Raten-Fenster (Turnover 1e-4…0.1/Schritt)
kalibrierbar. Hypothesen-Generator (Via-Negativa: Apophenie als
Hypothese OK, als Beweis nicht).

### VECTOR_SATURATION_MARGIN (offen, transkategorial)
Realzellen betreiben hohe Enzymdichte → nahe am Sättigungs-Kollaps?
Hypothese: reale Metabolit-Felder sind glatt, weil der Damköhler-
Kollaps sie glättet. Testbar:registry-K k-Faktor-Sweep Richtung Sättigung.

## Verweise

- scratch/experiments/iter-11/{rate_sweep.py,result.json,experiment.md}
- Origin_Ruliad Phase 6/7 (Laplacian-Schema, Runaway-Problem)
- Damköhler 1936; Turing 1952 (Reaktions-Diffusions-Muster als
  Klassiker des Fensters)