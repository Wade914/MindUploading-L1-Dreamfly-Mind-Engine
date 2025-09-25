"""
@Created on: 2025/09/15
@Author: DreamFly Team
@Des: 笔记管理 - 数据模型
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreateNoteRequest(BaseModel):
    """创建笔记请求模型"""
    title: str
    content: str
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = []


class UpdateNoteRequest(BaseModel):
    """更新笔记请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    """笔记响应模型"""
    id: int
    user_id: str
    title: str
    content: str
    folder_id: Optional[str] = None
    tags: List[str] = []
    preview: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CreateFolderRequest(BaseModel):
    """创建文件夹请求模型"""
    name: str
    parent_id: Optional[str] = None


class FolderResponse(BaseModel):
    """文件夹响应模型"""
    id: str
    user_id: str
    name: str
    parent_id: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True
