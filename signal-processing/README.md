# Signal Processing

本目录收录信号处理相关项目。

---

## 项目列表

| 目录 | 项目名 | 课程/场景 |
|------|--------|-----------|
| [fft-spectrum-analyzer/](./fft-spectrum-analyzer/) | 实时频谱分析仪 | 数字信号处理课程设计 |

---

### FFT 实时频谱分析仪

基于 Cooley-Tukey 基2 DIT 算法的实时频谱分析仪，纯 Python 实现，配备 PyQt5 图形界面。

**算法亮点**
- 纯 Python 实现基2 时间抽取递归 FFT/IFFT
- RMSE < 2.2×10⁻¹⁴（对比 NumPy 参考实现）
- 频率定位精度 < 0.1 Hz，复杂度 O(N log N)

**GUI 扩展功能（5项）**
1. 频谱瀑布图
2. 实时音高检测
3. 录音保存 / CSV 导出
4. 多分辨率 FFT 叠加显示
5. 噪声抑制（谱减法 + OLA）

**技术栈**：Python 3.14 · PyQt5 · matplotlib · sounddevice · NumPy

**快速启动**

```bash
pip install PyQt5 matplotlib sounddevice soundfile numpy scipy
python gui_app.py
```
