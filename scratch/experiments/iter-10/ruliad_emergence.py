"""Iter-10: Ruliad-Emergenz-Metriken auf dem RDME.

Portiert aus Origin_Ruliad/Emergence_Phase_6.py (mit Attribuierung):
  - binarize (Quantil)
  - mutual_information_binary
  - lz_complexity_binary

Anwendung: RDME-Voxel-Felder (cellsim L3) über die Zeit. Test, ob die
Zellsimulation nicht-triviale computationale Struktur erzeugt
(Ruliad: "computational fixed points" in Kausalgraphen).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.modules.reactions import default_registry

# ---------------------------------------------------------------
# Emergenz-Metriken — portiert aus Origin_Ruliad/Emergence_Phase_6.py
# (Ruliad UV Consciousness Simulation, mit Anpassungen)
# ---------------------------------------------------------------

def binarize(z: np.ndarray, method: str = "quantile", q: float = 0.65) -> np.ndarray:
    """Binarisiert ein Array basierend auf einer Schwelle (Origin_Ruliad Phase 6)."""
    if method == "quantile":
        thr = np.quantile(z, q) if np.any(z) else 0.5
    elif method == "mean":
        thr = z.mean()
    else:
        thr = np.median(z)
    return (z > thr).astype(np.uint8)


def mutual_information_binary(a: np.ndarray, b: np.ndarray) -> float:
    """Mutual Information für zwei binäre Felder (Origin_Ruliad Phase 6)."""
    p00 = np.mean((a == 0) & (b == 0))
    p01 = np.mean((a == 0) & (b == 1))
    p10 = np.mean((a == 1) & (b == 0))
    p11 = np.mean((a == 1) & (b == 1))
    eps = 1e-12
    mi = 0.0
    for p_joint, p_a, p_b in [
        (p00, p00 + p01, p00 + p10),
        (p01, p00 + p01, p01 + p11),
        (p10, p10 + p11, p00 + p10),
        (p11, p10 + p11, p01 + p11),
    ]:
        if p_joint > eps and p_a > eps and p_b > eps:
            mi += p_joint * np.log2(p_joint / (p_a * p_b))
    return float(mi)


def lz_complexity_binary(arr: np.ndarray) -> float:
    """Normalisierte Lempel-Ziv-Komplexität (Origin_Ruliad Phase 6)."""
    s = "".join("1" if x else "0" for x in arr.astype(np.uint8).ravel())
    n = len(s)
    if n == 0:
        return 0.0
    dictionary: set[str] = set()
    w = ""
    for c in s:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            dictionary.add(wc)
            w = c
    basis = n / np.log2(n) if n > 1 else 1.0
    return len(dictionary) / max(1.0, basis)


# ---------------------------------------------------------------
# Experiment: RDME mit Reaktionen vs. Diffusions-Kontrolle
# ---------------------------------------------------------------

def rdme_field_series(
    grid_shape: tuple[int, int, int],
    n_steps: int,
    with_reactions: bool,
    seed: int = 42,
    localized_seed: bool = True,
) -> np.ndarray:
    """Führt RDME aus und liefert binarisierte Voxel-Snapshots der dominante Spezies.

    Bei localized_seed=True werden Partikel als Gauß-Fleck im Zentrum
    initialisiert (wie Origin_Ruliad lokale Quellen nutzt) statt uniform.
    Returns: Array [n_snapshots, n_voxels] mit 0/1-Werten.
    """
    registry = default_registry()
    if not with_reactions:
        # Kontrolle: alle Reaktionskonstanten auf 0 → nur Diffusion/Migration
        from dataclasses import replace

        registry = type(registry)(
            species_ids=registry.species_ids,
            reactions=tuple(
                replace(r, k=0.0) for r in registry.reactions
            ),
        )
    rdme = RDMEAdapter(registry=registry, grid_shape=grid_shape)
    rng = make_rng(seed, 0, 0)

    if localized_seed:
        # Heterogene Initialisierung: Gauß-Fleck im Zentrum für alle Spezies
        center = tuple(s // 2 for s in grid_shape)
        for voxels in rdme.state.voxels.values():
            voxels[:] = 5   # niedriger Grundpegel
            # Gauß-Boost um Zentrum
            for i in range(grid_shape[0]):
                for j in range(grid_shape[1]):
                    for k in range(grid_shape[2]):
                        dist2 = sum(
                            (idx - c) ** 2 for idx, c in zip((i, j, k), center, strict=True)
                        )
                        voxels[i, j, k] += int(120 * np.exp(-dist2 / 4.0))
        rdme.state.total_particles = sum(
            int(v.sum()) for v in rdme.state.voxels.values()
        )

    # Dominante Spezies = die mit den meisten Partikeln
    dominant = max(rdme.state.voxels, key=lambda k: int(rdme.state.voxels[k].sum()))

    snapshots: list[np.ndarray] = []
    for step in range(n_steps):
        rdme.step(1e-3, rng)
        if step % 10 == 0:
            field = rdme.state.voxels[dominant].ravel()
            snapshots.append(binarize(field, q=0.75))
    return np.asarray(snapshots)


def temporal_mi(snapshots: np.ndarray) -> list[float]:
    """MI zwischen aufeinanderfolgenden Snapshots."""
    mis = []
    for i in range(snapshots.shape[0] - 1):
        mis.append(mutual_information_binary(snapshots[i], snapshots[i + 1]))
    return mis


def spatial_mi(snapshots: np.ndarray, grid_shape: tuple[int, int, int]) -> list[float]:
    """MI zwischen horizontal benachbarten Voxeln (Kohärenz-Länge Proxy)."""
    mis = []
    for snap in snapshots:
        field = snap.reshape(grid_shape)
        a = field[:, :-1, :].ravel()
        b = field[:, 1:, :].ravel()
        mis.append(mutual_information_binary(a, b))
    return mis


def lz_series(snapshots: np.ndarray) -> list[float]:
    """LZ-Komplexität pro Snapshot."""
    return [lz_complexity_binary(s) for s in snapshots]


def run_iter10(
    grid_shape: tuple[int, int, int] = (6, 6, 6),
    n_steps: int = 3000,
    seed: int = 42,
) -> dict[str, object]:
    """Hauptexperiment: Reaktiv vs. diffusiv."""
    snap_reactive = rdme_field_series(grid_shape, n_steps, with_reactions=True, seed=seed)
    snap_control = rdme_field_series(grid_shape, n_steps, with_reactions=False, seed=seed)

    results = {}
    for label, snaps in [("reactive", snap_reactive), ("diffusive", snap_control)]:
        t_mi = temporal_mi(snaps)
        s_mi = spatial_mi(snaps, grid_shape)
        lz = lz_series(snaps)
        results[label] = {
            "temporal_mi_mean": float(np.mean(t_mi)),
            "temporal_mi_max": float(np.max(t_mi)),
            "spatial_mi_mean": float(np.mean(s_mi)),
            "lz_mean": float(np.mean(lz)),
            "lz_first": float(lz[0]),
            "lz_last": float(lz[-1]),
            "lz_growth": float(lz[-1] - lz[0]),
            "n_snapshots": len(lz),
        }

    r = results["reactive"]
    d = results["diffusive"]

    # Signal-Bewertung (ergebnisoffen, via experiment.md-Kriterien)
    mi_diff = r["temporal_mi_mean"] - d["temporal_mi_mean"]
    if mi_diff > 0.05 and r["temporal_mi_mean"] > 0.1:
        signal = "STRONG"
    elif mi_diff > 0.02:
        signal = "WEAK"
    elif r["temporal_mi_mean"] < 0.01 and d["temporal_mi_mean"] < 0.01:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"

    return {
        "results": results,
        "mi_difference_reactive_minus_diffusive": mi_diff,
        "signal": signal,
        "grid_shape": list(grid_shape),
        "n_steps": n_steps,
        "next_vectors": [
            "Falls STRONG: → production module src/cellsim/modules/emergence.py",
            "Falls WEAK: → iter-10-retry mit größerem Gitter (10³) und längerer Laufzeit",
            "Falls NULL: RDME-Raten zu schwach für Emergenz → Rate-Scaling nötig",
            "Falls CONTRADICTION: Diffusion erzeugt mehr Struktur als Reaktion → Registry prüfen",
            "Querverbindung: Genesis.md UVC 232 nm → EM-Schicht (iter-1) als Photonik-Input",
        ],
    }


if __name__ == "__main__":
    result = run_iter10()
    print("=== iter-10: Ruliad-Emergenz im RDME ===\n")
    for label, r in result["results"].items():
        print(f"--- {label} ---")
        print(f"  Temporal MI: mean={r['temporal_mi_mean']:.4f} max={r['temporal_mi_max']:.4f}")
        print(f"  Spatial MI:  mean={r['spatial_mi_mean']:.4f}")
        print(f"  LZ:          first={r['lz_first']:.4f} last={r['lz_last']:.4f} "
              f"growth={r['lz_growth']:+.4f}")
    print(f"\nMI-Differenz (reaktiv - diffusiv): {result['mi_difference_reactive_minus_diffusive']:+.4f}")
    print(f"Signal: {result['signal']}")

    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\n→ Wrote {target}")
