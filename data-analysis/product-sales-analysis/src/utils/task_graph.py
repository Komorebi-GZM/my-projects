"""
任务依赖图模块 - 产品销售数据分析项目

本模块提供章节间依赖关系管理功能。通过 TaskGraph 类，
可以查询章节状态、检查前置依赖是否满足、更新章节完成状态，
并打印整体进度概览。
"""

from typing import Dict, List, Optional


# ============================================================
# 章节依赖关系配置
# ============================================================
# 键为章节标识符，值为该章节的前置依赖列表
CHAPTER_DEPENDENCIES: Dict[str, List[str]] = {
    "ch01_data_cleaning": [],                                    # 无依赖
    "ch02_descriptive_analysis": ["ch01_data_cleaning"],          # 依赖 ch01
    "ch03_sales_forecasting": ["ch01_data_cleaning", "ch02_descriptive_analysis"],  # 依赖 ch01, ch02
    "ch04_price_elasticity": ["ch01_data_cleaning", "ch02_descriptive_analysis"],   # 依赖 ch01, ch02
    "ch05_conclusions_and_recommendations": ["ch02_descriptive_analysis", "ch03_sales_forecasting", "ch04_price_elasticity"],  # 依赖 ch02, ch03, ch04
}

# 章节中文名称
CHAPTER_NAMES: Dict[str, str] = {
    "ch01_data_cleaning": "数据清洗",
    "ch02_descriptive_analysis": "描述性统计与可视化",
    "ch03_sales_forecasting": "销售趋势预测",
    "ch04_price_elasticity": "价格弹性分析",
    "ch05_conclusions_and_recommendations": "结论与业务建议",
}


class TaskGraph:
    """
    任务依赖图管理器。

    管理数据分析各章节之间的依赖关系和执行状态。
    支持查询状态、检查依赖、更新进度和打印概览。

    Attributes:
        statuses: 各章节的执行状态字典。
            状态值: "pending"（待执行）、"running"（执行中）、"completed"（已完成）、"failed"（失败）。
    """

    def __init__(self):
        """初始化 TaskGraph，将所有章节状态设为 pending。"""
        self.statuses: Dict[str, str] = {
            chapter: "pending" for chapter in CHAPTER_DEPENDENCIES
        }

    def get_status(self, chapter: str) -> str:
        """
        获取指定章节的执行状态。

        Args:
            chapter: 章节标识符。

        Returns:
            str: 章节状态（pending / running / completed / failed）。
        """
        return self.statuses.get(chapter, "unknown")

    def check_dependencies(self, chapter: str) -> bool:
        """
        检查指定章节的所有前置依赖是否已完成。

        Args:
            chapter: 章节标识符。

        Returns:
            bool: 所有前置依赖均已完成返回 True，否则返回 False。
        """
        deps = CHAPTER_DEPENDENCIES.get(chapter, [])
        for dep in deps:
            if self.statuses.get(dep) != "completed":
                print(f"[依赖检查] 章节 '{chapter}' 的前置依赖 '{dep}' 尚未完成（状态: {self.statuses.get(dep)}）")
                return False
        print(f"[依赖检查] 章节 '{chapter}' 的所有前置依赖已满足")
        return True

    def update_status(self, chapter: str, status: str) -> None:
        """
        更新指定章节的执行状态。

        Args:
            chapter: 章节标识符。
            status: 新状态，可选值为 "pending"、"running"、"completed"、"failed"。

        Raises:
            ValueError: 当状态值不合法时抛出。
        """
        valid_statuses = {"pending", "running", "completed", "failed"}
        if status not in valid_statuses:
            raise ValueError(f"无效的状态值: {status}，有效值为: {valid_statuses}")

        old_status = self.statuses.get(chapter, "unknown")
        self.statuses[chapter] = status
        print(f"[状态更新] 章节 '{chapter}': {old_status} -> {status}")

    def print_status(self) -> None:
        """打印所有章节的执行状态概览。"""
        print("=" * 60)
        print("任务执行状态概览")
        print("=" * 60)

        for chapter, deps in CHAPTER_DEPENDENCIES.items():
            name = CHAPTER_NAMES.get(chapter, chapter)
            status = self.statuses.get(chapter, "unknown")
            status_symbol = {
                "pending": "[ ]",
                "running": "[~]",
                "completed": "[x]",
                "failed": "[!]",
                "unknown": "[?]",
            }.get(status, "[?]")

            dep_info = f" (依赖: {', '.join(deps)})" if deps else " (无依赖)"
            print(f"  {status_symbol} {chapter} - {name}{dep_info}  状态: {status}")

        print("=" * 60)

        completed = sum(1 for s in self.statuses.values() if s == "completed")
        total = len(self.statuses)
        print(f"  进度: {completed}/{total} 已完成")
        print("=" * 60)
