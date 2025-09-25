"""
@Created on: 2025/09/15
@Author: DreamFly Team
@Des: 笔记管理 - 业务逻辑
"""

import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from .models import CreateNoteRequest, UpdateNoteRequest, NoteResponse, CreateFolderRequest, FolderResponse


class NotesService:
    """笔记服务类"""
    
    @staticmethod
    async def create_note(db: AsyncSession, user_id: str, note_data: CreateNoteRequest) -> NoteResponse:
        """创建笔记"""
        # 生成预览文本（前50个字符）
        preview = note_data.content[:50] + "..." if len(note_data.content) > 50 else note_data.content
        
        # 将标签转换为JSON字符串
        tags_json = json.dumps(note_data.tags) if note_data.tags else "[]"
        
        # 插入笔记数据
        insert_sql = """
        INSERT INTO notes (user_id, title, content, folder_id, tags, preview, created_at, updated_at)
        VALUES (:user_id, :title, :content, :folder_id, :tags, :preview, :created_at, :updated_at)
        """
        
        now = datetime.now().isoformat()
        
        result = await db.execute(text(insert_sql), {
            "user_id": user_id,
            "title": note_data.title,
            "content": note_data.content,
            "folder_id": note_data.folder_id,
            "tags": tags_json,
            "preview": preview,
            "created_at": now,
            "updated_at": now
        })
        
        await db.commit()
        
        # 获取插入的ID
        note_id = result.lastrowid
        
        # 返回创建的笔记
        return await NotesService.get_note_by_id(db, note_id)
    
    @staticmethod
    async def get_notes_by_user(db: AsyncSession, user_id: str, folder_id: Optional[str] = None) -> List[NoteResponse]:
        """获取用户的笔记列表"""
        if folder_id:
            query_sql = """
            SELECT id, user_id, title, content, folder_id, tags, preview, created_at, updated_at
            FROM notes
            WHERE user_id = :user_id AND folder_id = :folder_id
            ORDER BY updated_at DESC
            """
            result = await db.execute(text(query_sql), {"user_id": user_id, "folder_id": folder_id})
        else:
            query_sql = """
            SELECT id, user_id, title, content, folder_id, tags, preview, created_at, updated_at
            FROM notes
            WHERE user_id = :user_id AND (folder_id IS NULL OR folder_id = '')
            ORDER BY updated_at DESC
            """
            result = await db.execute(text(query_sql), {"user_id": user_id})

        notes = []
        for row in result.fetchall():
            # 解析标签JSON
            tags = json.loads(row.tags) if row.tags else []

            notes.append(NoteResponse(
                id=row.id,
                user_id=row.user_id,
                title=row.title,
                content=row.content,
                folder_id=row.folder_id,
                tags=tags,
                preview=row.preview,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))

        return notes

    @staticmethod
    async def get_all_notes_by_user(db: AsyncSession, user_id: str) -> List[NoteResponse]:
        """获取用户的所有笔记（不按文件夹过滤）"""
        query_sql = """
        SELECT id, user_id, title, content, folder_id, tags, preview, created_at, updated_at
        FROM notes
        WHERE user_id = :user_id
        ORDER BY updated_at DESC
        """
        result = await db.execute(text(query_sql), {"user_id": user_id})
        
        notes = []
        for row in result.fetchall():
            # 解析标签JSON
            tags = json.loads(row.tags) if row.tags else []
            
            notes.append(NoteResponse(
                id=row.id,
                user_id=row.user_id,
                title=row.title,
                content=row.content,
                folder_id=row.folder_id,
                tags=tags,
                preview=row.preview,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return notes
    
    @staticmethod
    async def get_note_by_id(db: AsyncSession, note_id: int) -> Optional[NoteResponse]:
        """根据ID获取笔记"""
        query_sql = """
        SELECT id, user_id, title, content, folder_id, tags, preview, created_at, updated_at
        FROM notes 
        WHERE id = :note_id
        """
        
        result = await db.execute(text(query_sql), {"note_id": note_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # 解析标签JSON
        tags = json.loads(row.tags) if row.tags else []
        
        return NoteResponse(
            id=row.id,
            user_id=row.user_id,
            title=row.title,
            content=row.content,
            folder_id=row.folder_id,
            tags=tags,
            preview=row.preview,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    @staticmethod
    async def update_note(db: AsyncSession, note_id: int, user_id: str, note_data: UpdateNoteRequest) -> Optional[NoteResponse]:
        """更新笔记"""
        # 首先检查笔记是否存在且属于该用户
        existing_note = await NotesService.get_note_by_id(db, note_id)
        if not existing_note or existing_note.user_id != user_id:
            return None
        
        # 构建更新字段
        update_fields = []
        params = {"note_id": note_id, "updated_at": datetime.now().isoformat()}
        
        if note_data.title is not None:
            update_fields.append("title = :title")
            params["title"] = note_data.title
        
        if note_data.content is not None:
            update_fields.append("content = :content")
            update_fields.append("preview = :preview")
            params["content"] = note_data.content
            params["preview"] = note_data.content[:50] + "..." if len(note_data.content) > 50 else note_data.content
        
        if note_data.folder_id is not None:
            update_fields.append("folder_id = :folder_id")
            params["folder_id"] = note_data.folder_id
        
        if note_data.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = json.dumps(note_data.tags)
        
        if not update_fields:
            return existing_note
        
        update_fields.append("updated_at = :updated_at")
        
        update_sql = f"""
        UPDATE notes 
        SET {', '.join(update_fields)}
        WHERE id = :note_id
        """
        
        await db.execute(text(update_sql), params)
        await db.commit()
        
        # 返回更新后的笔记
        return await NotesService.get_note_by_id(db, note_id)
    
    @staticmethod
    async def delete_note(db: AsyncSession, note_id: int, user_id: str) -> bool:
        """删除笔记"""
        # 首先检查笔记是否存在且属于该用户
        existing_note = await NotesService.get_note_by_id(db, note_id)
        if not existing_note or existing_note.user_id != user_id:
            return False
        
        delete_sql = "DELETE FROM notes WHERE id = :note_id"
        await db.execute(text(delete_sql), {"note_id": note_id})
        await db.commit()
        
        return True


class FoldersService:
    """文件夹服务类"""
    
    @staticmethod
    async def create_folder(db: AsyncSession, user_id: str, folder_data: CreateFolderRequest) -> FolderResponse:
        """创建文件夹"""
        import uuid
        folder_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        insert_sql = """
        INSERT INTO note_folders (id, user_id, name, parent_id, created_at)
        VALUES (:id, :user_id, :name, :parent_id, :created_at)
        """
        
        await db.execute(text(insert_sql), {
            "id": folder_id,
            "user_id": user_id,
            "name": folder_data.name,
            "parent_id": folder_data.parent_id,
            "created_at": now
        })
        
        await db.commit()
        
        return FolderResponse(
            id=folder_id,
            user_id=user_id,
            name=folder_data.name,
            parent_id=folder_data.parent_id,
            created_at=now
        )
    
    @staticmethod
    async def get_folders_by_user(db: AsyncSession, user_id: str) -> List[FolderResponse]:
        """获取用户的文件夹列表"""
        query_sql = """
        SELECT id, user_id, name, parent_id, created_at
        FROM note_folders 
        WHERE user_id = :user_id
        ORDER BY created_at ASC
        """
        
        result = await db.execute(text(query_sql), {"user_id": user_id})
        
        folders = []
        for row in result.fetchall():
            folders.append(FolderResponse(
                id=row.id,
                user_id=row.user_id,
                name=row.name,
                parent_id=row.parent_id,
                created_at=row.created_at
            ))
        
        return folders
