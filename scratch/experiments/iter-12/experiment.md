# iter-12: Genesis-UVC-Brücke — 232 nm → EM-Schicht → RDME (VECTOR_GENESIS_UVC_BRIDGE)

## Hypothese (ergebnisoffen)

Genesis.md leitet 232 nm UVC ab (יְהִי אוֹר Σ=232, E≈5.34 eV —
"Nukleotid-Präkuror-Photochemie"-Fenster) und markiert die Gematria
selbst als "numerologische Heuristik mit hypothesen-generierender
Wirkung". Brücke: EM-Modul (Flussdichte) → iter-11-Damköhler-Fenster
(Turnover 1e-4…0.1/Molekül/Schritt) → RDME-Photoreaktion
PhotoP + γ(232nm) → PhotoN (HYPOTHESE-Proxy für Sutherland 2015).

**Vorhersage vor Simulation** (Physik, nicht Sim):

| Quelle | Fluss | Turnover/Schritt | Prognose |
|---|---|---|---|
| exogen, frühe Erde | 1e15 /cm²/s | 1.0e-3 | im Fenster → sichtbar |
| endogen (Popp 1e-5/ATP) | 4.8e9 /cm²/s (bei 100 nm) | 4.8e-9 | 5 Dekaden unterm Fenster → unsichtbar |

## Method

- Arme: `uvc_lokal_exogen` (Gauß-Photonenfeld), `thermal_uniform_exogen`
  (identisches Event-Budget, gleichverteilt), `uvc_lokal_endogen`
  (EM-Modul-Fluss), `dark_control`.
- σ=1e-17 cm², QY=0.1 (beide HYPOTHESE, dokumentiert), dt=1 s,
  600 Schritte, 16³, 2 Seeds/Arm.
- Photokinetik: lokales Tau-Leaping mit Feasibility-Cap (iter-11).

## Result

**Signal: BRIDGE_VISIBLE** (mit quantitativen Vorbehalten)

| Arm | Events | tMI | LZ-Wachstum | Licht-Kontrast |
|---|---|---|---|---|
| uvc_lokal_exogen | 588 | 0.124 | +0.876 | **+0.29** |
| thermal_uniform_exogen | 596 | 0.109 | +0.952 | 0.00 |
| uvc_lokal_endogen | **0** | 0.000 | +0.000 | 0.00 |
| dark_control | 0 | 0.000 | +0.000 | 0.00 |

**Permutationstest Licht-Gedächtnis** (H0: ortsfreie Produkte,
2000 Permutationen): beobachteter Kontrast +0.29, H0-Mittel +0.000,
H0-p99 +0.121, **p < 0.0005** (0/2000). H0 erwartet 8.2 Produkte im
Lichtbereich (1.4 % der Voxel), beobachtet ~23.

### Befunde

1. **Licht-Gedächtnis ist statistisch echt**: Die ortsaufgelöste
   232-nm-Quelle erzeugt eine messbare Orts-Korrelation zwischen
   Photonenfeld und Photoprodukt (p < 5e-4) — bei identischem
   Gesamt-Event-Budget zeigt die thermische Kontrolle exakt 0
   Kontrast. Die Brücke Genesis→EM→RDME ist simulativ
   **wirkungsvoll, aber absolut schwach**.
2. **Endogene Chemolumineszenz quantitativ widerlegt** (im Rahmen):
   Popp-Faktor 1e-5/ATP → 0 Events in 600 s auf 16³. Ultrawache
   Photonen treiben keine messbare Photochemie auf Zell-Zeitskalen —
   5 Dekaden unterm Damköhler-Fenster. Das präzisiert die iter-1-
   Aussage: Ultraweak-Photonen sind als **Signal** (Kommunikations-
   hypothese) denkbar, als **Reaktionstreiber** aber um Größen-
   ordnungen zu schwach.
3. **Diskretheits-Boden der rint-Diffusion** (Methoden-Befund):
   Die Origin_Ruliad-Phase-6-Laplace-Diffusion rundet O(1)-
   Perturbationen weg (isolierte 7 in 8er-Background: upd=7.6 → rint
   → 8; isolierte 1er → 0.4 → 0). Events feuerten korrekt, das Feld
   vernichtete sie. Fix: **stochastische Sprung-Diffusion**
   (Binomial-Sprünge pro Richtung, massenerhaltend exakt, Counts O(1)
   überleben). Gültigkeitsgrenze: rint-Diffusion nur für Counts ≳ 5
   pro Voxel (iter-11-Regime); spärliche Chemie braucht Sprünge.
4. **Metrik-Kalibrierung**: Der iter-11-MI/LZ-Schwellwert ist für
   dichte Felder kalibriert. Bei ~0.15 Teilchen/Voxel versagt er
   (MI 0.009 trotz echten Signals) — ein Permutationstest gegen H0
   'ortsfreie Events' ist die zur Spärlichkeit passende Statistik.
   (Via-Negativa: Schwellwert-Anpassung NACH Beobachtung ist
   Texas-Sharpshooter-gefährdet — deshalb Permutationstest als
   vorgezogene Signifikanz, nicht nachträglicher Schwellwert-Shift.)

## Interpretation

- **VECTOR_GENESIS_UVC_BRIDGE: geschlossen (als Hypothesen-Brücke).**
  Die 232-nm-Wahl ist numerisch mit dem EM-Modul verdrahtbar und
  simulativ sichtbar — als *präbiotische* Quelle (exogen, frühe Erde,
  Sutherland-Rahmen). Für *in-vivo*-Bewusstseins-/Steuerungs-Hypothesen
  über endogene UVC-Photonen liefert das Experiment eine
  **quantitative Negativeinschätzung** (5 Dekaden).
- Konsistent mit Via-Negativa: Genesis.md selbst fordert
  hypothesen-generierenden, nicht beweisenden Status — der Befund
  trägt das: Brücke technisch gangbar, aber die in-vivo-Variante
  scheitert an der Größenordnung.

## Strategische Vektoren

- **VECTOR_STOCHASTIC_DIFFUSION_PRODUCTION** (offen): Sprung-Diffusion
  als Alternative zur rint-Diffusion in `modules/emergence.py`
  (Tests: Massenerhalt exakt, O(1)-Counts überleben, Äquivalenz im
  dichten Regime).
- **VECTOR_SPARSE_METRICS** (offen): Permutations-Statistik für
  spärliche Felder in `modules/emergence.py` ergänzen (MI/LZ sind
  dichte-kalibriert).
- **VECTOR_ENDOGEN_UVC_TIMESCALE** (offen): Wird endogene UVC-Chemie
  bei Akkumulationszeiten ~Jahren messbar (Turnover 5e-9/s → 1
  Event/Molekül/6.6 Jahre)? → Präbiotik-Zeitskalen vs. Zellzyklus.
- **VECTOR_SATURATION_MARGIN** (offen, aus iter-11).

## Verweise

- scratch/experiments/iter-12/{uvc_bridge.py,result.json}
- Genesis.md (232 nm, explizit heuristisch); Sutherland 2015 (Nature
  Chemistry 7, 696 — UV-getriebene Nukleotid-Synthese)
- iter-11 (Damköhler-Fenster); iter-1 (EM-Schicht, Popp-Faktor)