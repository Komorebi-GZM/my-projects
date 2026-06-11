"""
Prompt 构建器 - 三套实测有效的 Prompt 模板
"""

from __future__ import annotations

from ..infra.difficulty import Difficulty
from .models import MoveRequest

# 模板一：极简工业通用版（云端模型首选）
MINIMAL_PROMPT = """# 输出格式（严格遵循）
仅输出UCCI坐标（4个字符，如h2e2），禁止任何其他文字。

# 角色
中国象棋AI。

# 当前局势
FEN: {fen}
走子方: {side}

# 示例
输入: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
输出: h2e2

输入: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/R1BAKABNR b - - 1 1
输出: h7e7

# 任务
根据当前FEN，输出最佳走子UCCI坐标。

# 严格禁止
- 禁止解释走子原因
- 禁止输出思考过程
- 禁止添加标点符号
- 禁止输出多个选项"""

# 模板二：Few-shot轻量约束版（本地模型专用）
FEWSHOT_PROMPT = """# 输出格式（严格遵循）
仅输出4字符UCCI坐标（如h2e2），禁止任何其他文字。

UCCI坐标说明：
- 棋盘列用a-i表示（左到右），行用0-9表示（下到上）
- h2e2 = 从h列2行移动到e列2行

# 角色
中国象棋AI。

# 当前局势
FEN: {fen}
走子方: {side}

# 示例（严格模仿此格式）
例1：
FEN: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
输出: h2e2

例2：
FEN: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/R1BAKABNR b - - 1 1
输出: h7e7

# 任务
根据FEN输出最佳走子，仅输出4字符坐标。

# 严格禁止
- 禁止解释原因
- 禁止输出思考过程
- 禁止添加标点或换行
- 禁止输出坐标以外的任何内容"""

# 模板三：轻量结构化极简版（支持JSON输出的模型）
STRUCTURED_PROMPT = """# 输出格式（严格JSON，禁止Markdown代码块）
{{"move": "UCCI坐标4字符", "confidence": "high|medium|low"}}

# 角色
中国象棋AI。

# 当前局势
FEN: {fen}
走子方: {side}

# 示例
输入: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
输出: {{"move": "h2e2", "confidence": "high"}}

输入: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/R1BAKABNR b - - 1 1
输出: {{"move": "h7e7", "confidence": "high"}}

# 任务
输出JSON格式走子，move字段仅含4字符UCCI坐标。

# 严格禁止
- 禁止输出```json代码块标记
- 禁止解释走子原因
- 禁止输出思考字段
- 禁止在JSON外添加任何文字"""


# 带错误提示的重试模板（追加到已有 Prompt 后面）
RETRY_PROMPT_SUFFIX = """

# 错误修正
你上次的输出: {last_output}
错误原因: {error_message}
请仅输出一个合法的UCCI坐标。"""


PROMPT_TEMPLATES = {
    "minimal": MINIMAL_PROMPT,
    "fewshot": FEWSHOT_PROMPT,
    "structured": STRUCTURED_PROMPT,
}


def select_prompt_version(provider: str, model: str) -> str:
    """
    根据提供商和模型选择最优 Prompt 版本

    Args:
        provider: 模型提供商
        model: 模型名称

    Returns:
        Prompt 版本名称
    """
    # DeepSeek 和 GPT 使用极简版
    if provider == "deepseek" or provider == "openai":
        return "minimal"

    # 本地模型用 Few-shot 版
    if provider == "ollama":
        return "fewshot"

    # 默认极简版
    return "minimal"


class PromptBuilder:
    """
    Prompt 组装器

    根据模型和输入，组装完整的 Prompt 字符串
    """

    @classmethod
    def build(cls, request: MoveRequest, last_error: str | None = None) -> str:
        """
        构建完整的 Prompt

        Args:
            request: 走子请求
            last_error: 上次错误信息（用于重试）

        Returns:
            完整的 Prompt 字符串
        """
        # 选择模板
        template = PROMPT_TEMPLATES.get(request.prompt_version, PROMPT_TEMPLATES["minimal"])

        # 填充模板
        prompt = template.format(
            fen=request.fen,
            side=request.side,
        )

        if request.valid_moves:
            prompt += "\n\n# 合法走子\n"
            prompt += " ".join(request.valid_moves)

        # 注入难度提示
        try:
            difficulty = Difficulty(request.difficulty)
            prompt = inject_difficulty_hint(prompt, difficulty)
        except ValueError:
            # 如果难度无效，使用默认的 medium
            prompt = inject_difficulty_hint(prompt, Difficulty.MEDIUM)

        # 如果是重试，追加错误信息
        if last_error and isinstance(last_error, dict):
            prompt += RETRY_PROMPT_SUFFIX.format(
                last_output=last_error.get("last_output", "未知"),
                error_message=last_error.get("error_message", "未知错误"),
            )

        return prompt

    @classmethod
    def build_system_prompt(cls, version: str = "minimal") -> str:
        """
        返回系统 Prompt

        Args:
            version: Prompt 版本

        Returns:
            系统 Prompt 字符串
        """
        # 在简短的场景下，所有内容都在 user prompt 中更有效
        # 系统 prompt 保持极简
        if version == "structured":
            return "你是中国象棋AI。请依据格式输出JSON走子。"
        return "你是中国象棋AI。请严格按格式输出。"

    @classmethod
    def estimate_tokens(cls, prompt: str) -> int:
        """
        估算 Token 消耗量

        Args:
            prompt: Prompt 字符串

        Returns:
            估算的 Token 数（约等于字符数 / 2）
        """
        return len(prompt) // 2 + 1


DIFFICULTY_HINTS: dict[Difficulty, str] = {
    Difficulty.EASY: "# 难度提示：你是在陪新手练习，请偶尔尝试非常规走子，体验象棋乐趣。",
    Difficulty.MEDIUM: "# 难度提示：保持稳定发挥，选择当前局面的合理走子。",
    Difficulty.HARD: "# 难度提示：这是高水平对局，请选择当前最优或次优走子。",
}


def inject_difficulty_hint(prompt: str, difficulty: Difficulty) -> str:
    """
    向 Prompt 注入难度提示

    Args:
        prompt: 原始 Prompt
        difficulty: 难度级别

    Returns:
        注入难度提示后的 Prompt
    """
    hint = DIFFICULTY_HINTS.get(difficulty, "")
    if hint:
        return f"{prompt}\n{hint}"
    return prompt
