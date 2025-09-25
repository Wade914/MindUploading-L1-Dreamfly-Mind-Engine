"""
@Created on: 2025/09/15
@Author: DreamFly Team
@Des: 笔记管理 - API接口
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from database.session import get_db
from core.response import success, fail
from .models import CreateNoteRequest, UpdateNoteRequest, CreateFolderRequest
from .service import NotesService, FoldersService

router = APIRouter(prefix="/api/user", tags=["笔记管理"])


@router.post("/notes", response_model=dict)
async def create_note(
    note_data: CreateNoteRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建新笔记"""
    try:
        note = await NotesService.create_note(db, user_id, note_data)
        return success(data={"note": note.model_dump()}, msg="笔记创建成功")
    except Exception as e:
        return fail(msg=f"创建笔记失败: {str(e)}")


@router.get("/notes", response_model=dict)
async def get_notes(
    user_id: str = Query(..., description="用户ID"),
    folder_id: Optional[str] = Query(None, description="文件夹ID"),
    all_notes: bool = Query(False, description="是否获取所有笔记"),
    db: AsyncSession = Depends(get_db)
):
    """获取笔记列表"""
    try:
        if all_notes:
            notes = await NotesService.get_all_notes_by_user(db, user_id)
        else:
            notes = await NotesService.get_notes_by_user(db, user_id, folder_id)
        return success(data={"notes": [note.model_dump() for note in notes]}, msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取笔记失败: {str(e)}")


@router.get("/notes/{note_id}", response_model=dict)
async def get_note_detail(
    note_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取笔记详情"""
    try:
        note = await NotesService.get_note_by_id(db, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
        
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此笔记")
        
        return success(data={"note": note.model_dump()}, msg="获取成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"获取笔记详情失败: {str(e)}")


@router.put("/notes/{note_id}", response_model=dict)
async def update_note(
    note_id: int,
    note_data: UpdateNoteRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新笔记"""
    try:
        note = await NotesService.update_note(db, note_id, user_id, note_data)
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在或无权访问")
        
        return success(data={"note": note.model_dump()}, msg="笔记更新成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"更新笔记失败: {str(e)}")


@router.delete("/notes/{note_id}", response_model=dict)
async def delete_note(
    note_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除笔记"""
    try:
        success_deleted = await NotesService.delete_note(db, note_id, user_id)
        if not success_deleted:
            raise HTTPException(status_code=404, detail="笔记不存在或无权访问")
        
        return success(msg="笔记删除成功")
    except HTTPException:
        raise
    except Exception as e:
        return fail(msg=f"删除笔记失败: {str(e)}")


@router.post("/note-folders", response_model=dict)
async def create_folder(
    folder_data: CreateFolderRequest,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """创建文件夹"""
    try:
        folder = await FoldersService.create_folder(db, user_id, folder_data)
        return success(data={"folder": folder.model_dump()}, msg="文件夹创建成功")
    except Exception as e:
        return fail(msg=f"创建文件夹失败: {str(e)}")


@router.get("/note-folders", response_model=dict)
async def get_folders(
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取文件夹列表"""
    try:
        folders = await FoldersService.get_folders_by_user(db, user_id)
        return success(data={"folders": [folder.model_dump() for folder in folders]}, msg="获取成功")
    except Exception as e:
        return fail(msg=f"获取文件夹失败: {str(e)}")
