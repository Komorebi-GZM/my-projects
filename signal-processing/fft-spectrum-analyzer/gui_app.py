"""
gui_app.py — 实时频谱分析仪（扩展版）

集成 5 个扩展功能：
  1. 频谱历史瀑布图     — 最近 10 帧的频谱堆叠显示
  2. 实时音高显示        — 主峰频率 → 乐理音名 (如 A4 440Hz)
  3. 录音保存与导出      — 录制 WAV + 导出频谱 CSV
  4. 多分辨率 FFT        — 长窗 (高频率分辨率) + 短窗 (高时间分辨率) 叠加显示
  5. 噪声抑制            — 背景噪声谱估计 + 频谱减法的显示与信号重建

数据流:
  麦克风 → sd.InputStream (回调线程)
    → CircularBuffer.write()          (无锁环形缓冲区)
    → QTimer @ 50ms (主线程)
      → CircularBuffer.read_last()
      → apply_window() + my_fft.fft()
      → 时域 / 频谱 / 瀑布图更新
      → 峰值检测 → 音高显示
      → 可选: 双 FFT / 噪声抑制
"""

from __future__ import annotations

import math
import os
import sys
import time
from datetime import datetime
from typing import Optional

import numpy as np

import sounddevice as sd
import soundfile as sf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QGroupBox,
    QSizePolicy,
    QCheckBox,
    QSlider,
)

# ── 项目模块 ──
sys.path.insert(0, os.path.dirname(__file__))
from audio_processor import apply_window, freq_to_note_name
from fft_analysis.my_fft import fft


# ── 常量 ──
SAMPLE_RATE = 16000              # 采样率 (Hz)
DEFAULT_FRAME_SIZE = 2048        # 默认 FFT 点数
SHORT_FFT_SIZE = 256             # 多分辨率 FFT 短窗点数 (Δf = 62.5 Hz)
TIME_WINDOW_SEC = 0.200          # 时域显示窗口 (秒)
BUFFER_SIZE = int(SAMPLE_RATE * TIME_WINDOW_SEC)  # 3200 samples
FFT_SIZE_OPTIONS = [1024, 2048]
WINDOW_OPTIONS = ['hann', 'rect', 'hamming']
WINDOW_LABELS = ['Hann', 'Rectangular', 'Hamming']
WATERFALL_FRAMES = 10            # 瀑布图保留的历史帧数


# ─────────────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────────────

def _ifft(x: list[complex]) -> np.ndarray:
    """用 my_fft.fft 实现 IFFT。

    原理: IDFT(X) = (1/N) · conj(DFT(conj(X)))
    因此用 fft 实现: ifft(X) = conj(fft(conj(X))) / N

    返回:
        numpy 数组 (复数)，取 .real 获得实数重建信号
    """
    n = len(x)
    conj_x = [complex(v.real, -v.imag) for v in x]
    fft_result = fft(conj_x)
    return np.array(
        [complex(v.real / n, -v.imag / n) for v in fft_result],
        dtype=np.complex128,
    )


# ─────────────────────────────────────────────────────────────────────
# 环形缓冲区 (无锁, 单生产者/单消费者)
# ─────────────────────────────────────────────────────────────────────

class CircularBuffer:
    """固定容量环形缓冲区，只保留最近的 N 个采样点。"""

    def __init__(self, capacity: int):
        self._buf = np.zeros(capacity, dtype=np.float64)
        self._cap = capacity
        self._pos = 0
        self._count = 0

    def write(self, data: np.ndarray):
        n = len(data)
        if n >= self._cap:
            self._buf[:] = data[-self._cap:]
            self._pos = 0
            self._count = self._cap
            return
        end = self._pos + n
        if end <= self._cap:
            self._buf[self._pos:end] = data
        else:
            first = self._cap - self._pos
            self._buf[self._pos:] = data[:first]
            self._buf[:n - first] = data[first:]
        self._pos = (self._pos + n) % self._cap
        self._count = min(self._count + n, self._cap)

    def read_last(self, n: int) -> np.ndarray:
        if n <= 0:
            return np.array([], dtype=np.float64)
        if n > self._cap:
            n = self._cap
        if self._count < n:
            out = np.zeros(n, dtype=np.float64)
            out[n - self._count:] = self._read_contiguous(self._count)
            return out
        return self._read_contiguous(n)

    def _read_contiguous(self, n: int) -> np.ndarray:
        start = (self._pos - n) % self._cap
        end = start + n
        if end <= self._cap:
            return self._buf[start:end].copy()
        first = self._cap - start
        out = np.empty(n, dtype=np.float64)
        out[:first] = self._buf[start:]
        out[first:] = self._buf[:n - first]
        return out

    @property
    def count(self) -> int:
        return self._count

    def read_newest_n(self, n: int) -> np.ndarray:
        """读取最近的 n 个样本 (read_last 的别名，接口兼容)。"""
        return self.read_last(n)


