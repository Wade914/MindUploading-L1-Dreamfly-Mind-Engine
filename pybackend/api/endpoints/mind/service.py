"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 意识体管理 - 业务逻辑服务
"""

import os
import json
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from fastapi import HTTPException, status
from core.exception import UnicornException
from cfg.config import settings
from core.path_manager import get_path_manager

from .models import Mind
from .params import CreateMindParams, GetMindParams, ListMindParams
from .schemas import (
    CreateMindResponseSchema, 
    MindListResponseSchema, 
    MindSchema, 
    MindContentResponseSchema
)


class MindService:
    """意识体管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.path_manager = get_path_manager()
        self.minds_dir = str(self.path_manager.minds_dir)

    def _generate_filename(self, name: str) -> str:
        """生成文件名"""
        return f"{name}.mind"

    async def create_mind(self, params: CreateMindParams) -> CreateMindResponseSchema:
        """创建意识体"""
        filename = self._generate_filename(params.name)
        
        # 检查是否已存在同名意识体（防止重复创建）
        query = select(Mind).where(
            Mind.user_id == params.user_id,
            Mind.name == params.name
        )
        result = await self.db.execute(query)
        existing_mind = result.scalar_one_or_none()

        if existing_mind:
            raise UnicornException(code=400, errmsg=f"意识体 '{params.name}' 已存在")

        # 保存文件内容到磁盘
        file_path = os.path.join(self.minds_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(params.mind_content)
        except Exception as e:
            raise UnicornException(code=500, errmsg=f"保存文件失败: {str(e)}")

        # 创建数据库记录
        mind = Mind(
            user_id=params.user_id,
            name=params.name,
            birth=params.birth,
            type=params.type,
            protocol=params.protocol,
            blockchain=params.blockchain,
            filename=filename,
            content=params.mind_content
        )

        self.db.add(mind)
        await self.db.flush()
        await self.db.refresh(mind)

        # 同步数据到 user_profiles 表
        await self._sync_to_user_profile(params.user_id, params.mind_content)

        return CreateMindResponseSchema(
            mind_id=mind.id,
            filename=filename,
            created=mind.created_at
        )

    async def get_mind_list(self, params: ListMindParams) -> MindListResponseSchema:
        """获取意识体列表"""
        # 构建查询
        query = select(Mind)
        count_query = select(func.count(Mind.id))
        
        if params.user_id:
            query = query.where(Mind.user_id == params.user_id)
            count_query = count_query.where(Mind.user_id == params.user_id)

        # 获取总数
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 分页查询
        query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
        result = await self.db.execute(query)
        minds = result.scalars().all()

        return MindListResponseSchema(
            items=[MindSchema.model_validate(mind) for mind in minds],
            total=total,
            page=params.page,
            page_size=params.page_size
        )

    async def get_mind_content(self, filename: str) -> MindContentResponseSchema:
        """获取意识体内容"""
        # 首先从数据库查找
        query = select(Mind).where(Mind.filename == filename)
        result = await self.db.execute(query)
        mind = result.scalar_one_or_none()
        
        if not mind:
            raise UnicornException(code=404, errmsg="意识体不存在")

        # 如果数据库中有内容，直接返回
        if mind.content:
            return MindContentResponseSchema(
                filename=filename,
                content=mind.content
            )

        # 否则从文件读取
        file_path = os.path.join(self.minds_dir, filename)
        if not os.path.exists(file_path):
            raise UnicornException(code=404, errmsg="意识体文件不存在")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return MindContentResponseSchema(
                filename=filename,
                content=content
            )
        except Exception as e:
            raise UnicornException(code=500, errmsg=f"读取文件失败: {str(e)}")

    async def get_mind_filenames(self) -> List[str]:
        """获取所有意识体文件名（兼容旧API）"""
        # 从数据库获取所有文件名
        query = select(Mind.filename)
        result = await self.db.execute(query)
        filenames = result.scalars().all()
        
        # 标准化文件名（确保以.mind结尾）
        normalized_filenames = []
        for filename in filenames:
            if filename.endswith('.mind.js'):
                normalized_filenames.append(filename.replace('.mind.js', '.mind'))
            elif not filename.endswith('.mind'):
                normalized_filenames.append(f"{filename}.mind")
            else:
                normalized_filenames.append(filename)
                
        return normalized_filenames

    async def delete_mind(self, mind_id: str, user_id: str) -> dict:
        """删除意识体"""
        # 查找意识体
        query = select(Mind).where(Mind.id == mind_id)
        result = await self.db.execute(query)
        mind = result.scalar_one_or_none()

        if not mind:
            raise UnicornException(code=404, errmsg="意识体不存在")

        # 验证所有权
        if mind.user_id != user_id:
            raise UnicornException(code=403, errmsg="无权删除此意识体")

        # 删除文件（如果存在）
        if mind.filename:
            file_path = os.path.join(self.minds_dir, mind.filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"删除文件失败: {str(e)}")

        # 删除数据库记录
        await self.db.delete(mind)
        await self.db.commit()

        return {"deleted_id": mind_id, "filename": mind.filename}

    async def _sync_to_user_profile(self, user_id: str, mind_content: str):
        """同步 mind 数据到 user_profiles 表"""
        try:
            # 解析 mind 内容 (JSON 格式)
            mind_data = json.loads(mind_content)

            # 提取基本信息
            metadata = mind_data.get('metadata', {})
            memory = mind_data.get('memory', {})

            name = metadata.get('name', '')
            birth = metadata.get('birth', '')
            self_cognition = memory.get('self_cognition', '')

            # 确保 user_profiles 记录存在
            check_sql = "SELECT id FROM user_profiles WHERE user_id = :user_id"
            result = await self.db.execute(text(check_sql), {"user_id": user_id})
            profile_exists = result.fetchone() is not None

            if not profile_exists:
                # 创建 user_profiles 记录
                insert_sql = """
                INSERT INTO user_profiles (user_id, bio, created_at, updated_at)
                VALUES (:user_id, :bio, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                await self.db.execute(text(insert_sql), {
                    "user_id": user_id,
                    "bio": self_cognition[:500] if self_cognition else ''  # 限制长度
                })
            else:
                # 更新 user_profiles 记录 (只更新为空的字段)
                update_sql = """
                UPDATE user_profiles
                SET bio = CASE WHEN bio IS NULL OR bio = '' THEN :bio ELSE bio END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id
                """
                await self.db.execute(text(update_sql), {
                    "user_id": user_id,
                    "bio": self_cognition[:500] if self_cognition else ''
                })

            # 更新 users 表的 birth 字段 (如果为空)
            if birth:
                update_user_sql = """
                UPDATE users
                SET birth = CASE WHEN birth IS NULL OR birth = '' THEN :birth ELSE birth END
                WHERE id = :user_id
                """
                await self.db.execute(text(update_user_sql), {
                    "user_id": user_id,
                    "birth": birth
                })

            await self.db.commit()

        except json.JSONDecodeError:
            # 如果 mind_content 不是有效的 JSON,忽略同步
            print(f"Mind content is not valid JSON, skipping sync for user {user_id}")
        except Exception as e:
            # 同步失败不影响 mind 创建,只记录错误
            print(f"Failed to sync mind data to user_profile: {str(e)}")