#!/usr/bin/env python3
"""
中国象棋AI对弈工具 - 程序入口

基于 Python 3.12 + LangGraph + Pygame 的桌面端中国象棋人机对弈工具。
支持多 LLM 模型（DeepSeek、GPT-4o、本地 Ollama）智能走子。

使用方法:
    python main.py              # 正常启动
    python main.py --debug      # 调试模式启动
    python main.py --mock-llm   # 模拟LLM模式（无需API Key）
    python main.py --config path/to/config.yaml  # 指定配置文件

作者: Chess AI Team
版本: 0.1.2
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from chess_ai.gui import ChessRenderer, EventLoop, GameController, GUIConfig
from chess_ai.gui.theme import ThemeManager
from chess_ai.infra import ConfigManager

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="chess_ai",
        description="中国象棋AI对弈工具 - 基于 LangGraph + Pygame",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 正常启动游戏
  python main.py --debug            # 调试模式（显示详细日志）
  python main.py --mock-llm         # 模拟 LLM 模式（无需 API Key）
  python main.py --config custom_config.yaml  # 使用自定义配置
        """,
    )

    parser.add_argument(
        "--config", "-c", type=str, default="config/config.yaml", help="配置文件路径 (默认: config/config.yaml)"
    )

    parser.add_argument("--debug", "-d", action="store_true", help="启用调试模式（显示详细日志和调试信息）")

    parser.add_argument(
        "--mock-llm", "-m", action="store_true", help="模拟 LLM 模式（使用随机走子，无需 API Key，用于开发测试）"
    )

    parser.add_argument("--version", "-v", action="version", version="%(prog)s 0.1.2")

    return parser.parse_args()


def setup_logging(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_dir / "chess_ai.log", encoding="utf-8")],
    )

    logging.getLogger("langgraph").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def check_environment() -> bool:
    logger = logging.getLogger(__name__)

    logger.info(f"Python 版本: {sys.version}")

    required_dirs = ["assets", "config", "docs"]
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            logger.warning(f"目录不存在: {dir_name}")

    assets_dir = PROJECT_ROOT / "assets"
    if assets_dir.exists():
        pieces_dir = assets_dir / "images" / "pieces"
        if pieces_dir.exists():
            piece_count = len(list(pieces_dir.glob("*.jpg")))
            logger.info(f"棋子图片数量: {piece_count}")

    return True


def create_directories() -> None:
    dirs_to_create = [
        "data",
        "logs",
        "saves",
    ]

    for dir_name in dirs_to_create:
        dir_path = PROJECT_ROOT / dir_name
        dir_path.mkdir(exist_ok=True)


def main() -> int:
    args = parse_arguments()

    # 加载 .env 文件到环境变量
    env_path = PROJECT_ROOT / "config" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logging.getLogger(__name__).info(f"已加载环境变量: {env_path}")

    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)

    logger.info("=" * 50)
    logger.info("中国象棋AI对弈工具启动")
    logger.info(f"配置文件: {args.config}")
    logger.info(f"调试模式: {args.debug}")
    logger.info(f"模拟 LLM: {args.mock_llm}")
    logger.info("=" * 50)

    if not check_environment():
        logger.error("环境检查失败，程序退出")
        return 1

    create_directories()

    try:
        config = ConfigManager(args.config)

        if args.mock_llm:
            os.environ["CHESS_LLM_MOCK"] = "true"
            logger.info("模拟 LLM 模式已启用，将使用随机合法走子")

        gui_config = GUIConfig.from_infra_config(config)
        theme = ThemeManager.get_theme("classic")

        renderer = ChessRenderer(gui_config, theme)
        controller = GameController(gui_config, renderer, theme)

        event_loop = EventLoop(gui_config, controller, renderer)

        logger.info("初始化完成，启动游戏界面...")

        event_loop.run()

        return 0

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.exception(f"程序运行出错: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
