# Audio Processor Design

> Date: 2026-06-05
> Status: Approved

## Overview

Audio signal preprocessor for FFT analysis: load WAV files, frame signals, and apply window functions. Integrates with the existing `fft_analysis/my_fft.py` for spectrum analysis.

## Components

### `audio_processor.py`

Three public functions, no classes:

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `load_audio(file_path, sr=None)` | file path, optional target SR | `(signal: np.ndarray, sr: int)` | Read WAV via `soundfile.read()` |
| `frame_signal(signal, frame_size, hop_length)` | 1D array, int, int | 2D `(num_frames, frame_size)` array | Sliding window segmentation |
| `apply_window(frame, window_type='hann')` | 1D array, str | 1D array (same length) | Apply window function |

### `main.py`

Demonstration script:

1. Generate 440 Hz sine wave → save `test.wav`
2. `load_audio` → `(signal, sr=44100)`
3. `frame_signal` → `(258, 1024)` frames
4. `apply_window(frames[0])` with Hann window
5. Call `my_fft.fft(windowed_frame)`
6. Compute magnitude spectrum → find top-5 peak frequencies
7. Print results

## Data Flow

```
440Hz sine generation
  → soundfile.write('test.wav')
  → load_audio('test.wav')
  → frame_signal(signal, 1024, 512)
  → apply_window(frames[0], 'hann')
  → my_fft.fft(windowed)
  → np.abs(spectrum) → peak frequencies
```

## Error Handling

All invalid inputs raise typed exceptions:
- File not found → `FileNotFoundError`
- Unsupported window type → `ValueError`
- Invalid frame_size/hop_length → `ValueError`
- Non-WAV file → `ValueError` from soundfile

## Files

```
vibe coding/
├── audio_processor.py    # new
├── main.py               # new
├── test.wav              # generated at runtime
└── fft_analysis/
    ├── my_fft.py         # existing
    └── ...
```

## Dependencies

- `soundfile` for WAV I/O
- `numpy` for array operations
- Existing `my_fft.py` (pure Python, no numpy FFT)
- Standard library: `math`, `os`
