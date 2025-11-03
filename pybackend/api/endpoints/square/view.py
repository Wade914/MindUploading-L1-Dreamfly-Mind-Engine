"""
@Created on: 2025/01/16
@Author: DreamFly Team
@Des: Square 广场 - API 接口
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.session import get_db
from core.response import success, fail
from .models import (
    CreateThoughtRequest, UpdateThoughtRequest,
    CreateCommentRequest,
    FollowRequest, UpdateProfileRequest
)
from .service import SquareService

router = APIRouter(prefix="/api/square", tags=["广场"])


# ==================== 思想元胞相关接口 ====================

@router.post("/thoughts", response_model=dict)
async def create_thought(
    thought_data: CreateThoughtRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """发布思想元胞"""
    try:
        thought = await SquareService.create_thought(db, user_id, thought_data)
        return success(data={"thought": thought.model_dump()}, msg="发布成功")
    except Exception as e:
        return fail(msg=f"发布失败: {str(e)}")


@router.get("/thoughts", response_model=dict)
async def get_thoughts(
    user_id: Optional[str] = Query(None, description="用户ID (过滤特定用户的思想元胞)"),
    current_user_id: Optional[str] = Query(None, description="当前用户ID (用于判断点赞状态)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取思想元胞列表"""
    try:
        result = await SquareService.get_thoughts(db, current_user_id, user_id, page, page_size)
        return success(data=result.model_dump(), msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")


@router.get("/thoughts/{thought_id}", response_model=dict)
async def get_thought_detail(
    thought_id: int = Path(..., description="思想元胞ID"),
    current_user_id: Optional[str] = Query(None, description="当前用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取思想元胞详情"""
    try:
        thought = await SquareService.get_thought_by_id(db, thought_id, current_user_id)
        if not thought:
            raise HTTPException(status_code=404, detail="思想元胞不存在")
        
        return success(data={"thought": thought.model_dump()}, msg="获取成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")


@router.delete("/thoughts/{thought_id}", response_model=dict)
async def delete_thought(
    thought_id: int = Path(..., description="思想元胞ID"),
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除思想元胞"""
    try:
        success_deleted = await SquareService.delete_thought(db, thought_id, user_id)
        if not success_deleted:
            raise HTTPException(status_code=404, detail="思想元胞不存在或无权删除")
        
        return success(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"删除失败: {str(e)}")


# ==================== 点赞相关接口 ====================

@router.post("/thoughts/{thought_id}/like", response_model=dict)
async def toggle_like(
    thought_id: int = Path(..., description="思想元胞ID"),
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """点赞/取消点赞"""
    try:
        is_liked, likes_count = await SquareService.toggle_like(db, thought_id, user_id)
        return success(
            data={"is_liked": is_liked, "likes_count": likes_count},
            msg="点赞成功" if is_liked else "取消点赞成功"
        )
    except Exception as e:
        return fail(msg=f"操作失败: {str(e)}")


# ==================== 评论相关接口 ====================

@router.post("/thoughts/{thought_id}/comments", response_model=dict)
async def create_comment(
    comment_data: CreateCommentRequest,
    thought_id: int = Path(..., description="思想元胞ID"),
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """发表评论"""
    try:
        comment = await SquareService.create_comment(db, thought_id, user_id, comment_data)
        return success(data={"comment": comment.model_dump()}, msg="评论成功")
    except Exception as e:
        return fail(msg=f"评论失败: {str(e)}")


@router.get("/thoughts/{thought_id}/comments", response_model=dict)
async def get_comments(
    thought_id: int = Path(..., description="思想元胞ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取评论列表"""
    try:
        result = await SquareService.get_comments(db, thought_id)
        return success(data=result.model_dump(), msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")


# ==================== 用户关注相关接口 ====================

@router.post("/follow", response_model=dict)
async def follow_user(
    follow_data: FollowRequest,
    user_id: str = Query(..., description="当前用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """关注用户"""
    try:
        success_followed = await SquareService.follow_user(db, user_id, follow_data.following_id)
        if not success_followed:
            return fail(msg="关注失败 (可能已经关注或不能关注自己)")
        
        return success(msg="关注成功")
    except Exception as e:
        return fail(msg=f"关注失败: {str(e)}")


@router.delete("/follow/{following_id}", response_model=dict)
async def unfollow_user(
    following_id: str = Path(..., description="要取消关注的用户ID"),
    user_id: str = Query(..., description="当前用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """取消关注用户"""
    try:
        success_unfollowed = await SquareService.unfollow_user(db, user_id, following_id)
        if not success_unfollowed:
            return fail(msg="取消关注失败 (可能没有关注关系)")
        
        return success(msg="取消关注成功")
    except Exception as e:
        return fail(msg=f"取消关注失败: {str(e)}")


# ==================== 用户资料相关接口 ====================

@router.get("/users/{target_user_id}", response_model=dict)
async def get_user_profile(
    target_user_id: str = Path(..., description="目标用户ID"),
    current_user_id: Optional[str] = Query(None, description="当前用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户公开资料"""
    try:
        profile = await SquareService.get_user_profile(db, target_user_id, current_user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return success(data={"profile": profile.model_dump()}, msg="获取成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")


@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: UpdateProfileRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新个人资料"""
    try:
        profile = await SquareService.update_user_profile(db, user_id, profile_data)
        return success(data={"profile": profile.model_dump()}, msg="更新成功")
    except Exception as e:
        return fail(msg=f"更新失败: {str(e)}")


# ==================== 时间线和探索页 ====================

@router.get("/timeline", response_model=dict)
async def get_timeline(
    user_id: str = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取关注用户的动态时间线"""
    try:
        result = await SquareService.get_following_thoughts(db, user_id, page, page_size)
        return success(data=result.model_dump(), msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")


@router.get("/explore", response_model=dict)
async def get_explore(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """探索页 - 推荐内容 (TODO: 待实现)"""
    # TODO: 实现推荐算法
    return success(data={"thoughts": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}, msg="功能开发中")


# ==================== 收藏相关接口 ====================

@router.post("/thoughts/{thought_id}/bookmark", response_model=dict)
async def toggle_bookmark(
    thought_id: int = Path(..., description="思想元胞ID"),
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """收藏/取消收藏思想元胞"""
    try:
        result = await SquareService.toggle_bookmark(db, user_id, thought_id)
        return success(data=result, msg=result["message"])
    except ValueError as e:
        return fail(msg=str(e))
    except Exception as e:
        return fail(msg=f"操作失败: {str(e)}")


@router.get("/bookmarks", response_model=dict)
async def get_bookmarks(
    user_id: str = Query(..., description="用户ID"),
    current_user_id: Optional[str] = Query(None, description="当前用户ID (用于判断点赞/收藏状态)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的收藏列表"""
    try:
        result = await SquareService.get_user_bookmarks(
            db,
            user_id,
            current_user_id or user_id,
            page,
            page_size
        )
        return success(data=result.model_dump(), msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取失败: {str(e)}")

