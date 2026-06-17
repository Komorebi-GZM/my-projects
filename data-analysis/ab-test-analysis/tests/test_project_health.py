"""
项目前置问题验证测试
TDD RED 阶段：验证修复前的行为，所有测试应先失败再通过
"""

import os
import sys
import ast
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestResult:
    """简单测试结果记录器"""
    def __init__(self):
        self.passed = []
        self.failed = []

    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            self.passed.append(name)
            print(f"  ✓ {name}")
        else:
            self.failed.append((name, detail))
            print(f"  ✗ {name} — {detail}")

    def summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{'='*60}")
        print(f"测试结果: {len(self.passed)}/{total} 通过")
        if self.failed:
            print(f"\n失败项:")
            for name, detail in self.failed:
                print(f"  ✗ {name}: {detail}")
        return len(self.failed) == 0


def test_s1_init_py_package_export(tr: TestResult):
    """S1: __init__.py 应作为正确的包导出文件"""
    print("\n[S1] __init__.py 包导出检查")

    init_path = os.path.join(PROJECT_ROOT, "src", "utils", "__init__.py")
    config_path = os.path.join(PROJECT_ROOT, "src", "utils", "config.py")

    # 检查 __init__.py 不应包含完整的配置常量定义
    with open(init_path, "r") as f:
        init_content = f.read()

    with open(config_path, "r") as f:
        config_content = f.read()

    # __init__.py 不应定义 PROJECT_ROOT 等常量（那是 config.py 的职责）
    has_project_root = "PROJECT_ROOT = Path" in init_content
    tr.check("__init__.py 不重复定义 PROJECT_ROOT", not has_project_root,
             "__init__.py 不应包含配置常量定义")

    # __init__.py 应有导入语句（从子模块导入公共接口）
    has_import = "from ." in init_content or "import " in init_content
    tr.check("__init__.py 包含导入语句", has_import,
             "应从子模块导入公共接口")

    # __init__.py 不应与 config.py 内容高度重复
    similarity = len(set(init_content.split()) & set(config_content.split())) / max(len(set(config_content.split())), 1)
    tr.check("__init__.py 与 config.py 不高度重复", similarity < 0.5,
             f"相似度 {similarity:.1%}，疑似重复内容")


def test_s2_no_root_data_files(tr: TestResult):
    """S2: 项目根目录不应散落数据文件"""
    print("\n[S2] 根目录数据文件检查")

    # 检查根目录下不应有 .csv/.xlsx/.json 数据文件
    data_extensions = {".csv", ".xlsx", ".xls", ".parquet", ".json"}
    root_files = os.listdir(PROJECT_ROOT)

    scattered = [f for f in root_files if os.path.splitext(f)[1].lower() in data_extensions]
    # 排除 project_params.json（这是配置文件，不是数据文件）
    scattered = [f for f in scattered if f != "project_params.json"]

    tr.check("根目录无散落数据文件", len(scattered) == 0,
             f"发现散落文件: {scattered}")


def test_m1_readme_exists(tr: TestResult):
    """M1: README.md 应存在"""
    print("\n[M1] README.md 检查")

    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    exists = os.path.exists(readme_path)
    tr.check("README.md 存在", exists, "project_convention.md 中列出了 README.md")

    if exists:
        with open(readme_path, "r") as f:
            content = f.read()
        tr.check("README.md 非空", len(content) > 50, "README 内容过少")


def test_m2_no_unused_imports_ch01(tr: TestResult):
    """M2: ch01 不应有未使用的导入"""
    print("\n[M2] ch01 冗余导入检查")

    ch01_path = os.path.join(PROJECT_ROOT, "src", "ch01_data_cleaning", "run.py")
    with open(ch01_path, "r") as f:
        content = f.read()

    # 检查 Visualizer 是否被导入
    visualizer_imported = "from src.utils.visualizer import Visualizer" in content
    tr.check("ch01 未导入未使用的 Visualizer", not visualizer_imported,
             "Visualizer 不应被导入（ch01 不需要可视化）")


