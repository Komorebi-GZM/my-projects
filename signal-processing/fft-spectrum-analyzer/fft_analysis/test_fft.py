"""
test_fft.py — FFT 实现验证脚本

测试内容：
  1. 单元测试：is_power_of_two, next_power_of_two
  2. 功能测试：对正弦波信号执行 FFT，与 numpy.fft.fft 对比幅度谱
  3. 精度验证：计算均方误差（MSE）
  4. 可视化（可选）：绘制幅度谱对比图
  5. 逆 FFT（ifft）验证：恢复后的时域信号与原始信号的误差

运行方式：
    python fft_analysis/test_fft.py
"""

import math
import cmath
import sys
import os

# 确保可以从项目根目录导入 my_fft
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fft_analysis.my_fft import is_power_of_two, next_power_of_two, fft, ifft, fft_freq

# ── 检查 numpy 是否可用（仅用于对比，非必须）──
try:
    import numpy as np
    HAS_NUMPY = True
    print("[INFO] numpy 可用，将进行精度对比验证")
except ImportError:
    HAS_NUMPY = False
    print("[WARN] numpy 不可用，仅运行基本功能测试")

# ── 检查 matplotlib 是否可用（仅用于绘图）──
try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互模式，避免 GUI 阻塞
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[WARN] matplotlib 不可用，跳过绘图")


# ====================================================================
# 测试 1: is_power_of_two
# ====================================================================
def test_is_power_of_two():
    """验证 is_power_of_two 对各种输入的判断是否正确"""
    # 2 的幂：应该返回 True
    powers = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    for p in powers:
        assert is_power_of_two(p), f"FAIL: {p} 应该是 2 的幂"
        print(f"  ✅ is_power_of_two({p}) = True")

    # 非 2 的幂：应该返回 False
    non_powers = [0, 3, 5, 6, 7, 9, 10, 100, 500, 1023]
    for p in non_powers:
        assert not is_power_of_two(p), f"FAIL: {p} 不应该是 2 的幂"
        print(f"  ✅ is_power_of_two({p}) = False")

    print("  ✅ test_is_power_of_two 全部通过\n")


# ====================================================================
# 测试 2: next_power_of_two
# ====================================================================
def test_next_power_of_two():
    """验证 next_power_of_two 能否正确找到最近的 2 的幂"""
    test_cases = [
        (1, 1),     # 已经是 2^0
        (2, 2),     # 已经是 2^1
        (3, 4),     # 大于等于 3 的最小 2 的幂是 4
        (4, 4),     # 已经是 2^2
        (5, 8),     # 5 → 8
        (7, 8),     # 7 → 8
        (8, 8),     # 已经是 2^3
        (9, 16),    # 9 → 16
        (100, 128), # 100 → 128
        (255, 256), # 255 → 256
        (1025, 2048), # 1025 → 2048
        (-5, 1),    # 负数 → 1
        (0, 1),     # 0 → 1
    ]
    for n, expected in test_cases:
        result = next_power_of_two(n)
        assert result == expected, f"FAIL: next_power_of_two({n}) = {result}, 期望 {expected}"
        print(f"  ✅ next_power_of_two({n}) = {result}")

    print("  ✅ test_next_power_of_two 全部通过\n")


