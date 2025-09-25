"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 请求参数
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessageParam(BaseModel):
    """聊天消息参数"""
    role: str = Field(..., description="角色：system/user/assistant")
    content: str = Field(..., description="消息内容")


class ChatParams(BaseModel):
    """聊天请求参数"""
    messages: List[ChatMessageParam] = Field(..., description="消息列表")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(1024, ge=1, le=4096, description="最大令牌数")
    stream: Optional[bool] = Field(True, description="是否流式输出")


class VoiceParams(BaseModel):
    """语音生成请求参数"""
    text: str = Field(..., min_length=1, max_length=1000, description="要生成语音的文本")
    voice: Optional[str] = Field("FunAudioLLM/CosyVoice2-0.5B:alex", description="语音模型")
    emotion: Optional[str] = Field("happy", description="情感")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="语音速度")