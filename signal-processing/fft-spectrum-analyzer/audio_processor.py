"""
audio_processor.py — 音频读取、分帧、加窗、频谱分析预处理工具

用于配合 my_fft.py 对音频信号进行 FFT 分析前的预处理。

函数:
    load_audio(file_path, sr=None)                    — 读取 WAV 文件
    frame_signal(signal, frame_size, hop_length)       — 分帧
    apply_window(frame, window_type='hann')            — 加窗
    compute_spectrum(frame, fft_func, fs)              — 计算幅度谱
    find_peaks(magnitude, freq, threshold_ratio=0.3)   — 找峰值频率
    freq_to_note_name(freq)                            — 频率转乐理音名
"""

from __future__ import annotations

import math
from typing import Callable, List, Tuple

import numpy as np
import soundfile as sf


# ─────────────────────────────────────────────────────────────────────
# 音频读取
# ─────────────────────────────────────────────────────────────────────

def load_audio(file_path: str, sr: int | None = None) -> Tuple[np.ndarray, int]:
    """读取 WAV 音频文件，返回 (信号数组, 采样率)。

    使用 soundfile 库读取，支持 WAV/FLAC/OGG 等格式。
    如果指定 sr 且与文件采样率不同，发出警告但不会隐式重采样
    （重采样需要额外依赖，留给调用方决定）。

    参数:
        file_path: 音频文件路径
        sr: 期望的采样率（可选）。若指定且与文件不符，打印警告。

    返回:
        (signal, sample_rate)
        - signal: 一维 numpy 数组 (float64)，已归一化到 [-1, 1]
        - sample_rate: 采样率 (int)

    异常:
        FileNotFoundError: 文件不存在
        ValueError: 非音频文件或读取失败
    """
    try:
        data, file_sr = sf.read(file_path, always_2d=False)
    except FileNotFoundError:
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    except Exception as e:
        raise ValueError(f"无法读取音频文件 '{file_path}': {e}")

    # 如果是多声道，取平均混音为单声道
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 确保数据类型为 float64
    data = np.asarray(data, dtype=np.float64)

    # 如果指定了目标采样率且不一致，发出警告
    if sr is not None and sr != file_sr:
        import warnings
        warnings.warn(
            f"文件采样率 ({file_sr} Hz) 与目标采样率 ({sr} Hz) 不一致。"
            f"返回原始采样率，请自行重采样。"
        )

    return data, file_sr


# ─────────────────────────────────────────────────────────────────────
# 分帧
# ─────────────────────────────────────────────────────────────────────

def frame_signal(
    signal: np.ndarray,
    frame_size: int,
    hop_length: int,
) -> np.ndarray:
    """将一维音频信号切分为多个帧（二维数组）。

    使用滑动窗口方式切分：
        frame[i] = signal[i * hop_length : i * hop_length + frame_size]

    尾部不足一帧的部分被丢弃（drop_last 策略）。

    参数:
        signal: 一维音频信号数组
        frame_size: 每帧的样本数（必须 > 0）
        hop_length: 帧移步长（必须 > 0）

    返回:
        二维数组，形状为 (num_frames, frame_size)

    异常:
        ValueError: frame_size 或 hop_length 不合法
    """
    if frame_size <= 0:
        raise ValueError(f"frame_size 必须为正数，传入 {frame_size}")
    if hop_length <= 0:
        raise ValueError(f"hop_length 必须为正数，传入 {hop_length}")

    n_samples = len(signal)

    # 计算可以完整切分的帧数
    if n_samples < frame_size:
        # 信号比一帧还短，返回空数组
        return np.empty((0, frame_size), dtype=signal.dtype)

    num_frames = (n_samples - frame_size) // hop_length + 1

    # 使用 stride_tricks 高效构建帧矩阵（无数据拷贝）
    # 这种方法的优势是 O(1) 内存开销，所有帧共享底层数据
    shape = (num_frames, frame_size)
    strides = (signal.strides[0] * hop_length, signal.strides[0])

    frames = np.lib.stride_tricks.as_strided(
        signal,
        shape=shape,
        strides=strides,
        writeable=False,
    )

    return frames.copy()  # 返回副本，避免共享底层数据的副作用


# ─────────────────────────────────────────────────────────────────────
# 加窗
# ─────────────────────────────────────────────────────────────────────

def _compute_window(frame_size: int, window_type: str) -> np.ndarray:
    """计算指定类型的窗口函数。

    支持三种窗口:
        - 'rect': 矩形窗（全1），相当于不加窗
        - 'hann': 汉宁窗 (Hann)，最常用的语音处理窗口
            w[n] = 0.5 * (1 - cos(2πn/(N-1)))
        - 'hamming': 汉明窗 (Hamming)
            w[n] = 0.54 - 0.46 * cos(2πn/(N-1))

    参数:
        frame_size: 窗口长度
        window_type: 窗口类型名

    返回:
        长度为 frame_size 的窗口系数数组

    异常:
        ValueError: 不支持的窗口类型
    """
    if window_type == 'rect':
        return np.ones(frame_size, dtype=np.float64)

    if window_type == 'hann':
        # 汉宁窗: w[n] = 0.5 * (1 - cos(2πn/(N-1)))
        n = np.arange(frame_size, dtype=np.float64)
        return 0.5 * (1.0 - np.cos(2.0 * math.pi * n / (frame_size - 1)))

    if window_type == 'hamming':
        # 汉明窗: w[n] = 0.54 - 0.46 * cos(2πn/(N-1))
        n = np.arange(frame_size, dtype=np.float64)
        return 0.54 - 0.46 * np.cos(2.0 * math.pi * n / (frame_size - 1))

    raise ValueError(
        f"不支持的窗口类型: '{window_type}'。"
        f"可选: 'rect', 'hann', 'hamming'"
    )


