# Genesis_Anomaly_Analysis 项目规范

> 版本：v2.0
> 生成日期：2026-06-02
> 基于：project_convention 技能模板

---

## 一、项目结构总览

```
Genesis_Anomaly_Analysis/
├── data/                          # 原始数据（只读，禁止修改）
│   └── 原始数据1/
│       ├── Genesis_AnomalyLabels.csv
│       ├── Genesis_StateMachineLabel.csv
│       ├── Genesis_lineardrive.csv
│       ├── Genesis_normal.csv
│       └── Genesis_pressure.csv
├── docs/                          # 项目文档
│   ├── analysis_goals.md          # 分析目标文档
│   ├── project_convention.md      # 本规范文档
│   └── flow_design.md             # 流程设计文档（后续生成）
├── src/                           # 源代码
│   ├── utils/                     # 工具模块
│   │   ├── config.py              # 全局配置
│   │   ├── data_loader.py         # 数据加载器
│   │   ├── visualizer.py          # 可视化工具
│   │   ├── metrics.py             # 评估指标
│   │   ├── output_manager.py      # 输出管理
│   │   └── task_graph.py          # 任务依赖图
│   ├── ch01_data_overview_and_cleaning/
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch02_plc_state_machine_analysis/
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch03_anomaly_detection_analysis/
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch04_sensor_performance_analysis/
│   │   ├── script.py
│   │   └── notebook.ipynb
│   └── ch05_performance_evaluation/
│       ├── script.py
│       └── notebook.ipynb
├── outputs/                       # 分析产物（按章节归档）
│   ├── ch01_data_overview_and_cleaning/
│   │   ├── report.md
│   │   └── figures/
│   ├── ch02_plc_state_machine_analysis/
│   │   ├── report.md
│   │   └── figures/
│   ├── ch03_anomaly_detection_analysis/
│   │   ├── report.md
│   │   └── figures/
│   ├── ch04_sensor_performance_analysis/
│   │   ├── report.md
│   │   └── figures/
│   └── ch05_performance_evaluation/
│       ├── report.md
│       └── figures/
├── project_params.json            # 项目参数配置
├── requirements.txt               # Python 依赖
└── README.md                      # 项目说明（可选）
```

---

## 二、命名规范

### 2.1 目录命名
- 章节目录：`ch{两位数字}_{英文名称}/`
- 工具目录：`utils/`（固定）
- 产物目录：与章节目录同名

### 2.2 脚本命名
- Python 脚本：`script.py`（章节主脚本）
- Notebook：`notebook.ipynb`
- 工具模块：`{功能}_utils.py` 或 `{功能}.py`

### 2.3 产物命名
- 报告：`report.md`（固定）
- 图表：`{描述}_{类型}.png`，如 `signal_timeseries_ch01.png`
- 数据表：`{描述}_table.csv`

### 2.4 变量命名
- 遵循 PEP8：小写 + 下划线
- 常量：全大写 + 下划线
- 类名：PascalCase

---

## 三、脚本编写规范

### 3.1 Python 脚本结构
```python
"""
章节标题：{name_cn}
章节ID：ch{XX}
目标：{一句话描述本章目标}
依赖：{前置章节}
"""

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import *
from utils.data_loader import *
from utils.visualizer import *

# 1. 数据加载
# 2. 分析处理
# 3. 结果输出
# 4. 报告生成
```

### 3.2 Notebook 结构
- 与 `script.py` 执行逻辑一致
- 每个 cell 有清晰注释
- 输出图表直接嵌入

### 3.3 代码质量
- 遵循 PEP8
- 关键函数添加类型注解
- 复杂逻辑添加 docstring
- 禁止硬编码参数（使用 `config.py`）

---

## 四、禁止事项清单

1. **禁止修改 `data/` 目录** — 原始数据只读，分析结果写入 `outputs/`
2. **禁止跨章节写入产物** — 每个章节的产物只能写入自己的 `outputs/chXX/` 目录
3. **禁止在项目根目录散落文件** — 所有文件必须归入 `src/`、`docs/`、`outputs/`、`data/`
4. **禁止跳过依赖直接执行** — 必须按批次顺序执行（ch01 → ch02 → ...）
5. **禁止在代码中硬编码参数** — 全局参数统一放入 `src/utils/config.py`
6. **禁止重复生成相同产物** — 检查产物是否存在，避免覆盖
7. **禁止在 Notebook 中直接修改数据文件** — 数据操作通过 `data_loader.py` 封装

---

## 五、环境配置

### 5.1 Python 版本
- 指定版本：Python 3.10
- 环境名：`py310`

### 5.2 依赖安装
```bash
pip install -r requirements.txt
```

### 5.3 运行脚本
```bash
# 单个章节
python src/ch01_data_overview_and_cleaning/script.py

# 按依赖顺序批量运行
# （由 task_dispatch 生成具体命令）
```

---

## 六、产物完整性检查

### 6.1 通用检查项
- [ ] `outputs/chXX/report.md` 存在且非空
- [ ] `outputs/chXX/figures/` 目录存在
- [ ] 图表文件格式为 PNG
- [ ] 数据表格式为 CSV

### 6.2 章节自定义检查项

| 章节 | 必含产物 |
|------|---------|
| ch01 | 数据集基本信息表、信号分布图 |
| ch02 | PLC 状态转移图、工序时序图、工序耗时表 |
| ch03 | 正常/异常信号对比图、畸变特征量化表、特征重要性排序 |
| ch04 | 传感器相关性热力图、信号稳定性评分表 |
| ch05 | 效率对比表、异常率统计、数据集局限性清单 |

### 6.3 report.md 四段框架
每个章节的 `report.md` 必须包含：
1. **背景** — 本章分析目的和数据来源
2. **分析方法** — 使用的技术和步骤
3. **分析发现** — 关键结果和图表
4. **小结** — 结论和下一步建议

---

## 七、依赖管理

### 7.1 章节依赖关系

```
ch01（数据概览与清洗）
 ├── ch02（PLC 状态机与工序分析）
 │    └── ch03（异常检测与抗干扰分析）
 │         └── ch05（运行效能评估）
 └── ch04（传感器性能关联分析）
      └── ch05（运行效能评估）
```

### 7.2 执行批次

| 批次 | 章节 | 说明 |
|------|------|------|
| Batch 1 | ch01 | 基础数据准备 |
| Batch 2 | ch02, ch04 | 并行执行（均依赖 ch01） |
| Batch 3 | ch03 | 依赖 ch02 |
| Batch 4 | ch05 | 汇总（依赖 ch03, ch04） |

---

## 八、数据文件清单

| 文件名 | 路径 | 用途 |
|--------|------|------|
| Genesis_AnomalyLabels.csv | data/原始数据1/ | 异常标签数据 |
| Genesis_StateMachineLabel.csv | data/原始数据1/ | 状态机标签数据 |
| Genesis_lineardrive.csv | data/原始数据1/ | 直线驱动工况参考 |
| Genesis_normal.csv | data/原始数据1/ | 正常工况参考 |
| Genesis_pressure.csv | data/原始数据1/ | 气压工况参考 |

---

## 九、修订记录

| 版本 | 日期 | 修订内容 |
|------|------|---------|
| v1.0 | 2026-06-02 | 初始版本，基于 project_convention v2.0 模板生成 |
