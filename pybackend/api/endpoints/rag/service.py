"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - 核心服务（整合embedding和检索）
"""

from typing import List, Dict, Any, Optional
from .embedding_service import get_embedding_service
from .vector_store import get_vector_store
from .schemas import SearchResultItem, SearchResultSchema
from core.exception import UnicornException


class RAGService:
    """RAG核心服务"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.embedding_service = get_embedding_service(use_local_model=True)
        self.vector_store = get_vector_store()
    
    async def vectorize_and_store(
        self,
        collection_name: str,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        向量化文本并存储到向量库
        
        Args:
            collection_name: 集合名称（documents/memories/notes）
            doc_id: 文档唯一ID
            content: 文本内容
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            # 1. 生成embedding
            embeddings = await self.embedding_service.encode(content)
            
            # 2. 存储到向量库
            await self.vector_store.add_documents(
                collection_name=collection_name,
                ids=[doc_id],
                embeddings=embeddings,
                documents=[content],
                metadatas=[metadata] if metadata else None
            )
            
            return True
            
        except Exception as e:
            print(f"❌ 向量化并存储失败: {str(e)}")
            return False
    
    async def search_knowledge(
        self,
        user_id: str,
        query: str,
        top_k: int = 3,
        collections: Optional[List[str]] = None
    ) -> List[SearchResultItem]:
        """
        检索相关知识
        
        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回结果数量
            collections: 要检索的集合列表
            
        Returns:
            检索结果列表
        """
        if collections is None:
            collections = ["documents", "memories", "notes"]
        
        try:
            # 1. 生成查询向量
            query_embeddings = await self.embedding_service.encode(query)
            
            # 2. 在所有集合中检索
            all_results = []
            
            for collection_name in collections:
                try:
                    # 只检索该用户的数据
                    results = await self.vector_store.query(
                        collection_name=collection_name,
                        query_embeddings=query_embeddings,
                        n_results=top_k,
                        where={"user_id": user_id}
                    )
                    
                    # 解析结果
                    if results and results.get('ids') and len(results['ids']) > 0:
                        for i in range(len(results['ids'][0])):
                            all_results.append(SearchResultItem(
                                id=results['ids'][0][i],
                                content=results['documents'][0][i],
                                score=1.0 - results['distances'][0][i],  # 距离转相似度
                                metadata=results['metadatas'][0][i] if results.get('metadatas') else {},
                                collection=collection_name
                            ))
                
                except Exception as e:
                    print(f"⚠️ 检索集合 '{collection_name}' 失败: {str(e)}")
                    continue
            
            # 3. 按相似度排序并返回top_k
            all_results.sort(key=lambda x: x.score, reverse=True)
            return all_results[:top_k]
            
        except Exception as e:
            print(f"❌ 知识检索失败: {str(e)}")
            return []
    
    async def delete_document(self, collection_name: str, doc_id: str):
        """删除文档"""
        await self.vector_store.delete_document(collection_name, doc_id)
    
    async def update_document(
        self,
        collection_name: str,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """更新文档"""
        # 生成新的embedding
        embeddings = await self.embedding_service.encode(content)
        
        # 更新向量库
        await self.vector_store.update_document(
            collection_name=collection_name,
            doc_id=doc_id,
            embedding=embeddings[0],
            document=content,
            metadata=metadata
        )


# 全局单例
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """获取RAG服务单例"""
    global _rag_service_instance
    
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    
    return _rag_service_instance

