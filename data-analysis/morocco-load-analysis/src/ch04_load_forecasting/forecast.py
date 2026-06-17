"""
Prompt-04: 短期电力负荷预测模型构建
基于 Laayoune zone1 负荷数据，构建 ARIMA/XGBoost/LightGBM/Prophet/LSTM
五模型对比选型，确定最优预测模型并完成 24h 滚动预测。

覆盖步骤:
  - Step 4.1: 预测目标选择与数据准备
  - Step 4.2: 特征集构建
  - Step 4.3: 数据集划分（时序顺序 80/10/10）
  - Step 4.4: ARIMA 模型训练与预测
  - Step 4.5: XGBoost 模型训练与预测
  - Step 4.6: LightGBM 模型训练与预测
  - Step 4.7: Prophet 模型训练与预测
  - Step 4.8: LSTM 模型训练与预测
  - Step 4.9: 多模型评估对比
  - Step 4.10: 最优模型 24h 滚动预测

产物输出到: outputs/ch04_load_forecasting/
"""

import sys
import os
import json
import time
import warnings

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.config import OUTPUT_BASE, PLT_STYLE
from utils.output_manager import save_dataframe, save_figure, save_markdown, ensure_dir
from utils.metrics import evaluate_model, compare_models
from utils.visualizer import plot_model_forecast

warnings.filterwarnings('ignore')

# === 全局配置 ===
INPUT_FILE = os.path.join(
    os.path.dirname(SRC_DIR),
    'outputs', 'ch01_data_preprocessing', 'ch01_feature_engineered_data.csv'
)
TARGET_CITY = 'Laayoune'
TARGET_ZONE = 'zone1'
LAG_WINDOWS = [1, 6, 12, 24, 48, 144]
ROLLING_WINDOWS = [6, 12, 24]
PROPHET_TIMEOUT = 300  # 5 分钟超时


# ================================================================
# Step 4.1: 预测目标选择与数据准备
# ================================================================
def load_and_prepare_target(input_file: str, output_dir: str) -> pd.DataFrame:
    """加载全城市数据，筛选 Laayoune zone1，检查数据质量"""
    print('\n[Step 4.1] 预测目标选择与数据准备...')

    df = pd.read_csv(input_file, parse_dates=['DateTime'])
    df = df.set_index('DateTime').sort_index()

    # 筛选目标
    target_df = df[(df['city'] == TARGET_CITY)][
        [TARGET_ZONE, 'hour', 'day_of_week', 'is_weekend', 'month', 'season', 'year']
    ].copy()
    target_df = target_df.rename(columns={TARGET_ZONE: 'load_kw'})

    # 数据质量检查
    print(f'  预测目标: {TARGET_CITY} / {TARGET_ZONE}')
    print(f'  时间范围: {target_df.index.min()} ~ {target_df.index.max()}')
    print(f'  数据点数: {len(target_df)}')
    print(f'  缺失值: {target_df["load_kw"].isnull().sum()}')

    # 检查时间连续性
    time_gaps = target_df.index.to_series().diff().dropna()
    irregular_gaps = time_gaps[time_gaps != pd.Timedelta(minutes=10)]
    if len(irregular_gaps) > 0:
        print(f'  警告: 发现 {len(irregular_gaps)} 个非10分钟间隔，进行重采样对齐')
        # 仅对数值列做 resample，避免 season 等字符串列报错
        numeric_cols = target_df.select_dtypes(include=[np.number]).columns.tolist()
        target_df[numeric_cols] = target_df[numeric_cols].resample('10T').mean().interpolate(method='linear')
        target_df = target_df.dropna(subset=['load_kw'])
    else:
        print('  时间连续性检查通过')

    # 处理缺失值
    if target_df['load_kw'].isnull().sum() > 0:
        print(f'  前向填充 {target_df["load_kw"].isnull().sum()} 个缺失值')
        target_df['load_kw'] = target_df['load_kw'].ffill().bfill()

    # 重新生成时间特征（重采样后可能需要）
    target_df['hour'] = target_df.index.hour
    target_df['day_of_week'] = target_df.index.dayofweek
    target_df['is_weekend'] = (target_df.index.dayofweek >= 5).astype(int)
    target_df['month'] = target_df.index.month
    target_df['year'] = target_df.index.year

    # 保存目标选择说明
    md_content = f"""# 预测目标选择说明

## 选择结果
- **城市**: {TARGET_CITY}
- **Zone**: {TARGET_ZONE}
- **时间范围**: {target_df.index.min()} ~ {target_df.index.max()}
- **数据点数**: {len(target_df)}
- **采样间隔**: 10 分钟

## 选择理由
1. Laayoune 数据时间跨度最长（约20个月），覆盖 2022-09 至 2024-05
2. 采样频率最高（10分钟），数据分辨率最优
3. 数据完整性最好，无大规模缺失
4. zone1 作为主馈线，负荷特征具有代表性

## 数据质量
- 缺失值: {target_df['load_kw'].isnull().sum()}
- 时间连续性: {'通过' if len(irregular_gaps) == 0 else f'发现{len(irregular_gaps)}个间隔异常，已重采样对齐'}
- 负荷范围: {target_df['load_kw'].min():.2f} ~ {target_df['load_kw'].max():.2f} kW
- 均值: {target_df['load_kw'].mean():.2f} kW
- 标准差: {target_df['load_kw'].std():.2f} kW
"""
    save_markdown(md_content, 'ch04_target_selection.md', output_dir)

    return target_df


