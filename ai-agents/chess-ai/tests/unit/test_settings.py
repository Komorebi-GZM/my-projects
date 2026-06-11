"""
设置界面功能单元测试
"""

from unittest.mock import Mock, patch

import pygame
import pytest

from chess_ai.gui.config import GUIConfig
from chess_ai.gui.controller import GameController, GameState
from chess_ai.gui.renderer import ChessRenderer, difficulty_button_rects
from chess_ai.gui.theme import ThemeManager


class MockRenderer:
    def __init__(self, config, theme=None):
        self.config = config
        self.theme = theme
        self.rendered = {}

    def render_board_background(self):
        return Mock()

    def render_pieces(self, surface, grid):
        pass

    def render_toolbar(self, surface, controller):
        pass

    def render_settings_dialog(self, surface, controller):
        self.rendered["settings"] = True

    def render_difficulty_selection(self, surface, current):
        pass

    def render_status_bar(self, surface, turn, message, ai_thinking):
        pass

    def render_game_over_dialog(self, surface, result):
        pass

    def clear(self, surface, color=None):
        pass

    def set_theme(self, theme):
        self.theme = theme

    def screen_to_board(self, x, y):
        return (y // 60, x // 60)

    def board_to_screen(self, row, col):
        return (col * 60 + 30, row * 60 + 30)


@pytest.fixture
def controller():
    config = GUIConfig()
    renderer = MockRenderer(config)
    controller = GameController(config, renderer)
    # 设置为WAITING状态以便测试
    controller.state = GameState.WAITING
    return controller


class TestSettingsState:
    """设置界面状态测试"""

    def test_initial_state_not_settings(self, controller):
        """初始状态不是设置"""
        assert controller.state != GameState.SETTINGS

    def test_can_transition_to_settings_via_toolbar(self, controller):
        """点击设置图标可以进入设置界面"""
        # 模拟点击设置图标 (索引4: new_game, undo, redo, save, settings, sound, exit)
        controller.config.window_width = 800
        controller.config.window_height = 750
        toolbar_y = controller.config.window_height - 50
        button_size = 40
        button_margin = 10
        start_x = button_margin
        # 设置图标是第5个按钮 (索引4)
        settings_x = start_x + 4 * (button_size + button_margin)
        settings_y = toolbar_y + (50 - button_size) // 2  # toolbar_height=50

        # 点击设置图标
        controller.handle_click(settings_x + 5, settings_y + 5)  # 在图标内部点击

        assert controller.state == GameState.SETTINGS

    def test_escape_from_settings_returns_waiting(self, controller):
        """从设置界面按ESC返回等待状态"""
        controller.state = GameState.SETTINGS
        controller.handle_key(27)  # ESC键码通常是27
        assert controller.state == GameState.WAITING

    def test_toggle_settings_method(self, controller):
        """toggle_settings方法可以切换状态"""
        assert controller.state == GameState.WAITING
        controller.toggle_settings()
        assert controller.state == GameState.SETTINGS
        controller.toggle_settings()
        assert controller.state == GameState.WAITING

    def test_render_calls_settings_dialog_when_in_settings(self, controller):
        """在SETTINGS状态下渲染会调用settings dialog"""
        controller.state = GameState.SETTINGS
        surface = Mock()
        controller.renderer = MockRenderer(controller.config)
        controller.render(surface)
        assert hasattr(controller.renderer.rendered, "get")
        # 检查是否调用了render_settings_dialog
        assert "settings" in controller.renderer.rendered

    def test_theme_change_via_settings_click(self, controller):
        """点击设置界面可以切换主题"""
        controller.state = GameState.SETTINGS
        # 设置窗口尺寸
        controller.config.window_width = 800
        controller.config.window_height = 750

        dialog_width = 350
        dialog_height = 300
        dialog_x = (controller.config.window_width - dialog_width) // 2
        dialog_y = (controller.config.window_height - dialog_height) // 2

        option_y = dialog_y + 60
        option_spacing = 50
        theme_y = option_y + 2 * option_spacing  # 主题是第三个选项
        theme_btn_width = 60
        theme_btn_spacing = 10
        theme_start_x = dialog_x + dialog_width - 3 * theme_btn_width - 2 * theme_btn_spacing - 20

        # 点击第一个主题按钮 (classic)
        theme_x = theme_start_x + 0 * (theme_btn_width + theme_btn_spacing)
        theme_y_abs = theme_y
        controller.handle_click(theme_x + 5, theme_y_abs + 5)

        # 检查主题是否切换
        # 注意：我们这里假设初始主题是classic，所以点击classic应该保持不变
        # 但我们可以检查消息
        assert "主题已切换为" in controller.message or controller.message == ""

        # 点击第二个主题按钮 (modern)
        theme_x = theme_start_x + 1 * (theme_btn_width + theme_btn_spacing)
        controller.handle_click(theme_x + 5, theme_y_abs + 5)
        assert controller._current_theme == "modern"
        assert "主题已切换为: modern" in controller.message

        # 点击第三个主题按钮 (dark)
        theme_x = theme_start_x + 2 * (theme_btn_width + theme_btn_spacing)
        controller.handle_click(theme_x + 5, theme_y_abs + 5)
        assert controller._current_theme == "dark"
        assert "主题已切换为: dark" in controller.message

    def test_toggle_sound_via_settings_click(self, controller):
        """点击设置界面可以切换音效"""
        controller.state = GameState.SETTINGS
        controller.config.window_width = 800
        controller.config.window_height = 750

        dialog_width = 350
        dialog_height = 300
        dialog_x = (controller.config.window_width - dialog_width) // 2
        dialog_y = (controller.config.window_height - dialog_height) // 2

        option_y = dialog_y + 60  # 第一行是音效
        sound_button_x = dialog_x + dialog_width - 80
        sound_rect_y = option_y

        initial_sound = controller.config.sound_enabled
        # 点击音效开关
        controller.handle_click(sound_button_x + 5, sound_rect_y + 5)
        assert controller.config.sound_enabled == (not initial_sound)
        assert f"音效已{'开启' if controller.config.sound_enabled else '关闭'}" in controller.message

        # 再次点击
        controller.handle_click(sound_button_x + 5, sound_rect_y + 5)
        assert controller.config.sound_enabled == initial_sound
        assert f"音效已{'开启' if controller.config.sound_enabled else '关闭'}" in controller.message

    def test_toggle_animation_via_settings_click(self, controller):
        """点击设置界面可以切换动画"""
        controller.state = GameState.SETTINGS
        controller.config.window_width = 800
        controller.config.window_height = 750

        dialog_width = 350
        dialog_height = 300
        dialog_x = (controller.config.window_width - dialog_width) // 2
        dialog_y = (controller.config.window_height - dialog_height) // 2

        option_y = dialog_y + 60  # 第一行是音效
        option_spacing = 50
        anim_y = option_y + option_spacing  # 第二行是动画
        anim_button_x = dialog_x + dialog_width - 80
        anim_rect_y = anim_y

        initial_anim = controller.config.animation_enabled
        # 点击动画开关
        controller.handle_click(anim_button_x + 5, anim_rect_y + 5)
        assert controller.config.animation_enabled == (not initial_anim)
        assert f"动画已{'开启' if controller.config.animation_enabled else '关闭'}" in controller.message

        # 再次点击
        controller.handle_click(anim_button_x + 5, anim_rect_y + 5)
        assert controller.config.animation_enabled == initial_anim
        assert f"动画已{'开启' if controller.config.animation_enabled else '关闭'}" in controller.message


class TestSettingsIntegration:
    """设置界面集成测试"""

    def test_settings_toggle_via_toolbar(self, controller):
        """通过工具栏切换设置界面"""
        controller.config.window_width = 800
        controller.config.window_height = 750
        toolbar_y = controller.config.window_height - 50
        button_size = 40
        button_margin = 10
        start_x = button_margin

        # 设置图标位置 (第5个按钮，索引4)
        settings_x = start_x + 4 * (button_size + button_margin)
        settings_y = toolbar_y + (50 - button_size) // 2

        # 点击设置图标打开设置
        controller.handle_click(settings_x + 5, settings_y + 5)
        assert controller.state == GameState.SETTINGS

        # 再次点击设置图标关闭设置
        controller.handle_click(settings_x + 5, settings_y + 5)
        assert controller.state == GameState.WAITING

    def test_render_includes_settings_dialog(self, controller):
        """渲染时包含设置对话框"""
        controller.state = GameState.SETTINGS
        controller.config.window_width = 800
        controller.config.window_height = 750

        surface = Mock()
        # 使用真实渲染器但mock其依赖
        with patch("chess_ai.gui.controller.ChessRenderer") as mock_renderer_class:
            mock_renderer_instance = Mock()
            mock_renderer_class.return_value = mock_renderer_instance
            controller.renderer = mock_renderer_instance

            controller.render(surface)

            # 检查是否调用了render_settings_dialog
            mock_renderer_instance.render_settings_dialog.assert_called_once_with(surface, controller)


class TestGameUIFlow:
    """游戏 UI 布局和主题测试"""

    def test_difficulty_click_uses_rendered_button_rects(self, controller):
        """难度按钮绘制区域和点击区域一致"""
        controller.state = GameState.SELECTING_DIFFICULTY

        with patch("chess_ai.gui.controller.ConfigManager") as mock_config_manager:
            mock_config = mock_config_manager.return_value
            for difficulty, rect in difficulty_button_rects(controller.config):
                controller.handle_click(rect.centerx, rect.centery)
                assert controller.difficulty == difficulty
                assert controller.state == GameState.WAITING
                mock_config.set_difficulty.assert_called_with(difficulty)
                controller.state = GameState.SELECTING_DIFFICULTY

    def test_named_themes_are_distinct(self):
        """三套主题不是同一套默认色"""
        classic = ThemeManager.get_theme("classic")
        modern = ThemeManager.get_theme("modern")
        dark = ThemeManager.get_theme("dark")

        assert modern.board_bg != classic.board_bg
        assert dark.app_bg != classic.app_bg

    def test_toolbar_renders_after_difficulty_selected(self, controller):
        """选择难度进入游戏后工具栏渲染不崩溃"""
        pygame.font.init()
        renderer = ChessRenderer(controller.config, ThemeManager.get_theme("classic"))
        surface = pygame.Surface((controller.config.window_width, controller.config.window_height))

        controller.state = GameState.WAITING

        renderer.render_toolbar(surface, controller)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
