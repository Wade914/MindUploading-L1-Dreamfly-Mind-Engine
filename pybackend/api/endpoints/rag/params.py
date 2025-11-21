"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - 请求参数
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class VectorizeDocumentParams(BaseModel):
    """向量化文档参数"""
    user_id: str = Field(..., description="用户ID")
    doc_id: int = Field(..., description="文档ID")
    content: str = Field(..., description="文档内容")
    metadata: Optional[dict] = Field(default={}, description="元数据")


class SearchKnowledgeParams(BaseModel):
    """知识检索参数"""
    user_id: str = Field(..., description="用户ID")
    query: str = Field(..., description="查询文本")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="返回结果数量")
    collections: Optional[List[str]] = Field(
        default=["documents", "memories", "notes"],
        description="要检索的集合"
    )


class VectorizeMemoryParams(BaseModel):
    """向量化记忆片段参数"""
    user_id: str = Field(..., description="用户ID")
    memory_id: int = Field(..., description="记忆ID")
    content: str = Field(..., description="记忆内容")
    metadata: Optional[dict] = Field(default={}, description="元数据")


class VectorizeNoteParams(BaseModel):
    """向量化笔记参数"""
    user_id: str = Field(..., description="用户ID")
    note_id: int = Field(..., description="笔记ID")
    content: str = Field(..., description="笔记内容")
    metadata: Optional[dict] = Field(default={}, description="元数据")

