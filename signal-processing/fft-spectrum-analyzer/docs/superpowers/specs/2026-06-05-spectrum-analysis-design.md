# Spectrum Analysis & Peak Finding Design

> Date: 2026-06-05
> Status: Approved

## Overview

Extend the audio processing pipeline with spectrum computation and peak detection, then build `analyze_audio.py` that demonstrates pitch detection on a synthesized piano tone.

## Components

### `audio_processor.py` — Two new functions

```python
def compute_spectrum(frame: np.ndarray, fft_func, fs: int) -> Tuple[np.ndarray, np.ndarray]:
def find_peaks(
    magnitude: np.ndarray,
    freq: np.ndarray,
    threshold_ratio: float = 0.3,
) -> list[tuple[float, float]]:
```

**`compute_spectrum`**
- Runs FFT on windowed/raw frame via `fft_func`
- Returns `(freq_bins, magnitude)` — positive frequencies only (first `N//2` bins)
- Frequency axis: `fft_freq(N, d=1/fs)` → positive half

**`find_peaks`**
- Scans `magnitude` array for local maxima (point > left neighbor AND point > right neighbor)
- Filters: keep only peaks where `magnitude > max(magnitude) * threshold_ratio`
- Returns sorted list `[(freq, mag), ...]` descending by magnitude

### Note Name Mapping

```python
A4 = 440.0
semitone = 69 + 12 * math.log2(freq / A4)
note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
note = note_names[semitone % 12]
octave = semitone // 12 - 1
# → e.g. "C4", "A#5"
```

Constrained to MIDI range [0, 127]; outside returns `f"{freq:.1f} Hz"`.

### `analyze_audio.py` — Script flow

```
synthesize_piano_note(note="C4", duration=2.0, sr=44100)
  → load_audio (via temp WAV)
  → frame_signal (1024, 512)
  → find highest-energy frame
  → apply_window (hann)
  → compute_spectrum
  → find_peaks (threshold_ratio=0.3)
  → print peak list with note names
  → plot spectrum + red peak markers → save spectrum.png
```

**Synthesized piano tone:**
- Fundamental sine wave at note frequency
- Harmonics 2–8 with decaying amplitude: `amp_k = 1/k` for even k, `0.8/k` for odd k
- Exponential amplitude envelope: `exp(-t * 2.0)` for natural decay
- Duration 2.0s, saved as temp WAV via `soundfile.write`

### Error Handling

- `compute_spectrum`: raises `ValueError` if frame is not 1D
- `find_peaks`: returns empty list for empty/flat input
- Plot saves even if no peaks found (spectrum only)

### Output

```
vibe coding/
├── audio_processor.py       # +2 functions
├── analyze_audio.py         # NEW
├── docs/superpowers/specs/
│   └── 2026-06-05-spectrum-analysis-design.md  # NEW
└── spectrum.png             # generated at runtime
```

### Dependencies

- Existing: `numpy`, `soundfile`, `matplotlib`, `fft_analysis.my_fft`
- No new dependencies
