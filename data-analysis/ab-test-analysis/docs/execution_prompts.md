# AB_Test_Analysis 执行指令文档

> 项目：A/B测试点击率数据分析
> 生成时间：2026-05-07
> 适用对象：AI Agent / 数据分析师

---

## 文档说明

本文档包含5个章节的执行Prompt，按照依赖关系分为3个批次执行：
- **第1批**：ch01（已完成）
- **第2批**：ch02, ch03, ch04（可并行）
- **第3批**：ch05（依赖ch02-ch04）

每个Prompt采用五段式结构：任务概述 → 执行步骤 → 产物总览 → 优化方向 → 异常处理。

---

# Prompt-01: ch01 数据清洗（已完成）

## 一、任务概述

### 1.1 本次任务是什么

对A/B测试原始数据进行质量检查与清洗，确保数据符合后续分析要求。包括缺失值检查、重复值检查、数据类型验证、异常值检测等。

### 1.2 从什么数据出发

- **输入数据**：`data/raw/ab_test_click_data.csv`
- **数据规模**：20,000行 × 4列
- **字段说明**：
  - `user_id`：用户唯一标识（int）
  - `click`：点击标识，0/1二值（int）
  - `group`：分组标识，con/exp（str）
  - `timestamp`：时间戳（str，需转换为datetime）

### 1.3 可以采用什么方法

- 使用 `pandas.isnull()` 检查缺失值
- 使用 `pandas.duplicated()` 检查重复值
- 使用 `pandas.to_datetime()` 转换时间格式
- 使用描述性统计验证数据分布合理性

---

## 二、执行步骤

### Step 1: 加载原始数据

**本步骤要做什么**：读取原始CSV文件，检查数据基本结构是否正确。

**本步骤输出产物**：
- 控制台输出：数据形状、列名、数据类型、前5行预览

**具体操作指引**：
1. 使用 `DataLoader.load_raw()` 加载数据
2. 调用 `get_data_info()` 获取数据基本信息
3. 打印数据预览

**代码框架**：
```python
from src.utils.config import Config
from src.utils.data_loader import DataLoader

config = Config()
loader = DataLoader(config)
df = loader.load_raw()
info = loader.get_data_info(df)
print(f"数据形状: {info['shape']}")
```

**本步骤完成后的检查标准**：
- [ ] 数据成功加载，无报错
- [ ] 数据形状为 (20000, 4)
- [ ] 列名与预期一致

---

### Step 2: 缺失值检查

**本步骤要做什么**：检查各字段是否存在缺失值，生成缺失值统计报告。

**本步骤输出产物**：
- 文件：`outputs/tables/ch01_missing_values_summary.csv`
- 内容：各列非空数量、缺失数量、缺失比例、数据类型

**具体操作指引**：
1. 使用 `Metrics.null_summary()` 生成缺失值汇总
2. 保存结果到表格目录
3. 打印总缺失值数量

**本步骤完成后的检查标准**：
- [ ] 缺失值汇总表已保存
- [ ] 总缺失值为0（或记录缺失情况）

---

### Step 3: 重复值检查

**本步骤要做什么**：检查是否存在完全重复的记录，如有则删除。

**本步骤输出产物**：
- 文件：`outputs/tables/ch01_duplicate_summary.json`
- 内容：总行数、重复行数、重复比例

**具体操作指引**：
1. 使用 `Metrics.duplicate_summary()` 统计重复值
2. 如有重复，使用 `df.drop_duplicates()` 删除
3. 保存统计结果

**本步骤完成后的检查标准**：
- [ ] 重复值统计已保存
- [ ] 数据已去重（如有重复）

---

### Step 4: 数据类型验证与转换

**本步骤要做什么**：验证关键字段的取值范围，转换timestamp为datetime类型。

**本步骤输出产物**：
- 控制台输出：各字段验证结果

**具体操作指引**：
1. 转换 `timestamp` 为 datetime 类型
2. 验证 `click` 取值仅为 0/1
3. 验证 `group` 取值仅为 con/exp
4. 验证 `user_id` 唯一性

**本步骤完成后的检查标准**：
- [ ] timestamp 已成功转换
- [ ] click 取值合法
- [ ] group 取值合法
- [ ] user_id 无重复

