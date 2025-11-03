"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 数据库配置
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# 数据库配置优先顺序：.env -> 环境变量 -> 默认(dreamfly.db)
from cfg.config import settings

_default_url = "sqlite+aiosqlite:///./dreamfly.db"
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL") or _default_url

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发环境下显示SQL语句
    future=True
)

# 创建异步会话
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()

# 数据库依赖注入
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()