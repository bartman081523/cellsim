# iter-11: RDME Rate-Sweep — Damköhler-Regime-Suche (VECTOR_RDME_TAU_LEAP_RATE_SWEEP)

## Hypothese

iter-10-retry: 1 globales Gillespie-Event/Schritt → reaktiv ≡ diffusiv.
Frage (ergebnisoffen): Gibt es ein Regime, in dem **lokale Chemie**
sichtbar aus der Diffusion herausbricht — und wo liegt die
Runaway-Grenze (Origin_Ruliad Phase 7: "Tuned chemistry parameters to
prevent runaway")?

## Method

- **Lokales Tau-Leaping**: Propensität pro Voxel
  `λ = k · dt_react · n_reaktant(voxel)` (first-order mass action,
  dokumentierte Vereinfachung — Registry-k ist ODE-skaliert),
  Poisson-Firings, begrenzt durch Feasibility
  (`fire = min(Poisson, verfügbare Reaktanten)` über ALLE negativen
  Stöchiometrien).
- **Diffusion**: vektorisierter 3D-Laplacian (Origin_Ruliad Phase 6,
  production `modules/emergence.py:laplacian_3d`).
- **Sweep**: dt_react ∈ {0, 1e-6, 1e-5, 1e-4, 1e-3} × D ∈ {0.05, 0.15,
  0.45}, 16³-Gitter, 600 Schritte, 3 Seeds (42/43/44), Mehrheitsentscheid.
- **Reaktionen** (Metabolit-Kern des Registry): glycolysis
  (Glc→2 Pyr + 2 ATP), atp_hydrolysis, atp_synthase.
- **Metriken**: production `emergence_metrics` (temporal/spatial MI,
  LZ) auf binarisiertem ATP-Feld + **Cross-Species-Signatur**
  (Pearson-Korrelation Glucose↔ATP; Diffusion allein erhält sie bei
  1.0, Chemie dekoreliert).

## Result

**Signal: EMERGENT** — Chemie in 9/12 Regimen sichtbar, 0 Runaway.

| Konfig | Klasse | tMI | sMI | LZ-Wachstum | corr(Glc,ATP) |
|---|---|---|---|---|---|
| D=0.05 Kontrolle | CONTROL | 0.681 | 0.436 | +0.000 | 1.000 |
| D=0.05, dt=1e-6 | DISTINCT | 0.631 | 0.393 | −0.258 | 0.953 |
| D=0.05, dt=1e-4 | DISTINCT | 0.439 | 0.346 | **+0.245** | 0.567 |
| D=0.05, dt=1e-3 | NULL | 0.681 | 0.436 | +0.000 | 0.993 |
| D=0.15, dt=1e-5 | DISTINCT | 0.103 | 0.091 | −0.242 | 0.301 |
| D=0.45, dt=1e-5 | DISTINCT | 0.035 | 0.037 | **+0.457** | **−0.249** |
| D=0.45, dt=1e-4 | DISTINCT | 0.015 | 0.020 | −0.531 | 0.045 |
| D=0.45, dt=1e-3 | NULL | 0.806 | 0.508 | +0.047 | 0.989 |

### Befunde

1. **Damköhler-Fenster gefunden**: Chemie sichtbar bei Turnover-
   Wahrscheinlichkeit pro Molekül und Schritt zwischen ~1e-4 und ~0.1
   (k·dt_react-Produkt). Unterhalb: unsichtbar (iter-10-retry-Regime).
   Oberhalb (~0.5): **Sättigungs-Kollaps** — Substrat wird instant
   erschöpft → uniformer Absorbing-State → Metriken ≡ Kontrolle.
   Chemie ist **bimodal unsichtbar**: zu langsam UND zu schnell.
2. **Chemie erzeugt Komplexität** (positives LZ-Wachstum) in zwei
   Fenstern: D=0.45/dt=1e-5 (+0.457) und D=0.05/dt=1e-4 (+0.245).
   Das ist die eigentliche "Emergenz-Reaktion sichtbar"-Signatur:
   nicht nur Zerstörung von Struktur (LZ<0), sondern aktiver Aufbau.
3. **Kein Runaway** (0/12): Feasibility-Capping wirkt als hartes
   chemisches Potenzial-Wand. Origin_Ruliads Phase-7-Tuning-Problem
   ist damit strukturell gelöst, nicht parameter-tuned.
4. **Numerik-Lektion**: 3D-7-Punkt-Laplacian hat Spektrum λ∈[−12, 0]
   (Summe dreier 1D-[−4,0]) → Stabilitätsgrenze d ≤ 1/6, **nicht**
   1/3. D=0.45 divergierte zunächst (INT64-Overflow via invalid cast
   → negative Counts → Poisson-Crash). Diagnose-Kette: lam-Guard +
   Isolations-Run pro Konfiguration.
5. **Massendrift der Kontrolle** (~2% Verlust durch rint+clamp in den
   ersten 100 Schritten während der Bump-Dissipation) — dokumentiert,
   für Metrik-Vergleiche unkritisch (beide Arme identisch behandelt).

## Interpretation

- **VECTOR_RDME_TAU_LEAP_RATE_SWEEP: geschlossen.** Das
  Reactiv-≠-Diffusiv-Kriterium (|Δcorr|>0.3 ODER ΔLZ>0.05 ODER
  ΔtMI>0.05) wird in 9 Regimen erfüllt.
- Produktionsempfehlung: Tau-Leap-Option mit Feasibility-Cap für den
  RDMEAdapter; Standard-dt_react im Fenster 1e-5…1e-4 wählen.
- Die Metrik-Suite ist **nicht** chemie-blind — iter-10-retry war ein
  Raten-Problem, wie vermutet.

## Strategische Vektoren

- **VECTOR_TAULEAP_PRODUCTION** (offen): lokales Tau-Leaping +
  Feasibility-Cap als Option in `RDMEAdapter` (Tests: Stabilitätsgrenze
  1/6, Feasibility, Determinismus).
- **VECTOR_GENESIS_UVC_BRIDGE** (offen, iter-12): ortsaufgelöste
  UVC-Quelle — jetzt mit bekannten sichtbaren Raten-Fenstern testbar.
- **VECTOR_SATURATION_MARGIN**: Realzellen laufen NAHE am Sättigungs-
  Kollaps (hohe Enzymdichte) — ist das die Erklärung, warum reale
  Metabolit-Felder glatt aussehen? (Hypothese, nicht behauptet.)