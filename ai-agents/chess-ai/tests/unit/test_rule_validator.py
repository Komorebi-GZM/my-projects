"""
规则验证器单元测试
"""

from chess_ai.board import BLACK, RED, Board
from chess_ai.move import Move
from chess_ai.rules import RuleValidator


class TestBasicValidation:
    """测试基本验证规则"""

    def test_validate_move_rejects_empty_source(self) -> None:
        """起始位置无棋子时拒绝"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(4, 4), to_pos=(3, 4), piece="R")
        assert validator.validate_move(move, board, RED) is False

    def test_validate_move_rejects_wrong_color(self) -> None:
        """移动对方棋子时拒绝"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(0, 0), to_pos=(1, 0), piece="r")
        assert validator.validate_move(move, board, RED) is False

    def test_color_case_normalization(self) -> None:
        """颜色参数接受大小写"""
        board = Board()
        board = board.set_piece((5, 0), "R")
        validator = RuleValidator()
        move = Move(from_pos=(5, 0), to_pos=(0, 0), piece="R")
        assert validator.validate_move(move, board, "RED") is True
        assert validator.validate_move(move, board, "Red") is True

    def test_validate_rejects_same_position(self) -> None:
        """走子到同一位置时拒绝"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(9, 0), to_pos=(9, 0), piece="R")
        assert validator.validate_move(move, board, RED) is False


class TestRookValidation:
    """测试车（Rook）移动验证"""

    def test_rook_can_move_horizontally(self) -> None:
        """车可以横向移动"""
        board = Board()
        board = board.set_piece((5, 0), "R")
        validator = RuleValidator()
        move = Move(from_pos=(5, 0), to_pos=(5, 8), piece="R")
        assert validator.validate_move(move, board, RED) is True

    def test_rook_can_move_vertically(self) -> None:
        """车可以纵向移动"""
        board = Board()
        board = board.set_piece((5, 0), "R")
        validator = RuleValidator()
        move = Move(from_pos=(5, 0), to_pos=(0, 0), piece="R")
        assert validator.validate_move(move, board, RED) is True

    def test_rook_cannot_move_diagonally(self) -> None:
        """车不能斜着走"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(9, 0), to_pos=(8, 1), piece="R")
        assert validator.validate_move(move, board, RED) is False

    def test_rook_cannot_jump_over_pieces(self) -> None:
        """车不能跳过其他棋子"""
        board = Board.create_initial()
        validator = RuleValidator()
        # Rook at (9,0), knight at (9,1) blocks path to (9,4)
        move = Move(from_pos=(9, 0), to_pos=(9, 4), piece="R")
        assert validator.validate_move(move, board, RED) is False

    def test_rook_can_capture_enemy_piece(self) -> None:
        """车可以吃掉敌方棋子"""
        board = Board()
        board = board.set_piece((9, 0), "R")
        board = board.set_piece((5, 0), "r")
        validator = RuleValidator()
        move = Move(from_pos=(9, 0), to_pos=(5, 0), piece="R", captured_piece="r")
        assert validator.validate_move(move, board, RED) is True

    def test_rook_cannot_capture_own_piece(self) -> None:
        """车不能吃己方棋子"""
        board = Board.create_initial()
        validator = RuleValidator()
        # Rook at (9,0), knight at (9,1) is own piece
        move = Move(from_pos=(9, 0), to_pos=(9, 1), piece="R", captured_piece="N")
        assert validator.validate_move(move, board, RED) is False


