"""订单状态机单元测试。"""

import pytest
from src.core.order_state import OrderStateMachine, OrderStatus, InvalidTransitionError


def test_order_status_enum_exists():
    """测试 OrderStatus 枚举存在。"""
    assert OrderStatus.PENDING.value == "PENDING"
    assert OrderStatus.COLLECTED.value == "COLLECTED"
    assert OrderStatus.TRANSIT.value == "TRANSIT"
    assert OrderStatus.STORED.value == "STORED"
    assert OrderStatus.DELIVERING.value == "DELIVERING"
    assert OrderStatus.COMPLETED.value == "COMPLETED"
    assert OrderStatus.CANCELLED.value == "CANCELLED"
    assert OrderStatus.EXCEPTION.value == "EXCEPTION"


def test_state_machine_valid_transition():
    """测试有效状态转换。"""
    sm = OrderStateMachine("PENDING")

    # PENDING -> COLLECTED
    sm.transition("COLLECTED")
    assert sm.current_status == "COLLECTED"

    # COLLECTED -> TRANSIT
    sm.transition("TRANSIT")
    assert sm.current_status == "TRANSIT"

    # TRANSIT -> STORED
    sm.transition("STORED")
    assert sm.current_status == "STORED"

    # STORED -> DELIVERING
    sm.transition("DELIVERING")
    assert sm.current_status == "DELIVERING"

    # DELIVERING -> COMPLETED
    sm.transition("COMPLETED")
    assert sm.current_status == "COMPLETED"


def test_state_machine_invalid_transition():
    """测试无效状态转换。"""
    sm = OrderStateMachine("PENDING")

    with pytest.raises(InvalidTransitionError) as exc_info:
        sm.transition("COMPLETED")  # 跳过中间状态

    assert "从 PENDING 到 COMPLETED 的转换无效" in str(exc_info.value)
    assert sm.current_status == "PENDING"


def test_state_machine_terminal_states():
    """测试终止状态不可转换。"""
    # COMPLETED 状态
    sm = OrderStateMachine("COMPLETED")
    with pytest.raises(InvalidTransitionError):
        sm.transition("CANCELLED")
    assert sm.current_status == "COMPLETED"  # COMPLETED 保持不变

    # CANCELLED 状态
    sm = OrderStateMachine("CANCELLED")
    with pytest.raises(InvalidTransitionError):
        sm.transition("PENDING")
    assert sm.current_status == "CANCELLED"  # CANCELLED 保持不变


def test_transition_invalid_target_state():
    """测试转换到无效目标状态。"""
    machine = OrderStateMachine("PENDING")
    with pytest.raises(InvalidTransitionError) as exc_info:
        machine.transition("INVALID_STATUS")
    assert "无效的目标状态" in str(exc_info.value)


def test_transition_from_invalid_initial_state():
    """测试从无效初始状态转换。"""
    with pytest.raises(InvalidTransitionError) as exc_info:
        OrderStateMachine("INVALID_STATUS")
    assert "无效的初始状态" in str(exc_info.value)


def test_exception_to_terminal():
    """测试从EXCEPTION状态可以转换到终态。"""
    sm = OrderStateMachine("EXCEPTION")
    sm.transition("COMPLETED")
    assert sm.current_status == "COMPLETED"

    sm2 = OrderStateMachine("EXCEPTION")
    sm2.transition("CANCELLED")
    assert sm2.current_status == "CANCELLED"


def test_transition_invalid_target_state():
    """测试转换到无效目标状态。"""
    machine = OrderStateMachine("PENDING")
    with pytest.raises(InvalidTransitionError) as exc_info:
        machine.transition("INVALID_STATUS")
    assert "无效的目标状态" in str(exc_info.value)


def test_transition_from_invalid_initial_state():
    """测试从无效初始状态转换。"""
    with pytest.raises(InvalidTransitionError) as exc_info:
        OrderStateMachine("INVALID_STATUS")
    assert "无效的初始状态" in str(exc_info.value)


def test_exception_to_terminal():
    """测试从EXCEPTION状态可以转换到终态。"""
    sm = OrderStateMachine("EXCEPTION")
    sm.transition("COMPLETED")
    assert sm.current_status == "COMPLETED"

    sm2 = OrderStateMachine("EXCEPTION")
    sm2.transition("CANCELLED")
    assert sm2.current_status == "CANCELLED"