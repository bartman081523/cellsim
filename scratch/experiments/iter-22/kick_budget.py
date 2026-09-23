#!/usr/bin/env python
"""iter-22 — VECTOR_OR_KICK_COUPLING: Ist der Kick chemisch adressierbar?

VORAB-REGISTRIERUNG (2026-09-23, vor dem Lauf fixiert; Produktion:
src/cellsim/modules/kick_coupling.py, getestet in tests/unit/test_kick_coupling.py)

FRAGE
  iter-18 liefert nur Ereignis-Muster (C2-Cap); die Kick-Kopplung ist in
  orch_or.py ausdrücklich HYPOTHESE. Falsifizierbarer Kern: der
  ENERGETISCHE Kanal. Kann ein OR-Kollaps-Event innerhalb der registrierten
  C1-Box (N ≤ 1e11, f ≤ 5e-2, a ≤ 8 nm, korreliert) überhaupt ein
  chemisches Quantum liefern — oder ist der Kick thermisch inert
  (Entwertung: Kernel bleibt reiner Muster-Generator)?

REGISTRIERTES MODELL (siehe kick_coupling.py-Docstring)
  Best-Case zugunsten von Orch-OR:
    E_kick = e_collective = ħ/τ_OR  (GESAMTE Selbstenergie, korreliert N²)
    Lieferung 100 % in EIN Zielmode, ohne Verlust.
  Adressierbarkeit (Fluktuations-Dissipation): E_acc ≥ 1.0·k_B·T —
    unterhalb k_B·T ist der Kick Teil des thermischen Ensembles, kein Gate
    (Floor ist Physik, kein Tuning-Parameter).
  Akkumulation nur im Relaxationsfenster der Zielmode (größzügig
    τ_relax ≤ 1e-3 s, ms-Übergänge real): E_acc = E_kick·max(1, τ_relax/τ_OR).
  Landauer-Kanal als zweiter Blick: kumulierter Bias im Fenster = E_acc/k_B·T.
  Trigger-Zweig (Null-Energie-Selektor) ist als Physik unfalsifizierbar
    (C2-Cap iter-18) und wird NICHT als Unterstützung gebucht.

Kriterien (VOR dem Lauf fixiert)
  K1 Integrität: Modul-Konstanten vs scipy.constants (CODATA, unabhängig,
     rel ≤ 1e-9); e_single vs registrierter iter-16/18-Anker 6.985e-49
     (rel ≤ 1e-4); τ_OR(Ecke) vs iter-18-Anker 1.5098e-4 (rel ≤ 1e-4);
     e_collective ≡ ħ/τ_OR (zweite explizite Route, rel ≤ 1e-12);
     N*-Formel ≡ numerische Bisektion (rel ≤ 1e-6, im Modul assertiert);
     Branch-A-Bound: für τ_relax ≤ τ_OR(N) gilt E_acc ≡ E_kick.
  K2 (G1) Doppel-Herleitung: E_acc via Produktions-Route (λ = 1/τ_OR aus
     penrose_tau_or_s) vs. rein explizite Route (τ_relax·E²/ħ), rel ≤ 1e-9,
     über (N, τ_relax)-Gitter mit τ_relax > τ_OR — prüft die
     Akkumulations-Logik NICHT gegen sich selbst (iter-19-Lektion).
  K3 (G2) Adressierbarkeit: exists (N ≤ N_BOX_MAX, τ_relax ≤ 1e-3) mit
     E_acc ≥ k_B·T → KICK_ADDRESSABLE; sonst INERT.
  K4 (G3) Gate-Konsistenz: adressierbare Konfigurationen müssen Gate-ON
     erreichen können — mit dem ABLEITBAREN Schild S_max = 9.901e3
     (iter-21, NICHT S=1e6). Registrierter Vergleich: N* < N_gate(S_max)
     wäre Gate-geblockt (separater Verdict-Zusatz); Schild ist bindend,
     falls N_gate(S_max) > N*.
  K5 (G4) Rand-Schärfe: τ_relax*, bei dem N* = N_BOX_MAX exakt erreicht
     wird (registrierte Empfindlichkeit, kein separates Verdict).

Verdict-Namen (alle Erstklass, keine Gesichts-sparende Verzweigung):
  KICK_INERT_BOX_WIDE   — keine in-Box-Konfiguration erreicht k_B·T im
                          Relaxationsfenster
  KICK_ADDRESSABLE      — in-Box adressierbar (Gate-ON mit ableitbarem
                          Schild erreichbar)
  KICK_ADDRESSABLE_S1E6_ONLY — in-Box adressierbar, aber Gate-ON nur mit
                          dem iter-21 falsifizierten Schild S=1e6
  REGISTRATION_ERROR    — K1/K2 verletzt

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import constants as sci_const

from cellsim.modules.kick_coupling import (
    ADDRESSABILITY_KBT_FLOOR,
    DELTA_G_ATP_J,
    N_BOX_MAX,
    REG_E_SINGLE_J,
    TAU_RELAX_GRID_S,
    e_collective_j,
    e_single_j,
    event_rate_per_s,
    gate_min_n_with_shield,
    n_addressable_threshold,
    per_event_thermal_ratio,
    relaxation_window_bias,
    relaxation_window_energy_j,
)
from cellsim.modules.orch_or import (
    G_NEWTON,
    HBAR,
    KB,
    ORConfig,
    penrose_tau_or_s,
)
from cellsim.modules.shielding import (
    EPS_RES_OPTIMISTIC,
    PHI_FREE_FLOOR,
)

HERE = Path(__file__).parent

# Registrierte iter-18-Ankerwerte (aus scratch/experiments/iter-18, NICHT
# hier neu hergeleitet — unabhängiger Anker gegen Produktionscode-Drift)
REG_TAU_OR = 1.5098e-4
# Registriertes ABLEITBARES Schild aus iter-21 (1/(φ_floor + ε_opt))
S_MAX_DERIVED = 1.0 / (PHI_FREE_FLOOR + EPS_RES_OPTIMISTIC)

CORNER = ORConfig()
BOX_CEIL = ORConfig(n_tubulins=N_BOX_MAX)


def verify_registration() -> dict:
    """K1: Integrität — Konstanten vs CODATA, Anker, Doppel-Routen."""
    checks = {}
    # Konstanten gegen scipy.constants (unabhängige CODATA-Herleitung)
    assert abs(HBAR - sci_const.hbar) / sci_const.hbar < 1e-9, "K1 ħ"
    assert abs(KB - sci_const.Boltzmann) / sci_const.Boltzmann < 1e-9, "K1 k_B"
    assert abs(G_NEWTON - sci_const.gravitational_constant) \
        / sci_const.gravitational_constant < 1e-9, "K1 G"
    checks["constants_vs_codata"] = True
    # e_single gegen registrierten Anker
    e_d = e_single_j(CORNER)
    assert abs(e_d - REG_E_SINGLE_J) / REG_E_SINGLE_J < 1e-4, "K1 e_single"
    checks["e_single_anchor"] = e_d
    # τ_OR gegen registrierten iter-18-Wert
    tau_or = penrose_tau_or_s(CORNER)
    assert abs(tau_or - REG_TAU_OR) / REG_TAU_OR < 1e-4, "K1 τ_OR-Anker"
    checks["tau_or_matches_iter18"] = tau_or
    # e_collective ≡ ħ/τ_OR (zweite explizite Route vs Produktionspfad)
    for cfg in (CORNER, BOX_CEIL, ORConfig(n_tubulins=1.0)):
        assert abs(e_collective_j(cfg)
                   - HBAR / penrose_tau_or_s(cfg)) \
            / e_collective_j(cfg) < 1e-12, "K1 E≡ħ/τ"
    checks["e_collective_identity"] = True
    # Branch-A-Bound: τ_relax ≤ τ_OR(N) → E_acc ≡ E_kick
    e_slow = relaxation_window_energy_j(CORNER, 1e-6)  # τ_relax < τ_OR
    assert abs(e_slow - e_collective_j(CORNER)) / e_slow < 1e-12, "K1 Branch-A"
    checks["branch_a_bound"] = True
    # N*-Formel ≡ Bisektion (im Modul assertiert)
    for tau in TAU_RELAX_GRID_S:
        n_addressable_threshold(CORNER, tau)
    checks["n_star_dual"] = True
    return checks


def dual_derivation() -> dict:
    """K2: E_acc via Produktions-Route vs rein explizite Route."""
    rows = []
    worst = 0.0
    for n in (1e10, 5e10, 1e11, 3e11):  # alle im akkumulierenden Zweig
        cfg = ORConfig(n_tubulins=n)
        e = e_collective_j(cfg)
        for tau in TAU_RELAX_GRID_S:
            if tau * event_rate_per_s(cfg) <= 1.0:
                continue  # Branch-A-Zeilen sind K1-abgedeckt
            route_prod = relaxation_window_energy_j(cfg, tau)
            route_expl = tau * e**2 / HBAR
            rel = abs(route_prod - route_expl) / route_expl
            worst = max(worst, rel)
            rows.append({"n": n, "tau_relax": tau, "rel_err": rel})
    return {"rows": rows, "worst_rel_err": worst,
            "pass": bool(worst <= 1e-9)}


def sweep() -> dict:
    """K3/K4: E_acc/k_B·T über der Box; adressierbare Region; Gate-Map."""
    n_grid = np.logspace(6.0, 11.5, 40)
    rows = []
    addressable = []
    for tau in TAU_RELAX_GRID_S:
        for n in n_grid:
            cfg = ORConfig(n_tubulins=float(n))
            ratio = relaxation_window_bias(cfg, tau)
            row = {"tau_relax": tau, "n": float(n), "E_acc_over_kT": ratio,
                   "addressable": ratio >= ADDRESSABILITY_KBT_FLOOR}
            rows.append(row)
            if row["addressable"]:
                addressable.append(row)
    # Schwellwerte pro τ_relax (formal, Bisektion-kontrolliert)
    thresholds = {str(tau): n_addressable_threshold(CORNER, tau)
                  for tau in TAU_RELAX_GRID_S}
    # τ_relax*, das N* exakt an die Box-Decke setzt: N* ∝ τ^(-1/4)
    n_star_1e3 = thresholds["0.001"]
    tau_star = 1e-3 * (n_star_1e3 / N_BOX_MAX) ** 4
    # Gate-Map: kleinstes N für Gate-ON bei verschiedenen Schilden
    gate = {
        "no_shield_S1": gate_min_n_with_shield(CORNER, 1.0),
        "derived_S_max_iter21": gate_min_n_with_shield(CORNER, S_MAX_DERIVED),
        "hypothesis_S1e6": gate_min_n_with_shield(CORNER, 1e6),
    }
    return {"rows": rows, "thresholds": thresholds, "tau_star_box": tau_star,
            "gate_min_n": gate, "n_addressable_rows": len(addressable)}


def verdict(integ: dict, dual: dict, swp: dict) -> str:
    """Registrierte Verdict-Logik (K3/K4) — vor dem Lauf fixiert."""
    if not integ.get("constants_vs_codata") or not integ.get(
            "e_collective_identity") or not dual["pass"]:
        return "REGISTRATION_ERROR"
    # existiert eine in-Box-adressierbare (N ≤ N_BOX_MAX) Konfiguration?
    # thresholds sind N*(τ_relax) — adressierbar ⇔ N* ≤ N_BOX_MAX
    in_box = [t for t in swp["thresholds"].values() if t <= N_BOX_MAX]
    if not in_box:
        return "KICK_INERT_BOX_WIDE"
    # Gate-Konsistenz: mit ableitbarem Schild erreichbar?
    n_gate_derived = swp["gate_min_n"]["derived_S_max_iter21"]
    n_gate_s1e6 = swp["gate_min_n"]["hypothesis_S1e6"]
    n_star_min = min(in_box)
    if n_star_min >= n_gate_derived:
        return "KICK_ADDRESSABLE"
    if n_star_min >= n_gate_s1e6:
        return "KICK_ADDRESSABLE_S1E6_ONLY"
    return "KICK_INERT_BOX_WIDE"


def main() -> None:
    integ = verify_registration()
    print("K1 Integrität:", json.dumps(integ, default=str, indent=1))
    dual = dual_derivation()
    print(f"K2 Doppel-Herleitung: worst rel {dual['worst_rel_err']:.2e} "
          f"({'PASS' if dual['pass'] else 'FAIL'}), {len(dual['rows'])} Zeilen")
    swp = sweep()
    print("\nK3 Adressierbarkeits-Schwellwerte N*(τ_relax) [Box-Decke 1e11]:")
    for tau, n_star in swp["thresholds"].items():
        margin = n_star / N_BOX_MAX
        print(f"  τ_relax = {tau} s: N* = {n_star:.4e}  "
              f"({margin:.2f}× über der Box-Decke)")
    print(f"  τ_relax* (N* = Box-Decke): {swp['tau_star_box']:.4e} s")
    print("\nK4 Gate-Map (kleinstes N für Gate-ON):")
    for k, v in swp["gate_min_n"].items():
        print(f"  {k:24s} N ≥ {v:.4e}")
    print("\nKontext (Ecke N=1e9 / Box-Decke N=1e11):")
    for label, cfg in (("Ecke", CORNER), ("Box-Decke", BOX_CEIL)):
        r1 = per_event_thermal_ratio(cfg)
        print(f"  {label:10s} R_1 = {r1:.4e} k_B·T  "
              f"E/ΔG_ATP = {e_collective_j(cfg) / DELTA_G_ATP_J:.2e}  "
              f"λ = {event_rate_per_s(cfg):.3e} 1/s")
    v = verdict(integ, dual, swp)
    print(f"\nVERDICT: {v}")
    out = {"registration": integ, "dual_derivation": dual,
           "thresholds": swp["thresholds"], "tau_star_box": swp["tau_star_box"],
           "gate_min_n": swp["gate_min_n"],
           "n_addressable_rows": swp["n_addressable_rows"],
           "corner": {"R_1_kBT": per_event_thermal_ratio(CORNER),
                      "E_over_dG_ATP": e_collective_j(CORNER) / DELTA_G_ATP_J,
                      "lambda_per_s": event_rate_per_s(CORNER)},
           "box_ceiling": {"R_1_kBT": per_event_thermal_ratio(BOX_CEIL),
                           "E_over_dG_ATP":
                               e_collective_j(BOX_CEIL) / DELTA_G_ATP_J,
                           "lambda_per_s": event_rate_per_s(BOX_CEIL)},
           "s_max_derived_iter21": S_MAX_DERIVED,
           "verdict": v}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str))
    print("\nresult.json geschrieben.")


if __name__ == "__main__":
    main()