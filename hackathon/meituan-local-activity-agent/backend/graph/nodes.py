import time
import structlog
from typing import Dict, Any
from graph.state import BrainstormState, TripState

logger = structlog.get_logger()

# 集中导入 — 避免每个函数内延迟导入
from agents.intent_agent import IntentAgent
from agents.planner_agent import PlannerAgent
from agents.brainstorm.brainstorm_engine import run_brainstorm_round
from agents.orchestrator import aggregate_reviews
from agents.executor_agent import ExecutorAgent
from tools.weather import get_weather


def _collect_vetoed_candidates(state: BrainstormState) -> list:
    """从 round1_reviews / round2_reviews 中提取所有被否决的 candidate_id。"""
    vetoed = set()
    for round_key in ("round1_reviews", "round2_reviews"):
        round_data = state.get(round_key)
        if not round_data or "reviews" not in round_data:
            continue
        for agent_reviews in round_data["reviews"].values():
            if isinstance(agent_reviews, dict):
                if agent_reviews.get("veto"):
                    for candidate in state.get("candidates", []) or []:
                        candidate_id = candidate.get("id")
                        if candidate_id:
                            vetoed.add(candidate_id)
                    continue
                # agent_reviews 是 {candidate_id: review} 的嵌套结构
                for candidate_id, review in agent_reviews.items():
                    if isinstance(review, dict) and review.get("veto"):
                        vetoed.add(candidate_id)
    return list(vetoed)


