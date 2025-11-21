"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 意识体管理 - 响应模式
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MindSchema(BaseModel):
    """意识体信息模式"""
    id: str
    user_id: str
    name: str
    birth: Optional[str] = None
    type: str
    protocol: str
    blockchain: str
    filename: str
    voice_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MindDetailSchema(MindSchema):
    """意识体详细信息模式（包含内容）"""
    content: Optional[str] = None


class CreateMindResponseSchema(BaseModel):
    """创建意识体响应模式"""
    mind_id: str
    filename: str
    created: datetime


class MindListResponseSchema(BaseModel):
    """意识体列表响应模式"""
    items: List[MindSchema]
    total: int
    page: int
    page_size: int
    
    
class MindContentResponseSchema(BaseModel):
    """意识体内容响应模式"""
    filename: str
    content: str