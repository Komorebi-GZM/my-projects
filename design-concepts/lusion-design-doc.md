# Lusion.co 设计解构文档

> 来源：https://lusion.co  
> 解构日期：2026-06-08  
> 工具：agent-browser DOM 提取 + 设计系统分析

---

# Section A — 拆解报告（中文）

## 1. 交互逻辑

### 用户流转
- **页面结构**：单页应用（SPA），全屏沉浸式 WebGL 体验，非传统导航滚动
- **主要交互行为**：
  - 滚动（自定义平滑滚动容器，非原生 document scroll）驱动内容呈现
  - 悬停项目卡片 → WebGL 3D 场景切换 / 视觉变形
  - 点击导航链接 → 锚点跳转或页面切换
  - 表单提交：Newsletter 邮箱订阅（footer 区域）
  - 音频控制：PLAY/MUTE 按钮控制环境音效或视频配乐
- **状态机**：
  - Header 按钮状态："Let's talk" pill 按钮（正常态）、"Menu Close" 切换按钮（菜单开关态）
  - 项目卡片：默认态 → hover 3D 激活态 → 点击跳转
  - 视频浮层：PLAY → 播放中 / MUTE → 静音切换
- **导航模式**：
  - Header 固定导航（HOME、ABOUT US、PROJECTS、LABS、CONTACT）
  - 导航链接采用双重文字（"HOME HOME"），暗示 hover 时文字滑动/替换动效
  - 返回按钮（Back）在项目详情页出现
- **反馈机制**：
  - WebGL 场景实时渲染作为主要视觉反馈
  - CSS transition 驱动的 hover/click 微交互
  - 音效作为辅助反馈维度

### 特殊交互
- **自定义平滑滚动**：`scrollMax=0`，页面不使用浏览器原生滚动，完全通过 CSS transform 或 JS 控制滚动
- **全屏 Canvas 渲染**：3 个 canvas 元素驱动核心视觉，WebGL 上下文
- **菜单系统**：Fixed 定位的全屏菜单浮层（z-index: 1000，`display:none` → 打开时切换），含导航链接 + Newsletter 输入

---

## 2. 交互动效

### 滚动驱动
- 自定义平滑滚动（非原生），可能基于 Locomotive Scroll 类似库或自研方案
- 视差分层：WebGL 3D 场景随滚动变换视角

### CSS Transition 体系
检测到的所有 transition 均使用 `cubic-bezier` 缓动：

| Transition | 时长 | 缓动函数 | 用途推断 |
|---|---|---|---|
| `color, transform` | 0.5s / 0.4s | `cubic-bezier(0.4, 0, 0.1, 1)` | 导航链接 hover（颜色 + 位移） |
| `transform` | 0.3s | `cubic-bezier(0.4, 0, 0.1, 1)` | 通用元素进出场 |
| `transform` | 0.3s | `cubic-bezier(0.16, 1, 0.3, 1)` | 弹性缓出（类似 spring） |
| `transform` | 0.1s | `cubic-bezier(0.4, 0, 0.1, 1)` | 快速响应（如按钮 press） |
| `transform` | 0.4s | `cubic-bezier(0.4, 0, 0.1, 1)` | 较大元素动效 |

### Hover 效果
- 导航链接：双重文字结构暗示文字滑动替换效果
- 项目卡片：WebGL 3D 场景激活 + 光标变为 pointer
- Pill 按钮：背景色 / 文字色过渡（color 0.5s transition）

### 性能策略
- 全部使用 `transform` + `opacity`（GPU 合成，不触发 reflow）
- Canvas 渲染在 `requestAnimationFrame` 循环中
- 无 `will-change` 显式声明（依赖浏览器自动优化）

---

## 3. 技术栈

```
框架：       Astro（通过 _astro/ 资源路径确认）
3D 渲染：    Three.js（3 个 canvas，WebGL 上下文）
动画：       CSS Transitions + 自研 JS（未检测到 GSAP 全局对象）
字体：       自定义字体 Aeonik（项目自托管）+ 系统 Helvetica fallback
             + IBM Plex Mono（代码/等宽场景）+ LusionMono（品牌定制等宽）
CSS：        Vanilla CSS + CSS Custom Properties（大规模使用）
构建：       Astro 内置（Vite 底层）
托管：       未确认（可能 Vercel / Cloudflare / 自建）
特殊：       无 img/video 标签 — 所有视觉内容通过 WebGL canvas 渲染
             音频系统（PLAY/MUTE 控制）
             41 个内联 SVG 图标
```

### 关键证据
- 资源路径包含 `_astro/` → Astro 框架
- `canvas` 元素 3 个，尺寸 1280×577、1282×579（全屏）+ 45×45（小图标/thumb）
- `--color-*`、`--base-padding-*`、`--grid-*` 等大量 CSS 自定义属性
- `clamp()`、`max()` 用于流体排版和间距

---

## 4. 排版布局

### 页面结构（自上而下）

