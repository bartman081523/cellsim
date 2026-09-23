"""Photonic-Coupling (iter-23): Superradianz-Quelle als Produktions-Kopplung.

Vektor VECTOR_PHOTONIC_COUPLING_PRODUCTION: der photonische Kanal
(Trp-Superradianz, Kurian et al. 2024) wird in die Produktionsschiene
(HybridDriver) gekoppelt und auf sein falsifizierbares Kernkriterium
geprüft: tut er in JCVI-syn3A Photochemie (Damköhler-Fenster)?

Registriertes Modell (Best-Case zugunsten des Kanals):
- Substrat: das GESAMTE Zell-Tryptophan in EINEM superradianten
  Kollektiv (Kurian-Substrat — Mikrotubuli-Trp-Gitter — existiert in
  syn3A nicht; Prokaryot; Gate-Kontext wie C3 in orch_or).
- Pump: 100 % der metabolischen ATP-Hydrolyse → Trp-Anregung
  (Quantenausbeute 1, absurde Obergrenze).
- Energieerhaltung: Φ ≤ P_pump/E_photon. Dicke-N² konzentriert die
  Emission in der ZEIT (Burst), erzeugt keine Energie — die
  Raten-Obergrenze ist kollektivgrößen-UNABHÄNGIG.
- Burst-Lemma: Absorptionswahrscheinlichkeit pro Molekül pro Burst
  = N·σ (ungesättigt; N·σ ≤ N_trp·σ ≪ 1) → Turnover = f·N·σ·QY
  = Φ_cap·σ·QY — N kürzt sich heraus; schritt-integrierte Photochemie
  ist burst-invariant. Die N²-Peak-Rate ist für die Chemie irrelevant.
- Geometrie: isotrope Punktquelle mit Absorption (Konvention
  superradiance.flux_at_cm2).
- Photochemie-Kriterium: Damköhler-Fenster [1e-4, 0.1] pro Molekül pro
  1-ms-Schritt ⇔ [0.1, 100] 1/s (iter-11/14, registriert).

Telemetrie-Konvention: gemeldet wird die EFFECTIVE Rate
min(declared, pump_cap) — die schritt-integrierte photochemisch
bindende Größe. Burst-Peaks sind an Sync-Sampling nicht auflösbar und
für das Fenster irrelevant (Lemma).
"""

from __future__ import annotations

from dataclasses import dataclass

from cellsim.modules.kick_coupling import DELTA_G_ATP_J
from cellsim.modules.superradiance import (
    ABSORPTION_LENGTH_NM,
    QUANTUM_YIELD_UVC,
    SIGMA_TRP_CM2,
    TRYPTOPHAN_WAVELENGTH_NM,
    aggregate_photon_rate_per_s,
    damkoehler_window_per_step,
    flux_at_cm2,
    photon_energy_j,
    turnover_per_second,
)

# --- registrierte Trp-Inventar-Anker (HYPOTHESE, MGENITALIUM-Proxy) ---
N_PROTEINS_SYN3A = 455             # protein-codierend (UniProt UP000326712)
MEAN_LENGTH_MGENITALIUM_AA = 340.0 # mittlere Proteinlänge (M. genitalium, Proxy)
TRP_FREQUENCY_HYPOTHESE = 1.3e-2   # Trp-Häufigkeit (seltenste kanonische AS)
N_TRP_EST_PER_CELL = round(
    N_PROTEINS_SYN3A * MEAN_LENGTH_MGENITALIUM_AA * TRP_FREQUENCY_HYPOTHESE
)


def n_trp_estimate() -> int:
    """Registrierte Trp-Inventar-Schätzung (HYPOTHESE): Proteome × Länge × Frequenz."""
    return N_TRP_EST_PER_CELL


def pump_cap_photons_per_s(
    atp_hydrolysis_per_s: float,
    wavelength_nm: float = TRYPTOPHAN_WAVELENGTH_NM,
) -> float:
    """Energieerhaltungs-Obergrenze: Φ_cap = P_pump/E_photon.

    P_pump = atp_hydrolysis_per_s · ΔG_ATP (100 % der metabolischen
    Leistung in den photonischen Kanal); E_photon = h·c/λ.
    Ein 280-nm-Photon kostet ~8.6 ΔG_ATP.
    """
    if atp_hydrolysis_per_s < 0:
        raise ValueError("atp_hydrolysis_per_s >= 0")
    power_w = atp_hydrolysis_per_s * DELTA_G_ATP_J
    return power_w / photon_energy_j(wavelength_nm)


