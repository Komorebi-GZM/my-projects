# online_gaming_analysis — 执行Prompt文档

## 文档说明

本文档为**全流程标准化数据分析执行指南**，覆盖从原始数据清洗预处理到在线小游戏数据分析总结报告的完整分析链条。每个章节的Prompt均设计为**自包含、可独立执行**的单元，可直接复制到AI助手（如ChatGPT、Claude、Cursor等）中执行，也可由数据分析师参照手动操作。

### 适用环境
- **Python 版本**: 3.10（本地 conda 环境 `py310`）
- **执行方式**: 每个章节均提供 **Jupyter Notebook (.ipynb)** 脚本，按章节编号命名（如 `ch01_data_cleaning/clean.ipynb`），支持交互式运行、逐步调试、可视化即时预览，便于学习和复现
- **环境管理**: 使用本地 conda 环境 `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **依赖库清单**: 见 `requirements.txt`
- **推荐 IDE**: Jupyter Notebook / VS Code（含 Jupyter 插件）

### 全局路径配置

```python
import os

# === 路径配置 ===
DATA_DIR = "data/"
RAW_DATA_FILE = os.path.join(DATA_DIR, "online-gaming-14-04-26.csv")
OUTPUT_BASE = "outputs/"
```

---

## 全局Skill库（可复用模块）

> 以下 4 个 Skill 贯穿全流程，每个章节均可调用。请在执行任何章节前，先将这些 Skill 代码保存为独立文件或直接嵌入 Notebook 的首个 Cell。

---

### Skill-01: 项目配置管理器 (`src/utils/config.py`)

核心常量：
| 常量 | 说明 |
|------|------|
| `PROJECT_ROOT` | 项目根目录 |
| `DATA_DIR` | 原始数据目录（`data/`） |
| `OUTPUT_BASE` | 输出根目录（`outputs/`） |
| `DOMAIN_PARAMS` | 业务领域参数字典，包含 `expected_rows`、`tag_special_char_map`、`tag_synonym_map`、`output_columns` 等 |

使用示例：
```python
from utils.config import PROJECT_ROOT, DATA_DIR, OUTPUT_BASE, DOMAIN_PARAMS
```

---

### Skill-02: 标准数据加载器 (`src/utils/data_loader.py`)

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `load_raw_data` | `load_raw_data(filename, sep='\t', keep_default_na=False, **kwargs) -> pd.DataFrame` | 从 `data/` 目录加载原始数据文件，支持 CSV/TSV |

使用示例：
```python
from utils.data_loader import load_raw_data
df = load_raw_data('online-gaming-14-04-26.csv', sep='\t', keep_default_na=False)
```

---

### Skill-03: 标准输出产物管理器 (`src/utils/output_manager.py`)

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `get_chapter_dir` | `get_chapter_dir(chapter_key) -> str` | 获取章节输出目录的完整路径（基于 CHAPTER_DIR_MAP） |
| `save_dataframe` | `save_dataframe(df, filename, output_dir, index=False, encoding='utf-8-sig') -> str` | 保存 DataFrame 为 CSV |
| `save_report` | `save_report(content, filename, output_dir) -> str` | 保存 Markdown 文本 |

使用示例：
```python
from utils.output_manager import get_chapter_dir, save_dataframe, save_report
output_dir = get_chapter_dir('ch01')
save_dataframe(df, "ch01_cleaned_online_gaming.csv", output_dir)
save_report(report_text, "ch01_cleaning_report.md", output_dir)
```

---

### Skill-04: 任务依赖图管理器 (`src/utils/task_graph.py`)

核心功能：
| 功能 | 说明 |
|------|------|
| 任务依赖关系定义 | 定义各章节之间的数据依赖关系 |
| 执行顺序验证 | 校验章节执行顺序是否满足依赖约束 |

---

## 数据集概况

| 项目 | 说明 |
|------|------|
| 数据文件 | `data/online-gaming-14-04-26.csv` |
| 文件格式 | TSV（制表符分隔） |
| 总行数 | 11,406 行 |
| 总列数 | 8 列 |
| 数据来源 | Poki + Newgrounds 双平台 |
| 编码 | UTF-8 |

### 原始数据列说明

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| `name` | str | 游戏名称 |
| `url` | str | 游戏链接（含 poki.com 或 newgrounds.com） |
| `likes` | int | 点赞数 |
| `dislikes` | int | 踩数 |
| `log_likes` | float | 点赞数的 log1p 变换值 |
| `log_dislikes` | float | 踩数的 log1p 变换值 |
| `description` | str | 游戏描述文本 |
| `tags` | str | 游戏标签（逗号分隔） |

---

# Prompt-01: 数据清洗预处理

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**基础起点**，目标是读取 Poki 和 Newgrounds 双平台的在线小游戏原始数据集（11,406 条记录），解决数据中存在的**完全重复行**、**无效行**（name/url 为空）、**URL 格式不规范**、**Description 含换行符**、**标签格式不统一**（特殊字符、近义词、无效标签）等问题，最终输出一份高质量、结构化的标准数据集，为后续所有分析章节提供可靠的数据基础。

原始数据为 TSV 格式，包含 8 列基础字段。清洗过程将新增 8 列业务字段（game_id、source、like_ratio、tag_count、desc_missing、tags_missing、likes_is_zero、dislikes_is_zero），最终输出 16 列的标准数据集。

本章在整体分析流程中处于**第一步**的位置，后续所有章节（EDA、标签分析、用户偏好建模等）均依赖本章的清洗产物。

### 1.2 从什么数据出发

数据文件为 `data/online-gaming-14-04-26.csv`，TSV 格式，共 11,406 行 x 8 列。

具体字段如下：
- **name**（str）：游戏名称，可能含引号、全角空格、连续空格等格式问题
- **url**（str）：游戏链接，以 `http://` 或 `https://` 开头，含 `poki.com` 或 `newgrounds.com`
- **likes**（int）：点赞数，可能存在 0 值
- **dislikes**（int）：踩数，可能存在 0 值
- **log_likes**（float）：likes 的 log1p 变换值，需验证与 likes 的一致性
- **log_dislikes**（float）：dislikes 的 log1p 变换值，需验证与 dislikes 的一致性
- **description**（str）：游戏描述文本，可能含换行符、缺失值
- **tags**（str）：游戏标签，逗号分隔，可能含特殊字符、近义词、无效标签

