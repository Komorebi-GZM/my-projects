"""
棋盘渲染器 - 纯渲染类，不包含业务逻辑
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

import pygame

from ..infra.difficulty import Difficulty
from .config import GUIConfig
from .theme import ColorTheme, ThemeManager, get_piece_color, get_piece_name

logger = logging.getLogger(__name__)


def difficulty_button_rects(config: GUIConfig) -> list[tuple[Difficulty, pygame.Rect]]:
    """返回难度选择按钮区域，供绘制和点击命中共用。"""
    button_width = 128
    button_height = 48
    button_spacing = 18
    total_width = 3 * button_width + 2 * button_spacing
    start_x = (config.window_width - total_width) // 2
    button_y = config.board_margin * 2 + 9 * config.grid_size + 36
    return [
        (Difficulty.EASY, pygame.Rect(start_x, button_y, button_width, button_height)),
        (
            Difficulty.MEDIUM,
            pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
        ),
        (
            Difficulty.HARD,
            pygame.Rect(start_x + 2 * (button_width + button_spacing), button_y, button_width, button_height),
        ),
    ]


class ControllerRenderState(Protocol):
    """渲染器需要读取的控制器状态。"""

    config: GUIConfig
    _current_theme: str

    @property
    def can_undo(self) -> bool:
        """是否可以撤销"""
        ...

    @property
    def can_redo(self) -> bool:
        """是否可以重做"""
        ...


def _get_font_path() -> str | None:
    """获取中文字体路径，优先使用项目资源目录中的字体"""
    # 尝试多种可能的字体路径
    possible_paths = [
        # 项目 assets/fonts 目录
        Path(__file__).parent.parent.parent.parent / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
        # 工作目录 assets/fonts 目录
        Path.cwd() / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
        # 上层工作目录
        Path.cwd().parent / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
    ]

    for path in possible_paths:
        if path.exists():
            logger.info(f"找到中文字体: {path}")
            return str(path)

    logger.warning("未找到项目中文字体，将使用系统字体")
    return None


class ChessRenderer:
    """
    棋盘渲染器 - 纯渲染类

    职责:
    - 绘制棋盘背景、网格、九宫格
    - 绘制棋子
    - 绘制高亮（选中、合法走位、吃子提示）
    - 绘制状态栏
    - 坐标转换
    """

    def __init__(self, config: GUIConfig, theme: ColorTheme | None = None):
        self.config = config
        self.theme = theme or ThemeManager.get_theme()
        self._font: pygame.font.Font | None = None
        self._piece_surfaces: dict[str, pygame.Surface] = {}
        self._board_surface: pygame.Surface | None = None

    def set_theme(self, theme: ColorTheme) -> None:
        """切换渲染主题并清空依赖主题的缓存。"""
        self.theme = theme
        self._board_surface = None
        self._piece_surfaces.clear()

    @property
    def font(self) -> pygame.font.Font:
        """获取字体"""
        if self._font is None:
            font_path = _get_font_path()
            if font_path:
                try:
                    # 使用项目中的 NotoSansSC 字体（支持中文）
                    self._font = pygame.font.Font(font_path, self.config.piece_radius)
                    logger.info("成功加载中文字体")
                except Exception as e:
                    logger.warning(f"加载字体失败: {e}，使用系统字体")
                    self._font = self._get_system_font()
            else:
                self._font = self._get_system_font()
        return self._font

    def _get_system_font(self) -> pygame.font.Font:
        """获取系统字体，优先选择支持中文的字体"""
        # 按优先级尝试多种支持中文的系统字体
        font_names = [
            "Noto Sans CJK SC",  # Linux 常见
            "Noto Sans SC",  # Linux 常见
            "WenQuanYi Micro Hei",  # Linux 常见
            "SimHei",  # Windows 常见
            "Microsoft YaHei",  # Windows 常见
            "PingFang SC",  # macOS 常见
            "Hiragino Sans GB",  # macOS 常见
        ]

        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, self.config.piece_radius)
                # 验证字体是否能渲染中文
                test_surface = font.render("帅", True, (0, 0, 0))
                if test_surface.get_width() > 0:
                    logger.info(f"使用系统字体: {font_name}")
                    return font
            except Exception:
                continue

        # 如果都失败，使用默认字体
        logger.warning("未找到支持中文的系统字体")
        return pygame.font.Font(None, self.config.piece_radius)

    def init_pygame(self) -> None:
        """初始化 Pygame（必须在使用渲染器前调用）"""
        if not pygame.get_init():
            pygame.init()
        logger.info("ChessRenderer 初始化完成")

    def screen_to_board(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
        """
        屏幕像素坐标转棋盘行列

        Args:
            screen_x: 屏幕 x 坐标
            screen_y: 屏幕 y 坐标

        Returns:
            (row, col) 或 None（超出棋盘范围）
        """
        margin = self.config.board_margin
        grid = self.config.grid_size

        col = (screen_x - margin + grid // 2) // grid
        row = (screen_y - margin + grid // 2) // grid

        if 0 <= col <= 8 and 0 <= row <= 9:
            return (row, col)
        return None

    def board_to_screen(self, row: int, col: int) -> tuple[int, int]:
        """
        棋盘行列转屏幕像素坐标（格子中心点）

        Args:
            row: 行 0-9
            col: 列 0-8

        Returns:
            (screen_x, screen_y)
        """
        margin = self.config.board_margin
        grid = self.config.grid_size

        screen_x = margin + col * grid
        screen_y = margin + row * grid

        return (screen_x, screen_y)

    def render_board_background(self) -> pygame.Surface:
        """
        渲染棋盘背景（只渲染一次，缓存结果）

        Returns:
            棋盘背景 Surface
        """
        if self._board_surface is not None:
            return self._board_surface

        width = self.config.board_margin * 2 + 8 * self.config.grid_size
        height = self.config.board_margin * 2 + 9 * self.config.grid_size
        surface = pygame.Surface((width, height))

        # 填充棋盘底色和细微横向纹理
        surface.fill(self.theme.board_bg)
        for y in range(0, height, 12):
            color = self.theme.board_bg_alt if (y // 12) % 2 == 0 else self.theme.board_bg
            pygame.draw.line(surface, color, (0, y), (width, y), 1)

        frame_rect = pygame.Rect(6, 6, width - 12, height - 12)
        pygame.draw.rect(surface, self.theme.panel_border, frame_rect, 3, border_radius=6)

        # 绘制网格线
        grid = self.config.grid_size
        line_color = self.theme.grid_line
        line_width = 2

        # 垂直线
        # 两条边线（col 0 和 col 8）贯穿整个棋盘
        for col in [0, 8]:
            x = self.config.board_margin + col * grid
            start_y = self.config.board_margin
            end_y = self.config.board_margin + 9 * grid
            pygame.draw.line(surface, line_color, (x, start_y), (x, end_y), line_width)

        # 内侧7条竖线在楚河汉界处断开（row 4 和 row 5 之间）
        for col in range(1, 8):
            x = self.config.board_margin + col * grid
            # 上半部分：row 0 到 row 4
            start_y_top = self.config.board_margin
            end_y_top = self.config.board_margin + 4 * grid
            pygame.draw.line(surface, line_color, (x, start_y_top), (x, end_y_top), line_width)
            # 下半部分：row 5 到 row 9
            start_y_bottom = self.config.board_margin + 5 * grid
            end_y_bottom = self.config.board_margin + 9 * grid
            pygame.draw.line(surface, line_color, (x, start_y_bottom), (x, end_y_bottom), line_width)

        # 水平线（全部10条，不跳过任何行）
        for row in range(10):
            y = self.config.board_margin + row * grid
            start_x = self.config.board_margin
            end_x = self.config.board_margin + 8 * grid
            pygame.draw.line(surface, line_color, (start_x, y), (end_x, y), line_width)

        # 绘制九宫格斜线（红方底部）
        x3 = self.config.board_margin + 3 * grid
        x5 = self.config.board_margin + 5 * grid
        y7 = self.config.board_margin + 7 * grid
        y9 = self.config.board_margin + 9 * grid
        pygame.draw.line(surface, line_color, (x5, y7), (x3, y9), line_width)
        pygame.draw.line(surface, line_color, (x3, y7), (x5, y9), line_width)

        # 绘制九宫格斜线（黑方顶部）
        y0 = self.config.board_margin
        y2 = self.config.board_margin + 2 * grid
        pygame.draw.line(surface, line_color, (x5, y0), (x3, y2), line_width)
        pygame.draw.line(surface, line_color, (x3, y0), (x5, y2), line_width)

        # 绘制楚河汉界
        river_rect = pygame.Rect(
            self.config.board_margin + 2,
            self.config.board_margin + 4 * grid + 4,
            8 * grid - 4,
            grid - 8,
        )
        pygame.draw.rect(surface, (*self.theme.panel_bg, 80), river_rect, border_radius=4)
        self._render_river_text(surface)

        # 绘制炮和兵的位置标记
        self._render_position_markers(surface)

        self._board_surface = surface
        return surface

    def _render_river_text(self, surface: pygame.Surface) -> None:
        """绘制楚河汉界文字"""
        font = self.font
        grid = self.config.grid_size
        margin = self.config.board_margin

        # 楚河汉界在第4行和第5行之间（从0开始）
        river_y = margin + 4 * grid + grid // 2 - font.get_height() // 2

        # 分别渲染每个字
        chu_char = font.render("楚", True, self.theme.river_text)
        he_char = font.render("河", True, self.theme.river_text)
        han_char = font.render("汉", True, self.theme.river_text)
        jie_char = font.render("界", True, self.theme.river_text)

        # 棋盘宽度：8个格子（从 col 0 到 col 8）
        8 * grid

        # 楚河放在左半边（col 0-3 区域的中心）
        chu_he_width = chu_char.get_width() + 5 + he_char.get_width()
        left_center = margin + 2 * grid  # 左半边中心（col 2）
        chu_x = left_center - chu_he_width // 2
        he_x = chu_x + chu_char.get_width() + 5

        # 汉界放在右半边（col 5-8 区域的中心）
        han_jie_width = han_char.get_width() + 5 + jie_char.get_width()
        right_center = margin + 6 * grid  # 右半边中心（col 6）
        han_x = right_center - han_jie_width // 2
        jie_x = han_x + han_char.get_width() + 5

        surface.blit(chu_char, (chu_x, river_y))
        surface.blit(he_char, (he_x, river_y))
        surface.blit(han_char, (han_x, river_y))
        surface.blit(jie_char, (jie_x, river_y))

    def _render_position_markers(self, surface: pygame.Surface) -> None:
        """绘制炮和兵的位置标记（小圆点标记在交叉点上）"""
        grid = self.config.grid_size
        margin = self.config.board_margin
        line_color = self.theme.grid_line

        # 炮的位置标记 - 对应 INITIAL_BOARD 中的实际位置
        # 黑炮在 row 2 (col 1 和 col 7)，红炮在 row 7 (col 1 和 col 7)
        cannon_positions = [
            (2, 1),
            (2, 7),  # 黑方炮 (第3行)
            (7, 1),
            (7, 7),  # 红方炮 (第8行)
        ]

        marker_size = 4
        for row, col in cannon_positions:
            x = margin + col * grid
            y = margin + row * grid
            pygame.draw.circle(surface, line_color, (x, y), marker_size, 1)

        # 兵的位置标记 - 对应 INITIAL_BOARD 中的实际位置
        # 黑卒在 row 3 (col 0, 2, 4, 6, 8)，红兵在 row 6 (col 0, 2, 4, 6, 8)
        soldier_positions = [
            (3, 0),
            (3, 2),
            (3, 4),
            (3, 6),
            (3, 8),  # 黑方卒
            (6, 0),
            (6, 2),
            (6, 4),
            (6, 6),
            (6, 8),  # 红方兵
        ]

        for row, col in soldier_positions:
            x = margin + col * grid
            y = margin + row * grid
            pygame.draw.circle(surface, line_color, (x, y), marker_size, 1)

    def render_pieces(self, surface: pygame.Surface, grid: Sequence[Sequence[str | None]]) -> None:
        """
        渲染棋子

        Args:
            surface: 目标 Surface
            grid: 棋盘状态（10×9）
        """
        for row in range(10):
            for col in range(9):
                piece = grid[row][col]
                if piece:
                    self._render_single_piece(surface, row, col, piece)

    def _render_single_piece(
        self,
        surface: pygame.Surface,
        row: int,
        col: int,
        piece: str,
    ) -> None:
        """渲染单个棋子"""
        screen_x, screen_y = self.board_to_screen(row, col)
        radius = self.config.piece_radius

        color = get_piece_color(piece)
        if color == "red":
            fg = self.theme.piece_red_fg
            bg = self.theme.piece_red_bg
        elif color == "black":
            fg = self.theme.piece_black_fg
            bg = self.theme.piece_black_bg
        else:
            return

        # 绘制带阴影的棋子圆形
        shadow_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (*self.theme.piece_shadow, 82), (radius + 6, radius + 7), radius)
        surface.blit(shadow_surface, (screen_x - radius - 5, screen_y - radius - 5))
        pygame.draw.circle(surface, fg, (screen_x, screen_y), radius)
        pygame.draw.circle(surface, bg, (screen_x, screen_y), radius - 3)
        pygame.draw.circle(surface, fg, (screen_x, screen_y), radius - 7, 1)

        # 绘制棋子文字
        name = get_piece_name(piece)
        text = self.font.render(name, True, fg)
        text_rect = text.get_rect(center=(screen_x, screen_y))
        surface.blit(text, text_rect)

    def render_highlight(
        self,
        surface: pygame.Surface,
        position: tuple[int, int] | None,
        color: tuple[int, int, int] | str,
        highlight_type: Literal["selected", "legal", "capture", "last_move", "check"] = "selected",
    ) -> None:
        """
        渲染高亮

        Args:
            surface: 目标 Surface
            position: (row, col) 或 None
            color: 颜色或高亮类型字符串
            highlight_type: 高亮类型
        """
        if position is None:
            return

        screen_x, screen_y = self.board_to_screen(*position)
        radius = self.config.piece_radius

        if highlight_type == "selected":
            pygame.draw.circle(surface, color, (screen_x, screen_y), radius + 5, 4)
            pygame.draw.circle(surface, self.theme.accent, (screen_x, screen_y), radius + 9, 2)

        elif highlight_type == "legal":
            pygame.draw.circle(surface, color, (screen_x, screen_y), 8, 0)
            pygame.draw.circle(surface, self.theme.panel_bg, (screen_x, screen_y), 3, 0)

        elif highlight_type == "capture":
            pygame.draw.circle(surface, self.theme.highlight_capture, (screen_x, screen_y), radius + 3, 3)
            pygame.draw.circle(surface, self.theme.highlight_selected, (screen_x, screen_y), radius + 8, 2)

        elif highlight_type == "last_move":
            # 上一步标记蓝色圆点
            pygame.draw.circle(surface, self.theme.highlight_last_move, (screen_x, screen_y), radius + 2, 2)

        elif highlight_type == "check":
            # 将军警告红色闪烁（实际由上层控制透明度）
            alpha = 128
            check_surface = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(
                check_surface, (*self.theme.highlight_check, alpha), (radius + 3, radius + 3), radius + 3
            )
            surface.blit(check_surface, (screen_x - radius - 3, screen_y - radius - 3))

    def render_legal_moves(
        self,
        surface: pygame.Surface,
        legal_moves: list[tuple[int, int]],
        occupied_positions: set[tuple[int, int]],
    ) -> None:
        """
        渲染合法走位列表

        Args:
            surface: 目标 Surface
            legal_moves: 合法目标位置列表
            occupied_positions: 已占用位置集合
        """
        for pos in legal_moves:
            if pos in occupied_positions:
                # 吃子提示（红色边框）
                self.render_highlight(surface, pos, self.theme.highlight_capture, "capture")
            else:
                # 空位走位（绿色圆点）
                self.render_highlight(surface, pos, self.theme.highlight_legal, "legal")

    def render_status_bar(
        self,
        surface: pygame.Surface,
        current_turn: str,
        message: str = "",
        ai_thinking: bool = False,
    ) -> None:
        """
        渲染状态栏

        Args:
            surface: 目标 Surface
            current_turn: 当前回合 (red/black)
            message: 提示消息
            ai_thinking: AI 是否正在思考
        """
        bar_height = 46
        bar_y = self.config.board_margin * 2 + 9 * self.config.grid_size + 10

        board_width = self.config.board_margin * 2 + 8 * self.config.grid_size
        bar_rect = pygame.Rect(12, bar_y, board_width - 24, bar_height)
        pygame.draw.rect(surface, self.theme.status_bar_bg, bar_rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, bar_rect, 1, border_radius=8)

        # 回合信息
        turn_text = "红方回合" if current_turn == "red" else "黑方回合"
        turn_color = self.theme.piece_red_fg if current_turn == "red" else self.theme.piece_black_fg
        pygame.draw.circle(surface, turn_color, (bar_rect.left + 24, bar_rect.centery), 8)
        turn_surface = self.font.render(turn_text, True, turn_color)
        surface.blit(turn_surface, (bar_rect.left + 40, bar_y + 10))

        # AI 思考中
        if ai_thinking:
            thinking_text = "AI 思考中..."
            thinking_surface = self.font.render(thinking_text, True, self.theme.accent)
            thinking_rect = thinking_surface.get_rect(center=(bar_rect.centerx, bar_rect.centery))
            surface.blit(thinking_surface, thinking_rect)

        # 消息
        if message:
            msg_surface = self.font.render(
                message, True, self.theme.error_color if "非法" in message else self.theme.font_color
            )
            msg_rect = msg_surface.get_rect(right=bar_rect.right - 16, centery=bar_rect.centery)
            surface.blit(msg_surface, msg_rect)

    def render_difficulty_selection(self, surface: pygame.Surface, current: Difficulty) -> None:
        """
        渲染难度选择界面

        Args:
            surface: 目标 Surface
            current: 当前选中的难度
        """
        surface.fill(self.theme.app_bg)
        board_surface = self.render_board_background()
        board_x = (self.config.window_width - board_surface.get_width()) // 2
        board_y = 20
        surface.blit(board_surface, (board_x, board_y))

        scrim = pygame.Surface((board_surface.get_width(), board_surface.get_height()), pygame.SRCALPHA)
        scrim.fill((0, 0, 0, 96))
        surface.blit(scrim, (board_x, board_y))

        title_text = self.font.render("选择 AI 难度", True, self.theme.inverse_text)
        title_rect = title_text.get_rect(centerx=self.config.window_width // 2, centery=78)
        surface.blit(title_text, title_rect)

        difficulties = [
            (Difficulty.EASY, "简单", "更随机", (44, 150, 96)),
            (Difficulty.MEDIUM, "中等", "攻守平衡", (48, 112, 186)),
            (Difficulty.HARD, "困难", "更稳健", (199, 54, 61)),
        ]

        by_diff = {diff: (label, hint, color) for diff, label, hint, color in difficulties}
        for diff, btn_rect in difficulty_button_rects(self.config):
            label, hint, color = by_diff[diff]
            is_selected = diff == current

            bg_color = self.theme.panel_bg if is_selected else self.theme.status_bar_bg
            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=8)
            pygame.draw.rect(surface, color, btn_rect, 3 if is_selected else 1, border_radius=8)

            label_color = self.theme.font_color
            label_surface = self.font.render(label, True, label_color)
            label_rect = label_surface.get_rect(center=(btn_rect.centerx, btn_rect.centery - 8))
            surface.blit(label_surface, label_rect)

            hint_surface = self.font.render(hint, True, self.theme.muted_text)
            hint_rect = hint_surface.get_rect(center=(btn_rect.centerx, btn_rect.centery + 14))
            surface.blit(hint_surface, hint_rect)

        hint_text = self.font.render("点击难度后开局。红方先行。", True, self.theme.inverse_text)
        hint_rect = hint_text.get_rect(centerx=self.config.window_width // 2, centery=620)
        surface.blit(hint_text, hint_rect)

        temp_texts = {
            Difficulty.EASY: "温度 0.8 - 随机灵活",
            Difficulty.MEDIUM: "温度 0.3 - 平衡稳定",
            Difficulty.HARD: "温度 0.1 - 精准严谨",
        }
        temp_text = self.font.render(temp_texts.get(current, ""), True, self.theme.highlight_selected)
        temp_rect = temp_text.get_rect(centerx=self.config.window_width // 2, centery=654)
        surface.blit(temp_text, temp_rect)

    def render_toolbar(self, surface: pygame.Surface, controller: ControllerRenderState) -> None:
        """
        渲染工具栏 - 底部按钮栏

        Args:
            surface: 目标 Surface
            controller: GameController 实例用于检查状态
        """
        toolbar_height = 50
        toolbar_y = self.config.window_height - toolbar_height
        toolbar_rect = pygame.Rect(0, toolbar_y, self.config.window_width, toolbar_height)

        pygame.draw.rect(surface, self.theme.app_bg, toolbar_rect)
        pygame.draw.line(surface, self.theme.panel_border, (0, toolbar_y), (self.config.window_width, toolbar_y), 1)

        # 按钮配置
        button_size = 40
        button_margin = 10
        start_x = button_margin
        button_y = toolbar_y + (toolbar_height - button_size) // 2

        buttons = [
            # (icon_name, tooltip, enabled_check, click_handler_attr)
            ("new_game.svg", "新游戏", lambda c: True, "reset_game"),
            ("undo.svg", "撤销 (Ctrl+Z)", lambda c: c.can_undo, "undo"),
            ("redo.svg", "重做 (Ctrl+Y)", lambda c: c.can_redo, "redo"),
            ("list.svg", "棋谱", lambda c: True, "show_game_list"),
            ("settings.svg", "设置", lambda c: True, None),
            ("sound.svg", "音效", lambda c: True, None),
            ("exit.svg", "退出", lambda c: True, None),
        ]

        # 加载并渲染图标
        for i, (icon_name, tooltip, enabled_check, click_handler) in enumerate(buttons):
            x = start_x + i * (button_size + button_margin)

            # 检查按钮是否可用
            is_enabled = enabled_check(controller)

            # 按钮背景
            btn_rect = pygame.Rect(x, button_y, button_size, button_size)
            bg_color = self.theme.button_bg if is_enabled else self.theme.button_disabled
            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=8)
            pygame.draw.rect(surface, self.theme.panel_border, btn_rect, 1, border_radius=8)

            # 加载图标
            try:
                icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icons" / icon_name
                if icon_path.exists():
                    icon_surface = pygame.image.load(str(icon_path))
                    # 调整图标大小
                    icon_surface = pygame.transform.scale(icon_surface, (button_size - 8, button_size - 8))
                    icon_rect = icon_surface.get_rect(center=btn_rect.center)
                    surface.blit(icon_surface, icon_rect)
                else:
                    # 如果图标不存在，绘制占位符
                    placeholder_font = self.font
                    placeholder_text = placeholder_font.render("?", True, self.theme.font_color)
                    placeholder_rect = placeholder_text.get_rect(center=btn_rect.center)
                    surface.blit(placeholder_text, placeholder_rect)
            except Exception as e:
                logger.warning(f"加载图标失败 {icon_name}: {e}")
                # 绘制占位符
                placeholder_font = self.font
                placeholder_text = placeholder_font.render("?", True, self.theme.font_color)
                placeholder_rect = placeholder_text.get_rect(center=btn_rect.center)
                surface.blit(placeholder_text, placeholder_rect)

            # 显示工具提示（简化版：在按钮下方显示文字）
            if is_enabled:
                tooltip_surface = pygame.font.Font(None, 16).render(tooltip, True, self.theme.inverse_text)
                tooltip_rect = tooltip_surface.get_rect(centerx=btn_rect.centerx, bottom=btn_rect.top - 2)
                surface.blit(tooltip_surface, tooltip_rect)

    def render_settings_dialog(
        self,
        surface: pygame.Surface,
        controller: ControllerRenderState,
    ) -> None:
        """
        渲染设置对话框

        Args:
            surface: 目标 Surface
            controller: GameController 实例
        """
        overlay = pygame.Surface((self.config.window_width, self.config.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        dialog_width = 350
        dialog_height = 300
        dialog_x = (self.config.window_width - dialog_width) // 2
        dialog_y = (self.config.window_height - dialog_height) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        shadow_rect = dialog_rect.move(0, 8)
        shadow = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 88), shadow.get_rect(), border_radius=8)
        surface.blit(shadow, shadow_rect)
        pygame.draw.rect(surface, self.theme.panel_bg, dialog_rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, dialog_rect, 2, border_radius=8)

        # 标题
        title_text = self.font.render("游戏设置", True, self.theme.panel_border)
        title_rect = title_text.get_rect(centerx=self.config.window_width // 2, top=dialog_y + 15)
        surface.blit(title_text, title_rect)

        option_y = dialog_y + 60
        option_spacing = 50

        # 1. 音效开关
        sound_label = self.font.render("音效", True, self.theme.font_color)
        surface.blit(sound_label, (dialog_x + 30, option_y))
        sound_button_x = dialog_x + dialog_width - 80
        sound_rect = pygame.Rect(sound_button_x, option_y, 40, 30)
        sound_on = controller.config.sound_enabled
        sound_bg = self.theme.accent if sound_on else self.theme.error_color
        pygame.draw.rect(surface, sound_bg, sound_rect, border_radius=8)
        sound_text = self.font.render("开" if sound_on else "关", True, (255, 255, 255))
        sound_text_rect = sound_text.get_rect(center=sound_rect.center)
        surface.blit(sound_text, sound_text_rect)

        # 2. 动画开关
        anim_y = option_y + option_spacing
        anim_label = self.font.render("走子动画", True, self.theme.font_color)
        surface.blit(anim_label, (dialog_x + 30, anim_y))
        anim_rect = pygame.Rect(sound_button_x, anim_y, 40, 30)
        anim_on = controller.config.animation_enabled
        anim_bg = self.theme.accent if anim_on else self.theme.error_color
        pygame.draw.rect(surface, anim_bg, anim_rect, border_radius=8)
        anim_text = self.font.render("开" if anim_on else "关", True, (255, 255, 255))
        anim_text_rect = anim_text.get_rect(center=anim_rect.center)
        surface.blit(anim_text, anim_text_rect)

        # 3. 主题选择
        theme_y = anim_y + option_spacing
        theme_label = self.font.render("主题", True, self.theme.font_color)
        surface.blit(theme_label, (dialog_x + 30, theme_y))

        themes = ["classic", "modern", "dark"]
        theme_names = {"classic": "经典", "modern": "现代", "dark": "暗黑"}
        # 获取控制器当前主题
        current_theme = getattr(controller, "_current_theme", "classic") or "classic"
        if current_theme not in themes:
            current_theme = "classic"

        theme_btn_width = 60
        theme_btn_spacing = 10
        theme_start_x = dialog_x + dialog_width - 3 * theme_btn_width - 2 * theme_btn_spacing - 20

        for i, theme_key in enumerate(themes):
            x = theme_start_x + i * (theme_btn_width + theme_btn_spacing)
            theme_rect = pygame.Rect(x, theme_y, theme_btn_width, 30)
            is_selected = current_theme == theme_key
            theme_bg = self.theme.accent if is_selected else self.theme.button_bg
            pygame.draw.rect(surface, theme_bg, theme_rect, border_radius=6)
            pygame.draw.rect(surface, self.theme.panel_border, theme_rect, 1, border_radius=6)
            theme_text_color = self.theme.inverse_text if is_selected else self.theme.font_color
            theme_text_s = self.font.render(theme_names[theme_key], True, theme_text_color)
            theme_text_rect = theme_text_s.get_rect(center=theme_rect.center)
            surface.blit(theme_text_s, theme_text_rect)

        # 4. 关闭按钮
        close_y = dialog_y + dialog_height - 50
        close_width = 100
        close_height = 36
        close_x = (self.config.window_width - close_width) // 2
        close_rect = pygame.Rect(close_x, close_y, close_width, close_height)
        pygame.draw.rect(surface, self.theme.button_bg, close_rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, close_rect, 1, border_radius=8)
        close_text = self.font.render("关闭", True, self.theme.font_color)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        surface.blit(close_text, close_text_rect)

    def render_game_over_dialog(
        self,
        surface: pygame.Surface,
        result: str,
    ) -> None:
        overlay = pygame.Surface((self.config.window_width, self.config.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        dialog_width = 300
        dialog_height = 150
        dialog_x = (self.config.window_width - dialog_width) // 2
        dialog_y = (self.config.window_height - dialog_height) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(surface, self.theme.panel_bg, dialog_rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, dialog_rect, 2, border_radius=8)

        result_map = {
            "red_checkmate": "红方获胜！",
            "black_checkmate": "黑方获胜！",
            "threefold_repetition": "和棋（三次重复）",
            "perpetual_check": "和棋（长将）",
        }
        result_text = result_map.get(result, result)

        text = self.font.render(result_text, True, self.theme.panel_border)
        text_rect = text.get_rect(center=(self.config.window_width // 2, dialog_y + 50))
        surface.blit(text, text_rect)

        button_width = 120
        button_height = 36
        button_x = (self.config.window_width - button_width) // 2
        button_y = dialog_y + 90

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, self.theme.button_bg, button_rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, button_rect, 1, border_radius=8)

        button_text = self.font.render("重新开始", True, self.theme.font_color)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        surface.blit(button_text, button_text_rect)

    def render_replay_controls(
        self,
        surface: pygame.Surface,
        current_step: int,
        total_steps: int,
    ) -> None:
        """
        渲染复盘控制按钮

        Args:
            surface: 目标 Surface
            current_step: 当前步数
            total_steps: 总步数
        """
        # 半透明背景
        overlay = pygame.Surface((self.config.window_width, self.config.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        # 返回按钮
        back_btn = pygame.Rect(10, 10, 60, 30)
        pygame.draw.rect(surface, self.theme.button_bg, back_btn, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, back_btn, 1, border_radius=8)
        back_text = self.font.render("返回", True, self.theme.font_color)
        back_rect = back_text.get_rect(center=back_btn.center)
        surface.blit(back_text, back_rect)

        # 标题
        title = self.font.render(f"复盘 ({current_step}/{total_steps})", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.config.window_width // 2, 25))
        surface.blit(title, title_rect)

        # 上一步按钮
        prev_btn = pygame.Rect(50, self.config.window_height - 120, 80, 40)
        prev_disabled = current_step == 0
        prev_bg = self.theme.button_disabled if prev_disabled else self.theme.button_bg
        pygame.draw.rect(surface, prev_bg, prev_btn, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, prev_btn, 1, border_radius=8)
        prev_text = self.font.render(
            "上一步", True, self.theme.font_color if not prev_disabled else self.theme.muted_text
        )
        prev_rect = prev_text.get_rect(center=prev_btn.center)
        surface.blit(prev_text, prev_rect)

        # 下一步按钮
        next_btn = pygame.Rect(150, self.config.window_height - 120, 80, 40)
        next_disabled = current_step >= total_steps
        next_bg = self.theme.button_disabled if next_disabled else self.theme.button_bg
        pygame.draw.rect(surface, next_bg, next_btn, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, next_btn, 1, border_radius=8)
        next_text = self.font.render(
            "下一步", True, self.theme.font_color if not next_disabled else self.theme.muted_text
        )
        next_rect = next_text.get_rect(center=next_btn.center)
        surface.blit(next_text, next_rect)

        # 进度条
        bar_x = 250
        bar_y = self.config.window_height - 100
        bar_width = self.config.window_width - bar_x - 50
        bar_height = 20

        pygame.draw.rect(surface, self.theme.status_bar_bg, (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        if total_steps > 0:
            progress = current_step / total_steps
            filled_width = int(bar_width * progress)
            if filled_width > 0:
                pygame.draw.rect(surface, self.theme.accent, (bar_x, bar_y, filled_width, bar_height), border_radius=8)

    def render_game_list(
        self,
        surface: pygame.Surface,
        games: list,
    ) -> None:
        """
        渲染棋谱列表

        Args:
            surface: 目标 Surface
            games: 对局记录列表
        """
        # 背景
        overlay = pygame.Surface((self.config.window_width, self.config.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # 标题
        title = self.font.render("棋谱列表", True, self.theme.inverse_text)
        title_rect = title.get_rect(center=(self.config.window_width // 2, 30))
        surface.blit(title, title_rect)

        # 返回按钮
        back_btn = pygame.Rect(10, 10, 60, 30)
        pygame.draw.rect(surface, self.theme.button_bg, back_btn, border_radius=8)
        pygame.draw.rect(surface, self.theme.panel_border, back_btn, 1, border_radius=8)
        back_text = self.font.render("返回", True, self.theme.font_color)
        back_rect = back_text.get_rect(center=back_btn.center)
        surface.blit(back_text, back_rect)

        # 对局列表
        list_start_y = 60
        item_height = 60
        list_start_x = 50
        list_width = self.config.window_width - 100

        if not games:
            no_games_text = self.font.render("暂无棋谱记录", True, self.theme.muted_text)
            no_games_rect = no_games_text.get_rect(center=(self.config.window_width // 2, list_start_y + 100))
            surface.blit(no_games_text, no_games_rect)
            return

        for i, game in enumerate(games):
            y = list_start_y + i * item_height

            # 列表项背景
            item_rect = pygame.Rect(list_start_x, y, list_width, item_height - 5)
            pygame.draw.rect(surface, self.theme.panel_bg, item_rect, border_radius=8)
            pygame.draw.rect(surface, self.theme.panel_border, item_rect, 1, border_radius=8)

            # 日期
            date_str = (
                game.start_time.strftime("%Y-%m-%d %H:%M")
                if hasattr(game.start_time, "strftime")
                else str(game.start_time)
            )
            date_text = self.font.render(date_str, True, self.theme.font_color)
            surface.blit(date_text, (list_start_x + 10, y + 5))

            # 结果
            result_map = {"ongoing": "进行中", "red_win": "红胜", "black_win": "黑胜", "draw": "和棋"}
            result_str = result_map.get(game.result, game.result)
            result_color = (
                (255, 100, 100)
                if game.result == "red_win"
                else (100, 100, 100)
                if game.result == "black_win"
                else self.theme.muted_text
            )
            result_text = self.font.render(result_str, True, result_color)
            surface.blit(result_text, (list_start_x + 10, y + 25))

            # 步数
            moves_text = self.font.render(f"{game.total_moves} 步", True, self.theme.muted_text)
            surface.blit(moves_text, (list_start_x + 150, y + 25))

            # 玩家方
            side_str = "红方" if game.player_side == "red" else "黑方"
            side_text = self.font.render(f"执{side_str}", True, self.theme.muted_text)
            surface.blit(side_text, (list_start_x + 250, y + 25))

            # 箭头指示
            arrow = self.font.render("→", True, self.theme.accent)
            arrow_rect = arrow.get_rect(right=item_rect.right - 10, centery=y + item_height // 2)
            surface.blit(arrow, arrow_rect)

    def clear(self, surface: pygame.Surface, color: tuple[int, int, int] | None = None) -> None:
        fill_color = color or self.theme.app_bg
        surface.fill(fill_color)
