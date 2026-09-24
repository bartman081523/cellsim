# Claims (fidelity-extrahiert)

## C01 — B · gemessen
Das Damköhler-Fenster überlebt Operator-, Gitter- und Seed-Wechsel (Replikationskette über drei Substrate).
- **distinct_cells**: 9/12 · 7/12 · 8/12
- **ordering**: 3/3
- **saturation_return**: True
- Kriterium: Registriert: ≥6 DISTINCT → REPLICATED_STRONG; Klassifikation per-Seed ≥2/3 gegen seed-gepaarte Kontrolle (Schranke |LZ-diff| > 0.05 oder corr_drop > 0.3).

## C02 — B · gemessen
Der beidseitige Sprung-Operator ist kalibriert: Varianz 2𝒟/6𝒟/18𝒟 je Achse, Drift unter der Schranke; der alte einseitige Operator scheitert an derselben Kalibrierung.
- **var**: 2.00–2.01 / 5.98–6.02 / 17.99–18.05 (erwartet 2/6/18)
- **var_rel_max**: 5.8e-03 (Schranke 3 %)
- **drift_max**: 0.0107 (Schranke 0.05)
- **symmetry_max**: 0.0141 (Schranke 0.1)
- **old_operator**: Drift +1.0/+3.0/+9.0 Voxel = 20×/60×/180× über der Schranke; Varianz −50 %; Symmetrie-Ratio 1.0 (analytisch)
- Kriterium: K1-Schwellen (iter-24 registriert): Massenerhalt exakt; Drift ≤ 0.05 Voxel/Achse; Varianz rel ≤ 3 %; Beidseitigkeit |c₊−c₋|/(c₊+c₋) ≤ 0.1. Schwellen durch dokumentierte Vorarbeit-Probe (seed 777) informiert, kein Ergebnis gebucht.

## C03 — B · gemessen
Der k-Sweep ist ein exaktes Damköhler-Gitter: (k_f, dt) und (1, k_f·dt) sind bit-identisch (tau-leap λ = k·dt·n ist linear).
- **equivalence**: 4/4 Paare bit-identisch
- Kriterium: Registriert: alle 4 Äquivalenz-Paare müssen in ALLEN Metrik-Feldern bit-identisch sein.

## C04 — B · gemessen
Die Sättigungs-Marge ist MODERATE: die Metrik-Kante liegt bei k_f = 10–100×, die harte Substrat-Sperre (Events-Plateau) bei ≈300–1000×.
- **edges**: D=0.05 → 10 · D=0.15 → 100 · D=0.45 → nicht lokalisiert (>1e4)
- **global**: globale Kante 10 → SATURATION_MARGIN_MODERATE
- **plateau**: Events k-invariant ab k_f ≈ 300 (D≤0.15) / 1000 (D=0.45)
- Kriterium: Registrierte Bande: NARROW < 10× ≤ MODERATE < 100× ≤ WIDE; Kante = größtes k_f mit DISTINCT; Oberende DISTINCT ⇒ nicht lokalisiert.

## C05 — B · gemessen
Das Fenster ist LZ-Entropie-getrieben, nicht corr-getrieben: das corr-Kriterium (corr_drop > 0.3) feuert in keinem Lauf der Kette.
- **corr_fires**: 0/39 Zellen (iter-24 + iter-25)
- **max_drop**: 0.025 · 0.024 vs Schranke 0.3
- Kriterium: Schranke registriert in iter-24/25: DISTINCT wenn corr_drop > 0.3 ODER lz_diff > 0.05.

## C06 — B · dokumentiert (Infrastruktur)
Der GPU-Port des Sprung-Operators (G1–G5 validiert) beschleunigt den Operator-Schritt um den Faktor 33.
- **speedup**: 263.9 ms → 7.98 ms pro Schritt = 33×
- Kriterium: G1–G5 mit denselben registrierten K1-Schwellen; G5 CPU↔GPU Verteilungs-Gleichheit (nicht Zug-Gleichheit).

