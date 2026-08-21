"""Membran-Wachstum: lineare Radius-Zeit-Funktion."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from cellsim.core.constants import (
    JCVI_CELL_RADIUS_NM_INITIAL,
    JCVI_CELL_RADIUS_NM_MATURE,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MembraneParams:
    """Konstanten des Membran-Wachstums."""

    radius_initial_nm: float = JCVI_CELL_RADIUS_NM_INITIAL
    radius_mature_nm: float = JCVI_CELL_RADIUS_NM_MATURE
    growth_rate_per_s: float = 0.01   # 1 % Radius pro s


class MembraneGeometry:
    """Zustandsbehaftete Radius-Zeit-Funktion."""

    def __init__(self, params: MembraneParams | None = None) -> None:
        self.params = params or MembraneParams()
        self._radius_nm = self.params.radius_initial_nm
        self._t_s = 0.0

    @property
    def radius_nm(self) -> float:
        return self._radius_nm

    @property
    def volume_nm3(self) -> float:
        # Kugel
        import math
        return (4.0 / 3.0) * math.pi * self._radius_nm**3

    @property
    def t_s(self) -> float:
        return self._t_s

    def update(self, dt_s: float) -> None:
        """Linear-Wachstum, abgeschnitten bei radius_mature_nm."""
        self._t_s += dt_s
        target = self.params.radius_initial_nm + self.params.growth_rate_per_s * self._t_s
        target = min(target, self.params.radius_mature_nm)
        # Monotonie erzwingen (numerisch robust)
        if target < self._radius_nm:
            return
        self._radius_nm = target

    def reset(self) -> None:
        self._radius_nm = self.params.radius_initial_nm
        self._t_s = 0.0
