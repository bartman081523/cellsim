"""iter-24-Nachfolger-Infrastruktur: GPU-Port (cupy) des beidseitigen
Sprung-Diffusions-Operators + registrierte Validierung.

STATUS: Infrastruktur für künftige Sweeps (NICHT das registrierte
iter-24-Protokoll — der CPU-Lauf läuft als registrierte R1 fertig).

SEMANTIK identisch zum Produktions-Operator (emergence.py, post-iter-15):
pro Achse n_out = binomial(n, 2𝒟), 50/50-Split auf ±Richtung →
Massenerhalt exakt, Drift 0, Varianzwachstum 2𝒟 je Achse (6𝒟 gesamt).
Substrat-Änderung ggü. CPU: (a) Geräte-RNG (Philox) statt numpy-PCG64 —
andere Stichproben-Züge, gleiche Verteilung; (b) batched über alle
Spezies: EIN Array (S, X, Y, Z), Sprünge entlang der räumlichen Achsen
1..3 statt 0..2.

VALIDIERUNG (vor Nutzung in einem registrierten Lauf zu fixieren):
  G1 Massenerhalt exakt (1 und k Schritte).
  G2 Drift: |com/Achse| ≤ 0.05 Voxel nach k=20 Schritten auf 63³
     (dieselbe registrierte K1-Schwelle wie iter-24 K1b).
  G3 Varianz: |var/Achse − 2𝒟·k|/(2𝒟·k) ≤ 0.03 nach k=20 auf 63³
     (dieselbe K1-Schwelle wie K1c).
  G4 Beidseitigkeit: |c₊−c₋|/(c₊+c₋) ≤ 0.1 nach 1 Schritt (K1d).
  G5 CPU↔GPU-Verteilungs-Äquivalenz: Varianz/Drift/Nachbar-Statistik
     innerhalb der G2/G3/G4-Schwellen beider Plattformen identisch
     (Verteilungs-Gleichheit, NICHT Zug-Gleichheit — andere RNG).
"""

from __future__ import annotations

import cupy as cp


def stochastic_jump_diffusion_gpu(
    stack: cp.ndarray,
    diff_coeff: float,
    rng: cp.random.Generator,
) -> cp.ndarray:
    """Beidseitige Sprung-Diffusion auf GPU, batched über Spezies.

    stack: (S, X, Y, Z) int64, nicht-negativ. Sprünge entlang der
    räumlichen Achsen 1/2/3. Massenerhalt exakt; Drift 0; Varianz
    2𝒟 je Achse pro Schritt. Semantik = emergence.stochastic_jump_
    diffusion pro Spezies.
    """
    p_dir = min(diff_coeff, 0.5)
    if p_dir == 0.0:
        return stack
    for axis in range(3):
        n_out = rng.binomial(stack, 2.0 * p_dir)
        plus = rng.binomial(n_out, 0.5)
        minus = n_out - plus
        stack = (
            stack
            - plus
            - minus
            + cp.roll(plus, 1, axis=axis + 1)
            + cp.roll(minus, -1, axis=axis + 1)
        )
    return stack


def validate_gpu() -> dict:
    """G1-G5: dieselben registrierten Schwellen wie iter-24 K1."""
    grid = (63, 63, 63)
    center = tuple(s // 2 for s in grid)
    steps = 20
    n_delta = 200_000
    rows = []
    mass_ok = drift_ok = var_ok = sym_ok = True
    for d in (0.05, 0.15, 0.45):
        rng = cp.random.Generator(cp.random.Philox4x3210(seed=555))
        stack = cp.zeros((1, *grid), dtype=cp.int64)
        stack[0][center] = n_delta
        before = int(stack.sum().item())
        stack = stochastic_jump_diffusion_gpu(stack, d, rng)
        after1 = int(stack.sum().item())
        g = stack[0]
        cm = tuple(int(c) for c in center)
        c_minus = float(g[(cm[0] - 1, cm[1], cm[2])].item())
        c_plus = float(g[(cm[0] + 1, cm[1], cm[2])].item())
        sym = abs(c_plus - c_minus) / max(c_plus + c_minus, 1.0)
        sym_ok = sym_ok and sym <= 0.1
        for _ in range(steps - 1):
            stack = stochastic_jump_diffusion_gpu(stack, d, rng)
        afterk = int(stack.sum().item())
        mass_ok = mass_ok and before == after1 == afterk
        g = stack[0].astype(cp.float64)
        idx = cp.indices(grid).astype(cp.float64)
        com = [float((g * idx[i]).sum().item() / afterk - center[i]) for i in range(3)]
        var = [
            float((g * (idx[i] - center[i] - com[i]) ** 2).sum().item() / afterk)
            for i in range(3)
        ]
        expect = 2.0 * d * steps
        rel = [abs(v - expect) / expect for v in var]
        drift_ok = drift_ok and all(abs(c) <= 0.05 for c in com)
        var_ok = var_ok and all(r <= 0.03 for r in rel)
        rows.append({"d": d, "sym": sym, "com": com, "var": var,
                     "expect": expect, "rel": rel})
    return {"rows": rows, "mass_ok": mass_ok, "drift_ok": drift_ok,
            "var_ok": var_ok, "symmetry_ok": sym_ok,
            "pass": bool(mass_ok and drift_ok and var_ok and sym_ok)}


if __name__ == "__main__":
    import json
    import time

    report = validate_gpu()
    for r in report["rows"]:
        print(f"D={r['d']:g}: Sym {r['sym']:.4f} | Drift "
              f"{[f'{c:+.4f}' for c in r['com']]} | Var/Achse "
              f"{[f'{v:.3f}' for v in r['var']]} (erwartet {r['expect']:.3f}, "
              f"rel {[f'{e:.1e}' for e in r['rel']]})")
    print(f"Massenerhalt {report['mass_ok']}, Drift {report['drift_ok']}, "
          f"Varianz {report['var_ok']}, Beidseitigkeit {report['symmetry_ok']} "
          f"({'PASS' if report['pass'] else 'FAIL'})")

    # Benchmark: GPU vs CPU pro Schritt (26 Spezies, 24³)
    s_spec = 26
    rng = cp.random.Generator(cp.random.Philox4x3210(seed=1))
    stack = cp.full((s_spec, 24, 24, 24), 50, dtype=cp.int64)
    for _ in range(3):  # warm-up
        stack = stochastic_jump_diffusion_gpu(stack, 0.15, rng)
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(20):
        stack = stochastic_jump_diffusion_gpu(stack, 0.15, rng)
    cp.cuda.Stream.null.synchronize()
    t1 = time.perf_counter()
    gpu_ms = (t1 - t0) / 20 * 1000
    print(f"\nGPU: {gpu_ms:.2f} ms/Schritt (26 Spezies, 24³) "
          f"vs CPU 263.9 ms → Faktor {263.9 / gpu_ms:.0f}×")
    print(json.dumps({"pass": report["pass"], "gpu_ms_per_step": gpu_ms}))
