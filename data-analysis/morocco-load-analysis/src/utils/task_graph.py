"""
任务依赖图模块
定义各 Prompt 之间的依赖关系，提供前置条件检查和进度查询功能。

使用方式:
    from utils.task_graph import TaskGraph

    tg = TaskGraph()
    tg.check_ready('prompt-02')   # 检查 Prompt-02 是否可以启动
    tg.get_status()               # 查看全部任务状态
    tg.get_dispatch_template(1)   # 获取 Batch-1 的派活模板
"""

import os
import glob

# === 任务定义 ===
TASKS = {
    'prompt-01': {
        'name': '数据预处理',
        'batch': 0,
        'depends': [],
        'script': 'src/ch01_preprocessing/preprocess.py',
        'notebook': 'src/ch01_preprocessing/preprocess.ipynb',
        'output_dir': 'outputs/ch01_data_preprocessing',
        'key_artifacts': [
            'ch01_cleaned_data.csv',
            'ch01_feature_engineered_data.csv',
        ],
    },
    'prompt-02': {
        'name': '用电规律挖掘',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'A',
        'script': 'src/ch02_load_pattern/analysis.py',
        'notebook': 'src/ch02_load_pattern/analysis.ipynb',
        'output_dir': 'outputs/ch02_load_pattern_analysis',
        'key_artifacts': [
            'ch02_descriptive_stats.csv',
            'ch02_load_rate_cv.csv',
        ],
    },
    'prompt-03': {
        'name': '峰值识别',
        'batch': 2,
        'depends': ['prompt-02'],
        'branch': 'A',
        'script': 'src/ch03_peak_analysis/peak_detection.py',
        'notebook': 'src/ch03_peak_analysis/peak_detection.ipynb',
        'output_dir': 'outputs/ch03_peak_analysis',
        'key_artifacts': [
            'ch03_peak_thresholds.csv',
            'ch03_peak_events.csv',
            'ch03_peak_duration_stats.csv',
            'ch03_peak_attribution.csv',
            'ch03_anomaly_peak_flags.csv',
        ],
    },
    'prompt-04': {
        'name': '短期负荷预测',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'B',
        'script': 'src/ch04_load_forecasting/forecast.py',
        'notebook': 'src/ch04_load_forecasting/forecast.ipynb',
        'output_dir': 'outputs/ch04_load_forecasting',
        'key_artifacts': [
            'ch04_model_comparison.csv',
        ],
    },
    'prompt-05': {
        'name': '中长期趋势分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'C',
        'script': 'src/ch05_midlong_term_trend/trend_analysis.py',
        'notebook': 'src/ch05_midlong_term_trend/trend_analysis.ipynb',
        'output_dir': 'outputs/ch05_midlong_term_trend',
        'key_artifacts': [
            'ch05_seasonal_strength.csv',
            'ch05_yoy_mom_analysis.csv',
        ],
    },
    'prompt-06': {
        'name': '跨国对比',
        'batch': 3,
        'depends': ['prompt-02', 'prompt-05'],
        'script': 'src/ch06_cross_country/comparison.py',
        'notebook': 'src/ch06_cross_country/comparison.ipynb',
        'output_dir': 'outputs/ch06_cross_country_comparison',
        'key_artifacts': [
            'ch06_benchmark_cleaned.csv',
            'ch06_difference_analysis.md',
        ],
    },
    'prompt-07': {
        'name': '配电网优化',
        'batch': 4,
        'depends': ['prompt-02', 'prompt-03', 'prompt-04', 'prompt-05'],
        'script': 'src/ch07_grid_optimization/optimization.py',
        'notebook': 'src/ch07_grid_optimization/optimization.ipynb',
        'output_dir': 'outputs/ch07_grid_optimization',
        'key_artifacts': [
            'ch07_optimization_metrics.csv',
        ],
    },
    'prompt-08': {
        'name': '总结展望',
        'batch': 5,
        'depends': ['prompt-01', 'prompt-02', 'prompt-03', 'prompt-04',
                    'prompt-05', 'prompt-06', 'prompt-07'],
        'script': 'src/ch08_summary/final_report.py',
        'notebook': 'src/ch08_summary/final_report.ipynb',
        'output_dir': 'outputs/ch08_summary',
        'key_artifacts': [
            'ch08_achievements_summary.md',
        ],
    },
}