---

### Step 5: 保存清洗后数据

**本步骤要做什么**：将清洗后的数据保存到 processed 目录。

**本步骤输出产物**：
- 文件：`data/processed/cleaned_data.csv`

**具体操作指引**：
1. 使用 `OutputManager.save_data()` 保存数据
2. 确认文件已生成

**本步骤完成后的检查标准**：
- [ ] 清洗后数据已保存
- [ ] 文件可正常读取

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物类型 | 文件名 | 存放路径 |
|---------|--------|----------|
| 数据文件 | cleaned_data.csv | data/processed/ |
| 表格 | ch01_missing_values_summary.csv | outputs/tables/ |
| 表格 | ch01_duplicate_summary.json | outputs/tables/ |

### 3.2 关键产物结构详解

**cleaned_data.csv**：
- 行数：20,000（或去重后数量）
- 列：user_id, click, group, timestamp
- timestamp 为 datetime 类型

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅进行基础质量检查，未深入分析异常值分布

### 4.2 可进一步优化的方向
- 可增加箱线图检测异常值
- 可增加时间序列完整性检查

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 发现大量缺失值时的处理策略
- 发现重复值时的处理策略

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|----------|
| 数据文件不存在 | 检查路径配置 |
| 列名与预期不符 | 暂停执行，向用户确认 |
| 缺失值比例>5% | 记录并报告用户 |

---

---

# Prompt-02: ch02 核心指标计算与可视化

## 一、任务概述

### 1.1 本次任务是什么

计算对照组和实验组的核心业务指标（点击率CTR、绝对提升、相对提升），并绘制带95%置信区间的可视化图表，直观展示两组差异。

### 1.2 从什么数据出发

- **输入数据**：`data/processed/cleaned_data.csv`
- **数据说明**：已完成清洗的A/B测试数据
- **依赖章节**：ch01（数据清洗）

### 1.3 可以采用什么方法

- 分组聚合计算点击率：`df.groupby('group')['click'].mean()`
- 比例的标准误计算：`sqrt(p*(1-p)/n)`
- 95%置信区间：`p ± 1.96 * SE`
- 可视化：matplotlib 柱状图 + 误差线

---

## 二、执行步骤

### Step 1: 加载清洗后数据

**本步骤要做什么**：读取ch01生成的清洗后数据。

**本步骤输出产物**：
- DataFrame对象：清洗后的数据

**具体操作指引**：
1. 使用 `DataLoader.load_processed("cleaned_data.csv")` 加载
2. 确认数据加载成功

**代码框架**：
```python
from src.utils.config import Config
from src.utils.data_loader import DataLoader

config = Config()
loader = DataLoader(config)
df = loader.load_processed("cleaned_data.csv")
```

**本步骤完成后的检查标准**：
- [ ] 数据成功加载
- [ ] 数据形状符合预期

---

### Step 2: 计算分组核心指标

**本步骤要做什么**：计算对照组和实验组的点击率、绝对提升、相对提升。

**本步骤输出产物**：
- 控制台输出：分组点击率、绝对提升、相对提升
- 文件：`outputs/tables/ch02_group_metrics.csv`

**具体操作指引**：
1. 按 `group` 分组，计算 `click` 的 count/sum/mean
2. 计算绝对提升：`CTR_exp - CTR_con`
3. 计算相对提升：`(CTR_exp - CTR_con) / CTR_con * 100%`
4. 保存结果

**代码框架**：
```python
group_stats = df.groupby("group")["click"].agg(["count", "sum", "mean"])
group_stats.columns = ["总用户数", "点击数", "点击率"]

ctr_con = group_stats.loc["con", "点击率"]
ctr_exp = group_stats.loc["exp", "点击率"]
absolute_lift = ctr_exp - ctr_con
relative_lift = (ctr_exp - ctr_con) / ctr_con * 100
```

**本步骤完成后的检查标准**：
- [ ] 分组统计表已保存
- [ ] 绝对提升和相对提升已计算

---

### Step 3: 计算95%置信区间

**本步骤要做什么**：为两组点击率计算95%置信区间。

