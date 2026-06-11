"""
GUI 配置 - Pygame 窗口和棋盘相关配置
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GUIConfig:
    """GUI 配置数据类"""

    window_width: int = 800
    window_height: int = 750
    board_width: int = 540
    board_height: int = 600
    board_margin: int = 30
    grid_size: int = 60
    piece_radius: int = 26
    window_title: str = "中国象棋AI对弈"
    fps: int = 60
    animation_enabled: bool = True
    animation_duration_ms: int = 200
    sound_enabled: bool = True
    show_hints: bool = True

    @classmethod
    def from_dict(cls, config: dict) -> GUIConfig:
        """从字典创建配置"""
        return cls(
            window_width=config.get("gui.window_width", 800),
            window_height=config.get("gui.window_height", 750),
            board_width=config.get("gui.board_width", 540),
            board_height=config.get("gui.board_height", 600),
            board_margin=config.get("gui.board_margin", 30),
            grid_size=config.get("gui.grid_size", 60),
            piece_radius=config.get("gui.piece_radius", 26),
            window_title=config.get("gui.window_title", "中国象棋AI对弈"),
            fps=config.get("gui.fps", 60),
            animation_enabled=config.get("gui.animation_enabled", True),
            animation_duration_ms=config.get("gui.animation_duration_ms", 200),
            sound_enabled=config.get("gui.sound_enabled", True),
            show_hints=config.get("gui.show_hints", True),
        )

    @classmethod
    def from_infra_config(cls, infra_config: object) -> GUIConfig:
        """从 infra ConfigManager 创建配置"""
        return cls(
            window_width=getattr(infra_config, "get", lambda k, d: d)("gui.window_width", 800),
            window_height=getattr(infra_config, "get", lambda k, d: d)("gui.window_height", 700),
            board_margin=getattr(infra_config, "get", lambda k, d: d)("gui.board_margin", 30),
            grid_size=getattr(infra_config, "get", lambda k, d: d)("gui.grid_size", 60),
            piece_radius=getattr(infra_config, "get", lambda k, d: d)("gui.piece_radius", 26),
            animation_enabled=getattr(infra_config, "get", lambda k, d: d)("gui.animation_enabled", True),
            sound_enabled=getattr(infra_config, "get", lambda k, d: d)("gui.sound_enabled", True),
            show_hints=getattr(infra_config, "get", lambda k, d: d)("gui.show_hints", True),
        )
