"""
@Created on: 2025/09/16
@Author: DreamFly Team
@Des: 社交网络 - API视图
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.session import get_db
from core.response import success, fail
from .models import AddUserRequest, UpdatePermissionRequest
from .service import SocialService

router = APIRouter(prefix="/api/social", tags=["社交网络"])


@router.post("/users", summary="添加用户")
async def add_user(
    request: AddUserRequest,
    owner_id: str = Query(..., description="授权者用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    添加用户到权限空间
    
    - **account_id**: 用户账号ID（用户名、邮箱或用户ID）
    - **space**: 权限空间（personal/family/public）
    - **is_inheritor**: 是否设为继承人（仅family空间有效）
    """
    try:
        service = SocialService(db)
        result = await service.add_user_permission(owner_id, request)
        return success(data=result.model_dump(), msg="添加用户成功")
    except Exception as e:
        return fail(msg=str(e))


@router.get("/users", summary="获取用户权限列表")
async def get_users(
    owner_id: str = Query(..., description="授权者用户ID"),
    space: Optional[str] = Query(None, description="权限空间过滤"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户权限列表
    
    - **owner_id**: 授权者用户ID
    - **space**: 权限空间过滤（可选）
    """
    try:
        service = SocialService(db)
        result = await service.get_user_permissions(owner_id, space)
        return success(data=[item.model_dump() for item in result], msg="获取成功")
    except Exception as e:
        return fail(msg=str(e))


@router.put("/users/{permission_id}", summary="更新用户权限")
async def update_user_permission(
    permission_id: str,
    request: UpdatePermissionRequest,
    owner_id: str = Query(..., description="授权者用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户权限
    
    - **permission_id**: 权限记录ID
    - **space**: 新的权限空间（可选）
    - **is_inheritor**: 是否设为继承人（可选）
    """
    try:
        service = SocialService(db)
        result = await service.update_user_permission(owner_id, permission_id, request)
        return success(data=result.model_dump(), msg="更新成功")
    except Exception as e:
        return fail(msg=str(e))


@router.delete("/users/{permission_id}", summary="移除用户权限")
async def remove_user_permission(
    permission_id: str,
    owner_id: str = Query(..., description="授权者用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    移除用户权限
    
    - **permission_id**: 权限记录ID
    """
    try:
        service = SocialService(db)
        await service.remove_user_permission(owner_id, permission_id)
        return success(msg="移除成功")
    except Exception as e:
        return fail(msg=str(e))


@router.get("/stats", summary="获取社交统计数据")
async def get_social_stats(
    owner_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取社交统计数据
    
    - **owner_id**: 用户ID
    """
    try:
        service = SocialService(db)
        result = await service.get_social_stats(owner_id)
        return success(data=result.model_dump(), msg="获取成功")
    except Exception as e:
        return fail(msg=str(e))


@router.get("/search", summary="搜索用户")
async def search_user(
    account_id: str = Query(..., description="用户账号ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    根据账号ID搜索用户
    
    - **account_id**: 用户账号ID（用户名、邮箱或用户ID）
    """
    try:
        service = SocialService(db)
        result = await service.search_user_by_account_id(account_id)
        if result:
            return success(data=result.model_dump(), msg="搜索成功")
        else:
            return fail(msg="用户不存在")
    except Exception as e:
        return fail(msg=str(e))
