"""
走子输出解析器 - 多级清洗 + 正则提取 + 兜底验证

适配当前主流 LLM 的输出乱象：
1. 前后加废话 ("根据局势，我认为最佳走子是：h2e2")
2. 换行与标点 ("h2e2\n", "h2e2。")
3. 格式跑偏 ("走子：h2e2", "move: h2e2")
4. 中文混用 ("炮二平五", "h2-e2")
5. JSON格式错误 (结构化版)
"""

from __future__ import annotations

import re
from typing import ClassVar


class MoveOutputParser:
    """
    走子输出解析器 - 适配模型输出乱象

    采用"多级清洗 + 正则提取 + 兜底验证"策略：
    1. 清洗常见噪音（代码块、客套话、标点）
    2. 尝试 JSON 提取（结构化版输出）
    3. 正则提取 UCCI 坐标
    4. 模糊匹配（处理连字符等变体）
    5. 最终校验（必须在合法走子列表中）
    """

    # UCCI 坐标正则：列(a-i) + 行(0-9) + 列(a-i) + 行(0-9)
    UCCI_PATTERN = re.compile(r"(?<!\w)([a-i][0-9][a-i][0-9])(?!\w)")

    # JSON move 字段提取正则
    JSON_MOVE_PATTERN = re.compile(r'["\']move["\']\s*:\s*["\']([a-i][0-9][a-i][0-9])["\']', re.IGNORECASE)

    # 中文简谱正则（如 "炮二平五"）
    CHINESE_NOTATION_PATTERN = re.compile(r"[炮車馬相仕兵卒砲車馬相仕兵卒]\d[平上下进退]\d")

    # 带连字符的 UCCI 格式（如 h2-e2）
    HYPHEN_UCCI_PATTERN = re.compile(r"([a-i][0-9])[-\s]+([a-i][0-9])")

    # 常见噪音前缀/后缀
    NOISE_PREFIXES: ClassVar[list[str]] = [
        r"根据.*?(?:输出|走子|选择|结果)",
        r"我认为.*?(?:是|为|最佳)",
        r"最佳走子[是为:]+",
        r"走子[是为:]+",
        r"(?:输出|结果|答案)[是为:：]+",
        r"move[是为:：]+",
        r"(?:我|AI|模型)[^，。]{0,10}?(?:选择|走|下)",
    ]

    # 常见噪音后缀（解释性文字）
    NOISE_SUFFIXES: ClassVar[list[str]] = [
        r"[（(][^)）]{0,30}[）)]",  # 括号内容
        r"[。，,、；;！!\n\r]+$",  # 结尾标点
        r"\s+",  # 末尾空白
    ]

    @classmethod
    def parse(
        cls,
        raw_output: str,
        valid_moves: list[str],
        mode: str = "standard",
    ) -> str | None:
        """
        解析模型输出，提取合法 UCCI 坐标

        Args:
            raw_output: 模型原始输出文本
            valid_moves: 合法走子列表（用于验证）
            mode: 解析模式 - "strict" | "standard" | "lenient"

        Returns:
            解析成功的 UCCI 坐标，若解析失败则返回 None
        """
        if not raw_output or not raw_output.strip():
            return None

        # 如果提供了合法走子列表且只有一个，直接检查
        if len(valid_moves) == 1:
            single = valid_moves[0]
            if single in raw_output:
                return single

        # 第1级：清洗常见噪音
        cleaned = cls._clean_noise(raw_output)

        # 构建验证集合（包含模糊变体）
        move_set = set(valid_moves)
        if valid_moves:
            move_set.update(cls._generate_fuzzy_variants(valid_moves))

        # 第2级：尝试 JSON 提取（结构化版输出）
        if "{" in cleaned:
            move = cls._extract_from_json(cleaned)
            if move and move in move_set:
                return move

        # 第3级：正则提取 UCCI 坐标
        matches = cls.UCCI_PATTERN.findall(cleaned)
        for move in matches:
            if move in move_set:
                return move  # type: ignore[no-any-return]

        # 第4级：模糊匹配（处理空格、连字符等变体）
        fuzzy_move = cls._fuzzy_extract(cleaned)
        if fuzzy_move and fuzzy_move in move_set:
            return fuzzy_move

        # 第5级：严格模式下尝试直接在原始输出中查找
        if mode == "strict":
            for move in valid_moves:
                if move in raw_output:
                    return move

        return None

    @classmethod
    def _clean_noise(cls, text: str) -> str:
        """清洗常见噪音"""
        # 去除 Markdown 代码块标记
        text = re.sub(r"```(?:json)?\s*\n?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        # 去除常见前缀废话
        for pattern in cls.NOISE_PREFIXES:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # 去除括号内的中文解释（如 "炮二平五" 式的说明）
        text = re.sub(r"[（(][^)）]{1,40}[）)]", "", text)

        # 去除结尾标点
        for pattern in cls.NOISE_SUFFIXES:
            text = re.sub(pattern, "", text)

        # 特殊字符替换
        text = text.replace("。", " ").replace("，", " ").replace("、", " ")
        text = text.replace("：", " ").replace(":", " ").replace(";", " ")

        return text.strip()

    @classmethod
    def _extract_from_json(cls, text: str) -> str | None:
        """从 JSON 结构中提取 move 字段"""
        # 尝试标准 JSON 格式
        match = cls.JSON_MOVE_PATTERN.search(text)
        if match:
            return match.group(1).lower()

        # 尝试宽松 JSON 格式（允许单引号、无引号等）
        loose_pattern = re.compile(r'(?:move|走子)\s*[=:]\s*"?([a-i][0-9][a-i][0-9])"?', re.IGNORECASE)
        match = loose_pattern.search(text)
        if match:
            return match.group(1).lower()

        return None

    @classmethod
    def _fuzzy_extract(cls, text: str) -> str | None:
        """
        模糊提取（处理带连字符、空格等变体）

        如 h2-e2 -> h2e2
        """
        # 处理带连字符/空格的格式：h2-e2 -> h2e2, h2 e2 -> h2e2
        match = cls.HYPHEN_UCCI_PATTERN.search(text)
        if match:
            return match.group(1) + match.group(2)

        return None

    @classmethod
    def _generate_fuzzy_variants(cls, moves: list[str]) -> set[str]:
        """生成走子的模糊变体集合"""
        variants = set()
        for move in moves:
            # 带连字符
            variants.add(f"{move[:2]}-{move[2:]}")
            # 带空格
            variants.add(f"{move[:2]} {move[2:]}")
            # 带中文逗号
            variants.add(f"{move[:2]}，{move[2:]}")
        return variants

    @classmethod
    def validate_format(cls, raw_output: str) -> tuple[bool, str]:
        """
        验证输出格式是否合规

        Args:
            raw_output: 模型原始输出

        Returns:
            (是否合规, 违规类型描述)
        """
        cleaned = raw_output.strip()

        if not cleaned:
            return False, "empty_output"

        # 提取所有UCCI坐标匹配
        ucci_matches = cls.UCCI_PATTERN.findall(cleaned)
        if ucci_matches and len(ucci_matches) <= 2:
            # 如果只有1-2个UCCI坐标，即使有其他文字也算可接受
            # 如果恰好只有一个匹配且整个字符串就是该坐标，则视为clean
            if len(ucci_matches) == 1 and cls.UCCI_PATTERN.fullmatch(cleaned):
                return True, "clean"
            return True, "acceptable_with_noise"

        # 纯坐标格式合规（上面已处理单匹配情况，这里处理完全匹配但可能被上面漏掉的情况）
        if cls.UCCI_PATTERN.fullmatch(cleaned):
            return True, "clean"

        # 可能是 JSON 格式
        if "{" in cleaned and "move" in cleaned.lower():
            return True, "json_format"

        return False, "unknown_format"
