from agents.brainstorm.base_agent import BaseReviewAgent


class SafetyAgent(BaseReviewAgent):
    """安全视角评审 Agent。"""
    prompt_file = "safety_agent.txt"
