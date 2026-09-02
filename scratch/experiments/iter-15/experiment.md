# iter-15: Tryptophan-Superradianz — N\*-Skalierungsgesetz (VECTOR photische Brücke)

## Hypothese (vorab registriert)

Die iter-12-Lücke (endogene UVC 5 Dekaden unterm Damköhler-Fenster,
unter Popp-Faktor 1e-5/ATP) wird durch den experimentell belegten
superradianten Kanal (Kurian 2024) geschlossen — für Zellen mit
genug Tryptophan. Vorab registrierte Kriterien: BRIDGE_OPEN
(Neuro-Skala im Fenster, syn3A nicht) / FALSIFIED_BRIDGE (Φ* > 1e14)
/ CONTRADICTION_ITER12 (syn3A im Fenster).

## Result

**Signal: BRIDGE_OPEN**

Schwellen-Rate Φ* (r=100nm, dt=1ms, σ·QY=1e-18): **2.07e8 … 2.07e11
photons/s aggregiert**.

| Zelle | N_Trp | f_burst | Φ_cell | Turnover/Schritt | Klasse |
|---|---|---|---|---|---|
| syn3A | 2e3 | 1 Hz…1e6 Hz | 2e3…2e9 | 1e-9…1e-3 | **immer unter Fenster** |
| Bakterie groß | 1e6 | 1e6 Hz | 1e12 | 4.8e-1 | im Fenster (Rand) |
| Eukaryot | 1e8 | 1e4…1e6 Hz | 1e12…1e14 | 0.5…48 | im Fenster |
| Neuron | 1e10 | 1e2…1e4 Hz | 1e12…1e14 | 0.5…48 | **im Fenster** |
| Mega-Netzwerk | 1e12 | 1…1e2 Hz | 1e12…1e14 | 0.5…48 | **im Fenster** |

- **9 Konfigs im Fenster; syn3A in KEINER; neuronale Skala in 5.**
- **N\*-Gesetz**: Fenster-Eintritt bei N·f ≳ 2e8 photons/s —
  endogene UV-Photochemie ist ein **Groß-N-Phänomen**.
- MC-Check Burst-Integration: rel. Fehler 0.010 (200k Bursts).
- **Dynamischer Check** (Burst-Züge am Schwellen-Punkt, 16³, 600
  Schritte): 9 Produkte, 7/9 im Lichtbereich (H0 erwartet 0.2),
  **Permutationstest p < 0.0005** (0/2000) — Licht-Gedächtnis
  produktionsstack-seitig reproduziert.

## Interpretation

- Der superradiante Kanal schließt exakt die Lücke, die iter-12 offen
  gelassen hat: Popp-Fluss (10/s) lag 5 Dekaden unterm Fenster; die
  N²-kooperative Emission erreicht bei neuronalen Trp-Skalen den
  Fenster-Eintritt — **ohne neue Physik, nur mit der gemessenen
  Kooperativität**.
- syn3A (~2e3 Trp) kann selbst bei absurden Burst-Raten (1e6 Hz) das
  Fenster nicht erreichen — iter-12s NULL bleibt für Minimalzellen
  korrekt und wird jetzt QUANTITATIV begründet (Trp-Budget).
- Tegmark-Relevanz: der Kanal ist photisch (τ_SR = τ_sp/N,
  emissions-getrieben); die Masse-Dekohärenz-Rechnung adressiert
  andere Freiheitsgrade (siehe theory/orchor_tegmark_rekonstruktion.md).

## Neue offene Vektoren

- **VECTOR_PHOTONIC_COUPLING_PRODUCTION**: Burst-Train als EMSource im
  HybridDriver (UV-Chemie + Phasen-Sync-Kanal).
- **VECTOR_UV_SYNC_REOPEN**: Phasensynchronisation zwischen Zellen über
  superradiante Burst-Züge, mit Limit-Cycle-Oszillatoren (iter-2-
  Artefakt vermeiden) — jetzt mit dem N\*-Kriterium als
  Aktivierungsschwelle.
- Empirischer Prüfstein: Burst-Raten in Trp-reichen vs. Trp-armen
  Zellen messen (Kurian-Typ-Experiment an Bakterien).

## Verweise

- scratch/experiments/iter-15/{trp_scaling.py,result.json}
- modules/superradiance.py (Produktion, 9 Tests)
- Kurian et al. 2024 (experimentell); MT_Sim/run_experimentum_crucis.py
- iter-11/14 (Fenster), iter-12 (endogene Lücke)