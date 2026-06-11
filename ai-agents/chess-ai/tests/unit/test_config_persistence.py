"""
配置持久化单元测试
"""

import os
import tempfile

import pytest
import yaml

from chess_ai.infra.config import ConfigManager
from chess_ai.infra.difficulty import Difficulty


class TestConfigPersistence:
    """测试配置持久化到 YAML 文件"""

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件路径"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("game:\n  difficulty: medium\n")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_set_difficulty_persists_to_file(self, temp_config_file):
        """set_difficulty 后保存到文件，下次加载仍有效"""
        # 重置单例
        ConfigManager._instance = None

        config = ConfigManager(temp_config_file)
        config.set_difficulty(Difficulty.HARD)
        config.save()

        # 重新加载
        ConfigManager._instance = None
        config2 = ConfigManager(temp_config_file)
        assert config2.get_difficulty() == Difficulty.HARD

    def test_save_creates_yaml_with_difficulty(self, temp_config_file):
        """保存后 YAML 文件包含 difficulty 字段"""
        ConfigManager._instance = None

        config = ConfigManager(temp_config_file)
        config.set_difficulty(Difficulty.EASY)
        config.save()

        with open(temp_config_file, encoding="utf-8") as f:
            saved = yaml.safe_load(f)

        assert saved["game"]["difficulty"] == "easy"

    def test_load_from_existing_file(self, temp_config_file):
        """从已有 YAML 文件加载 difficulty"""
        ConfigManager._instance = None

        # 先写入 hard
        config = ConfigManager(temp_config_file)
        config.set_difficulty(Difficulty.HARD)
        config.save()

        # 重新加载验证
        ConfigManager._instance = None
        config2 = ConfigManager(temp_config_file)
        assert config2.get("game.difficulty") == "hard"

    def test_save_preserves_other_config(self, temp_config_file):
        """保存不会丢失其他配置项"""
        ConfigManager._instance = None

        config = ConfigManager(temp_config_file)
        # 修改 model 配置
        config._config.setdefault("model", {})["name"] = "test-model"
        config.set_difficulty(Difficulty.MEDIUM)
        config.save()

        ConfigManager._instance = None
        config2 = ConfigManager(temp_config_file)
        assert config2.get("model.name") == "test-model"
        assert config2.get_difficulty() == Difficulty.MEDIUM