class TestKingValidation:
    """测试帅/将（King）移动验证"""

    def test_king_can_move_one_step_in_palace(self) -> None:
        """帅可以在九宫内走一步"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(9, 4), to_pos=(8, 4), piece="K")
        assert validator.validate_move(move, board, RED) is True

    def test_king_cannot_leave_palace(self) -> None:
        """帅不能离开九宫"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(9, 4), to_pos=(6, 4), piece="K")
        assert validator.validate_move(move, board, RED) is False

    def test_king_cannot_move_two_steps(self) -> None:
        """帅不能走两步"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(9, 4), to_pos=(7, 4), piece="K")
        assert validator.validate_move(move, board, RED) is False

    def test_king_cannot_move_diagonally(self) -> None:
        """帅不能斜着走（中国象棋将/帅只能直走）"""
        board = Board()
        board = board.set_piece((8, 3), "K")
        validator = RuleValidator()
        move = Move(from_pos=(8, 3), to_pos=(7, 4), piece="K")
        assert validator.validate_move(move, board, RED) is False


class TestAdvisorValidation:
    """测试仕/士（Advisor）移动验证"""

    def test_advisor_can_move_diagonally(self) -> None:
        """仕可以斜走一步"""
        board = Board()
        board = board.set_piece((8, 3), "A")
        validator = RuleValidator()
        move = Move(from_pos=(8, 3), to_pos=(7, 4), piece="A")
        assert validator.validate_move(move, board, RED) is True

    def test_advisor_cannot_leave_palace(self) -> None:
        """仕不能离开九宫"""
        board = Board()
        board = board.set_piece((8, 3), "A")
        validator = RuleValidator()
        # (6, 4) is outside palace (red palace: rows 7-9)
        move = Move(from_pos=(8, 3), to_pos=(6, 4), piece="A")
        assert validator.validate_move(move, board, RED) is False

    def test_advisor_cannot_move_straight(self) -> None:
        """仕不能直走"""
        board = Board()
        board = board.set_piece((8, 3), "A")
        validator = RuleValidator()
        move = Move(from_pos=(8, 3), to_pos=(7, 3), piece="A")
        assert validator.validate_move(move, board, RED) is False


class TestBishopValidation:
    """测试相/象（Bishop）移动验证"""

    def test_bishop_can_move_diagonally_two_steps(self) -> None:
        """相可以斜走两步（田字）"""
        board = Board.create_initial()
        validator = RuleValidator()
        # Bishop at (9,2), eye at (8,3) is empty, destination (7,4) is empty
        move = Move(from_pos=(9, 2), to_pos=(7, 4), piece="B")
        assert validator.validate_move(move, board, RED) is True

    def test_bishop_cannot_cross_river(self) -> None:
        """相不能过河"""
        board = Board()
        board = board.set_piece((5, 4), "B")  # red bishop at river's edge
        validator = RuleValidator()
        # (3, 6) is valid bishop pattern (dr=2, dc=2), eye at (4,5)
        # but row 3 is across the river for red
        move = Move(from_pos=(5, 4), to_pos=(3, 6), piece="B")
        assert validator.validate_move(move, board, RED) is False

    def test_bishop_cannot_move_if_eye_blocked(self) -> None:
        """相眼被堵时不能走"""
        board = Board()
        board = board.set_piece((5, 4), "B")
        board = board.set_piece((6, 5), "P")  # block the eye
        validator = RuleValidator()
        move = Move(from_pos=(5, 4), to_pos=(7, 6), piece="B")
        assert validator.validate_move(move, board, RED) is False


class TestKnightValidation:
    """测试马（Knight）移动验证"""

    def test_knight_can_move_l_shape(self) -> None:
        """马可以走日字（L形）"""
        board = Board()
        board = board.set_piece((4, 4), "N")
        validator = RuleValidator()
        move = Move(from_pos=(4, 4), to_pos=(2, 3), piece="N")
        assert validator.validate_move(move, board, RED) is True

    def test_knight_cannot_move_if_leg_blocked(self) -> None:
        """马腿被绊时不能走"""
        board = Board()
        board = board.set_piece((4, 4), "N")
        board = board.set_piece((3, 4), "P")  # block leg at (3,4)
        validator = RuleValidator()
        move = Move(from_pos=(4, 4), to_pos=(2, 3), piece="N")
        assert validator.validate_move(move, board, RED) is False

    def test_knight_eight_directions(self) -> None:
        """马有八个方向"""
        board = Board()
        board = board.set_piece((5, 5), "N")
        validator = RuleValidator()
        # All 8 possible L-shape destinations should be reachable (on empty board)
        destinations = [(3, 4), (3, 6), (4, 3), (4, 7), (6, 3), (6, 7), (7, 4), (7, 6)]
        for dest in destinations:
            move = Move(from_pos=(5, 5), to_pos=dest, piece="N")
            assert validator.validate_move(move, board, RED), f"Knight cannot move to {dest}"


class TestCannonValidation:
    """测试炮（Cannon）移动验证"""

    def test_cannon_can_move_like_rook(self) -> None:
        """炮可以像车一样移动（不吃子时）"""
        board = Board.create_initial()
        validator = RuleValidator()
        # 红炮在 (7,1)，(7,0) 为空
        move = Move(from_pos=(7, 1), to_pos=(7, 0), piece="C")
        assert validator.validate_move(move, board, RED) is True

    def test_cannon_needs_screen_to_capture(self) -> None:
        """炮吃子需要炮架"""
        board = Board()
        board = board.set_piece((8, 1), "C")
        board = board.set_piece((0, 1), "c")
        validator = RuleValidator()
        # No screen between (8,1) and (0,1)
        move = Move(from_pos=(8, 1), to_pos=(0, 1), piece="C", captured_piece="c")
        assert validator.validate_move(move, board, RED) is False

    def test_cannon_can_capture_with_one_screen(self) -> None:
        """炮有一个炮架时可以吃子"""
        board = Board()
        board = board.set_piece((8, 1), "C")
        board = board.set_piece((4, 1), "P")  # screen
        board = board.set_piece((0, 1), "c")
        validator = RuleValidator()
        move = Move(from_pos=(8, 1), to_pos=(0, 1), piece="C", captured_piece="c")
        assert validator.validate_move(move, board, RED) is True

    def test_cannon_cannot_capture_with_no_screen(self) -> None:
        """炮没有炮架时不能吃子"""
        board = Board()
        board = board.set_piece((8, 1), "C")
        board = board.set_piece((5, 1), "p")
        validator = RuleValidator()
        move = Move(from_pos=(8, 1), to_pos=(5, 1), piece="C", captured_piece="p")
        assert validator.validate_move(move, board, RED) is False

    def test_cannon_cannot_capture_with_two_screens(self) -> None:
        """炮有两个炮架时不能吃子"""
        board = Board()
        board = board.set_piece((8, 1), "C")
        board = board.set_piece((6, 1), "P")
        board = board.set_piece((4, 1), "p")
        board = board.set_piece((2, 1), "n")
        validator = RuleValidator()
        move = Move(from_pos=(8, 1), to_pos=(2, 1), piece="C", captured_piece="n")
        assert validator.validate_move(move, board, RED) is False


class TestPawnValidation:
    """测试兵/卒（Pawn）移动验证"""

    def test_red_pawn_can_move_forward_before_crossing_river(self) -> None:
        """红兵过河前只能向前走"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(6, 0), to_pos=(5, 0), piece="P")
        assert validator.validate_move(move, board, RED) is True

    def test_red_pawn_cannot_move_sideways_before_crossing_river(self) -> None:
        """红兵过河前不能横走"""
        board = Board.create_initial()
        validator = RuleValidator()
        move = Move(from_pos=(6, 0), to_pos=(6, 1), piece="P")
        assert validator.validate_move(move, board, RED) is False

    def test_red_pawn_can_move_sideways_after_crossing_river(self) -> None:
        """红兵过河后可以横走"""
        board = Board()
        board = board.set_piece((4, 4), "P")  # crossed river
        validator = RuleValidator()
        move = Move(from_pos=(4, 4), to_pos=(4, 5), piece="P")
        assert validator.validate_move(move, board, RED) is True

    def test_red_pawn_can_move_forward_after_crossing_river(self) -> None:
        """红兵过河后仍然可以向前走"""
        board = Board()
        board = board.set_piece((4, 4), "P")
        validator = RuleValidator()
        move = Move(from_pos=(4, 4), to_pos=(3, 4), piece="P")
        assert validator.validate_move(move, board, RED) is True

    def test_red_pawn_cannot_move_backward(self) -> None:
        """兵不能后退"""
        board = Board()
        board = board.set_piece((5, 4), "P")
        validator = RuleValidator()
        move = Move(from_pos=(5, 4), to_pos=(6, 4), piece="P")
        assert validator.validate_move(move, board, RED) is False

    def test_black_pawn_cannot_move_sideways_before_crossing_river(self) -> None:
        """黑卒过河前不能横走"""
        board = Board()
        board = board.set_piece((3, 0), "p")  # not crossed yet
        validator = RuleValidator()
        move = Move(from_pos=(3, 0), to_pos=(3, 1), piece="p")
        assert validator.validate_move(move, board, BLACK) is False

    def test_black_pawn_can_move_sideways_after_crossing_river(self) -> None:
        """黑卒过河后可以横走"""
        board = Board()
        board = board.set_piece((5, 4), "p")  # crossed river
        validator = RuleValidator()
        move = Move(from_pos=(5, 4), to_pos=(5, 5), piece="p")
        assert validator.validate_move(move, board, BLACK) is True


