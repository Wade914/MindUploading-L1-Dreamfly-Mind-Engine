"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 意识体管理 - 请求参数
"""

from pydantic import BaseModel, Field
from typing import Optional


class CreateMindParams(BaseModel):
    """创建意识体参数"""
    user_id: Optional[str] = Field(None, description="用户ID（将被JWT中的用户ID覆盖）")
    name: str = Field(..., min_length=1, max_length=100, description="意识体名称")
    birth: Optional[str] = Field(None, description="生日")
    mind_content: str = Field(..., description="意识体内容")
    type: Optional[str] = Field("MindCopy", description="类型")
    protocol: Optional[str] = Field("MCP-v1", description="协议")
    blockchain: Optional[str] = Field("ethereum", description="区块链")


class GetMindParams(BaseModel):
    """获取意识体参数"""
    filename: str = Field(..., description="文件名")


class ListMindParams(BaseModel):
    """获取意识体列表参数"""
    user_id: Optional[str] = Field(None, description="用户ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")