# tci_v2 — registrierte FHN-Vektor-Batterie (a–z): Lauf, Gates, Verdicts

Datum: 2026-09-28. Plan: `~/.claude/plans/tci-qualia-v2.md`. Denkmodus:
`ExtraordinaryFalsifierMixMind` (Pfad im Plan-Header). Registrierung:
Docstring von `v2_model.py`, fixiert VOR dem Hauptlauf — Kriterien, Gates,
Seeds und Verdict-Verzweigungen wurden nach der Registrierung nicht
verändert; Abweichungen nur als offen gebuchter KORREKTUR-LOG (unten).

## KORREKTUR-LOG (vor dem Hauptlauf; Pilot/Probe-Evidenz, Kriterien unverändert)

- **K1 Aktivitäts-Domäne** (Probe 1, PILOT-Regime A=0.5/eps=0.05/D=0.6,
  Seed 1400): Frame 0 zählte n=1885 „Kerne" bei u ∈ (−1.37, −1.01) —
  das Feld sitzt am Ruhepunkt, die Phase arctan2(δv, δu) ist dort
  reines Winkel-Rauschen, und die Plaquette-Curl unabhängiger
  Rausch-Winkel liegt flächendeckend über 0.5. Die Xu-Daten tragen eine
  Hilbert-Phase echter Oszillationen; ein erregbares Medium in Ruhe
  trägt KEINE Phase. Korrektur: Kern-Etikettierung nur in der
  Aktivitäts-Domäne (Mittel der 4 Eck-Abstände zum Ruhepunkt
  > ACT_THRESH = 0.5); die Plaquette-Formel bleibt VERBATIM.
  Probe-Befund: Frame-0-Artefakte 1885 → 0, echte Kerne unberührt.
- **K2 Per-Schritt-Rauschen 0.02 → 0.1** (Probe 2, gleiche Evidenz-Basis):
  bei σ_n=0.05 kollabiert die Kernaktivität nach dem Init-Transienten
  auf 0 (Frames 100–300: n=0) — Wellen laufen planar, Fronten brechen
  nicht; bei σ_n=0.1 anhaltende Kernaktivität über alle 400 Frames
  (n=3–20/Frame, punktartig, median quant = 1.00 in Kern-Frames) bei
  UNVERÄNDERTEN eps=0.05/D=0.6. AMP bleibt 0.5 (Probe: AMP 0.5 vs 2.0
  nahezu identisch — das Rauschen trägt die Fragmentierung, nicht der
  Antrieb).
- Beide Pilot-Resultate sind gebucht: `pilot_result_vor_korrektur.json`
  (σ_n=0.02, ohne Maske — 9/9 Konfigs unhealthy, Frame-0-Artefakte)
  und `pilot_result.json` (nach Korrektur). Keine Verdict-Promotion.

## Gates

- **G1 DETERMINISM: PASS** — Doppel-Lauf (Seed 1200, story_listen),
  u-Feld bit-identisch, max_abs_diff = 0.0.
- **G2 FINITENESS: PASS** — alle Entscheidungsmetriken finit;
  nan_fields = [] (NaN wäre offen gebucht und konservativ gewertet
  worden — trat nicht auf).

## Verdicts (registrierte Kriterien, 30 Haupt-Seeds 1200–1229 + 10 Switch-Seeds)

| Vektor | Verdict | Kern-Zahlen |
|---|---|---|
| Q1 SPIRAL_PROPAGATION | **ABSENT** (0/30) | median n_cores 0.0–2.0 (Kriterium ≥ 5), median Dauer 1–2 Frames (≥ 3), quant-Band ≥ 0.9 in ≥ 80 % der Kern-Frames verfehlt; nur Speed > 0.05 erfüllt (0.57–0.75 Zellen/Frame — aber das ist die Drift-Rausch-Fragmente, keine tragenden Spiralen) |
| Q2 DECODE | **WEAK** | LOO-Nearest-Centroid 4-kanalig: acc_spiral 0.325 vs Chance 0.25 (Nullmittel 0.2524), Permutation-p = 0.1264 → nicht signifikant; über Chance, aber beide Tests (p_perm < 0.05 UND Baseline-p < 0.05) verfehlt |
| Q3 DIRECTION_RECONFIG | **ABSENT** (0/10) | \|p_cw(A) − p_cw(B)\| max 0.091, aber 2·gepoolte SE 0.094–0.118 (Seed 1208: 0.0021 vs 0.044) — Kriterium \|diff\| > 2·SE nirgends erfüllt; Welch-p ≥ 0.127 |
| Q4 INTERACTION | **NOT_DOMINANT** | gepoolter Interaktions-Terminations-Anteil 0.1626 (21162/130159) vs registriert ≥ 0.8; Xu-Anker ~97.4 % nur als Interpretations-Vergleich |
| Q5 CHARGE_INFO_BEYOND_POSITION | **NOT_BEYOND_POSITION** | gain = 0.0 (acc_spiral 0.325 = acc_position 0.325 — identisch), gepaarte Permutation p = 1.0 |

Status: `REGISTERED_RUN_v2_vollstaendig` — 130/130 Trials persistiert
(`per_seed/trial_{seed}_{idx}.json`), keine abgebrochenen Läufe gebucht.
Gesamt-Laufzeit: ~234 s Haupt (127 s Slice 1 + 106 s Slice 2) + 149 s
Bestätigungs-Pilot.

## Interpretation (dreifach geschichtet)

