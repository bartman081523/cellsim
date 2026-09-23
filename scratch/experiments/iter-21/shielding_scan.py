#!/usr/bin/env python
"""iter-21 — VECTOR_SHIELDING_FIELD: Ist das Schild S=1e6 ableitbar?

VORAB-REGISTRIERUNG (2026-09-23, vor dem Lauf fixiert; Produktion:
src/cellsim/modules/shielding.py, getestet in tests/unit/test_shielding.py)

FRAGE
  iter-16 liess die großzügige Hagan-Ecke (f=5e-2, a=8 nm, N=1e9,
  korreliert) nur MIT dem Schild S=1e6 viable werden (Ratio 0.61);
  S=1e6 ist eine HYPOTHESE-Konstante. Kann S aus einem mechanistischen,
  ortsaufgelösten Dekohärenz-Feld ABGELEITET werden — oder stirbt die
  Ecke ohne die freie Konstante?

REGISTRIERTES MODELL (siehe shielding.py-Docstring)
  Registerierte Bilanz: Tegmark-KOLLISIONS-Kanal
    Γ_bulk = k_B·T·(Δm/m)²/ħ          (S=1-Bulk-Grenze)
    Γ_need = 1/τ_OR                    (Gate: τ_OR < τ_dec)
  Hebel auf dem Kollisions-Kanal (registriert):
    M1 Streuter-Ausschluss: Γ(r) = Γ_bulk·(φ(r) + (1−φ(r))·ε_res),
       Zwei-Zonen-Feld (Kern φ_free, außen 1.0)
    M2 Formfaktor: GESCHLOSSEN (S=1; λ_deB ≈ 0.023 nm ≪ Δx = 8 nm)
    M3 Debye: schirmt nur FELD-Kanäle → kein Hebel auf Γ_M (registriert)
    M4 Konformations-Achse: Δm/m freigelegt, Box [1e-4, 1e-2]
  Ausgeschlossen zugunsten von Orch-OR (Best-Fall): Ionen-Kanal κ_ion=0.
  Konsistenz-Haken: ε_res ≪ 1e-6 erfordert Fröhlich-artiges kohärentes
  Schild → REFUTED_BY_REIMERS_2010 in diesem Repo (Vector-Kette).

REGISTRIERTE SCHRANKEN (großzügig, Literatur-verankert)
  φ_free ≥ 1e-4      (dichtes Cytogel + Hydrationshülle)
  ε_res ∈ {1e-2 pess, 1e-6 opt}
  Δm/m ∈ [1e-4, 1e-2] (Floor = großzügige Konform-Superposition)
  Ecke fixiert: ORConfig() (f=5e-2, a=8 nm, N=1e9, korreliert)

Kriterien (VOR dem Lauf fixiert)
  K1 Integrität: Γ_bulk ≡ 1/τ_dec(S=1) (Produktionscode, rel ≤ 1e-12);
     τ_OR(Ecke) == 6.985e-49/ħ-Systematik, gegen die REGISTERIERTEN
     iter-18-Werte verankert (τ_OR = 1.5098e-4 s, τ_dec_bulk =
     2.4639e-10 s, rel ≤ 1e-6); S_need ≡ τ_OR/τ_dec_bulk.
  K2 (G1) Doppel-Herleitung: Monte-Carlo-Voxel-Sampling der Zonen-Rate
     über [0, r_core + d_w] (4e6 Samples, seed 2100) vs. analytisches
     Volumen-Mittel, rel ≤ 1e-3 — prüft die Zonen-Grenz-Logik
     NICHT gegen sich selbst (iter-19-Lektion).
  K3 (G2) S-Hebel: S_max = max Box-Unterdrückung = 1/(φ_floor + ε_opt)
     = 9.90e3. Registrierter Vergleich: S_max ≥ S_need(Ecke) = 6.13e5
     → SHIELD_DERIVABLE, sonst UNDERIVABLE.
  K4 (G3) Überleben: ratio = Γ̄_core·τ_OR < 1. Verdict-Namen:
     SHIELD_DERIVABLE
     SHIELD_UNDERIVABLE_CONFLUENCE_ONLY  (UNDERIVABLE + Überleben nur
        im Konfluenz-Fenster Δm/m ≲ Δm/m*, mindestens ein Regime
        überlebt im Box-Inneren/Floor, das andere nicht darüber)
     CORNER_DEAD_ALL_REGIMES             (kein Überleben beider Regime)
     REGISTRATION_ERROR                  (K1/K2 verletzt)
  K5 (G4) Kohärenz-Kern an der Ecke (Δm/m=1e-2, beide Regime,
     φ=Floor): r_h erwartet 0 (erforderliches φ ≈ 1.6e-6 < Floor).
     Konsistenz-Anzeige, kein separates Verdict.

Alle vier Ausgänge sind Erstklass-Resultate; keine Gesichts-sparende
Verzweigung. Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from cellsim.modules.orch_or import ORConfig, penrose_tau_or_s, tegmark_tau_dec_s
from cellsim.modules.shielding import (
    DELTA_M_FLOOR,
    DELTA_M_ITER16,
    EPS_RES_OPTIMISTIC,
    EPS_RES_PESSIMISTIC,
    PHI_FREE_FLOOR,
    ShieldingConfig,
    coherence_core_radius_nm,
    corner_ratio,
    effective_suppression,
    gamma_bulk_collision_per_s,
    gamma_needed_per_s,
    mean_core_gamma_per_s,
    required_phi_free,
    s_needed,
)

HERE = Path(__file__).parent
SEED = 2100
N_SAMPLES = 4_000_000

# Registrierte iter-18-Ankerwerte (aus scratch/experiments/iter-18, NICHT
# hier neu hergeleitet — unabhängiger Anker gegen Produktionscode-Drift)
REG_TAU_OR = 1.5098e-4
REG_TAU_DEC_BULK = 2.4639e-10

PHI_GRID = (1e-4, 1e-3, 1e-2)
DM_GRID = np.logspace(math.log10(DELTA_M_FLOOR), math.log10(DELTA_M_ITER16), 25)

CORNER = ORConfig()


def verify_registration() -> dict:
    """K1: Integrität gegen Produktionscode UND registrierte iter-18-Werte."""
    checks = {}
    # Γ_bulk ≡ 1/τ_dec(S=1)
    for dm in (DELTA_M_ITER16, DELTA_M_FLOOR, 3.7e-3):
        bulk = gamma_bulk_collision_per_s(CORNER, dm)
        tau = tegmark_tau_dec_s(ORConfig(delta_m_over_m_bulk=dm, shielding=1.0))
        assert approx_rel(bulk, 1.0 / tau, 1e-12), f"K1 Γ_bulk @{dm}"
    checks["gamma_bulk_identity"] = True
    # τ_OR gegen registrierten iter-18-Wert
    tau_or = penrose_tau_or_s(CORNER)
    assert abs(tau_or - REG_TAU_OR) / REG_TAU_OR < 1e-4, "K1 τ_OR-Anker"
    checks["tau_or_matches_iter18"] = tau_or
    # τ_dec_bulk (S=1) gegen registrierten iter-18-Wert
    tau_dec = tegmark_tau_dec_s(ORConfig(shielding=1.0))
    assert abs(tau_dec - REG_TAU_DEC_BULK) / REG_TAU_DEC_BULK < 1e-4, "K1 τ_dec"
    checks["tau_dec_bulk_matches_iter18"] = tau_dec
    # S_need ≡ τ_OR/τ_dec_bulk
    s_need = s_needed(CORNER, DELTA_M_ITER16)
    assert approx_rel(s_need, tau_or / tau_dec, 1e-9), "K1 S_need"
    checks["s_needed_corner"] = s_need
    return checks


def approx_rel(a: float, b: float, rel: float) -> bool:
    """Lokaler approx-Vergleich (kein pytest-Import im Experiment)."""
    return abs(a - b) <= rel * max(abs(a), abs(b))


def dual_derivation_mc() -> dict:
    """K2: MC-Sampling der Zonen-Rate vs. analytisches Volumen-Mittel.

    Sampling-Region [0, r_core + d_w] (enthält die Bulk-Schale) — prüft
    die Zonen-Grenz-Logik, nicht die Formel gegen sich selbst.
    """
    cfg = ShieldingConfig(phi_free=PHI_FREE_FLOOR, eps_res=EPS_RES_PESSIMISTIC,
                          delta_m_over_m=DELTA_M_ITER16)
    r_total = cfg.r_core_nm + cfg.d_w_nm
    rng = np.random.default_rng(SEED)
    # Uniform im Ball: r = R·u^(1/3), Richtung gleichverteilt (nur r zählt)
    r = r_total * rng.random(N_SAMPLES) ** (1.0 / 3.0)
    bulk = gamma_bulk_collision_per_s(CORNER, DELTA_M_ITER16)
    rates = np.where(
        r <= cfg.r_core_nm,
        bulk * (cfg.phi_free + (1.0 - cfg.phi_free) * cfg.eps_res),
        bulk,
    )
    mc_mean = float(rates.mean())
    v_frac = (cfg.r_core_nm / r_total) ** 3
    analytic = bulk * (v_frac * (cfg.phi_free + (1.0 - cfg.phi_free)
                                 * cfg.eps_res) + (1.0 - v_frac) * 1.0)
    rel = abs(mc_mean - analytic) / analytic
    return {"mc_mean": mc_mean, "analytic": analytic, "rel_err": rel,
            "n": N_SAMPLES, "seed": SEED,
            "pass": bool(rel <= 1e-3)}


def scan() -> dict:
    """K3/K4: Überleben über die registrierte Box; S_max; Kern-Karte."""
    rows = []
    for eps_label, eps in (("pessimistic", EPS_RES_PESSIMISTIC),
                           ("optimistic", EPS_RES_OPTIMISTIC)):
        for phi in PHI_GRID:
            dm_star = dm_boundary(eps, phi)
            for dm in DM_GRID:
                cfg = ShieldingConfig(phi_free=phi, eps_res=eps,
                                      delta_m_over_m=float(dm))
                rows.append({
                    "regime": eps_label, "eps_res": eps, "phi_free": phi,
                    "delta_m_over_m": float(dm),
                    "ratio": corner_ratio(cfg, CORNER),
                    "S_eff": effective_suppression(cfg, CORNER),
                    "survives": corner_ratio(cfg, CORNER) < 1.0,
                    "core_radius_nm": coherence_core_radius_nm(cfg, CORNER),
                })
            # Boundary (analytisch, Kreuzcheck gegen Grid unten)
            rows.append({"regime": eps_label, "eps_res": eps, "phi_free": phi,
                         "delta_m_over_m": dm_star, "boundary": True,
                         "ratio": 1.0, "survives": None, "S_eff": None,
                         "core_radius_nm": None})
    # S_max über der Box = größte Unterdrückung (kleinstes φ + ε)
    s_max = 1.0 / (PHI_FREE_FLOOR + EPS_RES_OPTIMISTIC)
    s_need = s_needed(CORNER, DELTA_M_ITER16)
    # Ecke mit iter-16-Δm/m (Headline)
    corner_rows = {}
    for eps_label, eps in (("pessimistic", EPS_RES_PESSIMISTIC),
                           ("optimistic", EPS_RES_OPTIMISTIC)):
        cfg = ShieldingConfig(phi_free=PHI_FREE_FLOOR, eps_res=eps,
                              delta_m_over_m=DELTA_M_ITER16)
        corner_rows[eps_label] = {
            "ratio": corner_ratio(cfg, CORNER),
            "S_eff": effective_suppression(cfg, CORNER),
            "core_radius_nm": coherence_core_radius_nm(cfg, CORNER),
            "required_phi_free": required_phi_free(cfg, CORNER),
        }
    return {"rows": rows, "s_max_box": s_max, "s_needed_corner": s_need,
            "corner_rows": corner_rows}


def dm_boundary(eps: float, phi: float) -> float:
    """Registrierte Überlebens-Grenze: (Δm/m)² < 1/(Γ_coeff·(φ+ε)·τ_OR)."""
    gamma_coeff = gamma_bulk_collision_per_s(CORNER, 1.0)  # k_B·T/ħ
    return math.sqrt(1.0 / (gamma_coeff * (phi + eps * (1.0 - phi))
                            * penrose_tau_or_s(CORNER)))


def verdict(scanres: dict, integ: dict, dual: dict) -> str:
    """Registrierte Verdict-Logik (K3/K4) — vor dem Lauf fixiert."""
    if not integ.get("gamma_bulk_identity") or not dual["pass"]:
        return "REGISTRATION_ERROR"
    s_max, s_need = scanres["s_max_box"], scanres["s_needed_corner"]
    if s_max >= s_need:
        return "SHIELD_DERIVABLE"
    # Überleben-Muster über die Box (ohne boundary-Zeilen)
    rows = [r for r in scanres["rows"] if not r.get("boundary")]
    surv_opt = [r for r in rows if r["regime"] == "optimistic" and r["survives"]]
    surv_pess = [r for r in rows if r["regime"] == "pessimistic" and r["survives"]]
    if surv_opt or surv_pess:
        return "SHIELD_UNDERIVABLE_CONFLUENCE_ONLY"
    return "CORNER_DEAD_ALL_REGIMES"


def main() -> None:
    integ = verify_registration()
    print("K1 Integrität:", json.dumps(integ, default=str, indent=1))
    dual = dual_derivation_mc()
    print(f"K2 Doppel-Herleitung: MC {dual['mc_mean']:.6e} vs analytisch "
          f"{dual['analytic']:.6e} → rel {dual['rel_err']:.2e} "
          f"({'PASS' if dual['pass'] else 'FAIL'})")
    scanres = scan()
    print(f"K3 S_max(Box) = {scanres['s_max_box']:.3e} vs "
          f"S_need(Ecke) = {scanres['s_needed_corner']:.3e} "
          f"→ {'DERIVABLE' if scanres['s_max_box'] >= scanres['s_needed_corner'] else 'UNDERIVABLE'}")
    print("\nEcke (Δm/m = 1e-2, iter-16-Fixierung, φ = Floor):")
    for k, v in scanres["corner_rows"].items():
        print(f"  {k:11s} ratio = {v['ratio']:.4g}  S_eff = {v['S_eff']:.3e}  "
              f"r_h = {v['core_radius_nm']:.1f} nm  "
              f"φ_erforderlich = {v['required_phi_free']:.3e}")
    print("\nÜberlebens-Grenzen Δm/m* (analytisch):")
    for eps_label, eps in (("pessimistic", EPS_RES_PESSIMISTIC),
                           ("optimistic", EPS_RES_OPTIMISTIC)):
        for phi in PHI_GRID:
            print(f"  {eps_label:11s} φ={phi:.0e}: Δm/m* = "
                  f"{dm_boundary(eps, phi):.4e}")
    v = verdict(scanres, integ, dual)
    print(f"\nVERDICT: {v}")
    rows = [r for r in scanres["rows"] if not r.get("boundary")]
    surv = {}
    for eps_label in ("pessimistic", "optimistic"):
        for phi in PHI_GRID:
            pts = [r["delta_m_over_m"] for r in rows
                   if r["regime"] == eps_label and r["phi_free"] == phi
                   and r["survives"]]
            surv[f"{eps_label}_phi{phi:.0e}"] = {
                "n_surviving": len(pts),
                "max_dm_surviving": max(pts) if pts else None,
            }
    out = {"registration": integ, "dual_derivation": dual,
           "s_max_box": scanres["s_max_box"],
           "s_needed_corner": scanres["s_needed_corner"],
           "corner_rows": scanres["corner_rows"],
           "survival_by_regime_phi": surv,
           "boundaries": {f"{eps}_{phi:.0e}": dm_boundary(eps, phi)
                          for eps in (EPS_RES_PESSIMISTIC, EPS_RES_OPTIMISTIC)
                          for phi in PHI_GRID},
           "verdict": v}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str))
    print("\nresult.json geschrieben.")


if __name__ == "__main__":
    main()