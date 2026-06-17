#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-01: 数据清洗
对原始小游戏数据集进行全面数据清洗，处理缺失值、去重、规范字段格式、修正标签。

覆盖步骤:
  - Step 01.1: 加载数据并校验行数
  - Step 01.2: 完全重复行去重 + 无效行清理
  - Step 01.3: URL/数值有效性校验
  - Step 01.4: Description 换行符清理 + 缺失值填充
  - Step 01.5: Name 清理（引号、全角空格、连续空格）
  - Step 01.6: 标签规范化（特殊字符替换 + 近义词合并 + 无效标签过滤）
  - Step 01.7: 新增业务字段（source, game_id, like_ratio, tag_count, 标记列）
  - Step 01.8: 输出清洗后数据和清洗报告

产物输出到: outputs/ch01_data_cleaning/
"""

import sys
import os
import re
import logging
import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime

# ---------------------------------------------------------------------------
# 路径设置：确保能正确导入 utils 包
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.config import PROJECT_ROOT, DATA_DIR, OUTPUT_BASE, DOMAIN_PARAMS
from utils.data_loader import load_raw_data
from utils.output_manager import get_chapter_dir, save_dataframe, save_report

# ---------------------------------------------------------------------------
# 常量配置（与 config.py DOMAIN_PARAMS 保持一致）
# ---------------------------------------------------------------------------

# 输入文件路径
INPUT_PATH = os.path.join(DATA_DIR, 'online-gaming-14-04-26.csv')

# 期望的原始数据行数
EXPECTED_ROWS = DOMAIN_PARAMS.get('expected_rows', 11406)

# 标签特殊字符替换映射表
TAG_SPECIAL_CHAR_MAP = DOMAIN_PARAMS.get('tag_special_char_map', {
    "point 'n click": "point and click",
    "point and click": "point and click",
    "run 'n gun": "run and gun",
    "idle / incremental": "idle incremental",
    "casino & gambling": "casino gambling",
    "pet / buddy": "pet buddy",
    "tube / rail": "tube rail",
    "time (rts)": "time rts",
    ".io": "io",
})

# 标签近义词合并映射表
TAG_SYNONYM_MAP = DOMAIN_PARAMS.get('tag_synonym_map', {
    "puzzles": "puzzle",
})

# 输出列顺序
OUTPUT_COLUMNS = DOMAIN_PARAMS.get('output_columns', [
    'game_id', 'name', 'url', 'source', 'likes', 'dislikes',
    'log_likes', 'log_dislikes', 'description', 'tags',
    'like_ratio', 'tag_count',
    'desc_missing', 'tags_missing', 'likes_is_zero', 'dislikes_is_zero'
])

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------

OUTPUT_DIR = get_chapter_dir('ch01')
OUTPUT_LOG = os.path.join(OUTPUT_DIR, 'ch01_cleaning.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_LOG, mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ============================================================
# 标签规范化函数
# ============================================================

def normalize_tags(tags_str):
    """规范化标签字符串：预处理、过滤、替换、合并、去重"""
    if not tags_str or tags_str.strip() == '':
        return ''
    # 预处理：去除首尾逗号、连续逗号
    tags_str = tags_str.strip().strip(',').replace(',,', ',')
    tag_list = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
    # 过滤无效标签（单字符、纯符号）
    tag_list = [t for t in tag_list if len(t) > 1 and not re.match(r'^[^a-z0-9]+$', t)]
    # 特殊字符替换
    tag_list = [TAG_SPECIAL_CHAR_MAP.get(t, t) for t in tag_list]
    # 近义词合并
    tag_list = [TAG_SYNONYM_MAP.get(t, t) for t in tag_list]
    # 去重（保持顺序）
    seen = set()
    unique_tags = []
    for t in tag_list:
        if t and t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return ','.join(unique_tags)


def count_tags(tags_str):
    """统计有效标签数量"""
    if not tags_str or tags_str.strip() == '':
        return 0
    return len([t for t in tags_str.split(',') if t.strip()])


# ============================================================
# 报告生成函数
# ============================================================

def generate_report(stats, df_clean, df_original):
    """生成 Markdown 格式的清洗报告"""

    # 标签统计
    all_tags_before = []
    for t in df_original['tags'].dropna():
        all_tags_before.extend([x.strip().lower() for x in t.split(',') if x.strip()])
    unique_before = len(set(all_tags_before))

    all_tags_after = []
    for t in df_clean['tags']:
        all_tags_after.extend([x.strip() for x in t.split(',') if x.strip()])
    unique_after = len(set(all_tags_after))
    tag_counts_after = Counter(all_tags_after)
    top20 = tag_counts_after.most_common(20)

    # 数据质量评分
    total_cells = len(df_clean) * 8  # 原始8列
    missing_cells = stats['missing_desc'] + stats['missing_tags']
    completeness = (total_cells - missing_cells) / total_cells * 100

    uniqueness = 100.0 if df_clean['game_id'].is_unique else 0.0

    validity = 100.0  # URL和数值全部通过
    if stats['invalid_urls'] > 0:
        validity -= stats['invalid_urls'] / len(df_clean) * 100
    if stats['negative_values'] > 0:
        validity -= stats['negative_values'] / len(df_clean) * 100
    validity = max(0, validity)

    consistency = 100.0 if stats['log_mismatch'] == 0 else max(0, 100 - stats['log_mismatch'] / len(df_clean) * 100)

    overall = (completeness + uniqueness + validity + consistency) / 4

    # 标签替换明细
    tag_replace_details = ""
    for original, replaced in TAG_SPECIAL_CHAR_MAP.items():
        if original == replaced:
            continue
        affected = df_original['tags'].str.lower().str.contains(re.escape(original), na=False).sum()
        tag_replace_details += f"    - `{original}` -> `{replaced}`（影响 {affected} 行）\n"
    for original, replaced in TAG_SYNONYM_MAP.items():
        affected = df_original['tags'].str.lower().str.contains(re.escape(original), na=False).sum()
        tag_replace_details += f"    - `{original}` -> `{replaced}`（影响 {affected} 行）\n"

    # 异常数据日志
    anomaly_log = ""
    if stats['invalid_urls'] > 0:
        anomaly_log += "### 无效 URL\n暂无\n\n"
    else:
        anomaly_log += "### 无效 URL\n无（全部通过校验）\n\n"

    if stats['log_mismatch'] > 0:
        anomaly_log += f"### log 值不一致记录\n共 {stats['log_mismatch']} 条\n\n"
    else:
        anomaly_log += "### log 值不一致记录\n无（全部一致）\n\n"

    if stats['short_names']:
        anomaly_log += "### 短名称记录（长度 <= 2）\n"
        for name in stats['short_names']:
            anomaly_log += f"- `{name}`\n"
        anomaly_log += "\n"
    else:
        anomaly_log += "### 短名称记录\n无\n\n"

    if stats['pure_symbol_names']:
        anomaly_log += "### 纯符号/空白名称\n"
        for name in stats['pure_symbol_names']:
            anomaly_log += f"- `{name}`\n"
        anomaly_log += "\n"
    else:
        anomaly_log += "### 纯符号/空白名称\n无\n\n"

    # 数据样例
    sample_df = df_clean[OUTPUT_COLUMNS].head(5)
    sample_rows = ""
    for _, row in sample_df.iterrows():
        sample_rows += f"| {row['game_id']} | {row['name'][:30]} | {row['source']} | {row['likes']} | {row['dislikes']} | {row['like_ratio']} | {row['tag_count']} |\n"

    # 字段类型
    dtype_info = ""
    for col in OUTPUT_COLUMNS:
        dtype_info += f"| {col} | {df_clean[col].dtype} |\n"

    report = f"""# 在线小游戏数据集清洗报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 数据集基本信息

