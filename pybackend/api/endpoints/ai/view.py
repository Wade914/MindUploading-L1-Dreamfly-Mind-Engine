"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 视图控制器
"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from .params import ChatParams, VoiceParams, CozeChatParams
from .service import AIService
from core.response import success


router = APIRouter(prefix="/ai", tags=["AI服务"])


def get_ai_service() -> AIService:
    """获取AI服务实例"""
    return AIService()


@router.post("/chat/completions", summary="聊天完成")
async def chat_completions(
    params: ChatParams,
    ai_service: AIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    聊天完成接口，支持流式和非流式输出，支持RAG知识增强

    - **messages**: 消息列表
    - **temperature**: 温度参数 (0.0-2.0)
    - **max_tokens**: 最大令牌数
    - **stream**: 是否流式输出
    - **user_id**: 用户ID（可选，用于RAG检索）
    - **enable_rag**: 是否启用RAG知识增强（默认True）
    """
    # 从params中获取RAG参数
    user_id = params.user_id
    enable_rag = params.enable_rag if params.enable_rag is not None else True

    if params.stream:
        # 流式响应 - 改进版本（支持RAG）
        async def generate():
            try:
                # 如果提供了user_id且启用RAG，使用RAG增强版本
                if user_id and enable_rag:
                    async for chunk in ai_service.chat_completion_with_rag(params, user_id, enable_rag):
                        yield f"data: {chunk}\n\n"
                else:
                    async for chunk in ai_service.chat_completion_stream(params):
                        yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                # 发生错误时发送错误信息并结束
                error_msg = '{"error": "AI服务暂时不可用"}'
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # 非流式响应
        result = await ai_service.chat_completion(params)
        return success(data=result, msg="聊天完成")


@router.post("/audio/speech", summary="语音生成")
async def generate_speech(
    params: VoiceParams,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    语音生成接口
    
    - **text**: 要生成语音的文本
    - **voice**: 语音模型
    - **emotion**: 情感
    - **speed**: 语音速度 (0.5-2.0)
    """
    result = await ai_service.generate_voice(params)
    return success(data=result.model_dump(), msg="语音生成成功")


@router.get("/models", summary="获取可用模型列表")
async def get_models():
    """获取可用的AI模型列表"""
    models = {
        "chat_models": [
            {
                "id": "deepseek-ai/DeepSeek-V3",
                "name": "DeepSeek V3",
                "description": "DeepSeek V3 大语言模型"
            }
        ],
        "voice_models": [
            {
                "id": "FunAudioLLM/CosyVoice2-0.5B:alex",
                "name": "CosyVoice Alex",
                "description": "CosyVoice 语音合成模型"
            }
        ]
    }
    return success(data=models, msg="获取模型列表成功")


@router.post("/coze/chat", summary="扣子智能体对话")
async def coze_chat(
    params: CozeChatParams,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    扣子智能体对话接口，支持流式输出

    - **user_id**: 用户ID
    - **additional_messages**: 消息列表
    - **stream**: 是否流式输出
    - **auto_save_history**: 是否保存对话历史
    - **conversation_id**: 会话ID（可选）
    """
    if params.stream:
        # 流式响应
        async def generate():
            try:
                async for chunk in ai_service.coze_chat_stream(params):
                    # 将文本内容包装成 SSE 格式
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_msg = json.dumps({"error": "扣子服务暂时不可用"}, ensure_ascii=False)
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # 非流式响应暂不支持
        return success(data={"message": "请使用流式模式"}, msg="非流式模式暂不支持")