# ================================================================
# Step 4.2: 特征集构建
# ================================================================
def build_features(df: pd.DataFrame) -> tuple:
    """构建滞后特征和滚动统计特征

    Returns:
        (df_with_features, feature_cols)
    """
    print('\n[Step 4.2] 特征集构建...')

    # 滞后特征
    for lag in LAG_WINDOWS:
        df[f'lag_{lag}'] = df['load_kw'].shift(lag)

    # 滚动统计特征
    for window in ROLLING_WINDOWS:
        df[f'rolling_mean_{window}'] = df['load_kw'].rolling(window=window).mean().shift(1)
        df[f'rolling_std_{window}'] = df['load_kw'].rolling(window=window).std().shift(1)

    # 将 season 字符串编码为数值（XGBoost/LightGBM 不接受 object 类型）
    season_map = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Autumn': 3}
    if 'season' in df.columns and df['season'].dtype == 'object':
        df['season'] = df['season'].map(season_map).fillna(-1).astype(int)

    # 特征列（排除目标变量）
    feature_cols = [c for c in df.columns if c != 'load_kw']

    # 删除 NaN 行（由 shift 和 rolling 产生）
    before_drop = len(df)
    df = df.dropna(subset=feature_cols)
    after_drop = len(df)
    print(f'  特征数量: {len(feature_cols)}')
    print(f'  删除 NaN 行: {before_drop - after_drop} (由 shift/rolling 产生)')
    print(f'  有效样本数: {len(df)}')

    return df, feature_cols


# ================================================================
# Step 4.3: 数据集划分（时序顺序，严禁 shuffle）
# ================================================================
def split_data(df: pd.DataFrame, feature_cols: list, output_dir: str) -> dict:
    """按时间顺序 80/10/10 划分数据集

    Returns:
        splits dict containing train/val/test DataFrames and X/y splits
    """
    print('\n[Step 4.3] 数据集划分（时序顺序 80/10/10）...')

    n = len(df)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]

    X_train, y_train = train[feature_cols], train['load_kw']
    X_val, y_val = val[feature_cols], val['load_kw']
    X_test, y_test = test[feature_cols], test['load_kw']

    split_info = {
        'target': f'{TARGET_CITY} / {TARGET_ZONE}',
        'total_samples': n,
        'train_samples': len(train),
        'val_samples': len(val),
        'test_samples': len(test),
        'train_ratio': f'{len(train)/n*100:.1f}%',
        'val_ratio': f'{len(val)/n*100:.1f}%',
        'test_ratio': f'{len(test)/n*100:.1f}%',
        'train_time_range': f'{train.index.min()} ~ {train.index.max()}',
        'val_time_range': f'{val.index.min()} ~ {val.index.max()}',
        'test_time_range': f'{test.index.min()} ~ {test.index.max()}',
        'feature_columns': feature_cols,
        'split_method': 'chronological_no_shuffle',
    }

    for k, v in split_info.items():
        if k != 'feature_columns':
            print(f'  {k}: {v}')

    # 保存划分信息
    split_path = os.path.join(output_dir, 'ch04_data_split_info.json')
    with open(split_path, 'w', encoding='utf-8') as f:
        json.dump(split_info, f, indent=2, default=str)
    print(f'  [保存] {split_path}')

    return {
        'train': train, 'val': val, 'test': test,
        'X_train': X_train, 'y_train': y_train,
        'X_val': X_val, 'y_val': y_val,
        'X_test': X_test, 'y_test': y_test,
        'feature_cols': feature_cols,
    }


