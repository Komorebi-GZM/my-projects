#!/usr/bin/env python3
"""ch06 可视化看板与总结报告 — 产物验证测试.

运行方式:
    python src/ch06_dashboard_summary/test_ch06.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import get_chapter_output_dir

OUTPUT_DIR = get_chapter_output_dir("ch06_dashboard_summary")
SRC_DIR_CH06 = Path(__file__).resolve().parent


def test_output_dir_exists() -> None:
    assert OUTPUT_DIR.exists(), f"输出目录不存在: {OUTPUT_DIR}"
    print(f"  [PASS] 输出目录存在")


def test_dashboard_py_exists() -> None:
    fpath = SRC_DIR_CH06 / "dashboard.py"
    assert fpath.exists(), "dashboard.py 不存在"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "dashboard.py 内容过短"
    assert "streamlit" in content, "dashboard.py 未使用 streamlit"
    assert "st." in content, "dashboard.py 缺少 streamlit 调用"
    print(f"  [PASS] dashboard.py: {len(content)} 字符, 包含 streamlit")


def test_comprehensive_report() -> None:
    import pandas as pd
    fpath = OUTPUT_DIR / "ch06_comprehensive_report.md"
    assert fpath.exists(), "综合报告不存在"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 1000, f"综合报告内容过短: {len(content)}"
    # 检查覆盖了全部章节
    chapters = ["ch01", "ch02", "ch03", "ch04", "ch05"]
    found = [c for c in chapters if c in content]
    assert len(found) >= 4, f"报告未覆盖足够章节: {found}"
    print(f"  [PASS] 综合报告: {len(content)} 字符, 覆盖章节: {found}")


def test_key_metrics_csv() -> None:
    import pandas as pd
    fpath = OUTPUT_DIR / "ch06_key_metrics_table.csv"
    assert fpath.exists(), "关键指标表不存在"
    df = pd.read_csv(fpath)
    assert len(df) > 0, "关键指标表为空"
    assert "metric" in df.columns or "Metric" in df.columns or "chapter" in df.columns, \
        f"缺少关键列, 现有列: {list(df.columns)}"
    print(f"  [PASS] 关键指标表: {len(df)} 行")


def test_all_ch06_prefix() -> None:
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            assert f.name.startswith("ch06_"), f"命名不规范: {f.name}"
    print(f"  [PASS] 所有产物以 ch06_ 开头")


def test_total_deliverables() -> None:
    all_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file()]
    assert len(all_files) >= 2, f"产物不足: {len(all_files)} < 2"
    print(f"  [PASS] 产物总数: {len(all_files)} >= 2")


def main() -> None:
    print("=" * 60)
    print("ch06 可视化看板与总结报告 — 产物验证测试")
    print("=" * 60)

    tests = [
        test_output_dir_exists,
        test_dashboard_py_exists,
        test_comprehensive_report,
        test_key_metrics_csv,
        test_all_ch06_prefix,
        test_total_deliverables,
    ]

    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {e}")
            failed += 1

    print()
    print(f"结果: {passed} PASSED, {failed} FAILED")
    print(f"状态: {'GREEN' if failed == 0 else 'RED'}")


if __name__ == "__main__":
    main()
