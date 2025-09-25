"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 记忆片段管理 - API接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.session import get_db
from core.response import success, fail
from .models import CreateMemoryRequest, UpdateMemoryRequest, CreateTestResultRequest
from .service import MemoryService, TestResultService

router = APIRouter(prefix="/api/user", tags=["记忆片段管理"])


@router.get("/memory-fragments", response_model=dict)
async def get_user_memory_fragments(
    user_id: str = Query(..., description="用户ID"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的记忆片段列表"""
    try:
        fragments = await MemoryService.get_user_memory_fragments(db, user_id, category)
        return success(data={"fragments": [fragment.model_dump() for fragment in fragments]})
    except Exception as e:
        return fail(msg=f"获取记忆片段失败: {str(e)}")


@router.post("/memory-fragments", response_model=dict)
async def create_memory_fragment(
    memory_data: CreateMemoryRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建新的记忆片段"""
    try:
        fragment = await MemoryService.create_memory_fragment(db, user_id, memory_data)
        return success(data={"fragment": fragment.model_dump()}, msg="记忆片段创建成功")
    except Exception as e:
        return fail(msg=f"创建记忆片段失败: {str(e)}")


@router.get("/memory-fragments/{fragment_id}", response_model=dict)
async def get_memory_fragment(
    fragment_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定的记忆片段详情"""
    try:
        fragment = await MemoryService.get_memory_fragment_by_id(db, fragment_id)
        if not fragment:
            return fail(code=404, msg="记忆片段不存在")
        
        # 验证所有权
        if fragment.user_id != user_id:
            return fail(code=403, msg="无权访问此记忆片段")
        
        return success(data={"fragment": fragment.model_dump()})
    except Exception as e:
        return fail(msg=f"获取记忆片段详情失败: {str(e)}")


@router.put("/memory-fragments/{fragment_id}", response_model=dict)
async def update_memory_fragment(
    fragment_id: int,
    memory_data: UpdateMemoryRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新记忆片段"""
    try:
        fragment = await MemoryService.update_memory_fragment(db, fragment_id, user_id, memory_data)
        if not fragment:
            return fail(code=404, msg="记忆片段不存在或无权修改")
        
        return success(data={"fragment": fragment.model_dump()}, msg="记忆片段更新成功")
    except Exception as e:
        return fail(msg=f"更新记忆片段失败: {str(e)}")


@router.delete("/memory-fragments/{fragment_id}", response_model=dict)
async def delete_memory_fragment(
    fragment_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除记忆片段"""
    try:
        success_deleted = await MemoryService.delete_memory_fragment(db, fragment_id, user_id)
        if not success_deleted:
            return fail(code=404, msg="记忆片段不存在或无权删除")
        
        return success(msg="记忆片段删除成功")
    except Exception as e:
        return fail(msg=f"删除记忆片段失败: {str(e)}")


@router.get("/test-results", response_model=dict)
async def get_user_test_results(
    user_id: str = Query(..., description="用户ID"),
    test_type: Optional[str] = Query(None, description="测试类型筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的测试结果列表"""
    try:
        test_results = await TestResultService.get_user_test_results(db, user_id, test_type)
        return success(data={"test_results": [result.model_dump() for result in test_results]})
    except Exception as e:
        return fail(msg=f"获取测试结果失败: {str(e)}")


@router.post("/test-results", response_model=dict)
async def create_test_result(
    test_data: CreateTestResultRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建测试结果"""
    try:
        test_result = await TestResultService.create_test_result(db, user_id, test_data)
        return success(data={"test_result": test_result.model_dump()}, msg="测试结果保存成功")
    except Exception as e:
        return fail(msg=f"保存测试结果失败: {str(e)}")


@router.get("/test-results/{test_id}", response_model=dict)
async def get_test_result(
    test_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定的测试结果详情"""
    try:
        test_result = await TestResultService.get_test_result_by_id(db, test_id)
        if not test_result:
            return fail(code=404, msg="测试结果不存在")
        
        # 验证所有权
        if test_result.user_id != user_id:
            return fail(code=403, msg="无权访问此测试结果")
        
        return success(data={"test_result": test_result.model_dump()})
    except Exception as e:
        return fail(msg=f"获取测试结果详情失败: {str(e)}")
