"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 文件上传 - API视图
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from core.response import success
from typing import Optional

from .params import UploadParams, GetUploadListParams, UploadType
from .service import UploadService

router = APIRouter()


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(..., description="用户ID"),
    upload_type: UploadType = Form(..., description="上传类型"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    上传文件
    
    - **file**: 上传的文件
    - **user_id**: 用户ID
    - **upload_type**: 上传类型 (thought/voice/image)
    
    文件大小限制：
    - 思想数据: 5MB
    - 声音数据: 10MB
    - 形象数据: 20MB
    """
    params = UploadParams(user_id=user_id, upload_type=upload_type)
    service = UploadService(db)
    result = await service.upload_file(file, params)
    return success(data=result.model_dump(), msg="文件上传成功")


@router.get("/uploads", summary="获取上传列表")
async def get_upload_list(
    user_id: Optional[str] = Query(None, description="用户ID"),
    upload_type: Optional[UploadType] = Query(None, description="上传类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取上传列表
    
    - **user_id**: 用户ID（可选）
    - **upload_type**: 上传类型（可选）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    params = GetUploadListParams(
        user_id=user_id,
        upload_type=upload_type,
        page=page,
        page_size=page_size
    )
    service = UploadService(db)
    result = await service.get_upload_list(params)
    return success(data=result.model_dump(), msg="获取成功")


@router.delete("/upload/{file_id}", summary="删除上传文件")
async def delete_upload(
    file_id: str,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    删除上传文件
    
    - **file_id**: 文件ID
    - **user_id**: 用户ID
    """
    service = UploadService(db)
    await service.delete_upload(file_id, user_id)
    return success(msg="文件删除成功")