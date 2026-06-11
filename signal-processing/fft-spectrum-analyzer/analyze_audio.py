"""
analyze_audio.py — 频谱分析与峰值标注演示

对合成的钢琴音色进行 FFT 频谱分析，检测峰值频率并标注乐理音名。

流程:
  1. 合成 C4 钢琴音色（基频 + 谐波 + 衰减包络）
  2. 分帧 → 取能量最大的一帧 → 加汉宁窗 → FFT
  3. 检测幅度谱中的峰值 → 映射到乐理音名
  4. 绘制频谱图，红点标注峰值 → 保存 spectrum.png
"""

from __future__ import annotations

import math
import os
import sys
import tempfile

import numpy as np
import soundfile as sf

# 确保可以从项目根目录导入各模块
sys.path.insert(0, os.path.dirname(__file__))

from audio_processor import (
    apply_window,
    compute_spectrum,
    find_peaks,
    freq_to_note_name,
    frame_signal,
    load_audio,
)
from fft_analysis.my_fft import fft

# ── 参数 ──
SAMPLE_RATE = 44100       # 采样率 (Hz)
DURATION = 2.0            # 信号时长 (秒)
FRAME_SIZE = 2048         # 帧长 — 更大的帧长 ≈ 更好的频率分辨率
HOP_LENGTH = 1024         # 帧移

# C4 = 261.63 Hz（基于 A4=440 Hz 的十二平均律）
C4_FREQ = 440.0 * 2.0 ** (-9.0 / 12.0)  # = 261.63 Hz
NUM_HARMONICS = 8  # 2 次 ~ 8 次谐波


def synthesize_piano_note(
    freq: float,
    duration: float = 2.0,
    sr: int = 44100,
) -> np.ndarray:
    """合成类似钢琴音色的信号。

    使用基频 + 谐波叠加 + 指数衰减包络来模拟钢琴音色：

        signal(t) = Σ A_k · sin(2π·k·f₀·t) · exp(-α·t)

    谐波振幅策略:
        - 偶次谐波 (k=2,4,6,8): A_k = 1/k
        - 奇次谐波 (k=3,5,7)  : A_k = 0.8/k

    参数:
        freq: 基频 (Hz)
        duration: 信号时长 (秒)
        sr: 采样率 (Hz)

    返回:
        一维 numpy 数组，归一化到 [-1, 1]
    """
    n_samples = int(sr * duration)
    t = np.arange(n_samples, dtype=np.float64) / sr

    # 基频
    signal = np.sin(2.0 * math.pi * freq * t)

    # 叠加谐波
    for k in range(2, NUM_HARMONICS + 1):
        if k % 2 == 0:
            amp = 1.0 / k  # 偶次谐波
        else:
            amp = 0.8 / k  # 奇次谐波
        signal += amp * np.sin(2.0 * math.pi * k * freq * t)

    # 指数衰减包络: 模拟钢琴的自然衰减
    envelope = np.exp(-t * 2.0)
    signal *= envelope

    # 归一化
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal /= max_val

    return signal


def _frequency_resolution(n: int, sr: int) -> float:
    """计算 FFT 频率分辨率 Δf = sr / N"""
    return sr / n


