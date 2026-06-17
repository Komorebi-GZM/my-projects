"""
章节：ch05 结论与决策建议
描述：综合所有分析结果，给出明确的业务决策建议
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.utils.config import Config
from src.utils.data_loader import DataLoader
from src.utils.output_manager import OutputManager


def load_previous_results(config):
    """加载前面章节的分析结果"""
    results = {}

    # 尝试加载ch02的分组统计
    try:
        ch02_path = config.tables_dir / "ch02_group_metrics_with_ci.csv"
        if ch02_path.exists():
            results["ch02"] = pd.read_csv(ch02_path)
    except Exception:
        pass

    # 尝试加载ch03的假设检验结果
    try:
        ch03_path = config.tables_dir / "ch03_hypothesis_test_results.csv"
        if ch03_path.exists():
            results["ch03"] = pd.read_csv(ch03_path).iloc[0].to_dict()
    except Exception:
        pass

    return results


def step01_summarize_results(results: dict, df: pd.DataFrame) -> dict:
    """
    步骤1：汇总所有分析结果
    """
    print("=" * 60)
    print("步骤1：分析结果汇总")
    print("=" * 60)

    summary = {}

    # 基础统计
    con_data = df[df["group"] == "con"]["click"]
    exp_data = df[df["group"] == "exp"]["click"]

    summary["n_con"] = len(con_data)
    summary["n_exp"] = len(exp_data)
    summary["ctr_con"] = con_data.mean()
    summary["ctr_exp"] = exp_data.mean()
    summary["absolute_lift"] = summary["ctr_exp"] - summary["ctr_con"]
    summary["relative_lift"] = summary["absolute_lift"] / summary["ctr_con"] * 100

    print(f"\n【基础统计】")
    print(f"  样本量: 对照组={summary['n_con']}, 实验组={summary['n_exp']}")
    print(f"  CTR: 对照组={summary['ctr_con']:.4f}, 实验组={summary['ctr_exp']:.4f}")
    print(f"  提升: 绝对={summary['absolute_lift']*100:.2f}pp, 相对={summary['relative_lift']:.1f}%")

    # 从ch03获取检验结果
    if "ch03" in results:
        ch03 = results["ch03"]
        summary["z_stat"] = ch03.get("z_stat", np.nan)
        summary["p_value"] = ch03.get("p_value", np.nan)
        summary["cohens_h"] = ch03.get("cohens_h", np.nan)
        summary["power"] = ch03.get("power", np.nan)
        summary["ci_lower"] = ch03.get("ci_lower", np.nan)
        summary["ci_upper"] = ch03.get("ci_upper", np.nan)

        print(f"\n【假设检验】")
        print(f"  Z统计量: {summary['z_stat']:.4f}")
        print(f"  p值: {summary['p_value']:.6f}")
        print(f"  95%CI: [{summary['ci_lower']*100:.2f}%, {summary['ci_upper']*100:.2f}%]")
        print(f"  Cohen's h: {summary['cohens_h']:.4f}")
        print(f"  统计功效: {summary['power']:.2%}")
    else:
        print(f"\n⚠ 未找到ch03结果，请先运行ch03")

    return summary


def step02_make_decision(summary: dict) -> tuple:
    """
    步骤2：基于严格决策框架做出决策
    """
    print("\n" + "=" * 60)
    print("步骤2：业务决策")
    print("=" * 60)

    p_value = summary.get("p_value", 1.0)
    cohens_h = abs(summary.get("cohens_h", 0))
    power = summary.get("power", 0)

    print(f"\n【决策条件】")
    print(f"  p值 = {p_value:.6f} (< 0.05?)")
    print(f"  |Cohen's h| = {cohens_h:.4f} (>= 0.2?)")
    print(f"  功效 = {power:.2%} (>= 80%?)")

    # 严格决策矩阵
    print(f"\n【决策逻辑】")

    if p_value < 0.05 and cohens_h >= 0.2 and power >= 0.8:
        decision = "全量上线"
        reason = "统计显著(p<0.05) + 效应有意义(h>=0.2) + 功效充足(>=80%)"
        risk = "低风险"

    elif p_value < 0.05 and cohens_h < 0.2:
        decision = "灰度发布"
        reason = "统计显著但效应量过小，实际业务意义有限"
        risk = "中风险 - 用户可能感知不到明显改进"

    elif p_value >= 0.05 and power < 0.8:
        decision = "需要进一步实验"
        reason = "功效不足，可能存在假阴性（第二类错误）"
        risk = "高风险 - 当前样本量不足以得出结论"

    else:
        decision = "放弃该版本"
        reason = "功效充足但仍不显著，新版本确实无提升效果"
        risk = "低风险 - 数据支持不采纳新版本"

    print(f"  决策: {decision}")
    print(f"  理由: {reason}")
    print(f"  风险: {risk}")

    return decision, reason, risk


def step03_generate_report(summary: dict, decision: str, reason: str, risk: str,
                           output: OutputManager) -> None:
    """
    步骤3：生成决策报告
    """
    print("\n" + "=" * 60)
    print("步骤3：生成决策报告")
    print("=" * 60)

    # 安全格式化辅助函数
    def safe_fmt(value, fmt_type: str, default: str = "N/A") -> str:
        """安全格式化，处理 NaN 和缺失值"""
        try:
            if pd.isna(value) or value is None:
                return default
            if fmt_type == "4f":
                return f"{float(value):.4f}"
            elif fmt_type == "6f":
                return f"{float(value):.6f}"
            elif fmt_type == "2f_pct":
                return f"{float(value)*100:.2f}%"
            elif fmt_type == "2pct":
                return f"{float(value):.2%}"
            elif fmt_type == "1f":
                return f"{float(value):.1f}%"
            else:
                return str(value)
        except (TypeError, ValueError):
            return default

    z_stat_str = safe_fmt(summary.get("z_stat"), "4f")
    p_value_str = safe_fmt(summary.get("p_value"), "6f")
    ci_lower_str = safe_fmt(summary.get("ci_lower"), "2f_pct")
    ci_upper_str = safe_fmt(summary.get("ci_upper"), "2f_pct")
    cohens_h_str = safe_fmt(summary.get("cohens_h"), "4f")
    power_str = safe_fmt(summary.get("power"), "2pct")

    report = f"""
