"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 用户资产管理 - 数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PricingModel(BaseModel):
    """定价模型"""
    preview: Dict[str, Any] = Field(default_factory=dict, description="预览配置")
    rent: Dict[str, Any] = Field(default_factory=dict, description="租赁配置")
    buy: Dict[str, Any] = Field(default_factory=dict, description="购买配置")


class ConsciousnessAsset(BaseModel):
    """意识体资产模型"""
    id: Optional[int] = Field(None, description="资产ID")
    user_id: str = Field(..., description="用户ID")
    name: str = Field(..., min_length=1, max_length=100, description="意识体名称")
    description: Optional[str] = Field(None, description="描述")
    type: Optional[str] = Field(None, description="类型")
    completeness: int = Field(default=0, ge=0, le=100, description="完整度")
    activity_score: int = Field(default=0, ge=0, le=100, description="活跃度")
    sync_status: str = Field(default="pending", description="同步状态")
    status: str = Field(default="draft", description="状态")
    tags: List[str] = Field(default_factory=list, description="标签")
    interactions_count: int = Field(default=0, description="互动次数")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="评分")
    pricing_model: Optional[PricingModel] = Field(None, description="定价模型")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    last_sync_at: Optional[datetime] = Field(None, description="最后同步时间")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CreateAssetRequest(BaseModel):
    """创建资产请求"""
    name: str = Field(..., min_length=1, max_length=100, description="意识体名称")
    description: Optional[str] = Field(None, description="描述")
    type: Optional[str] = Field(None, description="类型")
    tags: List[str] = Field(default_factory=list, description="标签")
    pricing_model: Optional[PricingModel] = Field(None, description="定价模型")


class UpdateAssetRequest(BaseModel):
    """更新资产请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="意识体名称")
    description: Optional[str] = Field(None, description="描述")
    type: Optional[str] = Field(None, description="类型")
    tags: Optional[List[str]] = Field(None, description="标签")
    pricing_model: Optional[PricingModel] = Field(None, description="定价模型")
    status: Optional[str] = Field(None, description="状态")


class UserStatistic(BaseModel):
    """用户统计数据模型"""
    stat_type: str = Field(..., description="统计类型")
    stat_value: str = Field(..., description="统计值")
    stat_date: Optional[str] = Field(None, description="统计日期")


class DashboardStats(BaseModel):
    """仪表板统计数据"""
    consciousness_level: int = Field(default=0, description="意识协合度")
    memory_count: int = Field(default=0, description="记忆片段数量")
    interaction_count: int = Field(default=0, description="互动次数")
    knowledge_points: int = Field(default=0, description="知识节点数量")
    assets_count: int = Field(default=0, description="资产数量")
    total_revenue: float = Field(default=0.0, description="总收入")
    monthly_revenue: float = Field(default=0.0, description="月收入")
