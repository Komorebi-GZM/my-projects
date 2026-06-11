"""Flask 应用配置。"""

import os


class Config:
    """基础配置。"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")


class DevelopmentConfig(Config):
    """开发环境配置。"""
    DEBUG = True
    DB_MODE = "local"  # local / production


class TestingConfig(Config):
    """测试环境配置。"""
    TESTING = True
    DB_MODE = "memory"  # 使用内存数据库


class ProductionConfig(Config):
    """生产环境配置。"""
    DB_MODE = "production"  # CloudBase NoSQL


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