初步探查显示数据可能存在完全重复行、name/url 为空的无效行、description 缺失值、tags 格式不统一等问题。

### 1.3 可以采用什么方法

核心处理方法包括：
1. **完全重复行去重**：使用 `DataFrame.duplicated(keep='first')` 识别并删除完全重复的行，保留首次出现的记录。
2. **无效行清理**：删除 name 或 url 为空的行，这些行无法用于后续分析。
3. **URL 正则校验**：使用正则表达式 `^https?://\S+$` 校验 URL 格式有效性。
4. **log 一致性验证**：验证 `log_likes == log1p(likes)` 是否成立，不一致时重新计算。
5. **标签规范化**：通过预定义的映射表进行特殊字符替换（如 `point 'n click` -> `point and click`）和近义词合并（如 `puzzles` -> `puzzle`），同时过滤单字符和纯符号标签。
6. **缺失值标记策略**：不直接删除缺失行，而是填充空字符串并设置标记列（desc_missing、tags_missing），保留原始缺失信息供后续分析使用。

替代方法：删除缺失行（会丢失信息）、使用众数/中位数填充描述（不适用于文本字段）、使用 NLP 模型生成缺失描述（成本高且可能引入偏差）。

## 二、执行步骤

### Step 01.1: 加载数据并校验行数

**本步骤要做什么**
从 `data/` 目录加载原始 TSV 文件，校验行数是否为期望的 11,406 行，并对 likes/dislikes 列进行强制类型转换（Int64），对 log_likes/log_dislikes 列转为 float 类型。

**具体操作指引**
使用 `load_raw_data()` 加载数据，指定 `sep='\t'` 和 `keep_default_na=False`。加载后使用 `pd.to_numeric()` 进行类型转换，并通过 `assert` 校验行数。

