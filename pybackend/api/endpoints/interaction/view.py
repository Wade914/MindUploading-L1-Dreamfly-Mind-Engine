"""
@Created on: 2025/01/18 10:00
@Author: DreamFly Team
@Des: 交互管理 - API视图
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from core.response import success

from .params import RecordInteractionParams, UpdateInteractionCountParams
from .schemas import InteractionRecordSchema, InteractionStatsSchema
from .service import InteractionService

router = APIRouter(prefix="/interaction", tags=["交互管理"])


@router.post("/record", summary="记录交互历史")
async def record_interaction(
    params: RecordInteractionParams,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    记录用户与意识体的交互历史
    
    - **user_id**: 用户ID
    - **mind_name**: 意识体名称
    - **user_message**: 用户消息
    - **ai_response**: AI回复
    - **tokens_used**: 使用的token数量
    """
    service = InteractionService(db)
    result = await service.record_interaction(params)
    return success(data=result.model_dump(), msg="交互记录成功")


@router.post("/update-count", summary="更新交互次数")
async def update_interaction_count(
    params: UpdateInteractionCountParams,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    更新用户与意识体的交互次数
    
    - **user_id**: 用户ID
    - **mind_name**: 意识体名称
    - **increment**: 增加的次数（默认1）
    """
    service = InteractionService(db)
    await service.update_interaction_count(params)
    return success(msg="交互次数更新成功")


@router.get("/stats", summary="获取交互统计")
async def get_interaction_stats(
    user_id: str,
    mind_name: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取用户与特定意识体的交互统计
    
    - **user_id**: 用户ID
    - **mind_name**: 意识体名称
    """
    service = InteractionService(db)
    result = await service.get_interaction_stats(user_id, mind_name)
    return success(data=result.model_dump(), msg="获取统计成功")
