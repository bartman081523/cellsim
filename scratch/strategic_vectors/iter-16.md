# Strategic Vectors — iter-15 + iter-16 (photische Brücke + Orch-OR-Korrektur)

## iter-15 ✅: Superradianz-Produktion + N\*-Skalierungsgesetz (BRIDGE_OPEN)

- **`modules/superradiance.py`** (Produktion, 9 Tests): Dicke-sech²
  (exakt normalisiert auf N Photonen/Burst), τ_SR = τ_sp/N, Peak ∝ N²,
  PhotonicCluster, Flux/Turnover-Brücke, Φ*-Threshold.
- **N\*-Gesetz**: Fenster-Eintritt bei N·f ≳ 2e8 photons/s. syn3A
  (2e3 Trp) in KEINER Konfiguration im Fenster (iter-12 quantitativ
  begründet); neuronale Skala (1e9⁻¹⁰ Trp) in 5 Konfigs. Endogene
  UV-Photochemie ist ein **Groß-N-Phänomen**.
- Dynamischer Check: Burst-Züge → Photochemie, Licht-Gedächtnis
  p < 0.0005 (Permutationstest, Produktion).
- **Physik-Fix**: `stochastic_jump_diffusion` war upwind (nur
  +Richtung → Advektion mit Drift p·t). Korrekt: Gesamtabfluss
  Binomial(2p), 50/50-Split — Varianz exakt 2𝒟/Achse,
  Delta-Funktion breitet sich symmetrisch aus (Test `no_drift`).

## iter-16 ✅: Orch-OR revidiert (Formel-Artefakt) — OPEN_SUBSTRATE

- **iter-7's E_G-Formel dimensional invalid** (J·s/m statt J) →
  "E_G = 187 J", τ = 5.7e-37 s waren Artefakte; Kriterium zusätzlich
  invertiert. **27-Dekaden-CONTRADICTION zurückgezogen.**
- Korrekte Penrose-Rechnung: Dimer kollabiert nie (τ=3.8e11 s);
  Hagan-Parametrisierung (kollektiv korreliert, Konformationsmasse):
  **7 viable Konfigs**, alle in der generösen Ecke (f=5 %, a=8nm,
  N=1e9, S=1e6, τ_OR/τ_dec = 0.61). **0 viable ohne Shielding.**
- LIMITATIONS.md: VECTOR_ORCH_OR F → **C (OPEN)**.
- Lesart: Tegmark = Grenzbedingung für bulk water (konsistent),
  nicht universelles Verdikt; auf den photischen Kanal (iter-15)
  nicht anwendbar. Bewusstseins-Behauptung bleibt unbelegt.

## Offene Vektoren

### VECTOR_PHOTONIC_COUPLING_PRODUCTION (offen)
Burst-Train als EMSource im HybridDriver; UV-Chemie + Phasen-Sync.

### VECTOR_UV_SYNC_REOPEN (offen)
Phasensynchronisation über superradiante Burst-Züge mit
Limit-Cycle-Oszillatoren (Goldbeter 1996) — iter-2-Artefakt vermeiden;
N\*-Kriterium als Aktivierungsschwelle.

### VECTOR_WINDOW_REPLICATION_V2 (offen)
iter-14-Fenster mit dem KORRIGIERTEN beidseitigen Sprung-Operator
re-replizieren (iter-14 lief mit dem drift-behafteten Operator).

### Empirische Prüfsteine (extern)
- Burst-Raten in Trp-reichen vs. Trp-armen Zellen (Kurian-Typ).
- UV-Chemie-Nachweis in Neuronen-kulturen vs. syn3A-Skala.

## Verweise

- scratch/experiments/iter-15/, iter-16/ (experiment.md + result.json)
- scratch/theory/orchor_tegmark_rekonstruktion.md
- LIMITATIONS.md (Orch-OR-Status revidiert)