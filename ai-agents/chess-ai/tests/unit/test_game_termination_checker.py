"""
终局检测器单元测试
"""

from chess_ai.board import Board
from chess_ai.rules import FENSerializer, GameTerminationChecker


class TestCheckmateDetection:
    """测试将死检测"""

    def test_is_checkmate_false_initial_position(self) -> None:
        """初始局面未被将死"""
        board = Board.create_initial()
        checker = GameTerminationChecker()
        assert checker.is_checkmate(board, "red") is False
        assert checker.is_checkmate(board, "black") is False

    def test_is_checkmate_true_red_cornered(self) -> None:
        """红方被将死场景"""
        board = Board()
        board = board.set_piece((9, 3), "K")  # Red king
        board = board.set_piece((9, 0), "r")  # Black rook covering row 9
        board = board.set_piece((0, 3), "r")  # Black rook covering col 3
        board = board.set_piece((0, 0), "k")  # Black king safe
        checker = GameTerminationChecker()
        assert checker.is_checkmate(board, "red") is True

    def test_is_checkmate_false_in_check_with_escape(self) -> None:
        """被将军但有逃逸路线时未将死"""
        board = Board()
        board = board.set_piece((9, 4), "K")  # Red king
        board = board.set_piece((0, 4), "r")  # Black rook far away
        board = board.set_piece((0, 0), "k")  # Black king
        checker = GameTerminationChecker()
        assert checker.is_checkmate(board, "red") is False


class TestStalemateDetection:
    """测试困毙检测"""

    def test_is_stalemate_false_initial_position(self) -> None:
        """初始局面未困毙"""
        board = Board.create_initial()
        checker = GameTerminationChecker()
        assert checker.is_stalemate(board, "red") is False

    def test_is_stalemate_true_no_moves_no_check(self) -> None:
        """无合法走子且未被将军时困毙"""
        # 构造确定性的困毙局面：
        # 黑将被自家士完全封锁（9个士填满黑方九宫），士的走法也被互相封锁
        # 红帅在同列远处，但被中路士遮挡不构成将军
        board = Board()
        # 黑方九宫全填满士
        board = board.set_piece((0, 3), "a")
        board = board.set_piece((0, 4), "k")  # 黑将在中心
        board = board.set_piece((0, 5), "a")
        board = board.set_piece((1, 3), "a")
        board = board.set_piece((1, 4), "a")
        board = board.set_piece((1, 5), "a")
        board = board.set_piece((2, 3), "a")
        board = board.set_piece((2, 4), "a")
        board = board.set_piece((2, 5), "a")
        # 红帅在远处同列被士遮挡
        board = board.set_piece((9, 3), "K")

        checker = GameTerminationChecker()
        assert not checker.rule_validator.is_in_check(board, "black")
        assert len(checker.rule_validator.get_legal_moves(board, "black")) == 0
        assert checker.is_stalemate(board, "black") is True


class TestThreefoldRepetition:
    """测试三次重复局面"""

    def test_is_threefold_repetition_false_initial(self) -> None:
        """初始局面无重复"""
        board = Board.create_initial()
        checker = GameTerminationChecker()
        assert checker.is_threefold_repetition(board) is False

    def test_is_threefold_repetition_true_after_repeats(self) -> None:
        """三次重复局面判和"""
        board = Board()
        board = board.set_piece((0, 4), "k")
        board = board.set_piece((9, 4), "K")
        board = board.set_piece((0, 0), "r")
        board = board.set_piece((9, 0), "R")

        checker = GameTerminationChecker()

        fen1 = "4k4/9/9/9/9/9/9/9/9/4K4 w -"
        fen2 = "4k4/9/9/9/9/9/9/9/9/4K4 b -"

        b1 = FENSerializer.from_fen(fen1)
        b1 = Board(grid=b1.grid, current_turn=b1.current_turn, fen_history=[fen1, fen2, fen1, fen2])
        assert checker.is_threefold_repetition(b1) is True


class TestGameTermination:
    """测试游戏结束判定"""

    def test_is_game_over_false_initial(self) -> None:
        """初始局面游戏未结束"""
        board = Board.create_initial()
        checker = GameTerminationChecker()
        is_over, reason = checker.is_game_over(board)
        assert is_over is False
        assert reason is None

    def test_is_game_over_true_checkmate(self) -> None:
        """将死时游戏结束"""
        board = Board()
        board = board.set_piece((9, 3), "K")
        board = board.set_piece((9, 0), "r")
        board = board.set_piece((0, 3), "r")
        board = board.set_piece((0, 0), "k")
        checker = GameTerminationChecker()
        is_over, reason = checker.is_game_over(board)
        assert is_over is True
        assert reason == "black_checkmate"  # Red is checkmated


class TestPerpetualCheck:
    """测试长将检测"""

    def test_is_perpetual_check_false_normal(self) -> None:
        """正常局面无长将"""
        board = Board.create_initial()
        checker = GameTerminationChecker()
        assert checker.is_perpetual_check(board, "red") is False
