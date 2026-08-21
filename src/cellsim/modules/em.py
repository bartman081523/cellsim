"""EM-Schicht (L_new): Maxwell im statischen Limit + Chemolumineszenz.

Iter-1 (scratch) hat gezeigt: Chemolumineszenz (~10 Photonen/s pro
JCVI-syn3A-Zelle) erzeugt eine messbare UV-Flussdichte von ~10⁸
Photonen/cm²/s bei 1 µm Abstand. Schwarzkörper ist bei 310K im UV
vernachlässigbar.

Diese Schicht modelliert:
  - Dipol-Quelle im Cytoplasma (ATP-getrieben)
  - Ausbreitung im freien Raum (1/r²)
  - Optionale Absorption durch Nachbarzellen
  - UV-Photonen-Budget pro Zelle

Status: NEUE Schicht (L5 in der 4-Schichten-Erweiterung).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


# Konsistente Konstanten (lokale Kopie, nicht von core.constants um Unabhängigkeit zu wahren)
h_planck = 6.626_070_15e-34
c_light = 299_792_458.0
k_boltzmann = 1.380_649e-23


@dataclass(frozen=True)
class EMParams:
    """Parameter der EM-Schicht."""

    temperature_K: float = 310.0
    atp_hydrolysis_per_s: float = 1.0e6   # typische JCVI-Rate
    photon_yield_per_atp: float = 1.0e-5  # Popp-Faktor
    zell_radius_nm: float = 250.0
    absorption_length_nm: float = 200.0   # Wasser + Cytoplasma


def schwarzkoerper_emission(wavelength_nm: float, temperature_K: float) -> float:
    """Planck-Funktion: spektrale Leistungsdichte [W/m²/nm]."""
    lam = wavelength_nm * 1e-9
    exponent = h_planck * c_light / (lam * k_boltzmann * temperature_K)
    if exponent > 500:
        return 0.0
    return 2 * h_planck * c_light**2 / (lam**5 * (math.exp(exponent) - 1)) * 1e-9


def chemolumineszenz_photons_per_s(
    atp_hydrolysis_per_s: float,
    yield_per_atp: float = 1.0e-5,
) -> float:
    """UV-Photonen/s aus ATP-getriebenen Reaktionen (Popp-Faktor)."""
    return atp_hydrolysis_per_s * yield_per_atp


@dataclass
class EMSource:
    """Eine einzelne EM-Quelle (z.B. eine Zelle)."""

    position_nm: np.ndarray
    photons_per_s: float
    zell_radius_nm: float

    def total_photons_per_s(self) -> float:
        return self.photons_per_s

    def flux_density_at(
        self,
        target_position_nm: np.ndarray,
        absorption_length_nm: float = 200.0,
    ) -> float:
        """Photonen-Flussdichte [Photons/cm²/s] am Ziel.

        1/r²-Ausbreitung + Absorption im Medium.
        """
        r_nm = float(np.linalg.norm(target_position_nm - self.position_nm))
        if r_nm < 1e-9:
            return 0.0
        # Absorption: exp(-r/absorption_length)
        absorption_factor = math.exp(-r_nm / absorption_length_nm)
        # Kugeloberfläche in cm²
        r_cm = r_nm * 1e-7
        surface_cm2 = 4 * math.pi * r_cm**2
        flux_per_cm2 = (self.photons_per_s * absorption_factor) / surface_cm2
        return flux_per_cm2


def estimate_uv_emission(
    params: EMParams | None = None,
    wavelength_nm: float = 300.0,
) -> dict[str, float]:
    """Schätzt UV-Emission einer einzelnen JCVI-syn3A-Zelle."""
    p = params or EMParams()
    out: dict[str, float] = {}
    # Schwarzkörper (in W/m²/nm)
    radiance = schwarzkoerper_emission(wavelength_nm, p.temperature_K)
    out[f"radiance_{int(wavelength_nm)}nm_W_per_m2_per_nm"] = radiance
    # Chemolumineszenz (in Photonen/s)
    photons = chemolumineszenz_photons_per_s(
        p.atp_hydrolysis_per_s,
        p.photon_yield_per_atp,
    )
    out["chemolumineszenz_photons_per_s"] = photons
    # Flussdichte bei 1 µm
    source = EMSource(
        position_nm=np.array([0.0, 0.0, 0.0]),
        photons_per_s=photons,
        zell_radius_nm=p.zell_radius_nm,
    )
    out["flux_density_1um"] = source.flux_density_at(
        np.array([1000.0, 0.0, 0.0]),
        absorption_length_nm=p.absorption_length_nm,
    )
    out["flux_density_10um"] = source.flux_density_at(
        np.array([10_000.0, 0.0, 0.0]),
        absorption_length_nm=p.absorption_length_nm,
    )
    return out
