"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 记忆片段管理 - 数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MemoryFragment(BaseModel):
    """记忆片段模型"""
    id: Optional[int] = Field(None, description="片段ID")
    user_id: str = Field(..., description="用户ID")
    title: str = Field(..., min_length=1, max_length=200, description="记忆标题")
    content: str = Field(..., min_length=1, description="记忆内容")
    time_period: Optional[str] = Field(None, description="时间段")
    category: Optional[str] = Field(None, description="分类")
    importance: int = Field(default=5, ge=1, le=10, description="重要程度(1-10)")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CreateMemoryRequest(BaseModel):
    """创建记忆片段请求"""
    title: str = Field(..., min_length=1, max_length=200, description="记忆标题")
    content: str = Field(..., min_length=1, description="记忆内容")
    time_period: Optional[str] = Field(None, description="时间段")
    category: Optional[str] = Field(None, description="分类")
    importance: int = Field(default=5, ge=1, le=10, description="重要程度(1-10)")
    tags: List[str] = Field(default_factory=list, description="标签")


class UpdateMemoryRequest(BaseModel):
    """更新记忆片段请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="记忆标题")
    content: Optional[str] = Field(None, min_length=1, description="记忆内容")
    time_period: Optional[str] = Field(None, description="时间段")
    category: Optional[str] = Field(None, description="分类")
    importance: Optional[int] = Field(None, ge=1, le=10, description="重要程度(1-10)")
    tags: Optional[List[str]] = Field(None, description="标签")


class TestResult(BaseModel):
    """测试结果模型"""
    id: Optional[int] = Field(None, description="结果ID")
    user_id: str = Field(..., description="用户ID")
    test_type: str = Field(..., description="测试类型")
    results: dict = Field(..., description="测试结果")
    score: Optional[int] = Field(None, description="得分")
    answers: Optional[dict] = Field(None, description="用户答案")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class CreateTestResultRequest(BaseModel):
    """创建测试结果请求"""
    test_type: str = Field(..., description="测试类型")
    results: dict = Field(..., description="测试结果")
    score: Optional[int] = Field(None, description="得分")
    answers: Optional[dict] = Field(None, description="用户答案")