## C07 — C · gemessen
Die iter-7 Orch-OR-Formel war dimensional invalid (E in J·s/m) — die '27-Dekaden-Widerspruch' war ein Formel-Artefakt. Die korrekte Penrose-Rechnung (E_G = G·(ΔM)²/a) gibt Kollaps-Zeiten viele Dekaden über der Dekohärenz; nur die Hagan-Parametrisierung erreicht Grenznähe.
- **artifact**: E_G-Formel-Artefakt: τ = 5.65e-37 s (invalid)
- **corrected_dimer**: τ_OR(Dimer) ≈ 3.8e11 s — kollabiert nie
- **hagan_best**: τ_OR/τ_dec = 0.61 (f=5%, a=8 nm, N=1e9, S=1e6) — ohne Shielding nichts viable
- Kriterium: Korrigierte Penrose-Formel (iter-16 registriert); Hagan-Ecke als freie Parameter-Ecke, nicht als Ableitung.

## C08 — C · gemessen
Shielding S=1e6 ist als ableitbar FALSIFIZIERT: die Box liefert maximal S ≈ 9.9e3, die Ecke braucht S ≈ 6.1e5 — Überleben nur in Konfluenz zweier Floor-Hypothesen.
- **gap**: S_max 9.9e+03 vs S_need 6.1e+05 (Faktor 62 zu wenig)
- Kriterium: Ortsgelöstes Dekohärenz-Feld Γ(r) = Γ_bulk·(φ + (1−φ)·ε_res); S_max = 1/(φ_floor + ε_opt).

## C09 — C · gemessen
Die Kick-Kopplung ist energetisch entwertet: Adressierbarkeit braucht N* ≈ 1.7e11 Ionen bei τ_relax = 1 ms — 1.74× über der Box-Decke; pro Event bleiben ~1.6e-10 k_B·T an der Ecke.
- **n_star**: N* 1.74e+11 vs Box-Decke 1e11
- **corner_energy**: 1.6e-10 k_B·T pro Event
- Kriterium: Fluktuations-Dissipation: E_acc ≥ k_B·T im Relaxationsfenster (τ_relax ≤ 1e-3 s, großzügig).

## C10 — C · gemessen
Der photonische Kanal ist für syn3A INERT: Turnover am Energie-Pump-Cap liegt 3 Dekaden unter dem Damköhler-Fenster; die N²-Peak-Rate ist burst-invariant und chemisch irrelevant.
- **turnover**: 5.65e-05/s bei r = 100 nm — 1771× unter Fenster-Unterkante (0.1/s)
- **burst**: Burst-Invarianz: |ΔNorm| = 2.8e-16 (rel)
- Kriterium: Pump-Cap Φ_cap = P_ATP/E_photon (energiegebunden, kollektiv-unabhängig); Fenster-Unterkante 0.1/s (iter-23 registriert).

## C12 — B · gemessen
Feingitter (iter-26): die D=0.05-Kante (10) ist bestätigt; die Kantenfolge über D ist aber NICHT monoton (EDGE_D_NONMONOTONE) und die Klassifikation bildet kein zusammenhängendes Band.
- **edges**: D=0.05 → 10 · D=0.1 → 3 · D=0.15 → ≥200 (n.lok.) · D=0.25 → 30 · D=0.3 → ≥1000 (n.lok.) (D=0.45 iter-25, rechtszensiert)
- **band**: 4/5 Anker mit internen NULLs — Zellflips zwischen benachbarten k_f
- **lz_straddle**: LZgrw -0.049…+0.081 straddelt die ±0.05-Schwelle
- **gates**: K1 PASS · K2 bit-identisch · K4a 2/2 · K5 9/9 bit-identisch zu iter-25
- Kriterium: Registriert (iter-26): k_edge = größtes k_f mit DISTINCT (per-Seed ≥2/3); Oberenden-Regel (Gitterspitze DISTINCT ⇒ nicht lokalisiert); V2-Intervall-Konsistenz benachbarter D.

## C11 — B · gemessen
Die Registry trägt KEIN Turing-Substrat: 0/20 Autokatalyse im Netto-Schema, 0 Verstärkungs-Zyklen, alle Jacobian-Kombinationen negativ, Attraktor = Totzustand (ATP = 0).
- **autocatalysis**: 0/20 Netto-Reaktionen
- **cycles**: 0 Verstärkungs-Zyklen (48 Conversion-Zyklen)
- **jacobian**: max Re(λ) = -1.2e-04 < 0
- **dead**: Attraktor ATP = 0 (Residual 8.6e-9)
- Kriterium: Turing-Instabilität verlangt Re(λ) > 0 bei endlichem k; Autokatalyse verlangt positive Netto-Stöchiometrie-Selbstverstärkung.
