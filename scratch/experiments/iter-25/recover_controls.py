"""iter-25 Nachtrag: Kontroll-Baselines persistieren (post-hoc Recovery).

Buchhaltungs-Note iter-25: der registrierte Lauf (saturation_margin.py)
klassifizierte gegen in-run-Kontrollen (dt=0, seed-gepaart) und
persistierte deren Mittel NICHT in result.json (Abweichung vom
iter-24-Stil, wo dt=0 Teil des Sweep-Gitters war). Dieser Recovery-Lauf
wiederholt die 9 deterministischen Kontrollzellen NUR zur Persistenz —
gleiche Seeds, gleicher Harness → bit-identische Werte (in-run-K2
belegt Determinismus des Harness). KEIN neuer Befund, KEINE neue
Klassifikation; die gebuchte Klassifikation beruht auf den in-run-
Kontrollen, nicht auf diesen Werten.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import saturation_margin as sm

SEEDS = sm.SEEDS
DIFF_COEFFS = sm.DIFF_COEFFS


def main() -> None:
    rows = []
    for d in DIFF_COEFFS:
        runs = [sm.run_config(1.0, 0.0, d, s) for s in SEEDS]
        mean = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
        rows.append({"diff_coeff": d, "mean": mean,
                     "per_seed_lz": [r["lz_growth"] for r in runs],
                     "per_seed_corr": [r["corr_glc_atp_mean"] for r in runs],
                     "per_seed_tmi": [r["temporal_mi_mean"] for r in runs]})
        print(f"Kontrolle D={d:g}: LZ {mean['lz_growth']:+.4f} | corr "
              f"{mean['corr_glc_atp_mean']:.4f} | tMI {mean['temporal_mi_mean']:.4f} "
              f"| p11 {mean['p11_mean']:.4f} | mass {mean['mass_ratio']:.2f}",
              flush=True)
    target = Path(__file__).with_name("controls_recovery.json")
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"→ {target}")


if __name__ == "__main__":
    main()
