"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 用户资产管理 - API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.session import get_db
from core.response import success, fail
from .models import ConsciousnessAsset, CreateAssetRequest, UpdateAssetRequest, DashboardStats
from .service import UserAssetsService

router = APIRouter(prefix="/api/user", tags=["用户资产管理"])


@router.get("/consciousness-assets", response_model=dict)
async def get_user_consciousness_assets(
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的意识体资产列表"""
    try:
        assets = await UserAssetsService.get_user_consciousness_assets(db, user_id)
        return success(data={"assets": [asset.model_dump() for asset in assets]})
    except Exception as e:
        return fail(msg=f"获取资产列表失败: {str(e)}")


@router.post("/consciousness-assets", response_model=dict)
async def create_consciousness_asset(
    asset_data: CreateAssetRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建新的意识体资产"""
    try:
        asset = await UserAssetsService.create_consciousness_asset(db, user_id, asset_data)
        return success(data={"asset": asset.model_dump()}, msg="意识体资产创建成功")
    except Exception as e:
        return fail(msg=f"创建资产失败: {str(e)}")


@router.get("/consciousness-assets/{asset_id}", response_model=dict)
async def get_consciousness_asset(
    asset_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定的意识体资产详情"""
    try:
        asset = await UserAssetsService.get_consciousness_asset_by_id(db, asset_id)
        if not asset:
            return fail(code=404, msg="资产不存在")

        # 验证资产所有权
        if asset.user_id != user_id:
            return fail(code=403, msg="无权访问此资产")

        return success(data={"asset": asset.model_dump()})
    except Exception as e:
        return fail(msg=f"获取资产详情失败: {str(e)}")


@router.put("/consciousness-assets/{asset_id}", response_model=dict)
async def update_consciousness_asset(
    asset_id: int,
    asset_data: UpdateAssetRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新意识体资产"""
    try:
        asset = await UserAssetsService.update_consciousness_asset(db, asset_id, user_id, asset_data)
        if not asset:
            return fail(code=404, msg="资产不存在或无权修改")

        return success(data={"asset": asset.model_dump()}, msg="资产更新成功")
    except Exception as e:
        return fail(msg=f"更新资产失败: {str(e)}")


@router.delete("/consciousness-assets/{asset_id}", response_model=dict)
async def delete_consciousness_asset(
    asset_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除意识体资产"""
    try:
        success_deleted = await UserAssetsService.delete_consciousness_asset(db, asset_id, user_id)
        if not success_deleted:
            return fail(code=404, msg="资产不存在或无权删除")

        return success(msg="资产删除成功")
    except Exception as e:
        return fail(msg=f"删除资产失败: {str(e)}")


@router.get("/dashboard-stats", response_model=dict)
async def get_dashboard_stats(
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户仪表板统计数据"""
    try:
        stats = await UserAssetsService.get_user_dashboard_stats(db, user_id)
        return success(data={"stats": stats.model_dump()})
    except Exception as e:
        return fail(msg=f"获取统计数据失败: {str(e)}")