def parse_intent(state: BrainstormState) -> Dict[str, Any]:
    """解析用户意图。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="parse_intent", trace_id=trace_id)

    try:
        agent = IntentAgent()
        intent = agent.parse(state["user_input"], trace_id)
        city_override = state.get("city_override")
        if city_override:
            if "location" not in intent:
                intent["location"] = {}
            intent["location"]["city"] = city_override
        city = intent.get("location", {}).get("city", "上海")
        weather = get_weather(city, trace_id=trace_id)
        intent["weather"] = weather
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info("node_complete", node="parse_intent", trace_id=trace_id, latency_ms=latency_ms)

        return {
            "intent": intent,
            "trip_state": TripState.INTENT_PARSING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="parse_intent", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"意图解析失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def generate_plans(state: BrainstormState) -> Dict[str, Any]:
    """根据意图生成候选方案。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="generate_plans", trace_id=trace_id)

    try:
        agent = PlannerAgent()
        candidates = agent.generate(state["intent"], trace_id)
        latency_ms = int((time.time() - start_time) * 1000)
        if not candidates:
            logger.error("node_failed", node="generate_plans", trace_id=trace_id, error="No plan available", latency_ms=latency_ms)
            return {
                "candidates": [],
                "error": "No plan available",
                "trip_state": TripState.FAILED.value,
                "latency_ms": latency_ms
            }
        logger.info("node_complete", node="generate_plans", trace_id=trace_id, candidate_count=len(candidates), latency_ms=latency_ms)

        return {
            "candidates": candidates,
            "round": 0,
            "trip_state": TripState.PLANNING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="generate_plans", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"方案生成失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def brainstorm_round1(state: BrainstormState) -> Dict[str, Any]:
    """第1轮头脑风暴评审。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="brainstorm_round1", trace_id=trace_id)

    try:
        reviews = run_brainstorm_round(
            candidates=state["candidates"],
            round_num=1,
            intent=state["intent"],
            trace_id=trace_id
        )
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info("node_complete", node="brainstorm_round1", trace_id=trace_id, latency_ms=latency_ms)

        return {
            "round1_reviews": reviews,
            "round": 1,
            "trip_state": TripState.BRAINSTORMING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="brainstorm_round1", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"第1轮评审失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def brainstorm_round2(state: BrainstormState) -> Dict[str, Any]:
    """第2轮头脑风暴评审（基于第1轮反馈修改方案）。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="brainstorm_round2", trace_id=trace_id)

    try:
        planner = PlannerAgent()
        candidates = planner.revise(
            state["candidates"],
            state.get("round1_reviews", {}).get("reviews", {})
        )

        reviews = run_brainstorm_round(
            candidates=candidates,
            round_num=2,
            intent=state["intent"],
            trace_id=trace_id
        )
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info("node_complete", node="brainstorm_round2", trace_id=trace_id, latency_ms=latency_ms)

        return {
            "round2_reviews": reviews,
            "round": 2,
            "candidates": candidates,
            "trip_state": TripState.BRAINSTORMING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="brainstorm_round2", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"第2轮评审失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def aggregate_and_confirm(state: BrainstormState) -> Dict[str, Any]:
    """汇总评审结果，确认最优方案。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="aggregate_and_confirm", trace_id=trace_id)

    try:
        final_score, best_plan = aggregate_reviews(
            state.get("round1_reviews"),
            state.get("round2_reviews"),
            state.get("candidates", [])
        )
        latency_ms = int((time.time() - start_time) * 1000)
        if best_plan is None:
            logger.error("node_failed", node="aggregate_and_confirm", trace_id=trace_id, error="No plan available", latency_ms=latency_ms)
            return {
                "final_score": final_score,
                "best_plan": None,
                "error": "No plan available",
                "execution_result": {"success": False, "error": "No plan available", "results": []},
                "trip_state": TripState.FAILED.value,
                "latency_ms": latency_ms
            }
        logger.info(
            "node_complete", node="aggregate_and_confirm", trace_id=trace_id,
            final_score=final_score, best_plan_id=best_plan.get("id") if best_plan else None,
            latency_ms=latency_ms
        )

        return {
            "final_score": final_score,
            "best_plan": best_plan,
            "trip_state": TripState.CONFIRMING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="aggregate_and_confirm", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"汇总确认失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def replan(state: BrainstormState) -> Dict[str, Any]:
    """重新规划：排除被安全否决的方案，生成新候选。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="replan", trace_id=trace_id, replan_count=state.get("replan_count", 0))

    try:
        replan_count = state.get("replan_count", 0) + 1
        if replan_count >= 2:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "node_failed",
                node="replan",
                trace_id=trace_id,
                error="Replan attempts exhausted",
                replan_count=replan_count,
                latency_ms=latency_ms,
            )
            return {
                "replan_count": replan_count,
                "error": "Replan attempts exhausted",
                "execution_result": {"success": False, "error": "Replan attempts exhausted", "results": []},
                "trip_state": TripState.FAILED.value,
                "latency_ms": latency_ms
            }

        planner = PlannerAgent()

        # B3 修复：从历史评审中提取被否决的 candidate_id
        vetoed = _collect_vetoed_candidates(state)
        logger.info("replan_exclude", trace_id=trace_id, vetoed_candidates=vetoed)

        candidates = planner.regenerate(
            state["intent"],
            exclude_options=vetoed
        )
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info("node_complete", node="replan", trace_id=trace_id, new_candidate_count=len(candidates), latency_ms=latency_ms)

        return {
            "replan_count": replan_count,
            "round": 0,
            "candidates": candidates,
            "trip_state": TripState.REPLANNING.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="replan", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {"error": f"重规划失败: {e}", "trip_state": TripState.FAILED.value, "latency_ms": latency_ms}


def execute_plan(state: BrainstormState) -> Dict[str, Any]:
    """执行最优方案。"""
    trace_id = state.get("trace_id", "unknown")
    start_time = time.time()
    logger.info("node_start", node="execute_plan", trace_id=trace_id)

    try:
        executor = ExecutorAgent()
        intent = state.get("intent", {})
        city = intent.get("location", {}).get("city", "上海")
        result = executor.execute(state["best_plan"], trace_id, city=city)
        latency_ms = int((time.time() - start_time) * 1000)
        if not result.get("success"):
            error = result.get("error", "方案执行失败")
            logger.error("node_failed", node="execute_plan", trace_id=trace_id, error=error, latency_ms=latency_ms)
            return {
                "error": error,
                "execution_result": result,
                "trip_state": TripState.FAILED.value,
                "latency_ms": latency_ms
            }

        logger.info("node_complete", node="execute_plan", trace_id=trace_id, latency_ms=latency_ms)

        return {
            "execution_result": result,
            "trip_state": TripState.COMPLETED.value,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error("node_failed", node="execute_plan", trace_id=trace_id, error=str(e), latency_ms=latency_ms)
        return {
            "error": f"方案执行失败: {e}",
            "execution_result": {"success": False, "error": str(e), "results": []},
            "trip_state": TripState.FAILED.value,
            "latency_ms": latency_ms
        }
