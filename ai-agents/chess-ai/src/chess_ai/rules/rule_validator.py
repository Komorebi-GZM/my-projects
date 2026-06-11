"""
规则验证器 - 中国象棋走子合法性验证
"""

from __future__ import annotations

from chess_ai.board import BLACK, RED, Board
from chess_ai.board.types import PieceChar, Position, Side, get_side, opposite_side
from chess_ai.move import Move


class RuleValidator:
    """
    中国象棋规则验证器

    验证走子合法性，包括：
    - 各棋子走法规则
    - 九宫限制
    - 河界限制
    - 蹩马腿、塞象眼
    - 将军检测
    - 合法走子生成
    """

    def __init__(self) -> None:
        """初始化规则验证器"""
        pass

    # ─── 颜色归一化 ────────────────────────────────────────────

    @staticmethod
    def _normalize_color(color: str) -> Side:
        """将颜色参数归一化为小写"""
        if isinstance(color, str):
            return "red" if color.lower() == "red" else "black"
        return color

    # ─── 位置判定 ──────────────────────────────────────────────

    @staticmethod
    def _is_in_palace(pos: Position, color: Side) -> bool:
        """判断位置是否在九宫内"""
        row, col = pos
        if color == RED:
            return 7 <= row <= 9 and 3 <= col <= 5
        return 0 <= row <= 2 and 3 <= col <= 5

    @staticmethod
    def _has_crossed_river(pos: Position, color: Side) -> bool:
        """判断棋子是否已过河"""
        row, _ = pos
        if color == RED:
            return row <= 4
        return row >= 5

    @staticmethod
    def _is_on_own_side(pos: Position, color: Side) -> bool:
        """判断棋子是否在己方半场"""
        row, _ = pos
        if color == RED:
            return row >= 5
        return row <= 4

    # ─── 棋盘操作 ──────────────────────────────────────────────

    @staticmethod
    def apply_move(board: Board, move: Move) -> Board:
        """应用走子到棋盘（返回新棋盘，不修改原棋盘），自动切换走子方"""
        new_board = board.remove_piece(move.from_pos)
        new_board = new_board.set_piece(move.to_pos, move.piece)
        # 切换走子方
        new_turn = opposite_side(board.current_turn)
        return Board(
            grid=new_board.grid,
            current_turn=new_turn,
            half_move_clock=new_board.half_move_clock,
            full_move_number=new_board.full_move_number,
            fen_history=new_board.fen_history,
            move_history=new_board.move_history,
        )

    # ─── 路径检测 ──────────────────────────────────────────────

    @staticmethod
    def _is_path_clear(board: Board, from_pos: Position, to_pos: Position) -> bool:
        """检查直线路径是否畅通（不含起点和终点）"""
        fr, fc = from_pos
        tr, tc = to_pos

        if fr == tr:
            step = 1 if tc > fc else -1
            for c in range(fc + step, tc, step):
                if board.get_piece((fr, c)) is not None:
                    return False
            return True

        if fc == tc:
            step = 1 if tr > fr else -1
            for r in range(fr + step, tr, step):
                if board.get_piece((r, fc)) is not None:
                    return False
            return True

        return False

    @staticmethod
    def _count_screens(board: Board, from_pos: Position, to_pos: Position) -> int:
        """统计直线路径上的棋子数量（不含起点和终点）"""
        fr, fc = from_pos
        tr, tc = to_pos
        count = 0

        if fr == tr:
            step = 1 if tc > fc else -1
            for c in range(fc + step, tc, step):
                if board.get_piece((fr, c)) is not None:
                    count += 1
            return count

        if fc == tc:
            step = 1 if tr > fr else -1
            for r in range(fr + step, tr, step):
                if board.get_piece((r, fc)) is not None:
                    count += 1
            return count

        return 0

    # ─── 基本验证入口 ──────────────────────────────────────────

    def validate_move(self, move: Move, board: Board, color: str) -> bool:
        """
        验证走子的基本合法性

        Args:
            move: 要验证的走子
            board: 当前棋盘
            color: 走子方

        Returns:
            True 如果走子合法
        """
        color = self._normalize_color(color)

        # 检查起始位置有棋子
        piece = board.get_piece(move.from_pos)
        if piece is None:
            return False

        # 检查棋子属于走子方
        if get_side(piece) != color:
            return False

        # 检查不是原地走子
        if move.from_pos == move.to_pos:
            return False

        # 检查目标位置没有己方棋子
        dest_piece = board.get_piece(move.to_pos)
        if dest_piece is not None and get_side(dest_piece) == color:
            return False

        # 按棋子类型验证走法
        piece_type = piece.upper()
        validators = {
            "K": self._validate_king_move,
            "A": self._validate_advisor_move,
            "B": self._validate_bishop_move,
            "R": self._validate_rook_move,
            "N": self._validate_knight_move,
            "C": self._validate_cannon_move,
            "P": self._validate_pawn_move,
        }

        validator = validators.get(piece_type)
        if validator is None:
            return False

        return validator(move, board)

    # ─── 棋子走法验证器 ──────────────────────────────────────

    @staticmethod
    def _validate_king_move(move: Move, board: Board) -> bool:
        """验证帅/将走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        dr = abs(tr - fr)
        dc = abs(tc - fc)

        # 只能走一步（包括对角/直走都算一步。但中国象棋的将/帅只能直走一格）
        # 将/帅只能走直线一格
        if not ((dr == 1 and dc == 0) or (dr == 0 and dc == 1)):
            return False

        color = get_side(move.piece)
        return RuleValidator._is_in_palace(move.to_pos, color)

    @staticmethod
    def _validate_advisor_move(move: Move, board: Board) -> bool:
        """验证仕/士走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        dr = abs(tr - fr)
        dc = abs(tc - fc)

        # 斜走一步
        if not (dr == 1 and dc == 1):
            return False

        color = get_side(move.piece)
        return RuleValidator._is_in_palace(move.to_pos, color)

    def _validate_bishop_move(self, move: Move, board: Board) -> bool:
        """验证相/象走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        dr = abs(tr - fr)
        dc = abs(tc - fc)

        # 斜走两步（田字）
        if not (dr == 2 and dc == 2):
            return False

        color = get_side(move.piece)

        # 不能过河
        if not self._is_on_own_side(move.to_pos, color):
            return False

        # 象眼不能被堵
        eye_r = (fr + tr) // 2
        eye_c = (fc + tc) // 2
        if board.get_piece((eye_r, eye_c)) is not None:
            return False

        return True

    def _validate_rook_move(self, move: Move, board: Board) -> bool:
        """验证车走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos

        # 必须直线走
        if fr != tr and fc != tc:
            return False

        # 路径不能被阻挡
        return self._is_path_clear(board, move.from_pos, move.to_pos)

    def _validate_knight_move(self, move: Move, board: Board) -> bool:
        """验证马走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        dr = tr - fr
        dc = tc - fc
        abs_dr = abs(dr)
        abs_dc = abs(dc)

        # 日字形：|dr|=2,|dc|=1 或 |dr|=1,|dc|=2
        if not ((abs_dr == 2 and abs_dc == 1) or (abs_dr == 1 and abs_dc == 2)):
            return False

        # 检查蹩马腿
        if abs_dr == 2:
            leg_r = fr + (1 if dr > 0 else -1)
            leg_c = fc
        else:
            leg_r = fr
            leg_c = fc + (1 if dc > 0 else -1)

        return board.get_piece((leg_r, leg_c)) is None

    def _validate_cannon_move(self, move: Move, board: Board) -> bool:
        """验证炮走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos

        # 必须直线走
        if fr != tr and fc != tc:
            return False

        is_capture = board.get_piece(move.to_pos) is not None

        if not is_capture:
            # 不吃子时，像车一样移动
            return self._is_path_clear(board, move.from_pos, move.to_pos)

        # 吃子时需要恰好一个炮架
        return self._count_screens(board, move.from_pos, move.to_pos) == 1

    def _validate_pawn_move(self, move: Move, board: Board) -> bool:
        """验证兵/卒走法"""
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        dr = tr - fr
        dc = tc - fc
        abs_dr = abs(dr)
        abs_dc = abs(dc)

        color = get_side(move.piece)
        has_crossed = self._has_crossed_river(move.from_pos, color)

        # 只能走一步
        if abs_dr + abs_dc != 1:
            return False

        # 向前方向
        forward = -1 if color == RED else 1

        if dr == forward and dc == 0:
            return True

        # 横走：只有过河后才能横走
        if dc != 0 and dr == 0:
            return has_crossed

        # 后退：永远不允许
        return False

    # ─── 走子生成 ──────────────────────────────────────────────

    def _generate_raw_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成某个棋子的候选走子列表"""
        piece_type = piece.upper()
        generators = {
            "K": self._gen_king_moves,
            "A": self._gen_advisor_moves,
            "B": self._gen_bishop_moves,
            "R": self._gen_rook_moves,
            "N": self._gen_knight_moves,
            "C": self._gen_cannon_moves,
            "P": self._gen_pawn_moves,
        }
        gen = generators.get(piece_type)
        if gen is None:
            return []
        return gen(board, row, col, piece)

    def _gen_king_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成帅/将的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr <= 9 and 0 <= nc <= 8:
                if self._is_in_palace((nr, nc), color):
                    dest = board.get_piece((nr, nc))
                    if dest is None or get_side(dest) != color:
                        moves.append(
                            Move(
                                from_pos=(row, col),
                                to_pos=(nr, nc),
                                piece=piece,
                                captured_piece=dest,
                            )
                        )
        return moves

    def _gen_advisor_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成仕/士的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr <= 9 and 0 <= nc <= 8:
                if self._is_in_palace((nr, nc), color):
                    dest = board.get_piece((nr, nc))
                    if dest is None or get_side(dest) != color:
                        moves.append(
                            Move(
                                from_pos=(row, col),
                                to_pos=(nr, nc),
                                piece=piece,
                                captured_piece=dest,
                            )
                        )
        return moves

    def _gen_bishop_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成相/象的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        for dr, dc in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr <= 9 and 0 <= nc <= 8:
                if not self._is_on_own_side((nr, nc), color):
                    continue
                eye_r, eye_c = (row + nr) // 2, (col + nc) // 2
                if board.get_piece((eye_r, eye_c)) is not None:
                    continue
                dest = board.get_piece((nr, nc))
                if dest is None or get_side(dest) != color:
                    moves.append(
                        Move(
                            from_pos=(row, col),
                            to_pos=(nr, nc),
                            piece=piece,
                            captured_piece=dest,
                        )
                    )
        return moves

    def _gen_knight_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成马/馬的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr <= 9 and 0 <= nc <= 8:
                if abs(dr) == 2:
                    leg_r = row + (1 if dr > 0 else -1)
                    leg_c = col
                else:
                    leg_r = row
                    leg_c = col + (1 if dc > 0 else -1)
                if board.get_piece((leg_r, leg_c)) is not None:
                    continue
                dest = board.get_piece((nr, nc))
                if dest is None or get_side(dest) != color:
                    moves.append(
                        Move(
                            from_pos=(row, col),
                            to_pos=(nr, nc),
                            piece=piece,
                            captured_piece=dest,
                        )
                    )
        return moves

    def _gen_rook_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成车的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr <= 9 and 0 <= nc <= 8:
                dest = board.get_piece((nr, nc))
                if dest is None:
                    moves.append(
                        Move(
                            from_pos=(row, col),
                            to_pos=(nr, nc),
                            piece=piece,
                            captured_piece=None,
                        )
                    )
                else:
                    if get_side(dest) != color:
                        moves.append(
                            Move(
                                from_pos=(row, col),
                                to_pos=(nr, nc),
                                piece=piece,
                                captured_piece=dest,
                            )
                        )
                    break
                nr += dr
                nc += dc
        return moves

    def _gen_cannon_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成炮的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            screen_found = False
            while 0 <= nr <= 9 and 0 <= nc <= 8:
                dest = board.get_piece((nr, nc))
                if not screen_found:
                    if dest is None:
                        moves.append(
                            Move(
                                from_pos=(row, col),
                                to_pos=(nr, nc),
                                piece=piece,
                                captured_piece=None,
                            )
                        )
                    else:
                        screen_found = True
                else:
                    if dest is not None:
                        if get_side(dest) != color:
                            moves.append(
                                Move(
                                    from_pos=(row, col),
                                    to_pos=(nr, nc),
                                    piece=piece,
                                    captured_piece=dest,
                                )
                            )
                        break
                nr += dr
                nc += dc
        return moves

    def _gen_pawn_moves(self, board: Board, row: int, col: int, piece: PieceChar) -> list[Move]:
        """生成兵/卒的候选走子"""
        color = get_side(piece)
        moves: list[Move] = []
        forward = -1 if color == RED else 1

        candidates: list[tuple[int, int]] = [(row + forward, col)]
        if self._has_crossed_river((row, col), color):
            candidates.append((row, col + 1))
            candidates.append((row, col - 1))

        for nr, nc in candidates:
            if 0 <= nr <= 9 and 0 <= nc <= 8:
                dest = board.get_piece((nr, nc))
                if dest is None or get_side(dest) != color:
                    moves.append(
                        Move(
                            from_pos=(row, col),
                            to_pos=(nr, nc),
                            piece=piece,
                            captured_piece=dest,
                        )
                    )
        return moves

    # ─── 将军检测 ──────────────────────────────────────────────

    def is_in_check(self, board: Board, color: str) -> bool:
        """
        判断指定方是否被将军

        Args:
            board: 当前棋盘
            color: 要检查的方

        Returns:
            True 如果被将军
        """
        color = self._normalize_color(color)

        # 帅将对脸也视为将军
        if self.is_kings_facing(board):
            return True

        king_pos = board.get_king_position(color)
        enemy_color = opposite_side(color)

        # 检查所有敌方棋子是否能攻击到己方帅/将
        for row in range(10):
            for col in range(9):
                piece = board.get_piece((row, col))
                if piece is not None and get_side(piece) == enemy_color:
                    move = Move(
                        from_pos=(row, col),
                        to_pos=king_pos,
                        piece=piece,
                        captured_piece=board.get_piece(king_pos),
                    )
                    if self.validate_move(move, board, enemy_color):
                        return True

        return False

    def will_cause_check(self, move: Move, board: Board, color: str) -> bool:
        """
        判断执行走子后是否会导致己方被将军

        Args:
            move: 要检查的走子
            board: 当前棋盘
            color: 走子方

        Returns:
            True 如果走子后己方被将军
        """
        color = self._normalize_color(color)
        new_board = self.apply_move(board, move)
        return self.is_in_check(new_board, color)

    # ─── 帅将对脸检测 ──────────────────────────────────────────

    def is_kings_facing(self, board: Board) -> bool:
        """
        判断两个帅/将是否对面（同列无遮挡）

        Returns:
            True 如果两个帅将对面
        """
        try:
            red_king = board.get_king_position(RED)
            black_king = board.get_king_position(BLACK)
        except ValueError:
            return False

        # 必须在同一列
        if red_king[1] != black_king[1]:
            return False

        # 检查中间是否有棋子
        col = red_king[1]
        min_row = min(red_king[0], black_king[0])
        max_row = max(red_king[0], black_king[0])

        for row in range(min_row + 1, max_row):
            if board.get_piece((row, col)) is not None:
                return False

        return True

    # ─── 合法走子生成 ──────────────────────────────────────────

    def get_piece_legal_moves(self, board: Board, row: int, col: int) -> list[Move]:
        """
        获取指定位置上棋子的所有合法走子

        Args:
            board: 当前棋盘
            row: 行
            col: 列

        Returns:
            合法走子列表
        """
        piece = board.get_piece((row, col))
        if piece is None:
            return []

        color = get_side(piece)
        candidates = self._generate_raw_moves(board, row, col, piece)
        legal: list[Move] = []

        for move in candidates:
            # 验证走子规则
            if not self.validate_move(move, board, color):
                continue
            # 验证不会导致被将军
            if self.will_cause_check(move, board, color):
                continue
            legal.append(move)

        return legal

    def get_legal_moves(self, board: Board, color: str) -> list[Move]:
        """
        获取指定方的所有合法走子

        Args:
            board: 当前棋盘
            color: 走子方

        Returns:
            所有合法走子列表
        """
        color = self._normalize_color(color)
        all_moves: list[Move] = []

        for row in range(10):
            for col in range(9):
                piece = board.get_piece((row, col))
                if piece is not None and get_side(piece) == color:
                    all_moves.extend(self.get_piece_legal_moves(board, row, col))

        return all_moves
