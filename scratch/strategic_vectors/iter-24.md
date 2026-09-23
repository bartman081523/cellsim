# iter-24 — VECTOR_WINDOW_REPLICATION_V2

**Verdict: REPLICATED_STRONG_V2 · Grade: B · Status: abgeschlossen (2026-09-23)**

## Frage

iter-16-Vektor: das iter-14-Damköhler-Fenster mit dem KORRIGIERTEN
beidseitigen Sprung-Operator re-replizieren. Operator-Archäologie (git
3fa5753): iter-14 lief auf einem EINSEITIGEN (upwind) Operator —
`moves = binomial(f, 𝒟)`, alle Sprünge +1 → Advektion mit Drift +𝒟 je
Achse, Varianz ≈ 3𝒟 gesamt; die damals gebuchte Kalibrierung
„6𝒟" traf die Implementation nicht. Produktion (post-iter-15):
beidseitig, Drift 0, Varianz 2𝒟 je Achse.

## Registrierung (Kurzfassung)

iter-14-Protokoll VERBATIM (Gitter 24³, 600 Schritte, Q_BIN 0.75,
3-Reaktions-Subset, Bump auf Glucose+ATP, tau-leap); EINZIGE Änderungen:
(a) beidseitiger Operator, (b) disjunkte Seeds {200,201,202}. K1
Operator-Kalibrierung als UNABHÄNGIGE Messung (Delta 2e5, 63³, k=20;
Schranken: Drift ≤ 0.05, Varianz rel ≤ 3 %, Symmetrie ≤ 0.1 — der alte
Operator scheitert dort um 20×–180×); K2 Harness-Determinismus
(bit-identisch); K3 iter-14-Verdict-Logik VERBATIM.

## Resultat

- **K1 PASS** (alle Sub-Kriterien; Varianz 2.00/6.01/18.05 vs erwartet
  2/6/18; Drift max 0.011; Symmetrie max 0.014) · **K2 PASS**
- **8/9 DISTINCT** (iter-14: 7/9), **Ordnung 3/3**, **Sättigungs-
  Rückkehr True**, 0 RUNAWAY
- → **REPLICATED_STRONG_V2**: die Replikationskette iter-11 → 14 → 24
  trägt auf drei Operator-Substraten (rint-Laplace 16³ → einseitig 24³
  → beidseitig 24³); die Basis des N\*-Gesetzes steht.

## Epistemischer Status

- **Träger-Konstante repliziert**: in BEIDEN Läufen feuert das
  corr-Kriterium NIE (Drops ≤ ~0.05, Schranke 0.3; tMI ≈ 0) — alle
  DISTINCTs sind **LZ-Wachstums-getrieben**. Das Fenster ist ein
  Fenster in der temporalen Entropie-Struktur, nicht in der
  Glc-ATP-Korrelation. Jetzt als replizierter Befund gebucht.
- **CORREKTUR zu iter-14.md**: die Zeile „Kalibrierung ✅ p=𝒟
  (6𝒟/Schritt)" war gegen die damalige Implementation falsch
  (einseitig → 3𝒟 + Drift); der beidseitige Operator erfüllt sie erst.
  K1 misst das unabhängig (keine Docstring-Selbst-Bezeugung).
- **Zellgrenzen Rauschen dominiert**: 4/9 Zellen identisch, 5 Kippen
  an der 0.05-LZ-Schranke (per-Seed-Klassifikation, Konfig-Mittel
  persistiert nur Mittel — wie iter-14). Robust ist die Konfig-Ebene
  (8/9, Ordnung, Sättigung), nicht die Einzelzelle.
- **Nicht behauptet**: kein corr-Fenster, keine scharfen Zellgrenzen,
  keine U-Form-Tiefe-Aussage (VECTOR_STOCH_CONTROL_METRIC offen).

## Nächste Vektoren

1. VECTOR_SATURATION_MARGIN (Registry-k-Sweep, jetzt beidseitiger
   Operator, GPU-Sweep mit G-Kriterien)
2. VECTOR_ENDOGEN_UVC_TIMESCALE
3. reserviert iter-19b: VECTOR_SHELL1_CASCADE

Artefakte: `scratch/experiments/iter-24/{window_replication_v2.py,
result.json,experiment.md,gpu_operator.py,gpu_validation.txt}`;
Produktion `modules/emergence.py` unverändert (K1 misst ihn
unabhängig).