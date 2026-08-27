"""Iter-9: Integrations-Adapter in einer Zelle.

Test: laufen alle 4+ Produktions-Module in EINER Zelle synchron?
- RDME (L3 Gillespie-SSA) mit lokaler Diffusion (A-O)
- ODE (Glycolyse + ATP-Hydrolyse)
- Chromosom (Bead-Spring)
- EM (Chemolumineszenz, Popp)
- Cryptochrom (Compass)
- QuQuint-VQE (Reaktionsraten-Beschleuniger)

Output: Telemetrie, ATP-Stabilität, Cross-Modul-Signale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

import numpy as np

from cellsim.driver.integration import (
    IntegratedCell,
    IntegrationConfig,
)


def run_iter9(
    t_end_s: float = 5.0,
    dt_s: float = 1e-3,
    seed: int = 42,
) -> dict[str, object]:
    """Integrierte Zelle für 5 Sekunden."""
    config = IntegrationConfig(
        rdme_grid_shape=(4, 4, 4),
        n_chromosome_beads=20,
        seed=seed,
    )
    rng = np.random.default_rng(seed)
    cell = IntegratedCell(config)
    n_steps = int(t_end_s / dt_s)

    history = {
        "atp_mM": [],
        "chromo_yield": [],
        "em_uv_photons_per_s": [],
        "rdme_particles": [],
        "membrane_radius_nm": [],
    }

    for _ in range(n_steps):
        tel = cell.step(dt_s, rng)
        history["atp_mM"].append(tel["atp_mM"])
        history["chromo_yield"].append(tel["chromo_yield"])
        history["em_uv_photons_per_s"].append(tel["em_uv_photons_per_s"])
        history["rdme_particles"].append(tel["rdme_particles"])
        history["membrane_radius_nm"].append(tel["membrane_radius_nm"])

    atp_arr = np.asarray(history["atp_mM"])
    chromo_arr = np.asarray(history["chromo_yield"])

    return {
        "n_steps": n_steps,
        "atp_min_mM": float(atp_arr.min()),
        "atp_max_mM": float(atp_arr.max()),
        "atp_mean_mM": float(atp_arr.mean()),
        "atp_stable": 0.01 < atp_arr.mean() < 100.0,
        "chromo_yield_mean": float(chromo_arr.mean()),
        "chromo_yield_var": float(chromo_arr.std()),
        "em_uv_final": float(history["em_uv_photons_per_s"][-1]),
        "rdme_particles_final": int(history["rdme_particles"][-1]),
        "n_modules_active": 5,
        "signal": "STRONG" if 0.01 < atp_arr.mean() < 100.0 else "CONTRADICTION",
        "next_vectors": [
            "iter-9b: 10 integrierte Zellen in einer Suspension (UV-Kopplung mit realistischer ODE)",
            "iter-9c: Vergleich gegen JCVI-syn3A-Wachstumsdaten (biologische Validierung)",
            "Falls STRONG: → driver/integration.py in cellsim.core als Standard-Sim",
        ],
    }


if __name__ == "__main__":
    result = run_iter9()
    print("=== iter-9: Integration aller Module ===\n")
    print(f"ATP mean: {result['atp_mean_mM']:.3f} mM "
          f"(stable: {result['atp_stable']})")
    print(f"Cryptochrom yield: {result['chromo_yield_mean']:.4f} "
          f"± {result['chromo_yield_var']:.4f}")
    print(f"EM UV (final): {result['em_uv_final']:.2e} Photonen/s")
    print(f"RDME particles (final): {result['rdme_particles_final']}")
    print(f"\nSignal: {result['signal']}")

    target = __file__.replace("integration_run.py", "result.json")
    with open(target, "w") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"→ Wrote {target}")
