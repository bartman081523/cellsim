"""Tests für L1/MES-Stub."""

from __future__ import annotations

from cellsim.modules.mes import (
    CellState,
    MESAdapter,
    MESParams,
)


def test_mes_initial_state_is_healthy() -> None:
    mes = MESAdapter()
    assert mes.state.cell_state == CellState.HEALTHY


def test_mes_becomes_stressed_on_low_atp() -> None:
    mes = MESAdapter(MESParams(atp_min_mM=1.0, atp_critical_mM=0.2))
    mes.step(dt_s=1.0, atp_mM=0.5)
    assert mes.state.cell_state in (CellState.DAMAGED, CellState.STRESSED)


def test_mes_becomes_dead_on_critical_atp() -> None:
    mes = MESAdapter(MESParams(atp_critical_mM=0.5))
    mes.step(dt_s=1.0, atp_mM=0.05)
    assert mes.state.cell_state == CellState.DEAD


def test_mes_recovers_from_repairing_to_healthy() -> None:
    mes = MESAdapter()
    # Erst Schaden verursachen
    mes.step(dt_s=1.0, atp_mM=0.2)  # sehr niedriges ATP → DAMAGED
    # Dann mit ATP-Input repairen
    for _ in range(20):
        mes.step(dt_s=1.0, atp_mM=3.0)
    assert mes.state.cell_state == CellState.HEALTHY


def test_mes_trigger_repair_only_when_damaged() -> None:
    mes = MESAdapter()
    # Alle Sub-Networks bei Health=1.0: trigger_repair ist no-op
    assert mes.trigger_repair() is False
    # Manually beschädige ein Sub-Network
    from cellsim.modules.mes import SubNetwork

    mes.state.sub_networks["energy"] = SubNetwork(
        name="energy", health_score=0.1,
    )
    assert mes.trigger_repair() is True


def test_mes_is_alive() -> None:
    mes = MESAdapter()
    assert mes.is_alive()
    mes.state.cell_state = CellState.DEAD
    assert not mes.is_alive()


def test_mes_memory_smoothed() -> None:
    mes = MESAdapter()
    mes.step(dt_s=1.0, atp_mM=5.0)
    mes.step(dt_s=1.0, atp_mM=0.0)
    # Memory sollte exponentiell geglättet sein, nicht schlagartig
    assert 0.0 < mes.state.memory["atp_mM"] < 5.0
