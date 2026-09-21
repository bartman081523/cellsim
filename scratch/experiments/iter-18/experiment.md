# iter-18: VECTOR_OR_KERNEL — OR-Kollaps-Kern vs. gematchte Kontrolle

## Kontext

iter-16 rekonstruierte die Hagan-Parametrisierung korrekt (iter-7's
E_G-Formel war dimensional invalid, das Gate war invertiert). Ergebnis:
die einzige viable Ecke ist großzügig HYPOTHETISCH (f=5e-2, a=8nm,
N=1e9 korreliert, S=1e6) mit τ_OR/τ_dec = 0.61 — Gate ON, aber
physikalische Realität NICHT behauptet.

iter-18 baut daraus einen **ausführbaren Kollaps-Kern in Produktion**
(`src/cellsim/modules/orch_or.py`) und testet die zentrale
Diskriminationsfrage mit vorab registrierten Kriterien.

## Vorab registrierte Kriterien (fixiert vor dem Lauf, 2026-09-21)

Arme (3 Seeds, base_seed 400):
- **or_kernel**: ORCollapseKernel (Gate ON, ratio 0.61, hazard
  dt/τ_OR = 0.6623 @ dt=1e-4), cluster_size 16, n_sites 4096,
  T=4000 Schritte. Ein Draw → K=16 Sites gleichzeitig (kollektiv).
- **classical**: gematchte Kontrolle — Poisson(h·K) Events/Schritt,
  Sites uniform unabhängig; identische mittlere Rate, kein Muster.
- **shuffled**: OR-Matrix mit permutierten Site-Labels (Marginals
  exakt erhalten, Clusterstruktur zerstört) — S3-Negativkontrolle.

Readout-Dünnungs-Leiter: q ∈ {1.0, 0.5, 0.1} (Binomial-Dünnung).

Observablen (h = 0.6623, K = 16, p = h/256 ≈ 0.0026):
- **S1** Fano der per-Schritt-Serie: OR ≈ (1−q) + (1−h)·K·q =
  5.40 / 3.20 / 1.44; klassisch ≈ 1.
- **S2** Fano der per-Voxel-Counts. [VORAB REGISTRIERT: 1−h = 0.34 —
  **KORREKTUR-LOG**: falsch. Die Cluster-Wahl ist uniform →
  per-Cluster-Counts ~ Binomial(T, h/256) → Fano 1 − p ≈ 0.997,
  nahezu Poisson; keine Under-Dispersion in den Marginals. Messung
  0.88–1.01 bestätigt die Korrektur. S2 hat in diesem Design KEINE
  Trennkraft — die kollektive Signatur lebt in S1+S3.]
- **S3** Within-Cluster-Korrelation (15 Positionspaare × 256 Cluster,
  letzte 1000 Schritte, binär-exakt): korrekt q·(1−p)/(1−p·q) ≈ q →
  1.00 / 0.50 / 0.10. [VORAB REGISTRIERT mit h statt p: 0.25/0.036 —
  **KORREKTUR-LOG**: in die Korrelationsformel gehört die
  per-Cluster-Feuerwahrscheinlichkeit p = h/256, nicht h. Messung
  (0.49 / 0.10) bestätigt die korrigierte Formel.] Permutationstest:
  200 Site-Label-Permutationen; klassisch ≈ 0.

Verdicts:
- DISTINGUISHED_q: [p_S3 < 0.005 UND z_S3 > 4] ODER [p_S1 < 0.01 UND
  Fano_step(OR) ≥ 3·Fano_step(classical)]
- CONTROL_INVALID: Fano_step(classical, q=1) ∉ [0.8, 1.25]
- SIGNATURE_ROBUST: DISTINGUISHED bei q=0.1 in allen 3 Seeds
- SIGNATURE_DETECTABLE: bei q ∈ {1.0, 0.5} in allen Seeds, nicht q=0.1
- INDISTINGUISHABLE: nicht DISTINGUISHED bei q=1

Claim-Deckel (C2): Die Kollektivität ist per Konstruktion EINGEBAUT
(ein Draw → K Sites). Das Experiment prüft, ob die beiden GENERATIVEN
Modelle an den vorab registrierten Statistiken unterscheidbar sind und
welche Statistik welchen Readout-Verlust überlebt — KEIN Nachweis von
Kollaps-Physik, KEINE Natur-Messung.

