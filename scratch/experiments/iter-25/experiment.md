# iter-25 — VECTOR_SATURATION_MARGIN

**Verdict: SATURATION_MARGIN_MODERATE · Grade: B · Status: abgeschlossen (2026-09-23)**

## Frage

iter-11/14-Vektor: „Realzellen betreiben hohe Enzymdichte → nahe am
Sättigungs-Kollaps? Hypothese: reale Metabolit-Felder sind glatt, weil
der Damköhler-Kollaps sie glättet. Testbar: registry-k k-Faktor-Sweep
Richtung Sättigung." Falsifizierbarer Kern: bei welchem k-Faktor k_f
(alle Registry-Geschwindigkeitskonstanten × k_f) verliert das
Fenster-DISTINCT-Muster seine Präsenz — und liegt das nominale Regime
(k_f = 1) NAHE an dieser Kante (Hypothese getragen) oder WEIT davon
(Hypothese falsifiziert)?

## Struktureller Vorab-Befund (registriert, vor dem Lauf)

Der Tau-Leaper ist first-order linear: λ = k·dt·n_reaktant
(`adapters/rdme.py`, `_step_tau_leap`); die Zug-ANZAHLEN hängen nicht
von dt ab. Damit ist (k_f, dt) eine **exakte Reparametrisierung** von
(1, k_f·dt) bei gleichem Seed — der k-Sweep bei dt=1e-5 ist ein feines
Damköhler-Gitter (Umsatz k·dt ∈ [1e-5, 1e-1], 3 Punkte je Dezade).
K4 verifiziert die Äquivalenz exakt (bit-identisch); Abweichen wäre
Harness-Asymmetrie (REGISTRATION_ERROR).

## Registriertes Protokoll (Kurzfassung)

- **M1** iter-24-Harness VERBATIM (Gitter 24³, 600 Schritte, Q_BIN
  0.75, 3-Reaktions-Subset glycolysis/atp_hydrolysis/atp_synthase,
  Gauß-Bump amp=150 width=6 auf Glucose+ATP, tau-leap, Metriken +
  corr + p11 + mass_ratio + events, classify/assess iter-14/24).
- **M2** Substrat: Diffusions-Operator auf GPU (iter-24-validiert,
  in-run K1 re-gemessen). RNG-Split: GPU-Philox für den Operator,
  CPU-PCG64 für tau-leap.
- **M3** Achse: k_f ∈ {1,3,10,30,100,300,1000,3000,10000} bei
  dt=1e-5; Anker D ∈ {0.05, 0.15, 0.45}; Seeds {200,201,202}
  (= iter-24 R1 → k_f=1-Zellen direkt vergleichbar). Kontrolle dt=0
  je Anker, seed-gepaart.
- **M4** Äquivalenz-Protokoll: (k_f, dt₀/k_f) vs (1, dt₀) für
  {(10,1e-5),(100,1e-5),(10,1e-4),(100,1e-4)} bei D=0.15 — erwartet
  bit-identisch.
- **Verdict-Bänder (registriert)**: NARROW < 10×; MODERATE
  10× ≤ Kante < 100×; WIDE ≥ 100× (lokalisiert); ABSENT > 1e4
  (Oberende DISTINCT); UNRESOLVABLE; REGISTRATION_ERROR bei
  K1/K2/K4-Verletzung.

## Durchführung

1. Lauf 1 (registriert): extern gestoppt bei Zelle 13/105 (EINTR —
   Signal aus der Nutzerschicht, keine Systemstörung: kein OOM, kein
   Suspend/Reboot, journal unauffällig). Teillog erhalten als
   `run_log_interrupted.txt`; NICHTS daraus gebucht.
2. Lauf 2 (registriert, identisch deterministisch): komplett, 27/27
   Zellen + K1/K2/K4/K5, exit 0.
3. Recovery-Lauf (`recover_controls.py`): die 9 dt=0-Kontrollzellen
   deterministisch wiederholt — NUR zur Persistenz (die in-run-
   Kontrollmittel waren nicht in result.json gelandet, s.
   CORREKTUR-LOG). Gleiche Seeds → bit-identische Werte; kein neuer
   Befund.

## Ergebnis

### K1 Operator-Kalibrierung (GPU, iter-24-Schwellen) — PASS

Identische Werte zu iter-24 gpu_validation.txt (deterministisch):
Sym 0.0101/0.0034/0.0197, Drift max 0.0097, Varianz
2.001/6.015/18.049 vs erwartet 2/6/18. Masse/Drift/Varianz/Beidseitigkeit ok.

### K2 Determinismus — PASS

run_config(1.0, 1e-5, 0.15, 200) doppelt → bit-identische Metriken.

### Kontroll-Baselines (dt=0, Recovery-Persistenz)

| D | LZ | corr | tMI | p11 |
|---|---|---|---|---|
| 0.05 | +0.0222 | 0.0529 | 0.0038 | 0.0510 |
| 0.15 | +0.0249 | 0.0186 | 0.0004 | 0.0482 |
| 0.45 | **−0.0252** | 0.0083 | 0.0001 | 0.0477 |

