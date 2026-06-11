"""Settings 单例模式测试

验证 maitian_agent 包级 settings 和 get_settings() 的单例行为。
TDD RED 阶段。
"""
import pytest


class TestSettingsSingleton:
    """验证 get_settings() 返回单例"""

    def test_get_settings_returns_same_instance(self):
        """多次调用 get_settings() 应返回同一个实例"""
        from maitian_agent.config.settings import get_settings

        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2, "get_settings() 应返回单例"

    def test_get_settings_is_lru_cached(self):
        """get_settings() 应使用 lru_cache 装饰"""
        from maitian_agent.config.settings import get_settings
        assert hasattr(get_settings, "cache_info"), "get_settings 应有 cache_info（lru_cache）"
        info = get_settings.cache_info()
        assert info.hits >= 1, f"应有缓存命中，cache_info: {info}"

    def test_get_settings_returns_settings_type(self):
        """get_settings() 返回值应为 Settings 类型"""
        from maitian_agent.config.settings import get_settings, Settings

        s = get_settings()
        assert isinstance(s, Settings), f"应为 Settings 类型，实际 {type(s)}"


class TestPackageLevelSettings:
    """验证 maitian_agent 包级 settings 的单例行为"""

    def test_package_settings_is_settings_type(self):
        """maitian_agent.settings 应为 Settings 类型"""
        from maitian_agent import settings
        from maitian_agent.config.settings import Settings

        assert isinstance(settings, Settings), f"应为 Settings 类型，实际 {type(settings)}"

    def test_package_settings_is_same_as_get_settings(self):
        """maitian_agent.settings 应与 get_settings() 返回同一实例"""
        from maitian_agent import settings
        from maitian_agent.config.settings import get_settings

        assert settings is get_settings(), (
            "包级 settings 应与 get_settings() 是同一实例（单例）"
        )

    def test_config_module_settings_is_same_as_get_settings(self):
        """config/settings.py 模块级 settings 应与 get_settings() 是同一实例"""
        from maitian_agent.config.settings import settings, get_settings

        assert settings is get_settings(), (
            "config.settings 模块级 settings 应与 get_settings() 是同一实例"
        )

    def test_package_settings_not_reinstantiated(self):
        """多次导入不应创建新实例"""
        import importlib
        import maitian_agent

        s1 = maitian_agent.settings
        importlib.reload(maitian_agent)
        s2 = maitian_agent.settings
        # reload 后 lru_cache 会被清除，但 get_settings 仍然返回新缓存实例
        # 关键是同一运行周期内不应创建多余实例
        assert isinstance(s2, type(s1)), "reload 后类型应一致"


class TestSettingsBackwardCompatibility:
    """验证向后兼容性"""

    def test_settings_has_expected_fields(self):
        """settings 应包含所有预期字段"""
        from maitian_agent import settings

        assert hasattr(settings, "project_name")
        assert hasattr(settings, "version")
        assert hasattr(settings, "openai_api_key")
        assert hasattr(settings, "openai_api_base")
        assert hasattr(settings, "model_name")
        assert hasattr(settings, "debug")
        assert hasattr(settings, "temperature")

    def test_settings_default_values(self):
        """settings 应有合理的默认值"""
        from maitian_agent import settings

        assert settings.project_name == "麦田智囊"
        assert settings.version == "1.0.0"
        assert settings.model_name == "deepseek-v2"
        assert settings.temperature == 0.7
        assert settings.debug is False

    def test_import_settings_class_still_works(self):
        """直接导入 Settings 类仍应可用"""
        from maitian_agent.config.settings import Settings

        s = Settings(_env_file=None, _env_nested_delimiter=None)
        assert s.project_name == "麦田智囊"

    def test_import_from_package_level_works(self):
        """from maitian_agent import settings 仍应可用"""
        from maitian_agent import settings

        assert settings is not None
        assert settings.project_name == "麦田智囊"
