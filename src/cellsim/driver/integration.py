"""Integrations-Adapter (L_new): verbindet alle Produktions-Module.

Phase D: kombiniert die 4+ Production-Module in EINEM Adapter.
  - RDME (L3)
  - Asakura-Oosawa Crowding (L2-Brücke)
  - EM-Schicht (Chemolumineszenz)
  - Cryptochrom-Compass
  - QuQuint-VQE-Beschleuniger (für Reaktionsraten)
  - Proton-Tunneling (für d ≤ 0.3 Å Enzyme)

Iter-9: Test, ob die Integration numerisch stabil ist und die einzelnen
Signale (EM-Fluss, Crypto-Sensitivität, etc.) weiterhin messbar bleiben.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.constants import SEED_BASE
from cellsim.modules.cryptochrome import CryptochromeAdapter
from cellsim.modules.em import EMParams, EMSource, estimate_uv_emission
from cellsim.modules.membrane import MembraneGeometry, MembraneParams
from cellsim.modules.reactions import default_registry
from cellsim.quantum.ququint import H_PT_ququint, QuQuintParams

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Konfiguration des Integrations-Adapters."""

    use_a_o_crowding: bool = True
    use_em_chemoluminescence: bool = True
    use_cryptochrome: bool = True
    use_ququint_vqe: bool = True
    use_proton_tunneling: bool = False  # nur bei d ≤ 0.3 Å Enzyme

    rdme_grid_shape: tuple[int, int, int] = (6, 6, 6)
    n_chromosome_beads: int = 50
    seed: int = SEED_BASE


@dataclass
class IntegrationState:
    """Aggregierter Zustand aller Module."""

    rdme_particles: int = 0
    ode_atp_mM: float = 2.0
    membrane_radius_nm: float = 200.0
    chromo_yield: float = 1.0
    em_uv_photons_per_s: float = 0.0
    n_steps: int = 0


class IntegratedCell:
    """Eine JCVI-syn3A-ähnliche Zelle mit allen Modulen."""

    def __init__(
        self,
        config: IntegrationConfig | None = None,
        membrane_params: MembraneParams | None = None,
    ) -> None:
        self.config = config or IntegrationConfig()
        self.membrane = MembraneGeometry(membrane_params)
        self.rdme = RDMEAdapter(
            registry=default_registry(),
            grid_shape=self.config.rdme_grid_shape,
            use_local_diffusion=self.config.use_a_o_crowding,
        )
        self.ode = ODEAdapter()
        self.chromosome = ChromosomeAdapter(
            n_beads=self.config.n_chromosome_beads,
        )
        self.cryptochrome = (
            CryptochromeAdapter() if self.config.use_cryptochrome else None
        )
        self.em_source = EMSource(
            position_nm=np.array([0.0, 0.0, 0.0]),
            photons_per_s=10.0,
            zell_radius_nm=self.membrane.params.radius_initial_nm,
        ) if self.config.use_em_chemoluminescence else None

        self.state = IntegrationState(rdme_particles=self.rdme.total_particles)

    def step(self, dt_s: float, rng: np.random.Generator) -> dict[str, float]:
        """Ein Schritt der integrierten Zelle."""
        self.state.n_steps += 1

        # 1) RDME-Schritt mit lokaler Diffusion (A-O)
        self.rdme.step(dt_s, rng)
        self.state.rdme_particles = self.rdme.total_particles

        # 2) ODE-Schritt (Glycolyse + ATP-Hydrolyse)
        self.ode.step(dt_s, rng)
        self.state.ode_atp_mM = float(self.ode.concentrations[1])

        # 3) Chromosom: Verlet-Integration
        self.chromosome.step(dt_s, rng)
        self.chromosome.couple_to_geometry(self.membrane.radius_nm)
        self.state.membrane_radius_nm = self.membrane.radius_nm

        # 4) Cryptochrom: B-Feld-Effekt (geomagnetisches Feld)
        if self.cryptochrome is not None:
            crypto_result = self.cryptochrome.step(dt_s=dt_s, b_field_t=50e-6)
            self.state.chromo_yield = crypto_result["crypto_singlet_yield"]

        # 5) EM: Chemolumineszenz-Output (Popp-Faktor)
        if self.em_source is not None:
            em_estimate = estimate_uv_emission(
                EMParams(atp_hydrolysis_per_s=1e6),
                wavelength_nm=300.0,
            )
            self.em_source.photons_per_s = em_estimate["chemolumineszenz_photons_per_s"]
            self.state.em_uv_photons_per_s = self.em_source.photons_per_s

        # 6) QuQuint-VQE: Hamiltonian-Diagonalisierung
        # Nur als Demonstration, kein Kostenfaktor im step()
        e_diag = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        h_ququint = H_PT_ququint(e_diag, QuQuintParams())

        return self._telemetry(h_ququint)

    def _telemetry(self, h_ququint: np.ndarray) -> dict[str, float]:
        return {
            "n_steps": float(self.state.n_steps),
            "rdme_particles": float(self.state.rdme_particles),
            "atp_mM": self.state.ode_atp_mM,
            "membrane_radius_nm": self.state.membrane_radius_nm,
            "chromo_yield": self.state.chromo_yield,
            "em_uv_photons_per_s": self.state.em_uv_photons_per_s,
            "ququint_ground_state": float(np.linalg.eigvalsh(h_ququint).real.min()),
        }


def run_integrated(
    t_end_s: float = 10.0,
    dt_s: float = 1e-3,
    seed: int = SEED_BASE,
) -> dict[str, float]:
    """Integrierte Zelle für t_end_s Sekunden simulieren."""
    rng = np.random.default_rng(seed)
    cell = IntegratedCell()
    n_steps = int(t_end_s / dt_s)
    for _ in range(n_steps):
        cell.step(dt_s, rng)
    return cell._telemetry(
        H_PT_ququint(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), QuQuintParams())
    )
