"""iter-25 — VECTOR_SATURATION_MARGIN: Wie weit ist das nominale kinetische
Regime von der Sättigungs-Kante entfernt?

VORAB-REGISTRIERUNG (2026-09-23, vor dem Lauf fixiert)

FRAGE
  iter-11/14 definieren den Vektor: "Realzellen betreiben hohe
  Enzymdichte → nahe am Sättigungs-Kollaps? Hypothese: reale
  Metabolit-Felder sind glatt, weil der Damköhler-Kollaps sie glättet.
  Testbar: registry-K k-Faktor-Sweep Richtung Sättigung."
  Falsifizierbarer Kern: bei welchem k-Faktor k_f (ALLE
  Registry-Geschwindigkeitskonstanten × k_f) verliert das
  Fenster-DISTINCT-Muster seine Präsenz — und ist das nominale Regime
  (k_f = 1) NAHE an dieser Kante (Hypothese getragen) oder WEIT davon
  (Hypothese falsifiziert)?

STRUKTURELLER VORAB-BEFUND (Registrierung, nicht Ergebnis)
  Der Tau-Leaper ist first-order linear: λ = k · dt · n_reaktant (rdme.py,
  _step_tau_leap). Damit ist k_f·dt eine EXAKTE Reparametrisierung der
  Damköhler-Zahl im Harness: Zelle (k_f, dt) ist bit-identisch zur Zelle
  (1, k_f·dt) bei gleichem Seed (gleiche Poisson-Züge, gleiche
  Feasibility-Caps, gleiche Diffusions-Züge — die Zug-ANZAHL hängt nicht
  von dt ab). Der k-Sweep bei dt=1e-5 ist daher ein FEINES
  Damköhler-Gitter (Umsatz k·dt ∈ [1e-5, 1e-1], 3 Punkte je Dezade) über
  dem iter-11/14/24-Fenster — die Kante wird in k·dt-Einheiten gemessen.
  K4 verifiziert die Äquivalenz exakt (bit-identisch); ein Abweichen wäre
  ein Harness-Asymmetrie-Befund (REGISTRATION_ERROR).

REGISTRIERTES PROTOTOKOLL
  M1 iter-24-Harness VERBATIM (beidseitiger Operator post-iter-15,
     Gitter 24³, N_STEPS=600, SNAP_EVERY=10, Q_BIN=0.75, 3-Reaktions-
     Subset, Gauß-Bump amp=150 width=6 auf Glucose+ATP,
     RDMEAdapter(use_tau_leap=True), Metriken + corr + p11 + mass_ratio
     + tau_leap_events, classify/assess-Logik iter-14/24).
  M2 SUBSTRAT-ÄNDERUNG (dokumentiert): Diffusions-Operator auf GPU
     (cupy-Port, iter-24-validiert G1–G5, 33–34×; in-run K1
     re-messung). RNG-Split: GPU-Philox für den Operator, CPU-PCG64
     für tau-leap — zwei unabhängige, seedfixe Ströme. Reihenfolge
     pro Schritt unverändert: Diffusion → Reaktion → Snapshot.
  M3 ACHSE: k_f ∈ {1, 3, 10, 30, 100, 300, 1000, 3000, 10000} (log,
     3/Dezade) bei dt_react=1e-5, Anker D ∈ {0.05, 0.15, 0.45};
     Seeds {200, 201, 202} (wie iter-24 R1 → k_f=1-Zellen direkt mit
     iter-24 R1 vergleichbar). Kontrolle: dt=0 (k-unabhängig) je D.
  M4 ÄQUIVALENZ-PROTOKOLL (K4): Paare (k_f, dt₀/k_f) vs (1, dt₀) für
     (k_f, dt₀) ∈ {(10, 1e-5), (100, 1e-5), (10, 1e-4), (100, 1e-4)}
     bei D=0.15 — erwartet BIT-IDENTISCH (λ linear, Zug-Anzahl
     dt-unabhängig). Nicht-Übereinstimmung ⇒ Harness-Asymmetrie.

KRITERIEN (vor dem Lauf fixiert)
  K1 Operator-Kalibrierung auf GPU mit den iter-24-K1-Schwellen
     (Delta 2e5, 63³, k=20; Masse exakt, Drift ≤ 0.05/Achse,
     Varianz rel ≤ 3 % von 2𝒟·k, Beidseitigkeit ≤ 0.1).
  K2 Harness-Determinismus: run_config(1.0, 1e-5, 0.15, 200) doppelt
     → bit-identische Metriken (beide RNG-Ströme seedfix).
  K3 (BINDEND) Sättigungs-Kante: je Anker D Klassifikation je k_f
     gegen die seed-gepaarte dt=0-Kontrolle (VERBATIM iter-14/24:
     DISTINCT bei corr_drop > 0.3 ODER lz_diff > 0.05 ODER
     tmi_diff > 0.05, ≥2/3 Seeds; RUNAWAY mass_ratio > 3).
     k_edge(D) = größtes k_f im Gitter mit DISTINCT; ist die Gitter-
     Spitze (k_f=1e4) selbst DISTINCT, ist die Kante nicht lokalisiert
     (> 1e4). Globale Kante = MINIMUM der lokalisierten Anker-Kanten
     (konservativ).
  K4 (BINDEND) Äquivalenz: alle 4 Paare bit-identisch in ALLEN
     Metrik-Feldern.
  K5 (Konsistenz, nicht bindend): GPU-k_f=1-Zellen vs iter-24-R1-CPU-
     Zellen bei dt=1e-5 — Klassifikations-Ebene berichtet
     (Substrat-Wechsel CPU→GPU erwartet klassifikations-stabil; iter-24
     belegt Operator-Robustheit des Phänomens).

VERDICT-NAMEN (keine Gesichts-sparende Verzweigung)
  SATURATION_MARGIN_NARROW    — globale Kante < 10×: das nominale Regime
      liegt nahe am Sättigungs-Kollaps; iter-11-Hypothese (reale
      Enzymdichte nahe Kante) getragen im getesteten Registry.
  SATURATION_MARGIN_MODERATE  — 10× ≤ Kante < 100×.
  SATURATION_MARGIN_WIDE      — Kante ≥ 100× (lokalisiert ≤ 1e4):
      Hypothese falsifiziert — das nominale Registry-Regime ist weit
      von der Sättigung entfernt.
  SATURATION_MARGIN_ABSENT    — Kante > 1e4 (Oberende DISTINCT):
      Sättigung im getesteten Bereich nicht erreichbar; Hypothese
      erst recht falsifiziert.
  SATURATION_MARGIN_UNRESOLVABLE — kein Anker hat irgendeine
      DISTINCT-Zelle (k_f=1 verliert das Signal unter dem GPU-Substrat
      gegen iter-24 R1) — Substrat-Sensitivität prüfen.
  REGISTRATION_ERROR          — K1/K2/K4 verletzt.

  Zusatzfeld DAMKOHLER_ÄQUIVALENZ: EQUIVALENT (K4 exakt) / BROKEN.

Post-hoc-Konsistenz wird NIE als Bestätigung gebucht.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import cupy as cp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-24"))

from gpu_operator import stochastic_jump_diffusion_gpu, validate_gpu

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.emergence import (
    binarize,
    emergence_metrics,
)
from cellsim.modules.reactions import ReactionRegistry, default_registry

N_STEPS = 600
SNAP_EVERY = 10
Q_BIN = 0.75
SEEDS = (200, 201, 202)  # wie iter-24 R1 → k_f=1-Zellen vergleichbar
GRID: tuple[int, int, int] = (24, 24, 24)
DT_SWEEP = 1e-5
DIFF_COEFFS = (0.05, 0.15, 0.45)
K_FACTORS = (1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0)
EQUIV_PAIRS = ((10.0, 1e-5), (100.0, 1e-5), (10.0, 1e-4), (100.0, 1e-4))

_SUBSET_NAMES = ("glycolysis", "atp_hydrolysis", "atp_synthase")


def _subset_registry(k_factor: float) -> ReactionRegistry:
    full = default_registry()
    by_name = {r.name: r for r in full.reactions}
    return ReactionRegistry(
        species_ids=full.species_ids,
        reactions=tuple(
            replace(by_name[n], k=by_name[n].k * k_factor)
            for n in _SUBSET_NAMES
        ),
    )


def _gaussian_bump(grid: tuple[int, int, int], amp: float, width: float) -> np.ndarray:
    center = tuple(s // 2 for s in grid)
    idx3 = np.indices(grid)
    d2 = sum((idx3[axis] - c) ** 2 for axis, c in enumerate(center))
    return (amp * np.exp(-d2 / width)).astype(np.int64)


def run_config(k_factor: float, dt_react: float, diff_coeff: float, seed: int) -> dict[str, float]:
    """iter-24-Harness VERBATIM; Operator auf GPU (iter-24-validiert).

    RNG-Split: GPU-Philox (seed) für Diffusion, CPU-PCG64 (make_rng)
    für tau-leap. Beide Ströme seedfix → bit-reproduzierbar.
    """
    rdme = RDMEAdapter(
        registry=_subset_registry(k_factor), grid_shape=GRID, use_tau_leap=True
    )
    rng_cpu = make_rng(seed, 0, 0)
    rng_gpu = cp.random.Generator(cp.random.Philox4x3210(seed=seed))
    bump = _gaussian_bump(GRID, amp=150.0, width=6.0)
    rdme.state.voxels["Glucose"] = rdme.state.voxels["Glucose"] + bump
    rdme.state.voxels["ATP"] = rdme.state.voxels["ATP"] + bump
    rdme.state.total_particles = sum(
        int(v.sum()) for v in rdme.state.voxels.values()
    )
    initial_total = rdme.state.total_particles
    species_order = list(rdme.state.voxels.keys())

    snaps_atp: list[np.ndarray] = []
    snaps_glc: list[np.ndarray] = []
    corr_series: list[float] = []

    for step in range(N_STEPS):
        arrs = [rdme.state.voxels[s] for s in species_order]
        stack = cp.stack([cp.asarray(a) for a in arrs])
        stack = stochastic_jump_diffusion_gpu(stack, diff_coeff, rng_gpu)
        for a, r in zip(arrs, cp.asnumpy(stack), strict=True):
            np.copyto(a, r)
        rdme.step(dt_react, rng_cpu)
        if step % SNAP_EVERY == 0:
            g = rdme.state.voxels["Glucose"].astype(np.float64)
            a = rdme.state.voxels["ATP"].astype(np.float64)
            snaps_atp.append(binarize(a, q=Q_BIN).copy())
            snaps_glc.append(binarize(g, q=Q_BIN).copy())
            if g.std() > 1e-12 and a.std() > 1e-12:
                corr_series.append(float(np.corrcoef(g.ravel(), a.ravel())[0, 1]))
            else:
                corr_series.append(0.0)

    snaps = np.asarray(snaps_atp)
    m = emergence_metrics(snaps, grid_shape=GRID)
    return {
        **m,
        "corr_glc_atp_mean": float(np.mean(corr_series)),
        "p11_mean": float(np.mean([
            float(np.mean((g & a).astype(np.float64)))
            for g, a in zip(snaps_glc, snaps_atp, strict=True)
        ])),
        "mass_ratio": float(rdme.state.total_particles / max(initial_total, 1)),
        "reaction_events_total": float(rdme.state.tau_leap_events),
    }


def classify(cfg: dict[str, float], control: dict[str, float]) -> str:
    """iter-14/24-Kriterien VERBATIM."""
    if cfg["mass_ratio"] > 3.0 or not np.isfinite(cfg["mass_ratio"]):
        return "RUNAWAY"
    corr_drop = abs(cfg["corr_glc_atp_mean"] - control["corr_glc_atp_mean"])
    lz_diff = abs(cfg["lz_growth"] - control["lz_growth"])
    tmi_diff = abs(cfg["temporal_mi_mean"] - control["temporal_mi_mean"])
    if corr_drop > 0.3 or lz_diff > 0.05 or tmi_diff > 0.05:
        return "DISTINCT"
    return "NULL"


def config_classification(
    runs: list[dict[str, float]], controls: list[dict[str, float]]
) -> str:
    per_seed = [classify(r, c) for r, c in zip(runs, controls, strict=True)]
    if per_seed.count("RUNAWAY") >= 2:
        return "RUNAWAY"
    if per_seed.count("DISTINCT") >= 2:
        return "DISTINCT"
    return "NULL"


def sweep() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    controls: dict[float, list[dict[str, float]]] = {}
    for d in DIFF_COEFFS:
        controls[d] = [run_config(1.0, 0.0, d, s) for s in SEEDS]
        print(f"  Kontrolle D={d:g} fertig", flush=True)

    for d in DIFF_COEFFS:
        for k_f in K_FACTORS:
            runs = [run_config(k_f, DT_SWEEP, d, s) for s in SEEDS]
            cls = config_classification(runs, controls[d])
            mean_run = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
            rows.append({
                "diff_coeff": d, "k_factor": k_f,
                "turnover_k_dt": k_f * DT_SWEEP,
                "classification": cls, "mean": mean_run,
            })
            print(f"  D={d:g} k_f={k_f:g} → {cls}", flush=True)
    return {"rows": rows, "n_seeds": len(SEEDS)}


def assess_margin(result: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """K3: k_edge je Anker = größtes DISTINCT-k_f; global = Minimum."""
    rows = result["rows"]
    edges: dict[str, Any] = {}
    for d in DIFF_COEFFS:
        cells = [r for r in rows if r["diff_coeff"] == d and r["k_factor"] > 1.0]
        base = next(r for r in rows if r["diff_coeff"] == d and r["k_factor"] == 1.0)
        distinct = [r for r in cells if r["classification"] == "DISTINCT"]
        if distinct:
            edge = max(r["k_factor"] for r in distinct)
            edges[f"{d:g}"] = {"k_edge": edge, "localized": True,
                               "k1_class": base["classification"]}
        elif base["classification"] == "DISTINCT":
            edges[f"{d:g}"] = {"k_edge": None, "localized": False,
                               "k1_class": base["classification"]}
        else:
            edges[f"{d:g}"] = {"k_edge": None, "localized": None,
                               "k1_class": base["classification"]}
    defined = [v["k_edge"] for v in edges.values() if v["k_edge"] is not None]
    localized = [v for v in edges.values() if v["k_edge"] is not None]
    if not localized:
        verdict = "SATURATION_MARGIN_UNRESOLVABLE"
    elif any(not v["localized"] for v in edges.values()):
        verdict = "SATURATION_MARGIN_ABSENT"
    elif defined:
        gmin = min(defined)
        if gmin < 10.0:
            verdict = "SATURATION_MARGIN_NARROW"
        elif gmin < 100.0:
            verdict = "SATURATION_MARGIN_MODERATE"
        else:
            verdict = "SATURATION_MARGIN_WIDE"
    else:
        verdict = "SATURATION_MARGIN_UNRESOLVABLE"
    result["k_edges"] = edges
    result["global_k_edge"] = min(defined) if defined else None
    return verdict, edges


def equivalence_check() -> dict[str, Any]:
    """K4: (k_f, dt₀/k_f) vs (1, dt₀) — erwartet bit-identisch.

    Begründung (registriert): tau-leap-Propensitäten sind linear in k
    (λ = k·dt·n) und die Zug-Anzahlen hängen nicht von dt ab; gleiche
    Seeds → identische Streams → identische Trajektorien.
    """
    rows = []
    all_equal = True
    for d_anchor in (0.15,):
        for k_f, dt0 in EQUIV_PAIRS:
            a = [run_config(k_f, dt0 / k_f, d_anchor, s) for s in SEEDS]
            b = [run_config(1.0, dt0, d_anchor, s) for s in SEEDS]
            pair_equal = all(x == y for x, y in zip(a, b, strict=True))
            all_equal = all_equal and pair_equal
            mean_a = {k: float(np.mean([r[k] for r in a])) for k in a[0]}
            mean_b = {k: float(np.mean([r[k] for r in b])) for k in b[0]}
            rows.append({
                "k_factor": k_f, "dt0": dt0,
                "dt_scaled": dt0 / k_f,
                "bit_identical": pair_equal,
                "lz_scaled": mean_a["lz_growth"],
                "lz_ref": mean_b["lz_growth"],
                "corr_scaled": mean_a["corr_glc_atp_mean"],
                "corr_ref": mean_b["corr_glc_atp_mean"],
            })
            print(f"  Äquiv (k={k_f:g}, dt={dt0 / k_f:g} vs 1, {dt0:g}) "
                  f"bit-identisch={pair_equal}", flush=True)
    return {"rows": rows, "equivalence": "EQUIVALENT" if all_equal else "BROKEN",
            "pass": bool(all_equal)}


def main() -> None:
    print("=== iter-25: SATURATION_MARGIN (k-Sweep Richtung Sättigung, GPU) ===")
    print(f"Gitter {GRID}, Seeds {SEEDS}, dt={DT_SWEEP:g}, "
          f"k_f ∈ {K_FACTORS}, Operator: GPU (beidseitig).\n")

    print("K1 Operator-Kalibrierung (GPU, iter-24-K1-Schwellen):", flush=True)
    cal = validate_gpu()
    for r in cal["rows"]:
        print(f"  D={r['d']:g}: Sym {r['sym']:.4f} | Drift "
              f"{[f'{c:+.4f}' for c in r['com']]} | Var/Achse "
              f"{[f'{v:.3f}' for v in r['var']]} (erwartet {r['expect']:.3f})",
              flush=True)
    print(f"  Masse {cal['mass_ok']}, Drift {cal['drift_ok']}, "
          f"Varianz {cal['var_ok']}, Beidseitigkeit {cal['symmetry_ok']} "
          f"({'PASS' if cal['pass'] else 'FAIL'})", flush=True)

    a = run_config(1.0, DT_SWEEP, 0.15, 200)
    b = run_config(1.0, DT_SWEEP, 0.15, 200)
    det = {"identical": a == b, "pass": bool(a == b)}
    print(f"K2 Determinismus: bit-identisch = {det['identical']} "
          f"({'PASS' if det['pass'] else 'FAIL'})\n", flush=True)

    result: dict[str, Any] = sweep()
    print(f"\n{'label':<22} {'class':<9} {'tMI':>6} {'LZgrw':>7} "
          f"{'corr':>7} {'p11':>6} {'mass':>6} {'events':>10}")
    for row in result["rows"]:
        m = row["mean"]
        label = f"D={row['diff_coeff']:g},k={row['k_factor']:g}"
        print(f"{label:<22} {row['classification']:<9} "
              f"{m['temporal_mi_mean']:>6.3f} {m['lz_growth']:>+7.3f} "
              f"{m['corr_glc_atp_mean']:>7.3f} {m['p11_mean']:>6.3f} "
              f"{m['mass_ratio']:>6.2f} {m['reaction_events_total']:>10.0f}")

    verdict, edges = assess_margin(result)
    result["verdict"] = verdict
    result["k_edges"] = edges
    print(f"\nKanten je Anker: {json.dumps(edges)}")
    print(f"Globale Kante: {result['global_k_edge']}")

    eq = equivalence_check()
    result["k4_equivalence"] = eq
    print(f"K4 Damköhler-Äquivalenz: {eq['equivalence']} "
          f"({'PASS' if eq['pass'] else 'FAIL'})")

    # K5 Konsistenz (berichtet, nicht bindend): k_f=1 vs iter-24 R1
    iter24_k1 = {0.05: "DISTINCT", 0.15: "DISTINCT", 0.45: "DISTINCT"}
    k1_rows = {r["diff_coeff"]: r["classification"]
               for r in result["rows"] if r["k_factor"] == 1.0}
    result["k5_consistency"] = {
        "iter24_r1_reference": iter24_k1,
        "gpu_k1": k1_rows,
        "classification_match": bool(all(
            k1_rows.get(d) == c for d, c in iter24_k1.items())),
    }
    print(f"K5 Konsistenz (GPU k=1 vs iter-24 R1 CPU): "
          f"{result['k5_consistency']['classification_match']}")

    if not cal["pass"] or not det["pass"] or not eq["pass"]:
        final = "REGISTRATION_ERROR"
    else:
        final = verdict
    result["final_verdict"] = final
    result["k1_operator_calibration"] = cal
    result["k2_determinism"] = det
    print(f"\nVERDICT: {final}")

    margins = {
        "SATURATION_MARGIN_NARROW": [
            "iter-11-Hypothese getragen (nominal nahe Kante); "
            "N*-Gesetz um Sättigungs-Schranke erweitern",
            "Feiner Sweep um die Kante (Faktor-Abstand < 2)",
        ],
        "SATURATION_MARGIN_MODERATE": [
            "Kante eine Dekade über nominal — Hypothese schwach getragen",
            "Feiner Sweep um die Kante + D-Abhängigkeit der Kante",
        ],
        "SATURATION_MARGIN_WIDE": [
            "Hypothese falsifiziert: nominale Kinetik weit von Sättigung",
            "VECTOR_ENDOGEN_UVC_TIMESCALE",
        ],
        "SATURATION_MARGIN_ABSENT": [
            "Kante > 1e4: Sättigung im Harness nicht erreichbar; "
            "Regime-Behauptung auf Harness-Gültigkeit begrenzen",
        ],
        "SATURATION_MARGIN_UNRESOLVABLE": [
            "GPU-Substrat verliert das k=1-Signal — Substrat-Sensitivität "
            "als eigene Korrektur prüfen",
        ],
    }
    if final == "REGISTRATION_ERROR":
        result["next_vectors"] = ["Harness-Asymmetrie/K1/K2 diagnostizieren; "
                                  "korrigierte Re-Registrierung"]
    else:
        result["next_vectors"] = margins.get(
            final, ["Substrat-Sensitivität prüfen"])

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")


if __name__ == "__main__":
    main()
