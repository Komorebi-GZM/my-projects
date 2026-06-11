"""
游戏控制器 - 交互控制类，管理状态机
"""

from __future__ import annotations

import logging
import threading
from enum import Enum, auto

import pygame

from ..agent import AgentOrchestrator
from ..board import BLACK, RED, Board
from ..infra import ConfigManager
from ..infra.difficulty import Difficulty
from ..rules import FENSerializer
from .config import GUIConfig
from .recorder import GameRecorder
from .renderer import ChessRenderer, difficulty_button_rects
from .theme import ColorTheme, ThemeManager, ucci_to_rowcol

logger = logging.getLogger(__name__)


class GameState(Enum):
    """游戏状态枚举"""

    WAITING = auto()
    PIECE_SELECTED = auto()
    AI_THINKING = auto()
    GAME_OVER = auto()
    STARTUP = auto()
    SELECTING_DIFFICULTY = auto()
    SETTINGS = auto()
    GAME_LIST = auto()
    REPLAY = auto()


class GameController:
    """
    游戏控制器 - 协调 GUI、规则引擎、Agent 三方交互

    管理游戏状态机，处理用户输入，调度 AI 调用
    """

    def __init__(
        self,
        config: GUIConfig,
        renderer: ChessRenderer,
        theme: ColorTheme | None = None,
    ):
        self.config = config
        self.renderer = renderer
        self.theme = theme

        # 游戏状态
        self.state: GameState = GameState.SELECTING_DIFFICULTY
        self.selected_pos: tuple[int, int] | None = None
        self.legal_moves: list[tuple[int, int]] = []
        self.message: str = ""

        # 棋盘状态
        self.board = FENSerializer.from_fen(FENSerializer.to_fen(Board.create_initial()))
        self.last_move: tuple[tuple[int, int], tuple[int, int]] | None = None
        self.check_pos: tuple[int, int] | None = None

        # 难度选择
        self.difficulty: Difficulty = Difficulty.MEDIUM

        # 主题设置
        self._current_theme: str = "classic"

        # 复盘模式
        self._replay_moves: list[tuple[str, str, str]] = []  # [(ucci, fen_before, side), ...]
        self._replay_index: int = 0
        self._replay_game_id: int | None = None

        # Agent
        self.agent = AgentOrchestrator()

        # AI 线程
        self._ai_thread: threading.Thread | None = None
        self._ai_result: str | None = None
        self._ai_error: str | None = None
        self._ai_done: threading.Event = threading.Event()

        # 主窗口 Surface
        self._surface: pygame.Surface | None = None
        # 撤销/重做历史栈：存储 (fen, last_move, check_pos)
        self._undo_stack: list[tuple[str, tuple | None, tuple | None]] = []
        self._redo_stack: list[tuple[str, tuple | None, tuple | None]] = []

        # 棋谱记录器
        self._recorder = GameRecorder()

        logger.info("GameController 初始化完成")

    def set_surface(self, surface: pygame.Surface) -> None:
        """设置主窗口 Surface"""
        self._surface = surface

    def start_game(self) -> None:
        """开始新游戏"""
        self.board = FENSerializer.from_fen(FENSerializer.to_fen(Board.create_initial()))
        self.state = GameState.WAITING
        self.selected_pos = None
        self.legal_moves = []
        self.message = ""
        self.last_move = None
        self.check_pos = None
        self._undo_stack = []
        self._redo_stack = []

        self.agent = AgentOrchestrator()

        # 开始棋谱记录
        self._recorder.start_game(FENSerializer.to_fen(self.board), "red")

        logger.info("游戏开始")

    def _record_state(self) -> None:
        """记录当前状态到 undo 栈（人类走子前调用）"""
        self._undo_stack.append((FENSerializer.to_fen(self.board), self.last_move, self.check_pos))
        self._redo_stack.clear()

    def undo(self) -> bool:
        """
        撤销上一步（成对撤销：人类+AI 各一步）

        Returns:
            是否成功撤销
        """
        if not self._undo_stack:
            return False

        # 等待 AI 线程结束
        if self._ai_thread is not None and self._ai_thread.is_alive():
            self._ai_thread.join(timeout=1.0)

        # 成对撤销：连续撤销人类步+AI步（如果 AI 有走子）
        for _ in range(2):
            if not self._undo_stack:
                break
            fen, last, check = self._undo_stack.pop()
            self._redo_stack.append((fen, last, check))
            self.board = FENSerializer.from_fen(fen)
            self.last_move = last
            self.check_pos = check

        # 同步 agent 棋盘状态
        self.agent.restore_board(self.board)
        self.state = GameState.WAITING
        self.selected_pos = None
        self.legal_moves = []
        self.message = "已撤销"
        logger.info("撤销成功")
        return True

    def redo(self) -> bool:
        """
        重做上一步（成对重做：恢复人类+AI 各一步）

        Returns:
            是否成功重做
        """
        if not self._redo_stack:
            return False

        if self._ai_thread is not None and self._ai_thread.is_alive():
            self._ai_thread.join(timeout=1.0)

        # 成对重做：连续恢复 AI 步 + 人类步
        pushed = 0
        while pushed < 2 and self._redo_stack:
            redone = self._redo_stack.pop()
            self._undo_stack.append((FENSerializer.to_fen(self.board), self.last_move, self.check_pos))
            fen, last, check = redone
            self.board = FENSerializer.from_fen(fen)
            self.last_move = last
            self.check_pos = check
            pushed += 1

        self.agent.restore_board(self.board)
        self.state = GameState.WAITING
        self.selected_pos = None
        self.legal_moves = []
        self.message = ""
        logger.info(f"重做成功（{pushed}步）")
        return True

    @property
    def can_undo(self) -> bool:
        """是否可以撤销"""
        return len(self._undo_stack) >= 1

    @property
    def can_redo(self) -> bool:
        """是否可以重做"""
        return len(self._redo_stack) >= 1

    def reset_game(self) -> None:
        """重置游戏"""
        self.start_game()
        logger.info("游戏已重置")

    def _handle_settings_click(self, screen_x: int, screen_y: int) -> None:
        """处理设置界面点击"""
        dialog_width = 350
        dialog_height = 300
        dialog_x = (self.config.window_width - dialog_width) // 2
        dialog_y = (self.config.window_height - dialog_height) // 2

        # 关闭按钮
        close_y = dialog_y + dialog_height - 50
        close_width = 100
        close_height = 36
        close_x = (self.config.window_width - close_width) // 2
        close_rect = pygame.Rect(close_x, close_y, close_width, close_height)
        if close_rect.collidepoint(screen_x, screen_y):
            self.state = GameState.WAITING
            self.message = ""
            return

        # 音效开关
        option_y = dialog_y + 60
        option_spacing = 50
        sound_button_x = dialog_x + dialog_width - 80
        sound_rect = pygame.Rect(sound_button_x, option_y, 40, 30)
        if sound_rect.collidepoint(screen_x, screen_y):
            self.config.sound_enabled = not self.config.sound_enabled
            self.message = f"音效已{'开启' if self.config.sound_enabled else '关闭'}"
            return

        # 动画开关
        anim_y = option_y + option_spacing
        anim_rect = pygame.Rect(sound_button_x, anim_y, 40, 30)
        if anim_rect.collidepoint(screen_x, screen_y):
            self.config.animation_enabled = not self.config.animation_enabled
            self.message = f"动画已{'开启' if self.config.animation_enabled else '关闭'}"
            return

        # 主题选择
        theme_y = anim_y + option_spacing
        themes = ["classic", "modern", "dark"]
        theme_btn_width = 60
        theme_btn_spacing = 10
        theme_start_x = dialog_x + dialog_width - 3 * theme_btn_width - 2 * theme_btn_spacing - 20

        for i, theme_key in enumerate(themes):
            x = theme_start_x + i * (theme_btn_width + theme_btn_spacing)
            theme_rect = pygame.Rect(x, theme_y, theme_btn_width, 30)
            if theme_rect.collidepoint(screen_x, screen_y):
                self._current_theme = theme_key
                self.message = f"主题已切换为: {theme_key}"
                self.renderer.set_theme(ThemeManager.get_theme(theme_key))
                return

    def _handle_game_list_click(self, screen_x: int, screen_y: int) -> None:
        """处理棋谱列表点击"""
        # 返回按钮
        back_btn_x = 10
        back_btn_y = 10
        back_btn_w = 60
        back_btn_h = 30
        if back_btn_x <= screen_x <= back_btn_x + back_btn_w and back_btn_y <= screen_y <= back_btn_y + back_btn_h:
            self.state = GameState.WAITING
            return

        # 游戏列表区域
        list_start_y = 60
        item_height = 60

        # 计算点击在列表中的索引
        clicked_index = (screen_y - list_start_y) // item_height
        if clicked_index >= 0:
            games = self._recorder.get_all_games()
            if 0 <= clicked_index < len(games):
                game = games[clicked_index]
                if game.id is not None:
                    self._load_game_for_replay(game.id)
                    self.state = GameState.REPLAY

    def _handle_replay_click(self, screen_x: int, screen_y: int) -> None:
        """处理复盘模式点击"""
        # 返回按钮
        back_btn_x = 10
        back_btn_y = 10
        back_btn_w = 60
        back_btn_h = 30
        if back_btn_x <= screen_x <= back_btn_x + back_btn_w and back_btn_y <= screen_y <= back_btn_y + back_btn_h:
            self.state = GameState.GAME_LIST
            return

        # 上一步按钮
        prev_btn_x = 50
        prev_btn_y = self.config.window_height - 120
        prev_btn_w = 80
        prev_btn_h = 40
        if prev_btn_x <= screen_x <= prev_btn_x + prev_btn_w and prev_btn_y <= screen_y <= prev_btn_y + prev_btn_h:
            self._replay_prev()
            return

        # 下一步按钮
        next_btn_x = prev_btn_x + prev_btn_w + 20
        next_btn_y = prev_btn_y
        if next_btn_x <= screen_x <= next_btn_x + prev_btn_w and next_btn_y <= screen_y <= next_btn_y + prev_btn_h:
            self._replay_next()
            return

    def _load_game_for_replay(self, game_id: int) -> None:
        """加载对局用于复盘"""
        game, moves = self._recorder.load_game(game_id)
        if not game:
            return

        # 解析走子历史
        self._replay_moves = [(m.move_ucci, m.fen_before, m.side) for m in moves]
        self._replay_index = 0
        self._replay_game_id = game_id

        # 加载初始棋盘
        if game.fen_initial:
            self.board = FENSerializer.from_fen(game.fen_initial)
        else:
            self.board = FENSerializer.from_fen(FENSerializer.to_fen(Board.create_initial()))

        self.last_move = None
        self.check_pos = None

    def _replay_prev(self) -> None:
        """复盘上一步"""
        if self._replay_index > 0:
            self._replay_index -= 1
            self._update_replay_board()

    def _replay_next(self) -> None:
        """复盘下一步"""
        if self._replay_index < len(self._replay_moves):
            self._replay_index += 1
            self._update_replay_board()

    def _update_replay_board(self) -> None:
        """根据复盘索引更新棋盘"""
        if self._replay_index == 0:
            # 回到初始局面
            game, _ = self._recorder.load_game(self._replay_game_id) if self._replay_game_id else (None, [])
            if game and game.fen_initial:
                self.board = FENSerializer.from_fen(game.fen_initial)
            else:
                self.board = FENSerializer.from_fen(FENSerializer.to_fen(Board.create_initial()))
            self.last_move = None
            self.check_pos = None
        else:
            # 应用到第 index 步的走子后的局面
            # 走子后的 FEN 需要从下一步的 fen_before 获取
            if self._replay_index <= len(self._replay_moves):
                _, fen_before, _ = self._replay_moves[self._replay_index - 1]
                if fen_before:
                    self.board = FENSerializer.from_fen(fen_before)

                # 获取上一步走子
                if self._replay_index > 0:
                    move_ucci, _, _ = self._replay_moves[self._replay_index - 1]
                    try:
                        from_pos, to_pos = ucci_to_rowcol(move_ucci)
                        self.last_move = (from_pos, to_pos)
                    except Exception:
                        self.last_move = None
                else:
                    self.last_move = None

    def handle_click(self, screen_x: int, screen_y: int) -> None:
        """
        处理鼠标点击事件

        Args:
            screen_x: 屏幕 x 坐标
            screen_y: 屏幕 y 坐标
        """
        # 检查工具栏点击
        if screen_y >= self.config.window_height - 50:
            self.handle_toolbar_click(screen_x, screen_y)
            return

        if self.state == GameState.SELECTING_DIFFICULTY:
            self._handle_difficulty_click(screen_x, screen_y)
            return

        if self.state == GameState.SETTINGS:
            self._handle_settings_click(screen_x, screen_y)
            return

        if self.state == GameState.GAME_LIST:
            self._handle_game_list_click(screen_x, screen_y)
            return

        if self.state == GameState.REPLAY:
            self._handle_replay_click(screen_x, screen_y)
            return

        if self.state in (GameState.AI_THINKING, GameState.STARTUP, GameState.GAME_OVER):
            return

        # 转换为棋盘坐标
        board_pos = self.renderer.screen_to_board(screen_x, screen_y)
        if board_pos is None:
            return

        row, col = board_pos

        if self.state == GameState.WAITING:
            self._handle_waiting_click(row, col)

        elif self.state == GameState.PIECE_SELECTED:
            self._handle_selected_click(row, col)

    def _handle_difficulty_click(self, screen_x: int, screen_y: int) -> None:
        """处理难度选择界面点击"""
        for difficulty, rect in difficulty_button_rects(self.config):
            if rect.collidepoint(screen_x, screen_y):
                self._select_difficulty(difficulty)
                return

    def _select_difficulty(self, difficulty: Difficulty) -> None:
        """选择难度并开始游戏"""
        self.difficulty = difficulty

        config = ConfigManager()
        config.set_difficulty(difficulty)
        config.save()

        logger.info(f"难度已选择: {difficulty.value}")

        # 创建新棋局
        self.start_game()

    def _handle_waiting_click(self, row: int, col: int) -> None:
        """处理等待状态下点击"""
        piece = self.board.get_piece((row, col))

        # 是否点击了己方棋子
        if piece is not None and piece.isupper():
            self._select_piece(row, col)

    def _handle_selected_click(self, row: int, col: int) -> None:
        """处理棋子选中状态下点击"""
        piece = self.board.get_piece((row, col))

        # 点击其他己方棋子 -> 切换选中
        if piece is not None and piece.isupper():
            self._select_piece(row, col)
            return

        # 点击合法走位 -> 执行走子
        target_pos = (row, col)
        if target_pos in self.legal_moves:
            self._execute_move(target_pos)
            return

        # 点击非法位置 -> 保持选中并提示
        self.message = "非法走子"

    def _select_piece(self, row: int, col: int) -> None:
        """选中棋子"""
        self.selected_pos = (row, col)
        self.state = GameState.PIECE_SELECTED

        self.legal_moves = self.agent.get_piece_legal_targets((row, col))

        self.message = ""
        logger.debug(f"选中棋子 ({row},{col})，合法走位 {len(self.legal_moves)} 个")

    def _execute_move(self, target_pos: tuple[int, int]) -> None:
        """执行走子"""
        if self.selected_pos is None:
            return

        # 记录状态用于撤销（人类走子前）
        self._record_state()

        _from_row, _from_col = self.selected_pos
        _to_row, _to_col = target_pos

        # 通过 agent 执行
        success, msg = self.agent.process_user_move(
            self.selected_pos,
            target_pos,
        )

        if not success:
            # 撤销刚记录的状态
            if self._undo_stack:
                self._undo_stack.pop()
            self.message = msg
            return

        # 更新本地棋盘
        self.board = self.agent.current_board

        # 记录走子
        self.last_move = (self.selected_pos, target_pos)

        # 记录到棋谱（人类走子）
        move_ucci = f"{chr(97 + _from_col)}{_from_row}{chr(97 + _to_col)}{_to_row}"
        fen_before = FENSerializer.to_fen(self.board)  # 这是走子前的FEN，需要获取之前的
        # 为了得到走子前的FEN，我们需要从撤销栈中获取
        if self._undo_stack:
            fen_before = self._undo_stack[-1][0]  # 获取最近的FEN
        else:
            fen_before = FENSerializer.to_fen(Board.create_initial())  # 初始局面
        self._recorder.record_move(move_ucci, fen_before, "red")

        self.check_pos = self.agent.get_check_position(BLACK)

        if self.agent.is_game_over:
            self.state = GameState.GAME_OVER
            reason = self.agent.game_result or "游戏结束"
            self.message = reason
            self._recorder.end_game(
                "red_win" if "red" in reason.lower() else "black_win" if "black" in reason.lower() else "draw"
            )
            return

        # 切换为 AI 回合
        self.state = GameState.AI_THINKING
        self.selected_pos = None
        self.legal_moves = []
        self.message = "AI 思考中..."

        # AI 走子前记录状态（方便撤销 AI 那步）
        self._undo_stack.append((FENSerializer.to_fen(self.board), self.last_move, self.check_pos))
        self._redo_stack.clear()

        # 启动 AI 线程
        self._start_ai_thread()

    def _start_ai_thread(self) -> None:
        """启动 AI 走子的子线程"""
        self._ai_done.clear()
        self._ai_result = None
        self._ai_error = None

        self._ai_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self._ai_thread.start()

    def _ai_worker(self) -> None:
        """AI 走子的子线程工作函数"""
        try:
            move, error = self.agent.generate_ai_move()
            self._ai_result = move
            self._ai_error = error
        except Exception as e:
            self._ai_error = str(e)
            logger.exception("AI 线程异常")
        finally:
            self._ai_done.set()

    def handle_key(self, key: int) -> None:
        """
        处理键盘事件

        Args:
            key: pygame 键常量
        """
        if key == pygame.K_r and self.state == GameState.GAME_OVER:
            self.reset_game()

        elif key == pygame.K_ESCAPE:
            if self.state == GameState.PIECE_SELECTED:
                self._cancel_selection()
            elif self.state == GameState.SETTINGS:
                self.state = GameState.WAITING
            elif self.state == GameState.GAME_OVER:
                pass

        elif key == pygame.K_z:
            mods = pygame.key.get_mods()
            if (mods & pygame.KMOD_CTRL) or (mods & pygame.KMOD_META):
                self.undo()

        elif key == pygame.K_y:
            mods = pygame.key.get_mods()
            if (mods & pygame.KMOD_CTRL) or (mods & pygame.KMOD_META):
                self.redo()

    def toggle_settings(self) -> None:
        """打开/关闭设置界面"""
        if self.state == GameState.SETTINGS:
            self.state = GameState.WAITING
        else:
            self.state = GameState.SETTINGS
        logger.info(f"设置界面{'打开' if self.state == GameState.SETTINGS else '关闭'}")

    def toggle_sound(self) -> None:
        """切换音效开关"""
        self.config.sound_enabled = not self.config.sound_enabled
        self.message = f"音效已{'开启' if self.config.sound_enabled else '关闭'}"
        logger.info(f"音效: {self.config.sound_enabled}")

    def show_game_list(self) -> None:
        """显示棋谱列表"""
        self.state = GameState.GAME_LIST
        logger.info("显示棋谱列表")

    def handle_toolbar_click(self, screen_x: int, screen_y: int) -> None:
        """
        处理工具栏点击事件

        Args:
            screen_x: 屏幕 x 坐标
            screen_y: 屏幕 y 坐标
        """
        toolbar_height = 50
        toolbar_y = self.config.window_height - toolbar_height

        if screen_y < toolbar_y:
            return

        button_size = 40
        button_margin = 10
        start_x = button_margin

        toolbar_buttons = [
            "reset_game",
            "undo",
            "redo",
            "show_game_list",  # 棋谱按钮
            "toggle_settings",
            "toggle_sound",
            None,  # exit - TODO
        ]

        for i, handler_name in enumerate(toolbar_buttons):
            x = start_x + i * (button_size + button_margin)
            btn_rect = pygame.Rect(x, toolbar_y + (toolbar_height - button_size) // 2, button_size, button_size)
            if btn_rect.collidepoint(screen_x, screen_y):
                if handler_name and hasattr(self, handler_name):
                    handler = getattr(self, handler_name)
                    if callable(handler):
                        handler()
                break

    def _cancel_selection(self) -> None:
        """取消棋子选中"""
        self.selected_pos = None
        self.legal_moves = []
        self.state = GameState.WAITING
        self.message = ""

    def update(self) -> None:
        """主循环更新 - 处理 AI 结果"""
        if self.state == GameState.AI_THINKING and self._ai_done.is_set():
            self._process_ai_result()

    def _process_ai_result(self) -> None:
        """处理 AI 走子结果"""
        self._ai_thread = None

        if self._ai_error:
            self.message = f"AI 走子失败: {self._ai_error}"
            # AI 失败，移除刚记录的 AI 走子状态
            if self._undo_stack:
                self._undo_stack.pop()
            # 即使 AI 失败，也尝试从 agent 获取棋盘
            if not self.agent.is_game_over:
                self.board = self.agent.current_board
            else:
                self.state = GameState.GAME_OVER
                self.message = self.agent.game_result or "游戏结束"
            return

        if self._ai_result:
            # 从 UCCI 解析走子
            try:
                from_pos, to_pos = ucci_to_rowcol(self._ai_result)
                self.last_move = (from_pos, to_pos)

                # 更新本地棋盘
                self.board = self.agent.current_board

                # 记录 AI 走子到棋谱
                fen_before = self._undo_stack[-1][0] if self._undo_stack else ""
                self._recorder.record_move(self._ai_result, fen_before, "black")

                self.check_pos = self.agent.get_check_position(RED)

                logger.info(f"AI 走子完成: {self._ai_result}")
            except Exception as e:
                logger.error(f"解析 AI 走子失败: {e}")
                self.board = self.agent.current_board

        # 检查游戏结束
        if self.agent.is_game_over:
            self.state = GameState.GAME_OVER
            self.message = self.agent.game_result or "游戏结束"
            # 记录对局结果
            result = self.agent.game_result or "draw"
            if "red" in result.lower():
                self._recorder.end_game("red_win")
            elif "black" in result.lower():
                self._recorder.end_game("black_win")
            else:
                self._recorder.end_game("draw")
        else:
            self.state = GameState.WAITING
            self.message = ""

    def render(self, surface: pygame.Surface) -> None:
        """
        渲染当前状态

        Args:
            surface: 目标 Surface
        """
        self.renderer.clear(surface)

        # 难度选择界面
        if self.state == GameState.SELECTING_DIFFICULTY:
            self.renderer.render_difficulty_selection(surface, self.difficulty)
            return

        # 设置界面
        if self.state == GameState.SETTINGS:
            # 渲染棋盘背景（作为背景）
            board_surface = self.renderer.render_board_background()
            surface.blit(board_surface, (0, 0))
            self.renderer.render_pieces(surface, self.board.grid)
            self.renderer.render_toolbar(surface, self)
            self.renderer.render_settings_dialog(surface, self)
            return

        # 棋谱列表界面
        if self.state == GameState.GAME_LIST:
            self.renderer.render_game_list(surface, self._recorder.get_all_games())
            return

        # 复盘界面
        if self.state == GameState.REPLAY:
            board_surface = self.renderer.render_board_background()
            surface.blit(board_surface, (0, 0))
            self.renderer.render_pieces(surface, self.board.grid)
            if self.last_move:
                from_pos, to_pos = self.last_move
                self.renderer.render_highlight(surface, from_pos, (100, 149, 237), "last_move")
                self.renderer.render_highlight(surface, to_pos, (100, 149, 237), "last_move")
            self.renderer.render_replay_controls(surface, self._replay_index, len(self._replay_moves))
            return

        # 渲染棋盘背景
        board_surface = self.renderer.render_board_background()
        surface.blit(board_surface, (0, 0))

        # 渲染棋子
        self.renderer.render_pieces(surface, self.board.grid)  # type: ignore[arg-type]

        # 渲染高亮
        if self.state == GameState.PIECE_SELECTED and self.selected_pos:
            # 选中棋子的黄色边框
            self.renderer.render_highlight(surface, self.selected_pos, (255, 255, 0), "selected")
            # 合法走位
            occupied = set()
            for r in range(10):
                for c in range(9):
                    if self.board.get_piece((r, c)) is not None:
                        occupied.add((r, c))
            self.renderer.render_legal_moves(surface, self.legal_moves, occupied)

        # 上一步走子标记
        if self.last_move:
            from_pos, to_pos = self.last_move
            self.renderer.render_highlight(surface, from_pos, (100, 149, 237), "last_move")
            self.renderer.render_highlight(surface, to_pos, (100, 149, 237), "last_move")

        # 将军提示
        if self.check_pos:
            self.renderer.render_highlight(surface, self.check_pos, (255, 0, 0), "check")

        # 状态栏
        turn = "red" if self.state != GameState.AI_THINKING else "black"
        self.renderer.render_status_bar(
            surface,
            turn,
            self.message,
            ai_thinking=(self.state == GameState.AI_THINKING),
        )

        # 工具栏
        self.renderer.render_toolbar(surface, self)

        # 游戏结束对话框
        if self.state == GameState.GAME_OVER:
            self.renderer.render_game_over_dialog(surface, self.message)
