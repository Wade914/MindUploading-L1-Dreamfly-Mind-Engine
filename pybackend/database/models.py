"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 数据库基础模型
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, UniqueConstraint
from sqlalchemy.sql import func
from database.session import Base
import uuid


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    birth = Column(String(20), comment="生日")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    password_salt = Column(String(32), nullable=False, comment="密码盐值")
    

class Mind(BaseModel):
    """意识体模型"""
    __tablename__ = "minds"

    user_id = Column(String(36), nullable=False, comment="用户ID")
    name = Column(String(100), nullable=False, comment="意识体名称")
    birth = Column(String(20), comment="生日")
    type = Column(String(50), default="MindCopy", comment="类型")
    protocol = Column(String(50), default="MCP-v1", comment="协议")
    blockchain = Column(String(50), default="ethereum", comment="区块链")
    filename = Column(String(255), nullable=False, comment="文件名")
    content = Column(Text, comment="意识体内容")
    voice_id = Column(String(200), comment="SiliconFlow音色ID")

    # 添加唯一约束，防止同一用户创建同名意识体
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_mind_name'),
    )


class Upload(BaseModel):
    """上传记录模型"""
    __tablename__ = "uploads"
    
    user_id = Column(String(36), nullable=False, comment="用户ID")
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    saved_filename = Column(String(255), nullable=False, comment="保存的文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_type = Column(String(50), comment="文件类型")
    file_size = Column(Integer, comment="文件大小")
    upload_type = Column(String(50), comment="上传类型：thought/voice/image")