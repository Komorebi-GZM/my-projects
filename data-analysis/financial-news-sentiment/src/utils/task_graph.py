"""任务依赖图与进度检查模块.

定义项目6个章节的依赖关系，提供进度检查与状态报告功能。

依赖关系:
    ch01 (数据预处理)
      -> ch02 (描述性统计)
      -> ch03 (文本挖掘与情感分析)
      -> ch04 (特征工程)
      -> ch05 (事件驱动策略分析)
      -> ch06 (可视化看板与总结报告)

Usage:
    命令行:
        python task_graph.py                    # 查看全部进度
        python task_graph.py --chapter ch01     # 查看指定章节
        python task_graph.py --report           # 生成进度报告

    代码中:
        >>> from src.utils.task_graph import TaskGraph
        >>> tg = TaskGraph()
        >>> tg.print_status()
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from src.utils.config import (
    CHAPTERS,
    OUTPUTS_DIR,
    setup_logging,
)

logger = logging.getLogger(__name__)


# =============================================================================
# 数据结构定义
# =============================================================================
@dataclass
class ChapterTask:
    """章节任务定义.

    Attributes:
        chapter_id: 章节ID，如 'ch01'.
        chapter_name: 章节目录名.
        title: 章节中文名称.
        description: 章节描述.
        dependencies: 依赖的章节ID列表.
        expected_outputs: 预期产物文件名列表.
        status: 当前完成状态 ('pending' / 'completed' / 'partial').
    """

    chapter_id: str
    chapter_name: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    status: str = "pending"


# =============================================================================
# 依赖关系定义
# =============================================================================
def build_task_graph() -> Dict[str, ChapterTask]:
    """构建6个章节的任务依赖图.

    Returns:
        章节ID到 ChapterTask 的映射字典.
    """
    tasks: Dict[str, ChapterTask] = {}

    # 定义各章节的预期产物（与实际产物文件名一致）
    expected_outputs_map: Dict[str, List[str]] = {
        "ch01": [
            "ch01_cleaned_data.csv",
            "ch01_data_quality_report.md",
            "ch01_missing_values_summary.csv",
            "ch01_category_statistics.csv",
            "ch01_keyword_statistics.csv",
        ],
        "ch02": [
            "ch02_time_distribution.png",
            "ch02_category_ranking.png",
            "ch02_impact_tier_analysis.png",
            "ch02_top50_keywords.png",
            "ch02_keyword_wordcloud.png",
            "ch02_source_bias_analysis.png",
            "ch02_text_length_and_cross.png",
            "ch02_category_yearly_trend.png",
            "ch02_descriptive_stats.csv",
            "ch02_descriptive_stats_report.md",
        ],
        "ch03": [
            "ch03_sentiment_labels.csv",
            "ch03_topic_model_results.csv",
            "ch03_sentiment_distribution.png",
            "ch03_sentiment_by_category.png",
            "ch03_sentiment_timeline.png",
            "ch03_event_window_sentiment.png",
            "ch03_topic_visualization.html",
            "ch03_sentiment_analysis_report.md",
            "ch03_topic_analysis_report.md",
        ],
        "ch04": [
            "ch04_engineered_features.csv",
            "ch04_feature_engineering_report.md",
            "ch04_correlation_heatmap.png",
            "ch04_feature_distribution.png",
            "ch04_feature_importance.csv",
        ],
        "ch05": [
            "ch05_event_calendar.csv",
            "ch05_influence_score.csv",
            "ch05_event_analysis.png",
            "ch05_event_analysis_report.md",
        ],
        "ch06": [
            "ch06_comprehensive_report.md",
            "ch06_key_metrics_table.csv",
        ],
    }

    # 定义依赖关系
    dependency_map: Dict[str, List[str]] = {
        "ch01": [],
        "ch02": ["ch01"],
        "ch03": ["ch01", "ch02"],
        "ch04": ["ch01", "ch02", "ch03"],
        "ch05": ["ch01", "ch02", "ch03", "ch04"],
        "ch06": ["ch01", "ch02", "ch03", "ch04", "ch05"],
    }

    # 从配置中构建任务
    for ch in CHAPTERS:
        ch_id = ch["id"]
        tasks[ch_id] = ChapterTask(
            chapter_id=ch_id,
            chapter_name=ch["name"],
            title=ch["title"],
            description=ch["description"],
            dependencies=dependency_map.get(ch_id, []),
            expected_outputs=expected_outputs_map.get(ch_id, []),
        )

    return tasks


# =============================================================================
# 进度检查
# =============================================================================
class TaskGraph:
    """任务依赖图管理器.

    提供进度检查、状态报告和依赖验证功能.

    Example:
        >>> tg = TaskGraph()
        >>> tg.check_progress()
        >>> tg.print_status()
    """

    def __init__(self) -> None:
        """初始化任务图."""
        self.tasks: Dict[str, ChapterTask] = build_task_graph()
        logger.info("任务图已初始化，共 %d 个章节", len(self.tasks))

    def check_progress(self) -> Dict[str, Dict]:
        """检查各章节产物完成状态.

        遍历所有章节，检查其输出目录中是否存在预期产物文件，
        并更新各章节的完成状态.

        Returns:
            章节ID到状态信息的映射字典，包含:
            - 'status': 'completed' / 'partial' / 'pending'
            - 'found': 已找到的产物列表
            - 'missing': 缺失的产物列表
            - 'total': 预期产物总数
            - 'found_count': 已找到产物数
        """
        results: Dict[str, Dict] = {}

        for ch_id, task in self.tasks.items():
            output_dir = OUTPUTS_DIR / task.chapter_name
            found: List[str] = []
            missing: List[str] = []

            for expected_file in task.expected_outputs:
                filepath = output_dir / expected_file
                if filepath.exists():
                    found.append(expected_file)
                else:
                    missing.append(expected_file)

            total = len(task.expected_outputs)
            found_count = len(found)

            if found_count == total and total > 0:
                status = "completed"
            elif found_count > 0:
                status = "partial"
            else:
                status = "pending"

            task.status = status

            results[ch_id] = {
                "status": status,
                "found": found,
                "missing": missing,
                "total": total,
                "found_count": found_count,
            }

            logger.debug("章节 %s 状态: %s (%d/%d)",
                         ch_id, status, found_count, total)

        return results

    def print_status(
        self,
        chapter_filter: Optional[str] = None,
    ) -> None:
        """打印进度状态报告.

        以树形结构展示各章节的完成状态和依赖关系.

        Args:
            chapter_filter: 指定章节ID进行过滤. None 显示全部.
        """
        progress = self.check_progress()

        # 状态图标
        status_icons = {
            "completed": "[OK]",
            "partial": "[..]",
            "pending": "[  ]",
        }

        print("\n" + "=" * 70)
        print("  金融新闻舆情分析 - 项目进度")
        print("=" * 70)

        for ch in CHAPTERS:
            ch_id = ch["id"]

            if chapter_filter and ch_id != chapter_filter:
                continue

            task = self.tasks[ch_id]
            info = progress[ch_id]
            icon = status_icons.get(info["status"], "[??]")

            print(f"\n  {icon} {ch_id}: {task.title}")
            print(f"       描述: {task.description}")

            if task.dependencies:
                deps = ", ".join(task.dependencies)
                print(f"       依赖: {deps}")

            print(f"       产物: {info['found_count']}/{info['total']}")

            if info["found"]:
                for f in info["found"]:
                    print(f"             [+] {f}")

            if info["missing"]:
                for f in info["missing"]:
                    print(f"             [-] {f}")

        print("\n" + "=" * 70)

        # 汇总统计
        total_chapters = len(CHAPTERS)
        completed = sum(
            1 for v in progress.values() if v["status"] == "completed"
        )
        partial = sum(
            1 for v in progress.values() if v["status"] == "partial"
        )
        pending = sum(
            1 for v in progress.values() if v["status"] == "pending"
        )

        print(f"  总计: {total_chapters} 个章节 | "
              f"已完成: {completed} | "
              f"部分完成: {partial} | "
              f"待开始: {pending}")
        print("=" * 70 + "\n")

    def generate_report(self) -> str:
        """生成进度报告（Markdown格式）.

        Returns:
            Markdown 格式的进度报告字符串.
        """
        progress = self.check_progress()

        lines: List[str] = [
            "# 项目进度报告",
            "",
            f"**项目**: 金融新闻舆情分析与市场预测",
            "",
            "## 章节进度",
            "",
            "| 章节 | 标题 | 状态 | 产物进度 |",
            "|------|------|------|----------|",
        ]

        status_labels = {
            "completed": "已完成",
            "partial": "部分完成",
            "pending": "待开始",
        }

        for ch in CHAPTERS:
            ch_id = ch["id"]
            task = self.tasks[ch_id]
            info = progress[ch_id]
            label = status_labels.get(info["status"], "未知")
            lines.append(
                f"| {ch_id} | {task.title} | {label} | "
                f"{info['found_count']}/{info['total']} |"
            )

        lines.extend([
            "",
            "## 依赖关系",
            "",
            "```",
        ])

        for ch_id, task in self.tasks.items():
            if task.dependencies:
                deps = " -> ".join(task.dependencies + [ch_id])
                lines.append(f"  {deps}")

        lines.extend([
            "```",
            "",
        ])

        return "\n".join(lines)

    def validate_dependencies(self, chapter_id: str) -> bool:
        """验证指定章节的所有依赖是否已完成.

        Args:
            chapter_id: 要验证的章节ID.

        Returns:
            True 表示所有依赖已完成，False 表示有未完成的依赖.
        """
        progress = self.check_progress()
        task = self.tasks.get(chapter_id)

        if task is None:
            logger.error("未知章节: %s", chapter_id)
            return False

        all_deps_met = True
        for dep_id in task.dependencies:
            dep_status = progress.get(dep_id, {}).get("status", "pending")
            if dep_status != "completed":
                logger.warning(
                    "章节 %s 的依赖 %s 尚未完成 (状态: %s)",
                    chapter_id, dep_id, dep_status,
                )
                all_deps_met = False

        return all_deps_met


# =============================================================================
# 命令行入口
# =============================================================================
def main() -> None:
    """命令行入口函数.

    支持以下参数:
        --chapter CH_ID: 查看指定章节进度
        --report: 生成 Markdown 格式进度报告
    """
    parser = argparse.ArgumentParser(
        description="金融新闻舆情分析 - 任务进度检查",
    )
    parser.add_argument(
        "--chapter",
        type=str,
        default=None,
        help="查看指定章节进度，如 ch01",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="生成 Markdown 格式进度报告",
    )

    args = parser.parse_args()

    # 初始化日志
    setup_logging()

    tg = TaskGraph()

    if args.report:
        report = tg.generate_report()
        print(report)
    else:
        tg.print_status(chapter_filter=args.chapter)


if __name__ == "__main__":
    main()
