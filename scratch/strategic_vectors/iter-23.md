# iter-23 — VECTOR_PHOTONIC_COUPLING_PRODUCTION

**Verdict: PHOTONIC_CHANNEL_INERT_FOR_SYN3A · Grade: C · Status: abgeschlossen (2026-09-23)**

## Frage

Die Trp-Superradianz (iter-15) war Produktions-ORPHAN. Vektor: den
photonischen Kanal als optionale Quelle in den HybridDriver koppeln
(Flag-gated, Default OFF) und den falsifizierbaren Kern prüfen: liefert
der Kanal in JCVI-syn3A photochemischen Turnover im registrierten
Damköhler-Fenster — oder ist er pump-energetisch entwertet?

## Registrierung (Kurzfassung)

Best-Case zugunsten des Kanals: das GESAMTE Zell-Trp (N_trp = 2011,
HYPOTHESE) als EIN superradiantes Kollektiv; 100 % der ATP-Hydrolyse
(1e6/s, EMParams-Anker) als Pump. Zwei strukturelle Schranken:
- **Pump-Cap (Energieerhaltung)**: Φ_cap = P_ATP/E_photon = 1.17e5
  Photonen/s bei 280 nm — ein UV-Photon kostet ~8.5 ΔG_ATP;
  kollektivgrößen-UNABHÄNGIG (Dicke-N² komprimiert Zeit, erzeugt keine
  Energie).
- **Burst-Lemma**: Absorption pro Molekül pro Burst = N·g(r)·σ
  (ungesättigt); mit f = Φ_cap/N kürzt sich N — schritt-integrierte
  Photochemie ist burst-invariant; die N²-Peak-Rate ist chemisch
  irrelevant. Domäne: N·g·σ ≪ 1; für N ≥ N_sat = 1/(g·σ) kappst
  Grundzustands-Entleerung auf (Φ_cap/N)·QY ≤ Average-Route —
  die Average-Route am Pump-Cap ist globale obere Schranke über alle N.

## Resultat (Kriterien K1–K5 PASS nach K3v2-Korrektur)

- Turnover am Pump-Cap: **5.65e-5/s bei r=100 nm (1.77e3× unter der
  Fenster-Unterkante 0.1/s)**; 4.27e-6/s bei r=250 nm (2.34e4×); bei
  10 nm immer noch 1.13e1× darunter — der Kanal ist an KEINER Distanz
  im Fenster.
- Fenster-Unterkante bräuchte 1.77e9 ATP/s = **1.77e3×** den
  EMParams-Anker (Energiekonsistenz: dasselbe Margin wie der Turnover).
- Produktions-Smoke: Driver-Telemetrie ≡ Modul-Raten (bit-identisch);
  Default-Quelle (f=1 Hz) liegt 1.03e5× unter lo.
- K2 Doppel-Herleitung: worst rel 2.4e-16; K3v2 Normalisierung ∫I dt ≡ N
  numerisch rel 2.84e-16 (τ_SR-skaliertes Gitter um t_delay).
- Domänen-Grenzen: N_sat(r=100 nm) = 2.07e8, N_sat(r=250 nm) = 2.74e9 —
  Kurian-Meganetzwerke (1e4–1e6) INNERHALB der Domäne (Lemma trägt auch
  für Eukaryoten-Substrate).

## Epistemischer Status

- **Photonischer Kanal in syn3A photochemisch INERT** — vom Declared
  (Kurian-Hypothese) zum Derived: Energieerhaltung schneidet das
  N²-Argument kollektiv-unabhängig ab, das Burst-Lemma entwertet den
  Peak-Rate-Eindruck strukturell.
- **CORREKTUR R1→R2**: das K3-Gitter enthielt N=1e9 außerhalb der
  Lemma-Domäne (N·g·σ = 4.83 ≥ 1) → R1 korrekt REGISTRATION_ERROR;
  Diagnose: Fehlregistrierung des Kriteriums, nicht des Modells; K3v2
  mit domänen-validem Teil-Gitter + gebuchten Domänen-Grenzen.
  R1-Ergebnis unangetastet auf Platte (`result_r1.json`).
- **Rand ehrlich**: die Falsifikation hängt am Pump-Anker (1e6 ATP/s);
  1.77e3× darüber läge die Unterkante — physiologisch entfernt (das
  bindete ~100 % des syn3A-Metabolismus), aber nicht parameterfrei.
- **Gate-Kontext**: Kurian-Substrat (Mikrotubuli-Trp-Gitter) fehlt in
  syn3A strukturell (Prokaryot) — C3-Gate OFF konsistent.
- **Ketten-Konsistenz iter-21/22/23**: Schild (Konfluenz zweier Floors),
  Kick (in-Box energetisch entwertet), Photonen (pump-entwertet) — drei
  Kanäle, drei unabhängige Energie-Schranken, ein Muster.

## Nächste Vektoren

1. VECTOR_WINDOW_REPLICATION_V2 (iter-14-Fenster, korrigierter
   Sprung-Operator — Basis des N\*-Gesetzes)
2. reserviert iter-19b: VECTOR_SHELL1_CASCADE

Artefakte: `scratch/experiments/iter-23/{photonic_budget.py,result.json,
result_r1.json,korrektur_log.md,experiment.md}`,
`src/cellsim/modules/photonic_coupling.py`,
`tests/unit/test_photonic_coupling.py`,
`tests/integration/test_photonic_driver.py`, Driver-Wiring
(`driver/loop.py`, `cli/run.py` --superradiance).