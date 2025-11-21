"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: RAG - 响应模式
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchResultItem(BaseModel):
    """检索结果项"""
    id: str = Field(..., description="文档ID")
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default={}, description="元数据")
    collection: str = Field(..., description="所属集合")


class SearchResultSchema(BaseModel):
    """检索结果模式"""
    results: List[SearchResultItem] = Field(default=[], description="检索结果列表")
    total: int = Field(..., description="结果总数")
    query: str = Field(..., description="查询文本")


class VectorizeResultSchema(BaseModel):
    """向量化结果模式"""
    success: bool = Field(..., description="是否成功")
    doc_id: str = Field(..., description="文档ID")
    collection: str = Field(..., description="集合名称")
    message: Optional[str] = Field(None, description="消息")

