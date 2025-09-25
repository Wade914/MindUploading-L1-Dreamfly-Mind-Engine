"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 文件上传 - 响应模式
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UploadSchema(BaseModel):
    """上传记录信息模式"""
    id: str
    user_id: str
    original_filename: str
    saved_filename: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    upload_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UploadResponseSchema(BaseModel):
    """文件上传响应模式"""
    file_id: str
    original_filename: str
    saved_filename: str
    file_size: int
    upload_type: str
    upload_time: datetime


class UploadListResponseSchema(BaseModel):
    """上传列表响应模式"""
    items: List[UploadSchema]
    total: int
    page: int
    page_size: int