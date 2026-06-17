"""
章节：ch03 假设检验与效应量
描述：执行比例Z检验、计算效应量Cohen's h、统计功效和MDE
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


def step01_proportion_z_test(df: pd.DataFrame) -> dict:
    """
    步骤1：比例Z检验（单尾）
    H0: p_exp <= p_con
    H1: p_exp > p_con
    """
    print("=" * 60)
    print("步骤1：比例Z检验（单尾）")
    print("=" * 60)

    # 提取数据
    con_data = df[df["group"] == "con"]["click"]
    exp_data = df[df["group"] == "exp"]["click"]

    n_con = len(con_data)
    n_exp = len(exp_data)
    x_con = con_data.sum()
    x_exp = exp_data.sum()

    p_con = x_con / n_con
    p_exp = x_exp / n_exp

    # 合并比例（用于计算标准误）
    p_pooled = (x_con + x_exp) / (n_con + n_exp)

    # Z统计量
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_con + 1/n_exp))
    z_stat = (p_exp - p_con) / se

    # 单尾p值（右侧检验）
    from scipy import stats
    p_value = 1 - stats.norm.cdf(z_stat)

    print(f"\n假设:")
    print(f"  H0: p_exp <= p_con (实验组点击率不高于对照组)")
    print(f"  H1: p_exp > p_con (实验组点击率高于对照组)")

    print(f"\n样本统计:")
    print(f"  对照组: n={n_con}, 点击={x_con}, CTR={p_con:.4f}")
    print(f"  实验组: n={n_exp}, 点击={x_exp}, CTR={p_exp:.4f}")

    print(f"\n检验结果:")
    print(f"  Z统计量: {z_stat:.4f}")
    print(f"  p值: {p_value:.6f}")
    print(f"  显著性水平: α = 0.05")

    if p_value < 0.05:
        print(f"\n✓ 结论: p < 0.05，拒绝H0，实验组点击率显著高于对照组")
    else:
        print(f"\n✗ 结论: p >= 0.05，无法拒绝H0，无显著差异")

    return {
        "n_con": n_con, "n_exp": n_exp,
        "x_con": x_con, "x_exp": x_exp,
        "p_con": p_con, "p_exp": p_exp,
        "p_pooled": p_pooled,
        "z_stat": z_stat,
        "p_value": p_value,
        "significant": p_value < 0.05
    }


def step02_confidence_interval(results: dict) -> dict:
    """
    步骤2：计算CTR差异的95%置信区间
    """
    print("\n" + "=" * 60)
    print("步骤2：CTR差异的95%置信区间")
    print("=" * 60)

    p_con = results["p_con"]
    p_exp = results["p_exp"]
    n_con = results["n_con"]
    n_exp = results["n_exp"]

    # 差异的标准误（使用各自比例）
    se_diff = np.sqrt(p_con * (1 - p_con) / n_con + p_exp * (1 - p_exp) / n_exp)

    diff = p_exp - p_con
    z = 1.96

    ci_lower = diff - z * se_diff
    ci_upper = diff + z * se_diff

    print(f"\nCTR差异: {diff:.4f} ({diff*100:.2f} pp)")
    print(f"95%置信区间: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]")

    if ci_lower > 0:
        print(f"\n✓ 置信区间不包含0，差异为正")
    elif ci_upper < 0:
        print(f"\n✗ 置信区间不包含0，差异为负")
    else:
        print(f"\n○ 置信区间包含0，差异不确定")

    return {
        "diff": diff,
        "se_diff": se_diff,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    }


def step03_cohens_h(results: dict) -> float:
    """
    步骤3：计算Cohen's h效应量
    """
    print("\n" + "=" * 60)
    print("步骤3：Cohen's h效应量")
    print("=" * 60)

    p_con = results["p_con"]
    p_exp = results["p_exp"]

    # Cohen's h = 2 * (arcsin(sqrt(p1)) - arcsin(sqrt(p2)))
    h = 2 * (np.arcsin(np.sqrt(p_exp)) - np.arcsin(np.sqrt(p_con)))

    print(f"\nCohen's h = {h:.4f}")

    # 效应量解释
    abs_h = abs(h)
    if abs_h < 0.2:
        effect_size = "可忽略 (negligible)"
    elif abs_h < 0.5:
        effect_size = "小效应 (small)"
    elif abs_h < 0.8:
        effect_size = "中等效应 (medium)"
    else:
        effect_size = "大效应 (large)"

    print(f"效应量解释: {effect_size}")

    return h


def step04_power_analysis(results: dict) -> dict:
    """
    步骤4：统计功效分析与MDE计算
    """
    print("\n" + "=" * 60)
    print("步骤4：统计功效分析与MDE")
    print("=" * 60)

    from statsmodels.stats.power import zt_ind_solve_power
    from statsmodels.stats.proportion import proportion_effectsize

    p_con = results["p_con"]
    p_exp = results["p_exp"]
    n_con = results["n_con"]
    n_exp = results["n_exp"]

    # 效应量（Cohen's h）
    effect_size = proportion_effectsize(p_exp, p_con)

    # 计算当前实验的统计功效
    power = zt_ind_solve_power(
        effect_size=effect_size,
        nobs1=n_exp,
        alpha=0.05,
        ratio=n_con/n_exp,
        alternative="larger"
    )

    print(f"\n统计功效分析:")
    print(f"  效应量 (Cohen's h): {effect_size:.4f}")
    print(f"  当前统计功效: {power:.4f} ({power*100:.1f}%)")

    if power >= 0.8:
        print(f"  ✓ 功效充足 (>= 80%)")
    else:
        print(f"  ⚠ 功效不足 (< 80%)，可能存在假阴性风险")

    # 计算MDE（最小可检测效应）
    # 在功效=80%，α=0.05条件下，能检测到的最小效应
    from scipy.optimize import brentq

    def power_diff(h, n1, n2, alpha=0.05, target_power=0.8):
        es = proportion_effectsize(p_con + h, p_con) if p_con + h < 1 else 0
        if es == 0:
            return 1
        try:
            p = zt_ind_solve_power(effect_size=es, nobs1=n1, alpha=alpha, ratio=n2/n1, alternative="larger")
            return p - target_power
        except Exception:
            return 1
    try:
        mde = brentq(lambda h: power_diff(h, n_exp, n_con), 0.001, 0.5)
        mde_pct = mde * 100
        print(f"\n最小可检测效应 (MDE):")
        print(f"  MDE = {mde:.4f} ({mde_pct:.2f} pp)")
        print(f"  解释: 在当前样本量下，有80%概率检测到至少{mde_pct:.2f}个百分点的CTR提升")
    except Exception as e:
        mde = None
        print(f"\nMDE计算失败: {e}")

    return {
        "effect_size": effect_size,
        "power": power,
        "mde": mde
    }


def main():
    """主函数"""
    print("╔" + "═" * 58 + "╗")
    print("║" + "  ch03 假设检验与效应量".center(46) + "║")
    print("╚" + "═" * 58 + "╝")

    # 初始化工具
    config = Config()
    loader = DataLoader(config)
    output = OutputManager(config)

    # 加载清洗后数据
    df = loader.load_processed("cleaned_data.csv")

    # 执行分析步骤
    results = step01_proportion_z_test(df)
    ci_results = step02_confidence_interval(results)
    h = step03_cohens_h(results)
    power_results = step04_power_analysis(results)

    # 汇总结果
    summary = {
        **results,
        **ci_results,
        "cohens_h": h,
        **power_results
    }

    # 保存结果
    summary_df = pd.DataFrame([summary])
    output.save_table(summary_df, "hypothesis_test_results", chapter_prefix="ch03")

    # 输出汇总
    print("\n" + "=" * 60)
    print("✓ ch03 完成！汇总结果:")
    print("=" * 60)
    print(f"Z统计量: {results['z_stat']:.4f}, p值: {results['p_value']:.6f}")
    print(f"95%CI: [{ci_results['ci_lower']*100:.2f}%, {ci_results['ci_upper']*100:.2f}%]")
    print(f"Cohen's h: {h:.4f}")
    print(f"统计功效: {power_results['power']:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