def apply_window(frame: np.ndarray, window_type: str = 'hann') -> np.ndarray:
    """对一帧信号施加窗口函数。

    窗口函数在时域上对帧进行逐点乘法，用于减少 FFT 中的频谱泄漏。
    不同的窗口在频率分辨率和幅度精度之间有不同权衡：
        - Hann:  主瓣宽度 2Δf，旁瓣衰减 -31dB，综合推荐
        - Hamming: 主瓣宽度 2Δf，旁瓣衰减 -41dB，近端旁瓣更小
        - Rect:  主瓣宽度 Δf，旁瓣衰减 -13dB，频率分辨率最高但泄漏最严重

    参数:
        frame: 一维帧信号数组
        window_type: 窗口类型，默认为 'hann'

    返回:
        加窗后的数组（副本），长度与输入相同

    异常:
        ValueError: 不支持的窗口类型或输入不是一维数组
    """
    if frame.ndim != 1:
        raise ValueError(f"输入必须是一维数组，传入 shape={frame.shape}")

    window = _compute_window(len(frame), window_type)
    return frame * window


# ─────────────────────────────────────────────────────────────────────
# 频谱计算
# ─────────────────────────────────────────────────────────────────────

def compute_spectrum(
    frame: np.ndarray,
    fft_func: Callable[[List[complex]], List[complex]],
    fs: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """对一帧信号计算幅度谱，返回正频率部分。

    参数:
        frame: 一维帧信号数组（加窗或未加窗均可）
        fft_func: FFT 函数，接受 list[complex] 返回 list[complex]
        fs: 采样率 (Hz)

    返回:
        (freq_bins, magnitude)
        - freq_bins: 正频率轴 (ndarray)，形状 (N//2,)
        - magnitude: 幅度谱 (ndarray)，形状 (N//2,)

    异常:
        ValueError: frame 不是一维数组
    """
    if frame.ndim != 1:
        raise ValueError(f"frame 必须是一维数组，传入 shape={frame.shape}")

    n = len(frame)
    # 执行 FFT
    spectrum = fft_func(frame.tolist())
    spectrum = np.asarray(spectrum, dtype=np.complex128)

    # 只取正频率部分（前 N//2 个点，含 DC 不含 Nyquist 的对称副本）
    half = n // 2
    magnitude = np.abs(spectrum[:half])

    # 构建频率轴: [0, fs/N, 2*fs/N, ..., (half-1)*fs/N]
    freq_bins = np.arange(half, dtype=np.float64) * fs / n

    return freq_bins, magnitude


def find_peaks(
    magnitude: np.ndarray,
    freq: np.ndarray,
    threshold_ratio: float = 0.3,
) -> list[tuple[float, float]]:
    """在幅度谱中检测峰值（局部极大值）。

    检测条件:
        1. magnitude[i] > magnitude[i-1] AND magnitude[i] > magnitude[i+1]
        2. magnitude[i] > max(magnitude) * threshold_ratio

    参数:
        magnitude: 幅度谱数组
        freq: 频率轴数组（与 magnitude 等长）
        threshold_ratio: 幅度阈值比例（相对最大幅度），默认 0.3

    返回:
        按幅度降序排列的 [(频率, 幅度), ...]
    """
    if len(magnitude) < 3:
        return []

    max_mag = np.max(magnitude)
    if max_mag == 0.0:
        return []

    threshold = max_mag * threshold_ratio
    peaks: list[tuple[float, float]] = []

    # 遍历内部点（跳过端点，端点不能是局部极大值）
    for i in range(1, len(magnitude) - 1):
        if magnitude[i] > magnitude[i - 1] and magnitude[i] > magnitude[i + 1]:
            if magnitude[i] > threshold:
                peaks.append((float(freq[i]), float(magnitude[i])))

    # 按幅度降序排列
    peaks.sort(key=lambda p: p[1], reverse=True)
    return peaks


# ─────────────────────────────────────────────────────────────────────
# 乐理音名映射
# ─────────────────────────────────────────────────────────────────────

# 十二平均律音名表
_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
_A4_FREQ = 440.0
_A4_MIDI = 69  # MIDI note number for A4


def freq_to_note_name(freq: float) -> str:
    """将频率转换为最近的乐理音名（如 261.63 → "C4"）。

    基于十二平均律（equal temperament）:
        semitone = 69 + 12 * log2(freq / 440)

    参数:
        freq: 频率 (Hz)

    返回:
        音名字符串，如 "C4", "A#5", "G3"。超出 MIDI 范围 [0,127]
        时返回 f"{freq:.1f} Hz"。
    """
    if freq <= 0:
        return f"{freq:.1f} Hz"

    # 计算 MIDI 半音编号（浮点）
    semitone_float = _A4_MIDI + 12.0 * math.log2(freq / _A4_FREQ)
    semitone = round(semitone_float)

    # 检查 MIDI 范围
    if semitone < 0 or semitone > 127:
        return f"{freq:.1f} Hz"

    note = _NOTE_NAMES[semitone % 12]
    octave = semitone // 12 - 1
    return f"{note}{octave}"