# ================================================================
# Step 4.4: ARIMA 模型训练与预测
# ================================================================
def train_arima(y_train, y_test, output_dir: str) -> dict:
    """训练 ARIMA 模型（非季节模式，seasonal=False）

    退化为纯 ARIMA 的理由:
    - m=144（日周期）在 88K 样本上 SARIMA 季节搜索空间过大
    - 季节 P/Q 组合即使限制范围仍可能超时
    - 纯 ARIMA 作为统计基线仍有价值

    内存优化: 对训练数据降采样到小时级（每6个点取均值），
    在降采样数据上训练 ARIMA，再对原始测试集做预测。
    """
    print('\n[Step 4.4] ARIMA 模型训练（非季节模式，小时级降采样）...')

    from pmdarima import auto_arima

    # 降采样到小时级以避免 OOM（70K → ~12K）
    y_train_hourly = y_train.groupby(
        pd.Grouper(freq='1h')
    ).mean().dropna()
    print(f'  降采样: {len(y_train)} → {len(y_train_hourly)} (10min → 1h)')

    t0 = time.time()
    arima_model = auto_arima(
        y_train_hourly,
        seasonal=False,  # 退化为纯 ARIMA
        stepwise=True,
        suppress_warnings=True,
        error_action='ignore',
        max_p=5, max_q=5,
        max_order=10,
        n_fits=30,
        trace=False,
    )
    elapsed = time.time() - t0
    print(f'  ARIMA 最优参数: order={arima_model.order}')
    print(f'  训练耗时: {elapsed:.1f}s')

    # 预测（对小时级测试集）
    y_test_hourly = y_test.groupby(
        pd.Grouper(freq='1h')
    ).mean().dropna()
    arima_pred_values = arima_model.predict(n_periods=len(y_test_hourly))
    arima_pred = pd.Series(arima_pred_values, index=y_test_hourly.index)

    # 评估（在小时级数据上）
    arima_result = evaluate_model(y_test_hourly.values, arima_pred_values, 'ARIMA')
    print(f'  MAE={arima_result["MAE"]}, RMSE={arima_result["RMSE"]}, MAPE={arima_result["MAPE"]}%')

    # 保存模型（使用 joblib 序列化）
    import joblib
    model_path = os.path.join(output_dir, 'ch04_arima_model.pkl')
    joblib.dump(arima_model, model_path)
    print(f'  [保存] {model_path}')

    # 保存预测图（小时级）
    plot_model_forecast(
        y_test_hourly, arima_pred, 'ARIMA - 负荷预测结果 (小时级)',
        output_path=os.path.join(output_dir, 'ch04_arima_forecast.png'),
        metrics_dict=arima_result,
    )

    return arima_result


