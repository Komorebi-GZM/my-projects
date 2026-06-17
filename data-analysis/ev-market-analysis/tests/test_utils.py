"""
工具模块单元测试

测试 src/utils/ 下的核心工具函数：
- data_loader: 数据加载
- visualizer: 可视化
- metrics: 指标计算
- output_manager: 输出管理
"""

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.config import (
    PROJECT_ROOT as CONFIG_PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_BASE,
    CHAPTER_CONFIG,
    ENTITY_CONFIG,
    DOMAIN_PARAMS,
    PLT_STYLE,
)
from utils.data_loader import load_raw_data, load_preprocessed
from utils.metrics import calc_mae, calc_rmse, calc_mape, evaluate_model, compare_models, calc_r2
from utils.output_manager import ensure_dir, get_chapter_dir, save_dataframe, save_markdown


# ──────────────────────────────────────────────
# config.py 测试
# ──────────────────────────────────────────────
class TestConfig:
    """配置模块测试"""

    def test_project_root_exists(self):
        """验证项目根目录存在"""
        assert CONFIG_PROJECT_ROOT.exists(), f"项目根目录不存在: {CONFIG_PROJECT_ROOT}"

    def test_data_dir_exists(self):
        """验证数据目录存在"""
        assert DATA_DIR.exists(), f"数据目录不存在: {DATA_DIR}"

    def test_output_base_exists(self):
        """验证输出目录存在"""
        assert OUTPUT_BASE.exists(), f"输出目录不存在: {OUTPUT_BASE}"

    def test_chapter_config_complete(self):
        """验证章节配置完整（9章）"""
        assert len(CHAPTER_CONFIG) == 9, f"章节配置应为9章，实际为{len(CHAPTER_CONFIG)}章"
        for i in range(1, 10):
            assert i in CHAPTER_CONFIG, f"缺少第{i}章配置"

    def test_entity_config_has_brands(self):
        """验证实体配置包含品牌列表"""
        assert "brands" in ENTITY_CONFIG, "实体配置缺少 brands 字段"
        assert len(ENTITY_CONFIG["brands"]) == 20, f"品牌数量应为20，实际为{len(ENTITY_CONFIG['brands'])}"

    def test_plt_style_has_required_keys(self):
        """验证可视化样式配置完整"""
        required_keys = ["style", "font_size", "figure_dpi", "save_dpi", "color_palette"]
        for key in required_keys:
            assert key in PLT_STYLE, f"PLT_STYLE 缺少必要配置项: {key}"


# ──────────────────────────────────────────────
# data_loader.py 测试
# ──────────────────────────────────────────────
class TestDataLoader:
    """数据加载器测试"""

    def test_load_raw_data_success(self):
        """验证原始数据加载成功"""
        df = load_raw_data()
        assert df is not None, "数据加载失败"
        assert len(df) > 0, "数据为空"

    def test_load_raw_data_shape(self):
        """验证原始数据形状正确"""
        df = load_raw_data()
        # 原始数据应为 2000 行 x 24 列
        assert df.shape[0] == 2000, f"原始数据行数应为2000，实际为{df.shape[0]}"
        assert df.shape[1] == 24, f"原始数据列数应为24，实际为{df.shape[1]}"

    def test_load_preprocessed_success(self):
        """验证预处理数据加载成功"""
        df = load_preprocessed()
        assert df is not None, "预处理数据加载失败"
        # 清洗后数据应为 1070 行 x 27 列
        assert df.shape[0] == 1070, f"清洗后数据行数应为1070，实际为{df.shape[0]}"
        assert df.shape[1] == 27, f"清洗后数据列数应为27，实际为{df.shape[1]}"


