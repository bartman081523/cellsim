# iter-21 — VECTOR_SHIELDING_FIELD

**Verdict: SHIELD_UNDERIVABLE_CONFLUENCE_ONLY · Grade: C (OPEN, geschärft) · Status: abgeschlossen (2026-09-23)**

## Frage

Ist das iter-16-Schild S=1e6 (HYPOTHESE-Konstante in ORConfig)
mechanistisch ableitbar aus einem ortsaufgelösten Dekohärenz-Feld — oder
ruht die großzügige Hagan-Ecke (τ_OR/τ_dec = 0.61 MIT Schild) vollständig
auf der freien Konstante?

## Registrierung (Kurzfassung)

Bilanz: Tegmark-Kollisions-Kanal Γ_bulk = k_B·T·(Δm/m)²/ħ. Debye schirmt
Felder, nicht Kontakt-Kollisionen → einzige Hebel: Streuter-Ausschluss
M1 (Γ(r) = Γ_bulk·(φ(r) + (1−φ(r))·ε_res), Zwei-Zonen) + Konformations-
Achse M4 (Δm/m ∈ [1e-4, 1e-2]). Formfaktor M2 geschlossen (λ_deB ≪ Δx).
Ionen-Kanal κ_ion = 0 als Best-Fall zugunsten von Orch-OR. Schranken
großzügig: φ_free ≥ 1e-4, ε_res ∈ {1e-2 pess, 1e-6 opt}. Konsistenz-Haken:
ε_res ≪ 1e-6 erfordert Fröhlich-Schild → REFUTED_BY_REIMERS_2010.

## Resultat (Kriterien K1–K5 alle PASS)

- S_max(Box) = 1/(φ_floor + ε_opt) = **9.90e3** vs S_need(Ecke) =
  **6.128e5** → **Faktor 62 zu kurz**. S=1e6 äquivalent zu
  φ_free ≈ 1e-6 — **100× unter dem physiologischen Floor**.
- Ecke (Δm/m = 1e-2) stirbt in BEIDEN Regimen: ratio 6188 (pess) /
  61.9 (opt); **kein Kohärenz-Kern** (r_h = 0). Pessimistisch ist
  φ_erforderlich NEGATIV: gebundenes Wasser allein dekohäriert mit
  4.1e7 s⁻¹ ≫ Γ_need = 6.6e3 — kein φ_free hilft.
- Überleben nur im Konfluenz-Fenster: Δm/m ≲ 1.3e-3 (opt) bzw.
  ≲ 1.2e-4 (pess) UND ε_res ≲ 1e-6 UND φ_free ≈ 1e-4.
- K2 Doppel-Herleitung (MC 4e6 vs analytisch, Zonen-Grenz-Logik):
  rel 1.91e-05 PASS.

## Epistemischer Status

- **Keine volle Orch-OR-Falsifikation**: Hagens Konform-Superposition
  lebt exakt im überlebenden Fenster. Aber die Beweislast liegt jetzt
  auf ZWEI großzügigen Floor-Hypothesen (Konform-Δm/m ≲ 1.3e-3 UND
  ε_res ≲ 1e-6) statt auf EINER freien Konstante — beide falsifizierbar
  anschließbar (Konformations-Ensembles; Hydrationswasser-Korrelations-
  zeiten). Der pessimistische Zweig (klassisches Bad) ist TOD.
- **iter-16-Statusänderung**: die "viable Region in der Ecke" ist ohne
  S=1e6 nicht mehr registriert-viable; die Ecke wird zur Konfluenz-
  Region mit beidseitig umschlossenem Schild (Fröhlich-Haken).
- Unverändert: Penrose-Formel, N\*-Gesetz, OR-Kernel (C2), C3-Gate OFF.

## Nächste Vektoren

1. VECTOR_OR_KICK_COUPLING (Kick-Hypothese falsifizierbar machen)
2. VECTOR_PHOTONIC_COUPLING_PRODUCTION (superradiance → HybridDriver)
3. VECTOR_WINDOW_REPLICATION_V2 (iter-14-Fenster, korrigierter Sprung-Operator)
4. reserviert iter-19b: VECTOR_SHELL1_CASCADE

Artefakte: `scratch/experiments/iter-21/{shielding_scan.py,result.json,experiment.md}`,
`src/cellsim/modules/shielding.py`, `tests/unit/test_shielding.py`.