```
┌──────────────────────────────────┐
│  HEADER (fixed, 146px, z:52)     │
│  Logo | Nav Links | Let's Talk   │
├──────────────────────────────────┤
│  HERO SECTION                    │
│  WebGL 3D 场景背景               │
│  H1: "We create 3D visual        │
│  storytelling..." (32px)         │
│  H4: "Bold Ideas, Brought to     │
│  Life" (128px, 超大展示)         │
│  H2: 描述段落 (19.2px)           │
│  CTA: "OUR APPROACH" →           │
├──────────────────────────────────┤
│  FEATURED WORK                   │
│  H4: "Featured Work" (102.4px)   │
│  项目卡片网格（每项含分类标签 +   │
│  项目名 + WebGL 预览）           │
│  CTA: "SEE ALL PROJECTS" →       │
├──────────────────────────────────┤
│  CTA SECTION                     │
│  "Let's work together!"          │
├──────────────────────────────────┤
│  FOOTER                          │
│  地址 | 社交媒体 | 邮箱           │
│  Newsletter 订阅表单             │
│  R&D: labs.lusion.co             │
└──────────────────────────────────┘
```

### 栅格系统
- **12 列栅格**：`calc((100% - 11 × 2vw) / 12)`
- **列间距**：`2vw`（流体）
- **内边距**：`padding-x: max(5vw, 40px)`、`padding-y: clamp(30px, 4vw, 50px)`
- **内容宽度**：全宽布局（fluid full-bleed），无边距约束
- **对齐方式**：Hero 区域左对齐，标题/描述/CTA 堆叠排列

### 视觉层次
- Z-pattern：Hero 标题 → 描述 → CTA 形成自然阅读流
- 超大标题（128px）建立强烈的品牌第一印象
- Featured Work 区域以项目卡片阵列形成视觉节奏
- 留白策略：大段留白让 WebGL 场景呼吸

---

## 5. 画面风格

### 设计趋势
- **WebGL/3D 沉浸式**：用 3D 实时渲染替代传统图片/视频
- **极简主义底色**：白底黑字，让 3D 内容成为绝对焦点
- **高对比度排版**：超大字号（128px）与负字距（-2.56px）的展示字体

### 情绪与调性
- 前卫 / 技术驱动 / 创意自信
- "我们做的东西很厉害，但我们不需要大喊大叫"（Let the work speak）
- 介于 agency 专业感与实验室实验感之间

### 背景策略
- 主背景：纯白 `#FFFFFF`
- WebGL Canvas 作为"内容"而非"装饰"
- 无渐变、无纹理、无网格线 — 极度克制

### 卡片风格
- 项目卡片：无传统卡片容器！每个项目由分类文字标签 + 字符间距展开的项目名 + WebGL 预览组成
- 无阴影、无边框、无圆角 — "反卡片"设计

### 图标风格
- 41 个内联 SVG
- 线条风格，简洁克制
- 用于导航箭头、关闭按钮、社交媒体图标等

---

## 6. 视觉元素

### Hero 区域
- 发布时标注为 "Bold Ideas, Brought to Life" 的超大 H4
- 文字可能随滚动产生视差或变形效果
- WebGL 3D 场景作为不可分割的背景内容

### 品牌元素
- Logo 在 header 左侧
- "Lusion" 品牌名在 footer 和项目描述中
- 品牌定制字体：Aeonik、LusionMono
- 品牌色系统：蓝、红、绿、紫四色高饱和点缀

### 项目卡片
- 无传统缩略图 — WebGL canvas 实时 3D 预览
- 每个项目的分类标签以 `•` 分隔（CONCEPT • WEB • DESIGN • 3D 等）
- 项目名通过字符间距展开显示，形成独特的视觉节奏

### CTA 层级
1. **Primary (填充)**：`"Let's talk"` pill 按钮 — 灰蓝底 `#2b2e3a` + 白字
2. **Secondary (文字链接)**：`"OUR APPROACH"`、`"SEE ALL PROJECTS"` — 14px 大写加粗
3. **Tertiary (导航)**：导航链接 — 16px 大写正常字重

### Footer 信息
- 地址：Bristol, UK（实体工作室存在感）
- 社交链接：Twitter/X、Instagram、LinkedIn
- 双邮箱：hello@ / business@（区分一般咨询和商务合作）
- Newsletter 订阅：输入框 + 箭头按钮
- R&D 实验室链接：labs.lusion.co

---

## 7. 色彩系统

### CSS 自定义属性（精确提取）

```css
--color-blue:       #1a2ffb;   /* 主品牌蓝 — CTA、链接 */
--color-dark-blue:  #071bdf;   /* 深蓝变体 — hover 状态 */
--color-red:        #ff4c41;   /* 强调红 — 错误、警示 */
--color-green:      #c1ff00;   /* 霓虹绿 — 成功、高亮 */
--color-purple:     #8832f7;   /* 紫 — 装饰点缀 */
--color-white:      #ffffff;   /* 纯白 — 主背景 */
--color-off-white:  #f0f1fa;   /* 淡紫白 — 替代分区背景 */
--color-dark-white: #e4e6ef;   /* 深灰白 — 菜单按钮背景 */
--color-grey-blue:  #2b2e3a;   /* 灰蓝 — pill 按钮填充色 */
--color-error:      #e90000;   /* 错误红 */
--header-color:     #0016ec;   /* Header 专属色 */
```

### 色彩使用规则

