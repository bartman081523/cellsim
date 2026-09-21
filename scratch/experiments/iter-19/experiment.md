# iter-19 — VECTOR_TURING_PROSPECTIVE (iter-17b): Turing-Muster prospektiv auf L=48

**Status: ABGESCHLOSSEN (2026-09-21)**

Mechanisches Verdict nach Vorab-Registrierung: **BAND_SHIFTED_CONTINUOUS**.
**Nachlauf-Befund (CORREKTUR-LOG B):** die registrierte "exakte Abbildung"
enthielt einen Stencil-Fehler — die registrierten Banden/Raten waren
Diagonalmodus-Werte in per-Achsen-Einheiten. In radialen Einheiten deckt
sich die registrierte Bande nahezu mit dem kontinuierlichen Symbol; die
vorab registrierte Diskrimination war damit **void**. Der Lauf selbst
lieferte saubere Daten, ein prospektives Onset-Bracket und eine
Banden-Verallgemeinerung; die korrigierte modus-aufgelöste Analyse
(`mode_correction.py`) ist Post-hoc-Konsistenz und wird **nicht** als
Bestätigung gebucht.

---

## 1. Frage

iter-17 (L=24) bestätigte Musterbildung am künstlichen Schnakenberg-Kern,
konnte aber die rivalisierenden Linearisierungen nicht unterscheiden:
Auf L=24 existiert die Schale 0.293 nicht. iter-19 wiederholt den Test
prospektiv auf L=48 (Schalen bis 0.472) mit zwei rivalisierenden
Vorhersagen aus der GLEICHEN Regel:

- **(a) Exakte diskrete Abbildung** (primär): M(k) = diag(mx,my)·(I+dt·J),
  die exakte Linearisierung des implementierten Updates (Sprung-Diffusion
  pro Achse, tau_leap, Reaktion vor Diffusion).
- **(b) Kontinuierliches Symbol** (Referenz): J − 2(1−cos k)·diag(D/DT).

Diskrimination: exakte Abbildung sagt Bande [0.1038, 0.2696], Schale 0.293
STABIL; kontinuierliches Symbol sagt Bande [0.186, 0.456], Peak bei 0.293.

## 2. Registrierte Kriterien (Kurzfassung; voll in turing_prospective.py-Docstring)

- **P1 ONSET**: D_v=1.0 auf Null-Niveau, D_v=3.0 wächst (Ratio ≥ 10 vs null3).
- **P2 BAND** (exakte Abbildung, primär): Leistung im out-high Fenster
  [0.280, 0.500] ≤ 3× null3 (Schale 0.293 stabil).
- **P3 GROWTH**: early sigma des Banden-Sums in [0.00113, 0.018]/Schritt;
  per-shell Fits gegen registrierte Raten.
- **P4 ANKER**: L=24-Anker repliziert iter-17 (k_peak = 0.262).
- **P5 BILANZ**: mean_x driftet ≤ 10 %.