**本步骤输出产物**：
- 控制台输出：带CI的分组统计
- 文件：`outputs/tables/ch02_group_metrics_with_ci.csv`

**具体操作指引**：
1. 对每组计算比例的标准误：`SE = sqrt(p*(1-p)/n)`
2. 计算95% CI：`p ± 1.96 * SE`
3. 保存完整统计表

**代码框架**：
```python
import numpy as np

n = len(group_data)
p = group_data.mean()
se = np.sqrt(p * (1 - p) / n)
ci_lower = p - 1.96 * se
ci_upper = p + 1.96 * se
```

**本步骤完成后的检查标准**：
- [ ] CI计算正确
- [ ] 结果表已保存

---

### Step 4: 绘制可视化图表

**本步骤要做什么**：绘制带95%置信区间的柱状图。

**本步骤输出产物**：
- 文件：`outputs/figures/ch02_ctr_comparison_with_ci.png`

**具体操作指引**：
1. 使用 matplotlib 创建柱状图
2. 添加误差线（capsize=10）
3. 添加数值标签
4. 设置标题、轴标签、图例
5. 保存图表

**代码框架**：
```python
import matplotlib.pyplot as plt
from src.utils.visualizer import Visualizer

visualizer = Visualizer(config)

fig, ax = plt.subplots(figsize=(10, 6))
errors = [ctrs - ci_lower, ci_upper - ctrs]
bars = ax.bar(groups, ctrs, yerr=errors, capsize=10, color=["#DD8452", "#4C72B0"])
ax.set_title("A/B测试点击率对比（含95%置信区间）")

save_path = visualizer.save_figure(fig, "ctr_comparison_with_ci", chapter_prefix="ch02")
```

**本步骤完成后的检查标准**：
- [ ] 图表已保存
- [ ] 图表包含误差线、数值标签、图例

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物类型 | 文件名 | 存放路径 |
|---------|--------|----------|
| 表格 | ch02_group_metrics.csv | outputs/tables/ |
| 表格 | ch02_group_metrics_with_ci.csv | outputs/tables/ |
| 图表 | ch02_ctr_comparison_with_ci.png | outputs/figures/ |

### 3.2 关键产物结构详解

**ch02_group_metrics_with_ci.csv**：
| 字段 | 说明 |
|------|------|
| group | 分组标识 |
| n | 样本量 |
| clicks | 点击数 |
| ctr | 点击率 |
| se | 标准误 |
| ci_lower | 置信区间下限 |
| ci_upper | 置信区间上限 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅展示两组对比，未展示时间维度变化

### 4.2 可进一步优化的方向
- 可增加分组分布直方图
- 可增加效应量可视化

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 置信水平是否保持95%（或需要99%）

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|----------|
| 清洗后数据不存在 | 提示先执行ch01 |
| CI计算出现负值 | 检查边界处理（clip到0） |

---

---

# Prompt-03: ch03 假设检验与效应量

## 一、任务概述

### 1.1 本次任务是什么

执行比例Z检验（单尾），计算p值、Z统计量、95%置信区间、Cohen's h效应量、统计功效和MDE（最小可检测效应），全面评估实验效果的统计显著性和实际业务意义。

### 1.2 从什么数据出发

- **输入数据**：`data/processed/cleaned_data.csv`
- **依赖章节**：ch01（数据清洗）

### 1.3 可以采用什么方法

- **比例Z检验**：检验两组点击率差异是否显著
- **Cohen's h**：两比例效应量，评估实际业务意义
- **统计功效分析**：使用 `statsmodels` 验证实验灵敏度
- **MDE计算**：最小可检测效应，评估实验设计合理性

---

## 二、执行步骤

### Step 1: 比例Z检验（单尾）

**本步骤要做什么**：建立假设，执行Z检验，判断实验组点击率是否显著高于对照组。

**假设设定**：
- H₀: p_exp ≤ p_con（实验组点击率不高于对照组）
- H₁: p_exp > p_con（实验组点击率高于对照组）
- 显著性水平：α = 0.05

**本步骤输出产物**：
- 控制台输出：假设、样本统计、检验结果、结论
- 数据：Z统计量、p值、是否显著

