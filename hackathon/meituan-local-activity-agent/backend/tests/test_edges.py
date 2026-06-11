"""edges.py 路由函数单元测试。

注意：使用 importlib 直接导入 edges 模块，避免触发 graph/__init__.py 的导入链。
"""
import sys
import types
import importlib
import pytest


# 直接加载 edges 模块，绕过 graph 包的 __init__.py
def _import_edges():
    """直接导入 graph/edges.py 模块。"""
    # 确保 graph 包目录在 path 中
    import os
    graph_dir = os.path.join(os.path.dirname(__file__), "..")
    if graph_dir not in sys.path:
        sys.path.insert(0, graph_dir)

    # 创建 graph 包的 stub（避免 __init__.py 的导入链）
    if "graph" not in sys.modules:
        graph_pkg = types.ModuleType("graph")
        graph_pkg.__path__ = [os.path.join(os.path.dirname(__file__), "..", "graph")]
        sys.modules["graph"] = graph_pkg

    return importlib.import_module("graph.edges")


edges = _import_edges()
safety_router = edges.safety_router
replan_router = edges.replan_router
executor_router = edges.executor_router
should_continue_brainstorm = edges.should_continue_brainstorm
error_router = edges.error_router


class TestErrorRouter:
    """测试通用错误路由。"""

    def test_with_error_returns_failed(self):
        assert error_router({"error": "boom"}) == "FAILED"

    def test_without_error_returns_continue(self):
        assert error_router({"error": None}) == "CONTINUE"


class TestSafetyRouter:
    """测试 safety_router 安全路由逻辑。"""

    def test_no_reviews_returns_confirming(self):
        state = {"round1_reviews": None, "round2_reviews": None}
        assert safety_router(state) == "CONFIRMING"

    def test_round1_veto_triggers_replanning(self):
        state = {
            "round1_reviews": {
                "round": 1,
                "reviews": {
                    "安全Agent": {
                        "plan_1": {"agent": "安全Agent", "score": 3, "veto": True, "veto_reason": "不安全"}
                    }
                }
            },
            "round2_reviews": None,
            "replan_count": 0,
        }
        assert safety_router(state) == "REPLANNING"

    def test_flat_veto_triggers_replanning(self):
        state = {
            "round1_reviews": {
                "round": 1,
                "reviews": {
                    "安全Agent": {"agent": "安全Agent", "score": 2, "veto": True, "veto_reason": "风险"}
                }
            },
            "replan_count": 0,
        }
        assert safety_router(state) == "REPLANNING"

    def test_round2_veto_triggers_replanning(self):
        state = {
            "round1_reviews": None,
            "round2_reviews": {
                "round": 2,
                "reviews": {
                    "安全Agent": {
                        "plan_1": {"agent": "安全Agent", "score": 3, "veto": True, "veto_reason": "不安全"}
                    }
                }
            },
            "replan_count": 0,
        }
        assert safety_router(state) == "REPLANNING"

    def test_both_rounds_checked_round1_veto(self):
        """B5 修复验证：round2 无 veto 时仍检查 round1 的 veto。"""
        state = {
            "round1_reviews": {
                "round": 1,
                "reviews": {
                    "安全Agent": {
                        "plan_1": {"agent": "安全Agent", "score": 2, "veto": True, "veto_reason": "风险"}
                    }
                }
            },
            "round2_reviews": {
                "round": 2,
                "reviews": {
                    "体验Agent": {
                        "plan_1": {"agent": "体验Agent", "score": 8, "veto": False}
                    }
                }
            },
            "replan_count": 0,
        }
        # round1 有 veto → 应触发重规划
        assert safety_router(state) == "REPLANNING"

    def test_replan_exhausted_returns_failed(self):
        state = {
            "round1_reviews": {
                "round": 1,
                "reviews": {
                    "安全Agent": {
                        "plan_1": {"agent": "安全Agent", "score": 2, "veto": True}
                    }
                }
            },
            "replan_count": 2,
        }
        assert safety_router(state) == "FAILED"

    def test_no_veto_returns_confirming(self):
        state = {
            "round1_reviews": {
                "round": 1,
                "reviews": {
                    "体验Agent": {
                        "plan_1": {"agent": "体验Agent", "score": 8, "veto": False}
                    }
                }
            },
            "replan_count": 0,
        }
        assert safety_router(state) == "CONFIRMING"


class TestReplanRouter:
    """测试 replan_router 重规划路由。"""

    def test_under_limit_returns_brainstorming(self):
        assert replan_router({"replan_count": 0}) == "BRAINSTORMING"
        assert replan_router({"replan_count": 1}) == "BRAINSTORMING"

    def test_with_error_returns_failed(self):
        assert replan_router({"replan_count": 0, "error": "boom"}) == "FAILED"

    def test_exhausted_returns_failed(self):
        assert replan_router({"replan_count": 2}) == "FAILED"
        assert replan_router({"replan_count": 3}) == "FAILED"


class TestExecutorRouter:
    """测试 executor_router 执行路由。"""

    def test_no_error_returns_completed(self):
        assert executor_router({}) == "COMPLETED"

    def test_with_error_returns_failed(self):
        assert executor_router({"error": "something broke"}) == "FAILED"


class TestShouldContinueBrainstorm:
    """测试 should_continue_brainstorm 续控路由。"""

    def test_round0_returns_continue(self):
        assert should_continue_brainstorm({"round": 0}) == "continue"

    def test_round1_no_reviews_returns_aggregate(self):
        assert should_continue_brainstorm({"round": 1, "round1_reviews": None}) == "aggregate"

    def test_round1_with_reviews_returns_continue(self):
        assert should_continue_brainstorm({"round": 1, "round1_reviews": {"round": 1}}) == "continue"

    def test_round2_returns_aggregate(self):
        assert should_continue_brainstorm({"round": 2}) == "aggregate"

    def test_with_error_returns_end(self):
        assert should_continue_brainstorm({"round": 1, "error": "boom"}) == "END"