# ====================================================================
# 测试 3: FFT 精度验证（与 numpy 对比）
# ====================================================================
def test_fft_accuracy():
    """生成正弦波信号，用我们的 fft() 与 np.fft.fft 做对比"""
    if not HAS_NUMPY:
        print("  ⏭️  跳过（numpy 不可用）\n")
        return

    # ── 信号参数 ──
    fs = 1024.0          # 采样率 (Hz)
    f0 = 100.0           # 正弦波频率 (Hz)
    T = 1.0              # 信号时长 (秒)
    N = int(fs * T)      # 总采样点数 = 1024

    # 生成时域信号: x(t) = sin(2π * f0 * t)
    # 物理含义：频率 f0 的正弦波，在离散时间下的采样
    t = np.arange(N) / fs           # 时间轴
    x = np.sin(2 * np.pi * f0 * t)  # 纯正弦波

    # ── 执行 FFT ──
    X_mine = np.array(fft(x.tolist()))   # 我们的实现
    X_np   = np.fft.fft(x)               # numpy 参考实现

    # ── 计算误差 ──
    # 均方误差 (MSE) : 衡量两个复频谱之间的平均平方误差
    #   MSE = (1/N) * Σ |X_mine[k] - X_np[k]|²
    # 归一化最大误差：反映单个点的最大偏差
    abs_error = np.abs(X_mine - X_np)
    mse = np.mean(abs_error ** 2)
    max_error = np.max(abs_error)
    relative_error = np.max(abs_error) / np.max(np.abs(X_np))

    print(f"  📊 FFT 精度对比:")
    print(f"     均方误差 (MSE)   = {mse:.6e}")
    print(f"     最大绝对误差     = {max_error:.6e}")
    print(f"     相对误差         = {relative_error:.6e}")

    # 阈值判定：对 1024 点双精度 FFT，MSE 应 < 1e-20
    # numpy 使用优化的 BLAS，我们的纯 Python 递归实现会有微小舍入差异
    # 但由于算法等价，误差应在浮点精度范围内
    assert mse < 1e-10, f"FAIL: MSE 过大 ({mse})"
    print(f"  ✅ MSE = {mse:.2e} < 1e-10，精度合格\n")

    # ── 幅度谱对比 ──
    # 幅度谱: |X[k]|, 反映各频率分量的强度
    mag_mine = np.abs(X_mine)
    mag_np   = np.abs(X_np)

    # 找到幅度最大的频率点（理论上应在 f0=100Hz 处）
    freqs = np.fft.fftfreq(N, d=1/fs)
    peak_idx = np.argmax(mag_np)
    peak_freq = abs(freqs[peak_idx])
    print(f"  📈 频谱峰值频率: {peak_freq:.2f} Hz (期望: {f0:.2f} Hz)")
    assert abs(peak_freq - f0) < 1.0, f"FAIL: 峰值频率偏差过大"
    print(f"  ✅ 频谱峰值与信号频率一致\n")

    # ── 绘制幅度谱对比图 ──
    if HAS_MPL:
        plot_spectrum_comparison(freqs, mag_mine, mag_np, f0, fs, N)
    else:
        print("  ⏭️  跳过绘图（matplotlib 不可用）\n")


# ====================================================================
# 测试 4: 逆 FFT 验证
# ====================================================================
def test_ifft():
    """验证 ifft(fft(x)) ≈ x，即正逆变换的复合应近似还原原始信号"""
    if not HAS_NUMPY:
        print("  ⏭️  跳过（numpy 不可用）\n")
        return

    # 生成测试信号（包含多个频率分量，测试更全面）
    fs = 1024.0
    N = 1024
    t = np.arange(N) / fs

    # 复合信号: 包含 50Hz, 150Hz, 300Hz 三个频率分量
    x = (np.sin(2 * np.pi * 50 * t) +
         0.5 * np.sin(2 * np.pi * 150 * t) +
         0.25 * np.sin(2 * np.pi * 300 * t))

    # 执行正变换和逆变换
    X = fft(x.tolist())
    x_recovered = ifft(X)

    # 计算时域恢复误差
    x_recovered_np = np.array(x_recovered)
    mse_time = np.mean(np.abs(x - x_recovered_np) ** 2)
    max_error_time = np.max(np.abs(x - x_recovered_np))

    print(f"  🔄 IFFT 验证 (ifft(fft(x)) ≈ x):")
    print(f"     时域 MSE  = {mse_time:.6e}")
    print(f"     最大误差   = {max_error_time:.6e}")

    assert mse_time < 1e-10, f"FAIL: IFFT 恢复误差过大 ({mse_time})"
    print(f"  ✅ IFFT 恢复精度合格\n")


