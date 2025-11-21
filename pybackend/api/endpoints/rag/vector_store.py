"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - 向量存储服务（ChromaDB封装）
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from cfg.config import settings
from core.exception import UnicornException


class VectorStoreService:
    """向量存储服务（基于ChromaDB）"""
    
    def __init__(self):
        """初始化ChromaDB客户端"""
        self.client = None
        self.collections = {}
        self._init_chromadb()
    
    def _init_chromadb(self):
        """初始化ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            # 获取持久化路径
            chroma_path = getattr(settings, 'CHROMA_DB_PATH', './pybackend/chroma_db')
            
            # 确保目录存在
            Path(chroma_path).mkdir(parents=True, exist_ok=True)
            
            print(f"🔄 正在初始化ChromaDB，路径: {chroma_path}")
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            print(f"✅ ChromaDB初始化成功！")
            
        except ImportError:
            raise UnicornException(
                code=500,
                errmsg="chromadb未安装，请运行: pip install chromadb"
            )
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"ChromaDB初始化失败: {str(e)}"
            )
    
    def get_or_create_collection(self, collection_name: str, metadata: Optional[Dict] = None):
        """获取或创建集合"""
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        try:
            # 默认使用余弦相似度
            if metadata is None:
                metadata = {"hnsw:space": "cosine"}
            
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata=metadata
            )
            
            self.collections[collection_name] = collection
            return collection
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"创建集合失败: {str(e)}"
            )
    
    async def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """添加文档到向量库"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"✅ 成功添加 {len(ids)} 个文档到集合 '{collection_name}'")
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"添加文档失败: {str(e)}"
            )
    
    async def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """查询向量库"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            return results
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"查询向量库失败: {str(e)}"
            )
    
    async def delete_document(self, collection_name: str, doc_id: str):
        """删除文档"""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=[doc_id])
            print(f"✅ 成功删除文档 {doc_id} from '{collection_name}'")
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"删除文档失败: {str(e)}"
            )
    
    async def update_document(
        self,
        collection_name: str,
        doc_id: str,
        embedding: List[float],
        document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """更新文档"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata] if metadata else None
            )
            
            print(f"✅ 成功更新文档 {doc_id} in '{collection_name}'")
            
        except Exception as e:
            raise UnicornException(
                code=500,
                errmsg=f"更新文档失败: {str(e)}"
            )


# 全局单例
_vector_store_instance = None


def get_vector_store() -> VectorStoreService:
    """获取向量存储服务单例"""
    global _vector_store_instance
    
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    
    return _vector_store_instance

