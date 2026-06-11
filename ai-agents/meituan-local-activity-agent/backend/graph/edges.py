from typing import Dict, Any


def error_router(state: Dict[str, Any]) -> str:
    """Stop the graph when a node has already produced an error."""
    if state.get("error"):
        return "FAILED"
    return "CONTINUE"


def safety_router(state: Dict[str, Any]) -> str:
    """安全路由：检查 round1_reviews 和 round2_reviews 中是否有安全否决。

    任一轮次中任何 Agent 对任何方案发出 veto，即触发重规划。
    重规划超过 2 次则标记为 FAILED。
    """
    if state.get("error"):
        return "FAILED"

    replan_count = state.get("replan_count", 0)

    # B5 修复：同时检查两个轮次，而非 `or` 短路跳过
    has_veto = False
    for round_key in ("round1_reviews", "round2_reviews"):
        round_reviews = state.get(round_key)
        if not round_reviews or "reviews" not in round_reviews:
            continue
        for agent_review in round_reviews["reviews"].values():
            if isinstance(agent_review, dict):
                if agent_review.get("veto"):
                    has_veto = True
                    break
                # agent_review 可能是 {candidate_id: review} 嵌套结构
                for review in agent_review.values():
                    if isinstance(review, dict) and review.get("veto"):
                        has_veto = True
                        break
            if has_veto:
                break
        if has_veto:
            break

    if has_veto:
        if replan_count >= 2:
            return "FAILED"
        return "REPLANNING"

    return "CONFIRMING"


def replan_router(state: Dict[str, Any]) -> str:
    """重规划路由：超过 2 次重规划则放弃。"""
    if state.get("error"):
        return "FAILED"

    replan_count = state.get("replan_count", 0)
    if replan_count >= 2:
        return "FAILED"
    return "BRAINSTORMING"


def executor_router(state: Dict[str, Any]) -> str:
    """执行路由：有 error 则标记失败。"""
    if state.get("error"):
        return "FAILED"
    return "COMPLETED"


def should_continue_brainstorm(state: Dict[str, Any]) -> str:
    """头脑风暴续控路由：决定是否进入第2轮评审。"""
    if state.get("error"):
        return "END"

    current_round = state.get("round", 0)
    reviews = state.get("round1_reviews")

    if current_round == 1 and not reviews:
        return "aggregate"

    if current_round >= 2:
        return "aggregate"

    return "continue"