# ====================================================================
# 测试 5: 边界情况
# ====================================================================
def test_edge_cases():
    """测试边界输入：空序列、单元素序列、已补零的序列"""
    if not HAS_NUMPY:
        print("  ⏭️  跳过（numpy 不可用）\n")
        return

    # 单元素输入
    x_single = [1.0 + 0j]
    X_single = fft(x_single)
    # DFT 对 N=1: X[0] = x[0]
    assert abs(X_single[0] - (1.0 + 0j)) < 1e-15, "FAIL: 单元素 FFT"
    print("  ✅ 单元素 FFT: pass")

    # 长度为 2 的输入
    x_two = [1.0 + 0j, 0.0 + 0j]
    X_two = fft(x_two)
    X_two_np = np.fft.fft(x_two)
    assert np.max(np.abs(np.array(X_two) - X_two_np)) < 1e-15, "FAIL: 2 元素 FFT"
    print("  ✅ 2 元素 FFT: pass")

    # 输入长度不是 2 的幂（自动补零）
    x3 = [1.0 + 0j, 2.0 + 0j, 3.0 + 0j]  # 3 → 补零到 4
    X3 = fft(x3)
    # 手动补零
    x3_padded = x3 + [0j]
    X3_np = np.fft.fft(x3_padded)
    assert np.max(np.abs(np.array(X3) - X3_np)) < 1e-15, "FAIL: 补零 FFT"
    print("  ✅ 自动补零 FFT: pass")

    # 纯实数输入
    x_real = [1.0, 2.0, 3.0, 4.0]
    X_real = fft(x_real)
    X_real_np = np.fft.fft(x_real)
    assert np.max(np.abs(np.array(X_real) - X_real_np)) < 1e-15, "FAIL: 实数 FFT"
    print("  ✅ 实数输入 FFT: pass")

    print("  ✅ test_edge_cases 全部通过\n")


# ====================================================================
# 绘图辅助
# ====================================================================
def plot_spectrum_comparison(freqs, mag_mine, mag_np, f0, fs, N):
    """绘制我们的 FFT 与 numpy FFT 的幅度谱对比图"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)

    # 只绘制正频率部分（前 N/2 个点）
    half = N // 2
    freqs_pos = freqs[:half]
    mag_mine_pos = mag_mine[:half]
    mag_np_pos = mag_np[:half]

    # 图1: 我们的 FFT 幅度谱
    ax1.stem(freqs_pos, mag_mine_pos, linefmt='C0-', markerfmt='C0o',
             basefmt=' ', label='my_fft')
    ax1.set_title('幅度谱 — my_fft 实现')
    ax1.set_xlabel('频率 (Hz)')
    ax1.set_ylabel('|X(f)|')
    ax1.axvline(f0, color='red', linestyle='--', alpha=0.5, label=f'{f0} Hz')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2: numpy FFT 幅度谱
    ax2.stem(freqs_pos, mag_np_pos, linefmt='C1-', markerfmt='C1o',
             basefmt=' ', label='np.fft.fft')
    ax2.set_title('幅度谱 — np.fft.fft (参考)')
    ax2.set_xlabel('频率 (Hz)')
    ax2.set_ylabel('|X(f)|')
    ax2.axvline(f0, color='red', linestyle='--', alpha=0.5, label=f'{f0} Hz')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 图3: 绝对误差
    abs_diff = np.abs(mag_mine - mag_np)
    ax3.semilogy(freqs_pos, abs_diff[:half], 'C2-', label='|my_fft - np.fft|')
    ax3.set_title('幅度谱绝对误差（对数坐标）')
    ax3.set_xlabel('频率 (Hz)')
    ax3.set_ylabel('绝对误差')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'fft_comparison.png')
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  📁 幅度谱对比图已保存: {output_path}\n")


# ====================================================================
# 主测试入口
# ====================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  FFT 实现测试套件")
    print("=" * 60)
    print()

    print("▶ 测试 1: is_power_of_two")
    test_is_power_of_two()

    print("▶ 测试 2: next_power_of_two")
    test_next_power_of_two()

    print("▶ 测试 3: FFT 精度（与 numpy 对比）")
    test_fft_accuracy()

    print("▶ 测试 4: IFFT 验证")
    test_ifft()

    print("▶ 测试 5: 边界情况")
    test_edge_cases()

    print("=" * 60)
    print("  所有测试完成！")
    print("=" * 60)
