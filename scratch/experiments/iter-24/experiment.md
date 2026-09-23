# iter-24 — VECTOR_WINDOW_REPLICATION_V2: Trägt das Damköhler-Fenster unter dem korrigierten Sprung-Operator?

**Status: ABGESCHLOSSEN (2026-09-23) · Verdict: REPLICATED_STRONG_V2 · Grade: B**

Vorab-Registrierung: `window_replication_v2.py`-Docstring (vor dem Lauf fixiert); Lauf als registrierte R1 auf dem Produktionstack (CPU, ~1 h 45 min); Kriterien und Verdict-Logik wie bei iter-14 VERBATIM.

---

## 1. Frage

iter-16 definiert den Vektor: „iter-14-Fenster mit dem KORRIGIERTEN beidseitigen Sprung-Operator re-replizieren (iter-14 lief mit dem drift-behafteten Operator)".

Operator-Archäologie (git `3fa5753`, `modules/emergence.py` zur Zeit von iter-14): der damalige Operator sprang **EINSEITIG** (upwind):

```python
moves = rng.binomial(f_int, p_dir)          # p = 𝒟
fields[s_id] = f_int - moves + np.roll(moves, 1, axis=axis)
```

Das ist **Advektion mit Drift +𝒟 pro Achse** (Mittelverschiebung, keine Diffusion) mit Varianzwachstum ≈ 3𝒟 gesamt — die iter-14-Buchhaltung („p=𝒟, Varianzwachstum 6𝒟/Schritt") traf die Implementation NICHT. Der iter-15-Fix (Produktion, heutige Version) macht die Sprünge **beidseitig**: `n_out = binomial(f, 2𝒟)`, 50/50 auf ±Richtung → Drift 0, Varianzwachstum exakt 6𝒟 gesamt (2𝒟 je Achse).

V2 re-repliziert das Fenster-Signal unter dem korrigierten Operator: **GLEICHE Kriterien, GLEICHE nominal-𝒟-Achse, GLEICHES Gitter/Registry/Bump — ANDERES Operator-Substrat.**

## 2. Registriertes Modell

- **M1** iter-14-Protokoll VERBATIM: N_STEPS=600, SNAP_EVERY=10, Q_BIN=0.75, GRID 24³, DT_REACTS=(0, 1e-6, 1e-5, 1e-4, 1e-3), DIFF_COEFFS=(0.05, 0.15, 0.45), MIN_STRONG=6/MIN_WEAK=3, 3-Reaktions-Subset („glycolysis", „atp_hydrolysis", „atp_synthase"), Gauß-Bump amp=150 width=6 auf Glucose+ATP, RDMEAdapter(use_tau_leap=True), Metriken via emergence_metrics + corr_glc_atp_mean + p11_mean + mass_ratio + reaction_events_total.
- **M2** EINZIGE Änderungen ggü. iter-14: (a) Operator = Produktion post-iter-15 (beidseitig); (b) Seeds {200, 201, 202} — disjunkt zu iter-11 {42,43,44} und iter-14 {100,101,102}.
- **M3** Nominal-𝒟-Achse unverändert: die tatsächliche Mischrate unterscheidet sich (iter-14: 3𝒟 + Drift; V2: 6𝒟, driftfrei) — genau das ist der getestete Substrat-Wechsel.

## 3. Kriterien (vor dem Lauf fixiert)

**K1 Operator-Kalibrierung als UNABHÄNGIGE Messung** (keine Selbst-Bezeugung durch den Docstring), Delta N=2e5 im Zentrum von 63³, k=20 Schritte:

| Sub-Kriterium | Schranke | Alter Operator (analytisch) |
|---|---|---|
| (a) Massenerhalt | exakt | exakt (beide) |
| (b) Drift nach k=20 | ≤ 0.05 Voxel/Achse | +𝒟·k = +1.0/+3.0/+9.0 → **20×–180× über der Schranke** |
| (c) Varianz vs 2𝒟·k | rel ≤ 3 % | ≈ 𝒟 je Achse → **−50 %** |
| (d) Beidseitigkeit: \|c₊−c₋\|/(c₊+c₋) nach 1 Schritt | ≤ 0.1 | c₋ = 0 → **ratio = 1 exakt** |

Vorarbeit-Note: ein vor der Registrierung dokumentierter Probe (seed 777) bestätigte Massenerhalt, Drift ≤ 2e-3/Achse und Varianz 2𝒟/Achse; er INFORMIERTE die Schwellen (Abstände ≥ 4× Rauschen), buchte aber KEIN Ergebnis.

**K2 Harness-Determinismus**: Konfig (D=0.15, dt=1e-5, seed 200) doppelt ausgeführt → bit-identische Metriken.

**K3 (BINDEND)** iter-14-Verdict-Logik VERBATIM: classify je Seed (RUNAWAY mass_ratio > 3; DISTINCT corr_drop > 0.3 ODER lz_diff > 0.05 ODER tmi_diff > 0.05 gegen die seed-gepaarte Kontrolle dt=0; Konfig-DISTINCT bei ≥2/3 Seeds DISTINCT). assess: 0 DISTINCT → FALSIFIED; Sättigungs-Rückkehr |corr(dt=1e-3) − ctrl| ≤ 0.1 je D; Fenster-Ordnung |corr(1e-6) − ctrl| < |corr(1e-5) − ctrl| für ≥2/3 D; ≥6 DISTINCT + sat + order ≥ 2 → REPLICATED_STRONG; ≥3 → REPLICATED_WEAK; sonst PARTIAL.

## 4. Ergebnis

**K1 — PASS** (alle vier Sub-Kriterien; der alte Operator würde um 20×–180× scheitern):

| 𝒟 | Symmetrie (≤ 0.1) | Drift/Achse (≤ 0.05) | Var/Achse (erwartet 2𝒟·k) | rel-Fehler (≤ 3 %) |
|---|---|---|---|---|
| 0.05 | 0.0141 | +0.0055 max | 2.003/2.006/2.000 (exp 2.000) | ≤ 3.1e-3 |
| 0.15 | 0.0041 | 0.0105 max | 5.977/6.010/6.019 (exp 6.000) | ≤ 3.8e-3 |
| 0.45 | 0.0033 | 0.0107 max | 18.105/18.007/17.985 (exp 18.000) | ≤ 5.8e-3 |

**K2 — PASS** (bit-identisch = True).

**Sweep** (Mittel über 3 Seeds; Klassifikation per Seed gegen die seed-gepaarte Kontrolle; Spalten: corr / LZ-Wachstum):

| Konfig | iter-14 (einseitig, Seeds 100-102) | iter-24 V2 (beidseitig, Seeds 200-202) |
|---|---|---|
| Kontrolle 𝒟=0.05 | NULL 0.0972 / +0.0978 | CONTROL 0.0522 / +0.1244 |
| (0.05, 1e-6) | **DISTINCT** 0.0830 / +0.0156 | **DISTINCT** 0.0468 / +0.0292 |
| (0.05, 1e-5) | NULL 0.0648 / +0.1015 | **DISTINCT** 0.0378 / +0.0292 |
| (0.05, 1e-4) | **DISTINCT** 0.0442 / +0.0295 | **DISTINCT** 0.0272 / +0.0046 |
| (0.05, 1e-3) | **DISTINCT** 0.0874 / −0.0109 | **DISTINCT** 0.0445 / +0.0219 |
| Kontrolle 𝒟=0.15 | NULL 0.0401 / −0.0053 | CONTROL 0.0200 / +0.0289 |
| (0.15, 1e-6) | **DISTINCT** 0.0371 / +0.0607 | NULL 0.0184 / −0.0020 |
| (0.15, 1e-5) | NULL 0.0303 / +0.0342 | **DISTINCT** 0.0163 / +0.0643 |
| (0.15, 1e-4) | NULL 0.0232 / −0.0166 | NULL 0.0112 / +0.0126 |
| (0.15, 1e-3) | **DISTINCT** 0.0344 / +0.0352 | **DISTINCT** 0.0158 / +0.0036 |
| Kontrolle 𝒟=0.45 | NULL 0.0222 / +0.0192 | CONTROL 0.0093 / −0.0302 |
| (0.45, 1e-6) | NULL 0.0202 / −0.0133 | NULL 0.0085 / +0.0080 |
| (0.45, 1e-5) | **DISTINCT** 0.0171 / +0.0504 | **DISTINCT** 0.0076 / +0.0282 |
| (0.45, 1e-4) | **DISTINCT** 0.0126 / +0.0222 | NULL 0.0050 / −0.0013 |
| (0.45, 1e-3) | NULL 0.0182 / +0.0216 | **DISTINCT** 0.0067 / +0.0531 |

**DISTINCT 8/9** (iter-14: 7/9), **Sättigungs-Rückkehr True** (|corr(1e-3) − ctrl| ≤ 0.1 in allen 3 D-Regimen: 0.008/0.004/0.003), **Fenster-Ordnung 3/3**, 0 RUNAWAY (mass_ratio ≤ 1.08).

## 5. Verdict

**REPLICATED_STRONG_V2** (registrierte Logik: ≥ 6 DISTINCT + sat + order ≥ 2; K1/K2 PASS).

## 6. Interpretation (was sich ändert — und was nicht)

- **Die Replikationskette iter-11 → 14 → 24 steht auf drei Operator-Substraten**: rint-Laplace 16³ (iter-11, Seeds 42-44) → einseitig drift-behaftet 24³ (iter-14, Seeds 100-102) → beidseitig driftfrei 24³ (iter-24, Seeds 200-202). Das Damköhler-Fenster (Phänomen) überlebt Gitter-, Seed-, Numerik- UND jetzt auch den Drift-vs-diffusiv-Wechsel. Die empirische Basis des N\*-Gesetzes (iter-15/16-Brücke) steht.
- **Strukturelle Konstante über alle drei Läufe: das corr-Kriterium feuert NIE.** In iter-14 UND V2 bleiben alle corr-Drops ≤ ~0.05 (Schranke 0.3) und tMI ≈ 0 (Schranke 0.05) — alle DISTINCTs sind **LZ-Wachstums-getrieben**. Das ist jetzt als replizierter Befund gebucht, nicht als Einzellauf-Zufall: das registrierte „Fenster" ist ein Fenster in der **temporalen Entropie-Struktur** (LZ der binarisierten Snapshots), nicht in der Glc-ATP-Korrelation. iter-14s methodischer Fund („corr-Magnitude operator-kalibriert") wird damit bestätigt und verschärft: auch unter dem korrigierten Operator ist corr kein Träger.
- **Zellmuster nahe der Schranke ist Rauschen dominiert**: 4/9 Zellen klassifizieren identisch, 5 kippen ((0.05,1e-5) NULL→DISTINCT, (0.15,1e-6) DISTINCT→NULL, (0.15,1e-5) NULL→DISTINCT, (0.45,1e-4) DISTINCT→NULL, (0.45,1e-3) NULL→DISTINCT) — alle Kippen liegen an der 0.05-LZ-Schranke, und die Klassifikation ist per-Seed (≥2/3) gegen seed-gepaarte Kontrollen, während result.json nur Konfig-Mittel persistiert (gleiches Buchhaltungsverhalten wie iter-14). Die ROBUSTE Ebene ist nicht die Einzelzelle, sondern das Konfig-Muster: 8/9 DISTINCT, Ordnung 3/3, Sättigung in beiden Läufen.
- **Buchhaltungskorrektur zu iter-14.md**: die dortige Zeile „Kalibrierung Sprung-Diffusion ✅ p=𝒟 (Varianzwachstum 6𝒟/Schritt)" war gegen die damalige Implementation (git 3fa5753, einseitig → 3𝒟 + Drift) FALSCH — iter-15s beidseitiger Operator erfüllt sie erst. K1 misst das jetzt unabhängig (keine Selbst-Bezeugung durch den Docstring): der alte Operator würde K1 um 20×–180× scheitern (Drift +1.0/+3.0/+9.0 Voxel, Symmetrie-Ratio 1.0 exakt).
- **Was NICHT behauptet wird**: kein corr-Drop-Fenster, keine scharfen Zellgrenzen, keine Aussage über die U-Form-Tiefe relativ zum Kontroll-Floor (iter-14s VECTOR_STOCH_CONTROL_METRIC bleibt offen). Das Fenster ist als Konfig-Muster über Substrate robust, nicht als absolute Magnitude.

## 7. CORREKTUR-LOG (nichts post-hoc gebucht)

- **Kein CORREKTUR des registrierten Protokolls** — der Lauf lief als registriert (K1/K2/K3 unverändert).
- **Vorarbeit-Probe (seed 777)** vor der Registrierung dokumentiert: informierte die K1-Schwellen (Abstände ≥ 4× Proben-Rauschen), buchte kein Ergebnis (im Registrierungs-Docstring).
- **gpu_operator.py (Nachfolge-Infrastruktur, nicht Teil des registrierten Laufs)**: cupy-API-Probe (`cp.random.Philox` existiert nicht → `cp.random.Philox4x3210`); Validierung G1–G4 mit denselben registrierten K1-Schwellen **PASS** (Masse exakt, Drift max 0.0097, Varianz rel max 7.4e-3, Symmetrie max 0.0197); **G5 CPU↔GPU-Äquivalenz** (Verteilungs-Gleichheit, nicht Zug-Gleichheit) innerhalb des Bandes. Benchmark: 7.8–8.0 ms/Schritt (26 Spezies, 24³) vs CPU 263.9 ms → **33–34×**; ein 47-Run-Sweep fällt von ~2 h auf ~3-4 min. Artefakt: `gpu_validation.txt`.
- **Buchhaltungs-Note**: result.json persistiert nur Konfig-Mittel + Konfig-Klassifikation, nicht die per-Seed-Klassifikationen (identisch zu iter-14). Nahe der 0.05-LZ-Schranke ist die Zell-Klassifikation aus den Mitteln allein rekonstruktiv nicht ableitbar — die Konfig-Ebene (8/9, Ordnung, Sättigung) ist die gebuchte Evidenz.

## 8. Nächste Vektoren

1. **VECTOR_SATURATION_MARGIN** (iter-11/14, offen) — Registry-k-Sweep Richtung Sättigung, jetzt unter dem beidseitigen Operator (GPU-Sweep, G-kriterien wie oben).
2. **VECTOR_ENDOGEN_UVC_TIMESCALE** (iter-12/13, offen) — 1 Event/Molekül/~6.6 Jahre, präbiotisch vs. in-vivo.
3. reserviert: **iter-19b VECTOR_SHELL1_CASCADE** (Turing-Schale-1-Anomalie).
4. optional: **VECTOR_STOCH_CONTROL_METRIC** (iter-14, offen) — Effektgrößen-Metrik relativ zum Kontroll-Rausch-Floor + Permutationstest direkt auf die U-Form.

## Artefakte

- `window_replication_v2.py` — Vorab-Registrierung + registrierter R1-Lauf (K1–K3)
- `result.json` — K1/K2-Reports + Sweep + Verdict
- `gpu_operator.py` + `gpu_validation.txt` — GPU-Port des Operators (Nachfolge-Infrastruktur, G1–G5 validiert, 33–34×)
- Produktion: `src/cellsim/modules/emergence.py` (beidseitiger Operator, post-iter-15) — unverändert, K1 misst ihn unabhängig