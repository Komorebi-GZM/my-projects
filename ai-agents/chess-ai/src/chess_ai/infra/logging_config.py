"""
日志配置 - 分级日志系统，支持文件轮转和控制台输出
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging(
    log_level: int | str = logging.INFO,
    log_file: str | Path = "./logs/chess_ai.log",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    format_string: str | None = None,
    date_format: str | None = None,
) -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别，如 logging.INFO 或 "INFO"
        log_file: 日志文件路径
        max_bytes: 单个日志文件最大字节数，触发轮转
        backup_count: 保留的备份文件数量
        format_string: 日志格式字符串，None 使用默认格式
        date_format: 日期格式字符串，None 使用默认格式
    """
    # 转换日志级别
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    # 设置默认格式
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(format_string, date_format)

    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 清除现有处理器（避免重复添加）
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（带轮转）
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 设置第三方库的日志级别以减少噪音
    logging.getLogger("langgraph").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    # 记录启动信息
    logger.info(f"日志系统初始化完成 - 级别: {logging.getLevelName(log_level)}, 文件: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 记录器名称，通常使用 __name__

    Returns:
        配置好的日志记录器实例
    """
    return logging.getLogger(name)


# 便捷函数，用于快速获取日志记录器
def logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷别名"""
    return get_logger(name)