**具体操作指引**：
1. 提取两组数据
2. 计算合并比例（pooled proportion）
3. 计算Z统计量：`Z = (p_exp - p_con) / SE`
4. 计算单尾p值
5. 与α比较得出结论

**代码框架**：
```python
from scipy import stats

# 提取数据
con_data = df[df["group"] == "con"]["click"]
exp_data = df[df["group"] == "exp"]["click"]

n_con, n_exp = len(con_data), len(exp_data)
x_con, x_exp = con_data.sum(), exp_data.sum()
p_con, p_exp = x_con / n_con, x_exp / n_exp

# 合并比例
p_pooled = (x_con + x_exp) / (n_con + n_exp)
se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_con + 1/n_exp))

# Z检验
z_stat = (p_exp - p_con) / se
p_value = 1 - stats.norm.cdf(z_stat)  # 单尾
```

**本步骤完成后的检查标准**：
- [ ] Z统计量已计算
- [ ] p值已计算
- [ ] 结论已输出

---

### Step 2: 计算CTR差异的95%置信区间

**本步骤要做什么**：计算两组点击率差异的置信区间。

**本步骤输出产物**：
- 控制台输出：CTR差异及95%CI

**具体操作指引**：
1. 计算差异的标准误（使用各自比例）
2. 计算95% CI
3. 判断CI是否包含0

**代码框架**：
```python
se_diff = np.sqrt(p_con * (1 - p_con) / n_con + p_exp * (1 - p_exp) / n_exp)
diff = p_exp - p_con
ci_lower = diff - 1.96 * se_diff
ci_upper = diff + 1.96 * se_diff
```

**本步骤完成后的检查标准**：
- [ ] CI已计算
- [ ] 已判断是否包含0

---

### Step 3: 计算Cohen's h效应量

**本步骤要做什么**：计算并解释效应量，评估差异的实际业务意义。

**本步骤输出产物**：
- 控制台输出：Cohen's h值及效应量解释

**具体操作指引**：
1. 计算Cohen's h：`h = 2 * (arcsin(sqrt(p_exp)) - arcsin(sqrt(p_con)))`
2. 根据阈值解释效应量大小

**效应量标准**：
| h值 | 解释 |
|-----|------|
| < 0.2 | 可忽略 |
| 0.2 ~ 0.5 | 小效应 |
| 0.5 ~ 0.8 | 中等效应 |
| ≥ 0.8 | 大效应 |

**代码框架**：
```python
h = 2 * (np.arcsin(np.sqrt(p_exp)) - np.arcsin(np.sqrt(p_con)))
```

**本步骤完成后的检查标准**：
- [ ] Cohen's h已计算
- [ ] 效应量已解释

---

### Step 4: 统计功效分析与MDE计算

**本步骤要做什么**：计算当前实验的统计功效，以及最小可检测效应。

**本步骤输出产物**：
- 控制台输出：统计功效、MDE

**具体操作指引**：
1. 使用 `statsmodels` 计算统计功效
2. 使用数值方法求解MDE
3. 评估功效是否充足（≥80%）

**代码框架**：
```python
from statsmodels.stats.power import zt_ind_solve_power
from statsmodels.stats.proportion import proportion_effectsize

effect_size = proportion_effectsize(p_exp, p_con)
power = zt_ind_solve_power(
    effect_size=effect_size,
    nobs1=n_exp,
    alpha=0.05,
    ratio=n_con/n_exp,
    alternative="larger"
)
```

**本步骤完成后的检查标准**：
- [ ] 统计功效已计算
- [ ] MDE已计算（或尝试计算）

---

### Step 5: 保存检验结果

**本步骤要做什么**：将所有检验结果汇总保存。

**本步骤输出产物**：
- 文件：`outputs/tables/ch03_hypothesis_test_results.csv`

**具体操作指引**：
1. 汇总所有结果到DataFrame
2. 保存到表格目录

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物类型 | 文件名 | 存放路径 |
|---------|--------|----------|
| 表格 | ch03_hypothesis_test_results.csv | outputs/tables/ |

### 3.2 关键产物结构详解

