from agents.brainstorm.base_agent import BaseReviewAgent


class BudgetAgent(BaseReviewAgent):
    """预算视角评审 Agent。"""
    prompt_file = "budget_agent.txt"