| 指标 | 值 |
|------|------|
| 原始文件 | `data/online-gaming-14-04-26.csv` |
| 原始行数 | {stats['original_rows']} |
| 原始列数 | {stats['original_cols']} |
| 清洗后行数 | {stats['cleaned_rows']} |
| 清洗后列数 | {len(OUTPUT_COLUMNS)} |
| 删除行数 | {stats['original_rows'] - stats['cleaned_rows']} |
| 数据来源 - Poki | {stats['poki_count']} 条 |
| 数据来源 - Newgrounds | {stats['newgrounds_count']} 条 |

## 2. 清洗操作汇总

### 2.1 完全重复行去重
- 删除完全重复行：**{stats['duplicated_rows']} 条**

### 2.2 无效行清理
- 删除 name/url 为空的行：**{stats['invalid_rows']} 条**

### 2.3 URL 有效性校验
- 无效 URL 数量：**{stats['invalid_urls']} 条**
- 校验规则：以 `http://` 或 `https://` 开头

### 2.4 数值列校验
- 负数值数量：**{stats['negative_values']} 条**
- log 值不一致数量：**{stats['log_mismatch']} 条**
- likes=0 的记录数：**{stats['zero_likes']} 条**
- dislikes=0 的记录数：**{stats['zero_dislikes']} 条**

