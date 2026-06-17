#!/usr/bin/env python3
"""ch03 文本挖掘与情感分析 — 产物验证测试.

TDD-RED 阶段：定义 ch03 全部产物的验证条件。
测试通过 = GREEN，测试失败 = RED。

运行方式:
    python src/ch03_text_mining_sentiment/test_ch03.py
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

OUTPUT_DIR = get_chapter_output_dir("ch03_text_mining_sentiment")

# 预期产物清单（依据 flow_design.md + execution_prompts.md Prompt-03）
EXPECTED_PNG_FILES = [
    "ch03_sentiment_distribution.png",
    "ch03_sentiment_by_category.png",
    "ch03_sentiment_timeline.png",
    "ch03_event_window_sentiment.png",
    "ch03_topic_timeline_heatmap.png",
]

EXPECTED_CSV_FILES = [
    "ch03_sentiment_labels.csv",
    "ch03_topic_model_results.csv",
]

EXPECTED_HTML_FILES = [
    "ch03_topic_visualization.html",
]

EXPECTED_MD_FILES = [
    "ch03_sentiment_analysis_report.md",
    "ch03_topic_analysis_report.md",
]

ALL_EXPECTED = (
    EXPECTED_PNG_FILES + EXPECTED_CSV_FILES
    + EXPECTED_HTML_FILES + EXPECTED_MD_FILES
)


def test_output_dir_exists() -> None:
    """验证 ch03 输出目录存在."""
    assert OUTPUT_DIR.exists(), f"输出目录不存在: {OUTPUT_DIR}"
    print(f"  [PASS] 输出目录存在: {OUTPUT_DIR}")


def test_png_count() -> None:
    """验证 PNG 图表数量 >= 5."""
    png_files = list(OUTPUT_DIR.glob("ch03_*.png"))
    assert len(png_files) >= 5, f"PNG 图表数量不足: {len(png_files)} >= 5"
    print(f"  [PASS] PNG 图表数量: {len(png_files)} >= 5")


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


def test_sentiment_labels_csv() -> None:
    """验证情感标签 CSV 存在且内容正确."""
    import pandas as pd
    fpath = OUTPUT_DIR / "ch03_sentiment_labels.csv"
    assert fpath.exists(), "情感标签文件不存在: ch03_sentiment_labels.csv"
    df = pd.read_csv(fpath)
    assert len(df) > 0, "情感标签数据为空"
    # 验证必需列
    required_cols = {"sentiment", "confidence", "sentiment_score"}
    assert required_cols.issubset(set(df.columns)), \
        f"缺少必需列: {required_cols - set(df.columns)}"
    # 验证情感标签覆盖率 = 100%
    coverage = df["sentiment"].notna().mean() * 100
    assert coverage == 100.0, f"情感标签覆盖率不足: {coverage}% < 100%"
    # 验证情感分布合理（任一类别占比 < 80%）
    sent_counts = df["sentiment"].value_counts(normalize=True)
    max_ratio = sent_counts.max() * 100
    assert max_ratio < 80, f"情感分布不合理: 最大类别占比 {max_ratio:.1f}% >= 80%"
    # 验证 sentiment_score 取值范围
    valid_scores = {-1, 0, 1}
    actual_scores = set(df["sentiment_score"].dropna().unique())
    assert valid_scores.issuperset(actual_scores), \
        f"sentiment_score 包含非法值: {actual_scores - valid_scores}"
    print(f"  [PASS] 情感标签: {len(df)} 行, 覆盖率 100%, "
          f"最大类别占比 {max_ratio:.1f}%")


def test_topic_model_results_csv() -> None:
    """验证主题建模结果 CSV 存在且内容正确."""
    import pandas as pd
    fpath = OUTPUT_DIR / "ch03_topic_model_results.csv"
    assert fpath.exists(), "主题建模结果文件不存在: ch03_topic_model_results.csv"
    df = pd.read_csv(fpath)
    assert len(df) > 0, "主题建模结果为空"
    # 验证必需列
    required_cols = {"topic_id", "topic_prob"}
    assert required_cols.issubset(set(df.columns)), \
        f"缺少必需列: {required_cols - set(df.columns)}"
    # 验证主题数量在 8-15 范围内
    n_topics = df["topic_id"].nunique()
    assert 8 <= n_topics <= 15, \
        f"主题数量不在合理范围: {n_topics} (要求 8-15)"
    print(f"  [PASS] 主题建模结果: {len(df)} 行, {n_topics} 个主题")


def test_topic_visualization_html() -> None:
    """验证 BERTopic 可视化 HTML 存在且非空."""
    fpath = OUTPUT_DIR / "ch03_topic_visualization.html"
    assert fpath.exists(), "BERTopic 可视化文件不存在: ch03_topic_visualization.html"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 1000, "BERTopic 可视化文件内容过小"
    assert "<html" in content.lower() or "<!doctype" in content.lower(), \
        "文件不是有效的 HTML"
    print(f"  [PASS] BERTopic 可视化 HTML: {len(content)} 字符")


def test_sentiment_report() -> None:
    """验证情感分析报告存在且内容完整."""
    fpath = OUTPUT_DIR / "ch03_sentiment_analysis_report.md"
    assert fpath.exists(), "情感分析报告不存在: ch03_sentiment_analysis_report.md"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "情感分析报告内容过短"
    # 检查报告包含关键分析维度（英文报告检查英文关键词）
    keywords = ["sentiment", "Sentiment", "FinBERT", "distribution", "timeline"]
    found = [kw for kw in keywords if kw in content]
    assert len(found) >= 2, \
        f"报告缺少关键分析维度，仅找到: {found} (需至少 2 个)"
    print(f"  [PASS] 情感分析报告: {len(content)} 字符, "
          f"包含关键词: {found}")


def test_topic_report() -> None:
    """验证主题分析报告存在且内容完整."""
    fpath = OUTPUT_DIR / "ch03_topic_analysis_report.md"
    assert fpath.exists(), "主题分析报告不存在: ch03_topic_analysis_report.md"
    content = fpath.read_text(encoding="utf-8")
    assert len(content) > 500, "主题分析报告内容过短"
    # 检查报告包含关键分析维度
    keywords = ["topic", "Topic", "BERTopic", "LDA", "coherence", "Coherence"]
    found = [kw for kw in keywords if kw in content]
    assert len(found) >= 2, \
        f"报告缺少关键分析维度，仅找到: {found} (需至少 2 个)"
    print(f"  [PASS] 主题分析报告: {len(content)} 字符, "
          f"包含关键词: {found}")


def test_all_files_ch03_prefix() -> None:
    """验证所有产物文件以 ch03_ 开头."""
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            assert f.name.startswith("ch03_"), \
                f"文件命名不符合规范: {f.name}（缺少 ch03_ 前缀）"
    print(f"  [PASS] 所有产物文件以 ch03_ 开头")


def test_total_deliverables() -> None:
    """验证产物总数 >= 10（5 PNG + 2 CSV + 1 HTML + 2 MD）."""
    all_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file()]
    assert len(all_files) >= 10, f"产物总数不足: {len(all_files)} >= 10"
    print(f"  [PASS] 产物总数: {len(all_files)} >= 10")


def main() -> None:
    """运行全部测试."""
    print("=" * 60)
    print("ch03 文本挖掘与情感分析 — 产物验证测试 (TDD-RED)")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"预期产物: {len(ALL_EXPECTED)} 个")
    print()

    tests = [
        test_output_dir_exists,
        test_png_count,
        test_png_dpi,
        test_sentiment_labels_csv,
        test_topic_model_results_csv,
        test_topic_visualization_html,
        test_sentiment_report,
        test_topic_report,
        test_all_files_ch03_prefix,
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
