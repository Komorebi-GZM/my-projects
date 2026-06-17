"""
Genesis_Anomaly_Analysis - 输出管理模块 (v2.2)
增强 generate_report_md 支持自动从CSV产物注入数据和图引用
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Any, List, Dict
import sys
import os

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ensure_output_dir


def save_dataframe(df: pd.DataFrame, 
                   filename: str, 
                   chapter_id: str,
                   index: bool = False) -> str:
    """保存 DataFrame 为 CSV 文件"""
    output_dir = ensure_output_dir(chapter_id)
    filepath = output_dir / filename
    df.to_csv(filepath, index=index, encoding='utf-8-sig')
    print(f"✓ 已保存: {filepath}")
    return str(filepath)


def save_figure(fig: plt.Figure, 
                filename: str, 
                chapter_id: str,
                dpi: int = 150) -> str:
    """保存图表为 PNG 文件"""
    output_dir = ensure_output_dir(chapter_id)
    figures_dir = output_dir / 'figures'
    filepath = figures_dir / filename
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"✓ 已保存: {filepath}")
    return str(filepath)


def save_markdown(content: str, 
                  filename: str, 
                  chapter_id: str) -> str:
    """保存 Markdown 报告"""
    output_dir = ensure_output_dir(chapter_id)
    filepath = output_dir / filename
    filepath.write_text(content, encoding='utf-8')
    print(f"✓ 已保存: {filepath}")
    return str(filepath)


def _df_to_markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    """将 DataFrame 转为 Markdown 表格字符串"""
    if df.empty:
        return ""
    show_df = df.head(max_rows)
    return show_df.to_markdown(index=False, floatfmt=".3f")


def _collect_output_images(chapter_id: str) -> List[str]:
    """收集章节输出目录下的所有PNG文件名"""
    output_dir = ensure_output_dir(chapter_id)
    figures_dir = output_dir / 'figures'
    images = []
    if figures_dir.exists():
        images = sorted([f.name for f in figures_dir.glob('*.png')])
    # 也检查根目录
    for f in output_dir.glob('*.png'):
        if f.name not in images:
            images.append(f.name)
    return images


def _collect_output_csvs(chapter_id: str) -> List[str]:
    """收集章节输出目录下的所有CSV文件名"""
    output_dir = ensure_output_dir(chapter_id)
    return sorted([f.name for f in output_dir.glob('*.csv')])


def generate_report_md(chapter_id: str,
                       chapter_title: str,
                       background: str,
                       methods: str,
                       findings: str,
                       conclusion: str,
                       csv_tables: Optional[Dict[str, pd.DataFrame]] = None,
                       image_captions: Optional[Dict[str, str]] = None,
                       chapter_type: str = '分析探索型',
                       priority: str = 'P1') -> str:
    """
    生成 report.md 内容（v2.2 强约束四段框架）
    
    Args:
        chapter_id: 章节ID（如 'ch01'）
        chapter_title: 章节标题
        background: 背景内容（≥80字）
        methods: 分析方法内容（≥60字）
        findings: 分析发现内容（≥200字，应包含表格和图引用）
        conclusion: 小结内容（≥80字）
        csv_tables: 可选，{csv_filename: DataFrame} 用于自动生成表格
        image_captions: 可选，{image_filename: 描述} 用于自动生成图引用
        chapter_type: 章节类型
        priority: 优先级
    
    Returns:
        Markdown 内容
    """
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 章节编号
    ch_num = chapter_id.replace('ch', '')
    
    # 自动收集图片（如果未手动提供）
    all_images = _collect_output_images(chapter_id)
    
    # 构建背景段
    bg_section = f"## {ch_num}.1 研究背景与目标\n{background}"
    
    # 构建方法段
    method_section = f"## {ch_num}.2 分析方法\n{methods}"
    
    # 构建发现段（自动注入表格和图引用）
    findings_parts = [f"## {ch_num}.3 分析发现\n"]
    
    # 如果提供了 csv_tables，自动生成子表格
    if csv_tables:
        for csv_name, df in csv_tables.items():
            if not df.empty:
                table_md = _df_to_markdown_table(df)
                if table_md:
                    findings_parts.append(f"### {csv_name.replace('.csv', '').replace('_', ' ').title()}\n{table_md}\n")
    
    # 附加手动 findings 文本
    findings_parts.append(findings)
    
    # 自动生成图引用（如果发现段中没有图引用，自动添加）
    has_image_ref = '![' in findings
    if not has_image_ref and image_captions:
        findings_parts.append("\n### 可视化图表\n")
        for img_name, caption in image_captions.items():
            findings_parts.append(f"![{caption}](figures/{img_name})\n")
    elif not has_image_ref and all_images:
        findings_parts.append("\n### 可视化图表\n")
        for img_name in all_images[:3]:  # 最多引用3张
            findings_parts.append(f"![{img_name.replace('.png', '')}](figures/{img_name})\n")
    
    findings_section = "\n".join(findings_parts)
    
    # 构建小结段
    conclusion_section = f"## {ch_num}.4 关键洞察与小结\n{conclusion}"
    
    # 组装完整报告
    content = f"""# {chapter_id} {chapter_title}

> **章节类型**: {chapter_type} | **优先级**: {priority}

---

{bg_section}

{method_section}

{findings_section}

{conclusion_section}

---

*报告生成时间: {timestamp}*
*数据来源: Genesis 工业自动化数据集*
"""
    return content


def list_outputs(chapter_id: str) -> list:
    """列出章节输出目录中的所有文件"""
    output_dir = ensure_output_dir(chapter_id)
    return list(output_dir.rglob('*'))


def check_output_exists(chapter_id: str, filename: str) -> bool:
    """检查产物文件是否已存在"""
    output_dir = ensure_output_dir(chapter_id)
    return (output_dir / filename).exists()
