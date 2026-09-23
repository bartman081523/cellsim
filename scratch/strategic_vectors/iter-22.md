# iter-22 — VECTOR_OR_KICK_COUPLING

**Verdict: KICK_INERT_BOX_WIDE · Grade: C (OPEN, geschärft) · Status: abgeschlossen (2026-09-23)**

## Frage

Die Kick-Kopplung (was ein OR-Kollaps chemisch bewirkt) ist in orch_or.py
ausdrücklich HYPOTHESE. Falsifizierbarer Kern: der energetische Kanal.
Kann ein Kollaps-Event innerhalb der registrierten C1-Box (N ≤ 1e11,
korreliert) überhaupt ein chemisches Quantum liefern?

## Registrierung (Kurzfassung)

Best-Case zugunsten von Orch-OR: E_kick = e_collective = ħ/τ_OR (gesamte
Selbstenergie, N²), 100 % Lieferung in EIN Zielmode. Adressierbarkeit
(Fluktuations-Dissipation): E_acc ≥ k_B·T — darunter ist der Kick Teil
des thermischen Ensembles, kein Gate. Akkumulation nur im Relaxations-
fenster (großzügig τ_relax ≤ 1e-3 s): E_acc = E_kick·max(1, τ_relax/τ_OR).
Landauer-Bias als zweiter Kanal. Trigger-Zweig (Null-Energie-Selektor) =
unfalsifizierbar (C2-Cap iter-18), nicht buchbar.

## Resultat (Kriterien K1–K5 alle PASS)

- N*(τ_relax): 1e-7 s → 1.744e12 (17.4× über Box); 1e-6 s → 9.81e11
  (9.8×); 1e-3 s → **1.744e11 (1.74× über der Box-Decke 1e11)**.
  τ_relax* = 9.25 ms — jenseits jeder registrierten Schranke.
- Per-Event: R_1 = 1.63e-10 k_B·T (Ecke) bzw. 1.63e-6 (Box-Decke);
  E/ΔG_ATP = 8.4e-12 bzw. 8.4e-8.
- Gate-Map: ohne Schild N ≥ 7.8e11 (außerhalb der Box — der Kick braucht
  das Schild); mit ableitbarem Schild (iter-21: 9.9e3) N ≥ 7.9e9 —
  das Gate ist offen, aber die Energie blockt (N* ≫ N_gate).
- K2 Doppel-Herleitung: worst rel 2.48e-16; K1 Konstanten vs CODATA
  (scipy) < 1e-9.

## Epistemischer Status

- **Kick innerhalb der Box energetisch entwertet** — vom Declared
  (HYPOTHESE) zum Derived: der iter-18-Kernel ist reiner Muster-Generator,
  chemisch wirklos in der registrierten Box.
- **Drei Umschließungen**: Gate braucht Schild (iter-21-liegferbar ok),
  Energie blockt (N* > Hameroff-Decke), Akkumulation jenseits des
  Relaxationsfensters = Kondensat-Typ = REFUTED_BY_REIMERS_2010.
- **Rand ehrlich**: bei τ_relax = 1 ms nur Faktor 1.74 Margin; die Box
  wird bei τ_relax ≥ 9.25 ms erreicht — außerhalb registrierter
  Schranken, aber die Falsifikation ist nicht parameterfrei.
- **Keine volle Orch-OR-Falsifikation**: Kollektive > 1e11, exotische
  Verstärker und der Trigger-Zweig bleiben außerhalb.
- Unverändert: Penrose-Formel, N\*-Gesetz, OR-Kernel-Signatur (C2),
  C3-Gate OFF.

## Nächste Vektoren

1. VECTOR_PHOTONIC_COUPLING_PRODUCTION (superradiance → HybridDriver)
2. VECTOR_WINDOW_REPLICATION_V2 (iter-14-Fenster, korrigierter Sprung-Operator)
3. reserviert iter-19b: VECTOR_SHELL1_CASCADE

Artefakte: `scratch/experiments/iter-22/{kick_budget.py,result.json,experiment.md}`,
`src/cellsim/modules/kick_coupling.py`, `tests/unit/test_kick_coupling.py`.