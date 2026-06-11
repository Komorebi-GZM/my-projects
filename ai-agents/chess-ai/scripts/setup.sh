#!/bin/bash
# ============================================
# 中国象棋AI对弈工具 - 环境初始化脚本
# ============================================
# 使用方法:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
#
# 功能:
#   - 检查 Python 版本
#   - 创建虚拟环境
#   - 安装依赖
#   - 创建必要的目录
#   - 复制配置文件模板
# ============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  中国象棋AI对弈工具 - 环境初始化${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==================== 检查 Python 版本 ====================
echo -e "${YELLOW}[1/6] 检查 Python 版本...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3 命令${NC}"
    echo "请先安装 Python 3.12+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}错误: 需要 Python $REQUIRED_VERSION+，当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 版本检查通过: $PYTHON_VERSION${NC}"

# ==================== 创建虚拟环境 ====================
echo ""
echo -e "${YELLOW}[2/6] 创建虚拟环境...${NC}"

if [ -d "venv" ]; then
    echo -e "${YELLOW}虚拟环境已存在，跳过创建${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source venv/bin/activate

# ==================== 升级 pip ====================
echo ""
echo -e "${YELLOW}[3/6] 升级 pip...${NC}"
pip install --upgrade pip setuptools wheel

# ==================== 安装依赖 ====================
echo ""
echo -e "${YELLOW}[4/6] 安装项目依赖...${NC}"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi

# ==================== 创建目录结构 ====================
echo ""
echo -e "${YELLOW}[5/6] 创建项目目录...${NC}"

directories=(
    "data"
    "logs"
    "saves"
    "src/board"
    "src/gui"
    "src/agent"
    "src/llm"
    "src/infra"
    "tests/unit"
    "tests/integration"
    "tests/fixtures"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo -e "  ${BLUE}创建: $dir${NC}"
done

echo -e "${GREEN}✓ 目录结构创建完成${NC}"

# ==================== 复制配置文件 ====================
echo ""
echo -e "${YELLOW}[6/6] 初始化配置文件...${NC}"

if [ -f "config/.env.example" ]; then
    if [ ! -f "config/.env" ]; then
        cp config/.env.example config/.env
        echo -e "${GREEN}✓ 已创建 config/.env${NC}"
        echo -e "${YELLOW}  提示: 请编辑 config/.env 文件，填入你的 API Key${NC}"
    else
        echo -e "${YELLOW}  config/.env 已存在，跳过${NC}"
    fi
else
    echo -e "${RED}  警告: 未找到 config/.env.example${NC}"
fi

# ==================== 完成提示 ====================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  环境初始化完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}使用方法:${NC}"
echo ""
echo -e "  1. 激活虚拟环境:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "  2. 配置 API Key:"
echo -e "     ${YELLOW}编辑 config/.env 文件${NC}"
echo ""
echo -e "  3. 启动游戏:"
echo -e "     ${YELLOW}python main.py${NC}"
echo ""
echo -e "  4. 调试模式启动:"
echo -e "     ${YELLOW}python main.py --debug${NC}"
echo ""
echo -e "  5. 模拟 LLM 模式（无需 API Key）:"
echo -e "     ${YELLOW}python main.py --mock-llm${NC}"
echo ""
echo -e "${BLUE}其他命令:${NC}"
echo ""
echo -e "  运行测试: ${YELLOW}./scripts/run_tests.sh${NC}"
echo -e "  代码格式化: ${YELLOW}black src/ tests/${NC}"
echo -e "  代码检查: ${YELLOW}ruff check src/ tests/${NC}"
echo ""
