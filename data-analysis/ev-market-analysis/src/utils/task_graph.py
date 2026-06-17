# -*- coding: utf-8 -*-
"""task_graph.py - 任务依赖图

定义项目各章节的任务依赖关系，支持拓扑排序和执行状态跟踪。
用于管理多步骤数据分析流程的执行顺序。
"""

from typing import Dict, List, Optional, Set


class TaskNode:
    """任务节点，表示一个可执行的分析步骤。"""

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str = "",
        depends_on: Optional[List[str]] = None,
        chapter: str = "",
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.depends_on = depends_on or []
        self.chapter = chapter
        self.status = "pending"  # pending / running / completed / failed

    def __repr__(self):
        return f"TaskNode(id={self.task_id!r}, name={self.name!r}, status={self.status!r})"


class TaskGraph:
    """任务依赖图，管理分析任务的执行顺序和状态。"""

    def __init__(self, project_name: str = "ev_market_analysis"):
        self.project_name = project_name
        self.tasks: Dict[str, TaskNode] = {}
        self._build_default_graph()

    def _build_default_graph(self):
        """构建默认的任务依赖图。"""
        # ================================================================
        # ch01: 数据清洗任务
        # ================================================================
        self.add_task(TaskNode(
            task_id="ch01_step1.1",
            name="数据加载与结构探查",
            description="加载原始 CSV 数据，检查行列数、数据类型、前 N 行预览",
            chapter="ch01_data_cleaning",
        ))
        self.add_task(TaskNode(
            task_id="ch01_step1.2",
            name="缺失值检测与处理",
            description="检测各列缺失值数量和比例，制定处理策略",
            chapter="ch01_data_cleaning",
            depends_on=["ch01_step1.1"],
        ))
        self.add_task(TaskNode(
            task_id="ch01_step1.3",
            name="重复值检测与处理",
            description="检测完全重复和部分重复（品牌+型号+年份+变体）的记录",
            chapter="ch01_data_cleaning",
            depends_on=["ch01_step1.1"],
        ))
        self.add_task(TaskNode(
            task_id="ch01_step1.4",
            name="数据类型验证与转换",
            description="验证数值列、分类列的数据类型，进行必要转换",
            chapter="ch01_data_cleaning",
            depends_on=["ch01_step1.2", "ch01_step1.3"],
        ))
        self.add_task(TaskNode(
            task_id="ch01_step1.5",
            name="异常值检测与处理",
            description="使用 IQR / Z-score 方法检测数值列异常值",
            chapter="ch01_data_cleaning",
            depends_on=["ch01_step1.4"],
        ))
        self.add_task(TaskNode(
            task_id="ch01_step1.6",
            name="清洗后数据保存与报告生成",
            description="保存清洗后的数据集，生成数据清洗报告",
            chapter="ch01_data_cleaning",
            depends_on=["ch01_step1.5"],
        ))

        # ================================================================
        # ch02: 市场格局分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-02",
            name="市场格局分析",
            description="品牌销量排名、市占率、品牌-细分交叉分析、国家销量分布、市场细分分布",
            chapter="ch02_market_landscape",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch03: 价格机制分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-03",
            name="价格机制分析",
            description="价格与参数相关性分析、特征重要性排序、价格-参数散点图",
            chapter="ch03_price_mechanism",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch04: 技术趋势分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-04",
            name="技术趋势分析",
            description="参数年度统计、技术趋势折线图、参数年均增长率(CAGR)",
            chapter="ch04_tech_trends",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch05: 销量归因分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-05",
            name="销量归因分析",
            description="销量TOP10车型、爆款车型画像、销量分组对比",
            chapter="ch05_sales_attribution",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch06: 时序趋势分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-06",
            name="时序趋势分析",
            description="年度趋势数据、年度趋势三线图、复合增长率",
            chapter="ch06_temporal_trends",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch07: 竞品对标分析
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-07",
            name="竞品对标分析",
            description="同级车型对比、性价比排名、竞争力雷达图",
            chapter="ch07_competitive_benchmark",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch08: 量化建模
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-08",
            name="量化建模",
            description="价格预测模型、模型评估、特征重要性、聚类分析",
            chapter="ch08_quantitative_modeling",
            depends_on=["ch01_step1.6"],
        ))

        # ================================================================
        # ch09: 商业决策建议
        # ================================================================
        self.add_task(TaskNode(
            task_id="prompt-09",
            name="商业决策建议",
            description="消费者购车建议、企业策略建议、行业趋势预判",
            chapter="ch09_business_recommendations",
            depends_on=["prompt-02", "prompt-03", "prompt-04", "prompt-05", "prompt-06", "prompt-07", "prompt-08"],
        ))

    def add_task(self, task: TaskNode):
        """添加任务节点。"""
        self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Optional[TaskNode]:
        """获取指定任务节点。"""
        return self.tasks.get(task_id)

    def get_chapter_tasks(self, chapter: str) -> List[TaskNode]:
        """获取指定章节的所有任务。"""
        return [t for t in self.tasks.values() if t.chapter == chapter]

    def topological_sort(self) -> List[str]:
        """拓扑排序，返回可执行的任务 ID 列表。

        Returns
        -------
        list[str]
            按依赖关系排序的任务 ID 列表。
        """
        in_degree: Dict[str, int] = {tid: 0 for tid in self.tasks}
        for task in self.tasks.values():
            for dep in task.depends_on:
                if dep in in_degree:
                    in_degree[task.task_id] += 1

        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            queue.sort()  # 确保确定性顺序
            current = queue.pop(0)
            result.append(current)

            for task in self.tasks.values():
                if current in task.depends_on:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)

        if len(result) != len(self.tasks):
            raise RuntimeError("检测到循环依赖，无法完成拓扑排序")

        return result

    def get_ready_tasks(self) -> List[TaskNode]:
        """获取当前可执行的任务（所有依赖已完成）。"""
        ready = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue
            deps_met = all(
                self.tasks[dep].status == "completed"
                for dep in task.depends_on
                if dep in self.tasks
            )
            if deps_met:
                ready.append(task)
        return ready

    def mark_completed(self, task_id: str):
        """标记任务为已完成。"""
        if task_id in self.tasks:
            self.tasks[task_id].status = "completed"

    def mark_failed(self, task_id: str):
        """标记任务为失败。"""
        if task_id in self.tasks:
            self.tasks[task_id].status = "failed"

    def summary(self) -> str:
        """生成任务执行摘要。"""
        lines = [f"项目: {self.project_name}", "=" * 50]
        for tid in self.topological_sort():
            task = self.tasks[tid]
            status_icon = {"pending": "[ ]", "running": "[~]", "completed": "[x]", "failed": "[!]"}
            lines.append(f"  {status_icon.get(task.status, '[?]')} {tid}: {task.name}")
        return "\n".join(lines)


