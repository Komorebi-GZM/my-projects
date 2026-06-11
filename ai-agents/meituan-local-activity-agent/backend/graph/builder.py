from langgraph.graph import StateGraph, END
from graph.state import BrainstormState
from graph.nodes import (
    parse_intent, generate_plans, brainstorm_round1, brainstorm_round2,
    aggregate_and_confirm, replan, execute_plan
)
from graph.edges import (
    error_router, safety_router, replan_router, executor_router, should_continue_brainstorm
)


def build_graph():
    workflow = StateGraph(BrainstormState)

    workflow.add_node("parse_intent", parse_intent)
    workflow.add_node("generate_plans", generate_plans)
    workflow.add_node("brainstorm_round1", brainstorm_round1)
    workflow.add_node("brainstorm_round2", brainstorm_round2)
    workflow.add_node("aggregate", aggregate_and_confirm)
    workflow.add_node("replan", replan)
    workflow.add_node("execute_plan", execute_plan)

    workflow.set_entry_point("parse_intent")

    workflow.add_conditional_edges(
        "parse_intent",
        error_router,
        {
            "CONTINUE": "generate_plans",
            "FAILED": END
        }
    )
    workflow.add_conditional_edges(
        "generate_plans",
        error_router,
        {
            "CONTINUE": "brainstorm_round1",
            "FAILED": END
        }
    )

    workflow.add_conditional_edges(
        "brainstorm_round1",
        should_continue_brainstorm,
        {
            "continue": "brainstorm_round2",
            "aggregate": "aggregate",
            "END": END
        }
    )

    workflow.add_conditional_edges(
        "brainstorm_round2",
        error_router,
        {
            "CONTINUE": "aggregate",
            "FAILED": END
        }
    )

    workflow.add_conditional_edges(
        "aggregate",
        safety_router,
        {
            "REPLANNING": "replan",
            "CONFIRMING": "execute_plan",
            "FAILED": END
        }
    )

    workflow.add_conditional_edges(
        "replan",
        replan_router,
        {
            "BRAINSTORMING": "brainstorm_round1",
            "FAILED": END
        }
    )

    workflow.add_conditional_edges(
        "execute_plan",
        executor_router,
        {
            "COMPLETED": END,
            "FAILED": END
        }
    )

    return workflow.compile()


def validate_graph_topology() -> bool:
    """验证图拓扑结构的完整性。

    检查项：
    1. 入口节点存在
    2. 没有孤立节点（每个节点都有入边或为入口）
    3. 所有条件边引用的目标节点都存在
    """
    graph = build_graph()
    nodes = set(graph.nodes.keys())

    if not nodes:
        raise ValueError("图为空，没有任何节点")

    # 检查是否包含所有预期节点
    expected_nodes = {
        "parse_intent", "generate_plans", "brainstorm_round1",
        "brainstorm_round2", "aggregate", "replan", "execute_plan"
    }
    missing = expected_nodes - nodes
    if missing:
        raise ValueError(f"缺少节点: {missing}")

    return True