**代码框架**:
```python
from utils.data_loader import load_raw_data
import pandas as pd

INPUT_PATH = os.path.join(DATA_DIR, 'online-gaming-14-04-26.csv')
EXPECTED_ROWS = 11406

df = load_raw_data('online-gaming-14-04-26.csv', sep='\t', keep_default_na=False)

# 强制类型转换
df['likes'] = pd.to_numeric(df['likes'], errors='coerce').astype('Int64')
df['dislikes'] = pd.to_numeric(df['dislikes'], errors='coerce').astype('Int64')
df['log_likes'] = pd.to_numeric(df['log_likes'], errors='coerce')
df['log_dislikes'] = pd.to_numeric(df['log_dislikes'], errors='coerce')

assert len(df) == EXPECTED_ROWS, f"行数不符: {len(df)} != {EXPECTED_ROWS}"
```

**本步骤完成后的检查标准**
- 数据成功加载，行数为 11,406
- likes/dislikes 列类型为 Int64
- log_likes/log_dislikes 列类型为 float64
- 无 assert 异常

**本步骤输出产物**
- 无独立文件（数据加载到内存，传递给后续步骤）

---

### Step 01.2: 完全重复行去重 + 无效行清理

**本步骤要做什么**
统计 Poki/Newgrounds 数据来源分布，删除完全重复行（保留首次出现），删除 name 或 url 为空的无效行。

**具体操作指引**
使用 `df.duplicated(keep='first')` 识别完全重复行，使用 `df.drop_duplicates()` 删除。无效行通过判断 name 或 url 去除空格后是否为空字符串来识别。

**代码框架**:
```python
# 来源统计
stats['poki_count'] = int(df['url'].str.contains('poki.com').sum())
stats['newgrounds_count'] = int(df['url'].str.contains('newgrounds.com').sum())

# 完全重复行去重
dup_count = int(df.duplicated(keep='first').sum())
df = df.drop_duplicates(keep='first').reset_index(drop=True)

# 无效行清理
invalid_mask = (df['name'].astype(str).str.strip() == '') | (df['url'].astype(str).str.strip() == '')
invalid_count = int(invalid_mask.sum())
df = df[~invalid_mask].reset_index(drop=True)
```

**本步骤完成后的检查标准**
- 统计了 Poki 和 Newgrounds 的数据量分布
- 完全重复行已全部删除
- name 或 url 为空的行已全部删除
- DataFrame 索引已重新编号

**本步骤输出产物**
- 无独立文件（中间处理结果在内存中传递）

---

### Step 01.3: URL/数值有效性校验

**本步骤要做什么**
对 URL 列进行格式校验（必须以 http:// 或 https:// 开头），检查 likes/dislikes 是否存在负数值，验证 log_likes 与 log1p(likes) 的一致性，统计 likes=0 和 dislikes=0 的记录数。

**具体操作指引**
URL 校验使用正则表达式 `^https?://\S+$`。log 一致性验证仅对 likes > 0 的记录进行，计算 `abs(log_likes - log1p(likes)) > 1e-6` 的不一致数量。

**代码框架**:
```python
import re
import numpy as np

# URL 有效性校验
url_pattern = re.compile(r'^https?://\S+$')
invalid_urls = int((~df['url'].astype(str).str.match(url_pattern)).sum())

# 数值列校验：负数值
negative_likes = int((df['likes'].fillna(0) < 0).sum())
negative_dislikes = int((df['dislikes'].fillna(0) < 0).sum())

# log 一致性验证
df_valid = df[(df['likes'].fillna(0) > 0)].copy()
if len(df_valid) > 0:
    computed_log = np.log1p(df_valid['likes'].fillna(0).astype(float))
    mismatch = int((abs(df_valid['log_likes'] - computed_log) > 1e-6).sum())
else:
    mismatch = 0

# 零值统计
stats['zero_likes'] = int((df['likes'] == 0).sum())
stats['zero_dislikes'] = int((df['dislikes'] == 0).sum())
```

