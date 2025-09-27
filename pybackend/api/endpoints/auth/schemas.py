"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 用户认证 - 响应模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    """用户信息模式"""
    id: str
    username: str
    email: str
    birth: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponseSchema(BaseModel):
    """登录响应模式"""
    user_id: str
    username: str
    email: str
    birth: Optional[str] = None
    register_time: datetime
    token: Optional[str] = None


class RegisterResponseSchema(BaseModel):
    """注册响应模式"""
    user_id: str
    username: str
    email: str
    birth: Optional[str] = None
    register_time: datetime
    token: Optional[str] = None