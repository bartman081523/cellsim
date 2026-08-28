# iter-10-retry: Ruliad-Emergenz mit vektorisierter Diffusion (Tau-Leap)

## Hypothese

iter-10 zeigte: Gillespie-SSA (1 Event/Schritt) lässt das 6³-Feld
quasi statisch (reaktiv ≡ diffusiv). Origin_Ruliad nutzt vektorisierte
Laplace-Diffusion. Mit portiertem 3D-Laplacian + lokalisiertem Seed
sollten reaktiv und diffusiv unterscheidbar sein.

## Method

1. **Hybrid-RDME** (Tau-Leap-Standard):
   - Vektorisierte 3D-Laplace-Diffusion (np.roll, 16³ Gitter) auf allen
     22 Spezies pro Schritt (portiert aus Origin_Ruliad Phase 6)
   - 1 Gillespie-Reaktions-Event pro Schritt (cellsim Registry)
   - Gauß-Fleck-IC für Glucose + ATP (Origin_Ruliad lokale Quellen)
2. Metriken: temporal MI, spatial MI, LZ-Komplexität (Origin_Ruliad)
3. Vergleich: reaktiv (Registry) vs. diffusiv (k=0 Kontrolle)

## Result

**Signal: CONTRADICTION (mit Substanz)**

| Metrik | reaktiv | diffusiv |
|---|---|---|
| Temporal MI (mean) | 0.7387 | 0.8090 |
| Spatial MI (mean) | 0.4738 | 0.5080 |
| LZ growth | -0.0029 | +0.0674 |

**Befunde**:
1. **Emergenz-Metriken funktionieren**: MI (0.74/0.81) und LZ (~0.74)
   messen echte Feld-Struktur auf 16³ — Origin_Ruliads Methodik
   überträgt auf 3D. ✓
2. **Aber**: Diffusion erzeugt MEHR Komplexität (LZ +0.067) als
   Reaktionen. Reaktionen wirken sogar komplexitäts-REDUZIEREND
   (LZ −0.003). Die 1-Reaktion-pro-Schritt-Rate ist zu schwach gegen
   die Diffusion.

## Interpretation

- **Positiv**: Das Ruliad-Emergenz-Messwerkzeug ist produktionsreif
  und in cellsim integriert (`modules/emergence.py`).
- **Offen**: Reaktions-/Diffusions-Raten-Verhältnis muss skaliert
  werden, damit Reaktionen sichtbar in die Emergenz-Metriken eingehen.
  Das ist ein Rate-Sweep (iter-10c), kein Widerlegungs-Befund gegen
  das Ruliad-Framework.

## Strategische Vektoren

- **VECTOR_RIAD_METRICS_PRODUCTION** ✅: `modules/emergence.py` mit
  8 Tests. Werkzeug für alle künftigen Felder (RDME, EM, Chromosom).
- **VECTOR_RATE_SWEEP** (offen): Verhältnis Reaktions-Events zu
  Diffusions-Schritten variieren, bis reaktiv ≠ diffusiv.
- **VECTOR_GENESIS_UVC_BRIDGE**: Genesis.md leitet UVC 232 nm für
  UV-getriebene Präbiotik ab (Sutherland 2015) — verbindet an die
  EM-Schicht (iter-1). Offener Vektor.