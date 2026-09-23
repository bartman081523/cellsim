# iter-22 — VECTOR_OR_KICK_COUPLING: Ist der Kick chemisch adressierbar?

**Status: ABGESCHLOSSEN (2026-09-23) · Verdict: KICK_INERT_BOX_WIDE · Grade: C (OPEN, geschärft)**

Vorab-Registrierung: `kick_budget.py`-Docstring (vor dem Lauf fixiert);
Produktionsmodul `src/cellsim/modules/kick_coupling.py` (11 Unit-Tests,
Invarianzen ohne Ergebnis-Buchung); `ruff check src/` clean.

---

## 1. Frage

iter-18 liefert nur Ereignis-Muster (C2-Cap); die Kick-Kopplung ist in
`orch_or.py` ausdrücklich HYPOTHESE ("Kick-Größe/-Richtung ist hier NICHT
modelliert"). Falsifizierbarer Kern der Hypothese ist der ENERGETISCHE
Kanal: Kann ein OR-Kollaps-Event innerhalb der registrierten C1-Box
(N ≤ 1e11, f ≤ 5e-2, a ≤ 8 nm, korreliert) überhaupt ein chemisches
Quantum liefern — oder ist der Kick thermisch inert (Entwertung: der
Kernel bleibt reiner Muster-Generator)?

## 2. Registriertes Modell (Kurzfassung; voll im Modul-/Skript-Docstring)

BEST-CASE zugunsten von Orch-OR: E_kick = e_collective = ħ/τ_OR (GESAMTE
Selbstenergie, korreliert N² = größtmögliches Budget), Lieferung zu 100 %
in EIN Zielmode, ohne Verlust.

- **Adressierbarkeit (Fluktuations-Dissipation)**: eine Mode bei 310 K
  fluktuiert selbst mit ~k_B·T; ein Kick unterhalb k_B·T ist für die
  Chemie selbst nicht von einer thermischen Fluktuation unterscheidbar —
  er ist Teil des Ensembles, kein Gate. Floor: E_acc ≥ 1.0·k_B·T
  (Physik, kein Tuning-Parameter).
- **Akkumulation nur im Relaxationsfenster**: Schläge, die langsamer
  eintreffen als die Mode thermalisiert, akkumulieren nicht — sie werden
  Wärme (Thermostat-klamppt). Großzügig: τ_relax ≤ 1e-3 s (ms-Übergänge
  existieren real); Konvention E_acc = E_kick·max(1, τ_relax/τ_OR).
- **Landauer-Kanal** (zweiter Blick): kumulierter Rate-Bias im Fenster
  = E_acc/k_B·T — dasselbe Kriterium, zweite Sicht.
- **Trigger-Zweig**: Null-Energie-Selektor = als Physik unfalsifizierbar
  (operationell ununterscheidbar von Stochastic-Seeding, C2-Cap iter-18);
  NICHT als Unterstützung buchbar. Der falsifizierbare Rest der
  Kick-Hypothese ist exakt der hier analysierte Energiekanal.

## 3. Kriterien (K1–K5, vor dem Lauf fixiert)

| Kriterium | Messung | Status |
|---|---|---|
| K1 Konstanten vs scipy.constants (CODATA, unabhängig) | ħ, k_B, G: rel < 1e-9 | PASS |
| K1 e_single vs iter-16/18-Anker 6.985e-49 | 6.98486e-49 | PASS |
| K1 τ_OR(Ecke) vs iter-18-Anker 1.5098e-4 | 1.50980e-4 | PASS |
| K1 e_collective ≡ ħ/τ_OR (zweite explizite Route) | rel < 1e-12 (N = 1, 1e9, 1e11) | PASS |
| K1 Branch-A-Bound (τ_relax ≤ τ_OR → E_acc ≡ E_kick) | rel < 1e-12 | PASS |
| K1 N*-Formel ≡ numerische Bisektion | rel ≤ 1e-6 (im Modul assertiert) | PASS |
| K2 Doppel-Herleitung E_acc (Produktions-λ vs rein explizit τ·E²/ħ) | worst rel **2.48e-16** (10 Zeilen) | PASS |

## 4. Ergebnis

**K3 — keine in-Box-Konfiguration ist adressierbar:**

| τ_relax | N* (E_acc = k_B·T) | Abstand zur Box-Decke (1e11) |
|---|---|---|
| 1e-7 s | 1.744e12 | **17.4× darüber** |
| 1e-6 s | 9.807e11 | **9.8× darüber** |
| 1e-3 s | 1.744e11 | **1.74× darüber** |

τ_relax*, das die Box-Decke exakt erreicht: **9.25e-3 s** — d. h. erst mit
~9-ms-Relaxationsmodes UND N = 1e11 exakt an der Hameroff-Grenze würde
das Kriterium greifen; jenseits jeder registrierten großzügigen Schranke.

**Per-Event-Hierarchie (Kontext):**

| | R_1 = E/k_B·T | E/ΔG_ATP | λ |
|---|---|---|---|
| Ecke (N=1e9) | **1.63e-10** | 8.4e-12 | 6.6e3 1/s |
| Box-Decke (N=1e11) | **1.63e-6** | 8.4e-8 | 6.6e7 1/s |

Ein einzelnes Event liegt 10 (Ecke) bzw. 6 (Decke) Größenordnungen unter
einem thermischen Quantum und 12 bzw. 8 unter EINEM ATP.

**K4 — Gate-Map (kleinstes N für Gate-ON):**

| Schild | N_gate | vs. Box-Decke |
|---|---|---|
| kein (S=1) | 7.83e11 | außerhalb der Box |
| ableitbar (iter-21: S_max = 9.901e3) | **7.87e9** | innerhalb |
| HYPOTHESE (S=1e6) | 7.83e8 | innerhalb |

Das ableitbare Schild öffnet das Gate ab N ≥ 7.9e9 — **das Schild ist
NICHT der bindende Faktor; die Energie ist es** (N* = 1.74e11 ≫ N_gate).

## 5. Verdict

**KICK_INERT_BOX_WIDE** (registrierte Logik: kein (N ≤ 1e11, τ_relax ≤
1e-3)-Punkt erreicht k_B·T im Relaxationsfenster; Gate mit ableitbarem
Schild erreichbar, also nicht bindend). Alle Kriterien PASS; kein
REGISTRATION_ERROR.

## 6. Interpretation (was sich ändert — und was nicht)

- **Die Kick-Kopplung ist innerhalb der registrierten Box energetisch
  entwertet.** Selbst BEST-CASE (gesamte Selbstenergie, 100 % Lieferung
  in eine Mode, ms-Relaxationsfenster, akkumulierend) bleibt der Kick in
  der Box unterhalb EINER thermischen Fluktuation der Zielmode. Die
  iter-18-Konsequenz verschärft sich vom Declared (HYPOTHESE) zum
  Derived: der OR-Kernel ist ein reiner Muster-Generator — die
  Ereignis-Muster sind Modell-Diskrimination (C2-Cap), chemisch WIRKLOS
  innerhalb der Box.
- **Rand-Schärfe ehrlich gebucht**: beim äußersten großzügigen
  τ_relax = 1 ms beträgt der Abstand nur 1.74×; die Box-Grenze wird bei
  τ_relax ≥ 9.25 ms erreicht. Die Falsifikation ist also nicht
  parameterfrei — sie hängt an (τ_relax, N) und ist für alle registrierten
  Werte (µs–ms-Modes, N ≤ 1e11 = Hameroff-Obergrenze) geschlossen.
  Adressierbarkeit außerhalb der Box verlangt Kollektive jenseits der
  Hameroff-Grenze.
- **Ketten-Konsistenz (drei Umschließungen)**: (a) Gate-ON ohne Schild
  verlangt N ≥ 7.8e11 — der Kick-Kanal BRAUCHT das Schild; mit dem
  ableitbaren Schild (iter-21) ist das Gate offen, aber die Energie
  blockt. (b) Adressierbarkeit verlangt N ≥ 1.74e11 > Hameroff-Decke.
  (c) Akkumulation ÜBER Relaxationsfenster hinweg (Sekunden–Minuten,
  die allein die Aggregate über k_B·T heben würden) ist ein
  Kondensat-Typ-Mechanismus — REFUTED_BY_REIMERS_2010. Das Kick-Szenario
  ist von allen drei Seiten umschlossen, wie das Schild-Szenario in
  iter-21.
- **Trigger-Zweig bleibt, bleibt unfalsifizierbar**: ein Null-Energie-
  Selektor ist operationell ununterscheidbar von Stochastic-Seeding —
  das ist genau der iter-18 C2-Cap. Er wird NICHT als Unterstützung
  gebucht; die falsifizierbare Kick-Hypothese (Energiekanal) ist in-Box
  tot.
- **Unverändert bleiben**: Penrose-Formel, N\*-Gesetz, OR-Kernel-Signatur
  (C2), C3 (syn3A-Gate OFF, N_eff = 1 — syn3A hat nicht einmal die Ecke,
  geschweige denn 1e11-Tubulin-Kollektive).

## 7. CORREKTUR-LOG (alles vor Dateneingang; nichts post-hoc)

- **(a) Test-Validierungs-Irrtum vor dem Experiment**: `ORConfig(n_tubulins=0.5)`
  wirft beim Bau KEIN ValueError (Validierung greift erst in
  `penrose_tau_or_s`); der Test wurde auf den Funktionsaufruf umgestellt.
  Modul-Mathematik unberührt.
- **(b) Lint**: ruff --fix (Import-Sortierung, Trailing-Newlines,
  Yoda-Bedingungen → `math.isclose`). Keine inhaltlichen Änderungen.
- **(c) Manuelle N\*-Schätzung im Entwurf (τ_relax = 1e-6 → 3.1e11) war
  falsch** (Potenz-Rechenfehler); der Fehler wurde NIE gebucht oder für
  ein Verdict benutzt — die registrierte Formel + Bisektion im Modul
  liefern 9.807e11, analytisch und numerisch konsistent (rel ≤ 1e-6).

## 8. Nächste Vektoren (Priorität unverändert)

1. **VECTOR_PHOTONIC_COUPLING_PRODUCTION** — superradiance als EMSource in
   den HybridDriver (Muster existiert in `driver/integration.py`).
2. **VECTOR_WINDOW_REPLICATION_V2** — iter-14-Fenster mit korrigiertem
   Sprung-Operator re-replizieren (Basis des N\*-Gesetzes).
3. reserviert: **iter-19b VECTOR_SHELL1_CASCADE** (Turing-Schale-1-Anomalie).

## Artefakte

- `kick_budget.py` — Vorab-Registrierung + Lauf (K1–K5, Verdict-Logik)
- `result.json` — Integrität, Doppel-Herleitung, Schwellwerte, Gate-Map, Verdict
- Produktion: `src/cellsim/modules/kick_coupling.py` + `tests/unit/test_kick_coupling.py`