# ============================================================================
# 章节级任务定义（用于任务分发和产物管理）
# ============================================================================

TASKS = {
    'prompt-01': {
        'name': '数据清洗',
        'batch': 0,
        'depends': [],
        'script': 'src/ch01_data_cleaning/preprocess.py',
        'notebook': 'src/ch01_data_cleaning/preprocess.ipynb',
        'output_dir': 'outputs/ch01_data_cleaning',
        'key_artifacts': [
            'cleaned_data.csv',
            'cleaning_report.md',
        ],
    },
    'prompt-02': {
        'name': '市场格局分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch02_market_landscape/analysis.py',
        'notebook': 'src/ch02_market_landscape/analysis.ipynb',
        'output_dir': 'outputs/ch02_market_landscape',
        'key_artifacts': [
            'brand_sales_ranking.csv',
            'brand_market_share.png',
            'brand_segment_crosstab.csv',
            'country_sales_distribution.png',
            'segment_distribution.png',
            'ch02_report.md',
        ],
    },
    'prompt-03': {
        'name': '价格机制分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch03_price_mechanism/analysis.py',
        'notebook': 'src/ch03_price_mechanism/analysis.ipynb',
        'output_dir': 'outputs/ch03_price_mechanism',
        'key_artifacts': [
            'correlation_matrix.csv',
            'correlation_heatmap.png',
            'feature_importance.csv',
            'price_scatter_matrix.png',
            'ch03_report.md',
        ],
    },
    'prompt-04': {
        'name': '技术趋势分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch04_tech_trends/analysis.py',
        'notebook': 'src/ch04_tech_trends/analysis.ipynb',
        'output_dir': 'outputs/ch04_tech_trends',
        'key_artifacts': [
            'yearly_param_stats.csv',
            'tech_trend_lines.png',
            'param_cagr.csv',
            'ch04_report.md',
        ],
    },
    'prompt-05': {
        'name': '销量归因分析',
        'batch': 2,
        'depends': ['prompt-01'],
        'script': 'src/ch05_sales_attribution/analysis.py',
        'notebook': 'src/ch05_sales_attribution/analysis.ipynb',
        'output_dir': 'outputs/ch05_sales_attribution',
        'key_artifacts': [
            'top10_models.csv',
            'best_seller_profile.csv',
            'sales_group_comparison.png',
            'ch05_report.md',
        ],
    },
    'prompt-06': {
        'name': '时序趋势分析',
        'batch': 2,
        'depends': ['prompt-01'],
        'script': 'src/ch06_temporal_trends/analysis.py',
        'notebook': 'src/ch06_temporal_trends/analysis.ipynb',
        'output_dir': 'outputs/ch06_temporal_trends',
        'key_artifacts': [
            'yearly_trends.csv',
            'yearly_trend_chart.png',
            'cagr_table.csv',
            'ch06_report.md',
        ],
    },
    'prompt-07': {
        'name': '竞品对标分析',
        'batch': 2,
        'depends': ['prompt-01'],
        'script': 'src/ch07_competitive_benchmark/analysis.py',
        'notebook': 'src/ch07_competitive_benchmark/analysis.ipynb',
        'output_dir': 'outputs/ch07_competitive_benchmark',
        'key_artifacts': [
            'segment_comparison.csv',
            'value_ranking.csv',
            'competitiveness_radar.png',
            'ch07_report.md',
        ],
    },
    'prompt-08': {
        'name': '量化建模',
        'batch': 3,
        'depends': ['prompt-01'],
        'script': 'src/ch08_quantitative_modeling/analysis.py',
        'notebook': 'src/ch08_quantitative_modeling/analysis.ipynb',
        'output_dir': 'outputs/ch08_quantitative_modeling',
        'key_artifacts': [
            'price_model.pkl',
            'model_metrics.csv',
            'feature_importance.png',
            'prediction_vs_actual.png',
            'clustering_result.csv',
            'ch08_report.md',
        ],
    },
    'prompt-09': {
        'name': '商业决策建议',
        'batch': 3,
        'depends': ['prompt-02', 'prompt-03', 'prompt-04', 'prompt-05', 'prompt-06', 'prompt-07', 'prompt-08'],
        'script': 'src/ch09_business_recommendations/analysis.py',
        'notebook': 'src/ch09_business_recommendations/analysis.ipynb',
        'output_dir': 'outputs/ch09_business_recommendations',
        'key_artifacts': [
            'consumer_advice.md',
            'enterprise_strategy.md',
            'industry_outlook.md',
            'ch09_report.md',
        ],
    },
}

# ============================================================================
# 批次定义（用于并行执行调度）
# ============================================================================

BATCHES = {
    0: {'name': '数据基础', 'tasks': ['prompt-01'], 'parallel': False},
    1: {'name': '核心描述分析', 'tasks': ['prompt-02', 'prompt-03', 'prompt-04'], 'parallel': True},
    2: {'name': '深度诊断分析', 'tasks': ['prompt-05', 'prompt-06', 'prompt-07'], 'parallel': True},
    3: {'name': '建模与总结', 'tasks': ['prompt-08', 'prompt-09'], 'parallel': False},
}
