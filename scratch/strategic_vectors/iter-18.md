# iter-18 — VECTOR_OR_KERNEL

**Datum**: 2026-09-21 · **Layer**: L4-Brücke · **Grade**: B

## Kernresultat

OR-Kollaps-Kern in Produktion (`modules/orch_or.py`, iter-16-viable
Ecke als Defaults, τ_OR/τ_dec = 0.61, N*-Gate 7.83e8, hazard dt/τ_OR,
kollektiver Cluster-Kick) + gematchte klassische Kontrolle
(identische Rate, unabhängige Sites).

Diskrimination **SIGNATURE_ROBUST** (3/3 Seeds, alle q ∈ {1.0, 0.5, 0.1}):
- S1 (Fano der Schritt-Serie): Formel (1−q)+(1−h)·K·q exakt
  (5.4/3.2/1.44 gemessen ±2 %)
- S3 (Within-Cluster-Korrelation): ≈ q exakt (1.00/0.49/0.10),
  z bis 506; **überlebt 90 % Readout-Verlust** — bei q=0.1 trägt S3
  allein die Distinktion (S1-Pfad versagt: Ratio 1.45 < 3)
- Shuffled-S3: ~0 (saubere Negativkontrolle) — Signatur sitzt in
  Cluster-Kohärenz, nicht in Marginals
- S2 (Voxel-Fano): KEINE Trennkraft (0.88–1.01 ≈ 1) — korrekt
  vorhergesagt 1 − p ≈ 0.997

## Via-Negativa

- C2-Deckel: Kollektivität EINGEBAUT — Modell-Diskrimination, kein
  Kollaps-Physik-Nachweis. Im Modul-Docstring vorab registriert.
- Zwei vorab-Formelfehler (S2: 1−h statt 1−p; S3: h statt p) im
  CORREKTUR-LOG dokumentiert statt stillschweigend korrigiert; die
  Messungen trafen die korrigierten Formeln exakt.
- C3 verankert: syn3A (N_eff=1, S=1) → Gate OFF, Kernel feuert nie
  (`syn3a_gate_check`, programmatisch testbar) — in der Zellsim
  wirklos, bewusst.

## Offen

- Kick-Kopplung (was ein Kollaps chemisch bewirkt) HYPOTHESE, nicht
  implementiert — bewusst nicht behauptet.
- Selbst-Audit-Eintrag für OR-KERNEL fehlt noch.

## Status

Abgeschlossen. 213 Tests grün, ruff src/ clean.