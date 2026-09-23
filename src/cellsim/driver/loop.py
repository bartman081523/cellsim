"""Hybrid-Treiber (RDME + ODE + Chromosom + Membrane).

Kernidee aus 4DWCM §5.2: RDME in deterministischen Intervallen unterbrechen,
ODE synchronisieren, Membrane und Chromosom updaten.
"""

from __future__ import annotations

import csv
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from cellsim.adapters.chromosome import ChromosomeAdapter
from cellsim.adapters.ode import ODEAdapter
from cellsim.adapters.rdme import RDMEAdapter
from cellsim.core.rng import make_rng
from cellsim.core.time_axis import TimeAxis
from cellsim.modules.membrane import MembraneGeometry, MembraneParams

logger = logging.getLogger(__name__)


@dataclass
class DriverResult:
    """Aggregierte Telemetrie einer Simulation."""

    time_s: list[float] = field(default_factory=list)
    radius_nm: list[float] = field(default_factory=list)
    glucose_mM: list[float] = field(default_factory=list)
    atp_mM: list[float] = field(default_factory=list)
    particles_total: list[int] = field(default_factory=list)
    rdme_steps: list[int] = field(default_factory=list)
    sync_count: list[int] = field(default_factory=list)
    rg_nm: list[float] = field(default_factory=list)
    # Photonische Kopplung (iter-23): Nullen wenn keine Quelle konfiguriert
    photon_rate_per_s: list[float] = field(default_factory=list)
    photon_flux_cm2_s: list[float] = field(default_factory=list)
    photochem_turnover_per_s: list[float] = field(default_factory=list)
    photon_pump_capped: list[float] = field(default_factory=list)
    seed: int = 0
    walltime_s: float = 0.0


class HybridDriver:
    """Treiber-Loop mit RDME/ODE-Synchronisation."""

    def __init__(
        self,
        time_axis: TimeAxis,
        rdme: RDMEAdapter,
        ode: ODEAdapter,
        chromosome: ChromosomeAdapter,
        membrane: MembraneGeometry,
        sync_interval: int = 100,
        seed: int = 49582,
        volumes_angstrom3: dict[str, float] | None = None,
        mes: object | None = None,
        photonic: object | None = None,
    ) -> None:
        self.time_axis = time_axis
        self.rdme = rdme
        self.ode = ode
        self.chromosome = chromosome
        self.membrane = membrane
        self.sync_interval = sync_interval
        self.seed = seed
        self._sync_count = 0
        # Volumes aus volumes.tsv (VECTOR_BRIDGE_L2_L3 Erweiterung)
        self.volumes_angstrom3 = volumes_angstrom3 or {}
        # L1/MES-Stub (VECTOR_ROSEN_HORIZON)
        self.mes = mes
        # Photonische Kopplung (iter-23): Superradianz-Quelle (default OFF)
        self.photonic = photonic

    def run(self) -> DriverResult:
        """Führt die Simulation durch und sammelt Telemetrie."""
        t0 = time.monotonic()
        rng = make_rng(base_seed=self.seed)

        result = DriverResult(seed=self.seed)
        result.time_s.append(0.0)
        result.radius_nm.append(self.membrane.radius_nm)
        result.glucose_mM.append(float(self.ode.concentrations[0]))
        result.atp_mM.append(float(self.ode.concentrations[1]))
        result.particles_total.append(self.rdme.total_particles)
        result.rdme_steps.append(self.rdme.state.step_count)
        result.sync_count.append(0)
        result.rg_nm.append(self.chromosome.radius_of_gyration_nm)
        ph_rate, ph_flux, ph_turn, ph_cap = self._photonic_row()
        result.photon_rate_per_s.append(ph_rate)
        result.photon_flux_cm2_s.append(ph_flux)
        result.photochem_turnover_per_s.append(ph_turn)
        result.photon_pump_capped.append(ph_cap)

        n_steps = self.time_axis.n_rdme_steps
        for step in range(n_steps):
            self.rdme.step(self.time_axis.dt_rdme_s, rng)

            if step % self.sync_interval == 0:
                self.ode.step(self.time_axis.dt_ode_s, rng)
                self.membrane.update(self.time_axis.dt_ode_s)
                self.chromosome.couple_to_geometry(self.membrane.radius_nm)
                self.chromosome.step(self.time_axis.dt_ode_s, rng)
                self._sync_count += 1

                # Crowding-Index aus echten PDB-Volumina (VECTOR_BRIDGE_L2_L3 erweitert)
                crowding_index = self._compute_crowding_index()
                self.chromosome.couple_to_crowding(crowding_index)

                # L1/MES: Zellzustand prüfen, ggf. Kolimit-Reparatur auslösen
                if self.mes is not None:
                    atp_mM = float(self.ode.concentrations[1])
                    self.mes.step(dt_s=self.time_axis.dt_ode_s, atp_mM=atp_mM)
                    # Wenn DEAD, stoppen
                    if hasattr(self.mes, "is_alive") and not self.mes.is_alive():
                        logger.warning("L1/MES: Zelle DEAD bei t=%.2fs", self.membrane.t_s)
                        break

                # Telemetrie
                result.time_s.append(self.membrane.t_s)
                result.radius_nm.append(self.membrane.radius_nm)
                result.glucose_mM.append(float(self.ode.concentrations[0]))
                result.atp_mM.append(float(self.ode.concentrations[1]))
                result.particles_total.append(self.rdme.total_particles)
                result.rdme_steps.append(self.rdme.state.step_count)
                result.sync_count.append(self._sync_count)
                result.rg_nm.append(self.chromosome.radius_of_gyration_nm)
                ph_rate, ph_flux, ph_turn, ph_cap = self._photonic_row()
                result.photon_rate_per_s.append(ph_rate)
                result.photon_flux_cm2_s.append(ph_flux)
                result.photochem_turnover_per_s.append(ph_turn)
                result.photon_pump_capped.append(ph_cap)

        result.walltime_s = time.monotonic() - t0
        logger.info(
            "Run done: %d RDME steps, %d syncs, %.2fs walltime",
            self.rdme.state.step_count,
            self._sync_count,
            result.walltime_s,
        )
        return result


    def _photonic_row(self) -> tuple[float, float, float, float]:
        """Photonische Telemetrie (iter-23); Nullen ohne Quelle.

        Die Quelle liefert eine stationäre Rate (Energie-Cap-Konvention,
        min(declared, pump_cap)); schritt-integrierte Photochemie ist
        burst-invariant (Lemma in modules/photonic_coupling.py).
        """
        if self.photonic is None:
            return (0.0, 0.0, 0.0, 0.0)
        rates = self.photonic.rates()
        return (
            float(rates["photon_rate_per_s"]),
            float(rates["photon_flux_cm2_s"]),
            float(rates["photochem_turnover_per_s"]),
            float(rates["photon_pump_capped"]),
        )


    def _compute_crowding_index(self) -> float:
        """Berechnet Crowding-Index aus RDME-Counts + echten PDB-Volumina.

        crowding_index = Σ_i N_i · V_ex_i / V_voxel
        """
        from cellsim.modules.crowding import CrowdingParams, compute_crowding

        if not self.volumes_angstrom3:
            return 0.0
        voxel_edge_nm = 10.0
        # Aggregiere Counts zu einer Crowding-Map (sehr grob: über Voxel-Mittel)
        crowding_field = compute_crowding(
            particle_counts=self.rdme.state.voxels,
            volumes_angstrom3=self.volumes_angstrom3,
            voxel_edge_nm=voxel_edge_nm,
            params=CrowdingParams(),
        )
        return crowding_field.mean_crowding


