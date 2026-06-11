"""
走子输出解析器单元测试
"""

from chess_ai.llm.parser import MoveOutputParser


class TestMoveOutputParser:
    """测试走子输出解析器"""

    def test_parse_clean_ucci(self) -> None:
        """解析干净的UCCI坐标"""
        valid_moves = ["h2e2", "h2e3"]
        assert MoveOutputParser.parse("h2e2", valid_moves) == "h2e2"
        assert MoveOutputParser.parse("h2e3", valid_moves) == "h2e3"

    def test_parse_with_code_block(self) -> None:
        """解析带Markdown代码块的输出"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse('```json\n{"move": "h2e2"}\n```', valid_moves) == "h2e2"
        assert MoveOutputParser.parse("```\nh2e2\n```", valid_moves) == "h2e2"

    def test_parse_with_noise_prefix(self) -> None:
        """解析带噪音前缀的输出"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("我认为最佳走子是：h2e2", valid_moves) == "h2e2"
        assert MoveOutputParser.parse("根据局势，我认为最佳走子是：h2e2", valid_moves) == "h2e2"

    def test_parse_with_noise_suffix(self) -> None:
        """解析带噪音后缀的输出"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("h2e2。", valid_moves) == "h2e2"
        assert MoveOutputParser.parse("h2e2，这是最佳走子", valid_moves) == "h2e2"

    def test_parse_with_hyphen(self) -> None:
        """解析带连字符的UCCI格式"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("h2-e2", valid_moves) == "h2e2"
        assert MoveOutputParser.parse("h2 - e2", valid_moves) == "h2e2"

    def test_parse_with_chinese_notation(self) -> None:
        """解析中文简谱（当前实现不支持，应返回None）"""
        valid_moves = ["h2e2"]
        # 当前解析器不支持中文简谱，所以返回None
        assert MoveOutputParser.parse("炮二平五", valid_moves) is None

    def test_parse_json_format(self) -> None:
        """解析JSON格式输出"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse('{"move": "h2e2"}', valid_moves) == "h2e2"
        assert MoveOutputParser.parse("{'move': 'h2e2'}", valid_moves) == "h2e2"

    def test_parse_invalid_move(self) -> None:
        """解析无效走子（不在合法走子列表中）"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("h2e3", valid_moves) is None
        assert MoveOutputParser.parse("i0i0", valid_moves) is None

    def test_parse_empty_output(self) -> None:
        """解析空输出"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("", valid_moves) is None
        assert MoveOutputParser.parse("   ", valid_moves) is None

    def test_parse_no_valid_moves(self) -> None:
        """当合法走子列表为空时"""
        valid_moves = []
        assert MoveOutputParser.parse("h2e2", valid_moves) is None

    def test_parse_single_valid_move_shortcut(self) -> None:
        """当只有一个合法走子时的快捷路径"""
        valid_moves = ["h2e2"]
        # 即使输出中有其他文字，也能匹配到该走子
        assert MoveOutputParser.parse("走子是h2e2没错", valid_moves) == "h2e2"

    def test_parse_fuzzy_variants(self) -> None:
        """测试模糊变体匹配"""
        valid_moves = ["h2e2"]
        assert MoveOutputParser.parse("h2-e2", valid_moves) == "h2e2"  # 连字符
        assert MoveOutputParser.parse("h2 e2", valid_moves) == "h2e2"  # 空格
        # 中文逗号变体
        assert MoveOutputParser.parse("h2，e2", valid_moves) == "h2e2"

    def test_validate_format(self) -> None:
        """测试格式验证"""
        # 纯坐标格式
        assert MoveOutputParser.validate_format("h2e2")[0] is True
        # 带噪音但可接受
        assert MoveOutputParser.validate_format("我认为最佳走子是：h2e2")[0] is True
        # JSON格式
        assert MoveOutputParser.validate_format('{"move": "h2e2"}')[0] is True
        # 空输出
        assert MoveOutputParser.validate_format("")[0] is False
        # 过长文本且无坐标
        assert MoveOutputParser.validate_format("这是一段很长的文字，没有任何走子信息")[0] is False
