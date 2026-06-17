"""
产物输出管理模块
统一管理图表、表格、数据文件的输出
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional


class OutputManager:
    """产物输出管理器"""

    def __init__(self, config):
        """
        初始化输出管理器

        Args:
            config: Config 配置实例
        """
        self.config = config

    def save_table(
        self,
        df: pd.DataFrame,
        filename: str,
        chapter_prefix: str = "ch01",
        index: bool = False,
    ) -> Path:
        """
        保存表格到产物目录

        Args:
            df: 数据框
            filename: 文件名（不含扩展名）
            chapter_prefix: 章节前缀
            index: 是否保存索引

        Returns:
            Path: 保存的文件路径
        """
        full_name = f"{chapter_prefix}_{filename}.csv"
        save_path = self.config.tables_dir / full_name

        df.to_csv(save_path, index=index, encoding="utf-8-sig")
        print(f"[OutputManager] 表格已保存: {save_path}")
        return save_path

    def save_data(
        self,
        df: pd.DataFrame,
        filename: str,
        index: bool = False,
    ) -> Path:
        """
        保存处理后数据到 processed 目录

        Args:
            df: 数据框
            filename: 文件名
            index: 是否保存索引

        Returns:
            Path: 保存的文件路径
        """
        save_path = self.config.data_processed_dir / filename
        df.to_csv(save_path, index=index, encoding="utf-8-sig")
        print(f"[OutputManager] 数据已保存: {save_path}")
        return save_path

    def save_json(
        self,
        data: dict,
        filename: str,
        chapter_prefix: str = "ch01",
    ) -> Path:
        """
        保存 JSON 数据

        Args:
            data: 字典数据
            filename: 文件名（不含扩展名）
            chapter_prefix: 章节前缀

        Returns:
            Path: 保存的文件路径
        """
        full_name = f"{chapter_prefix}_{filename}.json"
        save_path = self.config.tables_dir / full_name

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OutputManager] JSON已保存: {save_path}")
        return save_path
