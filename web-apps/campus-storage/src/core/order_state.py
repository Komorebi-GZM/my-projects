"""订单状态机模块。"""

from enum import Enum
from dataclasses import dataclass


class OrderStatus(Enum):
    """订单状态枚举。"""
    PENDING = "PENDING"       # 待取件
    COLLECTED = "COLLECTED"   # 已取件
    TRANSIT = "TRANSIT"       # 运输中
    STORED = "STORED"         # 已入库
    DELIVERING = "DELIVERING" # 派送中
    COMPLETED = "COMPLETED"   # 已完成
    CANCELLED = "CANCELLED"   # 已取消
    EXCEPTION = "EXCEPTION"   # 异常


@dataclass
class InvalidTransitionError(Exception):
    """无效状态转换错误。"""
    message: str = "无效的状态转换"


class OrderStateMachine:
    """订单状态机。"""

    # 状态转换矩阵：当前状态（字符串） -> 允许的下一状态（字符串）
    TRANSITION_MATRIX = {
        "PENDING": ["COLLECTED", "CANCELLED", "EXCEPTION"],
        "COLLECTED": ["TRANSIT", "EXCEPTION"],
        "TRANSIT": ["STORED", "EXCEPTION"],
        "STORED": ["DELIVERING", "EXCEPTION"],
        "DELIVERING": ["COMPLETED", "EXCEPTION"],
        # 终止状态：不可转换
        "COMPLETED": [],
        "CANCELLED": [],
        "EXCEPTION": ["COMPLETED", "CANCELLED"],
    }

    def __init__(self, initial_status: str):
        """初始化状态机。"""
        try:
            self._current_status = OrderStatus(initial_status)
        except ValueError:
            raise InvalidTransitionError(f"无效的初始状态: {initial_status}")

    @property
    def current_status(self) -> str:
        """当前状态（字符串）。"""
        return self._current_status.value

    def transition(self, new_status: str):
        """转换到新状态。"""
        try:
            target_status = OrderStatus(new_status)
        except ValueError:
            raise InvalidTransitionError(f"无效的目标状态: {new_status}")

        # 检查是否为终止状态
        if self.current_status in ["COMPLETED", "CANCELLED"]:
            raise InvalidTransitionError(f"终止状态 {self.current_status} 不可转换")

        # 检查转换是否允许
        if target_status.value not in self.TRANSITION_MATRIX[self.current_status]:
            raise InvalidTransitionError(
                f"从 {self.current_status} 到 {target_status.value} 的转换无效"
            )

        self._current_status = target_status