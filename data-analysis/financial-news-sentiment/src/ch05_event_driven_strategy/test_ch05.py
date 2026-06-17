#!/usr/bin/env python3
"""ch05 事件驱动策略分析 — 产物验证测试.

TDD-RED 阶段：定义 ch05 全部产物的验证条件。

运行方式:
    python src/ch05_event_driven_strategy/test_ch05.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import get_chapter_output_dir

OUTPUT_DIR = get_chapter_output_dir("ch05_event_driven_strategy")

EXPECTED_CSV = [
    "ch05_event_calendar.csv",
    "ch05_influence_score.csv",
]

EXPECTED_PNG = [
    "ch05_event_analysis.png",
]

EXPECTED_MD = [
    "ch05_event_analysis_report.md",
]

ALL_EXPECTED = EXPECTED_CSV + EXPECTED_PNG + EXPECTED_MD


def test_output_dir_exists() -> None:
    assert OUTPUT_DIR.exists(), f"输出目录不存在: {OUTPUT_DIR}"
    print(f"  [PASS] 输出目录存在")


def test_event_calendar_csv() -> None:
    import pandas as pd
    fpath = OUTPUT_DIR / "ch05_event_calendar.csv"
    assert fpath.exists(), "事件日历不存在"
    df = pd.read_csv(fpath)
    assert len(df) >= 10, f"高影响力事件不足: {len(df)} < 10"
    required = {"date", "title", "event_type", "influence_score"}
    assert required.issubset(set(df.columns)), f"缺少列: {required - set(df.columns)}"
    # 影响力评分不全相同
    assert df["influence_score"].nunique() > 1, "影响力评分分布不合理（全部相同）"
    print(f"  [PASS] 事件日历: {len(df)} 个事件, 评分分布合理")


def test_influence_score_csv() -> None:
    import pandas as pd
    fpath = OUTPUT_DIR / "ch05_influence_score.csv"
    assert fpath.exists(), "影响力评分表不存在"
    df = pd.read_csv(fpath)
    assert len(df) >= 10, f"影响力评分行数不足: {len(df)}"
    assert "influence_score" in df.columns, "缺少 influence_score 列"
    # 按影响力降序排列
    scores = df["influence_score"].values
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), "未按影响力降序排列"
    print(f"  [PASS] 影响力评分: {len(df)} 行, 已降序排列")


def test_event_analysis_png() -> None:
    from PIL import Image
    fpath = OUTPUT_DIR / "ch05_event_analysis.png"
    assert fpath.exists(), "事件分析图不存在"
    with Image.open(fpath) as img:
        dpi = img.info.get("dpi", (0, 0))
        assert dpi[0] >= 150, f"DPI 不足: {dpi[0]}"
    print(f"  [PASS] 事件分析图: DPI {dpi[0]}")


def test_report() -> None:
    fpath = OUTPUT_DIR / "ch05_event_analysis_report.md"
    assert fpath.exists(), "报告不存在"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "报告内容过短"
    keywords = ["event", "Event", "influence", "sentiment", "impact"]
    found = [kw for kw in keywords if kw in content]
    assert len(found) >= 2, f"报告缺少关键内容: {found}"
    print(f"  [PASS] 报告: {len(content)} 字符")


def test_event_type_coverage() -> None:
    import pandas as pd
    fpath = OUTPUT_DIR / "ch05_event_calendar.csv"
    if not fpath.exists():
        return
    df = pd.read_csv(fpath)
    types = df["event_type"].nunique()
    assert types >= 3, f"事件类型覆盖不足: {types} < 3"
    print(f"  [PASS] 事件类型覆盖: {types} 种")


def test_all_ch05_prefix() -> None:
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            assert f.name.startswith("ch05_"), f"命名不规范: {f.name}"
    print(f"  [PASS] 所有文件以 ch05_ 开头")


def test_total_deliverables() -> None:
    all_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file()]
    assert len(all_files) >= 4, f"产物不足: {len(all_files)} < 4"
    print(f"  [PASS] 产物总数: {len(all_files)} >= 4")


def main() -> None:
    print("=" * 60)
    print("ch05 事件驱动策略分析 — 产物验证测试 (TDD-RED)")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    tests = [
        test_output_dir_exists,
        test_event_calendar_csv,
        test_influence_score_csv,
        test_event_analysis_png,
        test_report,
        test_event_type_coverage,
        test_all_ch05_prefix,
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
    print("=" * 60)
    print(f"结果: {passed} PASSED, {failed} FAILED")
    print(f"状态: {'GREEN' if failed == 0 else 'RED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
