"""评审 Agent 基类。

所有头脑风暴评审 Agent（体验/安全/效率/预算）共享相同的评审逻辑，
子类只需定义 `prompt_file` 属性指定 Prompt 文件名。
"""
import os
from typing import Dict, Any, Optional
from agents.llm_client import call_llm_dict


class BaseReviewAgent:
    """评审 Agent 基类。"""

    prompt_file: str  # 子类必须定义，如 "experience_agent.txt"

    def review(
        self,
        candidate: Dict,
        intent: Dict,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """对候选方案进行评审。

        Args:
            candidate: 候选方案 Dict
            intent: 用户意图 Dict
            trace_id: 链路追踪 ID

        Returns:
            AgentReview Dict（含 score, veto, strengths, concerns, suggestions）
        """
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "prompts", self.prompt_file
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        user_prompt = f"方案：{candidate}\n用户意图：{intent}"
        return call_llm_dict(user_prompt, system_prompt, trace_id=trace_id)
