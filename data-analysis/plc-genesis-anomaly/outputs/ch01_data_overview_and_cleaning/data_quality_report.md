# 数据质量评估报告 (ch01)

## 1. 数据概况

| 指标 | 数值 |
|------|------|
| 数据文件总数 | 5 |
| 总记录行数 | 55,380 |
| 总单元格数 | 1,143,980 |
| 时间范围 | 2016-04-20 10:35:12.937999964 ~ 2017-07-24 17:01:15.730000 |

### 各文件基本信息

| file                          |   rows |   columns | time_range                                                    |
|:------------------------------|-------:|----------:|:--------------------------------------------------------------|
| Genesis_AnomalyLabels.csv     |  16220 |        19 | 2016-04-20 10:35:12.937999964 ~ 2016-04-20 10:47:53.354000092 |
| Genesis_StateMachineLabel.csv |  16220 |        19 | 2016-04-20 10:35:12.937999964 ~ 2016-04-20 10:47:53.354000092 |
| Genesis_lineardrive.csv       |   7424 |        23 | 2017-07-24 16:47:44.061000 ~ 2017-07-24 16:53:32.213000       |
| Genesis_normal.csv            |   7040 |        23 | 2017-07-24 16:39:08.721000 ~ 2017-07-24 16:44:39.079000       |
| Genesis_pressure.csv          |   8476 |        23 | 2017-07-24 16:54:38.295000 ~ 2017-07-24 17:01:15.730000       |

## 2. 缺失值分析

| 指标 | 数值 |
|------|------|
| 总缺失单元格数 | 0 |
| 整体缺失率 | 0.0000% |

### 各文件缺失值统计

| file                          |   total_cells |   missing_cells |   missing_rate | missing_rate_pct   |
|:------------------------------|--------------:|----------------:|---------------:|:-------------------|
| Genesis_AnomalyLabels.csv     |        308180 |               0 |              0 | 0.0000%            |
| Genesis_StateMachineLabel.csv |        308180 |               0 |              0 | 0.0000%            |
| Genesis_lineardrive.csv       |        170752 |               0 |              0 | 0.0000%            |
| Genesis_normal.csv            |        161920 |               0 |              0 | 0.0000%            |
| Genesis_pressure.csv          |        194948 |               0 |              0 | 0.0000%            |

## 3. 信号范围汇总

| signal                             |     min |    max |         mean |         std |
|:-----------------------------------|--------:|-------:|-------------:|------------:|
| MotorData.ActCurrent               |   -1181 |   1181 |     -9.09563 |    434.668  |
| MotorData.ActPosition              |   22011 | 389992 | 207316       | 107774      |
| MotorData.ActSpeed                 | -422617 | 331267 |    102.302   |  54707.3    |
| MotorData.IsAcceleration           |   -3045 |   6090 |      1.31647 |    500.951  |
| MotorData.IsForce                  |    -256 |    260 |     -2.6957  |     96.3595 |
| MotorData.SetAcceleration          |  -65536 |  65535 |  29016.4     |  36937.8    |
| MotorData.SetCurrent               |   -1132 |   1132 |    -15.6702  |    497.727  |
| MotorData.SetForce                 |    -249 |    249 |     -3.33509 |    109.407  |
| MotorData.SetSpeed                 | -412322 | 412322 |  -3808.13    |  61379.5    |
| NVL_Recv_Storage.GL_X_TimeSlideIn  |     240 |  10000 |    428.139   |   1075.46   |
| NVL_Recv_Storage.GL_X_TimeSlideOut |     180 |    260 |    203.925   |     17.7924 |

## 4. 数据质量评估

### 完整性
- 整体缺失率极低（0.0000%），数据完整性良好。
- 所有5个CSV文件均无显著缺失值问题。

### 一致性
- 时间戳格式存在差异：前两个文件使用 Unix 秒，后三个文件使用 Unix 毫秒，已统一解析为 datetime。
- 列结构存在差异：AnomalyLabels 和 StateMachineLabel 有 20 列（含 Label），其余有 24 列（无 Label）。
- 共有模拟量信号列：MotorData.ActCurrent, MotorData.ActPosition, MotorData.ActSpeed, MotorData.IsAcceleration, MotorData.IsForce, MotorData.SetAcceleration, MotorData.SetCurrent, MotorData.SetForce, MotorData.SetSpeed, NVL_Recv_Storage.GL_X_TimeSlideIn, NVL_Recv_Storage.GL_X_TimeSlideOut

### 时效性
- 数据时间跨度覆盖正常工况、直线驱动工况和气压工况。
- 采样间隔约为 50ms（基于数据点密度估算）。

## 5. 使用建议

1. **时间戳处理**：后续分析中需注意不同文件的时间戳精度差异。
2. **列对齐**：进行跨文件对比时，建议仅使用共同列（模拟量信号列）。
3. **异常样本**：AnomalyLabels 中异常样本（Label=1/2）占比极低（约 0.3%），后续异常检测分析需注意样本不平衡问题。
4. **信号选择**：ActCurrent、ActPosition、ActSpeed 为核心电机信号，建议作为重点分析对象。
