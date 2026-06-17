# ch01 数据清洗

## 背景
本章对原始销售数据 product_sales_dataset.csv 进行全面的数据质量检查和清洗。
数据包含 1000 条记录、8 个字段，时间跨度 2025-01-02 至 2026-05-16。

原始数据字段包括：Product_ID, Product_Name, Category, Price_USD, Quantity_Sold, Total_Sales_USD, Order_Date, Customer_City。

## 分析方法
- **缺失值检测**：逐列统计缺失数量和比例，使用 `df.isnull().sum()` 和 `df.isnull().mean()`
- **重复值检测**：检查完全重复的记录行，使用 `df.duplicated().sum()`
- **时间戳解析**：将 Order_Date 转换为 datetime 类型，使用 `pd.to_datetime()`
- **数据类型验证**：确保数值字段为 int64，分类字段为 object

## 分析发现

### 数据概况
- 数据形状：1000 行 × 8 列
- 缺失值：全部字段无缺失（总缺失值数量：0）
- 重复值：无重复记录（重复记录数：0）

### 时间范围
- 日期范围：2025-01-02 至 2026-05-16
- 数据覆盖约 17 个月的销售记录

### 字段统计
| 字段 | 类型 | 说明 |
|------|------|------|
| Product_ID | int64 | 产品唯一标识 |
| Product_Name | object | 产品名称（24 种） |
| Category | object | 产品品类（6 个） |
| Price_USD | int64 | 单价（范围：$10 - $500） |
| Quantity_Sold | int64 | 销量（范围：1 - 10） |
| Total_Sales_USD | int64 | 总销售额（范围：$10 - $5000） |
| Order_Date | datetime64 | 订单日期 |
| Customer_City | object | 客户城市（5 个） |

### 品类分布
- 品类数量：6 个
- 品类列表：Beauty, Books, Electronics, Fashion, Home, Sports

### 城市分布
- 城市数量：5 个
- 城市列表：Islamabad, Karachi, Lahore, Peshawar, Quetta

### 销售概况
- 产品种类：24 种
- 总销售额：$1,371,032
- 总销量：5,455 件
- 平均客单价：$1,371.03

## 小结
- **数据质量良好**：无缺失值、无重复记录，数据完整性高
- **无需额外清洗处理**：数据可直接用于下游分析
- **产物清单**：ch01_cleaned_data.csv
- **后续使用**：清洗后数据可供 ch02（描述性统计）、ch03（销售预测）、ch04（价格弹性分析）直接使用
