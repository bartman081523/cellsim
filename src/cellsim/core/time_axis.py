"""Default-Zeitachsen — eine Quelle für dt und t_end."""

from __future__ import annotations

from dataclasses import dataclass

from cellsim.core.constants import (
    JCVI_CELL_CYCLE_S,
    ODE_DT_S_DEFAULT,
    RDME_DT_S_DEFAULT,
)


@dataclass(frozen=True)
class TimeAxis:
    """Diskrete Zeitachse für RDME und ODE."""

    t_start_s: float
    t_end_s: float
    dt_rdme_s: float
    dt_ode_s: float

    @property
    def n_rdme_steps(self) -> int:
        return int(round((self.t_end_s - self.t_start_s) / self.dt_rdme_s))

    @property
    def n_ode_steps(self) -> int:
        return int(round((self.t_end_s - self.t_start_s) / self.dt_ode_s))


def smoke_time_axis() -> TimeAxis:
    """60-s-Smoke-Test-Zeitachse."""
    return TimeAxis(
        t_start_s=0.0,
        t_end_s=60.0,
        dt_rdme_s=RDME_DT_S_DEFAULT,
        dt_ode_s=ODE_DT_S_DEFAULT,
    )


def full_cycle_time_axis() -> TimeAxis:
    """Volle 105-min-Zellzyklus-Zeitachse (für spätere Vektoren)."""
    return TimeAxis(
        t_start_s=0.0,
        t_end_s=JCVI_CELL_CYCLE_S,
        dt_rdme_s=RDME_DT_S_DEFAULT,
        dt_ode_s=ODE_DT_S_DEFAULT,
    )
