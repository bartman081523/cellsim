# iter-17: VECTOR_PATTERN_FORMATION — Turing-Muster im RDME-Substrat

## Vorab registrierte Kriterien (fixiert vor dem Lauf, 2026-09-21)

Substrat: Schnakenberg-artiger Aktivator-Inhibitor-Kern auf dem
RDME/Gillespie-Stack (Gitter 24³, dt=0.05, Feed/Remove, R3 = 2X+Y→3X
autokatalytisch). Deterministischer Fixpunkt X*=400, Y*=520;
homogener Zustand stabil (traceJ = −0.203 < 0, detJ = 0.5 > 0).

Vorhersagen (Dispersions-Analyse, exaktes Gitter-Symbol 2(1−cos k),
am gemessenen Arbeitspunkt u=0.9997, v=1.2972, Jacobian
f_u=0.297, f_v=0.500, g_u=−1.297, g_v=−0.500):

- **Onset**: Turing-Instabilität für D_v > ≈ 1.556 (D_u fix 0.06)
- **D_v=0.25, 1.0**: stabil — kein Muster (peak_excess < 5)
- **D_v=3.0**: Bande k ∈ [0.850, 3.142], k* = 1.422, σ* = 0.0808/t
- **D_v=10.0**: Bande k ∈ [0.426, 3.142], k* = 1.029, σ* = 0.1762/t
- Muster-Kriterium: peak_excess ≥ 5 UND Dominanz der Banden-Modi
  (band_ratio ≥ 0.2), konsistent über 3 Seeds
- Negativkontrollen: matched-Null (D-Ratio=1), diffusion-only,
  mean-field (dev < 1e-12)

## Result (wie vorab ausgewertet)

| Konfig | peak_excess | k_peak | band_ratio | Verdict |
|---|---|---|---|---|
| D_v=0.25 | 5.51 | 0.453 | 0.523 | STABLE_AS_PREDICTED |
| D_v=1.0 | 24.22 | 0.411 | 0.537 | STABLE_AS_PREDICTED |
| D_v=3.0 | 23349.71 | **0.262** | 0.010 | **FALSIFIED_NO_PATTERN** |
| D_v=10.0 | 769365.99 | **0.262** | 0.178 | **FALSIFIED_NO_PATTERN** |

Nulls: matched-Null peak_excess=5.64 → ARTIFACT_PATTERN-Flag
(Metrik gesättigt durch rotes demographisches Rauschen — die
Schwelle 5 trennt nicht sauber, dokumentiert als Metrik-Defekt);
diffusion-only 2.34; mean-field dev ~1e-16 ✓.

Die vorab registrierten Verdicts stehen — **die vorab registrierte
Banden-Vorhersage ist FALSIFIZIERT**: bei D_v=3/10 entsteht massives
Muster, aber bei k_peak=0.262 (λ=24 = Box-Grundmode), nicht in der
vorhergesagten Bande.

## Diagnose-Kette (nach dem Lauf)

**1. Box-Mode-Diagnostik** (D_v=3, seed 300, 800 Schritte, Snapshots
alle 25; echte simulate()-Kette, nicht die isolierte Diffusions-Routine
— ein erster Diagnostik-Lauf mit `stochastic_jump_diffusion` auf einer
`astype`-Kopie diffundierte nicht und zeigte nur Chemie-Rauschen,
std=57 = exakt 0.142·400; verworfen):

- k_peak lockt auf 0.262 ab Schritt ~125 und bleibt dort
- peak_excess wächst exponentiell: 6 → 39 → 132 → 293 → 625 → 1415 →
  3434 → 9209 (Schritt 25→725)
- stdX: 21.65 → 58.51 (wachsend), stdY: 22.7 → 25.5 (fast flach)
- Endfeld: X min=243, max=1184, std=111.3; Y std=31.8 (Ratio 0.29)
- Autokorrelation X: lag1=0.942, lag6=0.397, lag12=−0.039 →
  kohärente Struktur mit λ ≈ 24 Voxeln (Nullstelle bei λ/2)
- Spektrum: Top-Moden 0.262 / 0.370 / 0.453 (n=1-Schale), dann erst
  0.524/0.585 — LOW-k dominiert, NICHT k*=1.42

**2. Einheiten-Bug gefunden (CORREKTUR-LOG)**: Die vorab registrierte
Disperson behandelte D_u/D_v als kontinuierliche Raten pro
Zeiteinheit. Das Sprung-Diffusions-Schema liefert sie aber **pro
Schritt** (n_sub·p_sub = D; Varianzzuwachs 2D pro Schritt pro Achse).
Korrekt: D_eff = D/DT = Faktor 20 bei DT=0.05.

- **Onset unverändert**: analytisch dt-invariant, denn die
  Instabilitätsbedingung (f_u·D_v + g_v·D_u)² > 2·D_u·D_v·detJ kürzt
  dt exakt heraus. Korrigierte Rechnung: D_v = 1.556 pro Schritt —
  identisch zur Lauf-Vorhersage. ✓
