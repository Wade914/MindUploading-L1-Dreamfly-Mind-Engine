"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 用户认证 - 请求参数
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterParams(BaseModel):
    """用户注册参数"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    birth: Optional[str] = Field(None, description="生日")


class LoginParams(BaseModel):
    """用户登录参数"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=1, description="密码")