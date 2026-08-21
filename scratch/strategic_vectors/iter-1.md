# Strategic Vectors — iter-1 (EM-Schicht)

## Signal: STRONG

**Quantitative Ergebnisse** (JCVI-syn3A bei 310 K):

| Größe | Wert |
|---|---|
| Schwarzkörper @ 250 nm | 2.9e-73 W/m²/nm (≈ null) |
| Schwarzkörper @ 400 nm | 4.7e-44 W/m²/nm (≈ null) |
| Chemolumineszenz | 10 Photonen/s pro Zelle |
| Fluss @ 1 µm | **8.0e7 Photonen/cm²/s** |
| Fluss @ 10 µm | 8.0e5 Photonen/cm²/s |

## Einordnung

- **Schwarzkörper ist irrelevant** im UV bei Körpertemperatur (Wien'sches
  Verschiebungsgesetz: Maximum bei ~10 µm).
- **Chemolumineszenz dominiert**: 10 Photonen/s/Zelle ist im Popp-Bereich
  (10–100 Photonen/s/cm² für ruhende Zellen).
- **Flussdichte von 8·10⁷ Photonen/cm²/s bei 1 µm** ist hoch genug,
  dass Nachbarzellen dieses Signal detektieren können.

## Strategische Vektoren

### VECTOR_EM_LAYER_PRODUCTION
EM-Schicht als Produktions-Code in `src/cellsim/modules/em.py` integrieren:
- Maxwell-Gleichungen statisch + Dipol-Quelle
- Chemolumineszenz-Modell mit ATP-getriebener Rate
- Output-Telemetrie: `em_uv_flux_density`

### VECTOR_UV_SYNCHRONIZATION_NEXT
→ **iter-2**: Kopplung zwischen 2 Zellen über UV-Photonen.
- Hypothese: ATP-Synthese-Raten können sich über Biophotonen-Austausch
  phasen-synchronisieren (Cifra-Sonn 2011).
- Vorhersage: Bei 2 Zellen in <10 µm Abstand ATP-Synthese-Oszillationen
  im 0.1-1 Hz Bereich mit Korrelationskoeffizient r > 0.5.

### VECTOR_ATP_DRIVEN_PHOTONICS
- ATP-Hydrolyse-Rate pro Zelle: ~10⁶/s → 10 Photonen/s
- Erhöhung der metabolischen Rate → höhere UV-Emission
- **Prüfbare Vorhersage**: Fastende Zellen emittieren weniger UV.

### VECTOR_RADICAL_PAIR_COUPLING
→ **iter-3**: Radikal-Paar-Mechanismus (Schulten) für Magnetorezeption.
- Cryptochrom-Flavoproteine als UV-/Blaulicht-Sensoren
- Spin-Chemie-Kopplung: könnte Zell-Zell-Synchronisation verstärken

## Verweise

- Popp, F.A. (1988): Biophotonen-Emission, ein nicht-thermischer
  Indikator für Lebensprozesse
- Cifra, M., Sonn, K.V. (2011): Electromagnetic cellular interactions
- Popp, F.A. & Beloussov, L.V. (2003): Integrative Biophysics

## CellsimMixMind-Audit

- Hypothesis: STRONG (quantitativ belegt mit Popp-Werten)
- Steelman: Schwarzkörper-Hypothese (klassisch) widerlegt durch Zahlen
- Method: konservativ (kein Skalierungs-Parameter)
- Nächste Iteration: iter-2 (UV-Synchronisation) als logische Folge
