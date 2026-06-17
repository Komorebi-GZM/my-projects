"""
数据加载工具模块
提供通用的数据加载功能，支持 CSV/Excel/Parquet 格式
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union


class DataLoader:
    """数据加载器"""

    def __init__(self, config):
        """
        初始化数据加载器

        Args:
            config: Config 配置实例
        """
        self.config = config
        self._raw_data_cache: Optional[pd.DataFrame] = None

    def load_raw(self, filename: Optional[str] = None) -> pd.DataFrame:
        """
        加载原始数据

        Args:
            filename: 数据文件名，默认使用配置中的文件名

        Returns:
            pd.DataFrame: 加载的数据框

        Raises:
            FileNotFoundError: 数据文件不存在
        """
        if self._raw_data_cache is not None and filename is None:
            return self._raw_data_cache

        fname = filename or self.config.raw_data_filename
        fpath = self.config.data_raw_dir / fname

        if not fpath.exists():
            raise FileNotFoundError(f"数据文件不存在: {fpath}")

        df = self._read_file(fpath)
        print(f"[DataLoader] 已加载原始数据: {fpath.name} ({len(df)} 行, {len(df.columns)} 列)")

        if filename is None:
            self._raw_data_cache = df

        return df

    def load_processed(self, filename: str) -> pd.DataFrame:
        """
        加载处理后的数据

        Args:
            filename: 数据文件名

        Returns:
            pd.DataFrame: 加载的数据框
        """
        fpath = self.config.data_processed_dir / filename

        if not fpath.exists():
            raise FileNotFoundError(f"处理后数据文件不存在: {fpath}")

        df = self._read_file(fpath)
        print(f"[DataLoader] 已加载处理后数据: {fpath.name} ({len(df)} 行, {len(df.columns)} 列)")
        return df

    def _read_file(self, fpath: Path) -> pd.DataFrame:
        """
        根据文件扩展名读取数据

        Args:
            fpath: 文件路径

        Returns:
            pd.DataFrame: 数据框
        """
        suffix = fpath.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(fpath)
        elif suffix in (".xlsx", ".xls"):
            return pd.read_excel(fpath)
        elif suffix == ".parquet":
            return pd.read_parquet(fpath)
        elif suffix == ".json":
            return pd.read_json(fpath)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        获取数据基本信息

        Args:
            df: 数据框

        Returns:
            dict: 包含 shape、dtypes、memory_usage 等信息
        """
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "null_counts": df.isnull().sum().to_dict(),
            "duplicate_count": df.duplicated().sum(),
        }
