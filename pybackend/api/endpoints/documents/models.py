"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 文档管理 - 数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserDocument(BaseModel):
    """用户文档模型"""
    id: Optional[int] = Field(None, description="文档ID")
    user_id: str = Field(..., description="用户ID")
    filename: str = Field(..., description="文件名")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_path: Optional[str] = Field(None, description="文件路径")
    extracted_text: Optional[str] = Field(None, description="提取的文本内容")
    tags: List[str] = Field(default_factory=list, description="标签")
    status: str = Field(default="uploaded", description="状态")
    uploaded_at: Optional[datetime] = Field(None, description="上传时间")
    processed_at: Optional[datetime] = Field(None, description="处理时间")


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: int = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")


class UpdateDocumentRequest(BaseModel):
    """更新文档请求"""
    tags: Optional[List[str]] = Field(None, description="标签")
    extracted_text: Optional[str] = Field(None, description="提取的文本内容")


class Transaction(BaseModel):
    """交易记录模型"""
    id: Optional[int] = Field(None, description="交易ID")
    buyer_id: Optional[str] = Field(None, description="买方ID")
    seller_id: Optional[str] = Field(None, description="卖方ID")
    consciousness_id: Optional[int] = Field(None, description="意识体ID")
    transaction_type: str = Field(..., description="交易类型")
    amount: float = Field(..., description="金额")
    status: str = Field(default="pending", description="状态")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class CreateTransactionRequest(BaseModel):
    """创建交易请求"""
    seller_id: Optional[str] = Field(None, description="卖方ID")
    consciousness_id: Optional[int] = Field(None, description="意识体ID")
    transaction_type: str = Field(..., description="交易类型")
    amount: float = Field(..., ge=0, description="金额")


class MarketConsciousnessItem(BaseModel):
    """市场意识体商品"""
    id: int = Field(..., description="意识体ID")
    name: str = Field(..., description="名称")
    description: Optional[str] = Field(None, description="描述")
    type: Optional[str] = Field(None, description="类型")
    seller_id: str = Field(..., description="卖方ID")
    rating: float = Field(..., description="评分")
    interactions_count: int = Field(..., description="互动次数")
    pricing_model: dict = Field(..., description="定价模型")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    tags: List[str] = Field(default_factory=list, description="标签")