**本步骤完成后的检查标准**
- 无效 URL 数量已记录
- 负数值数量已记录（期望为 0）
- log 不一致数量已记录（期望为 0）
- 零值统计已记录

**本步骤输出产物**
- 无独立文件（校验结果记录在 stats 字典中，最终写入清洗报告）

---

### Step 01.4: Description 换行符清理 + 缺失值填充

**本步骤要做什么**
将 description 中的 `\n` 和 `\r` 替换为空格，合并连续空格。统计 description 和 tags 的缺失情况，缺失值填充为空字符串，并设置标记列 desc_missing、tags_missing、likes_is_zero、dislikes_is_zero。

**具体操作指引**
换行符清理使用 `str.replace()` 逐个替换。缺失值标记必须在填充之前设置，否则会丢失缺失信息。零值标记列用于标识 likes 或 dislikes 原始值为 0 的记录。

**代码框架**:
```python
# 换行符清理
newline_count = int(df['description'].str.contains(r'[\n\r]', na=False).sum())
df['description'] = df['description'].str.replace('\n', ' ', regex=False)
df['description'] = df['description'].str.replace('\r', ' ', regex=False)
df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()

# 缺失值标记 + 填充（标记必须在填充之前设置）
stats['missing_desc'] = int((df['description'].astype(str).str.strip() == '').sum())
stats['missing_tags'] = int((df['tags'].astype(str).str.strip() == '').sum())

df['desc_missing'] = (df['description'].astype(str).str.strip() == '').astype(int)
df['tags_missing'] = (df['tags'].astype(str).str.strip() == '').astype(int)

df['description'] = df['description'].fillna('')
df['tags'] = df['tags'].fillna('')

# 零值标记
df['likes_is_zero'] = (df['likes'] == 0).astype(int)
df['dislikes_is_zero'] = (df['dislikes'] == 0).astype(int)
```

**本步骤完成后的检查标准**
- description 中无 `\n` 或 `\r` 字符
- description 和 tags 列无 NaN 值
- desc_missing 和 tags_missing 标记正确
- likes_is_zero 和 dislikes_is_zero 标记正确

**本步骤输出产物**
- 无独立文件（中间处理结果在内存中传递）

---

### Step 01.5: Name 清理（引号、全角空格、连续空格）

**本步骤要做什么**
去除游戏名称首尾的引号（单引号、双引号），将全角空格替换为半角空格，合并连续空格。同时记录短名称（长度 <= 2）和纯符号/空白名称，供后续审查。

**具体操作指引**
使用 `str.strip()` 去除首尾引号，`str.replace()` 替换全角空格（`\u3000`），正则表达式 `\s+` 合并连续空格。短名称和纯符号名称仅记录不删除，保留数据完整性。

**代码框架**:
```python
# 去除首尾引号
quoted_count = int(df['name'].str.match(r'^["\'].*["\']$', na=False).sum())
df['name'] = df['name'].str.strip('"\'').str.strip()

# 全角空格 -> 半角空格 + 合并连续空格
df['name'] = df['name'].str.replace('\u3000', ' ', regex=False)
df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)

# 短名称记录（长度 <= 2）
short_names = df[df['name'].str.len() <= 2]['name'].tolist()

# 纯符号/空白名称记录
pure_symbol_mask = df['name'].str.match(r'^[\W_]+$', na=False)
pure_symbol_names = df[pure_symbol_mask]['name'].tolist()
```

**本步骤完成后的检查标准**
- 无名称以引号开头或结尾
- 无全角空格
- 无连续空格
- 短名称和纯符号名称已记录

**本步骤输出产物**
- 无独立文件（异常名称记录在 stats 字典中，最终写入清洗报告）

---

### Step 01.6: 标签规范化（特殊字符替换 + 近义词合并 + 无效标签过滤）

**本步骤要做什么**
对 tags 列进行全面的规范化处理：去除首尾逗号和连续逗号，过滤无效标签（单字符、纯符号），通过预定义映射表进行特殊字符替换和近义词合并，最后去重并保持顺序。

