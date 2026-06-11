"""
主题配置 - 颜色和视觉风格定义
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal


@dataclass
class ColorTheme:
    """颜色主题"""

    app_bg: tuple[int, int, int] = (31, 38, 41)
    panel_bg: tuple[int, int, int] = (246, 238, 220)
    panel_border: tuple[int, int, int] = (113, 77, 42)
    board_bg: tuple[int, int, int] = (229, 190, 122)
    board_bg_alt: tuple[int, int, int] = (240, 210, 150)
    grid_line: tuple[int, int, int] = (105, 61, 31)
    river_text: tuple[int, int, int] = (126, 89, 52)
    accent: tuple[int, int, int] = (20, 111, 96)
    highlight_selected: tuple[int, int, int] = (247, 196, 64)
    highlight_legal: tuple[int, int, int] = (35, 150, 100)
    highlight_capture: tuple[int, int, int] = (199, 54, 61)
    highlight_last_move: tuple[int, int, int] = (48, 112, 186)
    highlight_check: tuple[int, int, int] = (225, 69, 70)
    piece_red_fg: tuple[int, int, int] = (178, 35, 42)
    piece_red_bg: tuple[int, int, int] = (255, 246, 229)
    piece_black_fg: tuple[int, int, int] = (34, 38, 39)
    piece_black_bg: tuple[int, int, int] = (239, 242, 236)
    piece_shadow: tuple[int, int, int] = (67, 44, 27)
    status_bar_bg: tuple[int, int, int] = (247, 243, 232)
    status_bar_text: tuple[int, int, int] = (49, 54, 51)
    overlay_bg: tuple[int, int, int, int] = (0, 0, 0, 128)  # 半透明黑色
    button_bg: tuple[int, int, int] = (237, 226, 202)
    button_hover: tuple[int, int, int] = (218, 201, 168)
    button_disabled: tuple[int, int, int] = (101, 100, 92)
    font_color: tuple[int, int, int] = (49, 54, 51)
    muted_text: tuple[int, int, int] = (107, 112, 105)
    inverse_text: tuple[int, int, int] = (250, 247, 238)
    error_color: tuple[int, int, int] = (199, 54, 61)


@dataclass
class PieceTheme:
    """棋子主题"""

    font_name: str = "SimHei"
    font_size: int = 20
    border_width: int = 2
    red_name: str = "帅"  # 实际根据棋子类型显示
    black_name: str = "将"


class ThemeManager:
    """主题管理器"""

    _themes: ClassVar[dict[str, ColorTheme]] = {
        "classic": ColorTheme(),
        "default": ColorTheme(),
        "modern": ColorTheme(
            app_bg=(24, 43, 46),
            panel_bg=(233, 239, 230),
            panel_border=(50, 95, 92),
            board_bg=(214, 224, 204),
            board_bg_alt=(229, 235, 216),
            grid_line=(53, 96, 88),
            river_text=(71, 117, 107),
            accent=(44, 129, 117),
            highlight_selected=(244, 181, 73),
            highlight_legal=(35, 148, 105),
            highlight_capture=(199, 62, 72),
            highlight_last_move=(45, 106, 189),
            highlight_check=(224, 77, 80),
            piece_red_fg=(183, 43, 51),
            piece_red_bg=(255, 248, 232),
            piece_black_fg=(24, 41, 43),
            piece_black_bg=(244, 247, 239),
            piece_shadow=(28, 45, 47),
            status_bar_bg=(232, 238, 227),
            status_bar_text=(32, 47, 47),
            button_bg=(214, 226, 213),
            button_hover=(196, 216, 204),
            button_disabled=(93, 108, 106),
            font_color=(32, 47, 47),
            muted_text=(84, 105, 101),
            error_color=(199, 62, 72),
        ),
        "dark": ColorTheme(
            app_bg=(18, 22, 24),
            panel_bg=(39, 43, 44),
            panel_border=(168, 135, 78),
            board_bg=(92, 76, 55),
            board_bg_alt=(106, 88, 63),
            grid_line=(215, 176, 105),
            river_text=(226, 194, 130),
            accent=(44, 144, 127),
            highlight_selected=(250, 199, 82),
            highlight_legal=(66, 184, 129),
            highlight_capture=(232, 85, 88),
            highlight_last_move=(95, 157, 225),
            highlight_check=(236, 79, 83),
            piece_red_fg=(244, 96, 97),
            piece_red_bg=(51, 34, 35),
            piece_black_fg=(230, 232, 224),
            piece_black_bg=(35, 39, 40),
            piece_shadow=(8, 10, 11),
            status_bar_bg=(34, 38, 39),
            status_bar_text=(242, 236, 222),
            button_bg=(62, 63, 59),
            button_hover=(83, 82, 75),
            button_disabled=(45, 47, 47),
            font_color=(242, 236, 222),
            muted_text=(174, 168, 153),
            inverse_text=(248, 241, 225),
            error_color=(244, 96, 97),
        ),
    }
    _current_theme: ClassVar[str] = "classic"

    @classmethod
    def get_theme(cls, name: str | None = None) -> ColorTheme:
        """获取主题"""
        theme_name = name or cls._current_theme
        return cls._themes.get(theme_name, cls._themes["default"])

    @classmethod
    def set_theme(cls, name: str) -> None:
        """设置当前主题"""
        if name in cls._themes:
            cls._current_theme = name

    @classmethod
    def register_theme(cls, name: str, theme: ColorTheme) -> None:
        """注册新主题"""
        cls._themes[name] = theme


# 静态工具函数
def get_piece_color(piece: str | None) -> Literal["red", "black", None]:
    """获取棋子颜色"""
    if piece is None:
        return None
    if piece.isupper():
        return "red"
    if piece.islower():
        return "black"
    return None


def get_piece_name(piece: str) -> str:
    """获取棋子显示名称"""
    piece_map = {
        "K": "帅",
        "k": "将",
        "R": "车",
        "r": "车",
        "N": "马",
        "n": "马",
        "B": "相",
        "b": "象",
        "A": "仕",
        "a": "士",
        "C": "炮",
        "c": "炮",
        "P": "兵",
        "p": "卒",
    }
    return piece_map.get(piece, "?")


def ucci_to_rowcol(ucci: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    UCCI 坐标转行列

    UCCI: 列(a-i) + 行(0-9) + 列(a-i) + 行(0-9)
    行列: row(0-9), col(0-8)，row=0 是黑方底线
    """
    from_col = ord(ucci[0]) - ord("a")
    from_row = int(ucci[1])
    to_col = ord(ucci[2]) - ord("a")
    to_row = int(ucci[3])

    return (from_row, from_col), (to_row, to_col)


def rowcol_to_ucci(row: int, col: int) -> str:
    """行列转 UCCI"""
    col_letter = chr(ord("a") + col)
    return f"{col_letter}{row}"
