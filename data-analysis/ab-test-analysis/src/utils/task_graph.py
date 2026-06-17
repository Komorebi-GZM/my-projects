"""
任务依赖图模块
管理章节之间的依赖关系和执行顺序
"""

from typing import Dict, List


class TaskGraph:
    """任务依赖图"""

    def __init__(self, config):
        """
        初始化任务依赖图

        Args:
            config: Config 配置实例
        """
        self.config = config
        self.chapters = config.chapters

    def get_execution_order(self) -> List[str]:
        """
        获取拓扑排序后的执行顺序

        Returns:
            List[str]: 按依赖关系排序的章节ID列表
        """
        # 简单实现：按章节ID排序
        sorted_chapters = sorted(self.chapters.keys())
        return sorted_chapters

    def get_dependencies(self, chapter_id: str) -> List[str]:
        """
        获取指定章节的依赖

        Args:
            chapter_id: 章节ID（如 ch01）

        Returns:
            List[str]: 依赖的章节ID列表
        """
        chapter = self.chapters.get(chapter_id, {})
        return chapter.get("dependencies", [])

    def is_ready(self, chapter_id: str, completed: List[str]) -> bool:
        """
        检查章节是否可以执行（所有依赖已完成）

        Args:
            chapter_id: 章节ID
            completed: 已完成的章节ID列表

        Returns:
            bool: 是否可以执行
        """
        deps = self.get_dependencies(chapter_id)
        return all(dep in completed for dep in deps)