def write_run_csv(result: DriverResult, out_path: Path) -> Path:
    """Schreibt den Zeit-Serien-Output als run.csv."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "time_s",
                "radius_nm",
                "glucose_mM",
                "atp_mM",
                "particles_total",
                "rdme_steps",
                "sync_count",
                "rg_nm",
                "photon_rate_per_s",
                "photon_flux_cm2_s",
                "photochem_turnover_per_s",
                "photon_pump_capped",
            ]
        )
        for i in range(len(result.time_s)):
            writer.writerow(
                [
                    f"{result.time_s[i]:.6f}",
                    f"{result.radius_nm[i]:.3f}",
                    f"{result.glucose_mM[i]:.6f}",
                    f"{result.atp_mM[i]:.6f}",
                    result.particles_total[i],
                    result.rdme_steps[i],
                    result.sync_count[i],
                    f"{result.rg_nm[i]:.3f}",
                    f"{result.photon_rate_per_s[i]:.6e}",
                    f"{result.photon_flux_cm2_s[i]:.6e}",
                    f"{result.photochem_turnover_per_s[i]:.6e}",
                    f"{result.photon_pump_capped[i]:.0f}",
                ]
            )
    logger.info("Wrote run.csv → %s", out_path)
    return out_path


def default_membrane() -> MembraneGeometry:
    return MembraneGeometry(MembraneParams())


def default_rdme(seed: int = 49582) -> RDMEAdapter:
    from cellsim.modules.reactions import default_registry

    return RDMEAdapter(registry=default_registry(), grid_shape=(6, 6, 6))


def default_ode() -> ODEAdapter:
    return ODEAdapter()


def default_chromosome(seed: int = 49582) -> ChromosomeAdapter:
    rng = np.random.default_rng(seed)
    return ChromosomeAdapter(n_beads=50, rng=rng)
