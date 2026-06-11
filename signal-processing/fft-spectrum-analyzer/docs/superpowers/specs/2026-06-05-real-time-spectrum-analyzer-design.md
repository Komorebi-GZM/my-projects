# Real-time Spectrum Analyzer Design

> Date: 2026-06-05
> Status: Approved

## Overview

PyQt5 + matplotlib real-time audio spectrum analyzer. Microphone input via sounddevice, rolling time-domain waveform, live FFT spectrum, and interactive control panel.

## Architecture

```
gui_app.py (single file)
└── MainWindow (QMainWindow)
    ├── matplotlib FigureCanvas
    │   ├── subplot 1: Time domain (rolling 200ms)
    │   └── subplot 2: Frequency spectrum
    └── Control panel (QWidget)
        ├── Start/Stop button
        ├── Window function dropdown (Hann/Rect/Hamming)
        ├── Freq scale dropdown (Linear/Log)
        ├── FFT size dropdown (1024/2048)
        └── Status label
```

## Data Flow

```
Microphone → sd.InputStream (callback thread)
  → CircularBuffer.write()  (thread-safe, O(1))
  → QTimer @ 50ms (main thread)
    → CircularBuffer.read_last(FFT_SIZE)
    → apply_window()
    → my_fft.fft()
    → update matplotlib lines
    → canvas.draw()
```

## Components

### CircularBuffer
- Fixed-capacity ring buffer (3200 samples = 200ms @ 16kHz)
- `write(data)`: append, overwrite oldest if full
- `read_last(n)`: return newest n samples
- No locks needed — single writer (callback) / single reader (timer)

### MainWindow
- Initial state: "Click Start" placeholder on spectrum
- Start: create InputStream + start QTimer
- Stop: stop stream + stop timer
- Close: clean up resources

### Controls
| Control | Options | Default |
|---------|---------|---------|
| Window | Hann, Rectangular, Hamming | Hann |
| Freq scale | Linear, Log | Linear |
| FFT size | 1024, 2048 | 2048 |

## Performance

- Timer interval: 50ms (~20fps, below callback rate of ~64ms)
- Audio callback: writes only, no FFT/GUI work
- MyFFT on 2048 points: ~2.3ms (verified in benchmark)
- matplotlib `draw()` per frame — sufficient for 2 simple subplots

## Dependencies

- `PyQt5` (new)
- `sounddevice` (new)
- `numpy` (existing)
- `matplotlib` (existing)
- `audio_processor.py` (existing — apply_window)
- `fft_analysis.my_fft` (existing — fft)

## Files

```
vibe coding/
├── gui_app.py                 # NEW
├── docs/superpowers/specs/
│   └── 2026-06-05-real-time-spectrum-analyzer-design.md  # NEW
```
