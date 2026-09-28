"""Diagnose zum Agreement-Test (POST-HOC, NICHT Teil der Registrierung).

Anlass: der pre-registrierte Lauf (xu_agreement_test.py, 2026-09-28)
lieferte H1/H2 ABSENT, H3 CHARGE_DEGRADED — ALLE Metriken exakt 0.0
(kein einziger Kern |Zeitmittel-Vorticity| > 0.3 in irgendeiner
Bedingung; Welch-p nan wegen Null-Varianz beider Seiten). Ein Floor-
Effekt: die Metrik kann nicht diskriminieren, wenn in BEIDEN
Bedingungen keine Kerne existieren. Vor der Buchung characterisiert
dieser Probe-Skript das Regime (keine Verdict-Aenderung):

Probe A (Regime-Charakterisierung, 3 Seeds x 2 Bedingungen):
  max|vort| + Kernzahl (>0.3) je SNAPSHOT (instantan) ueber die Zeit.
  Trennt: (a) Wirbel annihilieren voellig (Feld -> uniform),
          (b) Wirbel existieren instantaen, wandern aber (Dwell <
          30 % -> Zeitmittel unter Schwelle),
          (c) strukturierte Gegen-Trieb-Wand ohne Vortizitaet.

Probe B (Amplituden-Sweep, EXPLORATORIUSCH — Kriterien VERBATIM aus
  der Registrierung uebernommen, Verdicts als SWEEP_* gelabelt, keine
  Promotion zu Befunden): delta0 in {0.1, 0.2, 0.5}, counter vs
  uniform, 10 Seeds, E1-Metrik unverändert (Zeitmittel [1400,1500),
  |vort| > 0.3, Interface-Band x=50 +/- 6 vs Interior-Baende x=25/75,
  ratio-Kriterium r >= 2.0 in >= 7/10 UND Welch-p < 0.05).
  Null ist delta0-invariant (uniformer Drive rotiert das Feld nur
  gemeinsam; Plaquette-Zirkulation ist drift-invariant) — Spot-Check
  mit 3 Seeds bei delta0=0.5 statt Voll-Duplikat.

Seeds wie die Registrierung: 1000-1009. CPU numpy, ~2 min.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

from scipy import stats

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "xu_agreement_test", _HERE / "xu_agreement_test.py"
)
xu = importlib.util.module_from_spec(_spec)
sys.modules["xu_agreement_test"] = xu
_spec.loader.exec_module(xu)

SNAPSHOTS = (0, 10, 25, 50, 100, 200, 400, 700, 1000, 1300, 1499)
SWEEP_DELTAS = (0.1, 0.2, 0.5)

OUT_DIR = _HERE


def snapshot_trace(seed: int, drive_mode: str) -> list:
    """Instantaene Kern-Diagnostik entlang der Trajektorie.

    Loop spiegelt run_condition (gleicher RNG-Verbrauch, bit-identische
    Trajektorie), sammelt Snapshots statt Fenstermitteln.
    """
    rng = xu.np.random.default_rng(seed)
    delta_col = xu.drive_field(drive_mode)[xu.np.newaxis, :]
    phases = rng.uniform(0.0, 2.0 * xu.np.pi, (xu.N, xu.N))

    trace = []
    for t in range(xu.STEPS):
        phases = xu.relax(phases, rng)
        phases = xu.np.mod(phases + delta_col, 2.0 * xu.np.pi)
        if t in SNAPSHOTS:
            vort_t = xu.plaquette_vorticity(phases)
            trace.append(
                {
                    "t": t,
                    "n_cores": len(xu.cores_from(vort_t, xu.VORT_THRESHOLD)),
                    "max_abs_vort": float(xu.np.max(xu.np.abs(vort_t))),
                    "rho_interface": xu.band_density(vort_t, 50),
                    "rho_interior": float(
                        xu.np.mean(
                            [
                                xu.band_density(vort_t, xu.INTERIOR_BAND_X[0]),
                                xu.band_density(vort_t, xu.INTERIOR_BAND_X[1]),
                            ]
                        )
                    ),
                }
            )
    return trace


def main() -> None:
    started = time.time()
    print("Diagnose (post-hoc, nicht Teil der Registrierung) — Start")

    # Probe A: Regime
    probe_a = []
    for seed in (1000, 1001, 1002):
        for mode in ("uniform", "counter"):
            trace = snapshot_trace(seed, mode)
            probe_a.append({"seed": seed, "drive": mode, "trace": trace})

            print(
                f"A seed={seed} {mode:8s}: n_cores je Snapshot "
                f"{[s['n_cores'] for s in trace]}, "
                f"max|vort| t=1499 {trace[-1]['max_abs_vort']:.3f}"
            )

    # Probe B: Amplituden-Sweep (E1-Metrik VERBATIM)
    probe_b = []
    for delta in SWEEP_DELTAS:
        xu.DELTA0 = delta
        ratios_n = []
        ratios_a = []
        for seed in xu.SEEDS_E1:
            ratios_n.append(xu.e1_ratio(xu.run_condition(seed, "uniform", False)["vort_e1"]))
            ratios_a.append(xu.e1_ratio(xu.run_condition(seed, "counter", False)["vort_e1"]))
        arr_n = xu.np.array(ratios_n)
        arr_a = xu.np.array(ratios_a)
        _t, p = stats.ttest_ind(arr_a, arr_n, equal_var=False)
        n_ge_2 = int(xu.np.sum(arr_a >= 2.0))
        n_ge_13 = int(xu.np.sum(arr_a >= 1.3))
        if n_ge_2 >= 7 and p < 0.05:
            verdict = "SPIRAL_EDGE_REALIZED(sweep)"
        elif n_ge_13 >= 7:
            verdict = "SPIRAL_EDGE_WEAK(sweep)"
        else:
            verdict = "SPIRAL_EDGE_ABSENT(sweep)"
        probe_b.append(
            {
                "delta0": delta,
                "mean_ratio_null": float(xu.np.mean(arr_n)),
                "mean_ratio_alt": float(xu.np.mean(arr_a)),
                "ratios_alt": [float(x) for x in arr_a],
                "n_seeds_ratio_ge_2": n_ge_2,
                "n_seeds_ratio_ge_1_3": n_ge_13,
                "welch_p": float(p),
                "verdict": verdict,
            }
        )
        print(
            f"B delta0={delta}: mean_ratio null={xu.np.mean(arr_n):.4f} "
            f"alt={xu.np.mean(arr_a):.4f} n_ge_2={n_ge_2} n_ge_13={n_ge_13} "
            f"p={p:.4f} verdict={verdict}"
        )

    # Null-Invarianz-Spotcheck: uniform bei delta0=0.5 muss 0 Kerne
    # liefern (wie delta0=0.05) — Erwartung, kein Kriterium.
    xu.DELTA0 = 0.5
    null_max = []
    for seed in xu.SEEDS_E1[:3]:
        vort = xu.run_condition(seed, "uniform", False)["vort_e1"]
        null_max.append(float(xu.np.max(xu.np.abs(vort))))
    print(f"B null-spotcheck delta0=0.5: max|vort_e1| je Seed {null_max}")

    result = {
        "status": "POST_HOC_DIAGNOSE — nicht Teil der Registrierung",
        "registered_run": "result.json (delta0=0.05, H1/H2 ABSENT, "
        "H3 CHARGE_DEGRADED, alle Metriken 0.0, p nan)",
        "probe_a_regime": probe_a,
        "probe_b_sweep": probe_b,
        "null_invariance_spotcheck_max_abs_vort_d05": null_max,
        "runtime_s": time.time() - started,
    }
    out_path = OUT_DIR / "probe_result.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Ergebnis persistiert: {out_path}")
    print(f"Runtime: {result['runtime_s']:.1f} s")


if __name__ == "__main__":
    main()