**ch03_hypothesis_test_results.csv**：
| 字段 | 说明 |
|------|------|
| n_con, n_exp | 两组样本量 |
| p_con, p_exp | 两组点击率 |
| z_stat | Z统计量 |
| p_value | p值 |
| ci_lower, ci_upper | 差异的95%CI |
| cohens_h | 效应量 |
| power | 统计功效 |
| mde | 最小可检测效应 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅进行单尾检验，未展示双尾检验结果

### 4.2 可进一步优化的方向
- 可增加贝叶斯检验作为补充
- 可增加敏感性分析

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 检验类型是否保持单尾（或需要双尾）

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|----------|
| statsmodels未安装 | pip install statsmodels |
| MDE计算不收敛 | 扩大搜索范围或跳过 |

---

---

# Prompt-04: ch04 时间趋势分析

## 一、任务概述

### 1.1 本次任务是什么

按天和按小时分析点击率的时间变化趋势，检测是否存在新奇效应（Novelty Effect）或学习效应，增强结论的稳健性。

### 1.2 从什么数据出发

- **输入数据**：`data/processed/cleaned_data.csv`
- **时间范围**：2024-01-01 ~ 2024-01-07（7天）
- **依赖章节**：ch01（数据清洗）

### 1.3 可以采用什么方法

- 按天分组聚合：`df.groupby([df['timestamp'].dt.date, 'group'])`
- 按小时分组聚合：`df.groupby([df['timestamp'].dt.hour, 'group'])`
- 新奇效应检测：比较实验组前半期vs后半期点击率
- 可视化：时间序列折线图

---

## 二、执行步骤

### Step 1: 按天分析点击率趋势

**本步骤要做什么**：按天统计两组的点击率，观察随时间的变化。

**本步骤输出产物**：
- 控制台输出：按天点击率统计表
- 文件：`outputs/tables/ch04_daily_ctr_trend.csv`

**具体操作指引**：
1. 提取日期：`df['timestamp'].dt.date`
2. 按日期和分组聚合
3. 计算每天的点击率
4. 保存透视表

**代码框架**：
```python
df["date"] = df["timestamp"].dt.date
daily_stats = df.groupby(["date", "group"]).agg({
    "click": ["count", "sum", "mean"]
}).reset_index()
daily_stats.columns = ["date", "group", "users", "clicks", "ctr"]
```

**本步骤完成后的检查标准**：
- [ ] 按天统计表已生成
- [ ] 数据已保存

---

### Step 2: 按小时分析点击率趋势

**本步骤要做什么**：按小时统计两组的点击率，观察日内变化模式。

**本步骤输出产物**：
- 控制台输出：按小时点击率统计（前10行）
- 文件：`outputs/tables/ch04_hourly_ctr_trend.csv`

**具体操作指引**：
1. 提取小时：`df['timestamp'].dt.hour`
2. 按小时和分组聚合
3. 保存结果

**代码框架**：
```python
df["hour"] = df["timestamp"].dt.hour
hourly_stats = df.groupby(["hour", "group"]).agg({
    "click": ["count", "sum", "mean"]
}).reset_index()
```

**本步骤完成后的检查标准**：
- [ ] 按小时统计表已生成
- [ ] 数据已保存

---

### Step 3: 绘制时间趋势图

**本步骤要做什么**：绘制按天和按小时的点击率趋势折线图。

**本步骤输出产物**：
- 文件：`outputs/figures/ch04_daily_ctr_trend.png`
- 文件：`outputs/figures/ch04_hourly_ctr_trend.png`

**具体操作指引**：
1. 创建按天趋势图（折线图+标记）
2. 创建按小时趋势图
3. 添加图例、标题、网格
4. 保存图表

**代码框架**：
```python
fig, ax = plt.subplots(figsize=(10, 6))
for group, color in zip(["con", "exp"], ["#DD8452", "#4C72B0"]):
    data = daily_stats[daily_stats["group"] == group]
    ax.plot(data["date"], data["ctr"], marker="o", label=group.upper(), color=color)
ax.set_title("A/B测试点击率按天趋势")
ax.legend()
ax.grid(True, alpha=0.3)
```

**本步骤完成后的检查标准**：
- [ ] 两张趋势图已保存
- [ ] 图表清晰可读

---

