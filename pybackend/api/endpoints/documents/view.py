"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 文档管理 - API接口
"""

import os
import uuid
from urllib.parse import quote
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.session import get_db
from core.response import success, fail
from .models import UpdateDocumentRequest, CreateTransactionRequest
from .service import DocumentService, TransactionService

router = APIRouter(prefix="/api/user", tags=["文档管理"])

# 文件上传配置
UPLOAD_DIR = "uploads/documents"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx", ".md"}

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/documents", response_model=dict)
async def get_user_documents(
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的文档列表"""
    try:
        documents = await DocumentService.get_user_documents(db, user_id)
        return success(data={"documents": [doc.model_dump() for doc in documents]})
    except Exception as e:
        return fail(msg=f"获取文档列表失败: {str(e)}")


@router.post("/documents/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """上传文档文件"""
    try:
        # 验证文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return fail(msg=f"不支持的文件类型: {file_ext}")
        
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return fail(msg=f"文件大小超过限制: {MAX_FILE_SIZE / 1024 / 1024}MB")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 创建数据库记录
        document = await DocumentService.create_document_record(
            db, user_id, file.filename, file_ext, len(file_content), file_path
        )
        
        return success(
            data={
                "document": document.model_dump(),
                "upload_info": {
                    "document_id": document.id,
                    "filename": document.filename,
                    "file_size": document.file_size,
                    "status": document.status
                }
            },
            msg="文档上传成功"
        )
    
    except Exception as e:
        return fail(msg=f"文档上传失败: {str(e)}")


@router.get("/documents/{doc_id}", response_model=dict)
async def get_document(
    doc_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定的文档详情"""
    try:
        document = await DocumentService.get_document_by_id(db, doc_id)
        if not document:
            return fail(code=404, msg="文档不存在")
        
        # 验证所有权
        if document.user_id != user_id:
            return fail(code=403, msg="无权访问此文档")
        
        return success(data={"document": document.model_dump()})
    except Exception as e:
        return fail(msg=f"获取文档详情失败: {str(e)}")


@router.put("/documents/{doc_id}", response_model=dict)
async def update_document(
    doc_id: int,
    update_data: UpdateDocumentRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新文档"""
    try:
        document = await DocumentService.update_document(db, doc_id, user_id, update_data)
        if not document:
            return fail(code=404, msg="文档不存在或无权修改")
        
        return success(data={"document": document.model_dump()}, msg="文档更新成功")
    except Exception as e:
        return fail(msg=f"更新文档失败: {str(e)}")


@router.delete("/documents/{doc_id}", response_model=dict)
async def delete_document(
    doc_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    try:
        success_deleted = await DocumentService.delete_document(db, doc_id, user_id)
        if not success_deleted:
            return fail(code=404, msg="文档不存在或无权删除")
        
        return success(msg="文档删除成功")
    except Exception as e:
        return fail(msg=f"删除文档失败: {str(e)}")


@router.get("/documents/{doc_id}/download")
async def download_document(
    doc_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """下载文档文件"""
    try:
        # 获取文档信息
        document = await DocumentService.get_document_by_id(db, doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 验证所有权
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此文档")

        # 检查文件是否存在
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 返回文件
        # 对中文文件名进行URL编码以避免编码错误
        encoded_filename = quote(document.filename, safe='')
        return FileResponse(
            path=document.file_path,
            filename=document.filename,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.get("/documents/{doc_id}/preview")
async def preview_document(
    doc_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """预览文档文件"""
    try:
        # 获取文档信息
        document = await DocumentService.get_document_by_id(db, doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 验证所有权
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此文档")

        # 检查文件是否存在
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 根据文件类型设置合适的媒体类型
        media_type_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        file_ext = os.path.splitext(document.filename)[1].lower()
        media_type = media_type_map.get(file_ext, 'application/octet-stream')

        # 返回文件用于预览（inline显示而不是下载）
        # 对中文文件名进行URL编码以避免编码错误
        encoded_filename = quote(document.filename, safe='')
        return FileResponse(
            path=document.file_path,
            filename=document.filename,
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览文件失败: {str(e)}")


@router.get("/transactions", response_model=dict)
async def get_user_transactions(
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的交易记录"""
    try:
        transactions = await TransactionService.get_user_transactions(db, user_id)
        return success(data={"transactions": [trans.model_dump() for trans in transactions]})
    except Exception as e:
        return fail(msg=f"获取交易记录失败: {str(e)}")


@router.post("/transactions", response_model=dict)
async def create_transaction(
    transaction_data: CreateTransactionRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建交易记录"""
    try:
        transaction = await TransactionService.create_transaction(db, user_id, transaction_data)
        return success(data={"transaction": transaction.model_dump()}, msg="交易创建成功")
    except Exception as e:
        return fail(msg=f"创建交易失败: {str(e)}")


@router.get("/market/consciousness-items", response_model=dict)
async def get_market_consciousness_items(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """获取市场上的意识体商品"""
    try:
        items = await TransactionService.get_market_consciousness_items(db, limit)
        return success(data={"items": [item.model_dump() for item in items]})
    except Exception as e:
        return fail(msg=f"获取市场商品失败: {str(e)}")