class TestCheckDetection:
    """测试将军检测"""

    def test_is_in_check_rook_attack(self) -> None:
        """检测到车将军"""
        board = Board()
        board = board.set_piece((0, 0), "r")
        board = board.set_piece((5, 0), "K")
        validator = RuleValidator()
        assert validator.is_in_check(board, RED) is True

    def test_is_in_check_no_check(self) -> None:
        """初始局面无将军"""
        board = Board.create_initial()
        validator = RuleValidator()
        assert validator.is_in_check(board, RED) is False

    def test_is_in_check_knight_attack(self) -> None:
        """检测到马将军"""
        board = Board()
        board = board.set_piece((2, 3), "N")
        board = board.set_piece((0, 4), "k")
        validator = RuleValidator()
        assert validator.is_in_check(board, BLACK) is True


class TestWillCauseCheck:
    """测试是否会导致被将军"""

    def test_moving_blocking_piece_exposes_king(self) -> None:
        """移动遮挡棋子暴露将位"""
        board = Board()
        board = board.set_piece((4, 0), "K")  # red king
        board = board.set_piece((5, 0), "P")  # red pawn blocking
        board = board.set_piece((4, 4), "r")  # black rook on same row
        validator = RuleValidator()
        # Moving pawn away exposes king to rook
        move = Move(from_pos=(5, 0), to_pos=(6, 0), piece="P")
        assert validator.will_cause_check(move, board, RED) is True

    def test_capturing_checking_piece_rescues_king(self) -> None:
        """吃掉将军的棋子解除将军"""
        board = Board()
        board = board.set_piece((5, 0), "K")  # red king
        board = board.set_piece((5, 4), "r")  # black rook on same row
        board = board.set_piece((5, 3), "R")  # red rook can capture
        validator = RuleValidator()
        move = Move(from_pos=(5, 3), to_pos=(5, 4), piece="R", captured_piece="r")
        assert validator.will_cause_check(move, board, RED) is False


