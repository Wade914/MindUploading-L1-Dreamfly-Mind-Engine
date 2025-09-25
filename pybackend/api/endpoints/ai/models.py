"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 数据模型
"""

from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # system, user, assistant
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = True


class VoiceRequest(BaseModel):
    """语音生成请求模型"""
    text: str
    voice: Optional[str] = "FunAudioLLM/CosyVoice2-0.5B:alex"
    emotion: Optional[str] = "happy"
    speed: Optional[float] = 1.0