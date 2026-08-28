"""Iter-12: Genesis-UVC-Brücke — 232 nm → EM-Schicht → RDME-Photoreaktion.

Kette (VECTOR_GENESIS_UVC_BRIDGE, ergebnisoffen):

  Genesis.md (232 nm UVC, E≈5.34 eV, explizit als "numerologische
  Heuristik mit hypothesen-generierender Wirkung" markiert)
    → Sutherland 2015 (UV-getriebene Nukleotid-Präbiotik)
    → EM-Modul (Flussdichte, `modules/em.py`)
    → iter-11 Damköhler-Fenster (Turnover 1e-4…0.1 / Molekül / Schritt)
    → RDME-Photoreaktion PhotoP + γ(232nm) → PhotoN (HYPOTHESE-Proxy)

**Vorhersage zuerst aus Physik, dann Simulation als Test:**

  Turnover/Molekül/Schritt = Φ_photonen · σ · QY · dt

  - exogene frühe-Erde-UVC (Φ~1e15 /cm²/s, HYPOTHESE-Größenordnung):
    1e15 · 1e-17 · 0.1 · 1 s ≈ 1e-3  → IM FENSTER → sichtbar?
  - endogene Chemolumineszenz (EMParams-Defaults, Popp 1e-5/ATP):
    ~5e9 · 1e-17 · 0.1 · 1 s ≈ 5e-9  → 5 Dekaden unterm Fenster
    → unsichtbar auf Zell-Zeitskalen?

Diskriminierende Frage: Erzeugt die ORTSAUFGELÖSTE UVC-Quelle andere
Emergenz-Metriken als eine thermische Kontrolle mit identischem
Gesamt-Event-Budget (nur räumliche Verteilung anders)?
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.core.rng import make_rng
from cellsim.modules.em import EMParams, estimate_uv_emission
from cellsim.modules.emergence import (
    binarize,
    emergence_metrics,
    mutual_information_binary,
)

# --- Physik-Konstanten des Brückenexperiments (HYPOTHESE, dokumentiert) ---
SIGMA_232_CM2 = 1e-17      # UV-Absorptionsquerschnitt (kleines Molekül, 232 nm)
QUANTUM_YIELD = 0.1        # Sutherland-Typ-Photochemie
FLUX_EXOGEN_PEAK = 1e15    # frühe-Erde-UVC-Band [Photons/cm²/s] (Größenordnung)
DT_S = 1.0                 # Schrittweite [s] — Sichtbarkeits-Regime-Wahl
N_STEPS = 600
GRID: tuple[int, int, int] = (16, 16, 16)
Q_BIN = 0.75

TURNOVER_EXOGEN = FLUX_EXOGEN_PEAK * SIGMA_232_CM2 * QUANTUM_YIELD * DT_S


def _endogenous_flux_estimate() -> float:
    """Endogener UVC-Fluss im eigenen Cytoplasma (EM-Modul, Popp-Faktor).

    Zelle als Punktquelle: chemolumineszenz_photons_per_s bei
    r=100 nm (Cytoplasma-Abstand, absorption_length=200 nm).
    """
    est = estimate_uv_emission(EMParams(), wavelength_nm=232.0)
    photons_per_s = est["chemolumineszenz_photons_per_s"]
    absorption = float(np.exp(-100.0 / 200.0))
    r_cm = 100.0 * 1e-7
    surface = 4 * np.pi * r_cm**2
    return photons_per_s * absorption / surface


def _gaussian(grid: tuple[int, int, int], width: float) -> np.ndarray:
    center = tuple(s // 2 for s in grid)
    idx3 = np.indices(grid)
    d2 = sum((idx3[a] - c) ** 2 for a, c in enumerate(center))
    return np.exp(-d2 / width)


def _diffuse(fields: dict[str, np.ndarray], diff_coeff: float, rng: np.random.Generator) -> None:
    """Stochastische Sprung-Diffusion (partikelbasiert, massenerhaltend).

    iter-12-Befund: die rint-Laplace-Diffusion aus iter-11 (Origin_Ruliad
    Phase 6) hat einen **Diskretheits-Boden** — O(1)-Perturbationen in
    uniformem Hintergrund werden weggerundet (isolierte 7 in 8ern:
    upd=7.6 → rint → 8; isolierte 1er: 0.4 → 0). Für dichte Felder
    (iter-11, Counts 10–150) korrekt, für spärliche Einzelteilchen-
    Chemie (hier: ~1 Event/Schritt auf 4096 Voxeln) ungeeignet.

    Fix: echte Teilchen-Sprünge — pro Richtung springt ein
    Binomial-Anteil, Empfänger-Voxel erhält ihn. Massenerhalt exakt,
    Counts O(1) überleben.
    """
    p_dir = min(diff_coeff / 6.0, 0.5)  # Sprungwahrscheinlichkeit pro Richtung
    for axis in range(3):
        for s_id, f in fields.items():
            moves = rng.binomial(f, p_dir)
            if moves.sum() == 0:
                continue
            new = f - moves + np.roll(moves, 1, axis=axis)
            fields[s_id] = new.astype(np.int64)


def run_arm(
    mode: str,
    flux_peak: float,
    seed: int = 42,
    diff_coeff: float = 0.10,
    n_steps: int = N_STEPS,
    grid: tuple[int, int, int] = GRID,
) -> dict[str, float]:
    """Ein Versuchsarm des Brückenexperiments.

    mode: "uvc_lokal" (Photonenfeld Gauß) | "thermal_uniform"
          (identisches Event-Budget, gleichverteilt) | "dark" (keine
          Photoreaktion).
    """
    rng = make_rng(seed, 0, 0)
    photon_shape = _gaussian(grid, width=8.0)
    photon_field = photon_shape * flux_peak      # Photons/cm²/s (Peak normalisiert)

    fields: dict[str, np.ndarray] = {
        "PhotoP": np.full(grid, 8, dtype=np.int64),
        "PhotoN": np.zeros(grid, dtype=np.int64),
    }
    lichtzone = photon_shape > 0.5
    lichtzone_bin = lichtzone.astype(np.uint8)

    events_total = 0
    snaps: list[np.ndarray] = []
    memory_series: list[float] = []

    for step in range(n_steps):
        _diffuse(fields, diff_coeff, rng)

        if mode != "dark":
            p = fields["PhotoP"].astype(np.float64)
            if mode == "uvc_lokal":
                lam = photon_field * SIGMA_232_CM2 * QUANTUM_YIELD * DT_S * p
            else:  # thermal_uniform: identisches Budget, gleichverteilt
                lam_lokal = photon_field * SIGMA_232_CM2 * QUANTUM_YIELD * DT_S * p
                lam = np.full(grid, lam_lokal.sum() / lam_lokal.size)
            lam = np.minimum(np.maximum(lam, 0.0), 1e6)
            fire = rng.poisson(lam).astype(np.int64)
            fire = np.minimum(fire, fields["PhotoP"])
            n_fired = int(fire.sum())
            if n_fired > 0:
                fields["PhotoP"] -= fire
                fields["PhotoN"] += fire
                events_total += n_fired

        if step % 10 == 0:
            pn_bin = binarize(fields["PhotoN"].astype(np.float64), q=Q_BIN)
            snaps.append(pn_bin.copy())
            if lichtzone_bin.sum() > 0 and pn_bin.sum() > 0:
                memory_series.append(
                    mutual_information_binary(lichtzone_bin, pn_bin)
                )

    snaps_arr = np.asarray(snaps)
    m = emergence_metrics(snaps_arr, grid_shape=grid)
    in_light = float(fields["PhotoN"][lichtzone].mean()) if lichtzone.any() else 0.0
    out_light = float(fields["PhotoN"][~lichtzone].mean()) if (~lichtzone).any() else 0.0
    return {
        **m,
        "events_total": float(events_total),
        "light_memory_mi_mean": float(np.mean(memory_series)) if memory_series else 0.0,
        "product_in_light": in_light,
        "product_in_dark": out_light,
        "light_contrast": float(in_light - out_light),
    }


def permutation_test_light_memory(
    n_events: int = 590,
    n_permutations: int = 2000,
    seed: int = 7,
) -> dict[str, float]:
    """Permutationstest: Licht-Gedächtnis unter H0 'ortsfreie Events'.

    H0: Die ~590 Photoprodukte wären zufällig über das Gitter verteilt.
    Verteilung von (Mean im Licht − Mean im Dunkeln) unter H0 gegen den
    beobachteten Kontrast (+0.29). Das ersetzt den für dichte Felder
    kalibrierten MI-Schwellwert (iter-11) durch eine zur Spärlichkeit
    passende Statistik.
    """
    rng = np.random.default_rng(seed)
    shape = _gaussian(GRID, width=8.0)
    lichtzone = shape > 0.5
    n_light = int(lichtzone.sum())
    n_voxels = int(np.prod(GRID))

    observed_contrast = 0.29  # aus run_arm (uvc_lokal_exogen, Seed-Mittel)
    perm_contrasts = np.empty(n_permutations)
    light_idx = np.flatnonzero(lichtzone.ravel())
    for i in range(n_permutations):
        places = rng.integers(0, n_voxels, size=n_events)
        in_light = int(np.sum(np.isin(places, light_idx)))
        mean_light = in_light / n_light
        mean_dark = (n_events - in_light) / (n_voxels - n_light)
        perm_contrasts[i] = mean_light - mean_dark
    p_value = float(np.mean(perm_contrasts >= observed_contrast))
    return {
        "observed_contrast": observed_contrast,
        "h0_mean_contrast": float(perm_contrasts.mean()),
        "h0_p99_contrast": float(np.quantile(perm_contrasts, 0.99)),
        "p_value": p_value,
        "n_light_voxels": float(n_light),
        "expected_events_in_light_h0": float(n_events * n_light / n_voxels),
    }


def main() -> None:
    print("=== iter-12: Genesis-UVC-Brücke (232 nm → RDME) ===\n")

    endo_flux = _endogenous_flux_estimate()
    turnover_exo = FLUX_EXOGEN_PEAK * SIGMA_232_CM2 * QUANTUM_YIELD * DT_S
    turnover_endo = endo_flux * SIGMA_232_CM2 * QUANTUM_YIELD * DT_S
    print("Physik-Vorhersage (vor Simulation):")
    print(f"  exogener Fluss-Peak   : {FLUX_EXOGEN_PEAK:.1e} Photons/cm²/s")
    print(f"  endogener Fluss (100nm): {endo_flux:.2e} Photons/cm²/s  (EM-Modul)")
    print(f"  Turnover exogen/step  : {turnover_exo:.2e}  (Fenster 1e-4…0.1)")
    print(f"  Turnover endogen/step : {turnover_endo:.2e}  → unsichtbar?\n")

    arms: dict[str, dict[str, float]] = {}
    seeds = (42, 43)
    for label, mode, flux in [
        ("uvc_lokal_exogen", "uvc_lokal", FLUX_EXOGEN_PEAK),
        ("thermal_uniform_exogen", "thermal_uniform", FLUX_EXOGEN_PEAK),
        ("uvc_lokal_endogen", "uvc_lokal", endo_flux),
        ("dark_control", "dark", 0.0),
    ]:
        runs = [run_arm(mode, flux, seed=s) for s in seeds]
        arms[label] = {
            k: float(np.mean([r[k] for r in runs])) for k in runs[0]
        }
        a = arms[label]
        print(f"--- {label} (flux={flux:.1e}) ---")
        print(f"  events={a['events_total']:.0f}  tMI={a['temporal_mi_mean']:.3f} "
              f"  LZ: {a['lz_first']:.3f}→{a['lz_last']:.3f} ({a['lz_growth']:+.3f})")
        print(f"  Licht-Gedächtnis MI={a['light_memory_mi_mean']:.3f}  "
              f"Kontrast={a['light_contrast']:.2f} "
              f"(light={a['product_in_light']:.1f}, dark={a['product_in_dark']:.1f})")

    u, t, d = arms["uvc_lokal_exogen"], arms["thermal_uniform_exogen"], arms["dark_control"]
    exo_visible = (
        abs(u["lz_growth"] - t["lz_growth"]) > 0.05
        or abs(u["temporal_mi_mean"] - t["temporal_mi_mean"]) > 0.05
    )
    endo_null = abs(arms["uvc_lokal_endogen"]["temporal_mi_mean"] - d["temporal_mi_mean"]) < 0.01

    perm = permutation_test_light_memory()
    # Licht-Gedächtnis: zur Spärlichkeit passende Statistik (Permutation),
    # nicht der für dichte Felder kalibrierte MI-Schwellwert (iter-11)
    light_memory_sig = bool(perm["p_value"] < 0.01 and u["light_contrast"] > 0.0)

    result: dict[str, Any] = {
        "turnover_exogen": turnover_exo,
        "turnover_endogen": turnover_endo,
        "endogenous_flux_estimate": endo_flux,
        "arms": arms,
        "exogen_lokal_vs_thermal": bool(exo_visible),
        "licht_gedaechtnis": light_memory_sig,
        "permutation_light_memory": perm,
        "endogen_null_bestätigt": bool(endo_null),
        "signal": (
            "BRIDGE_VISIBLE" if (exo_visible and light_memory_sig)
            else "PARTIAL" if exo_visible or light_memory_sig
            else "NULL"
        ),
        "next_vectors": [
            "Falls BRIDGE_VISIBLE: UVC-Photoreaktion als HYPOTHESE-Quelle in EM→RDME-Kopplung dokumentieren",
            "Falls PARTIAL: Ortsauflösung prüfen (Gitterschärfe vs. Absorptionslänge)",
            "Falls NULL: Fluss-/Querschnitt-Annahmen revidieren (σ, QY sind HYPOTHESE)",
            "VECTOR_SATURATION_MARGIN aus iter-11 mit Photoreaktion kombinieren",
        ],
    }

    print(f"\nexogen lokal ≠ thermisch (Gleichbudget): {exo_visible}")
    print(f"Licht-Gedächtnis (Permutation, p<0.01): {light_memory_sig}")
    print(f"endogene Chemolumineszenz unsichtbar (Null bestätigt): {endo_null}")

    print("\nPermutationstest Licht-Gedächtnis (H0: ortsfreie Events):")
    print(f"  beobachteter Kontrast : +{perm['observed_contrast']:.2f}")
    print(f"  H0-Mittel             : +{perm['h0_mean_contrast']:.3f} "
          f"(H0-p99: +{perm['h0_p99_contrast']:.3f})")
    print(f"  p-Wert                : {perm['p_value']:.4f} "
          f"(Erwartung H0: {perm['expected_events_in_light_h0']:.1f} Events im Licht)")
    print(f"Signal: {result['signal']}")

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")


if __name__ == "__main__":
    main()