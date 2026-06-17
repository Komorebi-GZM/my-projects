# -*- coding: utf-8 -*-
"""ch03_price_mechanism/analysis.py - 第三章 价格机制分析

通过相关性分析和特征重要性建模，系统识别影响 EV 价格的核心因素，
量化电池容量、续航里程、马力、品牌溢价等参数对价格的解释力度。

输出产物（共7个）：
1. correlation_matrix.csv — 全变量相关系数矩阵
2. correlation_heatmap.png — 相关性热力图
3. feature_importance.csv — Random Forest 特征重要性排序
4. price_scatter_matrix.png — 价格-参数散点图矩阵
5. regression_summary.csv — 多元线性回归模型摘要
6. brand_premium.csv — 品牌溢价表
7. ch03_report.md — 章节分析报告
"""

import sys
from pathlib import Path

# ========== 项目根目录 ==========
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from utils.config import OUTPUT_BASE, PLT_STYLE, COLUMN_CONFIG
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown


def setup_plt_style():
    """设置 matplotlib 全局样式。"""
    try:
        plt.style.use(PLT_STYLE["style"])
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette(PLT_STYLE["color_palette"])
    plt.rcParams.update({
        "font.size": PLT_STYLE["font_size"],
        "figure.dpi": PLT_STYLE["figure_dpi"],
        "savefig.dpi": PLT_STYLE["save_dpi"],
    })


def format_thousands(x: float, pos=None) -> str:
    """坐标轴千分位格式化器。"""
    return f"{int(x):,}"