def test_m3_ch05_na_formatting(tr: TestResult):
    """M3: ch05 报告模板应安全处理 N/A 值"""
    print("\n[M3] ch05 N/A 格式化安全检查")

    ch05_path = os.path.join(PROJECT_ROOT, "src", "ch05_conclusion_recommendation", "run.py")
    with open(ch05_path, "r") as f:
        content = f.read()

    # 检查是否有不安全的格式化模式
    # 危险模式: f"{some_dict.get('key', 'N/A'):.4f}"
    dangerous_patterns = [
        r"\.get\([^)]+,\s*['\"]N/A['\"]\)[^}]*\.[\d]+[f%]",
        r"\.get\([^)]+,\s*['\"]N/A['\"]\)[^}]*format",
    ]

    has_dangerous = False
    for pattern in dangerous_patterns:
        if re.search(pattern, content):
            has_dangerous = True
            break

    tr.check("ch05 无不安全的 N/A 格式化", not has_dangerous,
             "发现可能抛出 TypeError 的格式化代码")


def test_l2_no_bare_except(tr: TestResult):
    """L2: 不应有裸 except 子句"""
    print("\n[L2] 裸 except 检查")

    # 检查所有章节脚本
    ch_dirs = [
        "ch03_hypothesis_testing",
        "ch05_conclusion_recommendation",
    ]

    for ch_dir in ch_dirs:
        script_path = os.path.join(PROJECT_ROOT, "src", ch_dir, "run.py")
        if not os.path.exists(script_path):
            continue

        with open(script_path, "r") as f:
            content = f.read()

        # 查找裸 except（不跟异常类型）
        bare_excepts = re.findall(r"except\s*:", content)
        tr.check(f"{ch_dir} 无裸 except", len(bare_excepts) == 0,
                 f"发现 {len(bare_excepts)} 个裸 except 子句")


def test_docs_completeness(tr: TestResult):
    """文档完整性检查"""
    print("\n[DOCS] 文档完整性检查")

    expected_docs = [
        "docs/project_convention.md",
        "docs/analysis_goals.md",
        "docs/flow_design.md",
        "docs/execution_prompts.md",
        "docs/task_dispatch_guide.md",
        "project_params.json",
    ]

    for doc in expected_docs:
        path = os.path.join(PROJECT_ROOT, doc)
        exists = os.path.exists(path)
        tr.check(f"{doc} 存在", exists, "文档缺失")


def test_utils_modules(tr: TestResult):
    """工具模块完整性检查"""
    print("\n[UTILS] 工具模块检查")

    expected_modules = [
        "src/utils/__init__.py",
        "src/utils/config.py",
        "src/utils/data_loader.py",
        "src/utils/visualizer.py",
        "src/utils/metrics.py",
        "src/utils/output_manager.py",
        "src/utils/task_graph.py",
    ]

    for mod in expected_modules:
        path = os.path.join(PROJECT_ROOT, mod)
        exists = os.path.exists(path)
        tr.check(f"{mod} 存在", exists, "模块缺失")


def test_chapter_scripts(tr: TestResult):
    """章节脚本完整性检查"""
    print("\n[CHAPTERS] 章节脚本检查")

    expected_scripts = [
        "src/ch01_data_cleaning/run.py",
        "src/ch02_metrics_visualization/run.py",
        "src/ch03_hypothesis_testing/run.py",
        "src/ch04_time_trend_analysis/run.py",
        "src/ch05_conclusion_recommendation/run.py",
    ]

    for script in expected_scripts:
        path = os.path.join(PROJECT_ROOT, script)
        exists = os.path.exists(path)
        tr.check(f"{script} 存在", exists, "脚本缺失")


def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + "  AB_Test_Analysis 前置问题验证测试".center(46) + "║")
    print("╚" + "═" * 58 + "╝")

    tr = TestResult()

    # 严重问题测试
    test_s1_init_py_package_export(tr)
    test_s2_no_root_data_files(tr)

    # 中等问题测试
    test_m1_readme_exists(tr)
    test_m2_no_unused_imports_ch01(tr)
    test_m3_ch05_na_formatting(tr)

    # 轻微问题测试
    test_l2_no_bare_except(tr)

    # 完整性测试
    test_docs_completeness(tr)
    test_utils_modules(tr)
    test_chapter_scripts(tr)

    all_passed = tr.summary()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
