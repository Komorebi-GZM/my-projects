"""
ch03 异常检测与抗干扰分析
目标：对比正常与异常工况下传感器信号差异，提取故障敏感特征
依赖：ch02
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ensure_output_dir, ANOMALY_LABELS
from utils.data_loader import load_anomaly_data, split_by_label
from utils.visualizer import plot_comparison, plot_boxplot
from utils.metrics import perform_ttest, perform_ks_test, extract_time_features, calc_cohens_d
from utils.output_manager import save_dataframe, save_figure, save_markdown, generate_report_md

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

CHAPTER_ID = 'ch03'
CHAPTER_TITLE = '异常检测与抗干扰分析'


def main():
    print(f"\n{'='*60}")
    print(f"执行 {CHAPTER_ID}: {CHAPTER_TITLE}")
    print(f"{'='*60}\n")

    # 1. 数据加载
    print("[1/9] 加载 AnomalyLabels 数据...")
    df = load_anomaly_data()

    # 2. 按标签分组
    print("[2/9] 按 Label 分组...")
    groups = split_by_label(df)
    print(f"  Label=0 (正常): {len(groups[0])} 行")
    print(f"  Label=1 (卡滞): {len(groups[1])} 行")
    print(f"  Label=2 (脱扣): {len(groups[2])} 行")

    # 关键信号列表（按 Prompt-03 要求扩展为4路关键信号）
    key_signals = [
        'MotorData.ActCurrent',
        'MotorData.ActSpeed',
        'MotorData.IsAcceleration',
        'MotorData.IsForce',
    ]
    # 确保列存在
    key_signals = [s for s in key_signals if s in df.columns]
    print(f"  关键信号: {key_signals}")

    # 3. 描述性统计对比
    print("[3/9] 统计对比...")
    comparison_records = []

    for signal in key_signals:
        for label, group_df in groups.items():
            comparison_records.append({
                'signal': signal,
                'label': label,
                'mean': group_df[signal].mean(),
                'std': group_df[signal].std(),
                'min': group_df[signal].min(),
                'max': group_df[signal].max(),
                'count': len(group_df),
            })

    comparison_df = pd.DataFrame(comparison_records)
    # 计算相对差异百分比（异常组 vs 正常组）
    comparison_df['rel_diff_pct'] = np.nan
    for signal in key_signals:
        normal_mean = comparison_df.loc[
            (comparison_df['signal'] == signal) & (comparison_df['label'] == 0), 'mean'
        ].values[0]
        for label in [1, 2]:
            idx = comparison_df[
                (comparison_df['signal'] == signal) & (comparison_df['label'] == label)
            ].index
            if len(idx) > 0:
                anomaly_mean = comparison_df.loc[idx, 'mean'].values[0]
                comparison_df.loc[idx, 'rel_diff_pct'] = (
                    (anomaly_mean - normal_mean) / abs(normal_mean) * 100 if normal_mean != 0 else np.nan
                )

    # 4. 统计检验
    print("[4/9] 执行统计检验...")
    test_results = []
    normal_group = groups[0]

    for signal in key_signals:
        for anomaly_label in [1, 2]:
            if anomaly_label in groups:
                ttest = perform_ttest(normal_group[signal], groups[anomaly_label][signal])
                kstest = perform_ks_test(normal_group[signal], groups[anomaly_label][signal])
                test_results.append({
                    'signal': signal,
                    'anomaly_label': anomaly_label,
                    't_statistic': ttest['t_statistic'],
                    't_pvalue': ttest['p_value'],
                    't_significant': ttest['significant'],
                    'ks_statistic': kstest['ks_statistic'],
                    'ks_pvalue': kstest['p_value'],
                    'ks_significant': kstest['significant'],
                    'cohens_d': ttest['cohens_d'],
                })

    test_df = pd.DataFrame(test_results)

    # 5. 波形对比可视化
    print("[5/9] 绘制波形对比图...")
    fig, axes = plt.subplots(len(key_signals), 1, figsize=(14, 3 * len(key_signals)), sharex=False)
    if len(key_signals) == 1:
        axes = [axes]

    colors = {0: '#2E86AB', 1: '#F24236', 2: '#F6AE2D'}
    labels = {0: 'Normal', 1: 'Jammed', 2: 'BreakFree'}

    for ax, signal in zip(axes, key_signals):
        # 绘制正常组（采样，避免过多点）
        normal_sample = groups[0].sample(min(2000, len(groups[0])), random_state=42)
        ax.plot(normal_sample.index, normal_sample[signal], color=colors[0],
                alpha=0.4, linewidth=0.5, label=f"{labels[0]} (n={len(groups[0])})")

        # 绘制异常组
        for lbl in [1, 2]:
            if lbl in groups and len(groups[lbl]) > 0:
                ax.plot(groups[lbl].index, groups[lbl][signal], color=colors[lbl],
                        alpha=0.9, linewidth=1.2, marker='o', markersize=2,
                        label=f"{labels[lbl]} (n={len(groups[lbl])})")

        ax.set_ylabel(signal)
        ax.set_title(f"Signal Comparison: {signal}")
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel('Time')
    fig.suptitle('Normal vs Anomaly Signal Time-Series Overlay', fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    save_figure(fig, 'signal_comparison_normal_anomaly.png', CHAPTER_ID, dpi=150)

    # 6. 特征提取
    print("[6/9] 提取时域特征...")
    feature_records = []
    for signal in key_signals:
        for label, group_df in groups.items():
            features = extract_time_features(group_df[signal])
            features['signal'] = signal
            features['label'] = label
            feature_records.append(features)

    feature_df = pd.DataFrame(feature_records)

    # 7. 特征区分力评估
    print("[7/9] 评估特征区分力...")
    # 基于原始信号的统计检验结果，评估各特征（均值、标准差等）的区分力
    # 使用描述性统计中的相对差异百分比和统计检验中的效应量
    feature_importance_records = []

    for signal in key_signals:
        for anomaly_label in [1, 2]:
            # 获取该信号该异常类型的统计检验结果
            test_row = test_df[
                (test_df['signal'] == signal) & (test_df['anomaly_label'] == anomaly_label)
            ]
            if len(test_row) > 0:
                # 获取描述性统计中的相对差异
                comp_row = comparison_df[
                    (comparison_df['signal'] == signal) & (comparison_df['label'] == anomaly_label)
                ]
                rel_diff = comp_row['rel_diff_pct'].values[0] if len(comp_row) > 0 else np.nan

                feature_importance_records.append({
                    'signal': signal,
                    'anomaly_label': anomaly_label,
                    't_pvalue': test_row['t_pvalue'].values[0],
                    'ks_pvalue': test_row['ks_pvalue'].values[0],
                    'cohens_d': test_row['cohens_d'].values[0],
                    't_significant': test_row['t_significant'].values[0],
                    'ks_significant': test_row['ks_significant'].values[0],
                    'mean_rel_diff_pct': rel_diff,
                    'significant': test_row['t_significant'].values[0] or test_row['ks_significant'].values[0],
                })

    importance_df = pd.DataFrame(feature_importance_records)
    # 按显著性和效应量排序
    importance_df['abs_cohens_d'] = importance_df['cohens_d'].abs()
    importance_df['min_pvalue'] = importance_df[['t_pvalue', 'ks_pvalue']].min(axis=1)
    importance_df.sort_values(
        by=['significant', 'abs_cohens_d'],
        ascending=[False, False],
        inplace=True
    )

    # 绘制信号箱线图（基于原始数据）
    feature_names = ['mean', 'std', 'max', 'min', 'peak_to_peak', 'rms', 'skewness', 'kurtosis']
    fig, axes = plt.subplots(len(feature_names), len(key_signals),
                             figsize=(4 * len(key_signals), 3 * len(feature_names)))
    if len(key_signals) == 1:
        axes = axes.reshape(-1, 1)
    if len(feature_names) == 1:
        axes = axes.reshape(1, -1)

    for i, feat in enumerate(feature_names):
        for j, signal in enumerate(key_signals):
            ax = axes[i, j]
            plot_data = feature_df[feature_df['signal'] == signal][['label', feat]].copy()
            plot_data['label_name'] = plot_data['label'].map(labels)
            sns.boxplot(data=plot_data, x='label_name', y=feat, ax=ax, hue='label_name',
                        palette=[colors[0], colors[1], colors[2]], legend=False)
            ax.set_title(f"{signal}\n{feat}", fontsize=9)
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)

    plt.suptitle('Feature Boxplots by Group', fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    save_figure(fig, 'feature_boxplots_by_group.png', CHAPTER_ID, dpi=150)

    # 8. 保存产物
    print("[8/9] 保存产物...")
    save_dataframe(comparison_df, 'normal_vs_anomaly_stats.csv', CHAPTER_ID)
    save_dataframe(test_df, 'statistical_test_results.csv', CHAPTER_ID)
    save_dataframe(feature_df, 'distortion_features_table.csv', CHAPTER_ID)
    save_dataframe(importance_df, 'feature_importance_ranking.csv', CHAPTER_ID)

    # 9. 生成 report.md
    print("[9/9] 生成章节报告...")

    # 构建 findings 内容
    significant_signals = test_df[test_df['t_significant'] | test_df['ks_significant']]
    sig_summary = ""
    if len(significant_signals) > 0:
        sig_summary = "显著区分正常与异常的信号：\n"
        for _, row in significant_signals.iterrows():
            sig_summary += (
                f"- {row['signal']} vs Label={int(row['anomaly_label'])}: "
                f"t_p={row['t_pvalue']:.4f}, KS_p={row['ks_pvalue']:.4f}, Cohen's d={row['cohens_d']:.3f}\n"
            )
    else:
        sig_summary = "注意：由于异常样本极少（Label=1 仅39条，Label=2 仅11条），统计检验功效有限，未检测到显著差异。建议结合效应量（Cohen's d）进行解读。\n"

    top_features = importance_df.head(5)
    feat_summary = "关键故障特征排序（Top 5，按显著性+效应量排序）：\n"
    for rank, (_, row) in enumerate(top_features.iterrows(), 1):
        feat_summary += (
            f"{rank}. {row['signal']} (Label={int(row['anomaly_label'])}): "
            f"Cohen's d={row['cohens_d']:.3f}, min_p={row['min_pvalue']:.4f}, "
            f"mean_diff={row['mean_rel_diff_pct']:.1f}%\n"
        )

    findings_text = (
        f"异常样本共 {len(groups[1]) + len(groups[2])} 条，占总数据的 "
        f"{(len(groups[1]) + len(groups[2])) / len(df) * 100:.2f}%。\n\n"
        f"{sig_summary}\n"
        f"{feat_summary}\n"
        f"描述性统计对比已保存至 normal_vs_anomaly_stats.csv，"
        f"统计检验结果已保存至 statistical_test_results.csv，"
        f"畸变特征量化表已保存至 distortion_features_table.csv，"
        f"特征重要性排序已保存至 feature_importance_ranking.csv。"
    )

    conclusion_text = (
        "故障工况下传感器信号存在可观测的数值畸变，尤其体现在电流（ActCurrent）和力控（IsForce）信号上。"
        "由于异常样本极度稀少（仅50条，占比0.31%），传统统计检验功效不足，"
        "建议后续研究采用 SMOTE 过采样或基于物理模型的异常检测方法补充分析。"
        "本章节提取的时域特征为后续抗干扰特征工程提供了基础。"
    )

    report = generate_report_md(
        chapter_id=CHAPTER_ID,
        chapter_title=CHAPTER_TITLE,
        background="本章对比正常（Label=0）与异常工况（Label=1 直线驱动卡滞、Label=2 驱动脱扣校正）下传感器信号的差异，量化故障信号的畸变特征，探索性提取故障敏感特征，为故障预警提供特征工程基础。",
        methods="采用独立样本 t 检验和 Kolmogorov-Smirnov 检验对比正常与异常信号的均值和分布差异；计算 Cohen's d 效应量评估差异大小；提取时域统计特征（均值、标准差、最大值、最小值、峰峰值、均方根、峭度、偏度），通过箱线图和 p-value 排序评估特征区分力。",
        findings=findings_text,
        conclusion=conclusion_text,
        csv_tables={
            'feature_importance_ranking.csv': importance_df.head(10),
        },
        image_captions={
            'signal_comparison_normal_anomaly.png': '正常vs异常信号对比图',
            'feature_boxplots_by_group.png': '特征箱线图',
        },
    )
    save_markdown(report, 'report.md', CHAPTER_ID)

    print(f"\n{'='*60}")
    print(f"{CHAPTER_ID} 执行完成")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
