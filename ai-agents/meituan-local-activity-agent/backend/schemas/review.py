from typing import TypedDict, List, Optional, Dict


class AgentReview(TypedDict):
    """单个 Agent 对单个候选方案的评审结果。"""
    agent: str
    score: float
    veto: bool
    veto_reason: Optional[str]
    strengths: List[str]
    concerns: List[str]
    suggestions: List[str]


class RoundReviews(TypedDict):
    """一轮评审的汇总结果。

    reviews 结构为嵌套 Dict：
    {
        "体验Agent": {"plan_1": AgentReview, "plan_2": AgentReview},
        "安全Agent": {"plan_1": AgentReview, "plan_2": AgentReview},
        ...
    }
    外层 key 为 agent_name，内层 key 为 candidate_id。
    """
    round: int
    reviews: Dict[str, Dict[str, AgentReview]]
    summary: str
