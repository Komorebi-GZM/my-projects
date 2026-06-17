"""
Genesis_Anomaly_Analysis - 任务依赖图管理模块
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import PROJECT_ROOT


class TaskGraph:
    """任务依赖图管理器"""
    
    # 章节依赖关系定义
    DEPENDENCIES = {
        'ch01': [],
        'ch02': ['ch01'],
        'ch03': ['ch02'],
        'ch04': ['ch01'],
        'ch05': ['ch03', 'ch04'],
    }
    
    # 执行批次
    BATCHES = [
        ['ch01'],           # Batch 1
        ['ch02', 'ch04'],   # Batch 2
        ['ch03'],           # Batch 3
        ['ch05'],           # Batch 4
    ]
    
    def __init__(self, status_file: Optional[str] = None):
        """
        初始化任务图
        
        Args:
            status_file: 状态文件路径（可选）
        """
        self.status_file = status_file or (PROJECT_ROOT / '.task_status.json')
        self.status = self._load_status()
    
    def _load_status(self) -> Dict[str, str]:
        """加载任务状态"""
        if self.status_file.exists():
            return json.loads(self.status_file.read_text())
        return {ch: 'pending' for ch in self.DEPENDENCIES.keys()}
    
    def _save_status(self):
        """保存任务状态"""
        self.status_file.write_text(json.dumps(self.status, indent=2))
    
    def get_dependencies(self, chapter_id: str) -> List[str]:
        """
        获取章节的前置依赖
        
        Args:
            chapter_id: 章节ID
        
        Returns:
            依赖列表
        """
        return self.DEPENDENCIES.get(chapter_id, [])
    
    def check_dependencies(self, chapter_id: str) -> bool:
        """
        检查前置依赖是否已完成
        
        Args:
            chapter_id: 章节ID
        
        Returns:
            是否满足依赖
        """
        deps = self.get_dependencies(chapter_id)
        return all(self.status.get(dep) == 'completed' for dep in deps)
    
    def update_status(self, chapter_id: str, status: str):
        """
        更新任务状态
        
        Args:
            chapter_id: 章节ID
            status: 状态 ('pending', 'running', 'completed', 'failed')
        """
        self.status[chapter_id] = status
        self._save_status()
    
    def get_status(self, chapter_id: Optional[str] = None) -> Dict:
        """
        获取任务状态
        
        Args:
            chapter_id: 章节ID（None 则返回全部）
        
        Returns:
            状态字典
        """
        if chapter_id:
            return {chapter_id: self.status.get(chapter_id, 'pending')}
        return self.status.copy()
    
    def get_ready_tasks(self) -> List[str]:
        """
        获取当前可执行的任务（依赖已满足且状态为 pending）
        
        Returns:
            可执行章节列表
        """
        ready = []
        for ch in self.DEPENDENCIES.keys():
            if self.status.get(ch) == 'pending' and self.check_dependencies(ch):
                ready.append(ch)
        return ready
    
    def get_batch_for_chapter(self, chapter_id: str) -> int:
        """
        获取章节所属批次
        
        Args:
            chapter_id: 章节ID
        
        Returns:
            批次号（1-based）
        """
        for i, batch in enumerate(self.BATCHES, 1):
            if chapter_id in batch:
                return i
        return 0
    
    def print_status(self):
        """打印格式化的进度表格"""
        print("\n" + "="*60)
        print("任务执行状态")
        print("="*60)
        print(f"{'章节':<10} {'批次':<8} {'状态':<12} {'依赖满足':<10}")
        print("-"*60)
        
        for ch in self.DEPENDENCIES.keys():
            batch = self.get_batch_for_chapter(ch)
            status = self.status.get(ch, 'pending')
            deps_ok = '✓' if self.check_dependencies(ch) else '✗'
            print(f"{ch:<10} {batch:<8} {status:<12} {deps_ok:<10}")
        
        print("="*60)
        completed = sum(1 for s in self.status.values() if s == 'completed')
        total = len(self.status)
        print(f"进度: {completed}/{total} ({completed/total*100:.1f}%)")
        print("="*60 + "\n")
    
    def get_execution_order(self) -> List[List[str]]:
        """
        获取按批次划分的执行顺序
        
        Returns:
            批次列表，每批包含可并行执行的章节
        """
        return self.BATCHES.copy()


def print_execution_plan():
    """打印执行计划"""
    graph = TaskGraph()
    batches = graph.get_execution_order()
    
    print("\n" + "="*60)
    print("Genesis_Anomaly_Analysis 执行计划")
    print("="*60)
    
    for i, batch in enumerate(batches, 1):
        print(f"\n批次 {i}: {' → '.join(batch)}")
        for ch in batch:
            deps = graph.get_dependencies(ch)
            if deps:
                print(f"  - {ch} (依赖: {', '.join(deps)})")
            else:
                print(f"  - {ch} (无依赖)")
    
    print("\n" + "="*60)
    print("执行命令示例:")
    print("  python src/ch01_data_overview_and_cleaning/script.py")
    print("="*60 + "\n")