**具体操作指引**
规范化流程为：预处理（去逗号） -> 转小写 -> 过滤无效标签 -> 特殊字符替换 -> 近义词合并 -> 去重。特殊字符替换映射表包含 9 条规则（如 `point 'n click` -> `point and click`），近义词合并映射表包含 1 条规则（`puzzles` -> `puzzle`）。

**代码框架**:
```python
TAG_SPECIAL_CHAR_MAP = {
    "point 'n click": "point and click",
    "run 'n gun": "run and gun",
    "idle / incremental": "idle incremental",
    "casino & gambling": "casino gambling",
    "pet / buddy": "pet buddy",
    "tube / rail": "tube rail",
    "time (rts)": "time rts",
    ".io": "io",
}

TAG_SYNONYM_MAP = {
    "puzzles": "puzzle",
}

def normalize_tags(tags_str):
    if not tags_str or tags_str.strip() == '':
        return ''
    tags_str = tags_str.strip().strip(',').replace(',,', ',')
    tag_list = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
    tag_list = [t for t in tag_list if len(t) > 1 and not re.match(r'^[^a-z0-9]+$', t)]
    tag_list = [TAG_SPECIAL_CHAR_MAP.get(t, t) for t in tag_list]
    tag_list = [TAG_SYNONYM_MAP.get(t, t) for t in tag_list]
    seen = set()
    unique_tags = []
    for t in tag_list:
        if t and t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return ','.join(unique_tags)

df['tags'] = df['tags'].apply(normalize_tags)
```

**本步骤完成后的检查标准**
- 标签中无特殊字符（`'`、`&`、`/`、`()`、`.` 等）
- 标签中无单字符标签
- 标签中无纯符号标签
- 近义词已合并（如 `puzzles` -> `puzzle`）
- 每条记录内标签无重复

**本步骤输出产物**
- 无独立文件（规范化结果在内存中传递）

---

### Step 01.7: 新增业务字段（source, game_id, like_ratio, tag_count, 标记列）

**本步骤要做什么**
新增 4 个核心业务字段：source（平台来源）、game_id（唯一主键）、like_ratio（点赞率）、tag_count（标签数量）。如 Step 01.3 中发现 log 值不一致，则重新计算 log 列。

**具体操作指引**
- source：通过 URL 中是否包含 `poki.com` 判断平台来源
- game_id：使用 `df.insert(0, ...)` 在第一列插入自增整数
- like_ratio：`likes / (likes + dislikes)`，两者均为 0 时为 NaN，保留 4 位小数
- tag_count：统计 tags 列中有效标签的个数

**代码框架**:
```python
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

# 如存在 log 值不一致，重新计算
if mismatch > 0:
    df['log_likes'] = np.log1p(df['likes'].fillna(0).astype(float))
    df['log_dislikes'] = np.log1p(df['dislikes'].fillna(0).astype(float))
```

**本步骤完成后的检查标准**
- game_id 为 1 到 N 的连续整数，无缺失
- source 仅包含 'poki' 和 'newgrounds' 两个值
- like_ratio 范围在 [0, 1] 之间
- tag_count >= 0

**本步骤输出产物**
- 无独立文件（业务字段在内存中传递给最终输出步骤）

---

### Step 01.8: 输出清洗后数据和清洗报告

**本步骤要做什么**
按指定列顺序输出清洗后的 CSV 文件，并生成包含数据质量评分、标签统计、异常日志的 Markdown 格式清洗报告。

**具体操作指引**
使用 `save_dataframe()` 输出 CSV（UTF-8-BOM 编码），使用 `save_report()` 输出 Markdown 报告。报告需重新加载原始数据用于标签清洗前后的对比统计。最终进行回读验证确保文件完整性。

