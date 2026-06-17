"""输出产物管理器模块.

提供统一的输出保存接口，支持：
- DataFrame 保存为 CSV
- 图表保存为 PNG/PDF（DPI >= 150）
- Markdown 报告保存
- 输出目录自动创建

Example:
    >>> from src.utils.output_manager import OutputManager
    >>> mgr = OutputManager("ch01_data_preprocessing")
    >>> mgr.save_dataframe(df, "cleaned_data.csv")
    >>> mgr.save_figure(fig, "distribution.png")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.utils.config import (
    FIGURE_DPI_HIGH,
    OUTPUTS_DIR,
    setup_logging,
)

logger = logging.getLogger(__name__)


class OutputManager:
    """输出产物管理器.

    负责管理指定章节的所有输出文件，包括数据、图表和报告。
    自动创建输出目录，确保产物存放位置一致。

    Attributes:
        chapter_name: 章节目录名.
        output_dir: 章节输出目录的 Path 对象.

    Example:
        >>> mgr = OutputManager("ch01_data_preprocessing")
        >>> mgr.save_dataframe(df, "cleaned_data.csv")
    """

    def __init__(self, chapter_name: str) -> None:
        """初始化输出管理器.

        Args:
            chapter_name: 章节目录名，如 'ch01_data_preprocessing'.
        """
        self.chapter_name: str = chapter_name
        self.output_dir: Path = OUTPUTS_DIR / chapter_name
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """确保输出目录存在，不存在则创建."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("输出目录已就绪: %s", self.output_dir)

    def get_path(self, filename: str) -> Path:
        """获取输出文件的完整路径.

        Args:
            filename: 文件名.

        Returns:
            完整的文件路径.
        """
        return self.output_dir / filename

    def save_dataframe(
        self,
        df: pd.DataFrame,
        filename: str,
        index: bool = False,
        encoding: str = "utf-8",
    ) -> Path:
        """保存 DataFrame 到 CSV 文件.

        Args:
            df: 要保存的 DataFrame.
            filename: 输出文件名，如 'cleaned_data.csv'.
            index: 是否保存索引，默认为 False.
            encoding: 文件编码，默认为 utf-8.

        Returns:
            保存文件的 Path 对象.

        Raises:
            ValueError: 当 df 不是 DataFrame 时抛出.

        Example:
            >>> path = mgr.save_dataframe(df, "cleaned_data.csv")
            >>> print(path)
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("输入必须是 pandas DataFrame")

        filepath = self.get_path(filename)
        df.to_csv(filepath, index=index, encoding=encoding)
        logger.info("DataFrame 已保存: %s (%d 行 x %d 列)",
                     filepath, df.shape[0], df.shape[1])
        return filepath

    def save_figure(
        self,
        fig,
        filename: str,
        dpi: Optional[int] = None,
        format: Optional[str] = None,
        bbox_inches: str = "tight",
        **kwargs,
    ) -> Path:
        """保存图表到文件.

        支持 PNG、PDF、SVG 等格式，默认 DPI >= 150.

        Args:
            fig: matplotlib Figure 对象.
            filename: 输出文件名，如 'distribution.png'.
            dpi: 图像分辨率，默认使用配置中的 FIGURE_DPI_HIGH (300).
            format: 图像格式，默认根据文件扩展名推断.
            bbox_inches: 边界框设置，默认为 'tight'.
            **kwargs: 传递给 fig.savefig() 的额外参数.

        Returns:
            保存文件的 Path 对象.

        Example:
            >>> import matplotlib.pyplot as plt
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3])
            >>> mgr.save_figure(fig, "line_plot.png", dpi=200)
        """
        if dpi is None:
            dpi = FIGURE_DPI_HIGH

        if dpi < 150:
            logger.warning("DPI 值 %d 低于推荐值 150，已自动调整为 150", dpi)
            dpi = 150

        filepath = self.get_path(filename)

        # 根据文件扩展名推断格式
        if format is None:
            suffix = filepath.suffix.lower().lstrip(".")
            if suffix:
                format = suffix
            else:
                format = "png"
                filepath = filepath.with_suffix(".png")

        fig.savefig(
            filepath,
            dpi=dpi,
            format=format,
            bbox_inches=bbox_inches,
            **kwargs,
        )
        logger.info("图表已保存: %s (DPI: %d, 格式: %s)",
                     filepath, dpi, format)
        return filepath

    def save_markdown(
        self,
        content: str,
        filename: str,
        encoding: str = "utf-8",
    ) -> Path:
        """保存 Markdown 报告到文件.

        Args:
            content: Markdown 文本内容.
            filename: 输出文件名，如 'summary_report.md'.
            encoding: 文件编码，默认为 utf-8.

        Returns:
            保存文件的 Path 对象.

        Example:
            >>> report = "# 数据清洗报告\\n\\n## 概述\\n..."
            >>> mgr.save_markdown(report, "summary_report.md")
        """
        filepath = self.get_path(filename)
        filepath.write_text(content, encoding=encoding)
        logger.info("Markdown 报告已保存: %s (%d 字符)",
                     filepath, len(content))
        return filepath

    def list_outputs(self, pattern: str = "*") -> list[Path]:
        """列出当前章节的所有输出文件.

        Args:
            pattern: 文件匹配模式，默认为 '*' (全部).

        Returns:
            匹配的文件路径列表.
        """
        files = sorted(self.output_dir.glob(pattern))
        return [f for f in files if f.is_file()]


def ensure_output_dir(chapter_name: str) -> Path:
    """确保指定章节的输出目录存在.

    便捷函数，用于不需要 OutputManager 实例的场景.

    Args:
        chapter_name: 章节目录名.

    Returns:
        输出目录的 Path 对象.

    Example:
        >>> output_dir = ensure_output_dir("ch01_data_preprocessing")
    """
    output_dir = OUTPUTS_DIR / chapter_name
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("输出目录已就绪: %s", output_dir)
    return output_dir