Auffällig: die Kontroll-LZ dreht bei D=0.45 ins Negative — schneller
Mischung zerstört die LZ-Baselinestruktur. (Folgen unten.)

### Sweep (27 Zellen; Klassifikation per-Seed ≥2/3, Tabelle zeigt Konfig-Mittel)

| Anker | k_f | class | LZ | events |
|---|---|---|---|---|
| D=0.05 | 1 | DISTINCT | −0.028 | 9.5e6 |
| D=0.05 | 3 | NULL | +0.055 | 2.9e7 |
| D=0.05 | 10 | DISTINCT | +0.006 | 9.8e7 |
| D=0.05 | 30–100 | NULL | +0.064/+0.039 | 3.0e8/1.0e9 |
| D=0.05 | 300–10000 | NULL | **+0.039 (identisch)** | **1.67e9 (identisch)** |
| D=0.15 | 1, 3 | DISTINCT | +0.062/+0.026 | 9.5e6/2.9e7 |
| D=0.15 | 10 | NULL | +0.007 | 9.8e7 |
| D=0.15 | 30, 100 | DISTINCT | −0.008/+0.039 | 3.0e8/1.0e9 |
| D=0.15 | 300–10000 | NULL | −0.003 (identisch) | 1.67e9 (identisch) |
| D=0.45 | 1, 3, 10 | NULL | +0.025/+0.016/−0.007 | 9.5e6/2.9e7/9.8e7 |
| D=0.45 | 30, 100 | DISTINCT | +0.087/+0.063 | 3.0e8/1.0e9 |
| D=0.45 | 300–10000 | DISTINCT | +0.053/+0.052 (identisch) | 1.67e9 (identisch) |

### Kanten

- D=0.05: k_edge = 10 (lokalisiert)
- D=0.15: k_edge = 100 (lokalisiert)
- D=0.45: Kante NICHT lokalisiert — Oberende (k_f=1e4) selbst
  DISTINCT (registrierte Regel; s. CORREKTUR-LOG zur Code-Abweichung)
- **Globale Kante = min(10, 100) = 10 → SATURATION_MARGIN_MODERATE**
  (Band 10 ≤ Kante < 100; exakt an der NARROW-Grenze)

### Substrat-Sperre (Events-Plateau — physische Sättigung, zweiter Rand)

D=0.05: events ab k_f=300 konstant 1.6725e9, Metriken bit-identisch —
die Trajektorien werden **k-invariant** (substrat-limitiert; mehr
Katalysator ändert nichts mehr). D=0.15: Plateau ab k_f=300
(1.6728e9). D=0.45: Plateau erst ab k_f=1000 (1.6729e9).
→ ZWEI verschiedene Kanten: die **Metrik-Kante** (registriertes K3:
10/100/nicht-lokalisiert) und die **Substrat-Sperre** (k≈300–1000).
Die Metrik-Kante VORAUS der harten Sättigung; am Plateau ist das Feld
chemisch eingefroren, aber seine LZ-Struktur bleibt je nach D
kontroll-nah (D≤0.15: NULL) oder kontroll-fern (D=0.45: LZ +0.052 vs
Kontrolle −0.0252 → DISTINCT bleibt).

### K4 Damköhler-Äquivalenz — EQUIVALENT (PASS)

Alle 4 Paare (k_f, dt₀/k_f) vs (1, dt₀) **bit-identisch** in allen
Metrik-Feldern — exakt wie registriert vorausgesagt (λ linear,
Zug-Anzahlen dt-unabhängig). Der k-Sweep ist damit gemessen, nicht
nur behauptet, ein feines Damköhler-Gitter.

### K5 Konsistenz (GPU k=1 vs iter-24 R1 CPU) — 2/3

D=0.05 DISTINCT ✓, D=0.15 DISTINCT ✓, D=0.45 **NULL vs iter-24
DISTINCT** (grenzwertige LZ-Zelle: GPU-Mittel +0.025 vs Kontrolle
−0.0252 → Diff 0.050, exakt an der Schranke; per-Seed ≥2/3 nicht
erreicht). Nicht bindend; konsistent mit der iter-24-Lektion
(Zellgrenzen Rauschen-dominiert, Konfig-Ebene robust).

## Hypothesen-Lesung

- **MODERATE**: das nominale Registry-Regime liegt 1–2 Dekaden unter
  der Metrik-Kante (10–100×) — iter-11-Hypothese („nahe am
  Sättigungs-Kollaps") **schwach getragen**: nicht nah (NARROW wäre
  < 10×), aber auch nicht weit (WIDE wäre ≥ 100×). Von der harten
  Substrat-Sperre trennen es 2.5–3 Dekaden (300–1000×).
