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
        # 优先级：voice_id > preset_voice > 默认claire
        # 注意：系统预置音色格式为 "模型名:音色名"
        if params.voice_id:
            # 使用用户自定义音色
            voice_to_use = params.voice_id
        elif params.preset_voice:
            # 使用前端选择的系统预置音色
            voice_to_use = f"{params.voice}:{params.preset_voice}"
        else:
            # 默认使用温柔女声
            voice_to_use = f"{params.voice}:claire"

        request_data = {
            "model": params.voice,
            "input": params.text,
            "voice": voice_to_use,  # 使用voice_id或系统预置音色
            "speed": params.speed,
            "response_format": "mp3"
        }

        request_url = f"{self.siliconflow_base_url}/audio/speech"
        print(f"\n{'='*60}")
        print(f"🔊 TTS 请求详情:")
        print(f"  URL: {request_url}")
        print(f"  Headers: Authorization: Bearer sk-***{self.siliconflow_api_key[-8:]}")
        print(f"  Body: {json.dumps(request_data, ensure_ascii=False, indent=4)}")
        print(f"{'='*60}\n")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 使用流式请求读取响应
                async with client.stream(
                    'POST',
                    request_url,
                    headers=headers,
                    json=request_data
                ) as response:
                    print(f"\n{'='*60}")
                    print(f"🔊 TTS 响应详情:")
                    print(f"  Status Code: {response.status_code}")
                    print(f"  Headers: {dict(response.headers)}")

                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"  Body: {error_text.decode('utf-8')}")
                        print(f"{'='*60}\n")
                        raise UnicornException(
                            code=response.status_code,
                            errmsg=f"语音服务调用失败: {error_text.decode('utf-8')}"
                        )

                    # 流式读取所有数据
                    audio_chunks = []
                    async for chunk in response.aiter_bytes():
                        audio_chunks.append(chunk)

                    audio_data = b''.join(audio_chunks)
                    print(f"  Body: [音频数据，长度: {len(audio_data)} 字节]")
                    print(f"{'='*60}\n")

                    return VoiceResponseSchema(
                        audio_data=audio_data.hex() if audio_data else None,
                        format="mp3"
                    )

        except UnicornException:
            raise
        except httpx.RequestError as e:
            raise UnicornException(code=500, errmsg=f"网络请求失败: {str(e)}")
        except Exception as e:
            print(f"❌ 语音服务异常: {str(e)}")
            import traceback
            traceback.print_exc()
            raise UnicornException(code=500, errmsg=f"语音服务异常: {str(e)}")

    async def upload_voice_to_siliconflow(self, voice_base64: str, filename: str = "voice.wav", custom_name: str = None, text: str = None) -> Optional[str]:
        """
        上传音频到SiliconFlow获取voice_id

        Args:
            voice_base64: base64编码的音频数据
            filename: 文件名
            custom_name: 自定义音色名称
            text: 参考音频的文字内容

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
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # 准备上传
                headers = {
                    "Authorization": f"Bearer {self.siliconflow_api_key}"
                }

                # 使用multipart/form-data上传，添加必需的参数
                async with httpx.AsyncClient(timeout=60.0) as client:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (filename, f, 'audio/mpeg')}
                        # 默认参考文本（用于语音克隆）- 如果用户未提供则使用默认
                        default_text = '从前，庄周梦见自己变成了蝴蝶，一只翩翩起舞的蝴蝶。他十分惬意舒畅，悠然自得，根本不知道自己原本是庄周。突然梦醒，他才惊觉自己分明是庄周。可他却疑惑起来，不知是庄周做梦变成了蝴蝶呢，还是蝴蝶做梦变成了庄周？'

                        data = {
                            'model': 'FunAudioLLM/CosyVoice2-0.5B',
                            'customName': custom_name or filename.replace('.mp3', '').replace('.wav', ''),
                            'text': text or default_text
                        }

                        response = await client.post(
                            f"{self.siliconflow_base_url}/uploads/audio/voice",
                            headers=headers,
                            files=files,
                            data=data
                        )

                    if response.status_code == 200:
                        result = response.json()
                        # SiliconFlow API 返回格式: {"uri": "speech:default:xxx:yyy"}
                        # uri 就是 voice_id
                        voice_id = result.get('uri') or result.get('voice_id') or result.get('data', {}).get('voice_id')
                        return voice_id if voice_id else None
                    else:
                        return None

            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
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