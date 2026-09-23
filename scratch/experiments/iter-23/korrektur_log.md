# CORREKTUR-LOG iter-23 — Run R1 → R2 (2026-09-23)

## R1-Ergebnis (result_r1.json, unangetastet)

**VERDICT: REGISTRATION_ERROR** — K3 verletzt.

- K1 Integrität: PASS (h, c, E_photon, ΔG_ATP, Fenster, σ/QY/λ, N_trp).
- K2 Doppel-Herleitung: PASS (Φ_cap worst rel 0.0; Turnover worst rel 2.4e-16).
- K3 Burst-Invarianz: **FAIL** — `max N·g·σ = 4.83e+00 ≥ 1` im registrierten
  N-Gitter {1, 1e2, 2011, 1e6, 1e9} bei r = 100 nm.
  - Die Normalisierung ∫I dt ≡ N hält numerisch (worst rel 2.84e-16) für
    ALLE N — sie ist domänen-unabhängig (Quell-Intensität, keine Absorption).
  - Die Route-Gleichheit (Burst-Route ≡ Average-Route) hält numerisch für
    alle N (rel 2.4e-16) — sie ist algebraisch, Sättigung ist im linearen
    Formelausdruck nicht kodiert.
  - Verletzt ist die **Gültigkeitsdomäne**: bei N = 1e9 absorbiert ein
    Molekül pro Burst 4.83 Photonen (Vorhersage der linearen Formel) —
    physikalisch unmöglich (Grundzustands-Entleerung kappst bei ~1/Burst).

## Diagnose: Fehlregistrierung des KRITERIUMS, nicht Falsifikation des Modells

Das registrierte Modell M4 definiert das Burst-Lemma MIT Gültigkeitsbedingung
„ungesättigt, N·σ·g(r) ≪ 1". Das K3-Gitter enthielt mit N = 1e9 einen Wert
AUSSERHALB dieser registrierten Domäne (bei r = 100 nm: N·g·σ = 4.83). Damit
prüfte K3 das Lemma außerhalb seines registrierten Gültigkeitsraums — ein
Fehler in der Kriteriums-Registrierung (R1), nicht im registrierten Modell.

Domänen-Grenze (analytisch): N_sat(r) = 1/(g(r)·σ).
- r = 100 nm: g = 4.827e8 cm⁻² → N_sat = 2.07e8
- r = 250 nm: g = 3.648e7 cm⁻² → N_sat = 2.74e9
Registriertes Substrat N_trp = 2011: 5 Größenordnungen INNERHALB der Domäne
(N_trp·g·σ = 9.7e-4 ≪ 1). Kurian-Meganetzwerk (1e4–1e6 Emitter): ebenfalls
innerhalb. N = 1e9 liegt bei r = 100 nm außerhalb (bei r = 250 nm innerhalb).

## R2-Registrierung (vor dem R2-Lauf fixiert)

K3v2 ersetzt K3; K1, K2, K4, K5 und die Verdict-Logik bleiben unangetastet:
1. ∫I dt ≡ N numerisch (rel ≤ 1e-6) über N ∈ {1, 1e2, 2011, 1e6, 1e9}
   (domänen-unabhängige Normalisierung).
2. Burst-Route ≡ Average-Route (rel ≤ 1e-6) über den DOMÄNEN-VALIDEN
   Teil-N-Gitter N ∈ {1, 1e2, 2011, 1e6} bei r = 100 nm, mit expliziter
   Assertion N·g·σ < 1 für jedes N der Teilmenge.
3. Domänen-Grenzen N_sat(r) für r ∈ {100, 250} nm gebucht als Ergebnis.
4. Sättigungs-Schranke (analytisch, gebucht): für N ≥ N_sat ist der
   per-Molekül-Turnover ≤ f·QY = (Φ_cap/N)·QY ≤ Φ_cap·g·σ·QY = Average-Route.
   Die Average-Route am Pump-Cap ist damit GLOBALE obere Schranke über alle N —
   K4 (bindend) bleibt unverändert gültig als Best-Case-Kriterium.

Bewertungsregel R2: VERDICT aus K4 über die registrierten bindenden Distanzen
wie in R1 registriert; REGISTRATION_ERROR nur noch bei Verletzung von
K1/K2/K3v2. Post-hoc-Konsistenz wird NIE als Bestätigung gebucht; der
R1-REGISTRATION_ERROR bleibt in der Kette dokumentiert.