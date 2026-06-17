"""
可视化工具模块
提供通用的数据可视化功能
"""

import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from typing import Optional, Union


# 设置中文字体支持
matplotlib.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


class Visualizer:
    """可视化工具"""

    def __init__(self, config):
        """
        初始化可视化工具

        Args:
            config: Config 配置实例
        """
        self.config = config
        self.style = config.visual_style

        # 应用全局样式
        plt.rcParams.update({
            "font.family": self.style["font_family"],
            "font.size": self.style["font_size"],
            "figure.dpi": self.style["dpi"],
        })

    def save_figure(
        self,
        fig: plt.Figure,
        filename: str,
        chapter_prefix: str = "ch01",
        subdir: Optional[str] = None,
    ) -> Path:
        """
        保存图表到产物目录

        Args:
            fig: matplotlib Figure 对象
            filename: 文件名（不含扩展名）
            chapter_prefix: 章节前缀（如 ch01）
            subdir: 子目录名（可选）

        Returns:
            Path: 保存的文件路径
        """
        save_dir = self.config.figures_dir
        if subdir:
            save_dir = save_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)

        ext = self.style["save_format"]
        full_name = f"{chapter_prefix}_{filename}.{ext}"
        save_path = save_dir / full_name

        fig.savefig(save_path, bbox_inches="tight", dpi=self.style["dpi"])
        plt.close(fig)
        print(f"[Visualizer] 图表已保存: {save_path}")
        return save_path

    def create_bar_plot(
        self,
        x,
        y,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        color: Optional[str] = None,
        figsize: Optional[tuple] = None,
    ) -> plt.Figure:
        """
        创建柱状图

        Args:
            x: x 轴数据
            y: y 轴数据
            title: 标题
            xlabel: x 轴标签
            ylabel: y 轴标签
            color: 柱子颜色
            figsize: 图表大小

        Returns:
            plt.Figure: Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize or self.style["figure_size"])
        ax.bar(x, y, color=color or self.style["color_palette"][0])
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig

    def create_histogram(
        self,
        data,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "频数",
        bins: int = 30,
        color: Optional[str] = None,
        figsize: Optional[tuple] = None,
    ) -> plt.Figure:
        """
        创建直方图

        Args:
            data: 数据
            title: 标题
            xlabel: x 轴标签
            ylabel: y 轴标签
            bins: 分箱数
            color: 颜色
            figsize: 图表大小

        Returns:
            plt.Figure: Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize or self.style["figure_size"])
        ax.hist(data, bins=bins, color=color or self.style["color_palette"][0], edgecolor="white")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig
