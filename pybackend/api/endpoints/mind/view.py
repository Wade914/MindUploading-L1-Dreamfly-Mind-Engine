"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 意识体管理 - API视图
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from core.response import success
from core.auth_middleware import get_current_user_id
from typing import Optional

from .params import CreateMindParams, ListMindParams
from .service import MindService

router = APIRouter()


@router.post("/mind", summary="创建意识体")
async def create_mind(
    params: CreateMindParams,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    创建意识体

    - **name**: 意识体名称
    - **birth**: 生日（可选）
    - **mind_content**: 意识体内容
    - **type**: 类型（可选，默认MindCopy）
    - **protocol**: 协议（可选，默认MCP-v1）
    - **blockchain**: 区块链（可选，默认ethereum）
    """
    # 使用JWT中的用户ID，覆盖参数中的user_id
    params.user_id = current_user_id
    service = MindService(db)
    result = await service.create_mind(params)
    return success(data=result.model_dump(), msg="意识体创建成功")


@router.get("/mind-list", summary="获取意识体文件名列表")
async def get_mind_filenames(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取所有意识体文件名列表（兼容旧API）
    """
    service = MindService(db)
    filenames = await service.get_mind_filenames()
    return success(data=filenames, msg="获取成功")


@router.get("/minds", summary="获取意识体列表")
async def get_mind_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    获取意识体列表（分页）
    
    - **user_id**: 用户ID（可选，为空则获取所有用户的意识体）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    params = ListMindParams(user_id=current_user_id, page=page, page_size=page_size)
    service = MindService(db)
    result = await service.get_mind_list(params)
    return success(data=result.model_dump(), msg="获取成功")


@router.get("/mind/{filename}", summary="获取指定意识体内容")
async def get_mind_content(
    filename: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取指定意识体内容

    - **filename**: 文件名
    """
    service = MindService(db)
    result = await service.get_mind_content(filename)
    return success(data=result.content, msg="获取成功")


@router.delete("/mind/{mind_id}", summary="删除意识体")
async def delete_mind(
    mind_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    删除意识体

    - **mind_id**: 意识体ID
    """
    service = MindService(db)
    result = await service.delete_mind(mind_id, current_user_id)
    return success(data=result, msg="删除成功")