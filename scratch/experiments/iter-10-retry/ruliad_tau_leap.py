"""Iter-10-retry: Ruliad-Emergenz mit vektorisierter Diffusion (Tau-Leaping).

Befund aus iter-10: Der Gillespie-SSA macht 1 Event/Schritt — bei 6³
Voxeln bleibt das Feld quasi statisch (reaktiv ≡ diffusiv). Origin_Ruliad
(Emergence_Phase_6/7) nutzt stattdessen vektorisierte Laplace-Diffusion
(alle Zellen pro Schritt) + lokale Chemie — und erzeugt reiche Struktur.

Fix (Hybrid-RDME, Standard-Tau-Leap-Ansatz):
  1. Vektorisierte 3D-Laplace-Diffusion (portiert aus Origin_Ruliad Phase 6,
     np.roll-basiert, auf 3D erweitert) auf ALLE Spezies pro Schritt
  2. Stochastische Gillespie-Reaktion pro Schritt (unser RDME)
  3. Lokalisierter Seed (Gauß-Fleck) wie Origin_Ruliads lokale Quellen

Hypothese (ergebnisoffen): Mit vektorisierter Diffusion unterscheiden
sich reaktiv und diffusiv messbar und LZ-Komplexität entwickelt sich
über die Zeit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.core.rng import make_rng
from cellsim.modules.reactions import default_registry

# ---------------------------------------------------------------
# Metriken — portiert aus Origin_Ruliad/Emergence_Phase_6.py
# (identisch zu iter-10/ruliad_emergence.py, hier inline zur
#  Vermeidung von Cross-Directory-Imports)
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
    return mi


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


def laplacian_3d(z: np.ndarray) -> np.ndarray:
    """3D diskreter Laplace-Operator (Origin_Ruliad Phase 6, 2D→3D erweitert).

    6-Nachbar-Summe minus 6·Z, periodische Randbedingungen (np.roll).
    """
    z = z.astype(np.float64)
    out = -6.0 * z
    for axis in range(3):
        out += np.roll(z, 1, axis=axis)
        out += np.roll(z, -1, axis=axis)
    return out


# ---------------------------------------------------------------
# Hybrid-RDME: vektorisierte Diffusion + Gillespie-Reaktionen
# ---------------------------------------------------------------

def run_hybrid(
    grid_shape: tuple[int, int, int] = (16, 16, 16),
    n_steps: int = 2000,
    diffusion_coeff: float = 0.15,
    seed: int = 42,
    with_reactions: bool = True,
) -> dict[str, float]:
    """Hybrid-RDME: Origin_Ruliad-Laplacian + cellsim-Reaktions-Registry."""
    registry = default_registry()
    if not with_reactions:
        from dataclasses import replace

        registry = type(registry)(
            species_ids=registry.species_ids,
            reactions=tuple(replace(r, k=0.0) for r in registry.reactions),
        )

    rng = make_rng(seed, 0, 0)
    center = tuple(s // 2 for s in grid_shape)

    # Gauß-Fleck für Glucose + ATP (Origin_Ruliad: lokale Quellen)
    fields: dict[str, np.ndarray] = {}
    for s_id in registry.species_ids:
        base = np.full(grid_shape, 5, dtype=np.int64)
        if s_id in ("Glucose", "ATP"):
            ii, jj, kk = np.indices(grid_shape)
            d2 = (ii - center[0]) ** 2 + (jj - center[1]) ** 2 + (kk - center[2]) ** 2
            base += (150 * np.exp(-d2 / 6.0)).astype(np.int64)
        fields[s_id] = base

    snapshots: list[np.ndarray] = []

    for step in range(n_steps):
        # 1) Vektorisierte Diffusion auf allen Spezies
        for s_id, f in fields.items():
            updated = f.astype(np.float64) + diffusion_coeff * laplacian_3d(f)
            fields[s_id] = np.maximum(np.rint(updated), 0.0).astype(np.int64)

        # 2) Gillespie-Reaktion: ein zufälliges Voxel pro Schritt
        if with_reactions:
            idx = tuple(int(rng.integers(0, s)) for s in grid_shape)
            rxn = registry.reactions[int(rng.integers(0, len(registry.reactions)))]
            ok = True
            for s_id, delta in rxn.species_change.items():
                if delta < 0:
                    v = fields.get(s_id)
                    if v is None or v[idx] < -delta:
                        ok = False
                        break
            if ok:
                for s_id, delta in rxn.species_change.items():
                    v = fields.get(s_id)
                    if v is not None:
                        v[idx] += delta

        if step % 5 == 0:
            snapshots.append(binarize(fields["ATP"], q=0.75).copy())

    snaps = np.asarray(snapshots)

    t_mis = [
        mutual_information_binary(snaps[i], snaps[i + 1])
        for i in range(snaps.shape[0] - 1)
    ]
    s_mis = []
    for snap in snaps:
        f = snap.reshape(grid_shape)
        s_mis.append(
            mutual_information_binary(f[:, :-1, :].ravel(), f[:, 1:, :].ravel())
        )
    lz = [lz_complexity_binary(s) for s in snaps]

    return {
        "temporal_mi_mean": float(np.mean(t_mis)) if t_mis else 0.0,
        "temporal_mi_first": float(t_mis[0]) if t_mis else 0.0,
        "temporal_mi_last": float(t_mis[-1]) if t_mis else 0.0,
        "spatial_mi_mean": float(np.mean(s_mis)) if s_mis else 0.0,
        "lz_first": float(lz[0]) if lz else 0.0,
        "lz_last": float(lz[-1]) if lz else 0.0,
        "lz_growth": float(lz[-1] - lz[0]) if lz else 0.0,
        "n_snapshots": float(snaps.shape[0]),
    }


if __name__ == "__main__":
    print("=== iter-10-retry: Ruliad-Emergenz (Tau-Leap-Hybrid) ===\n")
    out: dict[str, object] = {}

    for label, with_rxn in [("reactive", True), ("diffusive", False)]:
        r = run_hybrid(with_reactions=with_rxn, n_steps=2000, seed=42)
        out[label] = r
        print(f"--- {label} ---")
        print(f"  Temporal MI: mean={r['temporal_mi_mean']:.4f} "
              f"first={r['temporal_mi_first']:.4f} last={r['temporal_mi_last']:.4f}")
        print(f"  Spatial MI:  mean={r['spatial_mi_mean']:.4f}")
        print(f"  LZ: first={r['lz_first']:.4f} last={r['lz_last']:.4f} "
              f"growth={r['lz_growth']:+.4f}")

    r_t = float(out["reactive"]["temporal_mi_mean"])  # type: ignore[arg-type]
    d_t = float(out["diffusive"]["temporal_mi_mean"])  # type: ignore[arg-type]
    mi_diff = r_t - d_t

    # Signal-Kriterien (ergebnisoffen)
    if mi_diff > 0.05 and r_t > 0.1:
        signal = "STRONG"
    elif mi_diff > 0.02:
        signal = "WEAK"
    elif r_t < 0.01 and d_t < 0.01:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"

    out["mi_difference_reactive_minus_diffusive"] = mi_diff
    out["signal"] = signal
    out["next_vectors"] = [
        "Falls STRONG: → vektorisierte Diffusion als Tau-Leap in Production (OptimizedRDME)",
        "Falls CONTRADICTION: Reaktions-Raten im Hybrid zu schwach → Rate-Sweep",
        "Querverbindung: Origin_Ruliad Phase 6/7 nutzt dasselbe Laplacian-Schema in 2D",
        "Querverbindung: Genesis.md UVC 232 nm → EM-Schicht als Photonik-Quelle",
    ]

    print(f"\nMI-Differenz (reaktiv - diffusiv): {mi_diff:+.4f}")
    print(f"Signal: {signal}")
    target = Path(__file__).with_name("result.json")
    target.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"→ Wrote {target}")