| 用途 | 颜色 | 备注 |
|---|---|---|
| 主背景 | `#fff` | 全白，干净 |
| 正文 | `#000` / `rgb(0,0,0)` | 纯黑，高对比 |
| 主要 CTA 填充 | `#2b2e3a`（灰蓝） | 白字，pill 形状 |
| 次要 CTA 填充 | `#fff`（白） | 黑字，pill 形状 |
| 菜单按钮背景 | `#e4e6ef`（深灰白） | 黑字 |
| 链接/强调色 | `#1a2ffb`（蓝） | 推测用于 hover |
| 错误/警示 | `#e90000` / `#ff4c41` | 表单验证 |

### 渐变
- **未检测到任何 CSS 渐变** — 设计完全依赖纯色和 WebGL 渲染

---

## 8. 字体层级

### 字体家族

```
展示/正文：Aeonik（自托管自定义字体）
  字重：400（Regular）、500（Medium）
等宽：    IBM Plex Mono（代码场景）
品牌等宽：LusionMono（品牌定制）
Fallback：Helvetica, Arial, FreeSans, Garuda, sans-serif
```

### 排版层级表

| 层级 | 标签 | 字号 | 字重 | 行高 | 字距 | 颜色 | 用途 |
|---|---|---|---|---|---|---|---|
| Display | H4 | 128px | 400 | 1.0 (128px) | -2.56px | #000 | Hero 主标题 |
| 大标题 | H4 | 102.4px | 400 | 0.9 (92px) | -2.048px | #000 | 区域标题 |
| H1 | H1 | 32px | 400 | 1.1 (35px) | normal | #000 | Hero 副标题 |
| H3 | H3 | 38px | 400 | 1.15 (44px) | normal | #000 | Newsletter 标题 |
| H2/正文 | H2 | 19.2px | 400 | 1.4 (27px) | normal | #000 | 描述段落 |
| 导航 | A | 16px | 400 | — | — | #000 | 主导航链接 |
| CTA 链接 | A | 14px | 500 | — | — | #000 | 文字 CTA |
| Footer 链接 | A | 17.5px | 400 | — | — | #000 | Footer 文字 |
| Pill 按钮 | BUTTON | 14px | — | — | — | #fff/#000 | CTA 按钮 |

### 特殊处理
- 超大标题使用负字距（`letter-spacing: -2.56px`）让字形更紧凑有力
- 导航链接全部大写（`text-transform: uppercase`），建立统一节奏
- 没有文字阴影、渐变文字等装饰性处理
- 正文使用流体单位（`clamp()`），适配不同视口

---

## 9. 栅格系统

### 基础参数

```
栅格列数：  12 列
列宽：      calc((100% - 11 × 2vw) / 12)
列间距：    2vw（流体，随视口缩放）
容器内边距：padding-x: max(5vw, 40px)
            padding-y: clamp(30px, 4vw, 50px)
圆角：      --global-border-radius: 20px
图标尺寸：  --cross-size: clamp(0.875rem, 1vw, 2rem)
```

### 响应式断点推断

```
Mobile：  < 640px  — 单列堆叠，导航变汉堡菜单
Tablet：  640-1024px — 可能 2 列布局
Desktop： > 1024px — 全宽 12 列栅格 + 流体间距
```

### 布局行为
- **无固定最大宽度容器** — 全宽设计，利用 vw 单位保持比例
- **Header 固定定位**（`position: fixed; z-index: 52; height: 146px`）
- **内容区叠加在 WebGL canvas 之上**（通过 z-index 层级管理）
- Footer 采用多列信息布局：地址 / 社交 / 邮箱 / Newsletter

---

## 10. 组件架构

### 组件清单

| 组件 | 变体 | 关键参数 |
|---|---|---|
| **Pill Button** | Dark（填充）、Light（镂空） | `border-radius: 87.5-100px`、`height: 45px`、`font-size: 14px`、`padding: 0 16-23px`、`display: flex`、`align-items: center`、`gap: 9px` |
| **Nav Link** | Default、Active | `font-size: 16px`、`text-transform: uppercase`、`font-weight: 400`、双重文字结构 |
| **Text CTA** | Default | `font-size: 14px`、`text-transform: uppercase`、`font-weight: 500`、纯文字无背景 |
| **Project Card** | Default | 分类标签行 + 字距展开项目名 + WebGL 预览 canvas |
| **Menu Overlay** | Closed / Open | `position: fixed`、`z-index: 1000`、`display: none → block`、`bg: #000`、全屏覆盖 |
| **Newsletter Form** | Default | 输入框 + 箭头提交按钮、`padding: 30px` |
| **Sound Control** | PLAY / MUTE | `font-size: 16px`、透明背景、绝对定位 |
| **Video Overlay** | 播放中 / 暂停 | `position: static`、PLAY/MUTE 双按钮 |

### Pill Button 详细规格

```
Dark Variant ("Let's talk"):
  background: #2b2e3a (--color-grey-blue)
  color: #fff
  border-radius: 87.5px
  height: 44.8px
  font-size: 14px
  padding: 0 15.75px 0 22.75px (非对称，左侧给图标留空间)
  transition: color 0.5s, transform 0.4s cubic-bezier(0.4, 0, 0.1, 1)

Light Variant ("Back", "Menu Close"):
  background: #fff
  color: #000
  border-radius: 87.5-100px
  height: 44.8px
  font-size: 14px
```

### Header 结构

