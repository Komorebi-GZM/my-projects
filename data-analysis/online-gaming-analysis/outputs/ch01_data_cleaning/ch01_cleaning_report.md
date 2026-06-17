# 在线小游戏数据集清洗报告

> 生成时间：2026-04-25 22:59:51

## 1. 数据集基本信息

| 指标 | 值 |
|------|------|
| 原始文件 | `data/online-gaming-14-04-26.csv` |
| 原始行数 | 11406 |
| 原始列数 | 8 |
| 清洗后行数 | 11406 |
| 清洗后列数 | 16 |
| 删除行数 | 0 |
| 数据来源 - Poki | 1664 条 |
| 数据来源 - Newgrounds | 9742 条 |

## 2. 清洗操作汇总

### 2.1 完全重复行去重
- 删除完全重复行：**0 条**

### 2.2 无效行清理
- 删除 name/url 为空的行：**0 条**

### 2.3 URL 有效性校验
- 无效 URL 数量：**0 条**
- 校验规则：以 `http://` 或 `https://` 开头

### 2.4 数值列校验
- 负数值数量：**0 条**
- log 值不一致数量：**0 条**
- likes=0 的记录数：**19 条**
- dislikes=0 的记录数：**69 条**

### 2.5 Description 换行符清理
- 含换行符的记录数：**1038 条**
- 处理方式：将 `\n`/`\r` 替换为空格，合并连续空格

### 2.6 缺失值处理
- description 缺失：**1260 条** -> 填充空字符串，`desc_missing` 标记为 1
- tags 缺失：**34 条** -> 填充空字符串，`tags_missing` 标记为 1

### 2.7 零值标记
- `likes_is_zero` 标记：19 条为 1
- `dislikes_is_zero` 标记：69 条为 1

### 2.8 Name 清理
- 去除首尾引号的记录数：**1 条**
- 全角空格->半角空格、合并连续空格：全部行

### 2.9 标签规范化
- 清洗前唯一标签数：**216**
- 清洗后唯一标签数：**214**
- 特殊字符替换规则：**8 条**
- 近义词合并规则：**1 条**

**标签替换明细：**
    - `point 'n click` -> `point and click`（影响 489 行）
    - `run 'n gun` -> `run and gun`（影响 252 行）
    - `idle / incremental` -> `idle incremental`（影响 238 行）
    - `casino & gambling` -> `casino gambling`（影响 18 行）
    - `pet / buddy` -> `pet buddy`（影响 71 行）
    - `tube / rail` -> `tube rail`（影响 18 行）
    - `time (rts)` -> `time rts`（影响 37 行）
    - `.io` -> `io`（影响 36 行）
    - `puzzles` -> `puzzle`（影响 783 行）

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
| 1 | action | 4278 |
| 2 | other | 4108 |
| 3 | platformer | 1635 |
| 4 | adventure | 1621 |
| 5 | puzzle | 1459 |
| 6 | skill | 1226 |
| 7 | shooter | 1101 |
| 8 | simulation | 814 |
| 9 | point and click | 547 |
| 10 | strategy | 527 |
| 11 | mobile | 445 |
| 12 | gadgets | 430 |
| 13 | rpg | 402 |
| 14 | hop and bop | 391 |
| 15 | visual novel | 370 |
| 16 | fighting | 366 |
| 17 | spam | 364 |
| 18 | brain | 363 |
| 19 | mouse | 340 |
| 20 | sports | 335 |

## 4. 异常数据日志

### 无效 URL
无（全部通过校验）

### log 值不一致记录
无（全部一致）

### 短名称记录（长度 <= 2）
- `ЗВ`
- `互動`
- `J`
- `ÛA`

### 纯符号/空白名称
无


## 5. 数据质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 完整性 | 98.6% | 非缺失字段占比 |
| 唯一性 | 100.0% | game_id 唯一性 |
| 有效性 | 100.0% | URL/数值校验通过率 |
| 一致性 | 100.0% | log 值一致性 |
| **综合评分** | **99.6%** | 四维度均值 |

## 6. 输出文件说明

### 清洗后 CSV 列说明

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| game_id | int64 |
| name | object |
| url | object |
| source | object |
| likes | Int64 |
| dislikes | Int64 |
| log_likes | float64 |
| log_dislikes | float64 |
| description | object |
| tags | object |
| like_ratio | float64 |
| tag_count | int64 |
| desc_missing | int64 |
| tags_missing | int64 |
| likes_is_zero | int64 |
| dislikes_is_zero | int64 |

### 新增标记列使用说明
- `desc_missing=1`：该行的 description 为清洗后填充的空字符串，原始数据中无描述
- `tags_missing=1`：该行的 tags 为清洗后填充的空字符串，原始数据中无标签
- `likes_is_zero=1`：该行的 likes 原始值为 0
- `dislikes_is_zero=1`：该行的 dislikes 原始值为 0

## 7. 清洗后数据样例

| game_id | name | source | likes | dislikes | like_ratio | tag_count |
|---------|------|--------|-------|----------|------------|-----------|
| 1 | 100 Metres Race | poki | 59500 | 14800 | 0.8008 | 3 |
| 2 | 100% Golf | poki | 21400 | 5100 | 0.8075 | 4 |
| 3 | 1010 Color Match | poki | 46200 | 21000 | 0.6875 | 10 |
| 4 | 1010! Deluxe | poki | 41000 | 18100 | 0.6937 | 8 |
| 5 | 11-11 | poki | 148600 | 48200 | 0.7551 | 9 |

