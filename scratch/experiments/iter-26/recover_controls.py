"""iter-26 Nachtrag: Kontroll-Baselines persistieren (post-hoc Recovery).

Buchhaltungs-Note iter-26 (gleiches Muster wie iter-25): der
registrierte Lauf (edge_fine.py) klassifizierte gegen in-run-Kontrollen
(dt=0, seed-gepaart, M4) und persistierte deren Mittel NICHT in
result.json. Für D=0.05/0.15 deckt iter-25 controls_recovery.json die
Werte ab (gleicher Harness, gleiche Seeds → deterministisch
bit-identisch); für die NEUEN Anker D ∈ {0.10, 0.25, 0.30} existierten
die Kontrollen nur im Speicher des Laufs — ohne Persistenz wäre die
Klassifikation dieser 21 Zeilen aus den Artefakten nicht
nachrechenbar. Dieser Recovery-Lauf wiederholt die 15 deterministischen
Kontrollzellen NUR zur Persistenz — KEIN neuer Befund, KEINE neue
Klassifikation; die gebuchte Klassifikation beruht auf den in-run-
Kontrollen, nicht auf diesen Werten.

Cross-Check (erwartet, keine neue Messung): D=0.05/0.15 müssen
bit-identisch zu iter-25/controls_recovery.json sein (K5-Logik,
läuferübergreifender Determinismus).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "iter-25"))
import saturation_margin as sm  # noqa: E402 (Harness VERBATIM, wie edge_fine)

HERE = Path(__file__).resolve().parent
ANCHORS = (0.05, 0.10, 0.15, 0.25, 0.30)
ITER25_CTRL = HERE.parent / "iter-25" / "controls_recovery.json"


def main() -> None:
    rows = []
    for d in ANCHORS:
        runs = [sm.run_config(1.0, 0.0, d, s) for s in sm.SEEDS]
        mean = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
        rows.append({"diff_coeff": d, "mean": mean,
                     "per_seed_lz": [r["lz_growth"] for r in runs],
                     "per_seed_corr": [r["corr_glc_atp_mean"] for r in runs],
                     "per_seed_tmi": [r["temporal_mi_mean"] for r in runs]})
        print(f"Kontrolle D={d:g}: LZ {mean['lz_growth']:+.4f} | corr "
              f"{mean['corr_glc_atp_mean']:.4f} | tMI "
              f"{mean['temporal_mi_mean']:.4f} "
              f"| p11 {mean['p11_mean']:.4f} | mass {mean['mass_ratio']:.2f}",
              flush=True)
    target = HERE / "controls_recovery.json"
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"→ {target}")

    # Cross-Check gegen iter-25 (Determinismus über Läufer hinweg)
    ref = {r["diff_coeff"]: r["mean"]
           for r in json.loads(ITER25_CTRL.read_text(encoding="utf-8"))}
    for d in (0.05, 0.15):
        mine = next(r["mean"] for r in rows if r["diff_coeff"] == d)
        same = mine == ref[d]
        print(f"Cross-Check D={d:g} vs iter-25: bit-identisch={same}",
              flush=True)


if __name__ == "__main__":
    main()
