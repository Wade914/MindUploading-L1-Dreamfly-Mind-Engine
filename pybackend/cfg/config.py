"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 项目配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """项目配置 - 所有配置都从环境变量读取"""
    # 使用 pydantic-settings v2 的配置方式，明确指定 .env 路径
    model_config = SettingsConfigDict(
        env_file=str((Path(__file__).resolve().parent.parent / ".env")),
        case_sensitive=True,
        extra="ignore"
    )

    # 应用配置
    APP_NAME: str = "DreamFly API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = ""

    # 文件上传配置
    UPLOAD_DIR: str = ""
    MAX_FILE_SIZE: int = 20971520  # 20MB

    # 允许的文件类型
    ALLOWED_THOUGHT_TYPES: list = ['.txt', '.md', '.doc', '.docx', '.pdf']
    ALLOWED_VOICE_TYPES: list = ['.mp3', '.wav', '.m4a', '.aac']
    ALLOWED_IMAGE_TYPES: list = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # 意识体数据目录
    MINDS_DIR: str = ""

    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # AI模型配置
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_BASE_URL: str = ""
    DEEPSEEK_MODEL: str = ""
    COSYVOICE_MODEL: str = ""

    # AI请求配置
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1024
    AI_STREAM: bool = True

    # JWT认证配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    



# 全局配置实例
settings = Settings()