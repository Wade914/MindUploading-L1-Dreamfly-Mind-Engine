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
    user_id: Optional[str] = Field(None, description="用户ID（用于RAG检索）")
    enable_rag: Optional[bool] = Field(True, description="是否启用RAG知识增强")


class VoiceParams(BaseModel):
    """语音生成请求参数"""
    text: str = Field(..., min_length=1, max_length=1000, description="要生成语音的文本")
    voice: Optional[str] = Field("FunAudioLLM/CosyVoice2-0.5B:alex", description="语音模型或voice_id")
    emotion: Optional[str] = Field("happy", description="情感")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="语音速度")
    voice_id: Optional[str] = Field(None, description="用户预置音色ID（优先使用）")


class CozeMessageParam(BaseModel):
    """扣子消息参数"""
    role: str = Field(..., description="角色：user/assistant")
    type: str = Field("question", description="消息类型：question/answer")
    content: str = Field(..., description="消息内容")
    content_type: str = Field("text", description="内容类型：text/object_string")


class CozeChatParams(BaseModel):
    """扣子聊天请求参数"""
    user_id: str = Field("123456789", description="用户ID")
    additional_messages: List[CozeMessageParam] = Field(..., description="对话消息列表")
    stream: Optional[bool] = Field(True, description="是否启用流式返回")
    auto_save_history: Optional[bool] = Field(True, description="是否保存对话记录")
    conversation_id: Optional[str] = Field(None, description="会话ID，不传则自动生成")