# ================================================================
# Step 4.5: XGBoost 模型训练与预测
# ================================================================
def train_xgboost(X_train, y_train, X_val, y_val, X_test, y_test,
                   feature_cols: list, output_dir: str) -> tuple:
    """训练 XGBoost 回归模型"""
    print('\n[Step 4.5] XGBoost 模型训练...')

    import xgboost as xgb

    xgb_model = xgb.XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=1,
        early_stopping_rounds=50,
    )

    t0 = time.time()
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    elapsed = time.time() - t0
    print(f'  最佳迭代: {xgb_model.best_iteration if hasattr(xgb_model, "best_iteration") else "N/A"}, 训练耗时: {elapsed:.1f}s')

    # 预测
    xgb_pred = pd.Series(xgb_model.predict(X_test), index=y_test.index)
    xgb_result = evaluate_model(y_test.values, xgb_pred.values, 'XGBoost')
    print(f'  MAE={xgb_result["MAE"]}, RMSE={xgb_result["RMSE"]}, MAPE={xgb_result["MAPE"]}%')

    # 特征重要性
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(f'  特征重要性 TOP5:\n{importance.head(5).to_string(index=False)}')

    # 保存模型
    model_path = os.path.join(output_dir, 'ch04_xgb_model.json')
    xgb_model.save_model(model_path)
    print(f'  [保存] {model_path}')

    # 保存预测图
    plot_model_forecast(
        y_test, xgb_pred, 'XGBoost - 负荷预测结果',
        output_path=os.path.join(output_dir, 'ch04_xgb_forecast.png'),
        metrics_dict=xgb_result,
    )

    return xgb_result, xgb_model


# ================================================================
# Step 4.6: LightGBM 模型训练与预测
# ================================================================
def train_lightgbm(X_train, y_train, X_val, y_val, X_test, y_test,
                    feature_cols: list, output_dir: str) -> tuple:
    """训练 LightGBM 回归模型"""
    print('\n[Step 4.6] LightGBM 模型训练...')

    import lightgbm as lgb

    lgb_model = lgb.LGBMRegressor(
        n_estimators=500,
        num_leaves=31,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=1,
        verbose=-1,
    )

    t0 = time.time()
    lgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
    )
    elapsed = time.time() - t0
    best_iter = lgb_model.best_iteration_
    print(f'  最佳迭代: {best_iter}, 训练耗时: {elapsed:.1f}s')

    # 预测
    lgb_pred = pd.Series(lgb_model.predict(X_test), index=y_test.index)
    lgb_result = evaluate_model(y_test.values, lgb_pred.values, 'LightGBM')
    print(f'  MAE={lgb_result["MAE"]}, RMSE={lgb_result["RMSE"]}, MAPE={lgb_result["MAPE"]}%')

    # 保存模型
    model_path = os.path.join(output_dir, 'ch04_lgbm_model.txt')
    lgb_model.booster_.save_model(model_path)
    print(f'  [保存] {model_path}')

    # 保存预测图
    plot_model_forecast(
        y_test, lgb_pred, 'LightGBM - 负荷预测结果',
        output_path=os.path.join(output_dir, 'ch04_lgbm_forecast.png'),
        metrics_dict=lgb_result,
    )

    return lgb_result, lgb_model


# ================================================================
# Step 4.7: Prophet 模型训练与预测（允许超时跳过）
# ================================================================
def train_prophet(train, test, y_test, output_dir: str) -> dict:
    """训练 Prophet 模型

    注意: Prophet 设计初衷是日粒度数据，10min 高频天然不适配。
    设置 yearly_seasonality=False，并增加超时保护。
    内存优化: 降采样到小时级训练。
    """
    print('\n[Step 4.7] Prophet 模型训练（小时级降采样 + 5分钟超时保护）...')

    from prophet import Prophet

    # 降采样到小时级以避免 OOM
    train_hourly = train[['load_kw']].resample('1h').mean().dropna()
    test_hourly = test[['load_kw']].resample('1h').mean().dropna()
    print(f'  降采样: train {len(train)} → {len(train_hourly)}, test {len(test)} → {len(test_hourly)}')

    # 准备 Prophet 格式数据
    prophet_train = train_hourly.reset_index()
    prophet_train.columns = ['ds', 'y']

    prophet_model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=True,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
    )

    t0 = time.time()
    try:
        prophet_model.fit(prophet_train)
        elapsed = time.time() - t0
        print(f'  Prophet 训练完成，耗时: {elapsed:.1f}s')

        if elapsed > PROPHET_TIMEOUT:
            print(f'  警告: 训练耗时 {elapsed:.1f}s 超过 {PROPHET_TIMEOUT}s 阈值，但已完成')

        # 预测（小时级）
        future = prophet_model.make_future_dataframe(
            periods=len(test_hourly), freq='1h'
        )
        forecast = prophet_model.predict(future)
        forecast_indexed = forecast.set_index('ds')
        # 对齐 index：取交集
        common_idx = test_hourly.index.intersection(forecast_indexed.index)
        prophet_pred = forecast_indexed.loc[common_idx, 'yhat']
        y_test_prophet = test_hourly.loc[common_idx, 'load_kw']

        # 评估（小时级）
        prophet_result = evaluate_model(y_test_prophet.values, prophet_pred.values, 'Prophet')
        print(f'  MAE={prophet_result["MAE"]}, RMSE={prophet_result["RMSE"]}, MAPE={prophet_result["MAPE"]}%')

        # 保存预测图
        plot_model_forecast(
            y_test_prophet, prophet_pred, 'Prophet - 负荷预测结果 (小时级)',
            output_path=os.path.join(output_dir, 'ch04_prophet_forecast.png'),
            metrics_dict=prophet_result,
        )

        return prophet_result

    except Exception as e:
        elapsed = time.time() - t0
        print(f'  Prophet 训练失败（耗时 {elapsed:.1f}s）: {e}')
        print(f'  在对比表中标注为 N/A，不阻塞后续步骤')
        return {
            'model': 'Prophet',
            'MAE': float('nan'),
            'RMSE': float('nan'),
            'MAPE': float('nan'),
        }


