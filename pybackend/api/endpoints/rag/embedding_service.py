"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - Embedding向量化服务
"""

import os
from typing import List, Union
from cfg.config import settings
from core.exception import UnicornException


class EmbeddingService:
    """Embedding向量化服务
    
    支持两种模式：
    1. 本地模型模式（使用sentence-transformers）
    2. API模式（使用SiliconFlow或其他API）
    """
    
    def __init__(self, use_local_model: bool = True):
        """
        初始化Embedding服务
        
        Args:
            use_local_model: 是否使用本地模型（默认True）
        """
        self.use_local_model = use_local_model
        self.model = None
        
        if use_local_model:
            self._init_local_model()
        else:
            self._init_api_client()
    
    def _init_local_model(self):
        """初始化本地embedding模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # 使用中文效果好的模型
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5')
            
            print(f"🔄 正在加载本地embedding模型: {model_name}")
            self.model = SentenceTransformer(model_name)
            print(f"✅ 本地embedding模型加载成功！")
            
        except ImportError:
            raise UnicornException(
                code=500,
                errmsg="sentence-transformers未安装，请运行: pip install sentence-transformers"
            )
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"加载本地embedding模型失败: {str(e)}"
            )
    
    def _init_api_client(self):
        """初始化API客户端（预留接口）"""
        # TODO: 如果SiliconFlow提供embedding API，在这里初始化
        self.api_key = settings.SILICONFLOW_API_KEY
        self.api_base_url = settings.SILICONFLOW_BASE_URL
        
        if not self.api_key:
            raise UnicornException(code=500, errmsg="API Key未配置")
    
    async def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            向量列表，每个向量是一个float列表
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if self.use_local_model:
            return await self._encode_local(texts)
        else:
            return await self._encode_api(texts)
    
    async def _encode_local(self, texts: List[str]) -> List[List[float]]:
        """使用本地模型编码"""
        try:
            # sentence-transformers的encode方法是同步的
            # 在实际生产环境中，可以使用线程池来避免阻塞
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # 转换为列表格式
            return embeddings.tolist()
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"本地模型编码失败: {str(e)}"
            )
    
    async def _encode_api(self, texts: List[str]) -> List[List[float]]:
        """使用API编码（预留接口）"""
        # TODO: 实现API调用逻辑
        raise UnicornException(
            code=501,
            errmsg="API模式暂未实现，请使用本地模型模式"
        )
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        if self.use_local_model and self.model:
            return self.model.get_sentence_embedding_dimension()
        else:
            # 默认维度（根据实际API返回调整）
            return getattr(settings, 'EMBEDDING_DIMENSION', 512)


# 全局单例
_embedding_service_instance = None


def get_embedding_service(use_local_model: bool = True) -> EmbeddingService:
    """获取Embedding服务单例"""
    global _embedding_service_instance
    
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(use_local_model=use_local_model)
    
    return _embedding_service_instance

