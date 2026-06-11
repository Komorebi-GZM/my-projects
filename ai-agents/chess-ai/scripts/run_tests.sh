#!/bin/bash
# ============================================
# 中国象棋AI对弈工具 - 测试运行脚本
# ============================================
# 使用方法:
#   chmod +x scripts/run_tests.sh
#   ./scripts/run_tests.sh
#
# 可选参数:
#   ./scripts/run_tests.sh --cov        # 生成覆盖率报告
#   ./scripts/run_tests.sh --verbose    # 详细输出
#   ./scripts/run_tests.sh --board      # 仅运行棋盘引擎测试
#   ./scripts/run_tests.sh --gui        # 仅运行 GUI 测试
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo -e "${BLUE}激活虚拟环境...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}警告: 未找到虚拟环境，尝试使用系统 Python${NC}"
    fi
fi

# 解析参数
RUN_COV=false
VERBOSE=""
TEST_PATH="tests/"

while [[ $# -gt 0 ]]; do
    case $1 in
        --cov|-c)
            RUN_COV=true
            shift
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --board|-b)
            TEST_PATH="tests/unit/test_board.py"
            shift
            ;;
        --gui|-g)
            TEST_PATH="tests/unit/test_gui.py"
            shift
            ;;
        --agent|-a)
            TEST_PATH="tests/unit/test_agent.py"
            shift
            ;;
        --llm|-l)
            TEST_PATH="tests/unit/test_llm.py"
            shift
            ;;
        --integration|-i)
            TEST_PATH="tests/integration/"
            shift
            ;;
        --help|-h)
            echo "用法: ./scripts/run_tests.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --cov, -c        生成覆盖率报告"
            echo "  --verbose, -v    详细输出"
            echo "  --board, -b      仅运行棋盘引擎测试"
            echo "  --gui, -g        仅运行 GUI 测试"
            echo "  --agent, -a      仅运行 Agent 测试"
            echo "  --llm, -l        仅运行 LLM 测试"
            echo "  --integration, -i 仅运行集成测试"
            echo "  --help, -h       显示此帮助"
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  中国象棋AI对弈工具 - 测试运行${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}错误: 未找到 pytest${NC}"
    echo "请先运行: pip install pytest pytest-cov"
    exit 1
fi

# 构建 pytest 命令
PYTEST_CMD="pytest $TEST_PATH $VERBOSE"

if [ "$RUN_COV" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
    echo -e "${YELLOW}将生成覆盖率报告${NC}"
fi

echo -e "${BLUE}运行命令: $PYTEST_CMD${NC}"
echo ""

# 运行测试
if eval "$PYTEST_CMD"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  所有测试通过！${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    if [ "$RUN_COV" = true ]; then
        echo ""
        echo -e "${BLUE}覆盖率报告已生成:${NC}"
        echo -e "  HTML 报告: ${YELLOW}htmlcov/index.html${NC}"
        echo -e "  可用浏览器打开查看"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  测试失败！${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