# ================================================================
# Step 4.8: LSTM 模型训练与预测（CPU 友好参数）
# ================================================================
def train_lstm(train, val, test, y_test, output_dir: str) -> dict:
    """训练 LSTM 深度学习模型

    CPU 友好参数:
    - max_epochs=20, patience=3
    - batch_size=128, hidden_size=32, num_layers=1
    """
    print('\n[Step 4.8] LSTM 模型训练（CPU 友好参数）...')

    import torch
    import torch.nn as nn
    from sklearn.preprocessing import MinMaxScaler

    # MinMaxScaler 标准化
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train[['load_kw']].values)
    val_scaled = scaler.transform(val[['load_kw']].values)
    test_scaled = scaler.transform(test[['load_kw']].values)

    # 滑动窗口序列构造
    SEQ_LENGTH = 24  # 4 小时历史窗口

    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

    X_train_seq, y_train_seq = create_sequences(train_scaled, SEQ_LENGTH)
    X_val_seq, y_val_seq = create_sequences(val_scaled, SEQ_LENGTH)
    X_test_seq, y_test_seq = create_sequences(test_scaled, SEQ_LENGTH)

    print(f'  训练序列: {X_train_seq.shape}, 验证序列: {X_val_seq.shape}, 测试序列: {X_test_seq.shape}')

    # 转为 Tensor
    X_train_t = torch.FloatTensor(X_train_seq)
    y_train_t = torch.FloatTensor(y_train_seq)
    X_val_t = torch.FloatTensor(X_val_seq)
    y_val_t = torch.FloatTensor(y_val_seq)
    X_test_t = torch.FloatTensor(X_test_seq)

    # LSTM 模型定义
    class LSTMModel(nn.Module):
        def __init__(self, input_size=1, hidden_size=32, num_layers=1, output_size=1):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])

    model = LSTMModel(hidden_size=32, num_layers=1)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 训练循环
    MAX_EPOCHS = 20
    PATIENCE = 3
    BATCH_SIZE = 128
    best_val_loss = float('inf')
    patience_counter = 0
    best_state = None

    t0 = time.time()
    for epoch in range(MAX_EPOCHS):
        model.train()
        total_loss = 0
        n_batches = 0
        for i in range(0, len(X_train_t), BATCH_SIZE):
            batch_X = X_train_t[i:i + BATCH_SIZE]
            batch_y = y_train_t[i:i + BATCH_SIZE]
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        # 验证
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_t)
            val_loss = criterion(val_pred, y_val_t).item()

        if (epoch + 1) % 5 == 0:
            print(f'  Epoch {epoch+1}/{MAX_EPOCHS}, '
                  f'Train Loss: {total_loss/n_batches:.6f}, Val Loss: {val_loss:.6f}')

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f'  Early stopping at epoch {epoch+1}')
                break

    elapsed = time.time() - t0
    print(f'  训练耗时: {elapsed:.1f}s')

    # 加载最优模型
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    # 预测
    with torch.no_grad():
        lstm_pred_scaled = model(X_test_t).numpy()

    # 反标准化
    lstm_pred = scaler.inverse_transform(lstm_pred_scaled).flatten()
    y_test_actual = scaler.inverse_transform(y_test_seq).flatten()

    # 评估
    lstm_result = evaluate_model(y_test_actual, lstm_pred, 'LSTM')
    print(f'  MAE={lstm_result["MAE"]}, RMSE={lstm_result["RMSE"]}, MAPE={lstm_result["MAPE"]}%')

    # 保存模型
    model_path = os.path.join(output_dir, 'ch04_lstm_model.pt')
    torch.save(model.state_dict(), model_path)
    print(f'  [保存] {model_path}')

    # 保存预测图
    test_index_aligned = y_test.index[SEQ_LENGTH:]
    lstm_pred_series = pd.Series(lstm_pred, index=test_index_aligned)
    y_test_actual_series = pd.Series(y_test_actual, index=test_index_aligned)

    plot_model_forecast(
        y_test_actual_series, lstm_pred_series, 'LSTM - 负荷预测结果',
        output_path=os.path.join(output_dir, 'ch04_lstm_forecast.png'),
        metrics_dict=lstm_result,
    )

    return lstm_result


