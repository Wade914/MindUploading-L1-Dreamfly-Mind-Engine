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
    DATABASE_DIR: str = "./database"

    # 目录配置
    UPLOAD_DIR: str = "./uploads"
    MINDS_DIR: str = "./database/minds"
    LOG_DIR: str = "./logs"

    # 上传子目录配置
    UPLOAD_THOUGHT_DIR: str = "thought"
    UPLOAD_VOICE_DIR: str = "voice"
    UPLOAD_IMAGE_DIR: str = "image"
    UPLOAD_VIDEO_DIR: str = "video"
    UPLOAD_DOCUMENT_DIR: str = "documents"

    # 文件大小限制配置
    MAX_FILE_SIZE: int = 20971520  # 20MB
    MAX_THOUGHT_SIZE: int = 5242880  # 5MB
    MAX_VOICE_SIZE: int = 10485760  # 10MB
    MAX_IMAGE_SIZE: int = 20971520  # 20MB
    MAX_VIDEO_SIZE: int = 52428800  # 50MB
    MAX_DOCUMENT_SIZE: int = 10485760  # 10MB

    # 允许的文件类型
    ALLOWED_THOUGHT_TYPES: list = ['.txt', '.md', '.doc', '.docx', '.pdf']
    ALLOWED_VOICE_TYPES: list = ['.mp3', '.wav', '.m4a', '.aac']
    ALLOWED_IMAGE_TYPES: list = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    ALLOWED_VIDEO_TYPES: list = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
    ALLOWED_DOCUMENT_TYPES: list = ['.txt', '.pdf', '.doc', '.docx', '.md']

    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # AI模型配置
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_BASE_URL: str = ""
    DEEPSEEK_MODEL: str = ""
    COSYVOICE_MODEL: str = ""

    # 扣子智能体配置
    COZE_API_TOKEN: str = ""
    COZE_API_BASE_URL: str = "https://api.coze.cn"
    COZE_BOT_ID: str = ""

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

    # RAG配置
    CHROMA_DB_PATH: str = "./chroma_db"  # ChromaDB数据存储路径
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"  # 中文embedding模型
    EMBEDDING_DIMENSION: int = 512  # bge-small-zh-v1.5的维度
    RAG_TOP_K: int = 3  # 默认检索结果数量
    RAG_ENABLED: bool = True  # 是否启用RAG功能



# 全局配置实例
settings = Settings()