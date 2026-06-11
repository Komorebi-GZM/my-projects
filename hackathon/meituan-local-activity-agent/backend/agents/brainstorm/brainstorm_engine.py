import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from agents.brainstorm.experience_agent import ExperienceAgent
from agents.brainstorm.safety_agent import SafetyAgent
from agents.brainstorm.efficiency_agent import EfficiencyAgent
from agents.brainstorm.budget_agent import BudgetAgent

logger = structlog.get_logger()


def run_brainstorm_round(
    candidates: List[Dict],
    round_num: int,
    intent: Dict,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """并行执行一轮头脑风暴评审。

    D7 修复：单个 Agent 失败时重试 1 次（符合 DEV_GUIDE 4.5.2 规范），
    仍失败则返回默认安全评分（score=5.0, veto=False）。
    """
    agents = {
        "体验Agent": ExperienceAgent(),
        "安全Agent": SafetyAgent(),
        "效率Agent": EfficiencyAgent(),
        "预算Agent": BudgetAgent()
    }

    reviews: Dict[str, Dict[str, Any]] = {}

    def review_candidate(agent_name: str, agent, candidate: Dict) -> tuple:
        # D7 修复：失败后重试 1 次
        try:
            review = agent.review(candidate, intent, trace_id)
            return agent_name, candidate.get("id", "unknown"), review
        except Exception as e:
            logger.warning(
                "brainstorm_agent_retry",
                trace_id=trace_id,
                round=round_num,
                agent=agent_name,
                candidate_id=candidate.get("id", "unknown"),
                error=str(e),
            )
            try:
                review = agent.review(candidate, intent, trace_id)
                return agent_name, candidate.get("id", "unknown"), review
            except Exception as retry_error:
                logger.error(
                    "brainstorm_agent_failed",
                    trace_id=trace_id,
                    round=round_num,
                    agent=agent_name,
                    candidate_id=candidate.get("id", "unknown"),
                    error=str(retry_error),
                )
                return agent_name, candidate.get("id", "unknown"), {
                    "agent": agent_name,
                    "score": 5.0,
                    "veto": False,
                    "veto_reason": None,
                    "strengths": [],
                    "concerns": [f"评审失败（已重试1次仍失败）: {retry_error}"],
                    "suggestions": []
                }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for agent_name, agent in agents.items():
            for candidate in candidates:
                futures.append(
                    executor.submit(review_candidate, agent_name, agent, candidate)
                )

        for future in as_completed(futures):
            agent_name, candidate_id, review = future.result()
            if agent_name not in reviews:
                reviews[agent_name] = {}
            reviews[agent_name][candidate_id] = review

    logger.info(
        "brainstorm_round_complete",
        trace_id=trace_id,
        round=round_num,
        agents_reviewed=len(reviews),
        candidates_reviewed=len(candidates),
    )

    return {
        "round": round_num,
        "reviews": reviews,
        "summary": f"Round {round_num} completed"
    }