**代码框架**:
```python
from utils.output_manager import get_chapter_dir, save_dataframe, save_report

OUTPUT_DIR = get_chapter_dir('ch01')

# 按指定列顺序输出
OUTPUT_COLUMNS = [
    'game_id', 'name', 'url', 'source', 'likes', 'dislikes',
    'log_likes', 'log_dislikes', 'description', 'tags',
    'like_ratio', 'tag_count',
    'desc_missing', 'tags_missing', 'likes_is_zero', 'dislikes_is_zero'
]

df_output = df[OUTPUT_COLUMNS].copy()
save_dataframe(df_output, 'ch01_cleaned_online_gaming.csv', OUTPUT_DIR)

# 生成清洗报告
df_original = load_raw_data('online-gaming-14-04-26.csv', sep='\t', keep_default_na=False)
report = generate_report(stats, df_output, df_original)
save_report(report, 'ch01_cleaning_report.md', OUTPUT_DIR)

# 回读验证
df_verify = pd.read_csv(os.path.join(OUTPUT_DIR, 'ch01_cleaned_online_gaming.csv'), encoding='utf-8-sig')
assert len(df_verify) == len(df_output), "回读行数不一致"
```

**本步骤完成后的检查标准**
- `ch01_cleaned_online_gaming.csv` 文件存在且行数与内存中一致
- `ch01_cleaning_report.md` 文件存在且包含完整的清洗统计信息
- `ch01_cleaning.log` 文件存在且包含完整的执行日志
- 清洗后数据无完全重复行
- game_id 唯一
- description 和 tags 列无 NaN

**本步骤输出产物**
- `ch01_cleaned_online_gaming.csv` — 清洗后的标准数据集，存放于 `outputs/ch01_data_cleaning/`
- `ch01_cleaning_report.md` — Markdown 格式清洗报告，存放于 `outputs/ch01_data_cleaning/`
- `ch01_cleaning.log` — 执行日志，存放于 `outputs/ch01_data_cleaning/`

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 清洗后数据集 | ch01_cleaned_online_gaming.csv | CSV | outputs/ch01_data_cleaning/ | Prompt-02 ~ Prompt-06 |
| 2 | 清洗报告 | ch01_cleaning_report.md | Markdown | outputs/ch01_data_cleaning/ | 参考 |
| 3 | 执行日志 | ch01_cleaning.log | LOG | outputs/ch01_data_cleaning/ | 调试参考 |

### 3.2 关键产物结构详解

**ch01_cleaned_online_gaming.csv**（最重要的产物）:

列结构（共 16 列）：

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| `game_id` | int | 唯一主键，自增整数 1~N |
| `name` | str | 游戏名称（已清理引号、全角空格、连续空格） |
| `url` | str | 游戏链接 |
| `source` | str | 平台来源（poki / newgrounds） |
| `likes` | Int64 | 点赞数 |
| `dislikes` | Int64 | 踩数 |
| `log_likes` | float | 点赞数的 log1p 变换值 |
| `log_dislikes` | float | 踩数的 log1p 变换值 |
| `description` | str | 游戏描述（已清理换行符，缺失填充空字符串） |
| `tags` | str | 游戏标签（已规范化，逗号分隔） |
| `like_ratio` | float | 点赞率 = likes / (likes + dislikes)，保留 4 位小数 |
| `tag_count` | int | 有效标签个数 |
| `desc_missing` | int | 描述缺失标记（1=原始缺失，0=有值） |
| `tags_missing` | int | 标签缺失标记（1=原始缺失，0=有值） |
| `likes_is_zero` | int | 点赞零值标记（1=likes=0，0=likes>0） |
| `dislikes_is_zero` | int | 踩零值标记（1=dislikes=0，0=dislikes>0） |

行数量级：约 11,400 行（去重和清理后）
用途说明：后续所有分析章节的主要输入数据

**ch01_cleaning_report.md**（清洗报告）:
- 包含 7 个章节：数据集基本信息、清洗操作汇总、标签统计、异常数据日志、数据质量评分、输出文件说明、数据样例
- 数据质量评分从完整性、唯一性、有效性、一致性四个维度评估
- 标签统计包含 Top 20 标签排名

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. 标签映射表为手动维护，新增特殊字符或近义词需要人工更新映射规则
2. 缺失值统一填充为空字符串，未利用上下文信息进行智能填充
3. 标签规范化仅处理了英文标签，未考虑多语言标签的统一