@dataclass(frozen=True)
class PhotonicSource:
    """Optionale Superradianz-Quelle im HybridDriver (iter-23).

    Default: EIN Kollektiv mit dem geschätzten Gesamt-Trp-Bestand,
    1 Burst/s (produktions-plausibel, NICHT pump-sättigend).
    """

    n_clusters: int = 1
    n_per_cluster: int = N_TRP_EST_PER_CELL
    f_burst_hz: float = 1.0
    wavelength_nm: float = TRYPTOPHAN_WAVELENGTH_NM
    target_distance_nm: float = 100.0
    atp_hydrolysis_per_s: float = 1.0e6   # EMParams-Anker
    absorption_length_nm: float = ABSORPTION_LENGTH_NM

    def __post_init__(self) -> None:
        if self.n_clusters < 1:
            raise ValueError("n_clusters >= 1")
        if self.n_per_cluster < 1:
            raise ValueError("n_per_cluster >= 1")
        if self.f_burst_hz < 0:
            raise ValueError("f_burst_hz >= 0")
        if self.wavelength_nm <= 0:
            raise ValueError("wavelength_nm > 0")
        if self.target_distance_nm <= 0:
            raise ValueError("target_distance_nm > 0")
        if self.atp_hydrolysis_per_s < 0:
            raise ValueError("atp_hydrolysis_per_s >= 0")
        if self.absorption_length_nm <= 0:
            raise ValueError("absorption_length_nm > 0")

    @property
    def declared_rate_per_s(self) -> float:
        """M·N·f (superradiance.aggregate_photon_rate_per_s)."""
        return aggregate_photon_rate_per_s(
            self.n_clusters, self.n_per_cluster, self.f_burst_hz
        )

    @property
    def pump_cap_per_s(self) -> float:
        return pump_cap_photons_per_s(self.atp_hydrolysis_per_s, self.wavelength_nm)

    @property
    def effective_rate_per_s(self) -> float:
        """min(declared, pump_cap) — registrierte Telemetrie-Konvention."""
        return min(self.declared_rate_per_s, self.pump_cap_per_s)

    @property
    def pump_cap_active(self) -> bool:
        return self.declared_rate_per_s > self.pump_cap_per_s

    @property
    def flux_at_target_cm2(self) -> float:
        """Φ(r_target) = rate·exp(−r/r_abs)/(4πr²) in photons/cm²/s."""
        return flux_at_cm2(
            self.effective_rate_per_s,
            self.target_distance_nm,
            self.absorption_length_nm,
        )

    @property
    def turnover_at_target_per_s(self) -> float:
        """Photochemischer Turnover pro Molekül = Φ·σ·QY."""
        return turnover_per_second(self.flux_at_target_cm2)

    def rates(self) -> dict[str, float]:
        """Telemetrie für den HybridDriver (run.csv-Spalten).

        photon_pump_capped wird als 0.0/1.0 gemeldet (CSV-Schema).
        """
        return {
            "photon_rate_per_s": self.effective_rate_per_s,
            "photon_flux_cm2_s": self.flux_at_target_cm2,
            "photochem_turnover_per_s": self.turnover_at_target_per_s,
            "photon_pump_capped": 1.0 if self.pump_cap_active else 0.0,
        }


def window_bounds_per_s(dt_s: float = 1e-3) -> tuple[float, float]:
    """Damköhler-Fenster pro Sekunde skaliert (iter-11/14)."""
    return damkoehler_window_per_step(dt_s)


def classify_window(
    turnover_per_s: float,
    dt_s: float = 1e-3,
) -> str:
    """Klassifiziere Turnover gegen das registrierte Fenster.

    Rückgabe: "below" (unter unterer Grenze), "in", "above".
    """
    lo, hi = window_bounds_per_s(dt_s)
    if turnover_per_s < lo:
        return "below"
    if turnover_per_s > hi:
        return "above"
    return "in"


def burst_invariance_check(
    source: PhotonicSource,
    n_emitters: int,
    f_burst_hz: float,
) -> float:
    """Burst-Route des Turnovers (Lemma-Konvention, analytisch).

    Pro Burst absorbiert ein Molekül N·g(r)·σ Photonen (ungesättigt,
    N·σ ≪ 1); mit f Bursts/s:
      turnover_burst = f · N · g(r) · σ · QY.
    Mit pump-konsistenter f = Φ_cap/N ist das ≡ Φ_cap·g·σ·QY
    (Average-Route) — N kürzt sich. Rückgabe: burst-Route-Turnover.
    g(r) via flux_at_cm2(1.0, r) — dieselbe Geometrie-Konvention wie
    die Average-Route (keine Formel-Duplikation).
    """
    if n_emitters < 1:
        raise ValueError("n_emitters >= 1")
    if f_burst_hz < 0:
        raise ValueError("f_burst_hz >= 0")
    g = flux_at_cm2(
        1.0, source.target_distance_nm, source.absorption_length_nm
    )
    per_burst_absorbed = n_emitters * g * SIGMA_TRP_CM2
    if per_burst_absorbed >= 1.0:
        raise ValueError("Regime verletzt: N·g·σ >= 1 (Sättigung)")
    return f_burst_hz * per_burst_absorbed * QUANTUM_YIELD_UVC