Verdict-Logik: alle 5 → PATTERN_AS_PREDICTED_EXACT_MAP; P1/P3/P4/P5 ok +
P2 verletzt → BAND_SHIFTED_CONTINUOUS ("dann muss der Modellierungsfehler
in der Abbildung gefunden werden").

## 3. Lauf

Voller Lauf (~2.3 h, Hintergrund-Task, exit 0): 7 Konfigurationen
(anchor_L24, stable025, stable1.0, turing3 ×2 Seeds, turing10, null3 ×2,
null10), L=48 bzw. 24, T=400–1600 Schritte, base_seed 300. Daten:
`result.json` (670 KB). Registrierungs-Integrität wurde VOR dem Lauf
verifiziert (`verify_registration()` — die fehlerhafte Formel reproduzierte
ihre eigenen Zahlen; das prüft nur Selbstkonsistenz, nicht Korrektheit).

## 4. Mechanisches Verdict (nach Registrierung)

| Kriterium | Messung | Grenze | Status |
|---|---|---|---|
| P1 turing3/null3 @800 (Bande [0.104,0.270]) | **14526.98×** | ≥ 10 | PASS |
| P1 stable025 self @800 | 1.44× | < 3 | PASS |
| P1 stable10 self @800 | 1.49× | < 3 | PASS |
| P2 out-high [0.280,0.500] @800 vs null3 | **3622.2×** | ≤ 3 | **FAIL** |
| P2 out-high @1600 vs null3@800 | 6852.1× | — | (Kaskade) |
| P3 Banden-sigma early (n=8, ab Schritt 75) | **0.00730/Schritt** | [0.00113, 0.018] | PASS |
| P3 Schale 0.293 Wachstum bis 1600 | **×3866.75** | ~1 (registriert stabil) | kontra Registrierung |
| P4 k_peak (L=24-Anker) | **0.262** | 0.262±0.02 | PASS |
| P5 Drift turing3 / Anker | 0.00076 / 0.0121 | ≤ 0.10 | PASS |
| Banden-Verallgemeinerung D_v=10 (turing10/null10 @400) | **586.3×** | qualitativ | konsistent |

**Verdict: BAND_SHIFTED_CONTINUOUS** (P1/P3/P4/P5 erfüllt, P2 verletzt).

Wichtige Einzeldaten (turing3 seed 300):
- Schale 0.293: 2× Null-Niveau bei Schritt 100 → 8.8× @300 → 55× @500 →
  3484× @800 → Sättigung ~5250× @1000–1200 → Abkling auf 3867× @1600.
  Beschleunigtes Wachstum, Sättigung, Abkling — nichtlineares Regime mit
  OP-Verschiebung (mean_y 520 → 319.1/318.7 in turing3; turing10 → 233.2;
  Nullen ≈ 518.8).
- Departure (1.3× A0, A0 ≈ 4.0–4.7e7 = L³·σ²): in-band Schalen ab Schritt
  25–100; ALLE out-high Schalen (0.293, 0.320, 0.370, 0.393) bereits beim
  ersten Snapshot @25 mit Power-Raten +0.0033…+0.0086/Schritt.
- std_x wächst 20.0 → 477.8 bei stabilem Mittel (400.0 → 400.3) —
  Musterbildung ohne Massenverlagerung ✓.

## 5. CORREKTUR-LOG

**(a) Fehlende null1.0-Kontrolle.** `null1.0` wurde nicht als eigene
Konfig registriert; P1 benutzt stattdessen die Selbst-Baseline (Schritt 0)
der stable1.0-Arms. Dokumentiert, nicht verschwiegen; die P1-Aussage
(Onset-Bracket) bleibt belastbar, weil null3 die isotrope Kontrolle für
die Wachstumsseite liefert.

**(b) STENCIL-FEHLER in der registrierten exakten Abbildung (zentral).**
`turing_prospective.py::eig_max_step` rechnet
`mx = (1−2·du_step·c)³`, `my = (1−2·p_sub·c)^(3·n_sub)` mit
`c = 1−cos(k)` und der RADIALEN Wellenzahl k. Das ist der Multiplikator
des **Diagonalmodus (k,k,k)** (dessen per-Achsen Wellenzahl k/√3 ist und
dessen radiale Wellenzahl √3·k ist) — nicht der einer Modus (k,0,0), die
nur auf EINER Achse gedämpft wird. Die registrierten Zahlen (Bande
[0.1038, 0.2696], k*=0.169, Schalenraten 0.131→0.00347 … 0.262→0.00063,
Schale 0.293 "stabil") sind daher in **per-Achsen-Einheiten des
Diagonalmodus** ausgedrückt. Nachtrag mit radialen Einheiten
(×√3): Bande ≈ [0.180, 0.467], k* ≈ 0.2927 — praktisch das
kontinuierliche Symbol [0.186, 0.456], k* = 0.292. Dasselbe Bild bei
D_v=10: [0.0535, 0.2845]·√3 = [0.0927, 0.4927] vs registriert
[0.094, 0.490].
→ **Die registrierte Rivalität war ein Einheiten-Artefakt.** Die beiden
Analysen waren von Anfang an nahezu dieselbe Vorhersage; die mechanische
Interpretation von BAND_SHIFTED_CONTINUOUS ("exakte Abbildung falsifiziert,
kontinuierliches Symbol bestätigt") ist damit **void** — falsifiziert
wurde die fehlerhafte Registrierung, nicht die exakte Abbildung.
Integritätsnachweis: die fehlerhafte Formel reproduziert alle fünf
registrierten Zahlen exakt (0.1309→+0.003472, 0.18512→+0.004508,
0.2267→+0.002929, 0.2618→+0.000633, 0.2927→−0.001959) —
`mode_correction.py::registered_rate`.

**(c) Amplitude-vs-Power-Verwechslung.** Registrierte Schalenraten sind
Amplitudenraten (ln|eig|/Schritt); die Fits in `analyze.py` sind
Power-Raten (ln P/Schritt). Die in analysis.json gebuchten shell_fits
(z. B. Schale 0.262: gemessen 0.01117 "vs" registriert 0.000633, Ratio
17.65) vergleichen Äpfel mit Birnen. Die kanonische Korrektur (gemessen/2)
steht in §6. Ebenso mischt P3 ein Amplituden-Fenster [0.00113, 0.018] mit
einem Power-Fit (0.00730) — der Wert liegt in beiden Deutungen im Fenster,
das Buchhalten war aber schlampig.

**(d) MIXED_BANDS-Zweig unerreichbar.** Die elif-Reihenfolge in
`analyze.py` gibt BAND_SHIFTED_CONTINUOUS Vorrang vor MIXED_BANDS bei
identischen Bedingungen — registrierte Logik-Lücke, hier moot wegen (b).

**(e) Schalen-Label.** Schale 6 hat Zentrum 2π·√6/48 = 0.32064 (nicht
0.32059); Analyse-Skripte matchen per Toleranz. Schale 3: 0.22672
(Registrierung schrieb 0.22670).

**(f) analyze.py-Fehler vor Dateneingang behoben** (walrus-Restzeile,
falscher early_fit-Aufruf, defekte s293-Extraktion, JSON-String-Keys,
KeyError-Filter auf 'pass', P2-Display-Label). Keine nachträglichen
Kriterien-Änderungen.

## 6. Korrigierte modus-aufgelöste Analyse (POST-HOC — keine Bestätigung)

`mode_correction.py` rechnet die Abbildung pro Gittermodus nach:
mx = Π_a (1−2·du_step·c_a) (EIN Sprung-Diffusion-Aufruf, p = D_X = 0.06),
my = Π_a (1−2·p_sub·c_a)^n_sub, M = diag(mx,my)·(I+DT·J), Rate =
ln max|eig(M)| (Amplitude/Schritt); Vergleich mit dem kontinuierlichen
Symbol pro Modus und der gemessenen Früh-Rate (Power-Fit/2, Fenster
[1.5, 6]×A0, turing3 seed 300):

| Schale | n_Mod | exakt korr. | kont. Symbol | gemessen/2 |
|---|---|---|---|---|
| 0.13090 | 6 | −0.01047 | −0.01098 | **+0.00220** ⚠ |
| 0.18512 | 12 | +0.00071 | +0.00011 | +0.00180 |
| 0.22672 | 8 | +0.00347 | +0.00285 | +0.00172 |
| 0.26180 | 6 | +0.00447 | +0.00381 | +0.00559 |
| 0.29272 | 24 | +0.00469 | +0.00404 | +0.00302 |
| 0.32064 | 24 | +0.00452 | +0.00388 | +0.00321 |
| 0.37024 | 12 | +0.00359 | +0.00295 | +0.00190 |
| 0.39270 | 30 | +0.00300 | +0.00236 | +0.00357 |
| 0.41394 | 24 | +0.00227 | +0.00165 | +0.00222 |
| 0.43415 | 24 | +0.00149 | +0.00088 | +0.00186 |
| 0.45345 | 8 | +0.00063 | +0.00004 | +0.00107 |
| 0.47197 | 24 | −0.00016 | −0.00075 | +0.00081 |

Befunde:
1. **Korrigierte Abbildung ≈ kontinuierliches Symbol**: Differenz
   +0.0005…+0.0007/Schritt in jeder Schale — exakt der erwartete
   Splitting-Fehler O(dt·D·c). Korrigierte Bande (Moden-Scan):
   **[0.1851, 0.4534]** vs kontinuierlich [0.186, 0.456].
2. **Gemessene Raten decken die korrigierte Feinstruktur** (Post-hoc!):
   Peak-Lage (0.262–0.320), Abfall zu 0.453, Vorzeichenwechsel an der
   Oberkante — z. B. Schale 0.41394: vorhergesagt +0.00227, gemessen
   +0.00222. Systematische Abweichungen sind mit dem Baseline-Bias
   vereinbar (s. §7).
3. **Schale 0.131 ist die EINE saubere Diskrepanz**: beide korrigierten
   Analysen sagen Abkling (−0.0105), gemessen wächst sie (+0.0022; Bande
   inkl. 0.131 wächst 14527× über null3 @800).

## 7. Baseline-Bias der Früh-Raten (warum keine quantitative Buchung)

P(t) = A0·e^{2σt} + (S/2σ)(e^{2σt}−1) mit injiziertem Rauschen S: bei
σ ≈ 0.0047 ist S/(2σ) ≈ 9e7 > A0 = 4.4e7 — der injizierte Rauschbeitrag
übersteigt das Schritt-0-Niveau, frühe Log-Steigungen sind nach oben
verzerrt (Schale 1: Bias-Term dominiert). Robust sind nur die
Verhältnis-Kriterien (P1/P2 gegen die isotrope Null), nicht die
absoluten Früh-Raten. Single-Seed pro Konfig in der Diskriminationsfrage.

## 8. Schale-1-Anomalie: Kandidatenmechanismen (unentschieden)

- **Differenz-Kaskade** (Hauptkandidat): k1−k2 → (1,0,0), z. B.
  (2,1,0)−(1,1,0). Quellen-Raten: σ(2,1,0) = +0.00469 (instabil,
  Schale 5), σ(1,1,0) = +0.00071 (marginal). Idealisierte Kaskaden-Power-
  Rate 2(σ1+σ2) ≈ +0.0108/Schritt vs gemessen ≈ +0.0044…+0.0070 —
  gleiche Größenordnung (Kopplungskoeffizient < 1). Summen-Kaskaden
  können Schale 1 nicht speisen (niedrigster Modus); Differenz-Kaskaden
  schon.
- **OP-Drift** (geprüft, schwächer): mit dem End-Mittel (v = 319/400 =
  0.80) bleibt der Modus (1,0,0) in der korrigierten Abbildung stabil
  (|eig| ≈ 0.958); der Drift allein kippt die Schale nicht. Grobe Prüfung
  an Mittelwerten — lokale Fluktuationen (std_y wächst stark) nicht
  berücksichtigt.
- Fazit: Verletzung der LINEAREN Bande, erklärbar durch nichtlineare
  Kopplung; Mechanismus in iter-19 **nicht entschieden**. Neuer
  falsifizierbarer Zielvektor (iter-19b-Kandidat).

## 9. Was übrig bleibt (Kenntnis, Vorab-registrierungs-Treue)

Prospektiv gebucht (vor dem Lauf fixiert, vom Stencil-Fehler unberührt,
da verhältnis-/fensterbasiert):
- **Onset-Bracket**: D_v=0.25 und 1.0 flach (self 1.44×/1.49×), D_v=3
  wächst 14527× über null3. ✓
- **Musterbildung bei D_v=3 auf L=48** mit Aktivität über
  [0.131, 0.472] und k_peak-Konsistenz mit dem L=24-Anker (0.262). ✓
- **Banden-Verallgemeinerung**: D_v=10 wächst 586× über null10. ✓
- **Bilanz**: mean_x-Drift 0.08 %/1.2 % bei std_x ×24. ✓
- **Nichtlineares Regime**: Sättigung + Abkling + Y-Erschöpfung
  (520 → 319) — die lineare Theorie trägt nur im Early-Window.
Void gebucht: die exakte-Abb.-vs-kontinuierlich-Diskrimination
(Registrierungsfehler, §5b). Post-hoc gebucht (KEINE Bestätigung):
korrigierte Bande [0.1851, 0.4534] ≈ kontinuierlich; per-shell-Feinstruktur
passend innerhalb Baseline-Bias; Schale-1-Überschuss als neue Anomalie.

## 10. Nächster Vektor (iter-19b-Kandidat, noch NICHT registriert)

**VECTOR_SHELL1_CASCADE**: Ist der Schale-1-Überschuss eine
Differenz-Kaskade aus der aktiven Bande?
- Registrierbare Diskrimination: (i) Deaktiviere die Bande 0.185–0.453
  (Parameter-Variante ohne Instabilität bei gleichem Rauschen) →
  Schale-1-Überschuss muss verschwinden; (ii) Modusaufgelöste Phasen-
  Kreuzprodukte (2,1,0)×(1,1,0)* vs (1,0,0) im Early-Window (Kaskaden-
  Signatur); (iii) D_v-Variation: Kaskaden-Vorhersage folgt der
  Quellen-Bande, nicht der Schale-1-Locallinie.
- Zusätzlich: korrigierte per-Modus-Registrierung als Basis für jeden
  künftigen L=48-Lauf (mode_correction.py::exact_rate_mode), niemals
  wieder der Diagonalmodus-Stencil.

## Artefakte

- `turing_prospective.py` — Vorab-Registrierung + Lauf (Stencil-Fehler
  im Registrierungsteil DOKUMENTIERT BELASSEN, §5b; keine stille Korrektur)
- `analyze.py` / `analysis.json` — mechanisches Verdict nach Registrierung
- `mode_correction.py` / `mode_correction.json` — korrigierte
  modus-aufgelöste Analyse (Post-hoc) + Integritätsnachweis des Fehlers
- `result.json` — 7 Konfigurationen, base_seed 300