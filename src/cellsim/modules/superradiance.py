"""Superradianz-Modul (photischer L2-Kanal) — portiert aus MT_Sim.

Quelle: /run/media/julian/ML2/Python/MT_Sim/run_experimentum_crucis.py
(Dicke-sech²-Burst, numerisch stabil) + Kurian et al. 2024 (Experiment:
UV-Superradianz aus Tryptophan-Mega-Netzwerken in biologischen
Architekturen — gemessen).

Theorie-Anker (scratch/theory/orchor_tegmark_rekonstruktion.md):
- τ_SR = τ_sp/N: kooperative Emission wird mit der Netzwerkgröße
  SCHNELLER — der kohärente Zustand emittiert sich weg, bevor
  thermische Kanäle greifen.
- Peak ∝ N² (Dicke); Gesamteleergie pro Burst ≈ N·E (ein Photon pro
  Emitter).
- Tegmarks thermische Masse-Dekohärenz adressiert Massen-Positions-
  Superpositionen — kein anwendbarer Kanal auf den photonischen
  Substrat (kein Isomorphismus-Transfer).

Status: PRODUCTION (iter-15). Konstanten σ/QY sind HYPOTHESE
(dokumentiert); die Superradianz-Formeln sind Theorie-Standard (Dicke)
mit experimentellem Anker.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from cellsim.modules.em import c_light, h_planck

# --- iter-15-Konstanten (HYPOTHESE, dokumentiert) ---
TAU_SPONTANEOUS_S = 1e-9          # Trp-Fluoreszenz-Lebensdauer ~1 ns
TRYPTOPHAN_WAVELENGTH_NM = 280.0  # Trp-Absorption/Emission (Kurian: UV-B/C)
SIGMA_TRP_CM2 = 1e-17             # UV-Absorptionsquerschnitt (kleines Molekül)
QUANTUM_YIELD_UVC = 0.1           # Sutherland-Typ-Photochemie
ABSORPTION_LENGTH_NM = 200.0      # Cytoplasma (EM-Modul-Konvention)

# Damköhler-Fenster (iter-11/14, Turnover pro Molekül pro 1-ms-Schritt)
DAMKOHLER_WINDOW_PER_STEP = (1e-4, 0.1)


def photon_energy_j(wavelength_nm: float = TRYPTOPHAN_WAVELENGTH_NM) -> float:
    """E = h·c/λ."""
    return h_planck * c_light / (wavelength_nm * 1e-9)


def superradiance_time_s(n_emitters: int, tau_sp_s: float = TAU_SPONTANEOUS_S) -> float:
    """Dicke: τ_SR = τ_sp / N — kooperative Emission skaliert 1/N."""
    if n_emitters < 1:
        raise ValueError("n_emitters muss >= 1 sein")
    return tau_sp_s / n_emitters


def dicke_intensity_photons_per_s(
    n_emitters: int,
    t_s: np.ndarray | float,
    tau_sp_s: float = TAU_SPONTANEOUS_S,
    wavelength_nm: float = TRYPTOPHAN_WAVELENGTH_NM,
) -> np.ndarray | float:
    """Dicke-sech²-Burst: I(t) = A·sech²((t−t_d)/τ_SR).

    Normalisierung exakt: ∫ I dt = n_emitters Photonen (ein Photon pro
    Emitter). Peak = N²·E/(2·τ_sp·E) = N²/(2·τ_sp) Photonen/s ∝ N².
    Burst-Zentrum t_d = τ_SR·ln(N) (Dicke-Delay), numerisch stabil
    (cosh-Clip wie in MT_Sim/run_experimentum_crucis.py).
    """
    if n_emitters < 1:
        raise ValueError("n_emitters muss >= 1 sein")
    tau_sr = tau_sp_s / n_emitters
    t_delay = tau_sr * math.log(max(n_emitters, 2))
    amplitude = n_emitters / (2.0 * tau_sr)  # Integral sech² = 2τ_SR
    arg = (t_s - t_delay) / max(tau_sr, 1e-30)
    cosh_arg = np.cosh(np.clip(arg, -700.0, 700.0))
    sech_sq = np.where(np.isinf(cosh_arg), 0.0, (1.0 / cosh_arg) ** 2)
    return amplitude * sech_sq


@dataclass(frozen=True)
class PhotonicCluster:
    """Ein superradiantes Emitter-Cluster (z.B. Trp-Netzwerk)."""

    n_emitters: int
    tau_sp_s: float = TAU_SPONTANEOUS_S
    wavelength_nm: float = TRYPTOPHAN_WAVELENGTH_NM

    @property
    def tau_sr_s(self) -> float:
        return superradiance_time_s(self.n_emitters, self.tau_sp_s)

    @property
    def peak_photons_per_s(self) -> float:
        """Peak-Rate ∝ N²: n/(2·τ_SR) = N²/(2·τ_sp)."""
        return self.n_emitters / (2.0 * self.tau_sr_s)

    @property
    def photons_per_burst(self) -> float:
        return float(self.n_emitters)

    def intensity(self, t_s: np.ndarray | float) -> np.ndarray | float:
        return dicke_intensity_photons_per_s(
            self.n_emitters, t_s, self.tau_sp_s, self.wavelength_nm
        )


def aggregate_photon_rate_per_s(
    n_clusters: int,
    n_per_cluster: int,
    f_burst_hz: float,
) -> float:
    """Mittlere Photonenrate der Zelle: Φ = M·N·f (ein Photon pro
    Emitter pro Burst, Bursts mit Rate f pro Cluster)."""
    if f_burst_hz < 0:
        raise ValueError("f_burst_hz >= 0")
    return n_clusters * n_per_cluster * f_burst_hz


def flux_at_cm2(
    photon_rate_per_s: float,
    r_nm: float,
    absorption_length_nm: float = ABSORPTION_LENGTH_NM,
) -> float:
    """Isotrope Punktquelle: Φ(r) = rate·exp(−r/r_abs)/(4πr²) in
    photons/cm²/s (EMSource-Konvention aus modules/em.py)."""
    if r_nm <= 0:
        raise ValueError("r_nm > 0")
    absorption = math.exp(-r_nm / absorption_length_nm)
    r_cm = r_nm * 1e-7
    surface_cm2 = 4.0 * math.pi * r_cm**2
    return photon_rate_per_s * absorption / surface_cm2


def turnover_per_second(
    flux_photons_cm2_s: float,
    sigma_cm2: float = SIGMA_TRP_CM2,
    quantum_yield: float = QUANTUM_YIELD_UVC,
) -> float:
    """Photochemischer Turnover pro Molekül pro Sekunde = Φ·σ·QY."""
    return flux_photons_cm2_s * sigma_cm2 * quantum_yield


def damkoehler_window_per_step(dt_s: float = 1e-3) -> tuple[float, float]:
    """Sichtbarkeitsfenster (iter-11/14): Turnover k·dt ∈ [1e-4, 0.1]
    pro Molekül pro Schritt. Rückgabe pro Sekunde skaliert: [1e-4/dt,
    0.1/dt]."""
    if dt_s <= 0:
        raise ValueError("dt_s > 0")
    return (1e-4 / dt_s, 0.1 / dt_s)


def threshold_aggregate_rate_per_s(
    r_nm: float = 100.0,
    sigma_cm2: float = SIGMA_TRP_CM2,
    quantum_yield: float = QUANTUM_YIELD_UVC,
    absorption_length_nm: float = ABSORPTION_LENGTH_NM,
    dt_s: float = 1e-3,
) -> tuple[float, float]:
    """Aggregierte Photonenrate Φ* für Fenster-Eintritt.

    Turnover pro Schritt = Φ·G(r)·σ·QY·dt; Fenster [1e-4, 0.1]
    → Φ* = window_per_step/(G·σ·QY) (damkoehler_window_per_step
    liefert bereits pro-Sekunde-skaliert).
    Rückgabe: (untere Grenze, obere Grenze) in photons/s.
    """
    lo, hi = damkoehler_window_per_step(dt_s)
    g = math.exp(-r_nm / absorption_length_nm) / (4.0 * math.pi * (r_nm * 1e-7) ** 2)
    coupling = g * sigma_cm2 * quantum_yield
    return (lo / coupling, hi / coupling)
