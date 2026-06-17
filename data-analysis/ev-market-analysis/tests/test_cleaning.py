"""
数据清洗逻辑单元测试模块

对 ch01_data_cleaning 章节输出的 cleaned_data.csv 进行全面验证，
涵盖缺失值、重复键、数据类型、派生特征、数值范围等多个维度。
"""

import pandas as pd
import pytest

# 清洗后数据文件路径
CLEANED_DATA_PATH = (
    "/sessions/69fa11e03551c4fc0d3041bf/workspace/"
    "ev_market_analysis/outputs/ch01_data_cleaning/cleaned_data.csv"
)


@pytest.fixture(scope="module")
def df():
    """加载清洗后的数据，在整个测试模块中共享。"""
    return pd.read_csv(CLEANED_DATA_PATH)


# ──────────────────────────────────────────────
# 1. 缺失值检查
# ──────────────────────────────────────────────
def test_no_missing_values(df):
    """验证清洗后数据中不存在任何缺失值（NaN / NaT）。"""
    total_missing = df.isnull().sum().sum()
    assert total_missing == 0, (
        f"清洗后数据仍存在 {total_missing} 个缺失值，"
        f"分布如下:\n{df.isnull().sum()[df.isnull().sum() > 0]}"
    )


# ──────────────────────────────────────────────
# 2. 重复键检查
# ──────────────────────────────────────────────
def test_no_duplicate_keys(df):
    """验证 (brand, model, year, variant) 组合在数据集中无重复。"""
    key_cols = ["brand", "model", "year", "variant"]
    dup_count = df.duplicated(subset=key_cols).sum()
    assert dup_count == 0, (
        f"存在 {dup_count} 条重复的 (brand, model, year, variant) 记录"
    )


# ──────────────────────────────────────────────
# 3. 数据类型检查
# ──────────────────────────────────────────────
def test_data_types_correct(df):
    """验证关键列的数据类型是否正确。

    - year: 整数类型 (int)
    - safety_rating: 整数类型 (int)
    - brand: 分类类型或对象类型 (category / object)
    - price_usd: 数值类型 (float)
    - battery_capacity_kwh: 数值类型 (float)
    """
    # year 应为整数类型（pandas 读取 CSV 后可能是 int64 或 float64）
    assert pd.api.types.is_integer_dtype(df["year"]) or pd.api.types.is_float_dtype(df["year"]), (
        f"year 列类型应为整数类型，实际为 {df['year'].dtype}"
    )

    # safety_rating 应为整数类型
    assert pd.api.types.is_integer_dtype(df["safety_rating"]) or pd.api.types.is_float_dtype(df["safety_rating"]), (
        f"safety_rating 列类型应为整数类型，实际为 {df['safety_rating'].dtype}"
    )

    # brand 应为 object 或 category 类型
    assert pd.api.types.is_object_dtype(df["brand"]) or pd.api.types.is_categorical_dtype(df["brand"]), (
        f"brand 列类型应为 object 或 category，实际为 {df['brand'].dtype}"
    )

    # price_usd 应为数值类型
    assert pd.api.types.is_numeric_dtype(df["price_usd"]), (
        f"price_usd 列类型应为数值类型，实际为 {df['price_usd'].dtype}"
    )

    # battery_capacity_kwh 应为数值类型
    assert pd.api.types.is_numeric_dtype(df["battery_capacity_kwh"]), (
        f"battery_capacity_kwh 列类型应为数值类型，实际为 {df['battery_capacity_kwh'].dtype}"
    )


# ──────────────────────────────────────────────
# 4. 派生特征列存在性检查
# ──────────────────────────────────────────────
def test_derived_features_exist(df):
    """验证清洗后数据包含三个派生特征列：price_per_kwh、efficiency、power_to_weight。"""
    required_features = ["price_per_kwh", "efficiency", "power_to_weight"]
    missing = [col for col in required_features if col not in df.columns]
    assert len(missing) == 0, (
        f"缺少以下派生特征列: {missing}"
    )


# ──────────────────────────────────────────────
# 5. 派生特征正值检查
# ──────────────────────────────────────────────
def test_derived_features_positive(df):
    """验证三个派生特征列的值均为正数（> 0）。"""
    derived_features = ["price_per_kwh", "efficiency", "power_to_weight"]
    for col in derived_features:
        non_positive_count = (df[col] <= 0).sum()
        assert non_positive_count == 0, (
            f"派生特征 '{col}' 中有 {non_positive_count} 个非正值"
        )


# ──────────────────────────────────────────────
# 6. 价格范围合理性检查
# ──────────────────────────────────────────────
def test_price_range_reasonable(df):
    """验证 price_usd 在合理范围内（1000 < price_usd < 500000）。"""
    out_of_range = df[(df["price_usd"] <= 1000) | (df["price_usd"] >= 500000)]
    assert len(out_of_range) == 0, (
        f"存在 {len(out_of_range)} 条 price_usd 超出合理范围 (1000, 500000) 的记录"
    )


# ──────────────────────────────────────────────
# 7. 年份范围检查
# ──────────────────────────────────────────────
def test_year_range_valid(df):
    """验证 year 在 2020 至 2026 范围内（含边界）。"""
    out_of_range = df[(df["year"] < 2020) | (df["year"] > 2026)]
    assert len(out_of_range) == 0, (
        f"存在 {len(out_of_range)} 条 year 超出 2020-2026 范围的记录"
    )


# ──────────────────────────────────────────────
# 8. 安全评级范围检查
# ──────────────────────────────────────────────
def test_safety_rating_range(df):
    """验证 safety_rating 在 1 至 5 范围内（含边界）。"""
    out_of_range = df[(df["safety_rating"] < 1) | (df["safety_rating"] > 5)]
    assert len(out_of_range) == 0, (
        f"存在 {len(out_of_range)} 条 safety_rating 超出 1-5 范围的记录"
    )


# ──────────────────────────────────────────────
# 9. 客户评分范围检查
# ──────────────────────────────────────────────
def test_customer_rating_range(df):
    """验证 customer_rating 在 1 至 5 范围内（含边界）。"""
    out_of_range = df[(df["customer_rating"] < 1) | (df["customer_rating"] > 5)]
    assert len(out_of_range) == 0, (
        f"存在 {len(out_of_range)} 条 customer_rating 超出 1-5 范围的记录"
    )


# ──────────────────────────────────────────────
# 10. 保修年限范围检查
# ──────────────────────────────────────────────
def test_warranty_years_range(df):
    """验证 warranty_years 在合理范围内（1 <= warranty_years <= 10）。"""
    out_of_range = df[(df["warranty_years"] < 1) | (df["warranty_years"] > 10)]
    assert len(out_of_range) == 0, (
        f"存在 {len(out_of_range)} 条 warranty_years 超出 1-10 范围的记录"
    )
