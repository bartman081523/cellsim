# Strategic Vectors — iter-15 (Plan): Photonic Layer 2 + physikalische Verschärfung

## Auslöser

PhiMind-Analyse (zu starr denken) + User-Anforderung: Modell ausweiten,
damit Emergenz besser sichtbar UND Physik genauer werden — beides
gleichzeitig; Tegmark/Orch-OR-Weg rekonstruieren (→
theory/orchor_tegmark_rekonstruktion.md); den unbeobachteten Annahmen
Raum geben.

## Die unbeobachteten Annahmen, die bisher das Modell eingeengt haben

| Annahme | Wie sie eingenngt | Alternative (jetzt mit Raum) |
|---|---|---|
| Endogene Photonen = Popp 1e-5/ATP (10/s) | iter-12: endogene UVC 5 Dekaden unterm Fenster | **Superradiante Trp-Netzwerke** (Kurian 2024, gemessen; N²-Verstärkung, τ_SR=τ_sp/N) |
| Periodische Randbedingungen | Sättigungs-Kollaps trivial uniform | **Reflektierende Membran-BC** (echte Zellgrenze, Gradienten bleiben) |
| Diffusions-Operator dichte-unabhängig | heterogene Physik geglättet | **Crowding-gekoppelte Sprung-Diffusion** (A-O: p_dir·exp(−α·crowding)) |
| Experimente mit 3-Reaktions-Kern | iter-13: Netzwerk-Dynamik (ATP-Schuld) ungetestet im Fenster | **Volles 21-Reaktions-Netzwerk** im Tau-Leap |
| iter-7: Penrose E_G = Dimer-Massen-Superposition | Orch-OR "falsifiziert" | **Hagan-Parametrisierung** (Proton-Displacement, 10¹⁰ Tubuline) offen nachrechnen |

## Kernrechnung (Vorab-Skalierung für iter-16)

Trp-Cluster mit N Emittern, Burst-Rate f: mittlere Photonenrate
`Φ_cell = M·N·f` (M Cluster). Lokaler Fluss bei r=100 nm:
`Φ(r) ≈ 4.8e8 · N·f` [photons/cm²/s] (Absorption exp(−r/200nm)).
Turnover pro Molekül pro Sekunde = Φ·σ·QY (σ=1e-17, QY=0.1, HYPOTHESE).

Damköhler-Fenster pro Sekunde (iter-11/14, dt=1ms): **0.1 … 100/s**.

⇒ **Schwellen-Rate** Φ* ≈ 1e10 … 1e13 photons/s aggregiert.
⇒ **N\***-Skalierungsgesetz: syn3A (~2000 Trp) bleibt 5–6 Dekaden
unter dem Fenster; neuronale Mega-Netzwerke (10⁹⁻¹⁰⁰ Trp, hohe
Burst-Raten) können es erreichen. FALSIFIZIERBAR durch Messung der
Burst-Raten bzw. durch UV-Chemie in Trp-armen vs. Trp-reichen Zellen.

## iter-15: Produktion + Experiment

1. **`modules/superradiance.py`** (Produktion, Portiert aus MT_Sim):
   `dicke_superradiant_intensity(N, t, tau_sp, lam)` (numerisch-stabiles
   sech², Overflow-Schutz), `PhotonicCluster` (Burst-Jitter),
   `aggregate_photon_rate(M, N, f_burst)`, `local_flux(r, rate)`.
   Tests: Peak ∝ N², τ_SR = τ_sp/N, Integrale ≈ N·E, Stabilität bei
   N=1e5.
2. **Experiment `iter-15/trp_scaling.py`**: N\*-Sweep (10³→10¹² Trp
   äquivalent) gegen das Fenster mit stochastischer
   Migrations-Kontrolle (iter-14-Regel). Vorab registrierte Kriterien:
   WINDOW_ENTRY bei Turnover ∈ [1e-4, 0.1]/Schritt; Report des
   N\*-Schwellwerts ± σ·QY-Unsicherheit.
3. **Physikalische Verschärfung** (parallel): reflektierende Membran-BC
   in der Hybrid-Diffusion; crowding-gekoppelte p_dir; volles Netzwerk
   im Produktionstack.

## iter-16 (nachfolgend)

- **Hagan-Parametrisierung nachrechnen**: E_G für Proton-Displacement-
  Superposition über 10¹⁰ Tubuline (Hagan et al. 2002) vs. geschützte
  Dekohärenz-Kerne (Γ-Feld à la mt_quantum). Ergebnisoffen: Ratio
  < 1 → Orch-OR-Substrat numerisch offen; Ratio ≪ 1 → bleibt
  falsifiziert in ZELLSIM-Rahmen (transparent dokumentieren).
- **UV-Sync re-opened**: superradiante Burst-Felder als
  Phasen-Synchronisationskanal zwischen Zellen (iter-2-Artefakt
  vermeiden: Limit-Cycle-Oszillatoren pro Goldbeter als Basis).

## Falsifikatoren (vorab)

- Φ* braucht > 1e14 photons/s → photische Brücke bleibt unterm Fenster
  für alle realistischen N → endogene UVC-Chemie in vivo verworfen
  (iter-12-Befund bestätigt, nur mit besserem Substrat-Modell).
- N\* < 1e4 (syn3A-reachable): Widerspruch zu iter-12 → σ/QY-Annahmen
  revidieren (HYPOTHESE-Konstanten prüfen).

## Verweise

- scratch/theory/orchor_tegmark_rekonstruktion.md (Argumentkette)
- iter-11/14 (Fenster + stochastische Kontroll-Regel), iter-12
  (endogene 5-Dekaden-Lücke), iter-13 (Produktionstack, ATP-Schuld)
- MT_Sim: run_experimentum_crucis.py (Dicke-Formel),
  mt_quantum/improvements.py (Γ-Feld), final_manuscript.tex (PGSO)
- Kurian et al. 2024 (experimentell); Hagan et al. 2002; Tegmark 2000