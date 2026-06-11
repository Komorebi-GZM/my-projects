"""
main.py — 音频预处理 + FFT 演示

流程:
  1. 生成 440Hz 正弦波 → 保存 test.wav
  2. 读取 test.wav → 分帧 → 加汉宁窗
  3. 调用 my_fft.fft 计算第一帧的幅度谱
  4. 打印前 5 个峰值频率

关于频率分辨率:
  FFT 的频率分辨率 Δf = fs / N
  这里 fs=44100, N=1024 → Δf ≈ 43.07 Hz
  因此频率被离散化为若干个 "bin"（频点），只能测量 bin 中心频率。
  当信号频率正好落在 bin 中心时，出现单一干净峰值；
  当落在两个 bin 之间时，能量泄漏到相邻 bin（频谱泄漏）。
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import soundfile as sf

# 确保可以从项目根目录导入各模块
sys.path.insert(0, os.path.dirname(__file__))

from audio_processor import load_audio, frame_signal, apply_window
from fft_analysis.my_fft import fft, fft_freq

# ── 参数 ──
SAMPLE_RATE = 44100       # 采样率 (Hz)
DURATION = 3.0            # 信号时长 (秒)
FRAME_SIZE = 1024         # 帧长 (样本数)
HOP_LENGTH = 512          # 帧移

# FFT 频率分辨率: Δf = SAMPLE_RATE / FRAME_SIZE ≈ 43.07 Hz
# bin k 的中心频率 = k * Δf
# 我们选择两个频率来演示：
#   1. BIN_ALIGNED_FREQ — 正好落在 bin 10 中心 (10 × 43066/1024 ≈ 430.66)
#   2. MISALIGNED_FREQ — 落在两个 bin 之间 (440 Hz, 标准 A4)

BIN_ALIGNED_FREQ = 10 * SAMPLE_RATE / FRAME_SIZE  # = 430.664 Hz
MISALIGNED_FREQ = 440.0

OUTPUT_WAV = "test.wav"


def generate_test_tone(freq: float) -> np.ndarray:
    """生成指定频率的正弦波测试信号"""
    n_samples = int(SAMPLE_RATE * DURATION)
    t = np.arange(n_samples, dtype=np.float64) / SAMPLE_RATE
    signal = np.sin(2.0 * math.pi * freq * t)
    return signal


def find_top_peaks(
    magnitude: np.ndarray,
    freqs: np.ndarray,
    n_peaks: int = 5,
    min_freq: float = 1.0,
):
    """找到幅度谱中幅度最大的 n_peaks 个频率峰值。

    参数:
        magnitude: 幅度谱数组（正频率部分）
        freqs: 对应的频率轴
        n_peaks: 要返回的峰值数量
        min_freq: 忽略低于该频率的成分（过滤直流分量）

    返回:
        list[(频率, 幅度)], 按幅度从大到小排列
    """
    mask = freqs > min_freq
    mag_valid = magnitude[mask]
    freq_valid = freqs[mask]

    if len(mag_valid) == 0:
        return []

    # 取幅度最大的 n_peaks 个点
    peak_indices = np.argsort(mag_valid)[-n_peaks:][::-1]
    peaks = [(freq_valid[i], mag_valid[i]) for i in peak_indices]
    return peaks


def demonstrate_signal(label: str, freq: float, description: str):
    """对单个频率执行完整处理流程并打印结果"""
    print(f"\n{'─' * 60}")
    print(f"  ▶ {label}")
    print(f"  {description}")
    print(f"{'─' * 60}")

    # 生成
    signal = generate_test_tone(freq)

    # 写入 WAV
    sf.write(OUTPUT_WAV, signal, SAMPLE_RATE)

    # 读取
    data, sr = load_audio(OUTPUT_WAV)

    # 分帧
    frames = frame_signal(data, FRAME_SIZE, HOP_LENGTH)

    # 第一帧 + 汉宁窗
    windowed = apply_window(frames[0], 'hann')

    # FFT
    spectrum = fft(windowed.tolist())
    magnitude = np.abs(spectrum)

    bin_freqs = np.array(fft_freq(FRAME_SIZE, d=1.0 / sr))
    half = FRAME_SIZE // 2
    mag_pos = magnitude[:half]
    freq_pos = bin_freqs[:half]

    # 前 5 个峰值
    peaks = find_top_peaks(mag_pos, freq_pos, n_peaks=5)

    print(f"      帧长: {FRAME_SIZE},  采样率: {sr} Hz")
    print(f"      频率分辨率 Δf = {sr} / {FRAME_SIZE} = {sr/FRAME_SIZE:.2f} Hz")
    print(f"      期望频率: {freq:.2f} Hz")
    print()
    print(f"      前 {len(peaks)} 个峰值频率:")
    print(f"       {'频率 (Hz)':>12s} | {'幅度':>12s}  |  说明")
    print(f"       {'-' * 12}-+-{'-' * 12}-+--------")
    for i, (f, mag) in enumerate(peaks):
        note = ""
        if i == 0:
            note = "   ← 主峰"
            if abs(f - freq) < sr / FRAME_SIZE:
                bin_center = round(f / (sr / FRAME_SIZE))
                note += f" (bin {bin_center})"
        print(f"       {f:>12.2f} | {mag:>12.4f} |{note}")

    # 分析
    main_freq = peaks[0][0] if peaks else 0
    err = abs(main_freq - freq)
    delta_f = sr / FRAME_SIZE

    if err < delta_f * 0.1:
        # 频率对齐到 bin
        bin_idx = round(freq / delta_f)
        print(f"\n      ✅ 频率对齐: bin {bin_idx} = {bin_idx * delta_f:.2f} Hz")
        print(f"         主峰与期望偏差: {err:.4f} Hz (在浮点误差范围内)")
    else:
        # 频率落在两个 bin 之间
        lower_bin = int(freq / delta_f)
        upper_bin = lower_bin + 1
        print(f"\n      ℹ️ 频率未对齐 bin 中心")
        print(f"         {freq:.2f} Hz 落在 bin {lower_bin} ({lower_bin*delta_f:.2f} Hz)")
        print(f"         和 bin {upper_bin} ({upper_bin*delta_f:.2f} Hz) 之间")
        print(f"         能量按比例分配到两个 bin（频谱泄漏的正常现象）")
        print(f"         主峰偏差: {err:.2f} Hz")
        print(f"         可通过增大帧长或补零来提升分辨率")

    # 能量信息
    energy_before = np.sum(frames[0] ** 2)
    energy_after = np.sum(windowed ** 2)
    print(f"         帧能量 (加窗前): {energy_before:.2f}")
    print(f"         帧能量 (加窗后): {energy_after:.2f} ({energy_after/energy_before*100:.1f}%)")


def main():
    print("=" * 60)
    print("  音频预处理 + FFT 频谱分析演示")
    print("=" * 60)

    # —— 演示1: bin 对齐频率 ——
    demonstrate_signal(
        "演示 1: 频率对齐 FFT bin 中心",
        BIN_ALIGNED_FREQ,
        f"信号频率 = bin 10 = {BIN_ALIGNED_FREQ:.2f} Hz → 单一干净峰值",
    )

    # —— 演示2: 频率未对齐 ——
    demonstrate_signal(
        "演示 2: 频率未对齐 bin 中心",
        MISALIGNED_FREQ,
        f"信号频率 = {MISALIGNED_FREQ} Hz（标准 A4），落在两个 bin 之间 → 频谱泄漏",
    )

    # —— 总结 ——
    delta_f = SAMPLE_RATE / FRAME_SIZE
    print(f"\n{'=' * 60}")
    print(f"  总结")
    print(f"{'=' * 60}")
    print(f"  采样率:     {SAMPLE_RATE} Hz")
    print(f"  FFT 点数:   {FRAME_SIZE}")
    print(f"  频率分辨率: Δf = {delta_f:.2f} Hz")
    print(f"  帧移:       {HOP_LENGTH} 样本 ({HOP_LENGTH/SAMPLE_RATE*1000:.1f} ms)")
    print(f"  总帧数:     {int((SAMPLE_RATE*DURATION - FRAME_SIZE) / HOP_LENGTH) + 1}")
    print(f"\n  📝 关键结论:")
    print(f"     - FFT 将频率离散化为 N/2 个 bin，每个 bin 中心频率 = k·Δf")
    print(f"     - 信号频率与 bin 中心对齐 → 单一干净峰值")
    print(f"     - 信号频率落在两个 bin 之间 → 能量泄漏（频谱泄漏）")
    print(f"     - 加窗（Hann/Hamming）能减少泄漏，但会降低频率分辨率")
    print(f"     - 增大 FFT 点数 N 可提高分辨率：Δf = fs / N")
    print(f"{'=' * 60}")

    # 清理
    if os.path.exists(OUTPUT_WAV):
        os.remove(OUTPUT_WAV)


if __name__ == '__main__':
    main()
