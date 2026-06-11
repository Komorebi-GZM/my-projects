import uuid
import time
import structlog
from typing import Dict, Any, Tuple, Optional, List

logger = structlog.get_logger()

# N5: Session TTL（秒），默认 1 小时
SESSION_TTL_SECONDS = 3600


class SessionManager:
    """会话管理器：存储和管理用户会话状态，支持 TTL 自动过期。"""

    def __init__(self, ttl_seconds: int = SESSION_TTL_SECONDS):
        self.sessions: Dict[str, Dict] = {}
        self.ttl_seconds = ttl_seconds

    def _cleanup_expired(self):
        """清理已过期的会话。"""
        now = time.time()
        expired = [
            sid for sid, data in self.sessions.items()
            if now - data.get("created_at", 0) > self.ttl_seconds
        ]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.debug("sessions_cleaned", expired_count=len(expired))

    def create_session(self, user_input: str) -> str:
        self._cleanup_expired()
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_input": user_input,
            "state": None,
            "created_at": time.time()
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        self._cleanup_expired()
        session = self.sessions.get(session_id)
        if session and (time.time() - session.get("created_at", 0)) > self.ttl_seconds:
            del self.sessions[session_id]
            return None
        return session


session_manager = SessionManager()


def build_graph():
    # Local import avoids a circular import: graph.nodes imports aggregate_reviews from this module.
    from graph.builder import build_graph as _build_graph

    return _build_graph()


def aggregate_reviews(
    round1: Optional[Dict],
    round2: Optional[Dict],
    candidates: List
) -> Tuple[float, Optional[Dict]]:
    """汇总多轮评审结果，通过加权平均计算最优方案。

    算法说明：
    1. 遍历所有轮次的所有 Agent 评分，收集每个 candidate_id 的评分列表
    2. 对于同一 Agent 在 R1 和 R2 都评分的情况，取其**最后出现的评分**（R2 优先）
       — 这样避免 R1+R2 重复累加导致权重失衡
    3. 使用加权平均计算最终分数，权重：体验 0.30 / 安全 0.25 / 效率 0.20 / 预算 0.25
    4. 有 veto 的方案得分为 0

    Args:
        round1: 第1轮评审结果 {"round": 1, "reviews": {agent_name: {candidate_id: review}}}
        round2: 第2轮评审结果
        candidates: 候选方案列表

    Returns:
        (最优分数, 最优方案 Dict)
    """
    if not candidates:
        return 0.0, None

    weights = {"体验Agent": 0.30, "安全Agent": 0.25, "效率Agent": 0.20, "预算Agent": 0.25}

    # B4 修复：每个 Agent 每个方案只取最后一次评分（R2 覆盖 R1）
    latest_scores: Dict[str, Dict[str, float]] = {}  # {candidate_id: {agent_name: score}}

    for round_data in [round1, round2]:
        if not round_data:
            continue
        for agent_name, agent_reviews in round_data.get("reviews", {}).items():
            if not isinstance(agent_reviews, dict):
                continue
            if _is_flat_review(agent_reviews):
                for candidate in candidates:
                    candidate_id = candidate.get("id")
                    if not candidate_id:
                        continue
                    if candidate_id not in latest_scores:
                        latest_scores[candidate_id] = {}
                    score = agent_reviews.get("score", 5.0) if not agent_reviews.get("veto") else 0
                    latest_scores[candidate_id][agent_name] = score
                continue
            for candidate_id, review in agent_reviews.items():
                if not isinstance(review, dict):
                    continue
                if candidate_id not in latest_scores:
                    latest_scores[candidate_id] = {}
                score = review.get("score", 5.0) if not review.get("veto") else 0
                latest_scores[candidate_id][agent_name] = score  # 后轮覆盖前轮

    best_id = None
    best_score = -1.0

    for candidate_id, agent_scores in latest_scores.items():
        weighted_sum = 0.0
        total_weight = 0.0
        for agent_name, score in agent_scores.items():
            weight = weights.get(agent_name, 0.25)
            weighted_sum += score * weight
            total_weight += weight

        # 归一化：如果某些 Agent 缺失评分，按已有权重占比计算
        normalized_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        if normalized_score > best_score:
            best_score = normalized_score
            best_id = candidate_id

    best_plan = None
    for candidate in candidates:
        if candidate.get("id") == best_id:
            best_plan = candidate
            break

    # Fallback：如果没匹配到但有候选方案，返回第一个
    if best_plan is None and candidates:
        best_plan = candidates[0]
        best_score = 5.0

    return best_score, best_plan


def _is_flat_review(agent_reviews: Dict[str, Any]) -> bool:
    """Return True for {agent_name: AgentReview} compatibility payloads."""
    return any(key in agent_reviews for key in ("score", "veto", "concerns", "suggestions", "veto_reason"))


def run_planning_flow(user_input: str, trace_id: Optional[str] = None, city_override: Optional[str] = None) -> Dict[str, Any]:
    """Execute the graph-backed planning flow and return the API response shape."""
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    logger.info("planning_flow_start", trace_id=trace_id, user_input_length=len(user_input))

    try:
        from graph.state import TripState

        session_id = session_manager.create_session(user_input)
        graph = build_graph()
        initial_state = {
            "session_id": session_id,
            "trip_state": TripState.IDLE.value,
            "user_input": user_input,
            "intent": None,
            "candidates": None,
            "round": 0,
            "round1_reviews": None,
            "round2_reviews": None,
            "final_score": None,
            "best_plan": None,
            "replan_count": 0,
            "error": None,
            "trace_id": trace_id,
            "parent_trace_id": None,
            "latency_ms": None,
            "execution_result": None,
            "city_override": city_override,
        }

        final_state = graph.invoke(initial_state)
        session = session_manager.get_session(session_id)
        if session is not None:
            session["state"] = final_state

        result = {
            "session_id": session_id,
            "trace_id": final_state.get("trace_id", trace_id),
            "intent": final_state.get("intent"),
            "candidates": final_state.get("candidates"),
            "round1_reviews": final_state.get("round1_reviews"),
            "round2_reviews": final_state.get("round2_reviews"),
            "final_score": final_state.get("final_score"),
            "best_plan": final_state.get("best_plan"),
            "execution_result": final_state.get("execution_result") or {},
            "error": final_state.get("error"),
        }

        logger.info("planning_flow_complete", trace_id=trace_id, final_score=result["final_score"])
        return result

    except Exception as e:
        logger.error("planning_flow_failed", trace_id=trace_id, error=str(e))
        return {
            "trace_id": trace_id,
            "error": f"规划流程失败: {e}",
            "best_plan": None,
            "final_score": 0.0,
            "execution_result": {"success": False, "error": str(e), "results": []}
        }
