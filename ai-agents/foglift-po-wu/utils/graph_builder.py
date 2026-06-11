from langgraph.graph import StateGraph, END
from utils.supervisor import AgentState, supervisor_node
from agents.agent_wrappers import (
    jd_analyst_node,
    jargon_translator_node,
    gap_analyst_node,
    coordinator_jd_node,
    position_resolver_node,
    ladder_planner_node,
    skill_recommender_node,
    resource_retriever_node,
    coordinator_path_node,
    interviewer_node,
    answer_analyst_node,
    cheerleader_node,
    coordinator_int_node,
)





def _build_main_graph() -> StateGraph:
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor_node)

    g.add_node("jd_analyst", jd_analyst_node)
    g.add_node("jargon_translator", jargon_translator_node)
    g.add_node("gap_analyst", gap_analyst_node)
    g.add_node("coordinator_jd", coordinator_jd_node)

    g.add_node("position_resolver", position_resolver_node)
    g.add_node("ladder_planner", ladder_planner_node)
    g.add_node("skill_recommender", skill_recommender_node)
    g.add_node("resource_retriever", resource_retriever_node)
    g.add_node("coordinator_path", coordinator_path_node)

    g.add_node("interviewer", interviewer_node)
    g.add_node("answer_analyst", answer_analyst_node)
    g.add_node("cheerleader", cheerleader_node)
    g.add_node("coordinator_int", coordinator_int_node)

    g.set_entry_point("supervisor")

    g.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next_node", "jd_analyst"),
        {
            "jd_analyst": "jd_analyst",
            "position_resolver": "position_resolver",
            "interviewer": "interviewer",
            "answer_analyst": "answer_analyst",
        }
    )

    g.add_edge("jd_analyst", "jargon_translator")
    g.add_edge("jargon_translator", "gap_analyst")
    g.add_edge("gap_analyst", "coordinator_jd")
    g.add_edge("coordinator_jd", END)

    g.add_edge("position_resolver", "ladder_planner")
    g.add_edge("ladder_planner", "skill_recommender")
    g.add_edge("skill_recommender", "resource_retriever")
    g.add_edge("resource_retriever", "coordinator_path")
    g.add_edge("coordinator_path", END)

    g.add_edge("interviewer", END)

    g.add_edge("answer_analyst", "cheerleader")
    g.add_edge("cheerleader", "coordinator_int")
    g.add_edge("coordinator_int", END)

    return g


def build_graph():
    return _build_main_graph().compile()