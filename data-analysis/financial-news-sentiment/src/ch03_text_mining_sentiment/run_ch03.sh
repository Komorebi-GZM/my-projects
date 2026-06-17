#!/usr/bin/env bash
# ============================================================
# ch03 文本挖掘与情感分析 — 一键启动脚本
# ============================================================
# 用法:
#   bash run_ch03.sh              # 完整执行（安装依赖 + 训练 + 验证）
#   bash run_ch03.sh --skip-deps  # 跳过依赖安装，直接训练
#   bash run_ch03.sh --test-only  # 仅运行产物验证测试
#
# 环境要求: Python 3.10+, pip
# 预计耗时: GPU 约 30 分钟 | CPU 约 2-4 小时
# ============================================================

set -euo pipefail

# ---- 颜色定义 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---- 项目根目录（自动检测） ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# ---- 可选参数 ----
SKIP_DEPS=false
TEST_ONLY=false
for arg in "$@"; do
    case $arg in
        --skip-deps)  SKIP_DEPS=true ;;
        --test-only)  TEST_ONLY=true ;;
        --help|-h)
            echo "用法: bash run_ch03.sh [--skip-deps] [--test-only]"
            echo ""
            echo "  --skip-deps   跳过依赖安装，直接执行训练"
            echo "  --test-only   仅运行产物验证测试"
            echo "  --help        显示帮助信息"
            exit 0
            ;;
        *)
            echo -e "${RED}未知参数: $arg${NC}"
            exit 1
            ;;
    esac
done

# ---- 工具函数 ----
info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

separator() {
    echo ""
    echo "============================================================"
    echo "  $*"
    echo "============================================================"
}

# ============================================================
# Phase 0: 环境检查
# ============================================================
check_environment() {
    separator "Phase 0: 环境检查"

    # Python 版本
    info "检查 Python 版本..."
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ne 3 ] || [ "$PYTHON_MINOR" -lt 8 ]; then
        error "Python 版本需要 >= 3.8，当前: $PYTHON_VERSION"
    fi
    success "Python 版本: $PYTHON_VERSION"

    # pip
    info "检查 pip..."
    pip3 --version > /dev/null 2>&1 || error "pip3 未安装"
    success "pip 可用"

    # GPU 检测
    info "检测 GPU..."
    GPU_AVAILABLE=false
    if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        GPU_NAME=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
        GPU_AVAILABLE=true
        success "GPU 可用: $GPU_NAME"
        info "将使用 GPU 加速 (batch_size=32)"
    else
        warn "GPU 不可用，将使用 CPU (batch_size=8)"
        warn "CPU 模式预计耗时 2-4 小时"
        info "如需加速，可设置环境变量: CH03_SAMPLE_FRACTION=0.5"
    fi

    # 磁盘空间
    info "检查磁盘空间..."
    FREE_SPACE=$(df -BG "$PROJECT_ROOT" | awk 'NR==2{print $4}' | tr -d 'G')
    if [ "$FREE_SPACE" -lt 10 ]; then
        error "磁盘空间不足 10GB (剩余 ${FREE_SPACE}GB)，BERTopic embedding 缓存约需 2-3GB"
    fi
    success "磁盘空间: ${FREE_SPACE}GB 可用"

    # 输入数据检查
    info "检查输入数据..."
    INPUT_FILE="$PROJECT_ROOT/outputs/ch01_data_preprocessing/ch01_cleaned_data.csv"
    if [ ! -f "$INPUT_FILE" ]; then
        error "输入数据不存在: $INPUT_FILE"
    fi
    ROW_COUNT=$(wc -l < "$INPUT_FILE")
    success "输入数据: $INPUT_FILE (${ROW_COUNT} 行)"
}

# ============================================================
# Phase 1: 依赖安装
# ============================================================
install_dependencies() {
    separator "Phase 1: 安装依赖"

    info "升级 pip..."
    pip3 install --upgrade pip --quiet 2>&1 | tail -1

    info "安装核心依赖..."
    pip3 install \
        torch torchvision \
        transformers \
        pandas numpy \
        matplotlib seaborn pillow \
        tqdm \
        spacy \
        bertopic \
        gensim \
        --quiet 2>&1 | tail -3

    success "Python 依赖安装完成"

    info "下载 spaCy 英文模型..."
    python3 -m spacy download en_core_web_sm --quiet 2>&1 | tail -2
    success "spaCy 模型下载完成"

    info "验证关键依赖..."
    python3 -c "
import torch; print(f'  torch: {torch.__version__}')
import transformers; print(f'  transformers: {transformers.__version__}')
import spacy; print(f'  spacy: OK')
import bertopic; print(f'  bertopic: {bertopic.__version__}')
import gensim; print(f'  gensim: {gensim.__version__}')
print('  全部依赖验证通过')
" || error "依赖验证失败"
    success "全部依赖就绪"
}