def main():
    print("=" * 65)
    print("  频谱分析与峰值标注演示")
    print("  信号: 合成钢琴 C4 (基频 261.63 Hz + 8 次谐波)")
    print("=" * 65)

    # ── 1. 合成信号 ──
    print(f"\n正在合成 C4 钢琴音色...")
    signal = synthesize_piano_note(C4_FREQ, DURATION, SAMPLE_RATE)
    print(f"  信号长度: {len(signal)} 样本 ({DURATION:.1f} 秒 @ {SAMPLE_RATE} Hz)")

    # ── 2. 保存临时文件 ──
    tmp_wav = os.path.join(tempfile.gettempdir(), "_analyze_temp.wav")
    sf.write(tmp_wav, signal, SAMPLE_RATE)

    # ── 3. 加载音频 ──
    data, sr = load_audio(tmp_wav)
    print(f"  加载采样率: {sr} Hz")

    # ── 4. 分帧 ──
    frames = frame_signal(data, FRAME_SIZE, HOP_LENGTH)
    num_frames = frames.shape[0]
    print(f"  分帧: {FRAME_SIZE} 点/帧, 帧移 {HOP_LENGTH} → {num_frames} 帧")

    # ── 5. 找到能量最大的一帧 ──
    frame_energies = np.sum(frames ** 2, axis=1)
    best_idx = int(np.argmax(frame_energies))
    best_frame = frames[best_idx]
    print(f"  能量最大帧: 第 {best_idx + 1}/{num_frames} 帧")

    # ── 6. 加窗 + FFT ──
    delta_f = _frequency_resolution(FRAME_SIZE, sr)
    print(f"  帧长 {FRAME_SIZE}, Δf = {sr}/{FRAME_SIZE} = {delta_f:.2f} Hz")

    windowed = apply_window(best_frame, 'hann')
    freqs, magnitude = compute_spectrum(windowed, fft, sr)

    # ── 7. 峰值检测 ──
    print(f"\n{'─' * 65}")
    print(f"  峰值检测 (threshold_ratio=0.3, 仅保留幅度 > 30% 最大值的峰)")
    print(f"{'─' * 65}")
    peaks = find_peaks(magnitude, freqs, threshold_ratio=0.3)

    if not peaks:
        print("  (未检测到峰值)")
    else:
        print(f"   {'频率 (Hz)':>12s} | {'幅度':>12s} | {'音名':>6s} |  说明")
        print(f"   {'-' * 10}-+-{'-' * 10}-+-{'-' * 6}-+--------")
        for i, (f, mag) in enumerate(peaks):
            note = freq_to_note_name(f)
            desc = ""
            if i == 0:
                desc = "← 主峰 (基频)"
            else:
                # 谐波编号 = round(f / 基频)
                harmonic_n = round(f / C4_FREQ)
                if harmonic_n > 1 and abs(f - harmonic_n * C4_FREQ) < delta_f * 2:
                    desc = f"← {harmonic_n}次谐波"
                else:
                    # 检查是否是其他谐波
                    desc = "← 峰值"
            print(f"   {f:>10.2f} | {mag:>10.2f} | {note:>6s} | {desc}")

    # ── 8. 绘制频谱图 ──
    print(f"\n正在绘制频谱图...")
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 6))

        # 限定显示范围: 0 ~ 4 kHz（钢琴前几个谐波足够）
        display_max_freq = 2000
        mask = freqs <= display_max_freq

        ax.plot(freqs[mask], magnitude[mask], 'b-', linewidth=0.8, label='Magnitude Spectrum')

        # 标注峰值
        if peaks:
            peak_freqs = np.array([p[0] for p in peaks])
            peak_mags = np.array([p[1] for p in peaks])
            # 只标注显示范围内的峰值
            display_mask = peak_freqs <= display_max_freq
            ax.scatter(
                peak_freqs[display_mask],
                peak_mags[display_mask],
                color='red', s=60, zorder=5, label=f'Peaks ({len(peaks)} detected)',
            )

            # 在峰值点上标注音名
            for f, mag in peaks:
                if f > display_max_freq:
                    break
                note = freq_to_note_name(f)
                ax.annotate(
                    note,
                    xy=(f, mag),
                    xytext=(5, 10),
                    textcoords='offset points',
                    fontsize=9,
                    color='red',
                    fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='red', lw=0.8),
                )

        ax.set_xlabel('Frequency (Hz)', fontsize=12)
        ax.set_ylabel('Magnitude', fontsize=12)
        ax.set_title(
            f'Spectrum — Synthesized Piano C4 ({C4_FREQ:.2f} Hz)\n'
            f'Frame size={FRAME_SIZE}, Δf={delta_f:.2f} Hz, Window=Hann',
            fontsize=13,
        )
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, display_max_freq)

        # 标注基频和谐波的理论位置
        for k in range(1, NUM_HARMONICS + 1):
            harmonic_freq = k * C4_FREQ
            if harmonic_freq > display_max_freq:
                break
            ax.axvline(harmonic_freq, color='gray', linestyle=':', alpha=0.5, linewidth=0.5)

        plt.tight_layout()
        output_path = os.path.join(os.path.dirname(__file__), 'spectrum.png')
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"  ✅ 频谱图已保存: {output_path}")

    except ImportError:
        print("  ⚠️ matplotlib 未安装，跳过绘图")
    except Exception as e:
        print(f"  ⚠️ 绘图出错: {e}")

    # ── 9. 清理 ──
    try:
        os.remove(tmp_wav)
    except OSError:
        pass

    # ── 10. 总结 ──
    print(f"\n{'=' * 65}")
    print(f"  分析总结")
    print(f"{'=' * 65}")
    print(f"  信号: 合成钢琴 C4 ({C4_FREQ:.2f} Hz)")
    print(f"  谐波: 2 ~ {NUM_HARMONICS} 次 (共 {NUM_HARMONICS - 1} 个谐波)")
    print(f"  帧长: {FRAME_SIZE} 点, 频率分辨率: {delta_f:.2f} Hz")
    print(f"  检测到峰值: {len(peaks)} 个")
    if peaks:
        freqs_only = [p[0] for p in peaks]
        print(f"  主峰: {peaks[0][0]:.2f} Hz → {freq_to_note_name(peaks[0][0])}")
        print(f"  峰值频率列表:")
        for f, _ in peaks:
            note = freq_to_note_name(f)
            print(f"    {f:>8.2f} Hz → {note}")
    print(f"{'=' * 65}")


if __name__ == '__main__':
    main()
