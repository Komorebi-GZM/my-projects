#!/usr/bin/env python3
"""ch02 描述性统计分析 — 产物验证测试.

TDD-RED 阶段：定义 ch02 全部产物的验证条件。
测试通过 = GREEN，测试失败 = RED。

运行方式:
    python src/ch02_descriptive_stats/test_ch02.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 路径设置
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import get_chapter_output_dir

OUTPUT_DIR = get_chapter_output_dir("ch02_descriptive_stats")

# 预期产物清单（依据 flow_design.md 3.5 节 + execution_prompts.md Prompt-02）
EXPECTED_PNG_FILES = [
    "ch02_time_distribution.png",
    "ch02_category_ranking.png",
    "ch02_impact_tier_analysis.png",
    "ch02_top50_keywords.png",
    "ch02_keyword_wordcloud.png",
    "ch02_source_bias_analysis.png",
    "ch02_text_length_and_cross.png",
    "ch02_category_yearly_trend.png",
]

EXPECTED_CSV_FILES = [
    "ch02_descriptive_stats.csv",
]

EXPECTED_MD_FILES = [
    "ch02_descriptive_stats_report.md",
]

ALL_EXPECTED = EXPECTED_PNG_FILES + EXPECTED_CSV_FILES + EXPECTED_MD_FILES


def test_output_dir_exists() -> None:
    """验证 ch02 输出目录存在."""
    assert OUTPUT_DIR.exists(), f"输出目录不存在: {OUTPUT_DIR}"
    print(f"  [PASS] 输出目录存在: {OUTPUT_DIR}")


def test_png_count() -> None:
    """验证 PNG 图表数量 >= 8."""
    png_files = list(OUTPUT_DIR.glob("ch02_*.png"))
    assert len(png_files) >= 8, f"PNG 图表数量不足: {len(png_files)} >= 8"
    print(f"  [PASS] PNG 图表数量: {len(png_files)} >= 8")


def test_png_dpi() -> None:
    """验证 PNG 图片 DPI >= 150."""
    from PIL import Image
    for fname in EXPECTED_PNG_FILES:
        fpath = OUTPUT_DIR / fname
        if fpath.exists():
            with Image.open(fpath) as img:
                dpi = img.info.get("dpi", (0, 0))
                assert dpi[0] >= 150, f"{fname} DPI 不足: {dpi[0]} < 150"
            print(f"  [PASS] {fname} DPI: {dpi[0]} >= 150")
        else:
            print(f"  [SKIP] {fname} 不存在（尚未生成）")


def test_csv_files_exist() -> None:
    """验证 CSV 数据文件存在."""
    for fname in EXPECTED_CSV_FILES:
        fpath = OUTPUT_DIR / fname
        assert fpath.exists(), f"CSV 文件不存在: {fname}"
        print(f"  [PASS] {fname} 存在")


def test_csv_content() -> None:
    """验证描述统计汇总表内容."""
    import pandas as pd
    fpath = OUTPUT_DIR / "ch02_descriptive_stats.csv"
    if fpath.exists():
        df = pd.read_csv(fpath)
        assert len(df) > 0, "描述统计汇总表为空"
        print(f"  [PASS] 描述统计汇总表: {len(df)} 行")
    else:
        print(f"  [SKIP] ch02_descriptive_stats.csv 不存在")


def test_report_exists() -> None:
    """验证描述性统计报告存在且非空."""
    fpath = OUTPUT_DIR / "ch02_descriptive_stats_report.md"
    assert fpath.exists(), "报告文件不存在: ch02_descriptive_stats_report.md"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "报告内容过短"
    # 检查报告包含关键章节（英文报告检查英文关键词）
    assert ("Time" in content or "time" in content or "Distribution" in content
            or "Category" in content or "分布" in content), "报告缺少关键分析维度"
    print(f"  [PASS] 报告存在且内容完整 ({len(content)} 字符)")


def test_all_files_ch02_prefix() -> None:
    """验证所有产物文件以 ch02_ 开头."""
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            assert f.name.startswith("ch02_"), \
                f"文件命名不符合规范: {f.name}（缺少 ch02_ 前缀）"
    print(f"  [PASS] 所有产物文件以 ch02_ 开头")


def test_total_deliverables() -> None:
    """验证产物总数 >= 10（8 PNG + 1 CSV + 1 MD）."""
    all_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file()]
    assert len(all_files) >= 10, f"产物总数不足: {len(all_files)} >= 10"
    print(f"  [PASS] 产物总数: {len(all_files)} >= 10")


def main() -> None:
    """运行全部测试."""
    print("=" * 60)
    print("ch02 描述性统计分析 — 产物验证测试 (TDD-RED)")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"预期产物: {len(ALL_EXPECTED)} 个")
    print()

    tests = [
        test_output_dir_exists,
        test_png_count,
        test_png_dpi,
        test_csv_files_exist,
        test_csv_content,
        test_report_exists,
        test_all_files_ch02_prefix,
        test_total_deliverables,
    ]

    passed = 0
    failed = 0
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
    print("=" * 60)
    print(f"测试结果: {passed} PASSED, {failed} FAILED")
    if failed == 0:
        print("状态: GREEN — 全部测试通过")
    else:
        print("状态: RED — 存在失败测试")
    print("=" * 60)


if __name__ == "__main__":
    main()