```
HEADER (fixed, z:52, height:146px, transparent bg)
├── Logo (link "Go to home page")
├── Nav Links (HOME, ABOUT US, PROJECTS, LABS)
├── Right Section
│   ├── Sound Button (header-right-sound-btn)
│   ├── Let's Talk Button Placeholder
│   └── Let's Talk Pill Button (header-right-talk-btn)
└── Menu Button (header-right-menu-btn)
```

---

## 11. 可访问性

### 优势
- ✅ ARIA labels 应用于功能性按钮（`aria-label="Back"`、`"Menu button"`、`"Watch reel button"`、`"Send newsletter form button"`）
- ✅ 语义化标题层级（H1 → H2 → H3 → H4）虽然顺序不标准
- ✅ 相对单位：`rem`、`clamp()`、`vw` 用于文字和间距
- ✅ 交互元素有清晰的 cursor 变化（`cursor: pointer`）

### 问题
- ❌ **`user-scalable=no`**：viewport meta 中设置了 `maximum-scale=1.0, user-scalable=no`，阻止用户缩放 — 严重可访问性违规（WCAG 1.4.4）
- ❌ **缺少可见焦点指示器**：未检测到 `:focus-visible` 样式
- ❌ **无 `<nav>` 标签**：导航使用 `<button>` 和 `<link>` + `<div>`，而非语义化 `<nav>`
- ❌ **无 `<main>` 标签**：主内容区域缺少 landmark
- ❌ **无 `<section>` 标签**：634 个 div，0 个 section
- ❌ **40+ SVG 可能缺少可访问文本**：需检查 `<title>` / `aria-label`
- ❌ **未检测到 `prefers-reduced-motion`**：WebGL 重度动画无减弱选项
- ❌ **3 个 canvas 元素**：所有视觉内容在 canvas 中，对屏幕阅读器完全不可见

### 触摸目标
- Pill 按钮高度 44.8px ≈ 45px，符合 WCAG 44px 最小建议
- 导航链接文字大小 16px，行高充足

---

## 12. 响应式策略

### 方案
- **Desktop-first**：流体尺寸为主，通过 `clamp()` 和 `max()` 函数实现缩放
- Viewport meta：`width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no`

### 导航
- Desktop：水平导航栏 + pill 按钮
- Mobile：汉堡菜单触发全屏覆盖菜单（推测）
- 菜单按钮（`header-right-menu-btn`）在所有视口尺寸存在

### 布局变化（推断）
- 12 列栅格 → 小屏可能变 4-6 列或堆叠
- 项目卡片可能从多列变单列
- Footer 多列布局在移动端堆叠
- 超大标题（128px/102.4px）在小屏通过 `clamp()` 缩小

### 图片/视觉
- 无传统 `<img>` 标签 — 所有视觉内容通过 WebGL canvas
- Canvas 尺寸响应式缩放（1280×577 → 视口自适应）

### 排版
- 使用 `clamp()` 实现流体排版（如 `--base-padding-y: clamp(30px, 4vw, 50px)`）
- 间距使用 `vw` 和 `max()` 函数，始终与视口保持比例

### 间距
- Desktop：`padding-x: max(5vw, 40px)`（最小 40px）
- Mobile：间距随视口等比缩放

---

# Section B — 设计重构提示词

## B.1 Design Reconstruction Prompt (English)

````markdown
## Design Reconstruction Prompt — Lusion.co

### Visual Identity
A WebGL-driven immersive creative agency website. The design is radically minimal — pure white backgrounds with massive display typography, letting real-time 3D WebGL scenes carry all visual weight. No images, no videos, no gradients — just white space, black Aeonik type, and live 3D canvases. The aesthetic is "anti-decorative": confidence through restraint.

### Layout Architecture
- **Fixed Header** (146px, transparent, z-index 52): Logo left, uppercase nav links center, "Let's Talk" pill button right, menu toggle button
- **Hero Section**: Full-viewport WebGL canvas background. Stacked typography — H1 (32px) → Display H4 (128px, -2.56px letter-spacing) → H2 description (19.2px) → "OUR APPROACH" text CTA
- **Featured Work Section**: H4 heading (102.4px), followed by project cards. Each card = category tags (CONCEPT • DESIGN • 3D • etc.) + character-spaced project name + live WebGL 3D preview on hover
- **CTA Section**: "Let's work together!" clickable text block
- **Footer**: Address + social links + dual email + newsletter form (input + arrow submit)