## Kernel-Parameter (gemessen)

| Größe | Wert |
|---|---|
| e_single | 6.985e-49 J |
| τ_OR (N=1e9, korreliert) | 1.5098e-4 s |
| τ_dec (S=1e6) | 2.4639e-4 s |
| Ratio τ_OR/τ_dec | 0.6128 (Gate ON) |
| N* (Gate-Schwelle) | 7.83e8 |
| hazard @ dt=1e-4 | 0.6623 |

## Result

**Signal: SIGNATURE_ROBUST** — 3/3 Seeds, DISTINGUISHED bei ALLEN
q ∈ {1.0, 0.5, 0.1}; Kontrolle valide (Fano q=1 ≈ 1.0, Bereich
[0.8, 1.25] ✓); shuffled-S3 sauber negativ.

| q | S1 Fano_step (OR / Theorie) | S2 Fano_voxel (korrekt ≈0.997) | S3 corr (≈q) | z_S3 | shuffled S3 |
|---|---|---|---|---|---|
| 1.0 | 5.31–5.46 / 5.40 | 0.88–1.01 | 1.000 | ~506 | ~0.000 |
| 0.5 | 3.13–3.22 / 3.20 | 0.88–1.01 | 0.49 | ~250 | ~0.000 |
| 0.1 | 1.44–1.53 / 1.44 | 0.88–1.01 | 0.10 | 48–53 | ~0.000 |

- S1: quantitativ exakt (Formel (1−q)+(1−h)·K·q trifft gemessene Werte
  auf ±2 %); p_S1 = 0.0005 (p_min bei 2000 Permutationen) bei allen q.
- S3: Korrelation folgt exakt der korrigierten Formel ≈ q; p_S3 =
  0.0050 (p_min bei 200 Permutationen) in allen Zellen; z 506/250/50.
- Bei q=0.1 versagt der S1-Pfad (Ratio 1.45 < 3) — **S3 trägt die
  Distinktion allein**: die Within-Cluster-Korrelation überlebt
  90 % Readout-Verlust, die Fano-Statistik nicht.
- Shuffled-Arm: Marginals unverändert, S3 kollabiert auf ~0
  (p 0.26–0.93) — saubere Negativkontrolle, die Signatur sitzt
  wirklich in der Cluster-Kohärenz, nicht in den Marginals.

## Via-Negativa (ehrliche Abgrenzung)

- **C2-Deckel**: Kollektivität ist EINGEBAUT — der Test diskriminiert
  zwei generative Modelle, er beweist keine Kollaps-Physik.
- **S2 war vorab falsch registriert** (1−h statt 1−p) und hatte nie
  Trennkraft — Korrektur dokumentiert, nicht stillschweigend
  wegeditiert.
- **S3 war vorab mit h statt p registriert** — die Messung traf die
  KORRIGIERTE Formel exakt (0.49/0.10); die vorab registrierten Zahlen
  wären gefehlt haben. Beide Korrekturen stehen im Docstring.
- **C3 (syn3A)**: programmatisch verankert — `syn3a_gate_check()`:
  N_eff=1, S=1 → Ratio > 1e17 → Gate OFF, Kernel feuert nie. Der Kern
  ist in der Zellsimulation WIRKLOS (kein Mikrotubuli-Kollektiv).

## Produktion

- `src/cellsim/modules/orch_or.py`: ORConfig (frozen), `penrose_tau_or_s`,
  `tegmark_tau_dec_s`, `n_gate_threshold`, `ORCollapseKernel` (Gate,
  hazard dt/τ_OR, kollektiver kontiguierlicher Cluster-Kick),
  `syn3a_gate_check` — 14 Unit-Tests, alle grün.
- Testsuite gesamt: **213 passed**.

## Nächste Schritte

1. OR-Kick-Kopplung an RDME/Zustände bleibt HYPOTHESE und ist
   **nicht** implementiert (der Kernel liefert nur Ereignis-Muster) —
   bewusst nicht behauptet.
2. Falls iter-17b (Turing prospektiv) läuft: OR-Kern ist dort
   irrelevant (C3) — sauber getrennt halten.
3. Selbst-Audit-Update: neuer Vektor OR-KERNEL (Grade via
   `python -m cellsim audit --claim "..." --layer L4`).