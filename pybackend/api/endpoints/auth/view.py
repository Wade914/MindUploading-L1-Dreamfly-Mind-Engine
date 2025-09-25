"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 用户认证 - API视图
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from core.response import success

from .params import RegisterParams, LoginParams
from .schemas import LoginResponseSchema, RegisterResponseSchema
from .service import AuthService

router = APIRouter()


@router.post("/register", summary="用户注册")
async def register(
    params: RegisterParams,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    用户注册
    
    - **username**: 用户名
    - **email**: 邮箱
    - **password**: 密码
    - **birth**: 生日（可选）
    """
    service = AuthService(db)
    result = await service.register_user(params)
    return success(data=result.model_dump(), msg="注册成功")


@router.post("/login", summary="用户登录")
async def login(
    params: LoginParams,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    用户登录
    
    - **email**: 邮箱
    - **password**: 密码
    """
    service = AuthService(db)
    result = await service.login_user(params)
    return success(data=result.model_dump(), msg="登录成功")