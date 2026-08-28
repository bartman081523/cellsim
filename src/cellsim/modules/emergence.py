"""Emergenz-Metriken (L_new) — portiert aus Origin_Ruliad.

Quelle: /run/media/julian/ML2/Python/Origin_Ruliad/Emergence_Phase_6.py
(Methodik: binarize + mutual_information_binary + lz_complexity_binary,
 2D → 3D erweitert; Laplacian-Schema aus Phase 6/7).

Diese Metriken quantifizieren computationale Struktur in diskreten
Feldern (RDME-Voxel, EM-Felder, Chromosom-Konformationen) im Sinne
des Ruliad-Frameworks: "computational fixed points" entlang
Observer-Pfaden zeigen sich als persistente Struktur (MI > 0) und
entwickelnde Komplexität (LZ).

Status: PRODUCTION (iter-10/iter-10-retry):
- iter-10: uniforme IC → MI trivial 0 (Setup-Artefakt dokumentiert)
- iter-10-retry: lokalisierte IC + Tau-Leap → MI=0.74, spatial MI=0.47,
  echte Dynamik sichtbar; Reaktions-Raten im Hybrid noch zu schwach
  gegenüber Diffusion (CONTRADICTION für Rate-Skalierung — offen)
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def binarize(z: np.ndarray, method: str = "quantile", q: float = 0.65) -> np.ndarray:
    """Binarisiert ein Array basierend auf einer Schwelle.

    Methoden: "quantile" (default), "mean", "median".
    """
    if method == "quantile":
        thr = np.quantile(z, q) if np.any(z) else 0.5
    elif method == "mean":
        thr = z.mean()
    else:
        thr = np.median(z)
    return (z > thr).astype(np.uint8)


def mutual_information_binary(a: np.ndarray, b: np.ndarray) -> float:
    """Mutual Information zweier binärer Felder (in bit)."""
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
    """Normalisierte Lempel-Ziv-Komplexität eines binären Feldes."""
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
    """3D diskreter Laplace-Operator (Origin_Ruliad Phase 6, 2D→3D).

    6-Nachbar-Summe minus 6·Z, periodische Randbedingungen.
    """
    z = z.astype(np.float64)
    out = -6.0 * z
    for axis in range(3):
        out += np.roll(z, 1, axis=axis)
        out += np.roll(z, -1, axis=axis)
    return out


def emergence_metrics(
    snapshots: list[np.ndarray] | np.ndarray,
    grid_shape: tuple[int, int, int] | None = None,
    spatial_axis: int = 1,
) -> dict[str, float]:
    """Berechnet alle Emergenz-Metriken für eine Snapshot-Serie.

    - temporal_mi: MI zwischen aufeinanderfolgenden Snapshots
      (Struktur-Persistenz; MI(X,X)=H(X) für statische Felder)
    - spatial_mi: MI zwischen benachbarten Voxel-Spalten
      (räumliche Kohärenz)
    - lz_first/last/growth: Lempel-Ziv-Entwicklung (computational richness)
    """
    snaps = np.asarray(snapshots)
    if snaps.ndim == 2 and grid_shape is not None:
        snaps = snaps.reshape((-1, *grid_shape))

    t_mis = [
        mutual_information_binary(snaps[i], snaps[i + 1])
        for i in range(snaps.shape[0] - 1)
    ]

    s_mis: list[float] = []
    for snap in snaps:
        if snap.ndim < 2:
            continue
        sl_a = np.take(snap, range(snap.shape[spatial_axis] - 1), axis=spatial_axis)
        sl_b = np.take(snap, range(1, snap.shape[spatial_axis]), axis=spatial_axis)
        s_mis.append(mutual_information_binary(sl_a.ravel(), sl_b.ravel()))

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
