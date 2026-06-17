#!/usr/bin/env python3
"""ch04 特征工程 — 产物验证测试.

TDD-RED 阶段：定义 ch04 全部产物的验证条件。
测试通过 = GREEN，测试失败 = RED。

运行方式:
    python src/ch04_feature_engineering/test_ch04.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 路径设置
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import get_chapter_output_dir

OUTPUT_DIR = get_chapter_output_dir("ch04_feature_engineering")

# 预期产物清单
EXPECTED_CSV_FILES = [
    "ch04_engineered_features.csv",
    "ch04_feature_importance.csv",
]

EXPECTED_PNG_FILES = [
    "ch04_correlation_heatmap.png",
    "ch04_feature_distribution.png",
]

EXPECTED_MD_FILES = [
    "ch04_feature_engineering_report.md",
]

ALL_EXPECTED = EXPECTED_CSV_FILES + EXPECTED_PNG_FILES + EXPECTED_MD_FILES


def test_output_dir_exists() -> None:
    """验证 ch04 输出目录存在."""
    assert OUTPUT_DIR.exists(), f"输出目录不存在: {OUTPUT_DIR}"
    print(f"  [PASS] 输出目录存在: {OUTPUT_DIR}")


def test_feature_csv_exists() -> None:
    """验证特征工程 CSV 存在且内容正确."""
    import pandas as pd
    fpath = OUTPUT_DIR / "ch04_engineered_features.csv"
    assert fpath.exists(), "特征文件不存在: ch04_engineered_features.csv"
    df = pd.read_csv(fpath)
    assert len(df) > 0, "特征数据为空"
    # 验证特征数量 >= 30
    feature_cols = [c for c in df.columns if c != 'date']
    assert len(feature_cols) >= 30, f"特征数量不足: {len(feature_cols)} < 30"
    # 验证无缺失值
    assert df.isnull().sum().sum() == 0, "特征数据包含缺失值"
    print(f"  [PASS] 特征数据: {len(df)} 行 x {len(feature_cols)} 列, 无缺失值")


def test_feature_importance_csv() -> None:
    """验证特征重要性 CSV 存在."""
    import pandas as pd
    fpath = OUTPUT_DIR / "ch04_feature_importance.csv"
    assert fpath.exists(), "特征重要性文件不存在"
    df = pd.read_csv(fpath)
    assert len(df) > 0, "特征重要性数据为空"
    assert 'feature' in df.columns and 'importance' in df.columns, "缺少必需列"
    print(f"  [PASS] 特征重要性: {len(df)} 个特征")


def test_correlation_heatmap() -> None:
    """验证相关性热力图存在且 DPI 达标."""
    from PIL import Image
    fpath = OUTPUT_DIR / "ch04_correlation_heatmap.png"
    assert fpath.exists(), "相关性热力图不存在"
    with Image.open(fpath) as img:
        dpi = img.info.get("dpi", (0, 0))
        assert dpi[0] >= 150, f"DPI 不足: {dpi[0]} < 150"
    print(f"  [PASS] 相关性热力图: DPI {dpi[0]} >= 150")


def test_feature_distribution() -> None:
    """验证特征分布图存在."""
    from PIL import Image
    fpath = OUTPUT_DIR / "ch04_feature_distribution.png"
    assert fpath.exists(), "特征分布图不存在"
    with Image.open(fpath) as img:
        dpi = img.info.get("dpi", (0, 0))
        assert dpi[0] >= 150, f"DPI 不足: {dpi[0]} < 150"
    print(f"  [PASS] 特征分布图: DPI {dpi[0]} >= 150")


def test_report_exists() -> None:
    """验证特征工程报告存在且内容完整."""
    fpath = OUTPUT_DIR / "ch04_feature_engineering_report.md"
    assert fpath.exists(), "报告文件不存在"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "报告内容过短"
    keywords = ["feature", "Feature", "correlation", "VIF", "importance"]
    found = [kw for kw in keywords if kw in content]
    assert len(found) >= 2, f"报告缺少关键内容，仅找到: {found}"
    print(f"  [PASS] 特征工程报告: {len(content)} 字符")


def test_all_files_ch04_prefix() -> None:
    """验证所有产物文件以 ch04_ 开头."""
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            assert f.name.startswith("ch04_"), f"文件命名不符合规范: {f.name}"
    print(f"  [PASS] 所有产物文件以 ch04_ 开头")


def test_total_deliverables() -> None:
    """验证产物总数 >= 5."""
    all_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file()]
    assert len(all_files) >= 5, f"产物总数不足: {len(all_files)} < 5"
    print(f"  [PASS] 产物总数: {len(all_files)} >= 5")


def main() -> None:
    """运行全部测试."""
    print("=" * 60)
    print("ch04 特征工程 — 产物验证测试 (TDD-RED)")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"预期产物: {len(ALL_EXPECTED)} 个")
    print()

    tests = [
        test_output_dir_exists,
        test_feature_csv_exists,
        test_feature_importance_csv,
        test_correlation_heatmap,
        test_feature_distribution,
        test_report_exists,
        test_all_files_ch04_prefix,
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
