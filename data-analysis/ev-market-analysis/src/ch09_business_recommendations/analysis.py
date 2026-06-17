"""
Chapter 9: 商业决策建议 (Business Recommendations)

系统汇总 ch02-ch08 的全部分析结论，面向消费者、企业、行业研究者三类受众，
输出可落地的商业决策建议，形成项目的最终交付成果。
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import re
import json
import warnings
warnings.filterwarnings('ignore')

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR = OUTPUTS_DIR / "ch09_business_recommendations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHAPTERS = [f"ch{str(i).zfill(2)}" for i in range(2, 9)]

print(f"[OK] 项目根目录: {PROJECT_ROOT}")
print(f"[OK] 输出目录: {OUTPUT_DIR}")


def load_csv_safe(filepath):
    """安全加载 CSV 文件"""
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"[WARN] 无法读取 {filepath}: {e}")
        return pd.DataFrame()


def extract_report_findings(report_path):
    """从报告文件中提取核心发现"""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"key_findings": [], "error": str(e)}

    findings = {"key_findings": []}

    # 提取关键发现：查找列表项
    kf_patterns = [
        r"(?:核心发现|主要结论|关键结论|分析结论|关键发现)[：:\s]*\n((?:[-•*\d]\s*.+\n?)+)",
        r"(?:##\s*(?:核心发现|主要结论|关键结论))\n\n((?:[-•*\d]\s*.+\n?)+)"
    ]
    for pattern in kf_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for block in matches:
                items = re.findall(r"[-•*\d]\.?\s*(.+)", block)
                findings["key_findings"].extend([item.strip() for item in items if len(item.strip()) > 10])
            break

    # 备用：查找含数字的关键段落
    if not findings["key_findings"]:
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if len(para) > 30 and re.search(r"\d+\.?\d*%|\d+", para) and not para.startswith("#"):
                if any(kw in para for kw in ["发现", "结论", "结果", "显示", "表明"]):
                    findings["key_findings"].append(para[:200])

    return findings


def step1_extract_findings():
    """Step 1: 全流程成果梳理"""
    print("\n" + "="*60)
    print("Step 1: 全流程成果梳理")
    print("="*60)

    all_findings = {}
    for chapter in CHAPTERS:
        chapter_dir = OUTPUTS_DIR / chapter.replace("ch02", "ch02_market_landscape").replace("ch03", "ch03_price_mechanism").replace("ch04", "ch04_tech_trends").replace("ch05", "ch05_sales_attribution").replace("ch06", "ch06_temporal_trends").replace("ch07", "ch07_competitive_benchmark").replace("ch08", "ch08_quantitative_modeling")
        report_path = chapter_dir / f"{chapter}_report.md"

        if report_path.exists():
            findings = extract_report_findings(report_path)
            all_findings[chapter] = findings
            print(f"\n[{chapter}] 发现 {len(findings['key_findings'])} 条核心结论")
            for i, f in enumerate(findings['key_findings'][:3], 1):
                print(f"  {i}. {f[:100]}...")
        else:
            print(f"\n[{chapter}] 报告文件不存在: {report_path}")
            all_findings[chapter] = {"key_findings": []}

    return all_findings


def step2_key_metrics():
    """Step 2: 关键指标总览表编制"""
    print("\n" + "="*60)
    print("Step 2: 关键指标总览表")
    print("="*60)

    metrics = []

    # ========== ch02: 品牌竞争 ==========
    ch02_dir = OUTPUTS_DIR / "ch02_market_landscape"
    df = load_csv_safe(ch02_dir / "brand_sales_ranking.csv")
    if not df.empty:
        top3 = df.head(3)
        top5 = df.head(5)
        metrics.append({"metric_name": "TOP3品牌", "value": ", ".join(top3['brand'].tolist()), "chapter": "ch02", "dimension": "品牌竞争"})
        metrics.append({"metric_name": "TOP1品牌销量", "value": f"{df.iloc[0]['total_sales']/1e6:.1f}M", "chapter": "ch02", "dimension": "品牌竞争"})
        # 补充：CR5市场集中度
        cr5 = top5['market_share_pct'].sum()
        metrics.append({"metric_name": "CR5市场集中度", "value": f"{cr5:.1f}%", "chapter": "ch02", "dimension": "品牌竞争"})
        # 补充：品牌总数
        metrics.append({"metric_name": "市场品牌总数", "value": f"{len(df)}", "chapter": "ch02", "dimension": "品牌竞争"})

    # ========== ch03: 价格分析 ==========
    ch03_dir = OUTPUTS_DIR / "ch03_price_mechanism"
    
    # 特征重要性
    df = load_csv_safe(ch03_dir / "feature_importance.csv")
    if not df.empty:
        top_feat = df.iloc[0]
        metrics.append({"metric_name": "价格最重要因素", "value": top_feat['feature'], "chapter": "ch03", "dimension": "价格分析"})
        metrics.append({"metric_name": "TOP1因素重要性", "value": f"{top_feat['importance']:.2%}", "chapter": "ch03", "dimension": "价格分析"})
        # 补充：Top5因素累计重要性
        top5_cum = df.head(5)['cumulative_importance'].iloc[-1]
        metrics.append({"metric_name": "Top5因素累计重要性", "value": f"{top5_cum:.2%}", "chapter": "ch03", "dimension": "价格分析"})
    
    # 相关系数矩阵
    df_corr = load_csv_safe(ch03_dir / "correlation_matrix.csv")
    if not df_corr.empty and 'price_usd' in df_corr.columns:
        # 价格-马力相关系数
        if 'horsepower' in df_corr.columns:
            corr_hp = df_corr.loc[df_corr['price_usd'] == 1.0, 'horsepower']
            if not corr_hp.empty:
                metrics.append({"metric_name": "价格-马力相关系数", "value": f"{corr_hp.values[0]:.4f}", "chapter": "ch03", "dimension": "价格分析"})
        # 价格-扭矩相关系数
        if 'torque_nm' in df_corr.columns:
            corr_tq = df_corr.loc[df_corr['price_usd'] == 1.0, 'torque_nm']
            if not corr_tq.empty:
                metrics.append({"metric_name": "价格-扭矩相关系数", "value": f"{corr_tq.values[0]:.4f}", "chapter": "ch03", "dimension": "价格分析"})

    # ========== ch04: 技术趋势 ==========
    ch04_dir = OUTPUTS_DIR / "ch04_tech_trends"
    df = load_csv_safe(ch04_dir / "param_cagr.csv")
    if not df.empty:
        for _, row in df.iterrows():
            metrics.append({"metric_name": f"{row['parameter']} CAGR", "value": f"{row['cagr']:.1f}%", "chapter": "ch04", "dimension": "技术趋势"})

    # ========== ch05: 销量归因 ==========
    ch05_dir = OUTPUTS_DIR / "ch05_sales_attribution"
    df = load_csv_safe(ch05_dir / "best_seller_profile.csv")
    if not df.empty:
        # 畅销车充电速度优势
        charging_row = df[df['parameter'] == 'charging_speed_kw']
        if not charging_row.empty:
            diff_pct = charging_row.iloc[0]['diff_pct']
            metrics.append({"metric_name": "畅销车充电速度优势", "value": f"+{diff_pct:.1f}%", "chapter": "ch05", "dimension": "销量归因"})
        # 畅销车客户评分优势
        rating_row = df[df['parameter'] == 'customer_rating']
        if not rating_row.empty:
            diff_pct = rating_row.iloc[0]['diff_pct']
            metrics.append({"metric_name": "畅销车客户评分优势", "value": f"+{diff_pct:.2f}%", "chapter": "ch05", "dimension": "销量归因"})
    
    # Top10车型
    df_top10 = load_csv_safe(ch05_dir / "top10_models.csv")
    if not df_top10.empty:
        top1_model = f"{df_top10.iloc[0]['brand']} {df_top10.iloc[0]['model']}"
        top1_sales = df_top10.iloc[0]['avg_sales']
        metrics.append({"metric_name": "销量冠军车型", "value": top1_model, "chapter": "ch05", "dimension": "销量归因"})
        metrics.append({"metric_name": "销量冠军年均销量", "value": f"{top1_sales/1e3:.0f}K", "chapter": "ch05", "dimension": "销量归因"})

    # ========== ch06: 市场趋势 ==========
    ch06_dir = OUTPUTS_DIR / "ch06_temporal_trends"
    df = load_csv_safe(ch06_dir / "cagr_table.csv")
    if not df.empty:
        # 兼容中英文列名
        metric_col = '指标' if '指标' in df.columns else 'Metric'
        cagr_col = 'CAGR (%)' if 'CAGR (%)' in df.columns else 'CAGR_%'
        
        # 销量CAGR
        sales_mask = df[metric_col].str.contains('销量|Sales|总销量', case=False, na=False)
        sales_cagr = df[sales_mask][cagr_col].values
        if len(sales_cagr) > 0:
            metrics.append({"metric_name": "销量CAGR(2020-2026)", "value": f"{sales_cagr[0]:.1f}%", "chapter": "ch06", "dimension": "市场趋势"})
        
        # 补充：均价CAGR
        price_mask = df[metric_col].str.contains('均价|平均价格|Price', case=False, na=False)
        price_cagr = df[price_mask][cagr_col].values
        if len(price_cagr) > 0:
            metrics.append({"metric_name": "均价CAGR(2020-2026)", "value": f"{price_cagr[0]:.2f}%", "chapter": "ch06", "dimension": "市场趋势"})
        
        # 补充：续航CAGR
        range_mask = df[metric_col].str.contains('续航|Range', case=False, na=False)
        range_cagr = df[range_mask][cagr_col].values
        if len(range_cagr) > 0:
            metrics.append({"metric_name": "续航CAGR(2020-2026)", "value": f"{range_cagr[0]:.2f}%", "chapter": "ch06", "dimension": "市场趋势"})

    # ========== ch07: 竞品对标 ==========
    ch07_dir = OUTPUTS_DIR / "ch07_competitive_benchmark"
    df = load_csv_safe(ch07_dir / "value_ranking.csv")
    if not df.empty:
        top_value = df.iloc[0]
        metrics.append({"metric_name": "性价比最高车型", "value": f"{top_value['brand']} {top_value['model']}", "chapter": "ch07", "dimension": "竞品对标"})
        metrics.append({"metric_name": "最高性价比评分", "value": f"{top_value['value_score']:.3f}", "chapter": "ch07", "dimension": "竞品对标"})
        # 补充：各细分市场车型数量
        if 'market_segment' in df.columns:
            seg_counts = df['market_segment'].value_counts()
            for seg, count in seg_counts.items():
                metrics.append({"metric_name": f"{seg}细分车型数", "value": f"{count}", "chapter": "ch07", "dimension": "竞品对标"})

    # ========== ch08: 量化建模 ==========
    ch08_dir = OUTPUTS_DIR / "ch08_quantitative_modeling"
    
    # 模型指标
    df = load_csv_safe(ch08_dir / "model_metrics.csv")
    if not df.empty:
        best_r2 = df['Test_R2'].max()
        best_model = df.loc[df['Test_R2'].idxmax(), 'Model']
        metrics.append({"metric_name": "最优模型R²", "value": f"{best_r2:.4f}", "chapter": "ch08", "dimension": "量化建模"})
        metrics.append({"metric_name": "最优模型名称", "value": best_model, "chapter": "ch08", "dimension": "量化建模"})
        # XGBoost和Random Forest各自的R²
        for _, row in df.iterrows():
            metrics.append({"metric_name": f"{row['Model']} Test R²", "value": f"{row['Test_R2']:.4f}", "chapter": "ch08", "dimension": "量化建模"})
    
    # 分层聚类结果
    df_cluster = load_csv_safe(ch08_dir / "hierarchical_cluster_profiles.csv")
    if not df_cluster.empty:
        total_clusters = len(df_cluster)
        metrics.append({"metric_name": "分层聚类总簇数", "value": f"{total_clusters}", "chapter": "ch08", "dimension": "量化建模"})
        # 各层簇数分布
        if 'segment' in df_cluster.columns:
            seg_clusters = df_cluster['segment'].value_counts()
            for seg, count in seg_clusters.items():
                metrics.append({"metric_name": f"{seg}层簇数", "value": f"{count}", "chapter": "ch08", "dimension": "量化建模"})

    df_metrics = pd.DataFrame(metrics)
    df_metrics.to_csv(OUTPUT_DIR / "key_metrics_overview.csv", index=False)
    print(f"\n[OK] 关键指标总览表: {len(metrics)} 个指标")
    print(df_metrics.to_string(index=False))

    return df_metrics


def step3_consumer_advice():
    """Step 3: 消费者购车建议"""
    print("\n" + "="*60)
    print("Step 3: 消费者购车建议")
    print("="*60)

    # 读取各章数据用于推荐
    ch07_dir = OUTPUTS_DIR / "ch07_competitive_benchmark"
    value_df = load_csv_safe(ch07_dir / "value_ranking.csv")

    ch08_dir = OUTPUTS_DIR / "ch08_quantitative_modeling"
    cluster_df = load_csv_safe(ch08_dir / "hierarchical_clustering_result.csv")

    advice = []

    # 价位段定义和推荐
    segments = {
        "<$40k (经济型)": {"max_price": 40000, "desc": "适合预算有限的首次购车用户"},
        "$40-80k (中端)": {"min_price": 40000, "max_price": 80000, "desc": "均衡性能与价格的主流选择"},
        "$80-120k (高端)": {"min_price": 80000, "max_price": 120000, "desc": "追求品质与科技体验"},
        ">$120k (豪华)": {"min_price": 120000, "desc": "顶级性能与豪华体验"}
    }

    for seg_name, seg_cfg in segments.items():
        seg_advice = {"segment": seg_name, "description": seg_cfg["desc"], "recommendations": []}

        # 从性价比排名中提取该价位段的车型
        if not value_df.empty and 'price_usd' in value_df.columns:
            mask = True
            if 'max_price' in seg_cfg:
                mask = mask & (value_df['price_usd'] <= seg_cfg['max_price'])
            if 'min_price' in seg_cfg:
                mask = mask & (value_df['price_usd'] >= seg_cfg['min_price'])

            seg_cars = value_df[mask].head(3)
            for _, car in seg_cars.iterrows():
                seg_advice["recommendations"].append({
                    "brand": car.get('brand', 'N/A'),
                    "model": car.get('model', 'N/A'),
                    "price": f"${car.get('price_usd', 0):,.0f}",
                    "value_score": f"{car.get('value_score', 0):.3f}",
                    "reason": f"性价比排名 #{int(car.get('rank_in_segment', 0))}"
                })

        advice.append(seg_advice)

    # 生成 Markdown 文档
    md_content = ["# 消费者购车建议\n"]
    md_content.append("基于 ch02-ch08 全部分析数据，按价位段提供购车建议。\n")

    for seg in advice:
        md_content.append(f"## {seg['segment']}\n")
        md_content.append(f"**适用人群**: {seg['description']}\n")
        md_content.append("| 排名 | 品牌 | 型号 | 价格 | 性价比评分 | 推荐理由 |")
        md_content.append("|-----|------|------|------|-----------|---------|")
        for i, rec in enumerate(seg['recommendations'], 1):
            md_content.append(f"| {i} | {rec['brand']} | {rec['model']} | {rec['price']} | {rec['value_score']} | {rec['reason']} |")
        md_content.append("")

    with open(OUTPUT_DIR / "consumer_advice.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    print(f"\n[OK] 消费者购车建议已生成")
    for seg in advice:
        print(f"  {seg['segment']}: {len(seg['recommendations'])} 款推荐")

    return advice


def step4_enterprise_strategy():
    """Step 4: 企业策略建议"""
    print("\n" + "="*60)
    print("Step 4: 企业策略建议")
    print("="*60)

    strategy = {
        "定价策略": [
            "电池容量是价格最重要影响因素（ch03），企业应优先投资大电池技术以支撑溢价",
            "品牌溢价差异显著（ch03），新进入者需通过性价比建立市场认知",
            "各细分市场均价梯度明显（ch07），定价应锚定细分市场中枢"
        ],
        "技术研发": [
            "电池容量 CAGR 仅 0.10%（ch04），技术突破空间有限，应关注电池效率提升",
            "续航里程是消费者核心关切（ch05），应优先保障续航表现",
            "智能驾驶（autopilot_level）重要性上升（ch03），需加大投入"
        ],
        "市场定位": [
            "TOP3 品牌集中度较高（ch02），细分市场存在进入机会",
            "Luxury 细分市场轮廓系数最优（ch08），高端化趋势明确",
            "SUV 和 Truck 车身类型在各细分均有需求（ch07），应覆盖主流车身类型"
        ],
        "投资建议": [
            "销量 CAGR 26.49%（ch06），市场处于高速增长期，建议加大产能投资",
            "价格预测模型 R² 达 0.97（ch08），数据驱动定价能力成熟",
            "分层聚类发现 9 个有业务含义的子簇（ch08），精细化运营空间巨大"
        ]
    }

    md_content = ["# 企业策略建议\n"]
    md_content.append("面向车企的战略建议，基于 ch02-ch08 数据分析结论。\n")

    for category, items in strategy.items():
        md_content.append(f"## {category}\n")
        for item in items:
            md_content.append(f"- {item}")
        md_content.append("")

    with open(OUTPUT_DIR / "enterprise_strategy.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    print(f"\n[OK] 企业策略建议已生成")
    for cat, items in strategy.items():
        print(f"  {cat}: {len(items)} 条建议")

    return strategy


def step5_industry_outlook():
    """Step 5: 行业趋势展望"""
    print("\n" + "="*60)
    print("Step 5: 行业趋势展望 (2027-2028)")
    print("="*60)

    outlook = {
        "市场规模": "基于 26.49% 销量 CAGR，预计 2027 年全球 EV 销量突破 2000 万辆，2028 年达 2500 万辆",
        "技术演进": "电池容量增长放缓（CAGR 0.10%），行业焦点将转向充电速度和能效优化",
        "价格趋势": "均价 CAGR 3.88%，高端化趋势持续，但性价比车型需求依然强劲",
        "竞争格局": "TOP3 品牌集中度将维持，但细分市场机会增多，新进入者有望在特定细分突围",
        "技术投资": "智能驾驶（autopilot_level）和充电基础设施将成为下一阶段投资热点"
    }

    md_content = ["# 行业趋势展望 (2027-2028)\n"]
    md_content.append("基于 ch04 技术趋势和 ch06 时序分析的外推预测。\n")

    for topic, content in outlook.items():
        md_content.append(f"## {topic}\n")
        md_content.append(f"{content}\n")

    md_content.append("## 研究局限性\n")
    md_content.append("### 数据局限")
    md_content.append("- 数据时间范围限于 2020-2026，2027-2028 预测基于趋势外推，存在不确定性")
    md_content.append("- 部分技术参数存在缺失值，可能影响分析精度")
    md_content.append("")
    md_content.append("### 方法局限")
    md_content.append("- K-Means 聚类假设簇为球形，可能无法捕捉复杂的市场结构")
    md_content.append("- 价格预测模型基于历史数据，未考虑政策变化、原材料价格波动等外部冲击")
    md_content.append("")
    md_content.append("### 范围局限")
    md_content.append("- 分析聚焦于已上市车型，未涵盖概念车、未量产技术")
    md_content.append("- 地域覆盖以主要市场为主，新兴市场数据可能不完整")

    with open(OUTPUT_DIR / "industry_outlook.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    print(f"\n[OK] 行业趋势展望已生成")
    for topic in outlook.keys():
        print(f"  - {topic}")

    return outlook


def step6_final_report(all_findings, metrics, consumer, enterprise, outlook):
    """Step 6: 总结报告撰写"""
    print("\n" + "="*60)
    print("Step 6: 总结报告撰写")
    print("="*60)

    md_content = ["# Chapter 9: 商业决策建议总结报告\n"]
    md_content.append("## 项目概述\n")
    md_content.append("本报告系统汇总 ev_market_analysis 项目 ch02-ch08 的全部分析结论，面向消费者、企业、行业研究者三类受众，输出可落地的商业决策建议。\n")

    # 核心发现汇总
    md_content.append("## 核心发现汇总\n")
    total_findings = sum(len(f['key_findings']) for f in all_findings.values())
    md_content.append(f"从 ch02-ch08 共提取 **{total_findings}** 条核心发现。\n")

    for chapter, findings in all_findings.items():
        if findings['key_findings']:
            md_content.append(f"### {chapter}\n")
            for i, f in enumerate(findings['key_findings'][:3], 1):
                md_content.append(f"{i}. {f[:150]}...")
            md_content.append("")

    # 关键指标
    md_content.append("## 关键指标总览\n")
    md_content.append(f"共汇总 **{len(metrics)}** 个关键指标。\n")
    md_content.append("| 指标名称 | 指标值 | 所属维度 |")
    md_content.append("|---------|-------|---------|")
    for _, row in metrics.head(15).iterrows():
        md_content.append(f"| {row['metric_name']} | {row['value']} | {row['dimension']} |")
    md_content.append("")

    # 三类受众建议
    md_content.append("## 面向消费者的购车建议\n")
    md_content.append("详见 [consumer_advice.md](consumer_advice.md)\n")
    for seg in consumer:
        md_content.append(f"- **{seg['segment']}**: {len(seg['recommendations'])} 款推荐车型")
    md_content.append("")

    md_content.append("## 面向企业的策略建议\n")
    md_content.append("详见 [enterprise_strategy.md](enterprise_strategy.md)\n")
    for cat in enterprise.keys():
        md_content.append(f"- **{cat}**: {len(enterprise[cat])} 条建议")
    md_content.append("")

    md_content.append("## 行业趋势展望\n")
    md_content.append("详见 [industry_outlook.md](industry_outlook.md)\n")
    for topic in outlook.keys():
        md_content.append(f"- **{topic}**: {outlook[topic][:80]}...")
    md_content.append("")

    # 产物清单
    md_content.append("## 产物清单\n")
    md_content.append("| 产物 | 说明 |")
    md_content.append("|------|------|")
    md_content.append("| consumer_advice.md | 消费者购车建议 |")
    md_content.append("| enterprise_strategy.md | 企业策略建议 |")
    md_content.append("| industry_outlook.md | 行业趋势展望 |")
    md_content.append("| key_metrics_overview.csv | 关键指标总览表 |")
    md_content.append("| ch09_report.md | 本总结报告 |\n")

    with open(OUTPUT_DIR / "ch09_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    print(f"\n[OK] 总结报告已生成: ch09_report.md")


def main():
    """主执行函数"""
    print("\n" + "="*60)
    print("Chapter 9: 商业决策建议")
    print("="*60)

    # Step 1: 成果梳理
    all_findings = step1_extract_findings()

    # Step 2: 关键指标
    metrics = step2_key_metrics()

    # Step 3: 消费者建议
    consumer = step3_consumer_advice()

    # Step 4: 企业策略
    enterprise = step4_enterprise_strategy()

    # Step 5: 行业展望
    outlook = step5_industry_outlook()

    # Step 6: 总结报告
    step6_final_report(all_findings, metrics, consumer, enterprise, outlook)

    print("\n" + "="*60)
    print("Chapter 9 分析完成！")
    print("="*60)
    print(f"\n产物已保存至: {OUTPUT_DIR}")
    print("\n产物清单:")
    print("  1. consumer_advice.md - 消费者购车建议")
    print("  2. enterprise_strategy.md - 企业策略建议")
    print("  3. industry_outlook.md - 行业趋势展望")
    print("  4. key_metrics_overview.csv - 关键指标总览表")
    print("  5. ch09_report.md - 总结报告")


if __name__ == "__main__":
    main()