class TestApplyMove:
    """测试应用走子的公开接口"""

    def test_apply_move_returns_new_board_and_switches_turn(self) -> None:
        """应用走子返回新棋盘，并切换走子方"""
        board = Board()
        board = board.set_piece((9, 0), "R")
        validator = RuleValidator()
        move = Move(from_pos=(9, 0), to_pos=(8, 0), piece="R")

        new_board = validator.apply_move(board, move)

        assert board.get_piece((9, 0)) == "R"
        assert board.get_piece((8, 0)) is None
        assert new_board.get_piece((9, 0)) is None
        assert new_board.get_piece((8, 0)) == "R"
        assert new_board.current_turn == BLACK


class TestKingsFacing:
    """测试帅将对面"""

    def test_is_kings_facing_detects_facing(self) -> None:
        """检测到帅将对脸"""
        board = Board()
        board = board.set_piece((0, 4), "k")
        board = board.set_piece((9, 4), "K")
        validator = RuleValidator()
        assert validator.is_kings_facing(board) is True

    def test_is_kings_facing_no_facing(self) -> None:
        """初始局面无帅将对脸"""
        board = Board.create_initial()
        validator = RuleValidator()
        assert validator.is_kings_facing(board) is False

    def test_is_kings_facing_blocked_by_piece(self) -> None:
        """帅将之间被棋子挡住不算对脸"""
        board = Board.create_initial()
        validator = RuleValidator()
        # Initial position has pieces between kings (row 0-9, col 4)
        assert validator.is_kings_facing(board) is False

    def test_kings_facing_counts_as_check(self) -> None:
        """帅将对脸视为将军"""
        board = Board()
        board = board.set_piece((0, 4), "k")
        board = board.set_piece((9, 4), "K")
        validator = RuleValidator()
        assert validator.is_in_check(board, RED) is True
        assert validator.is_in_check(board, BLACK) is True


class TestLegalMoves:
    """测试合法走子生成"""

    def test_get_legal_moves_returns_list(self) -> None:
        """get_legal_moves 返回列表"""
        board = Board()
        board = board.set_piece((9, 4), "K")  # need king for legal move check
        board = board.set_piece((9, 0), "R")
        board = board.set_piece((9, 1), "N")
        validator = RuleValidator()
        moves = validator.get_legal_moves(board, RED)
        assert isinstance(moves, list)
        assert len(moves) > 0

    def test_get_piece_legal_moves_returns_list(self) -> None:
        """get_piece_legal_moves 返回列表"""
        board = Board()
        board = board.set_piece((9, 4), "K")  # need king for legal move check
        board = board.set_piece((9, 0), "R")
        validator = RuleValidator()
        moves = validator.get_piece_legal_moves(board, 9, 0)
        assert isinstance(moves, list)
        assert len(moves) > 0

    def test_get_piece_legal_moves_rejects_empty(self) -> None:
        """空位置返回空列表"""
        board = Board()
        board = board.set_piece((9, 4), "K")
        validator = RuleValidator()
        moves = validator.get_piece_legal_moves(board, 4, 4)
        assert moves == []

    def test_no_legal_moves_when_in_checkmate(self) -> None:
        """被将杀时无合法走子"""
        board = Board()
        board = board.set_piece((9, 4), "K")  # king
        board = board.set_piece((9, 3), "r")  # attacks left
        board = board.set_piece((9, 5), "r")  # blocks right (also attacks)
        board = board.set_piece((0, 4), "r")  # attacks column from top
        board = board.set_piece((8, 3), "R")  # red piece blocks diagonal
        board = board.set_piece((8, 5), "R")  # red piece blocks diagonal
        validator = RuleValidator()
        moves = validator.get_legal_moves(board, RED)
        assert len(moves) == 0
