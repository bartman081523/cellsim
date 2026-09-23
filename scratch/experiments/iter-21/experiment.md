# iter-21 — VECTOR_SHIELDING_FIELD: Ist das Schild S=1e6 ableitbar?

**Status: ABGESCHLOSSEN (2026-09-23) · Verdict: SHIELD_UNDERIVABLE_CONFLUENCE_ONLY · Grade: C (OPEN, geschärft)**

Vorab-Registrierung: `shielding_scan.py`-Docstring (vor dem Lauf fixiert);
Produktionsmodul `src/cellsim/modules/shielding.py` (10 Unit-Tests,
Invarianzen ohne Ergebnis-Buchung); `ruff check src/` clean.

---

## 1. Frage

iter-16 liess die großzügige Hagan-Ecke (f=5e-2, a=8 nm, N=1e9, korreliert)
nur MIT dem Schild S=1e6 viable werden (τ_OR/τ_dec = 0.61); 0 viable ohne
Shielding. S=1e6 ist in `ORConfig` eine HYPOTHESE-Konstante. Kann S aus
einem mechanistischen, ortsaufgelösten Dekohärenz-Feld (mt_quantum-Pattern:
Γ-Feld, Kohärenz-Kerne, Event-Horizont-Radius) ABGELEITET werden — oder
stirbt die Ecke ohne die freie Konstante?

## 2. Registriertes Modell (Kurzfassung; voll im Modul-/Skript-Docstring)

Registerierte Bilanz ist Tegmarks **Kollisions-Kanal**:
Γ_bulk = k_B·T·(Δm/m)²/ħ; Γ_need = 1/τ_OR (Gate τ_OR < τ_dec).

- **M1 Streuter-Ausschluss**: Γ(r) = Γ_bulk·(φ(r) + (1−φ(r))·ε_res),
  Zwei-Zonen-Feld (geschützter Kern φ_free, außen Bulk). Das ist der
  EINZIGE Hebel auf dem Kollisions-Kanal: Debye-Screening schirmt
  FELD-Kanäle, nicht Kontakt-Kollisionen (M3, registriert).
- **M2 Formfaktor**: GESCHLOSSEN (S=1) — thermale Wassermoleküle
  (λ_deB ≈ 0.023 nm ≪ Δx = 8 nm) lösen die Branches voll auf.
- **M4 Konformations-Achse**: Δm/m freigelegt, Box [1e-4, 1e-2]
  (iter-16 fixierte 1e-2; Floor = großzügige Konform-Superposition).
- **Best-Fall zugunsten von Orch-OR**: Ionen-Kanal κ_ion = 0 (jeder
  κ > 0 verschlechtert das Überleben nur).
- Konsistenz-Haken zur Kette: ε_res ≪ 1e-6 erfordert ein
  Fröhlich-artiges kohärentes Schild — REFUTED_BY_REIMERS_2010
  (VECTOR_FROEHLICH_CONDENSATION) in diesem Repo.

Registrierte Schranken (großzügig): φ_free ≥ 1e-4; ε_res ∈ {1e-2 pess
(klassisches Bad), 1e-6 opt (Motional-Narrowing)}; Δm/m ∈ [1e-4, 1e-2];
Ecke fixiert = ORConfig-Defaults.

## 3. Kriterien (K1–K5, vor dem Lauf fixiert)

| Kriterium | Messung | Status |
|---|---|---|
| K1 Γ_bulk ≡ 1/τ_dec(S=1) (Produktionscode, 3 Δm/m) | rel ≤ 1e-12 | PASS |
| K1 τ_OR(Ecke) vs iter-18-Anker | 1.50980e-4 vs 1.5098e-4 | PASS |
| K1 τ_dec_bulk vs iter-18-Anker | 2.46395e-10 vs 2.4639e-10 | PASS |
| K1 S_need ≡ τ_OR/τ_dec_bulk | 6.1276e5 | PASS |
| K2 Doppel-Herleitung (MC 4e6 Samples, seed 2100, Region [0, r_core+d_w] inkl. Bulk-Schale) | MC 2.001586e9 vs analytisch 2.001548e9 → **rel 1.91e-05** | PASS (≤ 1e-3) |
| K5 Kohärenz-Kern an der Ecke (beide Regime) | **r_h = 0 nm** | bestätigt (erwartet) |

## 4. Ergebnis

**K3 — das Schild ist NICHT ableitbar (UNDERIVABLE):**

| Größe | Wert |
|---|---|
| S_max(Box) = 1/(φ_floor + ε_opt) | **9.90e3** |
| S_need(Ecke) = Γ_bulk·τ_OR | **6.128e5** |
| Faktor | **62× zu kurz** |
| S=1e6 äquivalent zu | φ_free + ε_res = 1e-6 → φ ≈ 1e-6 (**100× unter dem Floor**) |

**Ecke (Δm/m = 1e-2, iter-16-Fixierung, φ = Floor) stirbt in BEIDEN Regimen:**

| Regime | ratio = Γ̄·τ_OR | S_eff | r_h | φ_erforderlich |
|---|---|---|---|---|
| pessimistisch (ε=1e-2) | **6188** | 99 | 0 nm | **negativ** — das gebundene Wasser ALLEIN dekohäriert mit 4.1e7 s⁻¹ ≫ Γ_need = 6.6e3; kein φ_free hilft |
| optimistisch (ε=1e-6) | **61.9** | 9.90e3 | 0 nm | 6.32e-7 — **100× unter dem Floor 1e-4** |

**Überlebens-Grenzen Δm/\* (analytisch, Grid bestätigt):**