### Step 4: 新奇效应检测

**本步骤要做什么**：检测实验组是否存在新奇效应（初期点击率高，随后下降）。

**本步骤输出产物**：
- 控制台输出：新奇效应检测结果及建议

**具体操作指引**：
1. 将实验期分为前半期和后半期
2. 计算两期的平均点击率
3. 比较差异，判断是否存在新奇效应

**判断标准**：
- 前半期 CTR > 后半期 CTR 超过10% → 可能存在新奇效应
- 差异在±10%以内 → 趋势稳定

**代码框架**：
```python
exp_ctrs = daily_pivot["exp_ctr"].values
first_half = np.mean(exp_ctrs[:len(exp_ctrs)//2])
second_half = np.mean(exp_ctrs[len(exp_ctrs)//2:])
diff_pct = (first_half - second_half) / first_half * 100
```

**本步骤完成后的检查标准**：
- [ ] 新奇效应检测已完成
- [ ] 结论已输出

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物类型 | 文件名 | 存放路径 |
|---------|--------|----------|
| 表格 | ch04_daily_ctr_trend.csv | outputs/tables/ |
| 表格 | ch04_hourly_ctr_trend.csv | outputs/tables/ |
| 图表 | ch04_daily_ctr_trend.png | outputs/figures/ |
| 图表 | ch04_hourly_ctr_trend.png | outputs/figures/ |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅进行简单的分段比较，未使用统计检验

### 4.2 可进一步优化的方向
- 可增加趋势线的统计检验
- 可增加周内效应分析（工作日vs周末）

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 时间分组粒度是否需要调整（如按半天）

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|----------|
| 时间数据格式错误 | 检查ch01的转换是否正确 |
| 某天数据量过少 | 记录并报告 |

---

---

# Prompt-05: ch05 结论与决策建议

## 一、任务概述

### 1.1 本次任务是什么

综合ch02-ch04的所有分析结果，基于严格决策框架（p值 + 效应量 + 统计功效）做出明确的业务决策建议，并生成完整的决策报告。

### 1.2 从什么数据出发

- **输入数据**：
  - `data/processed/cleaned_data.csv`
  - `outputs/tables/ch02_group_metrics_with_ci.csv`
  - `outputs/tables/ch03_hypothesis_test_results.csv`
- **依赖章节**：ch02, ch03, ch04

### 1.3 可以采用什么方法

- **严格决策矩阵**：综合p值、Cohen's h、统计功效进行决策
- **报告生成**：Markdown格式结构化报告

---

## 二、执行步骤

### Step 1: 加载并汇总所有分析结果

**本步骤要做什么**：读取前面章节的分析结果，汇总关键指标。

**本步骤输出产物**：
- 控制台输出：基础统计、假设检验结果汇总

**具体操作指引**：
1. 加载清洗后数据，计算基础统计
2. 尝试加载ch02和ch03的结果文件
3. 汇总所有关键指标

**代码框架**：
```python
def load_previous_results(config):
    results = {}
    try:
        ch03_path = config.tables_dir / "ch03_hypothesis_test_results.csv"
        if ch03_path.exists():
            results["ch03"] = pd.read_csv(ch03_path).iloc[0].to_dict()
    except:
        pass
    return results
```

**本步骤完成后的检查标准**：
- [ ] 基础统计已计算
- [ ] 前面章节结果已加载（如存在）

---

### Step 2: 基于决策框架做出决策

**本步骤要做什么**：应用严格决策矩阵，得出业务决策建议。

**严格决策矩阵**：

| 条件 | 决策建议 |
|------|----------|
| p<0.05 且 h≥0.2 且 功效≥0.8 | ✅ 全量上线 |
| p<0.05 且 h<0.2 | ⚠️ 灰度发布 |
| p≥0.05 且 功效<0.8 | 🔄 需要进一步实验 |
| p≥0.05 且 功效≥0.8 | ❌ 放弃该版本 |

**本步骤输出产物**：
- 控制台输出：决策条件、决策逻辑、最终决策

**具体操作指引**：
1. 检查p值、Cohen's h、统计功效
2. 应用决策矩阵
3. 输出决策及理由

