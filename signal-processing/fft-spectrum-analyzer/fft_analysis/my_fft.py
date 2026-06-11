"""
my_fft.py — 手动实现基2 Cooley-Tukey 快速傅里叶变换（FFT）

算法说明：
  - 使用 时间抽取（Decimation-In-Time, DIT） 递归结构
  - 将长度为 N 的序列分解为偶数索引和奇数索引两个子序列
  - 对子序列递归执行 FFT，再通过 蝶形运算（butterfly） 合并结果
  - 旋转因子（twiddle factor）: W_N^k = exp(-2πi * k / N)

参考资料：
  - Cooley & Tukey (1965). "An algorithm for the machine calculation of
    complex Fourier series"
"""

import math
import cmath  # 复数数学函数


# ─────────────────────────────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────────────────────────────

def is_power_of_two(n: int) -> bool:
    """
    判断 n 是否为 2 的整数次幂。

    原理：2 的幂的二进制表示只有最高位为 1（如 8 = 0b1000），
    减 1 后变为全 1（如 7 = 0b0111）。两者按位与的结果为 0。
    例如: 8 & 7 = 0b1000 & 0b0111 = 0 ✅
          6 & 5 = 0b0110 & 0b0101 = 0b0100 = 4 ❌
    特殊处理 n <= 0 的情况（非正整数不可能是 2 的幂）。
    """
    return n > 0 and (n & (n - 1)) == 0


def next_power_of_two(n: int) -> int:
    """
    返回大于等于 n 的最小 2 的幂。

    实现思路：将 n 减 1 后从最高位向低位逐次填充 1，
    最后加 1 得到结果。这是位运算的经典技巧。
    例如 n=5: n-1=4 (0b100) → 0b111 → +1 → 8
    特殊处理 n <= 0 时直接返回 1（长度为 1 的序列总是 2 的幂）。
    """
    if n <= 0:
        return 1
    if is_power_of_two(n):
        return n
    # 将最高位以下所有位都置为 1，再加 1 进位
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n |= n >> 32  # 支持 64 位整数
    return n + 1


# ─────────────────────────────────────────────────────────────────────
# 核心 FFT 实现
# ─────────────────────────────────────────────────────────────────────

def fft(x):
    """
    使用 Cooley-Tukey 基2 时间抽取（DIT）算法计算 FFT。

    参数:
        x: 复数序列（list[complex] 或 numpy array，或可转换为 complex 的序列）

    返回:
        频域复数数组（list[complex]），长度为 2 的幂

    算法流程:
        1. 将输入补零至 2 的幂长度（zero-padding）
        2. 递归分解序列为偶数索引部分和奇数索引部分
        3. 在每层递归中通过蝶形运算合并子结果
        4. 返回完整频谱
    """
    # ── Step 1: 转为复数列表并补零至 2 的幂 ──
    # 确保输入为复数，避免后续运算类型错误
    x = [complex(val) for val in x]
    n = len(x)
    n_padded = next_power_of_two(n)

    # 补零：长度不足时在后补 0+0j
    if n_padded > n:
        x.extend([0j] * (n_padded - n))
    n = n_padded

    # ── Step 2: 递归基 ──
    # 长度为 1 的序列，其 DFT 就等于它本身（X[0] = x[0]）
    if n == 1:
        return x

    # ── Step 3: 分解（分治） ──
    # 将序列按索引奇偶性拆分为两个子序列：
    #   偶数索引: x[0], x[2], x[4], ...
    #   奇数索引: x[1], x[3], x[5], ...
    # 这种拆分利用了 DFT 中旋转因子的对称性质：
    #     W_N^{k+N/2} = -W_N^k
    # 使得合并时只需要一半的计算量。
    even = fft(x[0::2])   # 递归计算偶数部分的 FFT
    odd  = fft(x[1::2])   # 递归计算奇数部分的 FFT

    # ── Step 4: 合并（蝶形运算） ──
    # 对于每个 k = 0, 1, ..., N/2 - 1：
    #
    #   X[k]         = E[k] + W_N^k * O[k]
    #   X[k + N/2]   = E[k] - W_N^k * O[k]
    #
    # 其中 E[k] = even_k, O[k] = odd_k
    #
    # 图示（蝶形运算，k = N/2 的输出合并两个输入）：
    #
    #   even_k ──────┬── (+) ──── X[k]
    #                 │
    #               [×] W_N^k     ← 旋转因子
    #                 │
    #   odd_k  ───────┴── (-) ──── X[k + N/2]
    #
    # 旋转因子 W_N^k = exp(-j * 2π * k / N)
    #   - 在 DFT 中，频域点 X[k] 是时域信号与频率为 k/N 的复正弦的相关
    #   - 偶数部分对应 k 处的贡献，奇数部分需要额外旋转 k 个样本
    #   - W_N^k 就是这个"额外旋转"的相位补偿

    half_n = n // 2
    result = [0j] * n

    for k in range(half_n):
        # 计算旋转因子（twiddle factor）
        #  W_N^k = cos(2πk/N) - j * sin(2πk/N)
        # 物理含义：对应奇数子序列相对于偶数子序列在频域中的相位偏移
        angle = -2 * math.pi * k / n
        twiddle = complex(math.cos(angle), math.sin(angle))

        # 蝶形运算的核心两步：
        t = twiddle * odd[k]           # 旋转因子 × 奇数部分
        result[k]         = even[k] + t   # 上半输出
        result[k + half_n] = even[k] - t   # 下半输出（利用了 W_N^{k+N/2} = -W_N^k）

    return result


def ifft(y):
    """
    逆 FFT（Inverse FFT）。

    原理：IDFT 公式与 DFT 公式的关系：
          DFT:  X[k] = Σ x[n] · W_N^{nk}
          IDFT: x[n] = (1/N) · Σ X[k] · W_N^{-nk}

    利用共轭性质：IDFT 可以通过对输入取共轭后执行 FFT，
    再对结果取共轭并除以 N 来实现。

    参数:
        y: 频域复数序列

    返回:
        时域复数序列（list[complex]）
    """
    n = len(y)
    # Step 1: 对输入求共轭
    conjugated = [val.conjugate() for val in y]
    # Step 2: 对共轭结果执行 FFT
    #   FFT(conj(y)) 等价于对原序列做共轭后的正变换
    #   conj(FFT(conj(y))) 就得到了 IDFT 的 N 倍
    result = fft(conjugated)
    # Step 3: 再次共轭并除以 N
    result = [val.conjugate() / n for val in result]
    return result


# ─────────────────────────────────────────────────────────────────────
# 实用工具（可选，用于测试验证）
# ─────────────────────────────────────────────────────────────────────

def fft_freq(n: int, d: float = 1.0):
    """
    返回 FFT 结果的频率轴（类似 np.fft.fftfreq）。

    参数:
        n: FFT 点数
        d: 采样间隔（秒），默认 1.0

    返回:
        list[float], 长度为 n 的频率值（Hz）

    频率范围：
      正频率部分: [0, 1/(n*d), 2/(n*d), ..., (n/2-1)/(n*d)]
      Nyquist 频率: 1/(2*d)
      负频率部分: [-n/(2n*d), -(n/2-1)/(n*d), ..., -1/(n*d)]
    """
    result = [0.0] * n
    for i in range(n):
        if i <= (n - 1) // 2:
            result[i] = i / (n * d)
        else:
            result[i] = (i - n) / (n * d)
    return result