# === 批次定义 ===
BATCHES = {
    0: {'name': '串行前置', 'tasks': ['prompt-01'], 'parallel': False},
    1: {'name': '三路并行', 'tasks': ['prompt-02', 'prompt-04', 'prompt-05'], 'parallel': True},
    2: {'name': '支线A续', 'tasks': ['prompt-03'], 'parallel': False},
    3: {'name': '跨国对比', 'tasks': ['prompt-06'], 'parallel': False},
    4: {'name': '配电网优化', 'tasks': ['prompt-07'], 'parallel': False},
    5: {'name': '总结展望', 'tasks': ['prompt-08'], 'parallel': False},
}


class TaskGraph:
    """任务依赖图，提供前置检查和进度查询"""

    def __init__(self, project_root: str = None):
        if project_root is None:
            from utils.config import PROJECT_ROOT
            project_root = PROJECT_ROOT
        self.project_root = project_root

    def _artifact_exists(self, artifact_name: str, task_key: str) -> bool:
        """检查关键产物是否存在"""
        task = TASKS[task_key]
        output_dir = os.path.join(self.project_root, task['output_dir'])
        return os.path.isfile(os.path.join(output_dir, artifact_name))

    def check_ready(self, task_key: str) -> dict:
        """检查某任务是否可以启动

        Returns:
            {'ready': bool, 'missing_deps': [...], 'missing_artifacts': [...]}
        """
        task = TASKS[task_key]
        missing_deps = []
        missing_artifacts = []

        for dep_key in task['depends']:
            dep = TASKS[dep_key]
            # 检查依赖任务的关键产物是否存在
            for artifact in dep['key_artifacts']:
                if not self._artifact_exists(artifact, dep_key):
                    missing_artifacts.append(
                        f"{dep_key}({dep['name']}): {artifact}"
                    )

        ready = len(missing_artifacts) == 0
        return {
            'ready': ready,
            'task': task_key,
            'name': task['name'],
            'batch': task['batch'],
            'missing_deps': missing_deps,
            'missing_artifacts': missing_artifacts,
        }

    def get_status(self) -> list:
        """查看全部任务状态"""
        results = []
        for task_key in TASKS:
            task = TASKS[task_key]
            if not task['key_artifacts']:
                results.append({
                    'task': task_key, 'name': task['name'],
                    'batch': task['batch'], 'status': '待开发',
                })
                continue

            exists_count = sum(
                1 for a in task['key_artifacts']
                if self._artifact_exists(a, task_key)
            )
            total = len(task['key_artifacts'])

            if exists_count == total:
                status = '✅ 已完成'
            elif exists_count > 0:
                status = f'🔄 进行中 ({exists_count}/{total})'
            else:
                status = '⬜ 未开始'

            results.append({
                'task': task_key, 'name': task['name'],
                'batch': task['batch'], 'status': status,
            })
        return results

    def get_current_batch(self) -> int:
        """根据产物存在情况推断当前应执行的批次"""
        for batch_num in sorted(BATCHES.keys()):
            batch = BATCHES[batch_num]
            for task_key in batch['tasks']:
                task = TASKS[task_key]
                all_exist = all(
                    self._artifact_exists(a, task_key)
                    for a in task['key_artifacts']
                )
                if not all_exist:
                    return batch_num
        return max(BATCHES.keys()) + 1  # 全部完成

    def print_status(self):
        """打印进度总览"""
        current = self.get_current_batch()
        print(f'当前应执行批次: Batch-{current}')
        print('=' * 60)

        for batch_num in sorted(BATCHES.keys()):
            batch = BATCHES[batch_num]
            marker = '▶' if batch_num == current else ' '
            parallel = ' [并行]' if batch['parallel'] else ''
            print(f'{marker} Batch-{batch_num}: {batch["name"]}{parallel}')

            for task_key in batch['tasks']:
                task = TASKS[task_key]
                exists_count = sum(
                    1 for a in task['key_artifacts']
                    if self._artifact_exists(a, task_key)
                )
                total = len(task['key_artifacts'])
                status = '✅' if exists_count == total else '⬜'
                branch = f" (支线{task.get('branch', '')})" if 'branch' in task else ''
                print(f'    {status} {task_key}: {task["name"]}{branch} '
                      f'[{exists_count}/{total}]')

        print('=' * 60)


# === CLI 入口 ===
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tg = TaskGraph()
    tg.print_status()
