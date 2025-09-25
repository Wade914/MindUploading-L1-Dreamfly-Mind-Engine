"""
@Created on: 2025/09/16
@Author: DreamFly Team
@Des: 社交网络 - 数据模型
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AddUserRequest(BaseModel):
    """添加用户请求模型"""
    account_id: str
    space: str  # 'personal', 'family', 'public'
    is_inheritor: bool = False


class UserPermission(BaseModel):
    """用户权限模型"""
    id: str
    user_id: str  # 被授权的用户ID
    owner_id: str  # 授权者ID
    account_id: str  # 被授权用户的账号ID
    name: str  # 用户名
    avatar: str = "👤"
    space: str  # 权限空间
    is_inheritor: bool = False
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class UpdatePermissionRequest(BaseModel):
    """更新权限请求模型"""
    space: Optional[str] = None
    is_inheritor: Optional[bool] = None


class SocialStats(BaseModel):
    """社交统计模型"""
    total_connections: int
    inheritors_count: int
    personal_space_users: int
    family_space_users: int
    public_space_users: int


class UserSearchResult(BaseModel):
    """用户搜索结果模型"""
    user_id: str
    username: str
    email: str
    avatar: str = "👤"
    created_at: datetime
