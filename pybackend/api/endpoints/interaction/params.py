"""
@Created on: 2025/01/18 10:00
@Author: DreamFly Team
@Des: 交互管理 - 请求参数
"""

from pydantic import BaseModel, Field
from typing import Optional


class RecordInteractionParams(BaseModel):
    """记录交互参数"""
    user_id: str = Field(..., description="用户ID")
    mind_name: str = Field(..., description="意识体名称")
    user_message: str = Field(..., description="用户消息")
    ai_response: str = Field(..., description="AI回复")
    tokens_used: Optional[int] = Field(0, description="使用的token数量")


class UpdateInteractionCountParams(BaseModel):
    """更新交互次数参数"""
    user_id: str = Field(..., description="用户ID")
    mind_name: str = Field(..., description="意识体名称")
    increment: Optional[int] = Field(1, description="增加的次数")