- **Kante wächst mit D** (10 → 100 → >1e4): schneller Mischung trägt
  das Fenster-Signal tief in die Sättigung hinein — am Plateau bleibt
  D=0.45 DISTINCT, während D≤0.15 kontroll-nah NULL wird. Teil davon
  ist ein Baseline-Effekt der Metrik (Kontroll-LZ dreht bei D=0.45
  negativ und vergrößert alle Diffs) — saubere Effektgrößen relativ
  zum Kontroll-Rausch-Floor bleiben VECTOR_STOCH_CONTROL_METRIC.
- **Gitter-Auflösung**: 3 Punkte je Dezade → die wahre Kante liegt
  irgendwo in (10, 30); das Verdict-Band ist daran robust (MODERATE
  für jede Kante in [10, 100)).
- **Nicht behauptet**: keine Aussage über reale syn3A-Enzymdichten
  (Registry-k sind MGENITALIUM/HYPOTHESE-Label); die Marge ist eine
  Eigenschaft DIESES Registry-Subsets + Metrik, nicht der Zelle.
  corr-Kriterium feuert in KEINER Zelle (4. Lauf in Folge) —
  strukturelle Konstante bestätigt: das Fenster ist LZ-Entropie-
  getrieben.

## Epistemischer Status / Vorbehalte

- **Nicht-Monotonie D=0.05**: DISTINCT/NULL/DISTINCT bei k=1/3/10 —
  grenznahe Zellen kippen per-Seed (iter-24-Lektion). Die globale
  Kante 10 ruht auf der schwächsten Anker-Zelle; robust ist die
  Konfig-Ebene (Kanten-Ordnung mit D, Plateau-Struktur), nicht die
  Einzelzelle.
- **Keine U-Form-Aussage, keine Absolut-Magnituden** — nur
  Klassifikations-Präsenz gegen die seed-gepaarte Kontrolle.

## CORREKTUR-LOG

1. **assess_margin-Code-Abweichung**: die registrierte Regel „ist die
   Gitterspitze (k_f=1e4) selbst DISTINCT, ist die Kante nicht
   lokalisiert" fehlt im Code — D=0.45 wurde als localized=true mit
   k_edge=1e4 gebucht. Korrekt (registriert): D=0.45 Kante > 1e4,
   NICHT lokalisiert. Der Verdict ist unter beiden Lesungen
   identisch (globale Kante = min der lokalisierten = min(10, 100) =
   10 → MODERATE). Der zusätzliche Code-Zweig
   „any(nicht-lokalisiert) → ABSENT" ist ÜBERHAUPT nicht Teil der
   Registrierung (die registrierte Globalregel ist MIN der
   lokalisierten Kanten, konservativ) — toter Zweig, dokumentiert;
   die Registrierung ist bindend.
2. **Kontroll-Persistenz-Lücke**: die 9 dt=0-Kontrollmittel wurden
   in-run klassifiziert, aber nicht in result.json persistiert
   (Abweichung vom iter-24-Stil, wo dt=0 Teil des Gitters war).
   Recovery-Lauf (deterministisch, bit-identisch) schließt die Lücke;
   Klassifikation nicht geändert.
3. **Interim-Remark korrigiert**: im Status zum ersten (gestoppten)
   Lauf hieß es „Kante ≈ 10 → NARROW" — falsch gegen die registrierte
   Bandgrenze (NARROW ist Kante < 10; 10.0 liegt exakt in MODERATE).
   Die Registrierung war bindend, das Verdict MODERATE korrekt.
4. **K5-Flip D=0.45**: GPU NULL vs iter-24-R1-CPU DISTINCT an einer
   grenzwertigen LZ-Zelle (Diff 0.050 an der Schranke) — nicht
   bindend, iter-24-Lesson bestätigt.
5. **Lauf 1 extern gestoppt** (EINTR, Zelle 13/105): Ursachensuche —
   kein OOM (13 Gi frei), kein Suspend/Reboot (uptime 14 d, `last -x`
   clean), journal unauffällig → Signal aus der Nutzerschicht.
   Teillog als `run_log_interrupted.txt` erhalten, nichts gebucht;
   Lauf 2 deterministisch komplett.

## Nächste Vektoren

1. Feiner Sweep um die Kante (Faktor-Abstand < 2, Band 10–30) +
   D-Abhängigkeit der Kante (mechanistische Erklärung offen:
   wie viel davon ist Metrik-Baseline?)
2. VECTOR_STOCH_CONTROL_METRIC (Effektgrößen relativ zum
   Kontroll-Rausch-Floor — jetzt doppelt motiviert)
3. VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13, offen)
4. reserviert iter-19b: VECTOR_SHELL1_CASCADE

## Artefakte

- `saturation_margin.py` (registriertes Protokoll + Implementation)
- `result.json` (27 Zellen, Kanten, K1–K5, next_vectors)
- `run_log.txt` (vollständiger Lauf 2), `run_log_interrupted.txt`
  (Lauf 1, nicht gebucht)
- `recover_controls.py`, `controls_recovery.json`,
  `controls_recovery_log.txt` (Kontroll-Persistenz)
- Vorlage: `scratch/experiments/iter-24/` (Harness + GPU-Operator)