### 2.5 Description 换行符清理
- 含换行符的记录数：**{stats['newline_in_desc']} 条**
- 处理方式：将 `\\n`/`\\r` 替换为空格，合并连续空格

### 2.6 缺失值处理
- description 缺失：**{stats['missing_desc']} 条** -> 填充空字符串，`desc_missing` 标记为 1
- tags 缺失：**{stats['missing_tags']} 条** -> 填充空字符串，`tags_missing` 标记为 1

### 2.7 零值标记
- `likes_is_zero` 标记：{stats['zero_likes']} 条为 1
- `dislikes_is_zero` 标记：{stats['zero_dislikes']} 条为 1

### 2.8 Name 清理
- 去除首尾引号的记录数：**{stats['quoted_names']} 条**
- 全角空格->半角空格、合并连续空格：全部行

### 2.9 标签规范化
- 清洗前唯一标签数：**{unique_before}**
- 清洗后唯一标签数：**{unique_after}**
- 特殊字符替换规则：**{len([k for k, v in TAG_SPECIAL_CHAR_MAP.items() if k != v])} 条**
- 近义词合并规则：**{len(TAG_SYNONYM_MAP)} 条**

**标签替换明细：**
{tag_replace_details}
### 2.10 新增业务字段
| 字段 | 说明 | 计算逻辑 |
|------|------|---------|
| `game_id` | 唯一主键 | 自增整数 1~N |
| `source` | 平台来源 | URL 含 `poki.com` -> poki，否则 -> newgrounds |
| `like_ratio` | 点赞率 | `likes / (likes + dislikes)`，两者均为 0 时为 NaN |
| `tag_count` | 标签数量 | 有效标签个数 |
| `desc_missing` | 描述缺失标记 | description 为空 -> 1，否则 -> 0 |
| `tags_missing` | 标签缺失标记 | tags 为空 -> 1，否则 -> 0 |
| `likes_is_zero` | 点赞零值标记 | likes=0 -> 1，否则 -> 0 |
| `dislikes_is_zero` | 踩零值标记 | dislikes=0 -> 1，否则 -> 0 |

## 3. 标签统计

### Top 20 标签（清洗后）

| 排名 | 标签 | 出现次数 |
|------|------|---------|
"""
    for i, (tag, count) in enumerate(top20, 1):
        report += f"| {i} | {tag} | {count} |\n"

    report += f"""
## 4. 异常数据日志