### 4.2 可进一步优化的方向
1. 引入 NLP 模型（如 TF-IDF + 余弦相似度）自动发现近义词，减少手动维护成本
2. 对 description 缺失的记录，利用 tags 和 name 信息生成简要描述
3. 增加标签层级分类（如将标签归类为"游戏类型"、"玩法特征"、"美术风格"等大类）

### 4.3 其他可选方法
1. 使用 spaCy 或 NLTK 进行更精细的文本清洗（去除 HTML 标签、特殊 Unicode 字符等）
2. 基于游戏 URL 的域名分析，扩展 source 字段为更细粒度的来源分类
3. 对 likes/dislikes 进行异常值检测（如使用 IQR 方法识别刷票行为）

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
1. 如果完全重复行数量异常多（> 总行数的 5%），需确认是否为数据采集问题
2. 如果 description 缺失率过高（> 30%），需确认是否需要补充数据
3. 如果标签规范化后唯一标签数大幅减少，需确认映射规则是否过于激进

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 行数校验失败 | `len(df) != 11406` | 检查文件是否被修改，确认文件路径 | 是 |
| URL 全部无效 | `invalid_urls == len(df)` | 检查分隔符参数是否正确（应为 `\t`） | 否 |
| log 值大量不一致 | `mismatch > 100` | 重新计算 log 列并记录警告 | 否 |
| 清洗后行数大幅减少 | 删除行数 > 总行数的 10% | 检查去重和清理逻辑，报告原因 | 是 |
| 标签映射后出现空标签 | 某条记录所有标签被过滤 | 保留空标签，通过 tags_missing 标记 | 否 |
| like_ratio 出现 NaN | likes 和 dislikes 均为 0 | 保留 NaN，后续分析时需处理 | 否 |

---

# Prompt-02: 热度分析

## 一、任务概述

本章对清洗后的游戏数据集进行热度分析，包括热度指标统计、分布特征分析、头部效应识别、Top N 排名和相关分析。输出热度统计表、Top 20 排名表、分平台统计表和多个可视化图表。

## 二、执行步骤

### Step 02.1: 加载清洗后数据
使用 `load_cleaned_data()` 加载 `ch01_cleaned_online_gaming.csv`。

### Step 02.2: 热度指标基本统计
计算 likes, dislikes, like_ratio, tag_count 的描述性统计（均值、中位数、标准差、分位数）。

### Step 02.3: 热度分布分析
生成点赞数对数直方图、分平台箱线图、点赞率分布图。

### Step 02.4: 头部效应分析
计算累计点赞占比曲线、Top 1%/5%/10%/20% 占比、80% 点赞所需游戏占比、近似 Gini 系数。

### Step 02.5: Top N 游戏排名
按点赞数排序，展示 Top 20 游戏，生成横向柱状图（分平台着色）。

### Step 02.6: 指标相关性分析
计算 Pearson 相关系数矩阵，分析 likes, dislikes, log_likes, like_ratio, tag_count 之间的相关性。

### Step 02.7: 保存统计表 + 生成报告
输出统计表、排名表、平台统计表、所有图表和 Markdown 报告。

## 三、产物

| 产物 | 文件 |
|------|------|
| 热度统计表 | `ch02_popularity_stats.csv` |
| Top 20 排名表 | `ch02_top20_games.csv` |
| 分平台统计表 | `ch02_platform_stats.csv` |
| 点赞分布图 | `ch02_likes_distribution.png` |
| 点赞率分布图 | `ch02_like_ratio_distribution.png` |
| 散点图 | `ch02_likes_vs_dislikes.png` |
| 头部效应图 | `ch02_head_effect.png` |
| Top 20 柱状图 | `ch02_top20_games.png` |
| 分析报告 | `ch02_popularity_analysis_report.md` |

---

# Prompt-03: 标签分析

## 一、任务概述

对游戏的标签数据进行全面的频率统计、共现分析和平台偏好对比，揭示标签体系的结构特征和平台差异。

## 二、执行步骤

### Step 03.1: 加载清洗后数据
使用 `load_cleaned_data()`。

### Step 03.2: 标签频率统计
提取所有标签，使用 Counter 统计频率，保存全量频率表。

