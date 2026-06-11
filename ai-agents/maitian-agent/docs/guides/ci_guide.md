# 麦田智囊 CI 使用指南

## 概述

项目使用 GitHub Actions 实现自动化 CI 流水线，每次推送或 PR 到 `main`/`develop` 分支时自动触发。

## 流水线结构

CI 包含 3 个并行 Job：

| Job | 功能 | 工具 | 失败影响 |
|-----|------|------|---------|
| **lint** | 代码风格检查 | ruff check + ruff format | 阻止合并 |
| **test** | 测试 + 覆盖率 | pytest + pytest-cov | 阻止合并 |
| **type-check** | 静态类型检查 | mypy | 阻止合并 |

## 触发条件

- **push**: `main`、`develop` 分支
- **pull_request**: 目标为 `main`、`develop` 的 PR

## 本地复现

### 安装开发依赖

```bash
pip install -r requirements.txt
```

### Lint 检查

```bash
# 代码风格检查
ruff check maitian_agent/

# 格式检查（不自动修复）
ruff format --check maitian_agent/

# 自动修复格式
ruff format maitian_agent/
```

### 测试 + 覆盖率

```bash
# 运行全部测试并生成覆盖率报告
python -m pytest tests/ \
  --cov=maitian_agent \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  -v --tb=short

# 仅运行测试（不含覆盖率）
python -m pytest tests/ -v --tb=short
```

### 类型检查

```bash
mypy maitian_agent/ --ignore-missing-imports
```

## 覆盖率配置

覆盖率配置位于 `pyproject.toml`：

```toml
[tool.coverage.run]
source = ["maitian_agent"]
omit = [
    "maitian_agent/**/__init__.py",
    "maitian_agent/cli.py",
    "maitian_agent/frontend/*",
]

[tool.coverage.report]
fail_under = 80
```

- **覆盖率阈值**: 80%（低于此值 CI 失败）
- **排除项**: `__init__.py`、CLI 入口、前端模块
- **报告格式**: 终端输出 + XML（上传为 Artifact）

## Ruff 规则配置

Ruff 配置位于 `pyproject.toml`：

```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]
ignore = ["E501", "B008", "SIM108"]
```

启用的规则集：
- **E/W**: pycodestyle 错误/警告
- **F**: pyflakes
- **I**: isort 导入排序
- **UP**: pyupgrade 自动升级语法
- **B**: flake8-bugbear 常见 bug 检测
- **SIM**: flake8-simplify 代码简化

## PR 合并保护

建议在 GitHub 仓库设置中启用分支保护规则：

1. 进入 **Settings → Branches → Branch protection rules**
2. 选择 `main` 分支
3. 勾选 **Require status checks to pass before merging**
4. 添加以下检查：
   - `Lint (ruff)`
   - `Test (pytest + coverage)`
   - `Type Check (mypy)`
5. 可选：勾选 **Require branches to be up to date before merging**

## 常见问题

### Q: CI 中 ruff 报错如何修复？

```bash
# 查看具体错误
ruff check maitian_agent/ --output-format=full

# 自动修复可修复的问题
ruff check maitian_agent/ --fix
```

### Q: 覆盖率不达标怎么办？

```bash
# 生成 HTML 报告查看未覆盖的行
python -m pytest tests/ --cov=maitian_agent --cov-report=html:htmlcov
# 打开 htmlcov/index.html 查看详情
```

### Q: mypy 报错太多怎么办？

当前 mypy 配置使用 `--ignore-missing-imports` 忽略第三方库类型。项目中的类型错误主要集中在非核心模块（vectorstore、knowledge_base 等），可逐步修复。