### Color Palette
```css
--color-blue:       #1a2ffb;   /* Brand accent */
--color-red:        #ff4c41;   /* Error, emphasis */
--color-green:      #c1ff00;   /* Success, highlight */
--color-purple:     #8832f7;   /* Decorative accent */
--color-white:      #ffffff;   /* Primary background */
--color-off-white:  #f0f1fa;   /* Alternate section bg */
--color-dark-white: #e4e6ef;   /* Menu button bg */
--color-grey-blue:  #2b2e3a;   /* Pill button fill */
--color-dark-blue:  #071bdf;   /* Dark blue variant */
--color-error:      #e90000;   /* Validation error */
```
Text: pure black (#000) on white backgrounds. No grey text — maximum contrast throughout.

### Typography System
```
Primary font:    Aeonik (self-hosted, weights 400, 500)
Mono font:       IBM Plex Mono
Brand mono:      LusionMono
Fallback:        Helvetica, Arial, sans-serif

Type scale:
  Display:  128px, weight 400, line-height 1.0, letter-spacing -0.02em
  Section:  102.4px, weight 400, line-height 0.9, letter-spacing -0.02em
  H1:       32px, weight 400, line-height 1.1
  H2:       19.2px, weight 400, line-height 1.4
  H3:       38px, weight 400, line-height 1.15
  Nav:      16px, weight 400, uppercase
  CTA text: 14px, weight 500, uppercase
  Footer:   17.5px, weight 400
  Pill btn: 14px, weight 400
```
All headings use normal weight (400). No bold anywhere.

### Component Specifications

**Pill Button**
```
Dark:  bg #2b2e3a, color #fff, border-radius 88px, height 45px, 
       font 14px, padding 0 16px 0 23px, flex + align-center + gap 9px
Light: bg #fff, color #000, same dimensions
Transition: color 0.5s, transform 0.4s cubic-bezier(0.4, 0, 0.1, 1)
```
**Nav Link**: 16px uppercase Aeonik, duplicate text structure (e.g. "HOME HOME") for slide animation on hover, transition: color 0.5s, transform 0.4s
**Text CTA**: 14px uppercase, weight 500, pure text link, no underline
**Project Card**: Category tag row (• separated, small caps) + character-spaced project name + WebGL canvas overlay on hover
**Newsletter Form**: Text input + arrow button, container padding 30px

### Interaction & Animation
- **Scroll**: Custom smooth scroll (no native scroll). Content translates via JS, WebGL scenes respond to scroll position
- **Hover (nav)**: Duplicate text slides in/out with color shift (0.5s transition)
- **Hover (projects)**: WebGL 3D preview activates on the card canvas
- **Transitions**: ALL use `cubic-bezier(0.4, 0, 0.1, 1)` — a sharp deceleration curve. Durations: 0.1s (quick), 0.3s (standard), 0.4s (large elements)
- **Menu**: Full-screen overlay (fixed, z-1000, black bg), slides in/out
- **Audio**: PLAY/MUTE toggle for ambient sound/video reel, absolute positioned

### Accessibility Requirements
- **MUST**: Remove `user-scalable=no` — allow browser zoom
- **MUST**: Add `:focus-visible` ring (2px solid #1a2ffb, 2px offset) to all interactive elements
- **MUST**: Use `<nav>`, `<main>`, `<section>` for semantic landmarks
- **MUST**: Add `aria-label` to all icon-only buttons
- **MUST**: Implement `prefers-reduced-motion` to disable WebGL animations
- **SHOULD**: Add off-screen text alternatives for canvas content
- **SHOULD**: Ensure 44×44px minimum touch targets (already mostly met)

### Responsive Behavior
```
Desktop (>1024px): Full layout, 12-col fluid grid, 128px display type
Tablet (640-1024px): 2-col where possible, scaled typography
Mobile (<640px): Single column, hamburger menu, clamped typography via clamp()
```
- Fluid spacing: `padding-x: max(5vw, 40px)`, `padding-y: clamp(30px, 4vw, 50px)`
- Grid: 12 columns, `2vw` gaps, column width `calc((100% - 11 * 2vw) / 12)`
- Typography uses `clamp()` for smooth scaling

### Technical Stack
```
Framework:   Astro
3D:          Three.js (WebGL)
CSS:         Vanilla CSS + CSS Custom Properties
Animation:   CSS Transitions + Custom JS (no GSAP)
Fonts:       Self-hosted Aeonik, IBM Plex Mono, LusionMono
Build:       Vite (via Astro)
```

### Implementation Priority
1. Layout shell: fixed header + full-viewport sections + custom scroll container
2. Typography: Aeonik font loading + CSS type scale + fluid clamp()
3. Color system: CSS custom properties for all colors
4. WebGL integration: Three.js scene setup + canvas management
5. Components: Pill buttons, nav links, project cards, newsletter form
6. Interactions: CSS transitions, custom smooth scroll, hover effects
7. Responsive: Mobile nav (hamburger → overlay), fluid spacing/type
8. Accessibility: Focus rings, semantic HTML, reduced motion, screen reader text
````

---

## B.2 设计重构提示词（中文）

````markdown
## 设计重构提示词 — Lusion.co

### 视觉风格
极致克制的 WebGL 沉浸式创意机构网站。纯白背景 + 超大展示排版 + 实时 3D WebGL 场景承担全部视觉重量。无图片、无视频标签、无渐变 — 仅靠留白、黑色 Aeonik 字体和实时 3D Canvas 渲染。美学核心：用克制展示自信（"anti-decorative"）。

### 布局架构
- **固定头部**（146px，透明，z-index 52）：Logo 左 + 大写导航链接中 + "Let's Talk" pill 按钮右 + 菜单切换按钮
- **Hero 区域**：全视口 WebGL canvas 背景，文字堆叠 — H1（32px）→ Display H4（128px，负字距）→ H2 描述（19.2px）→ "OUR APPROACH" 文字 CTA
- **作品展示区**：H4 标题（102.4px）+ 项目卡片列表。每张卡片 = 分类标签（CONCEPT • DESIGN • 3D 等）+ 字距展开项目名 + hover 时 WebGL 3D 实时预览
- **CTA 区**："Let's work together!" 可点击文字
- **Footer**：地址 + 社交链接 + 双邮箱 + Newsletter 订阅表单

### 色彩方案
```css
--color-blue:       #1a2ffb;   /* 品牌强调蓝 */
--color-red:        #ff4c41;   /* 错误/强调红 */
--color-green:      #c1ff00;   /* 成功/高亮霓虹绿 */
--color-purple:     #8832f7;   /* 装饰紫 */
--color-white:      #ffffff;   /* 主背景 */
--color-off-white:  #f0f1fa;   /* 替代分区背景 */
--color-dark-white: #e4e6ef;   /* 菜单按钮背景 */
--color-grey-blue:  #2b2e3a;   /* Pill 按钮填充 */
--color-dark-blue:  #071bdf;   /* 深蓝变体 */
--color-error:      #e90000;   /* 验证错误 */
```
文字：纯黑 (#000) 在白色背景上，全局最大化对比度。

### 字体系统
```
主字体：    Aeonik（自托管，字重 400、500）
等宽：      IBM Plex Mono
品牌等宽：  LusionMono
后备：      Helvetica, Arial, sans-serif

字号层级：
  超大展示：128px，字重 400，行高 1.0，字距 -0.02em
  区域标题：102.4px，字重 400，行高 0.9，字距 -0.02em
  H1：      32px，字重 400，行高 1.1
  H2：      19.2px，字重 400，行高 1.4
  H3：      38px，字重 400，行高 1.15
  导航：    16px，字重 400，大写
  CTA 文字：14px，字重 500，大写
  Footer：  17.5px，字重 400
  Pill 按钮：14px，字重 400
```
全局不使用粗体，保持极致干净。

### 组件规格

**Pill 按钮**
```
深色版：背景 #2b2e3a，文字 #fff，圆角 88px，高 45px，
        字号 14px，内边距 0 16px 0 23px，flex + 居中对齐 + 间距 9px
浅色版：背景 #fff，文字 #000，同尺寸
过渡：color 0.5s, transform 0.4s cubic-bezier(0.4, 0, 0.1, 1)
```
**导航链接**：16px 大写 Aeonik，双重文字结构（如"HOME HOME"）用于 hover 滑动动画
**文字 CTA**：14px 大写，字重 500，纯文字链接，无下划线
**项目卡片**：分类标签行（• 分隔）+ 字距展开项目名 + hover 时 WebGL canvas 叠加
**Newsletter 表单**：文字输入框 + 箭头提交按钮，容器内边距 30px

### 交互与动效
- **滚动**：自定义平滑滚动（非原生），内容通过 JS 控制位移，WebGL 场景响应滚动位置
- **Hover（导航）**：双重文字滑入/滑出 + 颜色过渡（0.5s）
- **Hover（项目）**：WebGL 3D 预览在卡片 canvas 上激活
- **过渡**：全部使用 `cubic-bezier(0.4, 0, 0.1, 1)`（急速减速曲线）。时长：0.1s（快速响应）、0.3s（标准）、0.4s（大元素）
- **菜单**：全屏覆盖（fixed, z-1000, 黑色背景），滑入/滑出
- **音频**：PLAY/MUTE 切换环境音效/视频配乐

### 可访问性要求
- **必须**：移除 `user-scalable=no` — 允许浏览器缩放
- **必须**：添加 `:focus-visible` 焦点环（2px solid #1a2ffb, 2px offset）
- **必须**：使用 `<nav>`、`<main>`、`<section>` 语义化标签
- **必须**：所有纯图标按钮添加 `aria-label`
- **必须**：实现 `prefers-reduced-motion` 禁用 WebGL 动画
- **建议**：为 canvas 内容添加屏幕外文字替代
- **建议**：确保触摸目标 ≥ 44×44px（已基本满足）

### 响应式策略
```
桌面 (>1024px)：完整布局，12 列流体栅格，128px 展示字号
平板 (640-1024px)：适当处用 2 列，排版等比缩放
手机 (<640px)：单列堆叠，汉堡菜单，clamp() 流体字号
```
- 流体间距：`padding-x: max(5vw, 40px)`，`padding-y: clamp(30px, 4vw, 50px)`
- 栅格：12 列，`2vw` 间距，列宽 `calc((100% - 11 * 2vw) / 12)`
- 排版使用 `clamp()` 实现平滑缩放

### 技术栈
```
框架：    Astro
3D：      Three.js (WebGL)
CSS：     Vanilla CSS + CSS 自定义属性
动画：    CSS Transitions + 自定义 JS（无 GSAP）
字体：    自托管 Aeonik、IBM Plex Mono、LusionMono
构建：    Vite（Astro 内置）
```

### 实现优先级
1. 布局骨架：固定头部 + 全视口分区 + 自定义滚动容器
2. 排版：Aeonik 字体加载 + CSS 字号层级 + 流体 clamp()
3. 色彩系统：CSS 自定义属性管理所有颜色
4. WebGL 集成：Three.js 场景搭建 + canvas 管理
5. 组件：Pill 按钮、导航链接、项目卡片、Newsletter 表单
6. 交互：CSS 过渡、自定义平滑滚动、hover 效果
7. 响应式：移动端导航（汉堡 → 覆盖菜单）、流体间距/字号
8. 可访问性：焦点环、语义化 HTML、减弱动画、屏幕阅读器文本
````

---

# Section C — 代码生成指引

## C.1 Vanilla HTML/CSS/JS 实现方案

### 文件结构
单文件 `index.html`，内嵌 CSS 和 JS。无需构建工具。

### 实现要点

**CSS 自定义属性（根变量）**
```css
:root {
  /* Colors */
  --color-blue: #1a2ffb;
  --color-red: #ff4c41;
  --color-green: #c1ff00;
  --color-purple: #8832f7;
  --color-white: #ffffff;
  --color-off-white: #f0f1fa;
  --color-dark-white: #e4e6ef;
  --color-grey-blue: #2b2e3a;
  --color-dark-blue: #071bdf;
  --color-error: #e90000;

  /* Spacing */
  --padding-x: max(5vw, 40px);
  --padding-y: clamp(30px, 4vw, 50px);
  --grid-gap: 2vw;
  --border-radius: 20px;

  /* Typography */
  --font-display: clamp(64px, 10vw, 128px);
  --font-section: clamp(48px, 8vw, 102.4px);
  --font-h1: clamp(24px, 3vw, 32px);
  --font-body: 19.2px;
  --font-nav: 16px;
}

/* Font face */
@font-face {
  font-family: 'Aeonik';
  src: url('fonts/Aeonik-Regular.woff2') format('woff2');
  font-weight: 400;
}
```

**Header 实现**
```css
.header {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 146px;
  z-index: 52;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--padding-x);
  background: transparent;
  transition: background 0.3s;
}
```

**Pill 按钮组件**
```css
.pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  height: 45px;
  padding: 0 16px 0 23px;
  border-radius: 88px;
  font-size: 14px;
  font-family: 'Aeonik', sans-serif;
  border: none;
  cursor: pointer;
  transition: color 0.5s, transform 0.4s cubic-bezier(0.4, 0, 0.1, 1);
}
.pill-btn--dark {
  background: var(--color-grey-blue);
  color: var(--color-white);
}
.pill-btn--light {
  background: var(--color-white);
  color: #000;
}
.pill-btn:hover { transform: scale(1.03); }
```

**导航链接双重文字动效**
```html
<a href="#" class="nav-link">
  <span class="nav-link__text">HOME</span>
  <span class="nav-link__text nav-link__text--clone">HOME</span>
</a>
```
```css
.nav-link {
  position: relative;
  overflow: hidden;
  display: inline-block;
}
.nav-link__text {
  display: block;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.1, 1);
}
.nav-link:hover .nav-link__text { transform: translateY(-100%); }
.nav-link:hover .nav-link__text--clone { transform: translateY(-100%); }
```

**自定义平滑滚动**
```js
// 使用 Intersection Observer + transform 实现
const scrollContainer = document.querySelector('.smooth-scroll');
let currentY = 0;
let targetY = 0;

window.addEventListener('wheel', (e) => {
  e.preventDefault();
  targetY += e.deltaY;
  targetY = Math.max(0, Math.min(targetY, maxScroll));
}, { passive: false });

function animate() {
  currentY += (targetY - currentY) * 0.1; // lerp
  scrollContainer.style.transform = `translateY(${-currentY}px)`;
  requestAnimationFrame(animate);
}
```

**WebGL 集成（Three.js）**
```js
import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
// Mount to hero canvas
document.querySelector('.hero-canvas').appendChild(renderer.domElement);

function render() {
  requestAnimationFrame(render);
  // Update scene based on scroll position
  renderer.render(scene, camera);
}
```

**项目卡片实现**
```html
<div class="project-card">
  <div class="project-card__tags">CONCEPT • WEB • DESIGN • 3D</div>
  <div class="project-card__name">
    <span>O</span><span>r</span><span>y</span><span>z</span><span>o</span>
  </div>
  <canvas class="project-card__preview"></canvas>
</div>
```
```css
.project-card__name span {
  display: inline-block;
  letter-spacing: 0.3em;
}
.project-card__preview {
  opacity: 0;
  transition: opacity 0.4s;
}
.project-card:hover .project-card__preview {
  opacity: 1;
}
```

### 性能注意事项
- Canvas 使用 `alpha: true` 保留透明背景，叠加在白色页面上
- `devicePixelRatio` 上限设为 2，防止高 DPI 设备性能问题
- Intersection Observer 用于懒激活项目卡片的 WebGL 场景
- 所有动画使用 `transform` + `opacity`（GPU 合成层）

---

## C.2 React + Tailwind CSS 实现方案

### 项目结构
```
src/
├── components/
│   ├── Header.jsx
│   │   ├── NavLink.jsx
│   │   ├── PillButton.jsx
│   │   └── MenuOverlay.jsx
│   ├── Hero.jsx
│   │   └── HeroCanvas.jsx       # Three.js 场景
│   ├── FeaturedWork.jsx
│   │   └── ProjectCard.jsx
│   │       └── ProjectCanvas.jsx # WebGL 预览
│   ├── CTASection.jsx
│   ├── Footer.jsx
│   │   └── NewsletterForm.jsx
│   └── SmoothScroll.jsx         # 自定义滚动容器
├── hooks/
│   ├── useSmoothScroll.js
│   ├── useWebGL.js
│   └── useReducedMotion.js
├── styles/
│   └── globals.css
└── App.jsx
```

### Tailwind 配置扩展
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        blue: { brand: '#1a2ffb', dark: '#071bdf' },
        red: { brand: '#ff4c41', error: '#e90000' },
        green: { brand: '#c1ff00' },
        purple: { brand: '#8832f7' },
        grey: { blue: '#2b2e3a' },
        offwhite: { DEFAULT: '#f0f1fa', dark: '#e4e6ef' },
      },
      fontFamily: {
        aeonik: ['Aeonik', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      fontSize: {
        'display': ['clamp(64px, 10vw, 128px)', { lineHeight: '1.0', letterSpacing: '-0.02em' }],
        'section': ['clamp(48px, 8vw, 102.4px)', { lineHeight: '0.9', letterSpacing: '-0.02em' }],
        'h3': ['38px', { lineHeight: '1.15' }],
        'body': ['19.2px', { lineHeight: '1.4' }],
      },
      spacing: {
        'header': '146px',
        'section': 'clamp(30px, 4vw, 50px)',
        'fluid-x': 'max(5vw, 40px)',
      },
      borderRadius: {
        'pill': '88px',
        'global': '20px',
      },
      transitionTimingFunction: {
        'lusion': 'cubic-bezier(0.4, 0, 0.1, 1)',
      },
      zIndex: {
        'header': '52',
        'menu': '1000',
      },
    },
  },
};
```

### 关键组件示例

**PillButton.jsx**
```jsx
export function PillButton({ variant = 'dark', children, icon }) {
  return (
    <button
      className={`
        inline-flex items-center gap-2 h-[45px] px-4 rounded-pill
        text-sm font-aeonik
        transition-[color,transform] duration-[400ms,500ms] ease-lusion
        hover:scale-[1.03]
        ${variant === 'dark'
          ? 'bg-grey-blue text-white'
          : 'bg-white text-black'
        }
      `}
    >
      {icon && <span className="w-4 h-4">{icon}</span>}
      {children}
    </button>
  );
}
```

**NavLink.jsx**
```jsx
export function NavLink({ href, children }) {
  return (
    <a
      href={href}
      className="relative overflow-hidden inline-block font-aeonik text-nav uppercase
                 transition-[color] duration-500 ease-lusion hover:text-blue-brand"
    >
      <span className="block transition-transform duration-400 ease-lusion
                       group-hover:-translate-y-full">
        {children}
      </span>
      <span className="absolute top-full left-0 transition-transform duration-400 ease-lusion
                       group-hover:-translate-y-full">
        {children}
      </span>
    </a>
  );
}
```

**useSmoothScroll.js**
```js
import { useEffect, useRef } from 'react';

export function useSmoothScroll() {
  const containerRef = useRef(null);
  const currentY = useRef(0);
  const targetY = useRef(0);

  useEffect(() => {
    const container = containerRef.current;
    const maxScroll = container.scrollHeight - window.innerHeight;

    const onWheel = (e) => {
      e.preventDefault();
      targetY.current = Math.max(0, Math.min(targetY.current + e.deltaY, maxScroll));
    };

    window.addEventListener('wheel', onWheel, { passive: false });

    let rafId;
    const animate = () => {
      currentY.current += (targetY.current - currentY.current) * 0.1;
      container.style.transform = `translate3d(0, ${-currentY.current}px, 0)`;
      rafId = requestAnimationFrame(animate);
    };
    rafId = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('wheel', onWheel);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return containerRef;
}
```

**HeroCanvas.jsx（Three.js 集成）**
```jsx
import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export function HeroCanvas({ scrollY }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Add 3D objects...

    const animate = () => {
      requestAnimationFrame(animate);
      // Tie to scroll
      camera.position.y = -scrollY.current * 0.002;
      renderer.render(scene, camera);
    };
    animate();

    return () => renderer.dispose();
  }, []);

  return <div ref={mountRef} className="fixed inset-0 -z-10" />;
}
```

### 可访问性增强
```jsx
// 焦点环样式（globals.css）
@layer base {
  *:focus-visible {
    @apply outline-2 outline-offset-2 outline-blue-brand;
  }
}

// 减弱动画
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

// Canvas 替代文本
<div role="img" aria-label="3D interactive visualization of our creative work">
  <canvas aria-hidden="true" />
</div>
```

---

## 附录：设计数据速查表

| 维度 | 关键值 |
|---|---|
| 主字体 | Aeonik (400, 500) |
| 展示字号 | 128px / -2.56px 字距 |
| 主背景 | #FFFFFF |
| 文字色 | #000000 |
| Pill 按钮高 | 45px |
| Pill 圆角 | 88px |
| Header 高 | 146px |
| Header z-index | 52 |
| 菜单 z-index | 1000 |
| 栅格 | 12 列 / 2vw 间距 |
| 内边距 X | max(5vw, 40px) |
| 内边距 Y | clamp(30px, 4vw, 50px) |
| 过渡缓动 | cubic-bezier(0.4, 0, 0.1, 1) |
| 过渡时长 | 0.1s / 0.3s / 0.4s / 0.5s |
| Canvas 数量 | 3 |
| SVG 数量 | 41 |
| 框架 | Astro + Three.js |
| 滚动方式 | 自定义平滑（非原生） |