**代码框架**：
```python
if p_value < 0.05 and cohens_h >= 0.2 and power >= 0.8:
    decision = "全量上线"
    reason = "统计显著+效应有意义+功效充足"
elif p_value < 0.05 and cohens_h < 0.2:
    decision = "灰度发布"
    reason = "统计显著但效应量过小"
# ...
```

**本步骤完成后的检查标准**：
- [ ] 决策已做出
- [ ] 理由已说明

---

### Step 3: 生成决策报告

**本步骤要做什么**：生成完整的Markdown格式决策报告。

**本步骤输出产物**：
- 文件：`outputs/tables/ch05_decision_report.md`

**报告结构**：
1. 实验概况
2. 关键发现（CTR对比表）
3. 统计检验结果
4. 决策建议（结论、理由、风险）
5. 后续行动（根据决策类型定制）

**具体操作指引**：
1. 使用f-string或模板生成报告
2. 根据决策类型生成对应的后续行动建议
3. 保存为Markdown文件

**本步骤完成后的检查标准**：
- [ ] 报告已生成
- [ ] 报告包含所有必要章节

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物类型 | 文件名 | 存放路径 |
|---------|--------|----------|
| 报告 | ch05_decision_report.md | outputs/tables/ |

### 3.2 关键产物结构详解

**ch05_decision_report.md**：
- 实验概况：时间、样本量、指标
- 关键发现：CTR对比表
- 统计检验：Z统计量、p值、CI、效应量、功效
- 决策建议：结论、理由、风险
- 后续行动：根据决策类型的定制建议

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 决策框架为固定规则，未考虑业务上下文

### 4.2 可进一步优化的方向
- 可增加成本效益分析
- 可增加风险评估矩阵

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 决策阈值是否需要调整（如功效要求90%）
- 是否有额外的业务约束需要考虑

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|----------|
| 前面章节结果不存在 | 提示先执行ch02-ch04 |
| 关键指标缺失 | 使用默认值或跳过相关判断 |

---

# 附录：全局工具模块引用

## Skill-01: DataLoader（数据加载器）

**路径**：`src/utils/data_loader.py`

**核心函数**：
- `load_raw()`：加载原始数据
- `load_processed(filename)`：加载处理后数据
- `get_data_info(df)`：获取数据基本信息

## Skill-02: Visualizer（可视化出图器）

**路径**：`src/utils/visualizer.py`

**核心函数**：
- `save_figure(fig, filename, chapter_prefix)`：保存图表
- `create_bar_plot(...)`：创建柱状图
- `create_histogram(...)`：创建直方图

## Skill-03: Metrics（评估指标计算器）

**路径**：`src/utils/metrics.py`

**核心函数**：
- `null_summary(df)`：缺失值汇总
- `duplicate_summary(df)`：重复值汇总
- `describe_all(df)`：描述性统计

## Skill-04: OutputManager（输出产物管理器）

**路径**：`src/utils/output_manager.py`

**核心函数**：
- `save_table(df, filename, chapter_prefix)`：保存表格
- `save_data(df, filename)`：保存数据文件
- `save_json(data, filename, chapter_prefix)`：保存JSON

---

# 执行顺序总结

## 批次划分

| 批次 | 章节 | 执行命令 | 依赖 |
|------|------|----------|------|
| 第1批 | ch01 | `python src/ch01_data_cleaning/run.py` | 无 |
| 第2批 | ch02 | `python src/ch02_metrics_visualization/run.py` | ch01 |
| 第2批 | ch03 | `python src/ch03_hypothesis_testing/run.py` | ch01 |
| 第2批 | ch04 | `python src/ch04_time_trend_analysis/run.py` | ch01 |
| 第3批 | ch05 | `python src/ch05_conclusion_recommendation/run.py` | ch02,ch03,ch04 |

## 一键执行脚本

```bash
# 顺序执行所有章节
cd /sessions/69fc7f204c1c339dc1cd197d/workspace
python src/ch01_data_cleaning/run.py
python src/ch02_metrics_visualization/run.py
python src/ch03_hypothesis_testing/run.py
python src/ch04_time_trend_analysis/run.py
python src/ch05_conclusion_recommendation/run.py
```
