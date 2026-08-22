"""Cryptochrom-Modell (L_new): Radikal-Paar-Spin-Dynamik.

Iter-3 (scratch) hat gezeigt: Cryptochrom-Singulett-Ausbeute zeigt
klar Magnetfeld-Abhängigkeit (Resonanz bei ~25-50 µT). Vorhersage
passt zu Vogel-Compass-Experimenten (Ritz 2000, Maeda 2008).

Diese Schicht modelliert:
  - Vereinfachtes 2-Zustands-System (Singulett |S>, Triplett |T>)
  - Magnetfeld-abhängige Singulett-Ausbeute
  - Optionale Hyperfein-Parameter für Trp-Radikale
  - Lindblad-artige Master-Gleichung (vereinfacht)

Status: NEUE Schicht in cellsim. Empirisch motiviert durch Cryptochrom-
Magnetorezeption in Vögeln + Mäusen. Für JCVI-syn3A: möglich, aber
unbekannt (M. genitalium hat Cry-Proteine).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Konsistente Konstanten (lokale Kopie)
MU_B = 9.274_010_0783e-24    # Bohr-Magneton [J/T]
G_E = -2.002_319_30436256    # freier Elektron g-Faktor
PLANCK = 6.626_070_15e-34    # J·s


@dataclass(frozen=True)
class CryptochromeParams:
    """Cryptochrom-Parameter nach Ritz et al. (2000).

    Bei B=0 erwartet die Theorie eine S/T-Entartung → Singulett-Pop ≈ 0.5.
    Bei geomagnetischem Feld (50 µT) zeigt Resonanz-Oszillation.
    """

    a_trp_1: float = 0.3e-3        # Trp-Hyperfein [T]
    a_trp_2: float = 0.3e-3
    a_trp_3: float = 0.3e-3
    g_fad: float = 2.0030           # FAD g-Faktor
    tau_s: float = 1.0e-5           # Radikal-Paar-Lebensdauer [s]
    r_nm: float = 1.0               # Trp-Distanz [nm]


@dataclass
class CryptochromeState:
    """Spin-Zustand des Radikal-Paars."""

    s_population: float = 1.0       # Singulett-Pop.
    t_population: float = 0.0       # Triplett-Pop.
    singlet_yield: float = 1.0      # Effektive Ausbeute
    coherence: float = 0.0          # S-T-Kohärenz
    step_count: int = 0


class CryptochromeAdapter:
    """Cryptochrom-Modell mit Magnetfeld-abhängiger Spin-Chemie."""

    name = "cryptochrome"

    def __init__(
        self,
        params: CryptochromeParams | None = None,
    ) -> None:
        self.params = params or CryptochromeParams()
        self.state = CryptochromeState()

    def step(
        self,
        dt_s: float,
        b_field_t: float = 50.0e-6,
    ) -> dict[str, float]:
        """Ein Cryptochrom-Schritt: Master-Gleichung-Update."""
        self.state.step_count += 1

        # Larmor-Frequenz für Singulett-Triplett-Mischung
        # ω = ΔE/ħ = g·μ_B·B/ħ
        omega = abs(G_E) * MU_B * b_field_t / PLANCK

        # Hyperfein-Aufspaltung (Trp-Kopplung)
        delta_hf = math.sqrt(
            self.params.a_trp_1**2
            + self.params.a_trp_2**2
            + self.params.a_trp_3**2
        )

        # Lindblad-artige Master-Gleichung (vereinfacht):
        # dS/dt = -k_rec · S + k_TS · T + k_pump   (Spin-Pump)
        # dT/dt = +k_rec · S - k_TS · T - k_pump
        # k_rec = 1/τ, k_TS = (sin²(ω·τ/2) + 1) · Δω_HF, k_pump = Photo-Anregung
        k_rec = 1.0 / self.params.tau_s
        # Hintergrund-Hyperfein-Rate: bei B=0 erzeugt die Hyperfein-Wechselwirkung
        # selbst Spin-Mischung. Rate = g·μ_B·δ_HF/ħ
        delta_omega_hf = abs(self.params.g_fad) * MU_B * delta_hf / PLANCK
        k_ts_base = delta_omega_hf
        k_ts_field = (math.sin(omega * self.params.tau_s / 2.0) ** 2) * delta_omega_hf
        k_ts = k_ts_base + k_ts_field
        # Photo-Pump: konstanter Spin-Bildungs-Input (Blaulicht-Anregung)
        k_pump = 1.0 / self.params.tau_s

        # Vollständige Master-Gleichung
        # Massen-Erhaltung: dS + dT = 0 (Population fließt zwischen S und T)
        d_s = (
            -k_rec * self.state.s_population
            + k_ts * self.state.t_population
            + k_pump * (1.0 - self.state.s_population)
        )

        self.state.s_population = max(0.0, min(1.0, self.state.s_population + d_s * dt_s))
        self.state.t_population = 1.0 - self.state.s_population
        self.state.singlet_yield = self.state.s_population
        return self._telemetry(b_field_t)

    def _telemetry(self, b_field_t: float) -> dict[str, float]:
        return {
            "crypto_s_population": self.state.s_population,
            "crypto_t_population": self.state.t_population,
            "crypto_singlet_yield": self.state.singlet_yield,
            "crypto_b_field_t": b_field_t,
        }

    @staticmethod
    def singlet_yield_at_field(
        b_field_t: float,
        params: CryptochromeParams | None = None,
        n_steps: int = 200,
    ) -> float:
        """Statische Methode: berechnet Singulett-Ausbeute bei gegebenem Feld."""
        adapter = CryptochromeAdapter(params)
        # Steady-State: viele Schritte mit gleichem Feld
        last_yield = 1.0
        for _ in range(n_steps):
            result = adapter.step(dt_s=1.0e-7, b_field_t=b_field_t)
            last_yield = result["crypto_singlet_yield"]
        return last_yield
