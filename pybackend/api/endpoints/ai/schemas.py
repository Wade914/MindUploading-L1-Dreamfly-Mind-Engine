"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 响应模式
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatChoice(BaseModel):
    """聊天选择"""
    index: int
    message: Dict[str, str]
    finish_reason: Optional[str] = None


class ChatUsage(BaseModel):
    """使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponseSchema(BaseModel):
    """聊天响应模式"""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[ChatUsage] = None


class VoiceResponseSchema(BaseModel):
    """语音生成响应模式"""
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # base64编码的音频数据
    duration: Optional[float] = None
    format: Optional[str] = "wav"


class ErrorResponseSchema(BaseModel):
    """错误响应模式"""
    error: Dict[str, Any]
    code: int
    message: str