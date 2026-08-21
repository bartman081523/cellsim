"""EM-Schicht (Iter-1): Schwarzkörper + Chemolumineszenz.

Sehr vereinfacht: berechnet erwartete UV-Photonen-Emission einer
einzelnen Zelle. Resultat ist die Basis für iter-2 (UV-Synchronisation
zwischen Zellen).
"""

from __future__ import annotations

import math

# Physikalische Konstanten
h_planck = 6.626_070_15e-34      # J·s
c_light = 299_792_458.0          # m/s
k_boltzmann = 1.380_649e-23      # J/K
AVOGADRO = 6.022_140_76e23        # 1/mol


def schwarzkoerper_spektrale_leistungsdichte(wavelength_nm: float, temperature_K: float) -> float:
    """Planck-Funktion: spektrale Leistungsdichte pro Wellenlänge [W/m²/nm].

    B(λ, T) = 2hc²/λ⁵ · 1/(exp(hc/λkT) - 1)
    """
    lam = wavelength_nm * 1e-9
    exponent = h_planck * c_light / (lam * k_boltzmann * temperature_K)
    if exponent > 500:
        return 0.0
    return 2 * h_planck * c_light**2 / (lam**5 * (math.exp(exponent) - 1)) * 1e-9


def chemolumineszenz_rate(atp_per_s: float = 1e6) -> float:
    """Geschätzte UV-Photonen/s aus ATP-getriebenen Reaktionen.

    Quelle: Popp, F.A. (1988) 'Biophotonen-Emission'.
    Annahme: ~1 Photon pro 10⁵ ATP-Hydrolysen über Singulett-Sauerstoff.
    """
    return atp_per_s / 1e5


def photonen_fluss_dichte(
    photonen_pro_s: float,
    zell_radius_nm: float = 250.0,
    abstand_nm: float = 1.0,
) -> float:
    """Photonen-Flussdichte am Nachbar bei gegebenem Abstand [Photonen/cm²/s]."""
    if abstand_nm <= 0:
        return 0.0
    # Kugeloberfläche bei radius=abstand (in nm)
    surface_cm2 = 4 * math.pi * (abstand_nm * 1e-7) ** 2
    return photonen_pro_s / max(surface_cm2, 1e-30)


def run_iter1() -> dict[str, float]:
    """Hauptfunktion für iter-1: berechnet UV-Emission."""
    results = {}

    # 1. Schwarzkörper bei 310 K (Körper-Temperatur)
    # Bei 250 nm UV: extrem schwach
    uv_wavelengths = [200.0, 250.0, 300.0, 350.0, 400.0]
    for lam in uv_wavelengths:
        radiance = schwarzkoerper_spektrale_leistungsdichte(lam, 310.0)
        results[f"schwarzkoerper_{int(lam)}nm_W_per_m2_per_nm"] = radiance

    # 2. Chemolumineszenz (Popp)
    atp_rate = 1e6    # typische ATP-Hydrolyse-Rate in JCVI-syn3A
    chl_photons = chemolumineszenz_rate(atp_rate)
    results["chemolumineszenz_photons_per_s"] = chl_photons

    # 3. Flussdichte am Nachbar (1 µm Abstand)
    flux_1um = photonen_fluss_dichte(chl_photons, abstand_nm=1000.0)
    results["flux_1um_photons_per_cm2_per_s"] = flux_1um

    # 4. Flussdichte bei 10 µm Abstand
    flux_10um = photonen_fluss_dichte(chl_photons, abstand_nm=10_000.0)
    results["flux_10um_photons_per_cm2_per_s"] = flux_10um

    # Signal-Bewertung (CellsimMixMind-Skala)
    if flux_1um > 1.0:
        signal = "STRONG"
    elif flux_1um > 0.01:
        signal = "WEAK"
    elif flux_1um > 1e-6:
        signal = "NULL"
    else:
        signal = "CONTRADICTION"

    results["signal"] = signal
    results["next_vectors"] = [
        "iter-2: UV-Phasen-Synchronisation zwischen Zellen",
        "iter-3: Radikal-Paar-Magnetorezeption (Schulten)",
        "iter-4: QuQuint-Beschleunigung der RDME-Ratenberechnung",
    ]
    return results


if __name__ == "__main__":
    import json

    results = run_iter1()
    print(json.dumps(results, indent=2))
    # Schreibe result.json
    target = __file__.replace("em_layer.py", "result.json")
    with open(target, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n→ Wrote {target}")
