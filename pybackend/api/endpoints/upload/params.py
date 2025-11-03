"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 文件上传 - 请求参数
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UploadType(str, Enum):
    """上传类型枚举"""
    THOUGHT = "thought"  # 思想数据
    VOICE = "voice"      # 声音数据
    IMAGE = "image"      # 形象数据
    VIDEO = "video"      # 视频数据


class UploadParams(BaseModel):
    """文件上传参数"""
    user_id: str = Field(..., description="用户ID")
    upload_type: UploadType = Field(..., description="上传类型")
    

class GetUploadListParams(BaseModel):
    """获取上传列表参数"""
    user_id: Optional[str] = Field(None, description="用户ID")
    upload_type: Optional[UploadType] = Field(None, description="上传类型")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")