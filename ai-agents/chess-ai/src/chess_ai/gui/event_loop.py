"""
Pygame 主循环 - 事件循环入口
"""

from __future__ import annotations

import logging

import pygame

from .config import GUIConfig
from .controller import GameController, GameState
from .renderer import ChessRenderer

logger = logging.getLogger(__name__)


class EventLoop:
    """
    Pygame 主循环 - 统一调度事件分发、帧率控制、界面刷新
    """

    def __init__(
        self,
        config: GUIConfig,
        controller: GameController,
        renderer: ChessRenderer,
    ):
        self.config = config
        self.controller = controller
        self.renderer = renderer

        self._running: bool = False
        self._clock: pygame.time.Clock | None = None
        self._screen: pygame.Surface | None = None

    def initialize(self) -> bool:
        """
        初始化 Pygame 和窗口

        Returns:
            是否初始化成功
        """
        self.renderer.init_pygame()
        self._clock = pygame.time.Clock()

        # 设置窗口
        self._screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption(self.config.window_title)

        # 初始化控制器
        self.controller.set_surface(self._screen)

        logger.info("Pygame 初始化完成")
        return True

    def run(self, initial_state: GameState = GameState.STARTUP) -> None:
        """
        启动主循环

        Args:
            initial_state: 初始游戏状态
        """
        if not self.initialize():
            logger.error("Pygame 初始化失败")
            return

        if initial_state != GameState.STARTUP:
            self.controller.state = initial_state
        if self.controller.state != GameState.SELECTING_DIFFICULTY:
            self.controller.start_game()
        self._running = True

        while self._running:
            # 1. 处理事件
            self._process_events()

            # 2. 更新逻辑
            self.controller.update()

            # 3. 渲染
            self._render_frame()

            # 4. 帧率控制
            if self._clock is not None:
                self._clock.tick(self.config.fps)

        self._cleanup()

    def _process_events(self) -> None:
        """处理事件队列"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    self.controller.handle_click(*event.pos)

            elif event.type == pygame.KEYDOWN:
                self.controller.handle_key(event.key)
                if event.key == pygame.K_q and (
                    pygame.key.get_mods() & pygame.KMOD_CTRL or pygame.key.get_mods() & pygame.KMOD_ALT
                ):
                    self._running = False

            elif event.type == pygame.WINDOWCLOSE:
                self._running = False

    def _render_frame(self) -> None:
        """渲染当前帧"""
        if self._screen is None:
            return

        self.controller.render(self._screen)
        pygame.display.flip()

    def _cleanup(self) -> None:
        """清理资源"""
        pygame.quit()
        logger.info("Pygame 已退出")

    def stop(self) -> None:
        """停止主循环"""
        self._running = False
