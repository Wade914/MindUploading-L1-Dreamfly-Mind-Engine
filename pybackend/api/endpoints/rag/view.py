"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - API接口
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from .service import get_rag_service, RAGService
from .params import SearchKnowledgeParams, VectorizeDocumentParams
from .schemas import SearchResultSchema, VectorizeResultSchema
from core.response import success, fail


router = APIRouter(prefix="/rag", tags=["RAG知识检索"])


def get_service() -> RAGService:
    """获取RAG服务实例"""
    return get_rag_service()


@router.post("/search", summary="检索知识", response_model=Dict[str, Any])
async def search_knowledge(
    params: SearchKnowledgeParams,
    rag_service: RAGService = Depends(get_service)
):
    """
    检索相关知识
    
    - **user_id**: 用户ID
    - **query**: 查询文本
    - **top_k**: 返回结果数量（默认3）
    - **collections**: 要检索的集合（默认全部）
    """
    try:
        results = await rag_service.search_knowledge(
            user_id=params.user_id,
            query=params.query,
            top_k=params.top_k,
            collections=params.collections
        )
        
        response = SearchResultSchema(
            results=results,
            total=len(results),
            query=params.query
        )
        
        return success(data=response.model_dump(), msg="检索成功")
        
    except Exception as e:
        return fail(msg=f"检索失败: {str(e)}")


@router.post("/vectorize/document", summary="向量化文档", response_model=Dict[str, Any])
async def vectorize_document(
    params: VectorizeDocumentParams,
    rag_service: RAGService = Depends(get_service)
):
    """
    向量化文档并存储
    
    - **user_id**: 用户ID
    - **doc_id**: 文档ID
    - **content**: 文档内容
    - **metadata**: 元数据
    """
    try:
        # 构建文档ID
        doc_id = f"doc_{params.user_id}_{params.doc_id}"
        
        # 添加user_id到metadata
        metadata = params.metadata or {}
        metadata['user_id'] = params.user_id
        metadata['doc_id'] = params.doc_id
        
        success_flag = await rag_service.vectorize_and_store(
            collection_name="documents",
            doc_id=doc_id,
            content=params.content,
            metadata=metadata
        )
        
        if success_flag:
            result = VectorizeResultSchema(
                success=True,
                doc_id=doc_id,
                collection="documents",
                message="文档向量化成功"
            )
            return success(data=result.model_dump(), msg="向量化成功")
        else:
            return fail(msg="向量化失败")
            
    except Exception as e:
        return fail(msg=f"向量化失败: {str(e)}")


@router.delete("/document/{collection}/{doc_id}", summary="删除文档")
async def delete_document(
    collection: str,
    doc_id: str,
    rag_service: RAGService = Depends(get_service)
):
    """删除向量库中的文档"""
    try:
        await rag_service.delete_document(collection, doc_id)
        return success(msg="删除成功")
    except Exception as e:
        return fail(msg=f"删除失败: {str(e)}")


@router.get("/health", summary="健康检查")
async def health_check():
    """检查RAG服务状态"""
    try:
        rag_service = get_rag_service()
        
        # 检查embedding服务
        embedding_status = "OK" if rag_service.embedding_service.model else "Not Loaded"
        
        # 检查向量库
        vector_store_status = "OK" if rag_service.vector_store.client else "Not Connected"
        
        return success(data={
            "embedding_service": embedding_status,
            "vector_store": vector_store_status,
            "status": "healthy"
        }, msg="RAG服务正常")
        
    except Exception as e:
        return fail(msg=f"RAG服务异常: {str(e)}")