- **Banden-Position dt-abhängig**: Bandkanten d = 2(1−cos k) skalieren
  mit dt, k mit √dt → Vorhersage-Bande war um Faktor ≈ 4.5 zu hoch.

**3. Korrigierte Disperson** (`corrected_dispersion.py`, exakt
nachgerechnet):

| D_v | korrigierte Bande | k* | λ* | σ* |
|---|---|---|---|---|
| 0.25 | stabil | — | — | — |
| 1.0 | stabil | — | — | — |
| 3.0 | [0.186, 0.456] | 0.292 | 21.5 Vox | 0.0808/t |
| 10.0 | [0.094, 0.490] | 0.222 | 28.3 Vox | 0.1763/t |

## Post-hoc-Konsistenz (KEINE Bestätigung — revidierte Vorhersage)

| Beobachtung | Korrigierte Vorhersage | Status |
|---|---|---|
| k_peak = 0.262 (n=1-Schale) | Bande [0.186, 0.456] enthält exakt die 3 n=1-Moden (0.262, 0.370, 0.453); k*=0.292 → nächste Gittermode 0.262 | konsistent |
| D_v=0.25/1.0 kein Muster | stabil (beide Konventionen) | ✓ bestätigt (robust gegen den Bug) |
| Onset zwischen 1.0 und 3.0 | D_v = 1.556 (dt-invariant) | ✓ bestätigt |
| Spätphase std²-Wachstum 0.0064/Schritt | 2σ*·dt = 0.0081/Schritt | ✓ innerhalb ~20 % |
| X mustert, Y fast flach (Ratio 0.29) | Aktivator patterned, Inhibitor diffundiert schnell | qualitativ ✓ |
| Amplitude sättigt (std 111 bei Mean 400) | nichtlineare Sättigung außerhalb linearer Theorie | erwartbar |

**Epistemischer Status**: Die vorab registrierte Banden-Vorhersage
bleibt FALSIFIZIERT (das Verdict steht). Die Korrektur ist eine
post-hoc-Übereinstimmung — sie erklärt die Falsifikation und macht
aus ihr eine neue, JETZT erstmals registrierte quantitative Vorhersage.
Eine Bestätigung liegt erst vor, wenn die korrigierte Disperson
**prospektiv** getestet wird (iter-17b).

## Entdeckung (neu, außerhalb der Vorab-Registrierung)

Genuine emergente stochastische Turing-artige Struktur im RDME-Substrat:

- Kollektives Wachstum einer endlichen Wellenlänge aus reinem
  demographischem Rauschen (kein seed-Feld, kein Zwang),
- Aktivator-Inhibitor-Asymmetrie (X std 111 vs Y std 32 bei Mean 400/520),
- Sättigung durch nichtlineare Terme (Mean bleibt 400 — Feed/Remove-
  Bilanz hält),
- kohärente Box-Skalen-Ordnung (λ ≈ 24 = Systemgröße).

Caveat: λ* ≈ 21.5 ≈ L=24 — das Gitter löst die korrigierte Bande nur
mit den 3 Moden der n=1-Schale auf; ein echtes Multi-Perioden-Muster
braucht L ≥ 48 (iter-17b).

## Offene Punkte → iter-17b

1. **Prospektiver Re-Test** mit korrigierter Disperson als neuer
   Vorab-Registrierung: Bande [0.186, 0.456] bei D_v=3, k*=0.292,
   σ*=0.0808/t, Onset 1.556; größerer Stack (L=48, T≥2000).
2. **Metrik-Defekt**: peak_excess ≥ 5 ist durch rotes demographisches
   Rauschen gesättigt (matched-Null selbst 5.64) — Kriterium muss
   band-selektiv werden (z.B. Leistung im korrigierten Band vs.
   matched-Null-Band, Permutationstest auf Moden-Basis).
3. **σ_meas war nan/0.0001** in der Lauf-Auswertung: die σ-Extraktion
   (log-Steigung der Moden-Amplitude über die letzten Snapshots) ist
   im sättigten Regime invalid — für iter-17b durch Wachstumsphasen-
   Fit (Schritte 100-400) ersetzen.
4. Registry-Audit bleibt: Netto-Stöchiometrie der 21 Reaktionen
   verdeckt Autokatalyse (VECTOR_REGISTRY_TURING_EXT) — das
   Schnakenberg-Substrat ist ein künstlicher Kern, kein Registry-
   Ausschnitt.

## Dateien

- `turing_rdme.py` — Experiment (Substrat, Nulls, Sweep, Verdicts)
- `corrected_dispersion.py` — korrigierte Disperson + Onset (Verifikation)
- `out/result.json` — Messreihen
- `run_log.txt` — Lauf-Ausgabe
- Produktion: `src/cellsim/modules/emergence.py::radial_power_spectrum`
  (+ 5 Tests) — radialer Spektrum-Detektor aus dieser Iteration