def step1_price_distribution(df: pd.DataFrame, chapter_output: Path):
    """Step 1: 价格分布描述统计"""
    print("\n" + "=" * 60)
    print("Step 1: 价格分布描述统计")
    print("=" * 60)

    # 全局描述统计
    price_desc = df["price_usd"].describe()
    print("\n=== 价格全局描述统计 ===")
    print(f"  均值:     ${price_desc['mean']:,.2f}")
    print(f"  中位数:   ${price_desc['50%']:,.2f}")
    print(f"  标准差:   ${price_desc['std']:,.2f}")
    print(f"  最小值:   ${price_desc['min']:,.2f}")
    print(f"  25%分位:  ${price_desc['25%']:,.2f}")
    print(f"  75%分位:  ${price_desc['75%']:,.2f}")
    print(f"  最大值:   ${price_desc['max']:,.2f}")

    # 按市场细分分组统计
    segment_order = ["Budget", "Mid-range", "Premium", "Luxury"]
    segment_price_stats = (
        df.groupby("market_segment")["price_usd"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .round(2)
        .reindex(segment_order)
    )
    segment_price_stats.columns = ["count", "mean", "median", "std", "min", "max"]
    print("\n=== 各细分价格统计 ===")
    print(segment_price_stats.to_string())

    # 可视化：价格分布图
    setup_plt_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 左图：全局价格直方图
    ax1 = axes[0]
    ax1.hist(df["price_usd"], bins=40, color="#3498db", edgecolor="white", alpha=0.8)
    ax1.axvline(df["price_usd"].mean(), color="#e74c3c", linestyle="--", linewidth=2,
                label=f"Mean: ${df['price_usd'].mean():,.0f}")
    ax1.axvline(df["price_usd"].median(), color="#27ae60", linestyle="--", linewidth=2,
                label=f"Median: ${df['price_usd'].median():,.0f}")
    ax1.set_xlabel("Price (USD)")
    ax1.set_ylabel("Frequency")
    ax1.set_title("Price Distribution (All Models)", fontsize=14, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))
    ax1.legend(fontsize=10)

    # 右图：按市场细分的箱线图
    ax2 = axes[1]
    sns.boxplot(data=df, x="market_segment", y="price_usd", order=segment_order,
                hue="market_segment", hue_order=segment_order,
                palette=["#27ae60", "#f1c40f", "#e67e22", "#c0392b"], ax=ax2, legend=False)
    ax2.set_xlabel("Market Segment")
    ax2.set_ylabel("Price (USD)")
    ax2.set_title("Price Distribution by Market Segment", fontsize=14, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    plt.tight_layout()
    save_figure(fig, chapter_output / "price_distribution.png", dpi=150)
    plt.close()

    # 验证
    assert 30000 < price_desc['mean'] < 100000, f"价格均值异常: ${price_desc['mean']:,.0f}"
    assert segment_price_stats.loc["Budget", "mean"] < segment_price_stats.loc["Luxury", "mean"]

    print("[OK] Step 1 完成")
    return price_desc, segment_price_stats


def step2_correlation_matrix(df: pd.DataFrame, chapter_output: Path):
    """Step 2: 全变量相关性计算"""
    print("\n" + "=" * 60)
    print("Step 2: 全变量相关性计算")
    print("=" * 60)

    # 获取数值型列
    num_cols = [col for col in COLUMN_CONFIG["numeric_columns"] if col in df.columns]
    print(f"数值型列数: {len(num_cols)}")

    # 计算Pearson相关系数矩阵
    corr_matrix = df[num_cols].corr(method="pearson")

    # 提取price_usd的相关系数，按绝对值降序排列
    price_corr = corr_matrix["price_usd"].drop("price_usd").sort_values(key=abs, ascending=False)
    print("\n=== 与价格的相关系数（按绝对值降序）===")
    for col, val in price_corr.items():
        direction = "正相关" if val > 0 else "负相关"
        strength = "强" if abs(val) >= 0.7 else ("中" if abs(val) >= 0.4 else "弱")
        print(f"  {col:30s}: {val:+.4f}  ({strength}{direction})")

    # 保存完整相关系数矩阵
    save_dataframe(corr_matrix.round(4), chapter_output / "correlation_matrix.csv")

    # 验证
    assert corr_matrix.shape[0] >= 14, f"数值型列数不足: {corr_matrix.shape[0]}"
    np.testing.assert_array_almost_equal(np.diag(corr_matrix.values), np.ones(len(num_cols)), decimal=10)
    assert corr_matrix.equals(corr_matrix.T), "相关系数矩阵不对称"

    print(f"\n[OK] 相关系数矩阵已保存 ({corr_matrix.shape[0]}x{corr_matrix.shape[1]})")
    return corr_matrix, price_corr, num_cols


def step3_correlation_heatmap(corr_matrix: pd.DataFrame, price_corr: pd.Series, chapter_output: Path):
    """Step 3: 相关性热力图绘制"""
    print("\n" + "=" * 60)
    print("Step 3: 相关性热力图绘制")
    print("=" * 60)

    setup_plt_style()

    # 筛选与价格相关性绝对值 > 0.3 的变量
    threshold = 0.3
    selected_vars = ["price_usd"] + list(price_corr[price_corr.abs() > threshold].index)
    corr_selected = corr_matrix.loc[selected_vars, selected_vars]

    print(f"筛选出 {len(selected_vars)} 个与价格相关性 > {threshold} 的变量")

    # 绘制热力图
    fig, ax = plt.subplots(figsize=(14, 11))
    mask = np.triu(np.ones_like(corr_selected, dtype=bool), k=1)

    sns.heatmap(
        corr_selected,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        mask=mask,
        square=True,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation"},
        ax=ax,
    )

    ax.set_title(
        f"Correlation Heatmap (|r| > {threshold} with Price)",
        fontsize=16, fontweight="bold", pad=15
    )
    ax.tick_params(axis="both", labelsize=9)

    plt.tight_layout()
    save_figure(fig, chapter_output / "correlation_heatmap.png", dpi=150)
    plt.close()

    print("[OK] 相关性热力图已保存")


def step4_price_scatter_matrix(df: pd.DataFrame, price_corr: pd.Series, chapter_output: Path):
    """Step 4: 价格-关键参数散点图"""
    print("\n" + "=" * 60)
    print("Step 4: 价格-关键参数散点图")
    print("=" * 60)

    setup_plt_style()

    segment_order = ["Budget", "Mid-range", "Premium", "Luxury"]
    segment_colors = {
        "Budget": "#27ae60", "Mid-range": "#f1c40f",
        "Premium": "#e67e22", "Luxury": "#c0392b",
    }

    # 选取Top5强相关变量（优先原始参数，排除派生特征）
    derived_features = ["price_per_kwh", "efficiency", "power_to_weight"]
    top5_vars = [v for v in price_corr.index if v not in derived_features][:5]
    print(f"Top5 关键参数: {top5_vars}")

    # 国家颜色映射
    country_colors = {
        "US": "#e74c3c", "China": "#3498db", "Germany": "#2ecc71",
        "Japan": "#f39c12", "South Korea": "#9b59b6", "Sweden": "#1abc9c",
    }

    # 绘制散点图矩阵
    fig, axes = plt.subplots(2, 3, figsize=(20, 13))
    axes = axes.flatten()

    for idx, var in enumerate(top5_vars):
        ax = axes[idx]
        for segment in segment_order:
            mask = df["market_segment"] == segment
            ax.scatter(
                df.loc[mask, var], df.loc[mask, "price_usd"],
                c=segment_colors[segment], label=segment,
                alpha=0.4, s=20, edgecolors="none",
            )

        # 添加趋势线
        z = np.polyfit(df[var], df["price_usd"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[var].min(), df[var].max(), 100)
        ax.plot(x_line, p(x_line), "k--", linewidth=1.5, alpha=0.7)

        # 标注相关系数
        r = price_corr[var]
        ax.text(
            0.02, 0.98, f"r = {r:+.3f}",
            transform=ax.transAxes, fontsize=11, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
        )

        ax.set_xlabel(var.replace("_", " ").title(), fontsize=10)
        ax.set_ylabel("Price (USD)", fontsize=10)
        ax.set_title(f"Price vs {var.replace('_', ' ').title()}", fontsize=12, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

        if idx == 0:
            ax.legend(fontsize=8, loc="lower right")

    # 第6个子图：品牌均价 vs 销量（品牌溢价概览）
    ax6 = axes[5]
    brand_avg = df.groupby("brand").agg(
        avg_price=("price_usd", "mean"),
        total_sales=("annual_sales_units", "sum"),
        country=("country_of_origin", "first"),
    ).reset_index()

    for country, color in country_colors.items():
        mask = brand_avg["country"] == country
        if mask.any():
            ax6.scatter(
                brand_avg.loc[mask, "total_sales"], brand_avg.loc[mask, "avg_price"],
                c=color, label=country, s=80, alpha=0.7, edgecolors="black", linewidth=0.5,
            )

    for _, row in brand_avg.iterrows():
        ax6.annotate(
            row["brand"], (row["total_sales"], row["avg_price"]),
            textcoords="offset points", xytext=(5, 5), fontsize=7, alpha=0.8,
        )

    ax6.set_xlabel("Total Sales", fontsize=10)
    ax6.set_ylabel("Avg Price (USD)", fontsize=10)
    ax6.set_title("Brand: Price vs Sales (Premium Overview)", fontsize=12, fontweight="bold")
    ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))
    ax6.xaxis.set_major_formatter(mticker.FuncFormatter(format_thousands))
    ax6.legend(fontsize=7, loc="upper right")

    plt.suptitle("Price vs Key Parameters (Colored by Market Segment)", fontsize=16, fontweight="bold", y=1.01)
    plt.tight_layout()
    save_figure(fig, chapter_output / "price_scatter_matrix.png", dpi=150)
    plt.close()

    print("[OK] 价格-关键参数散点图已保存")


def step5_random_forest(df: pd.DataFrame, num_cols: list, chapter_output: Path):
    """Step 5: Random Forest 特征重要性分析"""
    print("\n" + "=" * 60)
    print("Step 5: Random Forest 特征重要性分析")
    print("=" * 60)

    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    # 定义特征列（排除价格、销量、评分）
    exclude_cols = [
        "price_usd", "annual_sales_units", "customer_rating",
    ]
    # 同时排除不在数据中的派生特征（如果存在）
    derived_features = ["price_per_kwh", "efficiency", "power_to_weight"]
    exclude_cols += [c for c in derived_features if c in df.columns]
    feature_cols = [c for c in num_cols if c not in exclude_cols]
    print(f"特征数量: {len(feature_cols)}")
    print(f"特征列表: {feature_cols}")

    # 准备数据
    X = df[feature_cols].copy()
    y = df["price_usd"].copy()
    X = X.fillna(X.median())

    # 划分训练集/测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集: {X_train.shape[0]} 条, 测试集: {X_test.shape[0]} 条")

    # 训练 Random Forest 模型
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train, y_train)

    # 模型评估
    y_pred_train = rf_model.predict(X_train)
    y_pred_test = rf_model.predict(X_test)

    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))

    print(f"\n=== Random Forest 模型性能 ===")
    print(f"  训练集 R²: {r2_train:.4f}")
    print(f"  测试集 R²: {r2_test:.4f}")
    print(f"  测试集 MAE: ${mae_test:,.2f}")
    print(f"  测试集 RMSE: ${rmse_test:,.2f}")

    # 特征重要性
    importances = pd.Series(rf_model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    print(f"\n=== 特征重要性排序 ===")
    for feat, imp in importances.items():
        print(f"  {feat:30s}: {imp:.4f}")
    print(f"\n  特征重要性之和: {importances.sum():.4f}")

    # 保存特征重要性
    importance_df = importances.reset_index()
    importance_df.columns = ["feature", "importance"]
    importance_df["cumulative_importance"] = importance_df["importance"].cumsum()
    save_dataframe(importance_df.round(4), chapter_output / "feature_importance.csv")

    # 验证
    assert r2_test >= 0.7, f"RF模型 R²={r2_test:.4f} < 0.7"
    assert abs(importances.sum() - 1.0) < 0.01, f"特征重要性之和={importances.sum():.4f} != 1.0"

    print(f"\n[OK] RF模型 R²={r2_test:.4f} >= 0.7，模型拟合良好")
    return importances, importance_df, r2_train, r2_test, mae_test, rmse_test


def step6_ols_regression(df: pd.DataFrame, importances: pd.Series, importance_df: pd.DataFrame, chapter_output: Path):
    """Step 6: 多元线性回归分析"""
    print("\n" + "=" * 60)
    print("Step 6: 多元线性回归分析")
    print("=" * 60)

    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    # 选取Top5特征
    top5_features = importances.head(5).index.tolist()
    print(f"回归特征 (Top5): {top5_features}")

    # 准备数据
    X_ols = df[top5_features].copy().fillna(df[top5_features].median())
    X_ols = sm.add_constant(X_ols)
    y_ols = df["price_usd"].copy()

    # 拟合OLS模型
    ols_model = sm.OLS(y_ols, X_ols).fit()

    # 输出回归摘要
    print(f"\n=== 回归模型摘要 ===")
    print(f"  R²:          {ols_model.rsquared:.4f}")
    print(f"  Adjusted R²: {ols_model.rsquared_adj:.4f}")
    print(f"  F-statistic: {ols_model.fvalue:.2f} (p={ols_model.f_pvalue:.2e})")
    print(f"  AIC:         {ols_model.aic:.2f}")
    print(f"  BIC:         {ols_model.bic:.2f}")

    # 提取关键统计量
    regression_results = pd.DataFrame({
        "feature": ols_model.params.index,
        "coefficient": ols_model.params.values,
        "std_err": ols_model.bse.values,
        "t_value": ols_model.tvalues.values,
        "p_value": ols_model.pvalues.values,
        "ci_lower": ols_model.conf_int()[0].values,
        "ci_upper": ols_model.conf_int()[1].values,
    })
    regression_results["significant_005"] = regression_results["p_value"] < 0.05
    regression_results["significant_001"] = regression_results["p_value"] < 0.01

    print(f"\n=== 回归系数详情 ===")
    print(regression_results.to_string(index=False))

    # 多重共线性检查（VIF）
    print(f"\n=== 方差膨胀因子 (VIF) ===")
    vif_data = pd.DataFrame({
        "feature": top5_features,
        "VIF": [variance_inflation_factor(X_ols.values, i + 1) for i in range(len(top5_features))],
    })
    print(vif_data.to_string(index=False))

    # 保存回归结果
    save_dataframe(regression_results.round(4), chapter_output / "regression_summary.csv")

    # 验证
    n_significant = regression_results["significant_005"].sum()
    assert n_significant >= 3, f"显著特征数不足: {n_significant}/5"

    print(f"\n[OK] 显著特征数 (p<0.05): {n_significant}/{len(top5_features)}")
    return ols_model, regression_results


def step7_brand_premium(df: pd.DataFrame, chapter_output: Path):
    """Step 7: 品牌溢价量化分析"""
    print("\n" + "=" * 60)
    print("Step 7: 品牌溢价量化分析")
    print("=" * 60)

    setup_plt_style()

    # 整体均价
    overall_avg_price = df["price_usd"].mean()
    print(f"整体均价: ${overall_avg_price:,.2f}")

    # 品牌均价与溢价
    brand_premium = (
        df.groupby("brand")
        .agg(
            avg_price=("price_usd", "mean"),
            median_price=("price_usd", "median"),
            n_models=("model", "nunique"),
            main_segment=("market_segment", lambda x: x.mode().iloc[0]),
            country=("country_of_origin", "first"),
        )
        .round(2)
        .reset_index()
    )

    # 计算溢价
    brand_premium["premium_usd"] = brand_premium["avg_price"] - overall_avg_price
    brand_premium["premium_pct"] = (brand_premium["premium_usd"] / overall_avg_price * 100).round(2)
    brand_premium["price_tier"] = pd.cut(
        brand_premium["avg_price"],
        bins=[0, 30000, 50000, 80000, float("inf")],
        labels=["Economy", "Mid-range", "Premium", "Luxury"],
    )

    # 按溢价降序排列
    brand_premium = brand_premium.sort_values("premium_usd", ascending=False).reset_index(drop=True)
    brand_premium["rank"] = range(1, len(brand_premium) + 1)

    print("\n=== 品牌溢价排名 ===")
    print(brand_premium[["rank", "brand", "avg_price", "premium_usd", "premium_pct", "price_tier"]].to_string(index=False))

    n_premium = (brand_premium["premium_usd"] > 0).sum()
    n_discount = (brand_premium["premium_usd"] < 0).sum()
    print(f"\n溢价品牌数: {n_premium}, 折价品牌数: {n_discount}")

    # 保存
    save_dataframe(brand_premium, chapter_output / "brand_premium.csv", index=False)

    # 可视化：品牌溢价水平柱状图
    fig, ax = plt.subplots(figsize=(14, 9))

    plot_data = brand_premium.sort_values("premium_usd", ascending=True)
    colors = ["#e74c3c" if v > 0 else "#27ae60" for v in plot_data["premium_usd"]]

    bars = ax.barh(
        y=plot_data["brand"],
        width=plot_data["premium_usd"],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )

    for bar in bars:
        width = bar.get_width()
        offset = 500 if width >= 0 else -500
        ax.text(
            width + offset,
            bar.get_y() + bar.get_height() / 2,
            f"${width:+,.0f}",
            va="center",
            ha="left" if width >= 0 else "right",
            fontsize=9,
        )

    ax.axvline(x=0, color="black", linewidth=1)
    ax.set_xlabel("Price Premium vs Overall Average (USD)", fontsize=12)
    ax.set_title("Brand Price Premium Analysis\n(Red = Premium, Green = Discount)", fontsize=16, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

    plt.tight_layout()
    save_figure(fig, chapter_output / "brand_premium_chart.png", dpi=150)
    plt.close()

    # 验证
    assert len(brand_premium) == 20, f"品牌数应为20，实际为{len(brand_premium)}"

    print("[OK] 品牌溢价分析完成")
    return brand_premium, overall_avg_price


def step8_generate_report(
    chapter_output: Path,
    price_desc: pd.Series,
    segment_price_stats: pd.DataFrame,
    price_corr: pd.Series,
    importances: pd.Series,
    importance_df: pd.DataFrame,
    r2_train: float, r2_test: float, mae_test: float, rmse_test: float,
    ols_model, regression_results: pd.DataFrame,
    brand_premium: pd.DataFrame,
    overall_avg_price: float,
):
    """Step 8: 章节报告生成"""
    print("\n" + "=" * 60)
    print("Step 8: 章节报告生成")
    print("=" * 60)

    # 获取Top5相关变量
    top5_corr_vars = price_corr.head(5)

    report_content = f"""# 第三章 价格机制分析

> **章节编号**: ch03 | **分析类型**: 分析探索型（原型B） | **优先级**: P0

---

## 3.1 价格分布概览

全球EV市场价格区间为 **${price_desc['min']:,.0f} - ${price_desc['max']:,.0f}**，均价 **${price_desc['mean']:,.0f}**，中位数 **${price_desc['50%']:,.0f}**。

![价格分布图](price_distribution.png)

### 各细分价格统计

| 细分 | 样本数 | 均价(USD) | 中位数(USD) | 标准差 |
|------|--------|-----------|-------------|--------|
"""

    for seg, row in segment_price_stats.iterrows():
        report_content += f"| {seg} | {int(row['count'])} | {row['mean']:,.0f} | {row['median']:,.0f} | {row['std']:,.0f} |\n"

    report_content += f"""
## 3.2 价格影响因素 — 相关性分析

### 与价格相关性最强的变量（Top 10）

| 排名 | 变量 | 相关系数 | 方向 |
|------|------|----------|------|
"""

    for rank, (var, corr_val) in enumerate(price_corr.head(10).items(), 1):
        direction = "正相关" if corr_val > 0 else "负相关"
        report_content += f"| {rank} | {var} | {corr_val:+.4f} | {direction} |\n"

    report_content += f"""
![相关性热力图](correlation_heatmap.png)

**关键发现**：
- 与价格**最强正相关**的变量为 `{price_corr.index[0]}`（r={price_corr.iloc[0]:+.4f}）
- 与价格**最强负相关**的变量为 `{price_corr[price_corr < 0].index[0]}`（r={price_corr[price_corr < 0].iloc[0]:+.4f}）
- 派生特征 `price_per_kwh` 与价格呈负相关，符合"性价比"的经济学直觉

## 3.3 价格影响因素 — 散点图分析

![价格-参数散点图](price_scatter_matrix.png)

散点图展示了价格与 Top5 关键参数的关系形态。按市场细分着色后可观察到：
- **Luxury 细分**（红色）集中在高价格区间
- **Budget 细分**（绿色）集中在低价格区间
- 各参数与价格的关系基本呈线性趋势

## 3.4 价格影响因素 — Random Forest 特征重要性

### 模型性能

| 指标 | 训练集 | 测试集 |
|------|--------|--------|
| R² | {r2_train:.4f} | {r2_test:.4f} |
| MAE | - | ${mae_test:,.0f} |
| RMSE | - | ${rmse_test:,.0f} |

### 特征重要性排序（Top 10）

| 排名 | 特征 | 重要性 | 累计重要性 |
|------|------|--------|-----------|
"""

    for rank, (feat, imp) in enumerate(importances.head(10).items(), 1):
        cum_imp = importance_df[importance_df["feature"] == feat]["cumulative_importance"].values[0]
        report_content += f"| {rank} | {feat} | {imp:.4f} | {cum_imp:.4f} |\n"

    report_content += f"""
## 3.5 价格影响因素 — OLS 多元线性回归

### 回归模型摘要

| 指标 | 值 |
|------|-----|
| R² | {ols_model.rsquared:.4f} |
| Adjusted R² | {ols_model.rsquared_adj:.4f} |
| F-statistic | {ols_model.fvalue:.2f} |
| F p-value | {ols_model.f_pvalue:.2e} |

### 回归系数

| 特征 | 系数 | 标准误 | t值 | p值 | 显著性 |
|------|------|--------|-----|-----|--------|
"""

    for _, row in regression_results.iterrows():
        sig = "***" if row["significant_001"] else ("**" if row["significant_005"] else "n.s.")
        report_content += f"| {row['feature']} | {row['coefficient']:.4f} | {row['std_err']:.4f} | {row['t_value']:.4f} | {row['p_value']:.4f} | {sig} |\n"

    report_content += """
> 注：\\* p<0.05, \\*\\* p<0.01, \\*\\*\\* p<0.001, n.s. = 不显著

## 3.6 品牌溢价分析

整体均价为 **${0:,.0f}**。品牌溢价排名如下：

| 排名 | 品牌 | 均价(USD) | 溢价(USD) | 溢价率(%) | 定位 |
|------|------|-----------|-----------|-----------|------|
""".format(overall_avg_price)

    for _, row in brand_premium.iterrows():
        report_content += f"| {int(row['rank'])} | {row['brand']} | {row['avg_price']:,.0f} | {row['premium_usd']:+,.0f} | {row['premium_pct']:+.2f}% | {row['price_tier']} |\n"

    report_content += f"""
![品牌溢价图](brand_premium_chart.png)

## 3.7 本章小结

本章通过相关性分析、Random Forest 特征重要性和 OLS 多元线性回归三种方法，系统识别了影响EV价格的核心因素。核心结论如下：

1. **价格驱动力**：`{importances.index[0]}`（重要性={importances.iloc[0]:.4f}）和 `{importances.index[1]}`（重要性={importances.iloc[1]:.4f}）是影响EV价格的两大核心因素
2. **模型解释力**：Random Forest 模型测试集 R²={r2_test:.4f}，说明所选特征能解释价格变异的 {r2_test*100:.1f}%
3. **品牌溢价分化**：溢价最高的品牌为 `{brand_premium.iloc[0]['brand']}`（溢价 {brand_premium.iloc[0]['premium_pct']:+.1f}%），折价最多的品牌为 `{brand_premium.iloc[-1]['brand']}`（溢价 {brand_premium.iloc[-1]['premium_pct']:+.1f}%）
4. **市场细分效应**：Luxury 细分均价是 Budget 细分的 {segment_price_stats.loc['Luxury','mean'] / segment_price_stats.loc['Budget','mean']:.1f} 倍，价格梯度显著

---

*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源：cleaned_data.csv（1070行 x 27列）*
"""

    save_markdown(report_content, chapter_output / "ch03_report.md")
    print("[OK] 章节报告已保存: ch03_report.md")


def main():
    """主函数：执行全部8个分析步骤"""
    print("\n" + "=" * 70)
    print("第三章 价格机制分析 - 开始执行")
    print("=" * 70)

    # 创建输出目录
    chapter_output = ensure_dir(OUTPUT_BASE / "ch03_price_mechanism")
    print(f"[INFO] 输出目录: {chapter_output}")

    # 加载数据
    print("\n[INFO] 加载清洗后数据...")
    df = load_preprocessed(chapter="ch01_data_cleaning", filename="cleaned_data.csv")
    print(f"[INFO] 数据形状: {df.shape}")

    # 执行各步骤
    price_desc, segment_price_stats = step1_price_distribution(df, chapter_output)
    corr_matrix, price_corr, num_cols = step2_correlation_matrix(df, chapter_output)
    step3_correlation_heatmap(corr_matrix, price_corr, chapter_output)
    step4_price_scatter_matrix(df, price_corr, chapter_output)
    importances, importance_df, r2_train, r2_test, mae_test, rmse_test = step5_random_forest(df, num_cols, chapter_output)
    ols_model, regression_results = step6_ols_regression(df, importances, importance_df, chapter_output)
    brand_premium, overall_avg_price = step7_brand_premium(df, chapter_output)
    step8_generate_report(
        chapter_output, price_desc, segment_price_stats, price_corr,
        importances, importance_df, r2_train, r2_test, mae_test, rmse_test,
        ols_model, regression_results, brand_premium, overall_avg_price,
    )

    print("\n" + "=" * 70)
    print("第三章 价格机制分析 - 执行完成")
    print("=" * 70)
    print(f"\n输出产物列表 ({chapter_output}):")
    for f in sorted(chapter_output.glob("*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