# ============================================================
# Phase 2: 执行训练
# ============================================================
run_training() {
    separator "Phase 2: 执行 ch03 训练"

    OUTPUT_DIR="$PROJECT_ROOT/outputs/ch03_text_mining_sentiment"
    mkdir -p "$OUTPUT_DIR"

    info "开始训练..."
    info "  - 数据: 139,919 条新闻 (100% 全量)"
    info "  - 模型: FinBERT (ProsusAI/finbert)"
    info "  - 主题: BERTopic + LDA"
    echo ""

    START_TIME=$(date +%s)

    # 设置环境变量
    export TMPDIR="${TMPDIR:-/tmp}"
    export HF_ENDPOINT="${HF_ENDPOINT:-https://huggingface.co}"

    # 如果网络不通，自动切换镜像
    if ! timeout 10 python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download('ProsusAI/finbert', 'config.json')" 2>/dev/null; then
        warn "HuggingFace 直连超时，切换到镜像站..."
        export HF_ENDPOINT="https://hf-mirror.com"
    fi

    python3 "$PROJECT_ROOT/src/ch03_text_mining_sentiment/sentiment.py"

    END_TIME=$(date +%s)
    ELAPSED=$(( END_TIME - START_TIME ))
    MINUTES=$(( ELAPSED / 60 ))
    SECONDS=$(( ELAPSED % 60 ))

    echo ""
    success "训练完成! 耗时: ${MINUTES}分${SECONDS}秒"
}

# ============================================================
# Phase 3: 产物验证
# ============================================================
run_validation() {
    separator "Phase 3: 产物验证"

    info "运行测试脚本..."
    echo ""

    python3 "$PROJECT_ROOT/src/ch03_text_mining_sentiment/test_ch03.py"

    echo ""
    OUTPUT_DIR="$PROJECT_ROOT/outputs/ch03_text_mining_sentiment"
    FILE_COUNT=$(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "ch03_*" | wc -l)
    info "产物目录: $OUTPUT_DIR"
    info "产物数量: $FILE_COUNT 个文件"

    echo ""
    info "产物清单:"
    echo "  ┌─────────────────────────────────────────────────┐"
    echo "  │ 序号 │ 文件名                          │ 格式  │"
    echo "  ├──────┼──────────────────────────────────┼───────┤"

    FILES=(
        "ch03_sentiment_labels.csv:CSV"
        "ch03_topic_model_results.csv:CSV"
        "ch03_sentiment_distribution.png:PNG"
        "ch03_sentiment_by_category.png:PNG"
        "ch03_sentiment_timeline.png:PNG"
        "ch03_event_window_sentiment.png:PNG"
        "ch03_topic_visualization.html:HTML"
        "ch03_topic_timeline_heatmap.png:PNG"
        "ch03_sentiment_analysis_report.md:MD"
        "ch03_topic_analysis_report.md:MD"
    )

    IDX=1
    for ITEM in "${FILES[@]}"; do
        FNAME="${ITEM%%:*}"
        FTYPE="${ITEM##*:}"
        if [ -f "$OUTPUT_DIR/$FNAME" ]; then
            SIZE=$(du -h "$OUTPUT_DIR/$FNAME" | cut -f1)
            echo "  │  ${IDX}.  │ ${FNAME} │ ${FTYPE}  ${SIZE} │"
        else
            echo "  │  ${IDX}.  │ ${FNAME} │ ${FTYPE}  缺失 │"
        fi
        IDX=$((IDX + 1))
    done
    echo "  └──────┴──────────────────────────────────┴───────┘"
}

# ============================================================
# Main
# ============================================================
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║   ch03 文本挖掘与情感分析 — 一键启动               ║"
    echo "║   Batch-2 | Prompt-03 | TDD Workflow               ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""

    # Phase 0: 环境检查（始终执行）
    check_environment

    if [ "$TEST_ONLY" = true ]; then
        run_validation
        exit 0
    fi

    # Phase 1: 依赖安装
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    else
        info "跳过依赖安装 (--skip-deps)"
    fi

    # Phase 2: 训练
    run_training

    # Phase 3: 验证
    run_validation

    echo ""
    separator "全部完成!"
    echo ""
    success "产物输出目录: outputs/ch03_text_mining_sentiment/"
    success "下一步: 执行 Batch-3 (Prompt-04: 特征工程)"
    echo ""
}

main "$@"
