"""
配置管理器 - YAML + 环境变量双层配置
"""

from __future__ import annotations

import copy
import logging
import os
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from .difficulty import Difficulty


class ConfigManager:
    """
    配置管理器 - 单例模式

    优先级: 环境变量 > YAML 配置文件 > 默认值
    支持点分隔的键访问，如 "model.name"
    """

    _instance: Any = None

    def __new__(cls, config_path: str | Path = "config/config.yaml") -> ConfigManager:
        if cls._instance is None:
            instance: ConfigManager = super().__new__(cls)  # type: ignore[return-value]
            object.__setattr__(instance, "_initialized", False)
            cls._instance = instance
        return cls._instance  # type: ignore[no-any-return]

    def __init__(self, config_path: str | Path = "config/config.yaml") -> None:
        # 防止重复初始化（单例模式）
        initialized = getattr(self, "_initialized", False)
        if initialized:
            return

        self._config_path = Path(config_path)
        self._defaults: dict[str, Any] = {
            "model": {
                "name": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
                "timeout": 15,
                "temperature": 0.1,
                "max_tokens": 4096,
            },
            "agent": {
                "max_retries": 3,
                "checkpoint_path": "./data/checkpoints.db",
            },
            "logging": {
                "level": "INFO",
                "file_path": "./logs/chess_ai.log",
                "max_bytes": 10485760,
                "backup_count": 5,
            },
            "storage": {
                "db_path": "./data/chess.db",
                "saves_path": "./saves",
            },
            "gui": {
                "window_width": 800,
                "window_height": 700,
                "board_margin": 30,
                "grid_size": 60,
                "piece_radius": 26,
                "animation_enabled": True,
                "sound_enabled": True,
                "show_hints": True,
            },
            "game": {
                "ai_side": "black",
                "human_side": "red",
                "resign_threshold": -8.0,
                "difficulty": "medium",
            },
        }

        self._config: dict[str, Any] = {}
        self._load_config()
        self._initialized = True

    def _load_config(self) -> None:
        """加载配置：默认值 -> YAML 文件 -> 环境变量"""
        # 1. 从默认值深拷贝开始
        self._config = copy.deepcopy(self._defaults)

        # 2. 加载 YAML 文件（如果存在）
        if self._config_path.exists():
            try:
                with open(self._config_path, encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f) or {}
                self._deep_update(self._config, yaml_config)
            except Exception as e:
                logging.getLogger(__name__).warning(f"加载配置文件 {self._config_path} 失败: {e}")

        # 3. 覆盖环境变量（格式: CHESS_<KEY>，点转为下划线）
        for key, value in os.environ.items():
            if key.startswith("CHESS_"):
                config_key = key[6:].lower().replace("__", ".")
                keys = config_key.split(".")
                self._set_nested(self._config, keys, self._convert_env_value(value))

    def _deep_update(self, base: dict, update: dict) -> None:
        """深度合并两个字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def _set_nested(self, d: dict, keys: list[str], value: Any) -> None:
        """设置嵌套字典值"""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值为合适的类型"""
        # 布尔值
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # 整数
        try:
            if "." not in value:
                return int(value)
        except ValueError:
            pass

        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # 字符串（去除可能的引号）
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            return value[1:-1]
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1]

        return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 点分隔的键路径，如 "model.name"
            default: 键不存在时返回的默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        current = self._config

        try:
            for k in keys:
                if isinstance(current, dict):
                    current = current[k]
                else:
                    return default
            return current
        except (KeyError, TypeError):
            return default

    def get_difficulty(self) -> Difficulty:
        """
        获取当前 AI 难度级别

        Returns:
            Difficulty 枚举值
        """
        value = self.get("game.difficulty", "medium")
        return Difficulty(value)

    def set_difficulty(self, difficulty: Difficulty | str) -> None:
        """
        设置 AI 难度级别

        Args:
            difficulty: Difficulty 枚举或小写字符串 ("easy"/"medium"/"hard")

        Raises:
            ValueError: 如果字符串值无效
        """
        if isinstance(difficulty, str):
            difficulty = Difficulty(difficulty)
        self._config["game"]["difficulty"] = difficulty.value

    def get_required(self, key: str) -> Any:
        """
        获取必需的配置值，如果不存在则引发异常

        Args:
            key: 点分隔的键路径

        Returns:
            配置值

        Raises:
            KeyError: 如果配置不存在
        """
        value = self.get(key)
        if value is None:
            # 检查默认值中是否有此键（避免将 None 作为有效值）
            keys = key.split(".")
            current: Any = self._defaults
            try:
                for k in keys:
                    if isinstance(current, dict):
                        current = current[k]
                    else:
                        raise KeyError(f"配置键 '{key}' 不存在且无默认值")
            except KeyError:
                raise KeyError(f"配置键 '{key}' 不存在且无默认值")
        return value

    def mask_sensitive(self, value: str) -> str:
        """
        脱敏敏感值（如 API Key），保留后4位

        Args:
            value: 原始值

        Returns:
            脱敏后的值，如 "****1234"
        """
        if not value or len(value) <= 4:
            return "****"
        return "****" + value[-4:]

    def save(self) -> None:
        """
        保存当前配置到 YAML 文件

        仅保存与默认值不同的配置项，以保持文件整洁
        """
        # 计算需要保存的差异（相对于默认值）
        diff = self._compute_diff(self._defaults, self._config)
        if not diff:
            # 没有差异时删除文件（如果存在）
            if self._config_path.exists():
                self._config_path.unlink()
            return

        # 确保目录存在
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存到文件
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                yaml.dump(diff, f, default_flow_style=False, allow_unicode=True)
            logging.getLogger(__name__).debug(f"配置已保存到 {self._config_path}")
        except Exception as e:
            logging.getLogger(__name__).error(f"保存配置失败: {e}")

    def _compute_diff(self, defaults: dict, current: dict) -> dict:
        """
        计算当前配置相对于默认值的差异

        Args:
            defaults: 默认配置字典
            current: 当前配置字典

        Returns:
            只包含不同值的字典，保持嵌套结构
        """
        diff: dict[str, Any] = {}
        all_keys = set(defaults.keys()) | set(current.keys())

        for key in all_keys:
            default_val = defaults.get(key)
            current_val = current.get(key)

            if key in defaults and key in current:
                if isinstance(default_val, dict) and isinstance(current_val, dict):
                    nested_diff = self._compute_diff(default_val, current_val)
                    if nested_diff:
                        diff[key] = nested_diff
                elif default_val != current_val:
                    diff[key] = current_val
            elif key not in defaults and key in current:
                diff[key] = current_val

        return diff

    def __repr__(self) -> str:
        return f"ConfigManager(path='{self._config_path}')"
