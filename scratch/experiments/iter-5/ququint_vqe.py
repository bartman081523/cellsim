"""Iter-5: QuQuint-VQE-Beschleunigung (QuQuint-Hamiltonian-Diagonalisierung).

Hypothese: Mit QuQuint-VQE (d=5) ist die Magic State Distillation-
Threshold 36.3% statt 1% (Campbell et al. 2012). Die CCZ-Gate-
Implementierung braucht 4 M-Gates statt 7 T-Gates. Dies ist eine
echte Beschleunigung (keine 1000×-HYPOTHESE-Übert{}reibung).

Iter-5 delegiert an src/cellsim/quantum/ququint.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.quantum.ququint import run_iter5

if __name__ == "__main__":
    result = run_iter5()
    print("=== iter-5: QuQuint-VQE-Beschleunigung ===")
    print(f"Threshold-Faktor: {result['threshold_factor_ququint_vs_qubit']:.2f}×")
    print(f"CCZ-Gate-Ratio: 7/4 = {result['ccz_gate_ratio']:.2f}× reduction")
    print(f"\n{'γ':>8s} {'Grundzustand':>15s} {'Norm':>10s}")
    for r in result["results"]:
        print(f"  {r['gamma']:.3f}  {r['ground_state']:+.4f}  {r['matrix_norm']:.4f}")

    target = __file__.replace("ququint_vqe.py", "result.json")
    with open(target, "w") as fh:
        json.dump(result, fh, indent=2, default=float)
    print(f"\n→ Wrote {target}")