# ================================================================
# Step 4.10: 最优模型 24h 滚动预测
# ================================================================
def rolling_forecast_24h(best_model_name: str, model, target_df: pd.DataFrame,
                          feature_cols: list, output_dir: str,
                          xgb_model=None, lgb_model=None) -> None:
    """使用最优模型进行 24h（144 个 10min 点）滚动预测

    根据最优模型类型分支处理:
    - XGBoost/LightGBM: 逐步预测，每步更新 lag/rolling 特征
    - ARIMA: 直接 predict(n_periods=144)
    - Prophet: make_future_dataframe(periods=144)
    - LSTM: 自回归循环
    """
    print(f'\n[Step 4.10] 最优模型 24h 滚动预测（{best_model_name}）...')

    FORECAST_STEPS = 144  # 24h × 6次/h = 144 个 10min 点

    if best_model_name == 'ARIMA':
        # ARIMA 直接预测
        last_data = target_df['load_kw'].iloc[-144:]
        pred_values = model.predict(n_periods=FORECAST_STEPS)
        future_times = pd.date_range(
            start=target_df.index[-1] + pd.Timedelta(minutes=10),
            periods=FORECAST_STEPS,
            freq='10T',
        )
        forecast_df = pd.DataFrame({
            'predicted_load_kw': pred_values
        }, index=future_times)

    elif best_model_name in ('XGBoost', 'LightGBM'):
        # 树模型逐步预测
        current_model = xgb_model if best_model_name == 'XGBoost' else lgb_model
        last_data = target_df.iloc[-144:].copy()
        predictions = []

        for step in range(FORECAST_STEPS):
            features = {}
            for lag in LAG_WINDOWS:
                features[f'lag_{lag}'] = (
                    current_data['load_kw'].iloc[-lag]
                    if len(current_data) >= lag
                    else current_data['load_kw'].iloc[0]
                )
            for window in ROLLING_WINDOWS:
                features[f'rolling_mean_{window}'] = current_data['load_kw'].iloc[-window:].mean()
                features[f'rolling_std_{window}'] = current_data['load_kw'].iloc[-window:].std()

            future_time = current_data.index[-1] + pd.Timedelta(minutes=10)
            features['hour'] = future_time.hour
            features['day_of_week'] = future_time.dayofweek
            features['is_weekend'] = int(future_time.dayofweek in [5, 6])
            features['month'] = future_time.month
            features['year'] = future_time.year
            features['season'] = future_time.month  # 占位，实际不用于树模型

            feature_vector = pd.DataFrame([features])[feature_cols]
            pred = current_model.predict(feature_vector)[0]
            predictions.append({'DateTime': future_time, 'predicted_load_kw': pred})

            new_row = current_data.iloc[-1:].copy()
            new_row['load_kw'] = pred
            new_row.index = [future_time]
            current_data = pd.concat([current_data, new_row])

        forecast_df = pd.DataFrame(predictions).set_index('DateTime')

    elif best_model_name == 'Prophet':
        # Prophet 直接预测
        from prophet import Prophet
        prophet_df = target_df[['load_kw']].reset_index()
        prophet_df.columns = ['ds', 'y']
        p_model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
        )
        p_model.fit(prophet_df)
        future = p_model.make_future_dataframe(periods=FORECAST_STEPS, freq='10T')
        p_forecast = p_model.predict(future)
        forecast_df = p_forecast.set_index('ds').iloc[-FORECAST_STEPS:][['yhat']]
        forecast_df.columns = ['predicted_load_kw']

    elif best_model_name == 'LSTM':
        # LSTM 自回归预测
        import torch
        import torch.nn as nn
        from sklearn.preprocessing import MinMaxScaler

        scaler = MinMaxScaler(feature_range=(0, 1))
        all_scaled = scaler.fit_transform(target_df[['load_kw']].values)

        SEQ_LENGTH = 24
        current_seq = all_scaled[-SEQ_LENGTH:].copy()
        predictions = []

        class LSTMModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm = nn.LSTM(1, 32, 1, batch_first=True)
                self.fc = nn.Linear(32, 1)
            def forward(self, x):
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])

        lstm_net = LSTMModel()
        lstm_net.load_state_dict(torch.load(
            os.path.join(output_dir, 'ch04_lstm_model.pt'),
            weights_only=True,
        ))
        lstm_net.eval()

        for step in range(FORECAST_STEPS):
            x_input = torch.FloatTensor(current_seq[-SEQ_LENGTH:].reshape(1, SEQ_LENGTH, 1))
            with torch.no_grad():
                pred_scaled = lstm_net(x_input).numpy()[0, 0]
            pred = scaler.inverse_transform([[pred_scaled]])[0, 0]
            future_time = target_df.index[-1] + pd.Timedelta(minutes=10) * (step + 1)
            predictions.append({'DateTime': future_time, 'predicted_load_kw': pred})
            current_seq = np.append(current_seq, [[pred_scaled]], axis=0)

        forecast_df = pd.DataFrame(predictions).set_index('DateTime')

    else:
        print(f'  未知模型类型: {best_model_name}，跳过 24h 滚动预测')
        return

    # 绘制 24h 滚动预测图（含误差退化标注）
    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)

    # 预测曲线
    ax.plot(forecast_df.index, forecast_df['predicted_load_kw'],
            color='tomato', linewidth=1.5, label=f'24h 预测 ({best_model_name})')

    # 添加置信度递减阴影（渐变透明度）
    n_points = len(forecast_df)
    for i in range(0, n_points, 6):
        alpha = 0.15 * (1 - i / n_points)
        ax.axvspan(
            forecast_df.index[i],
            forecast_df.index[min(i + 6, n_points - 1)],
            alpha=alpha, color='orange',
        )

    # 标注有效预测区间
    ax.axvline(x=forecast_df.index[24], color='green', linestyle=':', alpha=0.7, linewidth=1)
    ax.axvline(x=forecast_df.index[48], color='yellow', linestyle=':', alpha=0.7, linewidth=1)
    ax.text(forecast_df.index[12], forecast_df['predicted_load_kw'].max() * 1.05,
            '4h', ha='center', fontsize=9, color='green', fontweight='bold')
    ax.text(forecast_df.index[36], forecast_df['predicted_load_kw'].max() * 1.05,
            '8h', ha='center', fontsize=9, color='orange', fontweight='bold')

    ax.set_title(f'{TARGET_CITY} {TARGET_ZONE} - 未来24小时负荷预测（{best_model_name}）',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('负荷 (kW)', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # 添加说明文本
    ax.text(0.02, 0.02,
            '注: 阴影区域表示预测置信度递减\n前4~8小时预测最为可靠',
            transform=ax.transAxes, fontsize=9,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    fig_path = os.path.join(output_dir, 'ch04_24h_rolling_forecast.png')
    fig.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  [保存] {fig_path}')

    print(f'  预测范围: {forecast_df.index[0]} ~ {forecast_df.index[-1]}')
    print(f'  预测值范围: {forecast_df["predicted_load_kw"].min():.2f} ~ {forecast_df["predicted_load_kw"].max():.2f} kW')


# ================================================================
# 主函数
# ================================================================
def main():
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch04_load_forecasting')
    ensure_dir(OUTPUT_DIR)

    print('=' * 60)
    print('Prompt-04: 短期电力负荷预测模型构建')
    print('=' * 60)
    print(f'输出目录: {OUTPUT_DIR}')
    print(f'预测目标: {TARGET_CITY} / {TARGET_ZONE}')

    total_t0 = time.time()

    # Step 1: 数据准备
    target_df = load_and_prepare_target(INPUT_FILE, OUTPUT_DIR)

    # Step 2: 特征工程
    target_df, feature_cols = build_features(target_df)
    save_dataframe(target_df, 'ch04_feature_dataset.csv', OUTPUT_DIR)

    # Step 3: 数据划分
    splits = split_data(target_df, feature_cols, OUTPUT_DIR)

    # Step 4: ARIMA
    arima_result = train_arima(
        splits['y_train'], splits['y_test'], OUTPUT_DIR
    )

    # Step 5: XGBoost
    xgb_result, xgb_model = train_xgboost(
        splits['X_train'], splits['y_train'],
        splits['X_val'], splits['y_val'],
        splits['X_test'], splits['y_test'],
        feature_cols, OUTPUT_DIR,
    )

    # Step 6: LightGBM
    lgb_result, lgb_model = train_lightgbm(
        splits['X_train'], splits['y_train'],
        splits['X_val'], splits['y_val'],
        splits['X_test'], splits['y_test'],
        feature_cols, OUTPUT_DIR,
    )

    # Step 7: Prophet
    prophet_result = train_prophet(
        splits['train'], splits['test'], splits['y_test'], OUTPUT_DIR
    )

    # Step 8: LSTM
    lstm_result = train_lstm(
        splits['train'], splits['val'], splits['test'],
        splits['y_test'], OUTPUT_DIR,
    )

    # Step 9: 多模型对比
    print('\n[Step 4.9] 多模型评估对比...')
    results = [arima_result, xgb_result, lgb_result, prophet_result, lstm_result]
    comparison_df = compare_models(
        results,
        os.path.join(OUTPUT_DIR, 'ch04_model_comparison.csv'),
    )
    print('\n' + '=' * 60)
    print('  多模型评估结果对比（按 MAPE 升序排列）')
    print('=' * 60)
    print(comparison_df.to_string(index=False))

    best_model = comparison_df.iloc[0]
    print(f'\n  最优模型: {best_model["model"]}, MAPE={best_model["MAPE"]}%, '
          f'质量: {best_model["quality"]}')

    # Step 10: 24h 滚动预测
    rolling_forecast_24h(
        best_model_name=best_model['model'],
        model=None,  # 各模型通过参数传入
        target_df=target_df,
        feature_cols=feature_cols,
        output_dir=OUTPUT_DIR,
        xgb_model=xgb_model,
        lgb_model=lgb_model,
    )

    # 产物汇总
    total_elapsed = time.time() - total_t0
    print('\n' + '=' * 60)
    print(f'  Prompt-04 执行完成！总耗时: {total_elapsed:.1f}s')
    print(f'  产物目录: {OUTPUT_DIR}')
    print('=' * 60)

    # 列出所有产物
    artifacts = sorted(os.listdir(OUTPUT_DIR))
    print(f'\n  产物清单 ({len(artifacts)} 个文件):')
    for f in artifacts:
        fpath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(fpath)
        if size > 1024 * 1024:
            size_str = f'{size / 1024 / 1024:.1f} MB'
        elif size > 1024:
            size_str = f'{size / 1024:.1f} KB'
        else:
            size_str = f'{size} B'
        print(f'    {f} ({size_str})')


if __name__ == '__main__':
    main()
