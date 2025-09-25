"""
@Created on: 2025/01/18 10:00
@Author: DreamFly Team
@Des: 交互管理 - 响应模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InteractionRecordSchema(BaseModel):
    """交互记录模式"""
    id: str
    user_id: str
    mind_name: str
    user_message: str
    ai_response: str
    tokens_used: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class InteractionStatsSchema(BaseModel):
    """交互统计模式"""
    total_interactions: int
    total_tokens: int
    last_interaction: Optional[datetime] = None