| Regime | φ=1e-4 | φ=1e-3 | φ=1e-2 |
|---|---|---|---|
| pessimistisch | **1.271e-4** (nur Floor-Punkt, ratio 0.62) | 1.219e-4 (2 Grid-Punkte) | 9.06e-5 (**0 Punkte — unter dem Floor**) |
| optimistisch | **1.271e-3** (14 Grid-Punkte) | 4.038e-4 (8) | 1.277e-4 (2) |

## 5. Verdict

**SHIELD_UNDERIVABLE_CONFLUENCE_ONLY** (registrierte Logik: UNDERIVABLE
+ Überleben nur im Konfluenz-Fenster). Alle Kriterien PASS; kein
REGISTRATION_ERROR. Alle vier registrierten Ausgänge waren Erstklass-
Resultate; keine Gesichts-sparende Verzweigung.

## 6. Interpretation (was sich ändert — und was nicht)

- **iter-16-Ecke verliert das freie Schild.** Die "viable Region in der
  großzügigen Parameter-Ecke" ruhte vollständig auf S=1e6; abgeleitet
  sind maximal ~1e4. Bei der iter-16-Parametrisierung (Δm/m = 1e-2)
  stirbt die Ecke in beiden Bad-Regimen (Faktor 62–6000 über der
  Überlebenslinie), und es existiert **kein Kohärenz-Kern**.
- **Überleben nur in Konfluenz**: Δm/m ≲ 1.3e-3 (großzügige Konform-
  Superposition) UND ε_res ≲ 1e-6 (Motional-Narrowing) UND
  φ_free ≲ 1e-4 — alle drei gleichzeitig an ihren Floors. Das ist
  **kein Beweis gegen Orch-OR**: Hagens Konform-Superpositions-Behauptung
  lebt exakt in diesem Fenster. Aber die Beweislast liegt jetzt auf
  ZWEI großzügigen Floor-Hypothesen statt auf EINER freien Konstante —
  und jede einzelne ist falsifizierbar anschließbar (Konform-Δm/m messbar
  an Konformations-Ensembles; ε_res an Hydrationswasser-Korrelationszeiten).
- **Debye-Screening ist kein Rettungshebel** auf der registrierten
  Tegmark-Bilanz — die Kollisions-Rate ist ein Kontakt-Kanal. Hagan et
  al. 2002 argumentieren teilweise über den ABGESCHIRMTEN Feld-Kanal
  (Dipol-Kopplung an die Ionen-Atmosphäre); dieser Kanal ist hier im
  Best-Fall (κ_ion = 0) zugunsten von Orch-OR ausgeschlossen und würde
  das Überleben nur verschlechtern. Eine volle Feld-Kanal-Bilanz wäre
  ein ANDERES Budget als das registrierte iter-16-Budget und bleibt
  offen deklariert.
- **Ketten-Konsistenz**: der einzige Weg unter ε_res = 1e-6 führt über
  ein kohärentes Schild (Fröhlich-Typ) — in diesem Repo bereits
  REFUTED (Reimers 2010). Das Schild-Szenario ist damit von beiden
  Seiten umschlossen.
- **Unverändert bleiben**: die Penrose-Formel (iter-16), das N\*-Gesetz
  (iter-15), der OR-Kernel als Modell-Diskrimination (iter-18, C2-Cap),
  und C3 (syn3A-Gate OFF, N_eff = 1).

## 7. CORREKTUR-LOG (alles vor Dateneingang; nichts post-hoc)

- **(a) Helper-Signatur-Bug vor dem Lauf**: `pytest_approx` wurde mit
  3 statt 4 Argumenten gerufen — beim Review vor der Ausführung
  gefunden, zu `approx_rel(a, b, rel)` vereinfacht. Keine Daten berührt.
- **(b) Test-seitige invertierte Identität** (vor dem Experiment, im
  Unit-Lauf): `test_s_needed_identity_with_gate_ratio` assertierte
  S_need ≡ 1/(τ_OR/τ_dec_bulk); korrekt ist S_need ≡ τ_OR/τ_dec_bulk
  (beide = Γ_bulk·τ_OR). Modul-Mathematik unberührt; der Testausdruck
  war falsch, nicht der Code.
- **(c) Lint**: ruff --fix (unbenutzter `math`-Import im Modul,
  Trailing-Newlines). Keine inhaltlichen Änderungen.
- **(d) Kosmetik**: die `boundaries`-Keys in result.json benutzen die
  ε-Werte ("0.01_" = pessimistisch, "1e-06_" = optimistisch) statt der
  Regime-Labels — Mapping hier dokumentiert, JSON nicht nachbearbeitet.

## 8. Nächste Vektoren (unveränderte Priorität, jetzt um eine Erkenntnis reicher)

1. **VECTOR_OR_KICK_COUPLING** — falsifizierbare Kick-Hypothese (was ein
   Kollaps chemisch bewirkt); macht den Kernel wirksam oder entwertet ihn.
2. **VECTOR_PHOTONIC_COUPLING_PRODUCTION** — superradiance als EMSource in
   den HybridDriver (Muster existiert in `driver/integration.py`).
3. **VECTOR_WINDOW_REPLICATION_V2** — iter-14-Fenster mit korrigiertem
   Sprung-Operator re-replizieren (Basis des N\*-Gesetzes).
4. reserviert: **iter-19b VECTOR_SHELL1_CASCADE** (Turing-Schale-1-Anomalie).

## Artefakte

- `shielding_scan.py` — Vorab-Registrierung + Lauf (K1–K5, Verdict-Logik)
- `result.json` — Integrität, Doppel-Herleitung, Box-Scan, Boundaries, Verdict
- Produktion: `src/cellsim/modules/shielding.py` + `tests/unit/test_shielding.py`