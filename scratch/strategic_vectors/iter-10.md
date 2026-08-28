# Strategic Vectors — iter-10 + iter-10-retry (Origin_Ruliad-Brücke)

## Quelle laut User: `/run/media/julian/ML2/Python/Origin_Ruliad/`

Konsultiert:
- **Ruliad-Paper** (Emergence of Physical Law / Now-Time): Kausalgraphen,
  Gravitation als Kantengewichts-Krümmung, UPEs als Kollaps-Signaturen
- **Emergence_Phase_6/7**: vektorisierte Laplace-Diffusion + Chemie auf
  2D-Feldern mit MI/LZ-Emergenz-Metriken
- **Genesis.md**: Gematria → Bioenergetik-Mapping (232 nm UVC →
  Sutherland 2015 UV-Präbiotik; pmf-Formel; 273 K Wasser-Referenz)
- **MT_Sim** (Info): LZ/MI-Konventionen bestätigt
- **upe_ruliad** (Info): UPE-These-Papers

## Ergebnisse

### iter-10 (SSA-only): NULL → Setup-Artefakt
Uniforme IC → MI trivial 0. Diagnose: keine räumliche Heterogenität.

### iter-10-retry (lokalisierter Seed + Tau-Leap-Hybrid): CONTRADICTION
| Metrik | reaktiv | diffusiv |
|---|---|---|
| Temporal MI | 0.739 | 0.809 |
| Spatial MI | 0.474 | 0.508 |
| LZ growth | −0.003 | +0.067 |

**Befund 1 (POSITIV)**: Origin_Ruliads Emergenz-Metriken (MI, LZ,
Binarize, Laplacian) übertragen sauber auf 3D-RDME-Felder — echte
Struktur wird gemessen (MI 0.74, spatial 0.47).

**Befund 2 (offen)**: Diffusion erzeugt mehr LZ-Wachstum als Reaktionen
— die 1-Event/Schritt-Reaktionsrate ist zu schwach. Das ist eine
**Rate-Skalierungs-Frage** (iter-10c), keine Widerlegung.

## Strategische Vektoren

### VECTOR_RULIAD_METRICS_PRODUCTION ✅
→ `src/cellsim/modules/emergence.py`: binarize, MI, LZ, laplacian_3d,
emergence_metrics(). 8 Tests. Quelle attribuiert (Origin_Ruliad Phase 6).

### VECTOR_RDME_TAU_LEAP_RATE_SWEEP (offen)
→ Reaktions-Events/Schritt gegen Diffusions-Koeffizient skalieren bis
reaktiv ≠ diffusiv (MI-Differenz > 0.05). Origin_Ruliad Phase 7 hatte
dasselbe Problem ("FIX: Tuned chemistry parameters to prevent runaway").

### VECTOR_GENESIS_UVC_BRIDGE (transkategorial, offen)
→ Genesis.md: "יְהִי אוֹר Σ=232 → 232 nm UVC" + Sutherland 2015
(UV-getriebene RNA-Präbiotik). Bridge zur EM-Schicht: UV-Emission bei
232 nm als Quelle für Präbiotik-Reaktionen. **Hypothesen-Generator**
(Via-Negativa: Apophenie als Hypothese OK, als Beweis nicht).

### VECTOR_ORCH_OR_KONTRAST
Origin_Ruliad §4.3 stützt Bewusstsein auf Orch-OR/Fröhlich — beide in
cellsim falsifiziert (iter-7, REFUTED_BY_REIMERS_2010). Der
Ruliad-Beitrag zu cellsim ist daher **methodisch** (Emergenz-Metriken,
Laplacian, Kausalgraphen), **nicht** die Bewusstseins-Ontologie.

## Verweise

- Origin_Ruliad: Ruliad-Paper + Emergence_Phase_1-12 (primäre Quelle)
- Wolfram (2020, 2021), Bókkon 2010 (UPE), Fröhlich 1968
- Genesis.md → Sutherland 2015, Lane & Martin 2010, Wächtershäuser 1988