# A/B测试分析报告 - 决策建议

## 实验概况
- **实验时间**: 2024-01-01 至 2024-01-07
- **样本量**: 对照组 {summary['n_con']:,} 人，实验组 {summary['n_exp']:,} 人
- **核心指标**: 点击率 (CTR)

## 关键发现

| 指标 | 对照组 | 实验组 | 差异 |
|------|--------|--------|------|
| 点击率 | {summary['ctr_con']*100:.2f}% | {summary['ctr_exp']*100:.2f}% | +{summary['absolute_lift']*100:.2f}pp ({summary['relative_lift']:.1f}%) |

## 统计检验结果
- **Z统计量**: {z_stat_str}
- **p值**: {p_value_str}
- **95%置信区间**: [{ci_lower_str}, {ci_upper_str}]
- **Cohen's h效应量**: {cohens_h_str}
- **统计功效**: {power_str}

## 决策建议

### 建议结论
**{decision}**

### 决策理由
{reason}

### 风险提示
{risk}

## 后续行动

根据决策建议，建议采取以下行动：

"""

    # 根据决策添加后续行动
    if decision == "全量上线":
        report += """
1. 制定全量上线计划，建议分阶段灰度至100%
2. 上线后持续监控核心指标，确保无回退
3. 记录本次实验经验，沉淀最佳实践
4. 考虑将新版本作为基准，继续迭代优化
"""
    elif decision == "灰度发布":
        report += """
1. 小范围灰度发布，观察用户反馈
2. 收集定性反馈，了解用户真实感受
3. 考虑优化新版本，提升效应量
4. 若反馈良好，可逐步扩大范围
"""
    elif decision == "需要进一步实验":
        report += """
1. 延长实验时间，收集更多样本
2. 或增加实验流量，提高样本量
3. 重新计算所需样本量，确保功效>=80%
4. 实验设计优化，控制混杂变量
"""
    else:
        report += """
1. 放弃当前新版本，保留旧版本
2. 分析新版本设计，找出问题所在
3. 重新设计实验方案，进行新一轮A/B测试
4. 考虑其他优化方向
"""

    # 保存报告
    report_path = output.config.outputs_dir / "tables" / "ch05_decision_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ 决策报告已保存: {report_path}")
    print(f"\n{'='*60}")
    print(report)


def main():
    """主函数"""
    print("╔" + "═" * 58 + "╗")
    print("║" + "  ch05 结论与决策建议".center(46) + "║")
    print("╚" + "═" * 58 + "╝")

    # 初始化工具
    config = Config()
    loader = DataLoader(config)
    output = OutputManager(config)

    # 加载清洗后数据
    df = loader.load_processed("cleaned_data.csv")

    # 加载前面章节的结果
    previous_results = load_previous_results(config)

    # 执行分析步骤
    summary = step01_summarize_results(previous_results, df)
    decision, reason, risk = step02_make_decision(summary)
    step03_generate_report(summary, decision, reason, risk, output)

    print("\n" + "=" * 60)
    print("✓ ch05 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
