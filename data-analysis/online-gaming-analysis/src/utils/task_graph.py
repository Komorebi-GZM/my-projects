"""
任务依赖图模块
定义各 Prompt 之间的依赖关系，提供前置条件检查和进度查询功能。

使用方式:
    from utils.task_graph import TaskGraph

    tg = TaskGraph()
    tg.check_ready('prompt-01')   # 检查是否可以启动
    tg.get_status()               # 查看全部任务状态
    tg.print_status()             # 打印进度总览
"""

import os

# === 任务定义 ===
TASKS = {
    'prompt-01': {
        'name': '数据清洗',
        'batch': 0,
        'depends': [],
        'script': 'src/ch01_data_cleaning/clean.py',
        'notebook': 'src/ch01_data_cleaning/clean.ipynb',
        'output_dir': 'outputs/ch01_data_cleaning',
        'key_artifacts': [
            'ch01_cleaned_online_gaming.csv',
            'ch01_cleaning_report.md',
        ],
    },
    'prompt-02': {
        'name': '热度分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch02_popularity_analysis/analysis.py',
        'notebook': 'src/ch02_popularity_analysis/analysis.ipynb',
        'output_dir': 'outputs/ch02_popularity_analysis',
        'key_artifacts': [
            'ch02_popularity_stats.csv',
            'ch02_popularity_analysis_report.md',
        ],
    },
    'prompt-03': {
        'name': '标签分析',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch03_tag_analysis/analysis.py',
        'notebook': 'src/ch03_tag_analysis/analysis.ipynb',
        'output_dir': 'outputs/ch03_tag_analysis',
        'key_artifacts': [
            'ch03_tag_frequency.csv',
            'ch03_tag_analysis_report.md',
        ],
    },
    'prompt-04': {
        'name': '跨平台对比',
        'batch': 1,
        'depends': ['prompt-01'],
        'script': 'src/ch04_cross_platform/analysis.py',
        'notebook': 'src/ch04_cross_platform/analysis.ipynb',
        'output_dir': 'outputs/ch04_cross_platform',
        'key_artifacts': [
            'ch04_platform_comparison.csv',
            'ch04_platform_analysis_report.md',
        ],
    },
    'prompt-05': {
        'name': '可视化报告',
        'batch': 2,
        'depends': ['prompt-02', 'prompt-03', 'prompt-04'],
        'script': 'src/ch05_visualization/report.py',
        'notebook': 'src/ch05_visualization/report.ipynb',
        'output_dir': 'outputs/ch05_visualization',
        'key_artifacts': [
            'ch05_summary_report.md',
        ],
    },
}

# === 批次定义 ===
BATCHES = {
    0: {'name': '数据清洗（串行前置）', 'tasks': ['prompt-01'], 'parallel': False},
    1: {'name': '分析章节（可并行）', 'tasks': ['prompt-02', 'prompt-03', 'prompt-04'], 'parallel': True},
    2: {'name': '可视化报告（串行收束）', 'tasks': ['prompt-05'], 'parallel': False},
}


class TaskGraph:
    """任务依赖图，提供前置检查和进度查询"""

    def __init__(self, project_root=None):
        if project_root is None:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from utils.config import PROJECT_ROOT
            project_root = PROJECT_ROOT
        self.project_root = project_root

    def _artifact_exists(self, artifact_name, task_key):
        """检查关键产物是否存在"""
        task = TASKS[task_key]
        output_dir = os.path.join(self.project_root, task['output_dir'])
        return os.path.isfile(os.path.join(output_dir, artifact_name))

    def check_ready(self, task_key):
        """检查某任务是否可以启动

        Returns:
            {'ready': bool, 'missing_artifacts': [...]}
        """
        task = TASKS[task_key]
        missing_artifacts = []

        for dep_key in task['depends']:
            dep = TASKS[dep_key]
            for artifact in dep['key_artifacts']:
                if not self._artifact_exists(artifact, dep_key):
                    missing_artifacts.append(
                        f"{dep_key}({dep['name']}): {artifact}"
                    )

        return {
            'ready': len(missing_artifacts) == 0,
            'task': task_key,
            'name': task['name'],
            'batch': task['batch'],
            'missing_artifacts': missing_artifacts,
        }

    def get_status(self):
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
                status = '已完成'
            elif exists_count > 0:
                status = f'进行中 ({exists_count}/{total})'
            else:
                status = '未开始'

            results.append({
                'task': task_key, 'name': task['name'],
                'batch': task['batch'], 'status': status,
            })
        return results

    def get_current_batch(self):
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
        return max(BATCHES.keys()) + 1

    def print_status(self):
        """打印进度总览"""
        print()
        print("=" * 60)
        print("  在线小游戏数据分析 — 任务进度")
        print("=" * 60)

        for batch_num in sorted(BATCHES.keys()):
            batch = BATCHES[batch_num]
            print(f"\n  Batch-{batch_num}: {batch['name']}")
            if batch['parallel']:
                print("  (可并行执行)")
            print(f"  {'任务':<16s} {'名称':<16s} {'状态':<16s}")
            print("  " + "-" * 50)
            for task_key in batch['tasks']:
                task = TASKS[task_key]
                status_info = self.get_status()
                status = next(
                    (s['status'] for s in status_info if s['task'] == task_key),
                    '未知'
                )
                print(f"  {task_key:<16s} {task['name']:<16s} {status:<16s}")

        current = self.get_current_batch()
        total = len(BATCHES)
        if current > max(BATCHES.keys()):
            print(f"\n  全部 {total} 个批次已完成!")
        else:
            print(f"\n  当前应执行: Batch-{current}")

        print("=" * 60)
        print()


if __name__ == '__main__':
    TaskGraph().print_status()