# ─────────────────────────────────────────────────────────────────────
# 主窗口
# ─────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """实时频谱分析仪主窗口（扩展版）。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-time Spectrum Analyzer")
        self.setMinimumSize(1200, 800)

        # ── 核心状态 ──
        self._running = False
        self._window_type: str = 'hann'
        self._fft_size: int = DEFAULT_FRAME_SIZE
        self._freq_log: bool = False
        self._stream: Optional[sd.InputStream] = None
        self._buffer = CircularBuffer(BUFFER_SIZE)
        self._frame_cache: Optional[np.ndarray] = None

        # ── 瀑布图 ──
        self._waterfall_buffer: Optional[np.ndarray] = None

        # ── 录音 ──
        self._recording = False
        self._recorded_chunks: list[np.ndarray] = []

        # ── 多分辨率 FFT ──
        self._dual_fft = False

        # ── 噪声抑制 ──
        self._noise_profile: Optional[np.ndarray] = None
        self._noise_suppression = False
        self._noise_alpha = 2.0
        # OLA (overlap-add) 重建缓存：保留上一帧后半段用于交叉淡化
        self._ola_prev: Optional[np.ndarray] = None

        # ── 定时器 (50ms ≈ 20 fps) ──
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._update_plots)

        self._setup_ui()

    # ─────────────────────────────────────────────────────────────────
    # UI 构建
    # ─────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ─── 左侧: matplotlib 画布 ───
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self._fig = Figure(figsize=(10, 6.5), dpi=100)
        self._fig.patch.set_facecolor('#fafafa')
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding,
        )

        # GridSpec 三等分，频谱略高
        gs = self._fig.add_gridspec(3, 1, height_ratios=[1, 1.5, 1])

        # ── 子图 1: 时域 ──
        self._ax_time = self._fig.add_subplot(gs[0])
        self._ax_time.set_facecolor('#f0f0f0')
        self._ax_time.set_xlim(0, TIME_WINDOW_SEC * 1000)
        self._ax_time.set_ylim(-1.2, 1.2)
        self._ax_time.set_ylabel("Amplitude")
        self._ax_time.set_title("Time Domain (last 200 ms)")
        self._ax_time.grid(True, alpha=0.3)

        t_ms = np.linspace(0, TIME_WINDOW_SEC * 1000, BUFFER_SIZE)
        (self._line_time,) = self._ax_time.plot(
            t_ms, np.zeros(BUFFER_SIZE), '#1f77b4', linewidth=0.8,
        )

        # ── 子图 2: 频谱 ──
        self._ax_freq = self._fig.add_subplot(gs[1])
        self._ax_freq.set_facecolor('#f0f0f0')
        self._ax_freq.set_xlim(0, SAMPLE_RATE / 2)
        self._ax_freq.set_xlabel("Frequency (Hz)")
        self._ax_freq.set_ylabel("Magnitude")
        self._ax_freq.set_title("Frequency Spectrum")
        self._ax_freq.grid(True, alpha=0.3)

        half = self._fft_size // 2
        self._freq_axis = (
            np.arange(half, dtype=np.float64) * SAMPLE_RATE / self._fft_size
        )

        # 主频谱线 (长窗)
        (self._line_freq,) = self._ax_freq.plot(
            self._freq_axis, np.zeros(half), '#d62728', linewidth=1.0,
            label=f'Long ({self._fft_size})',
        )
        # 短窗线 (多分辨率 FFT)
        (self._line_freq_short,) = self._ax_freq.plot(
            [], [], '#2ca02c', linewidth=1.0, linestyle='--', alpha=0.7,
            label=f'Short ({SHORT_FFT_SIZE})',
        )
        self._line_freq_short.set_visible(False)
        # 噪声抑制后频谱线
        (self._line_freq_clean,) = self._ax_freq.plot(
            [], [], '#9467bd', linewidth=1.5, alpha=0.85,
            label='Denoised',
        )
        self._line_freq_clean.set_visible(False)

        # 音高标注 (右上角)
        self._pitch_text = self._ax_freq.text(
            0.97, 0.95, '',
            transform=self._ax_freq.transAxes,
            ha='right', va='top', fontsize=15, fontweight='bold',
            color='#1a1a1a',
            bbox=dict(
                boxstyle='round,pad=0.35', facecolor='white',
                alpha=0.85, edgecolor='#cccccc',
            ),
        )

        # 占位文本
        self._placeholder = self._ax_freq.text(
            0.5, 0.5, "Click 'Start' to begin\nmicrophone capture",
            transform=self._ax_freq.transAxes,
            ha='center', va='center', fontsize=13,
            color='gray', fontweight='bold',
        )

        # ── 子图 3: 瀑布图 ──
        self._ax_waterfall = self._fig.add_subplot(gs[2])
        self._ax_waterfall.set_facecolor('#0a0a0a')
        self._ax_waterfall.set_ylabel('Frame (newest ↑)')
        self._ax_waterfall.set_xlabel('Frequency (Hz)')
        self._ax_waterfall.set_title(
            f'Spectrum History (Waterfall, last {WATERFALL_FRAMES} frames)',
        )
        self._ax_waterfall.set_xlim(0, SAMPLE_RATE / 2)
        self._ax_waterfall.set_ylim(0, WATERFALL_FRAMES)

        self._waterfall_buffer = np.zeros((WATERFALL_FRAMES, half))
        self._waterfall_img = self._ax_waterfall.imshow(
            self._waterfall_buffer,
            aspect='auto',
            cmap='inferno',
            extent=[0, SAMPLE_RATE / 2, 0, WATERFALL_FRAMES],
            interpolation='nearest',
            origin='lower',
        )

        self._fig.tight_layout(pad=2.0)
        canvas_layout.addWidget(self._canvas)

        # ─── 右侧: 控制面板 ───
        ctrl = QWidget()
        ctrl.setFixedWidth(220)
        ctrl_layout = QVBoxLayout(ctrl)
        ctrl_layout.setSpacing(8)

        # ── 开始/停止 ──
        self._btn_start = QPushButton("▶  Start")
        self._btn_start.setMinimumHeight(36)
        self._btn_start.setStyleSheet("font-size: 14px; font-weight: bold;")
        self._btn_start.clicked.connect(self._toggle_stream)
        ctrl_layout.addWidget(self._btn_start)

        # ── 窗函数 ──
        g = QGroupBox("Window Function")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._combo_window = QComboBox()
        self._combo_window.addItems(WINDOW_LABELS)
        self._combo_window.setCurrentIndex(0)
        self._combo_window.currentIndexChanged.connect(self._on_window_changed)
        gl.addWidget(self._combo_window)
        ctrl_layout.addWidget(g)

        # ── 频率刻度 ──
        g = QGroupBox("Frequency Scale")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._combo_freq = QComboBox()
        self._combo_freq.addItems(['Linear', 'Log (Hz)'])
        self._combo_freq.setCurrentIndex(0)
        self._combo_freq.currentIndexChanged.connect(self._on_freq_scale_changed)
        gl.addWidget(self._combo_freq)
        ctrl_layout.addWidget(g)

        # ── FFT 点数 ──
        g = QGroupBox("FFT Size")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._combo_fft = QComboBox()
        self._combo_fft.addItems([str(s) for s in FFT_SIZE_OPTIONS])
        self._combo_fft.setCurrentIndex(1)
        self._combo_fft.currentIndexChanged.connect(self._on_fft_size_changed)
        gl.addWidget(self._combo_fft)
        ctrl_layout.addWidget(g)

        # ── 多分辨率 FFT ──
        g = QGroupBox("Dual-Resolution FFT")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._cb_dual_fft = QCheckBox("Show Dual FFT")
        self._cb_dual_fft.stateChanged.connect(self._on_dual_fft_changed)
        gl.addWidget(self._cb_dual_fft)
        lbl = QLabel(
            f"Short window: {SHORT_FFT_SIZE} pt\n"
            f"(Δf = {SAMPLE_RATE/SHORT_FFT_SIZE:.1f} Hz)"
        )
        lbl.setStyleSheet("font-size: 10px; color: #666;")
        gl.addWidget(lbl)
        ctrl_layout.addWidget(g)

        # ── 噪声抑制 ──
        g = QGroupBox("Noise Suppression")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)

        self._btn_learn_noise = QPushButton("🎤 Learn Noise Profile")
        self._btn_learn_noise.clicked.connect(self._learn_noise_profile)
        gl.addWidget(self._btn_learn_noise)

        self._cb_noise_suppress = QCheckBox("Enable Suppression")
        self._cb_noise_suppress.setEnabled(False)
        self._cb_noise_suppress.stateChanged.connect(
            self._on_noise_suppress_changed,
        )
        gl.addWidget(self._cb_noise_suppress)

        row = QHBoxLayout()
        row.addWidget(QLabel("Amount:"))
        self._slider_alpha = QSlider(Qt.Horizontal)
        self._slider_alpha.setRange(10, 50)
        self._slider_alpha.setValue(20)
        self._slider_alpha.setTickPosition(QSlider.TicksBelow)
        self._slider_alpha.valueChanged.connect(self._on_alpha_changed)
        row.addWidget(self._slider_alpha)
        self._label_alpha_val = QLabel("2.0")
        self._label_alpha_val.setFixedWidth(30)
        row.addWidget(self._label_alpha_val)
        gl.addLayout(row)

        ctrl_layout.addWidget(g)

        # ── 录音与导出 ──
        g = QGroupBox("Recording & Export")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)

        self._btn_record = QPushButton("●  Record")
        self._btn_record.setStyleSheet("font-weight: bold;")
        self._btn_record.clicked.connect(self._toggle_recording)
        gl.addWidget(self._btn_record)

        self._btn_export_csv = QPushButton("📊 Export Spectrum CSV")
        self._btn_export_csv.clicked.connect(self._export_csv)
        gl.addWidget(self._btn_export_csv)

        ctrl_layout.addWidget(g)

        # ── 音高 ──
        g = QGroupBox("Pitch")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._label_pitch = QLabel("—")
        self._label_pitch.setAlignment(Qt.AlignCenter)
        self._label_pitch.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #d62728;"
        )
        gl.addWidget(self._label_pitch)
        self._label_pitch_freq = QLabel("— Hz")
        self._label_pitch_freq.setAlignment(Qt.AlignCenter)
        self._label_pitch_freq.setStyleSheet("font-size: 14px; color: #666;")
        gl.addWidget(self._label_pitch_freq)
        ctrl_layout.addWidget(g)

        # ── 状态 ──
        g = QGroupBox("Status")
        g.setStyleSheet("QGroupBox { font-weight: bold; }")
        gl = QVBoxLayout(g)
        self._label_status = QLabel("Idle")
        self._label_status.setWordWrap(True)
        self._label_status.setStyleSheet("font-size: 11px;")
        gl.addWidget(self._label_status)
        ctrl_layout.addWidget(g)

        ctrl_layout.addStretch()
        layout.addWidget(canvas_container, stretch=3)
        layout.addWidget(ctrl, stretch=1)

    # ─────────────────────────────────────────────────────────────────
    # 控件事件处理
    # ─────────────────────────────────────────────────────────────────

    def _on_window_changed(self, idx: int):
        self._window_type = WINDOW_OPTIONS[idx]

    def _on_freq_scale_changed(self, idx: int):
        self._freq_log = (idx == 1)
        self._rebuild_freq_ax()

    def _on_fft_size_changed(self, idx: int):
        self._fft_size = int(self._combo_fft.currentText())
        half = self._fft_size // 2
        self._freq_axis = (
            np.arange(half, dtype=np.float64) * SAMPLE_RATE / self._fft_size
        )
        self._rebuild_freq_ax()
        self._rebuild_waterfall()

    def _on_dual_fft_changed(self, state: int):
        self._dual_fft = (state == Qt.Checked)
        if not self._dual_fft:
            self._line_freq_short.set_visible(False)

    def _on_noise_suppress_changed(self, state: int):
        self._noise_suppression = (state == Qt.Checked)
        if not self._noise_suppression:
            self._line_freq_clean.set_visible(False)
            self._ola_prev = None

    def _on_alpha_changed(self, value: int):
        self._noise_alpha = value / 10.0
        self._label_alpha_val.setText(f"{self._noise_alpha:.1f}")

    # ─────────────────────────────────────────────────────────────────
    # 重建子图
    # ─────────────────────────────────────────────────────────────────

    def _rebuild_freq_ax(self):
        """清空并重建频谱子图，保持现有状态。"""
        self._ax_freq.clear()
        self._ax_freq.set_facecolor('#f0f0f0')
        self._ax_freq.set_xlabel("Frequency (Hz)")
        self._ax_freq.set_ylabel("Magnitude")
        self._ax_freq.set_title("Frequency Spectrum")
        self._ax_freq.grid(True, alpha=0.3)

        if self._freq_log:
            self._ax_freq.set_xscale('log')
            self._ax_freq.set_xlim(
                max(20, SAMPLE_RATE / self._fft_size), SAMPLE_RATE / 2,
            )
        else:
            self._ax_freq.set_xscale('linear')
            self._ax_freq.set_xlim(0, SAMPLE_RATE / 2)

        half = self._fft_size // 2
        (self._line_freq,) = self._ax_freq.plot(
            [], [], '#d62728', linewidth=1.0,
            label=f'Long ({self._fft_size})',
        )
        (self._line_freq_short,) = self._ax_freq.plot(
            [], [], '#2ca02c', linewidth=1.0, linestyle='--', alpha=0.7,
            label=f'Short ({SHORT_FFT_SIZE})',
        )
        self._line_freq_short.set_visible(self._dual_fft)

        (self._line_freq_clean,) = self._ax_freq.plot(
            [], [], '#9467bd', linewidth=1.5, alpha=0.85,
            label='Denoised',
        )
        self._line_freq_clean.set_visible(
            self._noise_suppression and self._noise_profile is not None
        )

        self._pitch_text = self._ax_freq.text(
            0.97, 0.95, '',
            transform=self._ax_freq.transAxes,
            ha='right', va='top', fontsize=15, fontweight='bold',
            color='#1a1a1a',
            bbox=dict(
                boxstyle='round,pad=0.35', facecolor='white',
                alpha=0.85, edgecolor='#cccccc',
            ),
        )

        if self._running:
            self._placeholder.set_visible(False)
        else:
            self._placeholder = self._ax_freq.text(
                0.5, 0.5, "Click 'Start' to begin\nmicrophone capture",
                transform=self._ax_freq.transAxes,
                ha='center', va='center', fontsize=13,
                color='gray', fontweight='bold',
            )

        self._fig.tight_layout(pad=2.0)
        self._canvas.draw_idle()

    def _rebuild_waterfall(self):
        """FFT 尺寸变化时重建瀑布图缓冲区。"""
        half = self._fft_size // 2
        self._waterfall_buffer = np.zeros((WATERFALL_FRAMES, half))
        self._waterfall_img.set_data(self._waterfall_buffer)
        self._waterfall_img.set_extent(
            [0, SAMPLE_RATE / 2, 0, WATERFALL_FRAMES],
        )
        self._canvas.draw_idle()

    # ─────────────────────────────────────────────────────────────────
    # 音频控制
    # ─────────────────────────────────────────────────────────────────

    def _toggle_stream(self):
        if self._running:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        if self._running:
            return
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                blocksize=1024,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            self._btn_start.setText("⏹  Stop")
            self._btn_start.setStyleSheet(
                "font-size: 14px; font-weight: bold;"
                " background-color: #ff6b6b; color: white;"
            )
            self._label_status.setText("Acquiring...")
            self._placeholder.set_visible(False)
            self._timer.start()
        except Exception as e:
            self._label_status.setText(f"Error starting stream:\n{e}")

    def _stop_stream(self):
        self._timer.stop()
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self._running = False
        self._btn_start.setText("▶  Start")
        self._btn_start.setStyleSheet(
            "font-size: 14px; font-weight: bold;"
        )
        self._label_status.setText("Stopped")
        self._frame_cache = None

        # 如果正在录音自动停止
        if self._recording:
            self._recording = False
            self._btn_record.setText("●  Record")
            self._btn_record.setStyleSheet("font-weight: bold;")

        self._placeholder = self._ax_freq.text(
            0.5, 0.5, "Click 'Start' to begin\nmicrophone capture",
            transform=self._ax_freq.transAxes,
            ha='center', va='center', fontsize=13,
            color='gray', fontweight='bold',
        )
        self._placeholder.set_visible(True)
        self._canvas.draw_idle()

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """回调线程 — 只做数据写入和录音累积，不做 GUI/FFT。"""
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        channel_data = indata[:, 0]
        self._buffer.write(channel_data)
        if self._recording:
            self._recorded_chunks.append(channel_data.copy())

    # ─────────────────────────────────────────────────────────────────
    # 主绘图更新 (定时器回调)
    # ─────────────────────────────────────────────────────────────────

    def _update_plots(self):
        if not self._running:
            return

        # ── 时域 ──
        time_data = self._buffer.read_last(BUFFER_SIZE)
        self._line_time.set_ydata(time_data)

        # ── 频域 ──
        frame_data = self._buffer.read_last(self._fft_size)
        if (
            self._frame_cache is not None
            and np.array_equal(frame_data, self._frame_cache)
        ):
            self._canvas.draw_idle()
            return
        self._frame_cache = frame_data.copy()

        windowed = apply_window(frame_data, self._window_type)
        try:
            spectrum = np.array(
                fft(windowed.tolist()), dtype=np.complex128,
            )
        except Exception as e:
            self._label_status.setText(f"FFT error: {e}")
            return

        half = self._fft_size // 2
        magnitude = np.abs(spectrum[:half])
        max_mag = float(np.max(magnitude))

        # ── 更新频谱线 (考虑对数/线性) ──
        if self._freq_log:
            mask = self._freq_axis > 0
            self._line_freq.set_data(self._freq_axis[mask], magnitude[mask])
        else:
            self._line_freq.set_ydata(magnitude)

        if max_mag > 1e-10:
            self._ax_freq.set_ylim(0, max_mag * 1.3)

        # ─────────────────────────────────────────────────────────
        # 扩展 4: 多分辨率 FFT
        # ─────────────────────────────────────────────────────────
        if self._dual_fft:
            short_data = self._buffer.read_last(SHORT_FFT_SIZE)
            short_win = apply_window(short_data, self._window_type)
            try:
                short_spec = np.array(
                    fft(short_win.tolist()), dtype=np.complex128,
                )
            except Exception:
                pass
            else:
                s_half = SHORT_FFT_SIZE // 2
                s_mag = np.abs(short_spec[:s_half])
                s_freq = (
                    np.arange(s_half, dtype=np.float64)
                    * SAMPLE_RATE / SHORT_FFT_SIZE
                )
                if self._freq_log:
                    sm = s_freq > 0
                    self._line_freq_short.set_data(s_freq[sm], s_mag[sm])
                else:
                    self._line_freq_short.set_data(s_freq, s_mag)
                self._line_freq_short.set_visible(True)

        # ─── 图例动态更新 ───
        legend_items = [self._line_freq]
        if self._dual_fft:
            legend_items.append(self._line_freq_short)
        if self._noise_suppression and self._noise_profile is not None:
            legend_items.append(self._line_freq_clean)
        if len(legend_items) > 1:
            self._ax_freq.legend(
                handles=legend_items, loc='upper left', fontsize=8,
            )
        elif (
            hasattr(self._ax_freq, 'legend_')
            and self._ax_freq.legend_ is not None
        ):
            self._ax_freq.legend_.remove()

        # ─────────────────────────────────────────────────────────
        # 扩展 5: 噪声抑制 (谱减法 + OLA 重建)
        # ─────────────────────────────────────────────────────────
        if self._noise_suppression and self._noise_profile is not None:
            if len(self._noise_profile) >= half:
                clean_mag = np.maximum(
                    0, magnitude - self._noise_profile[:half] * self._noise_alpha,
                )

                # 显示降噪后频谱
                if self._freq_log:
                    nm = self._freq_axis > 0
                    self._line_freq_clean.set_data(
                        self._freq_axis[nm], clean_mag[nm],
                    )
                else:
                    self._line_freq_clean.set_ydata(clean_mag)
                self._line_freq_clean.set_visible(True)

                # ── OLA 时域重建 ──
                # 用原始相位重建复数频谱 → IFFT → 加窗 → OLA
                phase = np.angle(spectrum[:half])
                clean_complex = clean_mag * np.exp(1j * phase)

                # 构造共轭对称频谱 (实信号 IFFT 的必要条件)
                # 对于偶数 N: [DC, pos_freq_1..half-1, Nyquist(如果N偶)]
                # refl = conj(pos_freq[::-1])
                dc_bin = np.array([complex(clean_complex[0].real, 0)])
                pos_only = clean_complex[1:]
                # 偶 N 时 half = N/2, pos_only 中不含 Nyquist
                symmetric = np.conj(pos_only[-1:0:-1])  # 反转并共轭
                full_clean = np.concatenate([dc_bin, pos_only, symmetric])

                # 如果 N 为偶数，需要包含 Nyquist 分量 (索引 half, 纯实数)
                if self._fft_size % 2 == 0:
                    # 此时 full_clean 长度为 1+(half-1)+(half-2)= N-2, 缺 Nyquist
                    nyquist = complex(clean_complex[half - 1].real, 0) if half > 0 else 0j
                    full_clean = np.concatenate([
                        full_clean[:half],
                        [nyquist],
                        full_clean[half:],
                    ])

                # IFFT
                recon = _ifft(full_clean.tolist())
                recon_real = np.real(recon)

                # Hann 窗口后 OLA
                w = np.hanning(self._fft_size)
                recon_win = recon_real * w

                if self._ola_prev is not None:
                    combined = np.zeros(self._fft_size)
                    combined[:self._fft_size // 2] = self._ola_prev
                    combined += recon_win
                    # 输出前半段作为重建信号
                    clean_signal = combined[:self._fft_size // 2]
                    self._ola_prev = recon_win[self._fft_size // 2:].copy()
                else:
                    self._ola_prev = recon_win[self._fft_size // 2:].copy()
                    clean_signal = recon_win[:self._fft_size // 2]

                # 在时域图上叠加降噪信号 (淡色)
                displayed = time_data.copy()
                overlap_len = min(
                    len(clean_signal), len(displayed),
                )
                displayed[-overlap_len:] = clean_signal[:overlap_len]
                # 可选：在时域图上显示降噪后的波形
                # (为保持干净，只在状态栏显示 NR 状态)

        # ─────────────────────────────────────────────────────────
        # 扩展 1: 瀑布图
        # ─────────────────────────────────────────────────────────
        if (
            self._waterfall_buffer is not None
            and half == self._waterfall_buffer.shape[1]
        ):
            self._waterfall_buffer = np.roll(self._waterfall_buffer, -1, axis=0)
            self._waterfall_buffer[-1] = magnitude
            self._waterfall_img.set_data(self._waterfall_buffer)
            wf_max = float(np.max(self._waterfall_buffer))
            if wf_max > 1e-10:
                self._waterfall_img.set_clim(0, wf_max)

        # ─────────────────────────────────────────────────────────
        # 扩展 2: 实时音高显示
        # ─────────────────────────────────────────────────────────
        peak_idx = int(np.argmax(magnitude))
        peak_freq = float(self._freq_axis[peak_idx])
        peak_val = float(magnitude[peak_idx])

        if peak_freq > 0 and peak_val > 1e-10:
            note = freq_to_note_name(peak_freq)
            self._label_pitch.setText(note)
            self._label_pitch_freq.setText(f"{peak_freq:.1f} Hz")
            self._pitch_text.set_text(f"{note}  {peak_freq:.1f} Hz")
        else:
            self._label_pitch.setText("—")
            self._label_pitch_freq.setText("— Hz")
            self._pitch_text.set_text("")

        # ── 状态信息 ──
        delta_f = SAMPLE_RATE / self._fft_size
        rec_indicator = " ● REC" if self._recording else ""
        ns_indicator = " | NR ON" if (
            self._noise_suppression and self._noise_profile is not None
        ) else ""
        self._label_status.setText(
            f"Running{rec_indicator}{ns_indicator}\n"
            f"Window: {self._window_type.capitalize()}\n"
            f"FFT: {self._fft_size} pt, Δf: {delta_f:.1f} Hz\n"
            f"Buffer: {self._buffer.count} samples",
        )

        self._canvas.draw_idle()

    # ─────────────────────────────────────────────────────────────────
    # 扩展 3: 录音保存与频谱导出
    # ─────────────────────────────────────────────────────────────────

    def _toggle_recording(self):
        if not self._running:
            self._label_status.setText("Start capture first")
            return
        if not self._recording:
            self._recording = True
            self._recorded_chunks = []
            self._btn_record.setText("■  Stop & Save")
            self._btn_record.setStyleSheet(
                "font-weight: bold;"
                " background-color: #ff4444; color: white;"
            )
        else:
            self._recording = False
            self._btn_record.setText("●  Record")
            self._btn_record.setStyleSheet("font-weight: bold;")
            self._save_recording()

    def _save_recording(self):
        if not self._recorded_chunks:
            return
        try:
            all_data = np.concatenate(self._recorded_chunks)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            sf.write(filename, all_data, SAMPLE_RATE)
            duration = len(all_data) / SAMPLE_RATE
            self._label_status.setText(
                f"Saved: {filename}\n"
                f"{len(all_data)} samples ({duration:.1f}s)",
            )
        except Exception as e:
            self._label_status.setText(f"Save error: {e}")

    def _export_csv(self):
        """导出当前频谱数据为 CSV 文件。"""
        if not self._running:
            self._label_status.setText("Start capture first")
            return
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spectrum_{timestamp}.csv"
            half = self._fft_size // 2
            frame_data = self._buffer.read_last(self._fft_size)
            windowed = apply_window(frame_data, self._window_type)
            spectrum = np.array(
                fft(windowed.tolist()), dtype=np.complex128,
            )
            magnitude = np.abs(spectrum[:half])

            data = np.column_stack([self._freq_axis, magnitude])
            header = (
                f"# Spectrum export {timestamp}\n"
                f"# Sample rate: {SAMPLE_RATE} Hz\n"
                f"# FFT size: {self._fft_size}\n"
                f"# Window: {self._window_type}\n"
                "freq_hz,magnitude"
            )
            np.savetxt(filename, data, delimiter=',', header=header, comments='')
            self._label_status.setText(f"Exported: {filename}")
        except Exception as e:
            self._label_status.setText(f"Export error: {e}")

    # ─────────────────────────────────────────────────────────────────
    # 扩展 5: 噪声抑制 — 学习噪声谱
    # ─────────────────────────────────────────────────────────────────

    def _learn_noise_profile(self):
        if not self._running:
            self._label_status.setText("Start capture first")
            return
        half = self._fft_size // 2

        # 从最近的帧多次采样取平均，得到更稳定的噪声估计
        num_samples = 6
        accum = np.zeros(half, dtype=np.float64)
        successful = 0
        for _ in range(num_samples):
            fd = self._buffer.read_last(self._fft_size)
            w = apply_window(fd, self._window_type)
            try:
                spec = np.array(fft(w.tolist()), dtype=np.complex128)
                accum += np.abs(spec[:half])
                successful += 1
            except Exception:
                continue

        if successful == 0:
            self._label_status.setText("Failed to learn noise profile")
            return

        self._noise_profile = accum / successful
        self._cb_noise_suppress.setEnabled(True)
        self._cb_noise_suppress.setChecked(True)
        self._noise_suppression = True
        self._line_freq_clean.set_visible(True)
        self._ola_prev = None  # 重置 OLA 缓存
        self._label_status.setText(
            f"Noise profile learned ({successful} frames averaged) ✓",
        )

    # ─────────────────────────────────────────────────────────────────
    # 关闭窗口
    # ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._stop_stream()
        event.accept()


# ─────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────

def main():
    """启动实时频谱分析仪。"""
    app = QApplication(sys.argv)
    app.setApplicationName("Spectrum Analyzer")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
