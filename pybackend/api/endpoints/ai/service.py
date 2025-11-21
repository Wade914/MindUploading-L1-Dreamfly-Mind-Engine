"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: AI服务 - 业务逻辑服务
"""

import json
import httpx
import base64
import tempfile
import os
from typing import Dict, Any, AsyncGenerator, Optional
from fastapi import HTTPException
from core.exception import UnicornException
from cfg.config import settings

from .params import ChatParams, VoiceParams, CozeChatParams
from .schemas import ChatResponseSchema, VoiceResponseSchema, CozeResponseSchema


class AIService:
    """AI服务"""
    
    def __init__(self):
        # 优先从 settings 读取，如果为空则从环境变量读取
        import os
        self.siliconflow_api_key = settings.SILICONFLOW_API_KEY or os.getenv("SILICONFLOW_API_KEY")
        self.siliconflow_base_url = settings.SILICONFLOW_BASE_URL or os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        self.deepseek_model = settings.DEEPSEEK_MODEL or os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3")

        # 扣子配置
        self.coze_api_token = settings.COZE_API_TOKEN or os.getenv("COZE_API_TOKEN")
        self.coze_api_base_url = settings.COZE_API_BASE_URL or os.getenv("COZE_API_BASE_URL", "https://api.coze.cn")
        self.coze_bot_id = settings.COZE_BOT_ID or os.getenv("COZE_BOT_ID")

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

    async def chat_completion_with_rag(
        self,
        params: ChatParams,
        user_id: str,
        enable_rag: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        带RAG增强的流式聊天完成

        Args:
            params: 聊天参数
            user_id: 用户ID
            enable_rag: 是否启用RAG检索（默认True）
        """
        # 如果启用RAG，先检索相关知识
        if enable_rag:
            try:
                from cfg.config import settings
                if getattr(settings, 'RAG_ENABLED', True):
                    from api.endpoints.rag.service import get_rag_service

                    # 提取用户最后一条消息作为查询
                    user_message = ""
                    for msg in reversed(params.messages):
                        if msg.role == "user":
                            user_message = msg.content
                            break

                    if user_message:
                        rag_service = get_rag_service()
                        results = await rag_service.search_knowledge(
                            user_id=user_id,
                            query=user_message,
                            top_k=getattr(settings, 'RAG_TOP_K', 3)
                        )

                        # 如果检索到相关知识，注入到system prompt
                        if results:
                            context = "\n\n【相关知识库内容】\n"
                            for idx, result in enumerate(results, 1):
                                source = result.metadata.get('filename') or result.metadata.get('title') or '未知来源'
                                context += f"{idx}. 来源：{source}\n内容：{result.content}\n\n"

                            # 找到system消息并追加context
                            for msg in params.messages:
                                if msg.role == "system":
                                    msg.content += context
                                    break

                            print(f"✅ RAG检索到 {len(results)} 条相关知识，已注入到对话上下文")
            except Exception as e:
                print(f"⚠️ RAG检索失败（不影响对话）: {str(e)}")

        # 调用原始的流式对话方法
        async for chunk in self.chat_completion_stream(params):
            yield chunk

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
        # 如果提供了voice_id，优先使用用户预置音色
        voice_to_use = params.voice_id if params.voice_id else params.emotion

        request_data = {
            "model": params.voice,
            "input": params.text,
            "voice": voice_to_use,  # 使用voice_id或emotion
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

    async def upload_voice_to_siliconflow(self, voice_base64: str, filename: str = "voice.wav") -> Optional[str]:
        """
        上传音频到SiliconFlow获取voice_id

        Args:
            voice_base64: base64编码的音频数据
            filename: 文件名

        Returns:
            voice_id: SiliconFlow返回的音色ID，失败返回None
        """
        try:
            # 解码base64音频数据
            # 如果包含data:audio前缀，先去除
            if ',' in voice_base64:
                voice_base64 = voice_base64.split(',')[1]

            audio_data = base64.b64decode(voice_base64)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # 准备上传
                headers = {
                    "Authorization": f"Bearer {self.siliconflow_api_key}"
                }

                # 使用multipart/form-data上传
                async with httpx.AsyncClient(timeout=60.0) as client:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (filename, f, 'audio/wav')}
                        response = await client.post(
                            f"{self.siliconflow_base_url}/uploads/audio/voice",
                            headers=headers,
                            files=files
                        )

                    if response.status_code == 200:
                        result = response.json()
                        # 根据SiliconFlow API返回格式提取voice_id
                        # 假设返回格式为 {"voice_id": "xxx"} 或 {"data": {"voice_id": "xxx"}}
                        voice_id = result.get('voice_id') or result.get('data', {}).get('voice_id')

                        if voice_id:
                            print(f"✅ 音频上传成功，voice_id: {voice_id}")
                            return voice_id
                        else:
                            print(f"⚠️ 音频上传成功但未返回voice_id，响应: {result}")
                            return None
                    else:
                        error_text = response.text
                        print(f"❌ 音频上传失败: {response.status_code} - {error_text}")
                        return None

            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            print(f"❌ 上传音频到SiliconFlow异常: {str(e)}")
            return None

    async def coze_chat_stream(self, params: CozeChatParams) -> AsyncGenerator[str, None]:
        """扣子智能体流式对话"""
        if not self.coze_api_token:
            print("扣子 API Token 未配置")
            return

        if not self.coze_bot_id:
            print("扣子 Bot ID 未配置")
            return

        headers = {
            "Authorization": f"Bearer {self.coze_api_token}",
            "Content-Type": "application/json"
        }

        # 构建请求数据
        request_data = {
            "bot_id": self.coze_bot_id,
            "user_id": params.user_id,
            "stream": params.stream,
            "auto_save_history": params.auto_save_history,
            "additional_messages": [
                {
                    "role": msg.role,
                    "type": msg.type,
                    "content": msg.content,
                    "content_type": msg.content_type
                }
                for msg in params.additional_messages
            ]
        }

        # 如果有会话ID，添加到请求中
        if params.conversation_id:
            request_data["conversation_id"] = params.conversation_id

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.coze_api_base_url}/v3/chat",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                ) as response:

                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"扣子 API 调用失败: {error_text.decode()}"
                        print(error_msg)
                        return

                    try:
                        # 扣子返回的是 SSE 格式
                        async for line in response.aiter_lines():
                            if line.startswith("data:"):
                                data = line[5:].strip()  # 移除 "data:" 前缀
                                if data == "[DONE]":
                                    print("✅ 扣子对话结束")
                                    break
                                if data:
                                    try:
                                        # 解析 JSON 数据
                                        event_data = json.loads(data)

                                        # 确保解析结果是字典类型
                                        if not isinstance(event_data, dict):
                                            continue

                                        # 扣子的数据格式：直接在顶层有 role、type、content 字段
                                        msg_type = event_data.get("type")
                                        msg_role = event_data.get("role")

                                        # 只处理 AI 助手的回答消息
                                        if msg_role == "assistant" and msg_type == "answer":
                                            content = event_data.get("content", "")
                                            if content:
                                                # 返回纯文本内容
                                                yield content

                                        # 对话完成状态
                                        elif event_data.get("status") == "completed":
                                            usage = event_data.get("usage", {})
                                            print(f"✅ 对话完成，token使用: {usage}")

                                    except json.JSONDecodeError as je:
                                        print(f"❌ JSON解析错误: {je}, 数据: {data}")
                                        continue
                                    except Exception as parse_error:
                                        print(f"❌ 数据处理错误: {parse_error}")
                                        continue

                    except Exception as stream_error:
                        print(f"扣子流式处理错误: {stream_error}")
                        return

        except httpx.RequestError as e:
            print(f"扣子网络请求失败: {e}")
            return
        except Exception as e:
            print(f"扣子服务异常: {e}")
            return