# ──────────────────────────────────────────────
# metrics.py 测试
# ──────────────────────────────────────────────
class TestMetrics:
    """指标计算器测试"""

    def test_calc_mae(self):
        """验证 MAE 计算正确"""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.2, 2.9, 4.1, 4.8])
        mae = calc_mae(y_true, y_pred)
        expected = np.mean(np.abs(y_true - y_pred))
        assert abs(mae - expected) < 1e-6, f"MAE 计算错误: {mae} != {expected}"

    def test_calc_rmse(self):
        """验证 RMSE 计算正确"""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        rmse = calc_rmse(y_true, y_pred)
        assert rmse == 0.0, f"完美预测的 RMSE 应为0，实际为{rmse}"

    def test_calc_mape(self):
        """验证 MAPE 计算正确"""
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 310.0])
        mape = calc_mape(y_true, y_pred)
        # MAPE = mean(|100-110|/100, |200-190|/200, |300-310|/300) * 100
        # = (0.1 + 0.05 + 0.0333) / 3 * 100 ≈ 6.11%
        assert 5 < mape < 7, f"MAPE 计算结果异常: {mape}"

    def test_calc_r2(self):
        """验证 R² 计算正确"""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        r2 = calc_r2(y_true, y_pred)
        assert r2 == 1.0, f"完美预测的 R² 应为1，实际为{r2}"

    def test_evaluate_model(self):
        """验证综合评估函数"""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        result = evaluate_model(y_true, y_pred, "TestModel", verbose=False)
        assert "model" in result, "结果缺少 model 字段"
        assert "mae" in result, "结果缺少 mae 字段"
        assert "rmse" in result, "结果缺少 rmse 字段"
        assert "mape" in result, "结果缺少 mape 字段"

    def test_compare_models(self):
        """验证模型对比函数"""
        results = [
            {"model": "ModelA", "mae": 0.1, "rmse": 0.15, "mape": 5.0},
            {"model": "ModelB", "mae": 0.2, "rmse": 0.25, "mape": 10.0},
        ]
        df = compare_models(results, sort_by="mape")
        assert len(df) == 2, "对比表行数错误"
        assert df.iloc[0]["Model"] == "ModelA", "排序错误，ModelA 应排在第一"


# ──────────────────────────────────────────────
# output_manager.py 测试
# ──────────────────────────────────────────────
class TestOutputManager:
    """输出管理器测试"""

    def test_ensure_dir(self):
        """验证目录创建功能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_subdir" / "nested"
            result = ensure_dir(test_dir)
            assert result.exists(), "目录未创建"
            assert result.is_dir(), "创建的不是目录"

    def test_get_chapter_dir(self):
        """验证章节目录获取"""
        for ch_num in range(1, 10):
            ch_key = f"ch{ch_num:02d}"
            ch_dir = get_chapter_dir(ch_key)
            assert ch_dir.exists(), f"章节目录不存在: {ch_dir}"
            assert "ch" in str(ch_dir), f"章节目录路径异常: {ch_dir}"

    def test_save_dataframe(self):
        """验证 DataFrame 保存功能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
            filepath = Path(tmpdir) / "test_data.csv"
            result = save_dataframe(df, filepath, verbose=False)
            assert result.exists(), "文件未创建"
            # 验证内容
            loaded = pd.read_csv(filepath)
            assert len(loaded) == 3, "保存的数据行数错误"

    def test_save_markdown(self):
        """验证 Markdown 保存功能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# Test Report\n\nThis is a test."
            filepath = Path(tmpdir) / "test_report.md"
            result = save_markdown(content, filepath, verbose=False)
            assert result.exists(), "文件未创建"
            # 验证内容
            loaded = filepath.read_text(encoding="utf-8")
            assert "Test Report" in loaded, "保存的内容不完整"


# ──────────────────────────────────────────────
# 集成测试
# ──────────────────────────────────────────────
class TestIntegration:
    """集成测试"""

    def test_cleaned_data_quality(self):
        """验证清洗后数据质量"""
        df = load_preprocessed()
        
        # 无缺失值
        assert df.isnull().sum().sum() == 0, "清洗后数据存在缺失值"
        
        # 无重复键
        key_cols = ["brand", "model", "year", "variant"]
        dup_count = df.duplicated(subset=key_cols).sum()
        assert dup_count == 0, f"存在 {dup_count} 条重复记录"
        
        # 派生特征存在
        derived_features = ["price_per_kwh", "efficiency", "power_to_weight"]
        for col in derived_features:
            assert col in df.columns, f"缺少派生特征: {col}"

    def test_chapter_dirs_exist(self):
        """验证所有章节输出目录存在"""
        for ch_num, ch_config in CHAPTER_CONFIG.items():
            ch_dir = OUTPUT_BASE / ch_config["dir_name"]
            assert ch_dir.exists(), f"章节目录不存在: {ch_dir}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
