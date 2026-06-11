import os
from typing import List, Dict, Any, Optional
from agents.llm_client import call_llm, _safe_eval_any


class PlannerAgent:
    """方案规划 Agent：负责生成、修改和重新生成候选方案。"""

    def __init__(self):
        self.prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "planner_agent.txt"
        )
        self.revise_prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "planner_revise.txt"
        )

    def generate(self, intent: Dict, trace_id: Optional[str] = None) -> List[Dict]:
        """根据用户意图生成初始候选方案。"""
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        user_prompt = str(intent)
        response_text = call_llm(user_prompt, system_prompt, trace_id=trace_id)
        candidates = _safe_eval_any(response_text)

        if not isinstance(candidates, list):
            candidates = [candidates]

        for i, candidate in enumerate(candidates):
            if "id" not in candidate:
                candidate["id"] = f"plan_{i + 1}"

        return candidates

    def revise(self, candidates: List[Dict], reviews: Dict) -> List[Dict]:
        """根据评审反馈修改方案。

        S8 修复：实现真正的修改逻辑。
        将评审反馈作为 LLM 输入，让 LLM 基于反馈改进方案。

        Args:
            candidates: 原始候选方案列表
            reviews: 评审结果 {agent_name: {candidate_id: AgentReview}}
        """
        if not reviews:
            return candidates

        # 收集每个方案的所有评审意见
        feedback_map: Dict[str, List[str]] = {}
        for agent_name, agent_reviews in reviews.items():
            if isinstance(agent_reviews, dict):
                for candidate_id, review in agent_reviews.items():
                    if isinstance(review, dict):
                        concerns = review.get("concerns", [])
                        suggestions = review.get("suggestions", [])
                        if concerns or suggestions:
                            if candidate_id not in feedback_map:
                                feedback_map[candidate_id] = []
                            feedback_parts = []
                            if concerns:
                                feedback_parts.append(f"问题: {', '.join(concerns)}")
                            if suggestions:
                                feedback_parts.append(f"建议: {', '.join(suggestions)}")
                            feedback_map[candidate_id].append(
                                f"[{agent_name}] {'; '.join(feedback_parts)}"
                            )

        if not feedback_map:
            return candidates

        # 使用 LLM 根据反馈修改方案
        revised_candidates = []
        for candidate in candidates:
            candidate_id = candidate.get("id", "")
            feedback = feedback_map.get(candidate_id, [])

            if not feedback:
                revised_candidates.append(candidate)
                continue

            try:
                prompt = (
                    f"原始方案：{candidate}\n\n"
                    f"评审反馈：\n" +
                    "\n".join(f"- {fb}" for fb in feedback) +
                    "\n\n请根据以上反馈修改方案，输出修改后的完整方案（保持 Dict 格式）。"
                )
                response_text = call_llm(
                    prompt,
                    "你是一个行程规划专家，根据评审反馈优化候选活动方案。",
                )
                revised = _extract_revised_candidate(_safe_eval_any(response_text), candidate_id)
                if revised:
                    revised["id"] = candidate_id
                    revised_candidates.append(revised)
                else:
                    revised_candidates.append(candidate)
            except Exception:
                # 修改失败时保留原方案
                revised_candidates.append(candidate)

        return revised_candidates

    def regenerate(self, intent: Dict, exclude_options: List[str]) -> List[Dict]:
        """重新生成方案，排除被否决的方案 ID。

        S8 修复 + B3 配合：将 exclude_options 传入 LLM，
        要求生成与被否决方案不同的新方案。

        Args:
            intent: 用户意图
            exclude_options: 需要排除的方案 ID 列表
        """
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        user_prompt = str(intent)
        if exclude_options:
            user_prompt += f"\n\n请勿生成以下 ID 的方案（已被否决）：{', '.join(exclude_options)}"

        response_text = call_llm(user_prompt, system_prompt)
        candidates = _safe_eval_any(response_text)

        if not isinstance(candidates, list):
            candidates = [candidates]

        # 确保新方案 ID 不与排除列表冲突
        used_ids = set(exclude_options)
        for i, candidate in enumerate(candidates):
            if "id" not in candidate or candidate["id"] in used_ids:
                new_id = f"plan_{i + 1}"
                counter = 1
                while new_id in used_ids:
                    counter += 1
                    new_id = f"plan_regenerated_{counter}"
                candidate["id"] = new_id
            used_ids.add(candidate["id"])

        return candidates


def _extract_revised_candidate(parsed: Any, candidate_id: str) -> Optional[Dict]:
    """Extract a plan-shaped revision and ignore review-shaped LLM fallbacks."""
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict) and item.get("id") == candidate_id and _is_plan_shaped(item):
                return item
        if len(parsed) == 1 and isinstance(parsed[0], dict):
            return _extract_revised_candidate(parsed[0], candidate_id)
        return None

    if not isinstance(parsed, dict):
        return None

    if not _is_plan_shaped(parsed):
        return None

    return parsed


def _is_plan_shaped(candidate: Dict) -> bool:
    """Return True for plan-like data, rejecting review-only payloads."""
    plan_fields = {
        "pois",
        "restaurant",
        "poi_name",
        "description",
        "total_budget",
        "estimated_duration_minutes",
        "highlights",
    }
    return bool(plan_fields.intersection(candidate.keys()))
