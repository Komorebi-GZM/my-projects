# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

数字信号处理课程设计 — 基于 Cooley-Tukey FFT 的实时频谱分析仪。

- **Language**: Python 3.14
- **GUI**: PyQt5 + matplotlib + sounddevice
- **Package manager**: pip / conda-forge

## Project Structure

```
fft/
├── fft_analysis/          # FFT 算法核心
│   ├── my_fft.py          #   纯 Python 基2 DIT FFT/IFFT 实现
│   ├── test_fft.py        #   单元测试
│   ├── verify_fft.py      #   验证脚本（基准、误差、信号测试）
│   └── verification.md    #   验证报告
├── audio_processor.py     # 音频预处理（分帧、加窗、峰值检测、音名映射）
├── gui_app.py             # PyQt5 实时频谱分析仪（5 个扩展功能）
├── main.py                # FFT 演示脚本（bin对齐 vs 频谱泄漏）
├── analyze_audio.py       # 钢琴音色合成 + 频谱峰值分析
└── report.md              # 课程设计报告
```

## Build & Test Commands

```bash
# 运行 FFT 演示
python main.py

# 运行音频频谱分析
python analyze_audio.py

# 启动 GUI 实时频谱分析仪
python gui_app.py

# 运行 FFT 测试
python -m pytest fft_analysis/test_fft.py -v

# 运行 FFT 完整验证（含基准测试）
python fft_analysis/verify_fft.py
```

## Key Technical Details

- **FFT 实现**: 基2 时间抽取 (DIT) 递归 Cooley-Tukey，RMSE < 2.2×10⁻¹⁴ vs NumPy
- **窗函数**: Hann（默认）、Hamming、Rectangular
- **GUI 扩展**: 瀑布图、实时音高检测、录音保存/CSV导出、多分辨率 FFT、噪声抑制（谱减法+OLA）
- **音频后端**: sounddevice（输入）+ soundfile（文件读写）
- **默认采样率**: 16000 Hz (GUI) / 44100 Hz (演示脚本)
- **默认 FFT 点数**: 2048 (GUI) / 1024 (演示脚本)