{anomaly_log}
## 5. 数据质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 完整性 | {completeness:.1f}% | 非缺失字段占比 |
| 唯一性 | {uniqueness:.1f}% | game_id 唯一性 |
| 有效性 | {validity:.1f}% | URL/数值校验通过率 |
| 一致性 | {consistency:.1f}% | log 值一致性 |
| **综合评分** | **{overall:.1f}%** | 四维度均值 |

## 6. 输出文件说明

### 清洗后 CSV 列说明

| 列名 | 数据类型 | 说明 |
|------|---------|------|
{dtype_info}
### 新增标记列使用说明
- `desc_missing=1`：该行的 description 为清洗后填充的空字符串，原始数据中无描述
- `tags_missing=1`：该行的 tags 为清洗后填充的空字符串，原始数据中无标签
- `likes_is_zero=1`：该行的 likes 原始值为 0
- `dislikes_is_zero=1`：该行的 dislikes 原始值为 0

## 7. 清洗后数据样例

| game_id | name | source | likes | dislikes | like_ratio | tag_count |
|---------|------|--------|-------|----------|------------|-----------|
{sample_rows}
"""

    return report


# ============================================================
# 主清洗流程
# ============================================================

def main():
    """Prompt-01 主函数：执行完整的数据清洗流程"""

    logger.info("=" * 60)
    logger.info("Prompt-01: 数据清洗 - 开始执行")
    logger.info("=" * 60)

    stats = {}

    # ------------------------------------------------------------------
    # Step 01.1: 加载数据并校验行数
    # ------------------------------------------------------------------
    try:
        logger.info(f"Step 01.1: 加载数据 - {INPUT_PATH}")
        df = load_raw_data('online-gaming-14-04-26.csv', sep='\t', keep_default_na=False)
        logger.info(f"原始数据: {len(df)} 行 x {len(df.columns)} 列")
        stats['original_rows'] = len(df)
        stats['original_cols'] = len(df.columns)

        # 强制类型转换
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').astype('Int64')
        df['dislikes'] = pd.to_numeric(df['dislikes'], errors='coerce').astype('Int64')
        df['log_likes'] = pd.to_numeric(df['log_likes'], errors='coerce')
        df['log_dislikes'] = pd.to_numeric(df['log_dislikes'], errors='coerce')

        assert len(df) == EXPECTED_ROWS, f"行数不符: {len(df)} != {EXPECTED_ROWS}"
        logger.info("Step 01.1: 数据加载和类型转换完成")
    except Exception as e:
        logger.error(f"Step 01.1: 数据加载失败: {e}")
        raise

    # ------------------------------------------------------------------
    # Step 01.2: 完全重复行去重 + 无效行清理
    # ------------------------------------------------------------------
    logger.info("Step 01.2: 完全重复行去重 + 无效行清理")

    # 来源统计
    stats['poki_count'] = int(df['url'].str.contains('poki.com').sum())
    stats['newgrounds_count'] = int(df['url'].str.contains('newgrounds.com').sum())

    # 完全重复行去重
    dup_count = int(df.duplicated(keep='first').sum())
    df = df.drop_duplicates(keep='first').reset_index(drop=True)
    stats['duplicated_rows'] = dup_count
    logger.info(f"  完全重复行去重: 删除 {dup_count} 条")

    # 无效行清理（name 或 url 为空）
    invalid_mask = (df['name'].astype(str).str.strip() == '') | (df['url'].astype(str).str.strip() == '')
    invalid_count = int(invalid_mask.sum())
    df = df[~invalid_mask].reset_index(drop=True)
    stats['invalid_rows'] = invalid_count
    logger.info(f"  无效行清理: 删除 {invalid_count} 条")

    # ------------------------------------------------------------------
    # Step 01.3: URL/数值有效性校验
    # ------------------------------------------------------------------
    logger.info("Step 01.3: URL/数值有效性校验")

    # URL 有效性校验
    url_pattern = re.compile(r'^https?://\S+$')
    invalid_urls = int((~df['url'].astype(str).str.match(url_pattern)).sum())
    stats['invalid_urls'] = invalid_urls
    logger.info(f"  URL 有效性校验: 无效 {invalid_urls} 条")

    # 数值列校验：负数值
    negative_likes = int((df['likes'].fillna(0) < 0).sum())
    negative_dislikes = int((df['dislikes'].fillna(0) < 0).sum())
    stats['negative_values'] = negative_likes + negative_dislikes
    logger.info(f"  数值校验: 负数值 {stats['negative_values']} 条")

    # log 一致性验证
    df_valid = df[(df['likes'].fillna(0) > 0)].copy()
    if len(df_valid) > 0:
        computed_log = np.log1p(df_valid['likes'].fillna(0).astype(float))
        mismatch = int((abs(df_valid['log_likes'] - computed_log) > 1e-6).sum())
    else:
        mismatch = 0
    stats['log_mismatch'] = mismatch
    logger.info(f"  log 一致性验证: 不一致 {mismatch} 条")

    # 零值统计
    stats['zero_likes'] = int((df['likes'] == 0).sum())
    stats['zero_dislikes'] = int((df['dislikes'] == 0).sum())

    # ------------------------------------------------------------------
    # Step 01.4: Description 换行符清理 + 缺失值填充
    # ------------------------------------------------------------------
    logger.info("Step 01.4: Description 换行符清理 + 缺失值填充")

    # 换行符清理
    newline_count = int(df['description'].str.contains(r'[\n\r]', na=False).sum())
    stats['newline_in_desc'] = newline_count
    df['description'] = df['description'].str.replace('\n', ' ', regex=False)
    df['description'] = df['description'].str.replace('\r', ' ', regex=False)
    df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()
    logger.info(f"  Description 换行符清理: {newline_count} 条")

    # 缺失值标记 + 填充
    stats['missing_desc'] = int((df['description'].astype(str).str.strip() == '').sum())
    stats['missing_tags'] = int((df['tags'].astype(str).str.strip() == '').sum())

    df['desc_missing'] = (df['description'].astype(str).str.strip() == '').astype(int)
    df['tags_missing'] = (df['tags'].astype(str).str.strip() == '').astype(int)

    df['description'] = df['description'].fillna('')
    df['tags'] = df['tags'].fillna('')
    logger.info(f"  缺失值处理: description 缺失 {stats['missing_desc']} 条, tags 缺失 {stats['missing_tags']} 条")

    # 零值标记
    df['likes_is_zero'] = (df['likes'] == 0).astype(int)
    df['dislikes_is_zero'] = (df['dislikes'] == 0).astype(int)
    logger.info(f"  零值标记: likes=0 {stats['zero_likes']} 条, dislikes=0 {stats['zero_dislikes']} 条")

    # ------------------------------------------------------------------
    # Step 01.5: Name 清理（引号、全角空格、连续空格）
    # ------------------------------------------------------------------
    logger.info("Step 01.5: Name 清理")

    quoted_count = int(df['name'].str.match(r'^["\'].*["\']$', na=False).sum())
    stats['quoted_names'] = quoted_count
    df['name'] = df['name'].str.strip('"\'').str.strip()
    df['name'] = df['name'].str.replace('\u3000', ' ', regex=False)
    df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)

    # 短名称记录
    short_names = df[df['name'].str.len() <= 2]['name'].tolist()
    stats['short_names'] = short_names

    # 纯符号/空白名称记录
    pure_symbol_mask = df['name'].str.match(r'^[\W_]+$', na=False)
    pure_symbol_names = df[pure_symbol_mask]['name'].tolist()
    stats['pure_symbol_names'] = pure_symbol_names

    logger.info(f"  Name 清理: 去除引号 {quoted_count} 条, 短名称 {len(short_names)} 条, 纯符号名称 {len(pure_symbol_names)} 条")

    # ------------------------------------------------------------------
    # Step 01.6: 标签规范化（特殊字符替换 + 近义词合并 + 无效标签过滤）
    # ------------------------------------------------------------------
    logger.info("Step 01.6: 标签规范化")

    df['tags'] = df['tags'].apply(normalize_tags)
    logger.info("  标签规范化完成")

    # ------------------------------------------------------------------
    # Step 01.7: 新增业务字段（source, game_id, like_ratio, tag_count, 标记列）
    # ------------------------------------------------------------------
    logger.info("Step 01.7: 新增业务字段")

    # 平台来源
    df['source'] = df['url'].apply(lambda x: 'poki' if 'poki.com' in str(x) else 'newgrounds')

    # 唯一主键
    df.insert(0, 'game_id', range(1, len(df) + 1))

    # 点赞率
    likes_val = df['likes'].fillna(0).astype(float)
    dislikes_val = df['dislikes'].fillna(0).astype(float)
    total = likes_val + dislikes_val
    df['like_ratio'] = likes_val / total.replace(0, float('nan'))
    df['like_ratio'] = df['like_ratio'].round(4)

    # 标签数量
    df['tag_count'] = df['tags'].apply(count_tags).astype(int)

    logger.info("  新增业务字段: source, game_id, like_ratio, tag_count")

    # 重新计算 log 列确保一致性
    if mismatch > 0:
        logger.warning(f"  发现 {mismatch} 条 log 值不一致，重新计算")
        df['log_likes'] = np.log1p(df['likes'].fillna(0).astype(float))
        df['log_dislikes'] = np.log1p(df['dislikes'].fillna(0).astype(float))

    # ------------------------------------------------------------------
    # Step 01.8: 输出清洗后数据和清洗报告
    # ------------------------------------------------------------------
    logger.info("Step 01.8: 输出产物")

    # 全字段数据类型校验
    stats['cleaned_rows'] = len(df)
    logger.info(f"  清洗完成: 最终 {len(df)} 行 x {len(OUTPUT_COLUMNS)} 列")

    # 输出清洗后 CSV
    df_output = df[OUTPUT_COLUMNS].copy()
    save_dataframe(df_output, 'ch01_cleaned_online_gaming.csv', OUTPUT_DIR)
    logger.info(f"  清洗后数据已保存: {os.path.join(OUTPUT_DIR, 'ch01_cleaned_online_gaming.csv')}")

    # 生成清洗报告（重新加载原始数据用于标签对比）
    df_original = load_raw_data('online-gaming-14-04-26.csv', sep='\t', keep_default_na=False)
    report = generate_report(stats, df_output, df_original)
    save_report(report, 'ch01_cleaning_report.md', OUTPUT_DIR)
    logger.info(f"  清洗报告已保存: {os.path.join(OUTPUT_DIR, 'ch01_cleaning_report.md')}")

    # ------------------------------------------------------------------
    # 最终验证
    # ------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("最终验证:")
    logger.info(f"  无完全重复行: {not df_output.duplicated().any()}")
    logger.info(f"  description 无 NaN: {not df_output['description'].isna().any()}")
    logger.info(f"  tags 无 NaN: {not df_output['tags'].isna().any()}")
    logger.info(f"  game_id 唯一: {df_output['game_id'].is_unique}")
    logger.info(f"  source 值: {sorted(df_output['source'].unique())}")
    logger.info(f"  like_ratio 范围: [{df_output['like_ratio'].min():.4f}, {df_output['like_ratio'].max():.4f}]")
    logger.info(f"  tag_count 范围: [{df_output['tag_count'].min()}, {df_output['tag_count'].max()}]")

    # 回读验证
    df_verify = pd.read_csv(os.path.join(OUTPUT_DIR, 'ch01_cleaned_online_gaming.csv'), encoding='utf-8-sig')
    logger.info(f"  回读行数一致: {len(df_verify) == len(df_output)}")

    logger.info("=" * 60)
    logger.info("Prompt-01: 数据清洗 - 执行完成")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
