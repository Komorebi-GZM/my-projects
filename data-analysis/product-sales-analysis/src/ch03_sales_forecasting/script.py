"""
ch03 销售趋势预测脚本 - 产品销售数据分析项目

本脚本执行销售趋势预测分析流程，包括：
1. 加载清洗后的数据
2. 按月聚合 Total_Sales_USD
3. 使用简单移动平均（SMA，窗口3和6）进行预测
4. 使用指数平滑（SES）进行预测
5. 计算预测误差（MAE, RMSE）
6. 绘制历史趋势 + 预测曲线图
7. 生成图表和报告（report.md）

前置依赖: ch01_data_cleaning, ch02_descriptive_analysis

执行方式:
    cd Product_Sales_Analysis
    python -m src.ch03_sales_forecasting.script
"""

import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.utils import (
    load_preprocessed,
    save_dataframe,
    save_markdown,
    save_figure,
    OUTPUT_BASE,
    CATEGORY_LIST,
    CITY_LIST,
    PLT_CONFIG,
)


def main():
    """执行销售趋势预测主流程。"""
    print("=" * 60)
    print("ch03 销售趋势预测 - 开始执行")
    print("=" * 60)

    # 定义输出目录
    output_dir = OUTPUT_BASE / "sales_forecasting"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 步骤 1: 加载清洗后的数据
    # ============================================================
    print("\n--- 步骤 1: 加载清洗后的数据 ---")
    df = load_preprocessed("ch01_data_cleaning", "product")
    print(f"数据形状: {df.shape}")
    print(f"数据列: {df.columns.tolist()}")

    # ============================================================
    # 步骤 2: 按月聚合 Total_Sales_USD
    # ============================================================
    print("\n--- 步骤 2: 按月聚合销售额 ---")

    # 确定日期列名
    date_col = 'date' if 'date' in df.columns else 'Date'
    sales_col = 'Total_Sales_USD' if 'Total_Sales_USD' in df.columns else 'total_price'

    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy['month'] = df_copy[date_col].dt.to_period('M')

    monthly = df_copy.groupby('month')[sales_col].sum().reset_index()
    monthly['month_str'] = monthly['month'].astype(str)
    monthly = monthly.sort_values('month').reset_index(drop=True)

    print(f"月度数据点数: {len(monthly)}")
    print(monthly[['month_str', sales_col]].to_string(index=False))

    save_dataframe(monthly[['month_str', sales_col]], output_dir / "monthly_sales.csv")

    # ============================================================
    # 步骤 3: 简单移动平均（SMA）预测
    # ============================================================
    print("\n--- 步骤 3: 简单移动平均（SMA）预测 ---")

    monthly['SMA_3'] = monthly[sales_col].rolling(window=3, min_periods=3).mean()
    monthly['SMA_6'] = monthly[sales_col].rolling(window=6, min_periods=6).mean()

    # 用最后一个 SMA 值作为未来预测
    sma3_forecast = monthly['SMA_3'].iloc[-1]
    sma6_forecast = monthly['SMA_6'].iloc[-1]
    print(f"SMA(3) 最新值: {sma3_forecast:,.2f}")
    print(f"SMA(6) 最新值: {sma6_forecast:,.2f}")

    # ============================================================
    # 步骤 4: 指数平滑（SES）预测
    # ============================================================
    print("\n--- 步骤 4: 指数平滑（SES）预测 ---")

    from statsmodels.tsa.holtwinters import SimpleExpSmoothing

    series = monthly[sales_col].values
    ses_model = SimpleExpSmoothing(series, initialization_method='estimated').fit(smoothing_level=0.3)
    monthly['SES'] = ses_model.fittedvalues
    ses_forecast = ses_model.forecast(1)[0]
    print(f"SES 预测下一期: {ses_forecast:,.2f}")

    # ============================================================
    # 步骤 5: 计算预测误差
    # ============================================================
    print("\n--- 步骤 5: 计算预测误差 ---")

    # 只在有足够数据的区间计算误差
    error_results = []
    for method, col in [('SMA_3', 'SMA_3'), ('SMA_6', 'SMA_6'), ('SES', 'SES')]:
        valid = monthly.dropna(subset=[col])
        if len(valid) > 0:
            actual = valid[sales_col].values
            predicted = valid[col].values
            mae = np.mean(np.abs(actual - predicted))
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            error_results.append({
                'Method': method,
                'MAE': round(mae, 2),
                'RMSE': round(rmse, 2),
                'N': len(valid)
            })
            print(f"{method}: MAE={mae:,.2f}, RMSE={rmse:,.2f} (n={len(valid)})")

    error_df = pd.DataFrame(error_results)
    save_dataframe(error_df, output_dir / "forecast_errors.csv")

    # ============================================================
    # 步骤 6: 绘制历史趋势 + 预测曲线图
    # ============================================================
    print("\n--- 步骤 6: 绘制趋势图 ---")

    fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
    x = range(len(monthly))
    labels = monthly['month_str'].tolist()

    # 历史实际值
    ax.plot(x, monthly[sales_col], marker='o', label='实际销售额', color='#2c3e50', linewidth=2)

    # SMA_3
    ax.plot(x, monthly['SMA_3'], marker='s', label='SMA(3)', color='#3498db', linewidth=1.5, linestyle='--')

    # SMA_6
    ax.plot(x, monthly['SMA_6'], marker='^', label='SMA(6)', color='#e67e22', linewidth=1.5, linestyle='--')

    # SES
    ax.plot(x, monthly['SES'], marker='d', label='SES', color='#e74c3c', linewidth=1.5, linestyle='-.')

    ax.set_xlabel('月份')
    ax.set_ylabel('销售额 (USD)')
    ax.set_title('月度销售额趋势与预测')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, 'sales_forecast_trend.png', output_dir, PLT_CONFIG['dpi'])
    plt.close()

    # 预测误差对比图
    if len(error_df) > 0:
        fig2, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].bar(error_df['Method'], error_df['MAE'], color=['#3498db', '#e67e22', '#e74c3c'])
        axes[0].set_title('MAE 对比')
        axes[0].set_ylabel('MAE')

        axes[1].bar(error_df['Method'], error_df['RMSE'], color=['#3498db', '#e67e22', '#e74c3c'])
        axes[1].set_title('RMSE 对比')
        axes[1].set_ylabel('RMSE')

        plt.suptitle('预测误差对比', fontsize=14)
        plt.tight_layout()
        save_figure(fig2, 'forecast_error_comparison.png', output_dir, PLT_CONFIG['dpi'])
        plt.close()

    # ============================================================
    # 步骤 7: 生成销售趋势预测报告
    # ============================================================
    print("\n--- 步骤 7: 生成销售趋势预测报告 ---")

    error_table = error_df.to_markdown(index=False) if hasattr(error_df, 'to_markdown') else error_df.to_string(index=False)

    report_content = f"""# 销售趋势预测报告

## 背景

本报告基于 ch01 清洗后的 {len(df)} 条销售记录，对月度销售额进行趋势预测。
通过简单移动平均（SMA）和指数平滑（SES）等时间序列方法，预测未来销售额走势，
为库存规划和销售策略提供数据支撑。

## 分析方法

1. **数据聚合**：按月汇总 Total_Sales_USD，构建月度时间序列
2. **简单移动平均（SMA）**：分别使用窗口 3 和窗口 6 计算移动平均值
3. **指数平滑（SES）**：使用简单指数平滑模型进行趋势拟合和预测
4. **误差评估**：计算各方法的 MAE（平均绝对误差）和 RMSE（均方根误差）

## 分析发现

### 月度销售额概览
- 数据点数：{len(monthly)} 个月
- 月均销售额：${{monthly[sales_col].mean():,.0f}}
- 最高月销售额：${{monthly[sales_col].max():,.0f}}
- 最低月销售额：${{monthly[sales_col].min():,.0f}}

### 预测结果
- SMA(3) 预测值：${{sma3_forecast:,.0f}}
- SMA(6) 预测值：${{sma6_forecast:,.0f}}
- SES 预测值：${{ses_forecast:,.0f}}

### 预测误差对比
{error_table}

## 小结

- 产物清单：monthly_sales.csv, forecast_errors.csv, sales_forecast_trend.png, forecast_error_comparison.png
- 通过 SMA 和 SES 方法对月度销售额进行了趋势预测，误差评估为模型选择提供了依据
- 对下游章节的影响：为 ch05 业务建议提供销售趋势预测数据支撑
"""
    report_path = save_markdown(report_content, output_dir / "report.md")
    print(f"销售趋势预测报告已保存至: {report_path}")

    print("\n" + "=" * 60)
    print("ch03 销售趋势预测 - 执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