### Step 03.3: 标签长尾分布
绘制标签频率柱状图 + 累计占比曲线，展示长尾特性。

### Step 03.4: 标签共现分析
计算 Top 30 标签的共现矩阵，提取 Top 20 共现对。

### Step 03.5: 共现热力图
可视化 Top 20 共现矩阵，生成共现对柱状图。

### Step 03.6: 标签数量分布
每游戏标签数的直方图和分平台箱线图。

### Step 03.7: 平台标签偏好对比
分别统计 Poki 和 Newgrounds 的 Top 标签，生成对比图。

### Step 03.8: 保存结果并生成报告
输出所有 CSV、PNG 和 Markdown 报告。

## 三、产物

| 产物 | 文件 |
|------|------|
| 标签频率表 | `ch03_tag_frequency.csv` |
| Poki 标签表 | `ch03_tags_poki.csv` |
| Newgrounds 标签表 | `ch03_tags_newgrounds.csv` |
| Top 20 标签图 | `ch03_top20_tags.png` |
| 长尾分布图 | `ch03_tag_long_tail.png` |
| 共现热力图 | `ch03_cooccurrence_top20.png` |
| 共现对图 | `ch03_top20_cooccurrence_pairs.png` |
| 标签数量分布 | `ch03_tag_count_distribution.png` |
| 平台对比图 | `ch03_platform_tag_comparison.png` |
| 分析报告 | `ch03_tag_analysis_report.md` |

---

# Prompt-04: 跨平台对比

## 一、任务概述

系统对比 Poki 和 Newgrounds 两个平台的所有可量化指标，使用统计检验验证差异显著性。

## 二、执行步骤

### Step 04.1: 加载数据
使用 `load_cleaned_data()`。

### Step 04.2: 平台基本特征对比
计算各平台的游戏数量、likes/dislikes/like_ratio/tag_count 的均值、中位数、标准差。

### Step 04.3: 统计检验
对每个指标执行 Mann-Whitney U 检验（非参数），判定差异是否显著（p < 0.05）。

### Step 04.4: 平台标签偏好对比
分别统计两平台的 Top 标签。

### Step 04.5: 生成对比图表
4 格箱线图（likes/dislikes/like_ratio/tag_count）、点赞率重叠直方图、点赞数分布对比、标签数量分布对比。

### Step 04.6: 平台相关性对比
分平台的 likes vs dislikes 散点图。

### Step 04.7: 报告生成
输出统计表、检验结果表和综合分析报告。

## 三、产物

| 产物 | 文件 |
|------|------|
| 平台对比表 | `ch04_platform_comparison.csv` |
| 检验结果表 | `ch04_statistical_tests.csv` |
| 指标对比箱线图 | `ch04_metric_comparison.png` |
| 点赞率对比 | `ch04_like_ratio_comparison.png` |
| 点赞分布对比 | `ch04_likes_dist_comparison.png` |
| 标签数量对比 | `ch04_tag_count_comparison.png` |
| 相关性散点图 | `ch04_platform_correlation.png` |
| 分析报告 | `ch04_platform_analysis_report.md` |

---

# Prompt-05: 可视化报告

## 一、任务概述

综合全部前序章节的分析结果，生成 9 宫格综合仪表板、关键指标汇总图和完整的最终分析报告。

## 二、执行步骤

### Step 05.1: 加载数据
使用 `load_cleaned_data()`。

### Step 05.2: 生成综合仪表板
9 宫格布局：平台分布饼图、Top 10 标签、点赞数分布、平台箱线图、头部效应、点赞率对比、标签数量对比、散点图、标签长尾。

### Step 05.3: 生成汇总图表
4 格汇总：平台数量对比、平均点赞数、平均点赞率、平均标签数量。

### Step 05.4: 生成综合报告
含项目概述、各章节要点、关键发现、综合分析结论。

## 三、产物

| 产物 | 文件 |
|------|------|
| 综合仪表板 | `ch05_dashboard.png` |
| 汇总图表 | `ch05_summary_chart.png` |
| 综合报告 | `ch05_summary_report.md` |
