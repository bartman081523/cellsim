#!/usr/bin/env python
"""iter-23 — VECTOR_PHOTONIC_COUPLING_PRODUCTION: Tut der photonische
Kanal in syn3A Photochemie?

VORAB-REGISTRIERUNG (2026-09-23, vor dem Lauf fixiert; Produktion:
src/cellsim/modules/photonic_coupling.py, getestet in
tests/unit/test_photonic_coupling.py + tests/integration/test_photonic_driver.py;
Driver-Wiring: HybridDriver(photonic=...), CLI --superradiance)

FRAGE
  Der photonische Kanal (Trp-Superradianz, Kurian et al. 2024) ist als
  Produktions-Modul an den HybridDriver gekoppelt (iter-23). Falsifizierbarer
  Kern: liefert der Kanal in JCVI-syn3A einen photochemischen Turnover
  INNERHALB des registrierten Damköhler-Fensters — oder ist er
  pump-energetisch entwertet (unterhalb des Fensters)?

REGISTRIERTES MODELL (Best-Case zugunsten des Kanals)
  M1 Substrat: das GESAMTE Zell-Trp (N_trp = 455·340·1.3e-2 = 2011,
     HYPOTHESE-Anker MGENITALIUM-Proxy) in EINEM superradianten Kollektiv.
     Kurian-Substrat (Mikrotubuli-Trp-Gitter, 1e4-1e6 Emitter) existiert in
     syn3A NICHT (Prokaryot) — Gate-Kontext wie C3 in orch_or.
  M2 Pump: 100 % der metabolischen ATP-Hydrolyse → Trp-Anregung (QE=1).
     ATP-Rate 1e6/s (EMParams-Anker), ΔG_ATP = 8.3e-20 J.
  M3 Energieerhaltung: Φ ≤ Φ_cap = P_pump/E_photon. Dicke-N² konzentriert
     Emission in der ZEIT, erzeugt KEINE Energie — Φ_cap ist
     kollektivgrößen-unabhängig. E_photon(280nm) = 7.09e-19 J ≈ 8.5 ΔG_ATP.
  M4 Burst-Lemma: pro Burst absorbiert ein Molekül N·g(r)·σ Photonen
     (ungesättigt); mit f = Φ_cap/N ist der Burst-Route-Turnover ≡
     Φ_cap·g·σ·QY — N kürzt sich; schritt-integrierte Photochemie ist
     burst-invariant (die N²-Peak-Rate ist für die Chemie irrelevant).
  M5 Geometrie: isotrope Punktquelle MIT Absorption
     (superradiance.flux_at_cm2-Konvention).
  M6 Kriterium: Damköhler-Fenster [1e-4, 0.1] pro Molekül pro 1-ms-Schritt
     ⇔ [0.1, 100] 1/s (iter-11/14).

Kriterien (VOR dem Lauf fixiert)
  K1 Integrität: h, c vs scipy CODATA (rel ≤ 1e-9); E_photon Modul vs
     explizit scipy h·c/λ (rel ≤ 1e-9); ΔG_ATP ≡ 50 kJ/mol/N_A via
     scipy N_A (rel ≤ 1e-3); Fenster-Anker [0.1, 100] 1/s; σ/QY/λ
     Anker; N_trp-Identität 455·340·1.3e-2.
  K2 (G1) Doppel-Herleitung: Φ_cap Produktionsroute vs explizite Route
     (atp·ΔG/(sci.h·sci.c/λ)), rel ≤ 1e-9 über (atp, λ)-Gitter; Turnover
     direkte Route vs Threshold-Inversion (eff/Φ*_lo·lo), rel ≤ 1e-9
     über r-Gitter.
  K3 (G2) Burst-Invarianz: ∫I(t)dt numerisch (trapz über sech²-Burst)
     ≡ N Photonen (rel ≤ 1e-6); numerische Burst-Route (Fluence·σ·QY·f)
     ≡ Average-Route (Φ_cap·g·σ·QY), rel ≤ 1e-6 über N-Gitter
     {1, 1e2, 2011, 1e6, 1e9}; Sättigung N·g·σ ≪ 1 (max gebucht).
  K4 (BINDEND) Pump-Cap vs Fenster: Turnover bei den registrierten
     bindenden Distanzen r ∈ {100 nm (Modul-Default), 250 nm
     (syn3A-Zellradius)} → classify_window. Best-Case = r=100 nm.
  K5 (Kontext, nicht bindend) Popp/EM-Anker: Flux bei 1 µm aus Φ_cap
     (mit Absorption) vs EM-Schicht-Referenz 7.96e7 (10 Photonen/s,
     ohne Absorption) — Konventionen explizit gebucht. Produktions-
     Smoke: Driver-Telemetrie ≡ Modul-Raten. Plausibilitäts-Gate:
     Kurian-Substrat in syn3A ABWESEND.

Verdict-Namen (alle erstklass, keine Gesichts-sparende Verzweigung):
  PHOTONIC_CHANNEL_INERT_FOR_SYN3A — Turnover unterhalb des Fensters an
      ALLEN registrierten bindenden Distanzen (best case r=100 nm)
  PHOTONIC_CHANNEL_IN_WINDOW — Turnover im Fenster für mindestens eine
      bindende Distanz
  PHOTONIC_CHANNEL_OVERDRIVE — Turnover oberhalb des Fensters
  REGISTRATION_ERROR — K1/K2/K3 verletzt

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.

KORREKTUR R2 (2026-09-23, nach R1; siehe korrektur_log.md, R1-Ergebnis in
result_r1.json): R1 endete in REGISTRATION_ERROR — K3 enthielt mit N = 1e9
einen Wert AUSSERHALB der in M4 registrierten Lemma-Domäne (N·g·σ = 4.83 ≥ 1
bei r = 100 nm). Fehlregistrierung des Kriteriums, nicht des Modells.
K3v2: Route-Gleichheit über domänen-validen Teil-Gitter {1, 1e2, 2011, 1e6};
Domänen-Grenzen N_sat(r) gebucht; Sättigungs-Schranke analytisch gebucht
(Turnover_sat ≤ (Φ_cap/N)·QY ≤ Average-Route — K4 bleibt globale Best-Case-
Schranke). K1/K2/K4/K5/Verdict-Logik unangetastet.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import constants as sci_const

from cellsim.modules.em import c_light, h_planck
from cellsim.modules.kick_coupling import DELTA_G_ATP_J
from cellsim.modules.photonic_coupling import (
    N_TRP_EST_PER_CELL,
    PhotonicSource,
    classify_window,
    n_trp_estimate,
    pump_cap_photons_per_s,
    window_bounds_per_s,
)
from cellsim.modules.superradiance import (
    ABSORPTION_LENGTH_NM,
    QUANTUM_YIELD_UVC,
    SIGMA_TRP_CM2,
    TAU_SPONTANEOUS_S,
    TRYPTOPHAN_WAVELENGTH_NM,
    dicke_intensity_photons_per_s,
    flux_at_cm2,
    photon_energy_j,
    threshold_aggregate_rate_per_s,
    turnover_per_second,
)

HERE = Path(__file__).parent

# Registrierte Anker (K1)
REG_DELTA_G_ATP_J = 8.3e-20        # iter-22-Anker (~50 kJ/mol)
REG_SIGMA_TRP_CM2 = 1e-17          # iter-15-Anker
REG_QY_UVC = 0.1                   # iter-15-Anker
REG_WAVELENGTH_NM = 280.0          # iter-15-Anker
REG_WINDOW_PER_STEP = (1e-4, 0.1)  # iter-11/14-Anker (dt = 1 ms)
BINDING_DISTANCES_NM = (100.0, 250.0)  # Modul-Default; syn3A-Zellradius

# Produktions-Smoke-Anker: Modul-Raten der Default-Quelle
SRC_DEFAULT = PhotonicSource()


def verify_registration() -> dict:
    """K1: Integrität — Konstanten vs CODATA/scipy, registrierte Anker."""
    checks: dict = {}
    # Planck c: Modul vs scipy (unabhängige CODATA-Herleitung)
    assert abs(h_planck - sci_const.h) / sci_const.h < 1e-9, "K1 h"
    assert abs(c_light - sci_const.c) / sci_const.c < 1e-9, "K1 c"
    checks["constants_vs_codata"] = True
    # E_photon: Modul vs explizite scipy-Route
    e_mod = photon_energy_j(REG_WAVELENGTH_NM)
    e_sci = sci_const.h * sci_const.c / (REG_WAVELENGTH_NM * 1e-9)
    assert abs(e_mod - e_sci) / e_sci < 1e-9, "K1 E_photon"
    checks["e_photon_J"] = e_mod
    # ΔG_ATP ≡ 50 kJ/mol / N_A (zweite Route via scipy N_A)
    dG_sci = 50.0e3 / sci_const.N_A
    assert abs(DELTA_G_ATP_J - dG_sci) / dG_sci < 1e-3, "K1 ΔG_ATP"
    checks["delta_g_atp_matches_50kJmol"] = True
    # Fenster-Anker (pro-Schritt exakt; pro-Sekunde-Skalierung in
    # Float-Toleranz — Division 1e-4/1e-3 ist nicht exakt 0.1)
    assert REG_WINDOW_PER_STEP == (1e-4, 0.1), "K1 Fenster-pro-Schritt"
    lo, hi = window_bounds_per_s(1e-3)
    assert abs(lo - 0.1) < 1e-12 and abs(hi - 100.0) < 1e-9, \
        "K1 Fenster-pro-Sekunde"
    checks["window_per_s"] = (lo, hi)
    # σ/QY/λ-Anker
    assert SIGMA_TRP_CM2 == REG_SIGMA_TRP_CM2, "K1 σ"
    assert QUANTUM_YIELD_UVC == REG_QY_UVC, "K1 QY"
    assert TRYPTOPHAN_WAVELENGTH_NM == REG_WAVELENGTH_NM, "K1 λ"
    # N_trp-Identität
    assert n_trp_estimate() == N_TRP_EST_PER_CELL == 2011, "K1 N_trp"
    checks["n_trp"] = n_trp_estimate()
    return checks


def dual_derivation() -> dict:
    """K2: Φ_cap und Turnover via zweite, unabhängige Route."""
    rows_cap = []
    worst_cap = 0.0
    for atp in (1e5, 1e6, 1e7):
        for lam_nm in (260.0, 280.0, 300.0):
            route_prod = pump_cap_photons_per_s(atp, lam_nm)
            route_sci = atp * DELTA_G_ATP_J / (
                sci_const.h * sci_const.c / (lam_nm * 1e-9)
            )
            rel = abs(route_prod - route_sci) / route_sci
            worst_cap = max(worst_cap, rel)
            rows_cap.append({"atp": atp, "lam": lam_nm, "rel_err": rel})
    rows_turn = []
    worst_turn = 0.0
    for r_nm in (50.0, 100.0, 250.0, 1000.0):
        src = PhotonicSource(target_distance_nm=r_nm)
        direct = src.turnover_at_target_per_s
        lo_star, _ = threshold_aggregate_rate_per_s(
            r_nm=r_nm,
            sigma_cm2=SIGMA_TRP_CM2,
            quantum_yield=QUANTUM_YIELD_UVC,
            absorption_length_nm=ABSORPTION_LENGTH_NM,
        )
        lo_window, _ = window_bounds_per_s(1e-3)
        inverted = src.effective_rate_per_s / lo_star * lo_window
        rel = abs(direct - inverted) / inverted
        worst_turn = max(worst_turn, rel)
        rows_turn.append({"r_nm": r_nm, "rel_err": rel})
    return {"cap": {"rows": rows_cap, "worst": worst_cap},
            "turnover": {"rows": rows_turn, "worst": worst_turn},
            "pass": bool(worst_cap <= 1e-9 and worst_turn <= 1e-9)}


def burst_invariance() -> dict:
    """K3v2 (CORREKTUR R2): Burst-Invarianz IM registrierten Gültigkeitsraum.

    1. ∫I dt ≡ N numerisch (domänen-unabhängig), N ∈ {1, 1e2, 2011, 1e6, 1e9}.
    2. Burst-Route ≡ Average-Route über domänen-valide N ∈ {1, 1e2, 2011,
       1e6} bei r = 100 nm (Assertion N·g·σ < 1 je N).
    3. Domänen-Grenzen N_sat(r) = 1/(g(r)·σ) für r ∈ {100, 250} nm gebucht.
    4. Sättigungs-Schranke: für N ≥ N_sat ist Turnover ≤ (Φ_cap/N)·QY ≤
       Average-Route (globale obere Schranke — Assertion, K4 bleibt bindend).

    Numerik: das Fenster ist pro N auf τ_SR skaliert und um das
    Burst-Zentrum t_delay = τ_SR·ln(max(N,2)) (Modul-Konvention) gelegt;
    Gitter-Abstand ~6.4e-4·τ_SR → Trapez-Fehler ~1e-8 ≪ Toleranz 1e-6.
    """
    # Geometrie-Konvention (Modul): g(r) = flux_at_cm2(1.0, r)
    r_nm = 100.0
    g = flux_at_cm2(1.0, r_nm, ABSORPTION_LENGTH_NM)
    g_250 = flux_at_cm2(1.0, 250.0, ABSORPTION_LENGTH_NM)
    cap = pump_cap_photons_per_s(1.0e6, REG_WAVELENGTH_NM)
    avg_route = cap * g * SIGMA_TRP_CM2 * QUANTUM_YIELD_UVC
    # 1. Normalisierung über das volle Gitter (domänen-unabhängig)
    norm_rows = []
    worst_norm = 0.0
    for n in (1, 100, N_TRP_EST_PER_CELL, 1e6, 1e9):
        rel_norm = _integral_norm(int(n))
        worst_norm = max(worst_norm, rel_norm)
        norm_rows.append({"n": n, "integral_norm_rel": rel_norm})
    # 2. Route-Gleichheit über domänen-validen Teil-Gitter (r = 100 nm)
    rows = []
    worst = 0.0
    max_sat = 0.0
    for n in (1, 100, N_TRP_EST_PER_CELL, 1e6):
        n_int = int(n)
        per_burst = n_int * g * SIGMA_TRP_CM2
        assert per_burst < 1.0, f"K3v2 Domäne: N·g·σ = {per_burst:.2e} >= 1"
        max_sat = max(max_sat, per_burst)
        integral = float(np.trapezoid(
            dicke_intensity_photons_per_s(n_int, _burst_grid(n_int)),
            _burst_grid(n_int)))
        f = cap / n  # pump-konsistente Burst-Rate
        burst_route = f * (integral * g * SIGMA_TRP_CM2) * QUANTUM_YIELD_UVC
        rel = abs(burst_route - avg_route) / avg_route
        worst = max(worst, rel)
        rows.append({"n": n, "f_burst": f, "n_g_sigma": per_burst,
                     "burst_route": burst_route, "avg_route": avg_route,
                     "rel_err": rel})
    # 3. Domänen-Grenzen gebucht
    n_sat = {"r_100nm": 1.0 / (g * SIGMA_TRP_CM2),
             "r_250nm": 1.0 / (g_250 * SIGMA_TRP_CM2)}
    # 4. Sättigungs-Schranke (analytisch): Average-Route ist globale
    #    obere Schranke über alle N (auch N >= N_sat).
    n_over = 1e9
    turnover_sat_upper = (cap / n_over) * QUANTUM_YIELD_UVC
    assert turnover_sat_upper <= avg_route, "K3v2 Schranke verletzt"
    return {"integral_norm_rel": worst_norm, "norm_rows": norm_rows,
            "rows": rows, "worst": worst,
            "max_n_g_sigma_valid": max_sat, "n_sat": n_sat,
            "saturation_note": {
                "n_probe": n_over,
                "linear_prediction_per_burst": n_over * g * SIGMA_TRP_CM2,
                "turnover_upper_bound": turnover_sat_upper,
                "avg_route_global_bound": avg_route},
            "pass": bool(worst_norm <= 1e-6 and worst <= 1e-6
                         and max_sat < 1.0
                         and turnover_sat_upper <= avg_route)}


def _burst_grid(n: int) -> np.ndarray:
    """τ_SR-skaliertes Gitter um das Burst-Zentrum (Modul-Konvention)."""
    tau_sr = TAU_SPONTANEOUS_S / n
    span = tau_sr * (math.log(max(n, 2.0)) + 120.0)
    return np.linspace(-span, span, 400_001)


def _integral_norm(n: int) -> float:
    """Relative Abweichung der numerischen Burst-Normalisierung von N."""
    t = _burst_grid(n)
    integral = float(np.trapezoid(
        dicke_intensity_photons_per_s(n, t), t))
    return abs(integral - n) / n


def sweep() -> dict:
    """K4/K5: Turnover vs Fenster an bindenden Distanzen; Kontext-Anker."""
    rows = []
    for r_nm in (10.0, 50.0, 100.0, 250.0, 1000.0, 10_000.0):
        cap = pump_cap_photons_per_s(1.0e6, REG_WAVELENGTH_NM)
        flux = flux_at_cm2(cap, r_nm, ABSORPTION_LENGTH_NM)
        turn = turnover_per_second(flux)
        lo_star, hi_star = threshold_aggregate_rate_per_s(
            r_nm=r_nm, sigma_cm2=SIGMA_TRP_CM2,
            quantum_yield=QUANTUM_YIELD_UVC,
            absorption_length_nm=ABSORPTION_LENGTH_NM)
        lo, _ = window_bounds_per_s(1e-3)
        rows.append({"r_nm": r_nm, "flux_cm2_s": flux,
                     "turnover_per_s": turn, "class": classify_window(turn),
                     "phi_star_lo": lo_star, "phi_star_hi": hi_star,
                     "margin_below_lo": lo / turn if turn > 0 else float("inf")})
    # ATP-Rate, die das Fenster-Unteres-Band an r=100 nm erreicht
    lo_star_100 = rows[2]["phi_star_lo"]
    p_needed = lo_star_100 * photon_energy_j(REG_WAVELENGTH_NM)
    atp_needed = p_needed / DELTA_G_ATP_J
    # K5 Kontext: Popp/EM-Anker (1 µm, beide Konventionen)
    flux_1um_abs = flux_at_cm2(cap, 1000.0, ABSORPTION_LENGTH_NM)
    flux_1um_noabs = cap / (4.0 * np.pi * (1000.0 * 1e-7) ** 2)
    # K5 Produktions-Smoke: Driver-Telemetrie vs Modul-Raten
    from cellsim.adapters.rdme import RDMEAdapter
    from cellsim.core.time_axis import TimeAxis
    from cellsim.driver.loop import (
        HybridDriver,
        default_chromosome,
        default_membrane,
        default_ode,
    )
    from cellsim.modules.reactions import default_registry

    driver = HybridDriver(
        time_axis=TimeAxis(t_start_s=0.0, t_end_s=0.02, dt_rdme_s=1e-3,
                           dt_ode_s=1e-3),
        rdme=RDMEAdapter(registry=default_registry(), grid_shape=(6, 6, 6)),
        ode=default_ode(),
        chromosome=default_chromosome(seed=49582),
        membrane=default_membrane(),
        sync_interval=10,
        seed=49582,
        photonic=SRC_DEFAULT,
    )
    run = driver.run()
    mod = SRC_DEFAULT.rates()
    smoke = {
        "n_samples": len(run.time_s),
        "driver_photon_rate_per_s": run.photon_rate_per_s[0],
        "module_photon_rate_per_s": mod["photon_rate_per_s"],
        "driver_turnover": run.photochem_turnover_per_s[0],
        "module_turnover": mod["photochem_turnover_per_s"],
        "driver_pump_capped": run.photon_pump_capped[0],
        "consistent": bool(
            run.photon_rate_per_s[0] == mod["photon_rate_per_s"]
            and run.photochem_turnover_per_s[0] == mod["photochem_turnover_per_s"]
            and all(v == mod["photon_rate_per_s"]
                    for v in run.photon_rate_per_s)
        ),
    }
    return {"rows": rows, "phi_star_lo_100": lo_star_100,
            "atp_needed_for_window": atp_needed,
            "atp_margin_over_anchor": atp_needed / 1.0e6,
            "popp_anchor": {"phi_cap": cap, "flux_1um_with_abs": flux_1um_abs,
                            "flux_1um_no_abs": flux_1um_noabs,
                            "em_layer_reference_1um": 10.0 / (
                                4.0 * np.pi * (1000.0 * 1e-7) ** 2),
                            "em_source_rate": 10.0},
            "production_smoke": smoke,
            "n_trp": n_trp_estimate(),
            "n_trp_sigma": N_TRP_EST_PER_CELL * SIGMA_TRP_CM2}


def verdict(integ: dict, dual: dict, burst: dict, swp: dict) -> str:
    """Registrierte Verdict-Logik (K4) — vor dem Lauf fixiert."""
    if (not integ.get("constants_vs_codata") or not dual["pass"]
            or not burst["pass"]):
        return "REGISTRATION_ERROR"
    classes = [r["class"] for r in swp["rows"]
               if r["r_nm"] in BINDING_DISTANCES_NM]
    if all(c == "below" for c in classes):
        return "PHOTONIC_CHANNEL_INERT_FOR_SYN3A"
    if any(c == "in" for c in classes):
        return "PHOTONIC_CHANNEL_IN_WINDOW"
    return "PHOTONIC_CHANNEL_OVERDRIVE"


def main() -> None:
    integ = verify_registration()
    print("K1 Integrität:", json.dumps(integ, default=str, indent=1))
    dual = dual_derivation()
    print(f"K2 Doppel-Herleitung: Φ_cap worst rel {dual['cap']['worst']:.2e}, "
          f"Turnover worst rel {dual['turnover']['worst']:.2e} "
          f"({'PASS' if dual['pass'] else 'FAIL'})")
    burst = burst_invariance()
    sn = burst["saturation_note"]
    print(f"K3v2 Burst-Invarianz: ∫I dt rel {burst['integral_norm_rel']:.2e}, "
          f"Route-rel worst {burst['worst']:.2e}, "
          f"max N·g·σ (domänen-valid) {burst['max_n_g_sigma_valid']:.2e}, "
          f"N_sat(r=100nm) = {burst['n_sat']['r_100nm']:.3e}, "
          f"N_sat(r=250nm) = {burst['n_sat']['r_250nm']:.3e}, "
          f"Sättigungs-Schranke (N={sn['n_probe']:.0e}): "
          f"{sn['turnover_upper_bound']:.2e} ≤ Average-Route "
          f"{sn['avg_route_global_bound']:.2e} "
          f"({'PASS' if burst['pass'] else 'FAIL'})")
    swp = sweep()
    print("\nK4 Turnover vs Fenster (Φ_cap = "
          f"{pump_cap_photons_per_s(1.0e6):.4e} Photonen/s, Best-Case):")
    for r in swp["rows"]:
        print(f"  r = {r['r_nm']:>8.0f} nm: Turnover {r['turnover_per_s']:.3e} 1/s "
              f"→ {r['class']:5s} (Faktor {r['margin_below_lo']:.2e} unter lo)")
    print(f"  Φ*_lo(r=100nm) = {swp['phi_star_lo_100']:.3e} Photonen/s "
          f"→ ATP nötig {swp['atp_needed_for_window']:.3e}/s "
          f"({swp['atp_margin_over_anchor']:.2e}× EMParams-Anker 1e6/s)")
    pa = swp["popp_anchor"]
    print(f"\nK5 Kontext: Φ_cap {pa['phi_cap']:.3e}/s; Flux@1µm "
          f"mit Abs {pa['flux_1um_with_abs']:.3e} / ohne Abs "
          f"{pa['flux_1um_no_abs']:.3e} vs EM-Schicht-Ref "
          f"{pa['em_layer_reference_1um']:.3e} (aus "
          f"{pa['em_source_rate']:.0f} Photonen/s, ohne Abs)")
    ps = swp["production_smoke"]
    print(f"K5 Produktions-Smoke: {ps['n_samples']} Samples, "
          f"Driver ≡ Modul: {ps['consistent']} "
          f"(rate {ps['driver_photon_rate_per_s']:.4e}/s, turnover "
          f"{ps['driver_turnover']:.3e}/s, pump_capped {ps['driver_pump_capped']:.0f})")
    print(f"K5 Inventar: N_trp = {swp['n_trp']} (HYPOTHESE), "
          f"N_trp·σ = {swp['n_trp_sigma']:.2e} ≪ 1 (Sättigung unmöglich); "
          f"Kurian-Substrat (Mikrotubuli) in syn3A ABWESEND (Prokaryot)")
    v = verdict(integ, dual, burst, swp)
    print(f"\nVERDICT: {v}")
    out = {"registration": integ, "dual_derivation": dual,
           "burst_invariance": burst, "sweep": swp,
           "binding_distances_nm": BINDING_DISTANCES_NM, "verdict": v}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str))
    print("\nresult.json geschrieben.")


if __name__ == "__main__":
    main()