1. **Gemessen**: Im registrierten Regime (eps=0.05, D=0.6, σ_n=0.1 nach
   K2, Aktivitäts-Maske nach K1) bildet das FHN-GitterTransient-Kerne
   (1–3 pro Frame, Dauer 1–2 Frames), aber **keine tragenden,
   quantisierten Spiral-Kerne** — Q1 verfehlt alle drei Struktur-Checks
   zugleich. Ohne tragende Spiralen entleert sich die Kette:
   Dekodierbarkeit sinkt auf Rauschen über Chance (0.325, p=0.13),
   Richtungssignatur ändert sich nicht über den Switch ( diffs ≈ SE),
   Terminationen sind überwiegend Rand-/Diffusions-Ereignisse (16 %),
   und Ladungs-Features tragen **exakt null** Information über die
   Positions-Kontrolle hinaus (gain 0.0, p=1.0).
2. **Nicht messbar (Ebene B)**: Ob diesem Vektor Qualia-Identität
   zukäme, bleibt untestbar — keine Vorabaussage, wie registriert.
3. **HYPOTHESE (Ebene C) — FALSIFIZIERT in diesem Medium**: Die
   Routing-Hypothese (Spiral-Ort + Ladung tragen Task-Routing jenseits
   der Position) ist **als registriert falsifiziert**: Q1 ABSENT und
   Q5 NOT_BEYOND_POSITION schließen die Kette vor ihrer ersten Stufe.
   Der falsifizierbare Kern der Ebene C trägt in diesem Medium nicht.

## Via-Negativa-Residuum

Was nach allen Negationen steht: (a) Der Xu-Analog-Kette fehlt im
FHN-Medium bereits das Fundament — ein erregbares Medium am Ruhepunkt
trägt keine Phase (K1); die Xu-Daten tragen sie stets, weil ihr Träger
echte Oszillationen sind. Die Analogie „Phase → Wirbel-Charge" erzeugt
hier transient-quantisierte, aber nicht persistente Strukturen.
(b) Wo Strukturen auftreten (D=0.3-Konfigs im Pilot: 39–92 Kerne/Frame,
quant ≈ 0.2–0.35), sind es Rausch-Schäume, keine quantisierten Spiralen
— Menge ist nicht Struktur. (c) Ein anderes Regime, das Q1–Q5 erfüllen
könnte, wäre eine NEUE Hypothese und verlangt NEUE Registrierung — kein
post-hoc Angeln in denselben Daten (Anti-Sharpshooter).

Xu-Anker (Interpretations-Vergleich, NICHT Kriterium): ~19 Spiralen/
Frame, Dekodier 48.3 % vs Chance 25 %, Annihilation ~97.4 %,
Richtungs-Flip 174.6° — hier gegenüber: 0–2 Kerne/Frame median,
0.325, 16.3 %, |diff| ≤ 0.09.

## Dateien

- `v2_model.py` — Modell + Metriken + Statistik + Registrierungs- und
  Korrektur-Log (Docstring)
- `v2_run.py` — Stages pilot / main / analyze
- `pilot_result_vor_korrektur.json` / `pilot_result.json` — beide
  Pilot-Scans (vor/nach K1+K2)
- `gates.json` — G1/G2
- `per_seed/trial_{seed}_{sched_idx}.json` — 130 Per-Seed-Vektoren
  (vollständig persistiert; mean-level-Buchung ist unauditierbar —
  Harness-Lektion iter-27/28)
- `v2_result.json` — Gates + Q-Verdicts + Per-Seed-Zusammenfassung
- `probe_regime.py`, `probe_regime2.py` — Diagnosen (PILOT-Labels,
  keine Verdict-Promotion)

Seeds: Pilot 1400–1403, Haupt 1200–1229 + Switch 1200–1209 — disjunkt
zu Korpus 1000–1009/2000–2009 und cellsim 200–339; Permutations-Seeds
4242/4243. Commit enthält nur Skripte/Resultate — keine Xu-Source-xlsx,
keine Paper-PDFs, nicht `neuro_vortices.txt`, keine Per-Seed-JSONs.

## Nachtrag 2026-10-05 — Rohdaten-LFS-Anker (KORREKTUR der Commit-Zeile oben)

Die Zeile oben („… keine Per-Seed-JSONs") ist für den Buchungs-Zeitpunkt
(2026-09-28) historisch korrekt und für den Stand ab 2026-10-05 falsch:
alle 130 per_seed-Trial-JSONs sind als Git LFS committet (Roh-Commit
`11949ec`), Muster `scratch/experiments/tci_v2/per_seed/**` in
`.gitattributes`; Integrität über SHA-256 je Datei in
`per_seed_manifest.json` (Manifest-Hash `8a305f27efd278a1…`). Re-Auswer-
tungen lesen ab jetzt ausschließlich die committeten Artefakte. Die
Ausschlüsse (Xu-Source-xlsx, Paper-PDFs, `neuro_vortices.txt`) bleiben
weiterhin gültig.

Kettenglied-Bruch (Ledger-Disziplin P3, offen gebucht): die Rohdaten
wurden ex ante persistiert, der git-Commit erfolgte erst nach der
Verdict-Buchung — das Glied „Roh-Commit vor Auswertung" fehlt in der
Entstehung; geschlossen ab 2026-10-05. Verdicts bleiben unverändert.

Quelle der Analog-Kette: Xu, Y., Long, X., Feng, J. & Gong, P. (2023),
„Interacting spiral wave patterns underlie complex brain dynamics and
are related to cognitive processing", Nature Human Behaviour 7,
1196–1215, DOI 10.1038/s41562-023-01626-5. Anschlusssliteratur mit DOIs:
`../../notes/tci_vortex_assessment.md` §10.