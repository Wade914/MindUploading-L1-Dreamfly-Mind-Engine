"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 业务逻辑服务
"""

import json
import httpx
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
from core.exception import UnicornException
from cfg.config import settings

from .params import ChatParams, VoiceParams
from .schemas import ChatResponseSchema, VoiceResponseSchema


class AIService:
    """AI服务"""
    
    def __init__(self):
        # 优先从 settings 读取，如果为空则从环境变量读取
        import os
        self.siliconflow_api_key = settings.SILICONFLOW_API_KEY or os.getenv("SILICONFLOW_API_KEY")
        self.siliconflow_base_url = settings.SILICONFLOW_BASE_URL or os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        self.deepseek_model = settings.DEEPSEEK_MODEL or os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3")

        if not self.siliconflow_api_key:
            raise UnicornException(code=500, errmsg="SiliconFlow API Key 未配置")

    async def chat_completion(self, params: ChatParams) -> Dict[str, Any]:
        """聊天完成"""
        headers = {
            "Authorization": f"Bearer {self.siliconflow_api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求数据（非流式固定为 False，避免服务端返回 SSE）
        request_data = {
            "model": self.deepseek_model,
            "messages": [msg.model_dump() for msg in params.messages],
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "stream": False
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.siliconflow_base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )

                if response.status_code != 200:
                    error_text = response.text
                    raise UnicornException(
                        code=response.status_code,
                        errmsg=f"AI服务调用失败: {error_text}"
                    )

                # 兼容性解析：优先按 JSON 解析，失败则给出更明确错误
                try:
                    return response.json()
                except Exception as parse_err:
                    raise UnicornException(code=500, errmsg=f"AI服务返回解析失败: {str(parse_err) or '未知错误'}")

        except httpx.RequestError as e:
            raise UnicornException(code=500, errmsg=f"网络请求失败: {str(e)}")
        except UnicornException:
            # 透传我们构造的业务异常
            raise
        except Exception as e:
            # 捕获未知异常，返回更明确的信息
            raise UnicornException(code=500, errmsg=f"AI服务异常: {str(e) or '未知错误'}")

    async def chat_completion_stream(self, params: ChatParams) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        headers = {
            "Authorization": f"Bearer {self.siliconflow_api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求数据，确保流式输出
        request_data = {
            "model": self.deepseek_model,
            "messages": [msg.model_dump() for msg in params.messages],
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.siliconflow_base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                ) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"AI服务调用失败: {error_text.decode()}"
                        print(f"SiliconFlow API错误: {error_msg}")
                        # 不抛出异常，直接结束生成器
                        return
                    
                    try:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # 移除 "data: " 前缀
                                if data.strip() == "[DONE]":
                                    break
                                if data.strip():  # 只处理非空数据
                                    yield data
                    except Exception as stream_error:
                        print(f"流式处理错误: {stream_error}")
                        # 不抛出异常，优雅结束
                        return

        except httpx.RequestError as e:
            print(f"网络请求失败: {e}")
            # 不抛出异常，直接结束生成器
            return
        except UnicornException as e:
            print(f"已知异常: {e.errmsg}")
            return
        except Exception as e:
            print(f"AI服务异常: {e}")
            return

    async def generate_voice(self, params: VoiceParams) -> VoiceResponseSchema:
        """生成语音"""
        headers = {
            "Authorization": f"Bearer {self.siliconflow_api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求数据
        request_data = {
            "model": params.voice,
            "input": params.text,
            "voice": params.emotion,
            "speed": params.speed
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.siliconflow_base_url}/audio/speech",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    raise UnicornException(
                        code=response.status_code, 
                        errmsg=f"语音服务调用失败: {error_text}"
                    )
                
                # 假设返回的是音频数据
                audio_data = response.content
                
                return VoiceResponseSchema(
                    audio_data=audio_data.hex() if audio_data else None,
                    format="wav"
                )
                
        except httpx.RequestError as e:
            raise UnicornException(code=500, errmsg=f"网络请求失败: {str(e)}")
        except Exception as e:
            raise UnicornException(code=500, errmsg=f"语音服务异常: {str(e)}")