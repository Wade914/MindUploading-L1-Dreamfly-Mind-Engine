"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 文件上传 - 业务逻辑服务
"""

import os
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import UploadFile, HTTPException
from core.exception import UnicornException
from core.path_manager import get_path_manager

from .models import Upload
from .params import UploadParams, GetUploadListParams, UploadType
from .schemas import UploadResponseSchema, UploadListResponseSchema, UploadSchema


class UploadService:
    """文件上传服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.path_manager = get_path_manager()
        # 目录已经在path_manager初始化时创建

    def _validate_file(self, file: UploadFile, upload_type: UploadType) -> None:
        """验证文件"""
        # 检查文件大小
        size_limit = self.path_manager.get_file_size_limit(upload_type.value)
        if hasattr(file, 'size') and file.size:
            if file.size > size_limit:
                raise UnicornException(
                    code=400,
                    errmsg=f"文件大小超过限制({size_limit // (1024*1024)}MB)"
                )

        # 检查文件类型
        allowed_types = self.path_manager.get_allowed_types(upload_type.value)
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_types:
                raise UnicornException(
                    code=400,
                    errmsg=f"不支持的文件类型，支持: {', '.join(allowed_types)}"
                )

    def _generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        file_ext = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"

    async def upload_file(
        self, 
        file: UploadFile, 
        params: UploadParams
    ) -> UploadResponseSchema:
        """上传文件"""
        # 验证文件
        self._validate_file(file, params.upload_type)
        
        # 生成保存文件名
        saved_filename = self._generate_filename(file.filename)
        
        # 确定保存路径
        type_dir = self.path_manager.get_upload_dir(params.upload_type.value)
        file_path = type_dir / saved_filename
        
        # 保存文件
        try:
            with open(str(file_path), "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                file_size = len(content)
        except Exception as e:
            raise UnicornException(code=500, errmsg=f"文件保存失败: {str(e)}")

        # 记录到数据库
        upload_record = Upload(
            user_id=params.user_id,
            original_filename=file.filename,
            saved_filename=saved_filename,
            file_path=str(file_path),
            file_type=file.content_type,
            file_size=file_size,
            upload_type=params.upload_type.value
        )
        
        self.db.add(upload_record)
        await self.db.flush()
        await self.db.refresh(upload_record)
        
        return UploadResponseSchema(
            file_id=upload_record.id,
            original_filename=upload_record.original_filename,
            saved_filename=upload_record.saved_filename,
            file_size=upload_record.file_size,
            upload_type=upload_record.upload_type,
            upload_time=upload_record.created_at
        )

    async def get_upload_list(self, params: GetUploadListParams) -> UploadListResponseSchema:
        """获取上传列表"""
        # 构建查询
        query = select(Upload)
        count_query = select(func.count(Upload.id))
        
        if params.user_id:
            query = query.where(Upload.user_id == params.user_id)
            count_query = count_query.where(Upload.user_id == params.user_id)
            
        if params.upload_type:
            query = query.where(Upload.upload_type == params.upload_type.value)
            count_query = count_query.where(Upload.upload_type == params.upload_type.value)

        # 获取总数
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 分页查询，按创建时间倒序
        query = query.order_by(Upload.created_at.desc())
        query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
        result = await self.db.execute(query)
        uploads = result.scalars().all()

        return UploadListResponseSchema(
            items=[UploadSchema.model_validate(upload) for upload in uploads],
            total=total,
            page=params.page,
            page_size=params.page_size
        )

    async def delete_upload(self, file_id: str, user_id: str) -> bool:
        """删除上传文件"""
        # 查找文件记录
        query = select(Upload).where(Upload.id == file_id, Upload.user_id == user_id)
        result = await self.db.execute(query)
        upload_record = result.scalar_one_or_none()
        
        if not upload_record:
            raise UnicornException(code=404, errmsg="文件不存在")
        
        # 删除物理文件
        try:
            if os.path.exists(upload_record.file_path):
                os.remove(upload_record.file_path)
        except Exception as e:
            # 文件删除失败不影响数据库记录删除
            pass
        
        # 删除数据库记录
        await self.db.delete(upload_record)
        return True