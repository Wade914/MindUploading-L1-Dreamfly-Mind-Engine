"""
@Created on: 2025/01/16
@Author: DreamFly Team
@Des: Square 广场 - 业务逻辑
"""

import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Tuple
from .models import (
    CreateThoughtRequest, UpdateThoughtRequest, ThoughtCellResponse,
    CreateCommentRequest, CommentResponse,
    UserProfileResponse, UpdateProfileRequest,
    ThoughtListResponse, CommentListResponse, UserListResponse,
    BookmarkThoughtCellResponse, BookmarkListResponse
)


class SquareService:
    """Square 广场服务类"""
    
    # ==================== 思想元胞相关方法 ====================
    
    @staticmethod
    async def create_thought(db: AsyncSession, user_id: str, thought_data: CreateThoughtRequest) -> ThoughtCellResponse:
        """创建思想元胞"""
        # 将列表转换为 JSON 字符串
        images_json = json.dumps(thought_data.images) if thought_data.images else "[]"
        tags_json = json.dumps(thought_data.tags) if thought_data.tags else "[]"
        
        # 插入思想元胞数据
        insert_sql = """
        INSERT INTO thought_cells (user_id, content, images, visibility, tags, location, created_at, updated_at)
        VALUES (:user_id, :content, :images, :visibility, :tags, :location, :created_at, :updated_at)
        """
        
        now = datetime.now().isoformat()
        
        result = await db.execute(text(insert_sql), {
            "user_id": user_id,
            "content": thought_data.content,
            "images": images_json,
            "visibility": thought_data.visibility,
            "tags": tags_json,
            "location": thought_data.location,
            "created_at": now,
            "updated_at": now
        })
        
        await db.commit()
        
        # 获取插入的ID
        thought_id = result.lastrowid
        
        # 更新用户的思想元胞计数
        await SquareService._update_user_thoughts_count(db, user_id, 1)
        
        # 返回创建的思想元胞
        return await SquareService.get_thought_by_id(db, thought_id, user_id)
    
    @staticmethod
    async def get_thoughts(
        db: AsyncSession,
        current_user_id: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ThoughtListResponse:
        """获取思想元胞列表 (支持分页和用户过滤)"""
        offset = (page - 1) * page_size

        # 构建查询条件
        where_clause = "WHERE 1=1"
        params = {"limit": page_size, "offset": offset}

        if user_id:
            where_clause += " AND tc.user_id = :user_id"
            params["user_id"] = user_id

        # 查询思想元胞列表
        query_sql = f"""
        SELECT
            tc.id, tc.user_id, tc.content, tc.images, tc.visibility,
            tc.likes_count, tc.comments_count, tc.shares_count, tc.tags, tc.location,
            tc.created_at, tc.updated_at,
            u.username,
            up.avatar_url
        FROM thought_cells tc
        LEFT JOIN users u ON tc.user_id = u.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        {where_clause}
        ORDER BY tc.created_at DESC
        LIMIT :limit OFFSET :offset
        """

        result = await db.execute(text(query_sql), params)
        rows = result.fetchall()

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM thought_cells tc {where_clause}"
        count_params = {k: v for k, v in params.items() if k not in ['limit', 'offset']}
        count_result = await db.execute(text(count_sql), count_params)
        total = count_result.scalar()

        # 构建响应
        thoughts = []
        for row in rows:
            # 检查当前用户是否已点赞、已关注、已收藏
            is_liked = False
            is_following = False
            is_bookmarked = False
            if current_user_id:
                is_liked = await SquareService._check_is_liked(db, row.id, current_user_id)
                is_bookmarked = await SquareService._check_is_bookmarked(db, row.id, current_user_id)
                # 检查是否已关注该作者（不检查自己）
                if current_user_id != row.user_id:
                    is_following = await SquareService._check_is_following(db, current_user_id, row.user_id)

            thoughts.append(ThoughtCellResponse(
                id=row.id,
                user_id=row.user_id,
                username=row.username or "未知用户",
                avatar_url=row.avatar_url,
                content=row.content,
                images=json.loads(row.images) if row.images else [],
                visibility=row.visibility,
                likes_count=row.likes_count,
                comments_count=row.comments_count,
                shares_count=row.shares_count,
                tags=json.loads(row.tags) if row.tags else [],
                location=row.location,
                created_at=row.created_at,
                updated_at=row.updated_at,
                is_liked=is_liked,
                is_following=is_following,
                is_bookmarked=is_bookmarked
            ))

        return ThoughtListResponse(
            thoughts=thoughts,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + len(thoughts)) < total
        )

    @staticmethod
    async def get_following_thoughts(
        db: AsyncSession,
        current_user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> ThoughtListResponse:
        """获取关注用户的思想元胞列表"""
        offset = (page - 1) * page_size

        # 查询关注用户的思想元胞
        query_sql = """
        SELECT
            tc.id, tc.user_id, tc.content, tc.images, tc.visibility,
            tc.likes_count, tc.comments_count, tc.shares_count, tc.tags, tc.location,
            tc.created_at, tc.updated_at,
            u.username,
            up.avatar_url
        FROM thought_cells tc
        INNER JOIN user_follows uf ON tc.user_id = uf.following_id
        LEFT JOIN users u ON tc.user_id = u.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        WHERE uf.follower_id = :current_user_id
        ORDER BY tc.created_at DESC
        LIMIT :limit OFFSET :offset
        """

        params = {
            "current_user_id": current_user_id,
            "limit": page_size,
            "offset": offset
        }

        result = await db.execute(text(query_sql), params)
        rows = result.fetchall()

        # 查询总数
        count_sql = """
        SELECT COUNT(*)
        FROM thought_cells tc
        INNER JOIN user_follows uf ON tc.user_id = uf.following_id
        WHERE uf.follower_id = :current_user_id
        """
        count_result = await db.execute(text(count_sql), {"current_user_id": current_user_id})
        total = count_result.scalar()
        
        # 构建响应
        thoughts = []
        for row in rows:
            # 检查当前用户是否已点赞、已关注、已收藏
            is_liked = False
            is_following = False
            is_bookmarked = False
            if current_user_id:
                is_liked = await SquareService._check_is_liked(db, row.id, current_user_id)
                is_bookmarked = await SquareService._check_is_bookmarked(db, row.id, current_user_id)
                # 检查是否已关注该作者（不检查自己）
                if current_user_id != row.user_id:
                    is_following = await SquareService._check_is_following(db, current_user_id, row.user_id)

            thoughts.append(ThoughtCellResponse(
                id=row.id,
                user_id=row.user_id,
                username=row.username or "未知用户",
                avatar_url=row.avatar_url,
                content=row.content,
                images=json.loads(row.images) if row.images else [],
                visibility=row.visibility,
                likes_count=row.likes_count,
                comments_count=row.comments_count,
                shares_count=row.shares_count,
                tags=json.loads(row.tags) if row.tags else [],
                location=row.location,
                created_at=row.created_at,
                updated_at=row.updated_at,
                is_liked=is_liked,
                is_following=is_following,
                is_bookmarked=is_bookmarked
            ))
        
        return ThoughtListResponse(
            thoughts=thoughts,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + len(thoughts)) < total
        )
    
    @staticmethod
    async def get_thought_by_id(db: AsyncSession, thought_id: int, current_user_id: Optional[str] = None) -> Optional[ThoughtCellResponse]:
        """获取单个思想元胞详情"""
        query_sql = """
        SELECT 
            tc.id, tc.user_id, tc.content, tc.images, tc.visibility,
            tc.likes_count, tc.comments_count, tc.shares_count, tc.tags, tc.location,
            tc.created_at, tc.updated_at,
            u.username,
            up.avatar_url
        FROM thought_cells tc
        LEFT JOIN users u ON tc.user_id = u.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        WHERE tc.id = :thought_id
        """
        
        result = await db.execute(text(query_sql), {"thought_id": thought_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # 检查当前用户是否已点赞、已收藏
        is_liked = False
        is_bookmarked = False
        if current_user_id:
            is_liked = await SquareService._check_is_liked(db, thought_id, current_user_id)
            is_bookmarked = await SquareService._check_is_bookmarked(db, thought_id, current_user_id)

        return ThoughtCellResponse(
            id=row.id,
            user_id=row.user_id,
            username=row.username or "未知用户",
            avatar_url=row.avatar_url,
            content=row.content,
            images=json.loads(row.images) if row.images else [],
            visibility=row.visibility,
            likes_count=row.likes_count,
            comments_count=row.comments_count,
            shares_count=row.shares_count,
            tags=json.loads(row.tags) if row.tags else [],
            location=row.location,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_liked=is_liked,
            is_bookmarked=is_bookmarked
        )
    
    @staticmethod
    async def delete_thought(db: AsyncSession, thought_id: int, user_id: str) -> bool:
        """删除思想元胞 (只能删除自己的)"""
        # 检查思想元胞是否存在且属于当前用户
        check_sql = "SELECT user_id FROM thought_cells WHERE id = :thought_id"
        result = await db.execute(text(check_sql), {"thought_id": thought_id})
        row = result.fetchone()
        
        if not row or row.user_id != user_id:
            return False
        
        # 删除相关的点赞
        await db.execute(text("DELETE FROM thought_likes WHERE thought_id = :thought_id"), {"thought_id": thought_id})
        
        # 删除相关的评论
        await db.execute(text("DELETE FROM thought_comments WHERE thought_id = :thought_id"), {"thought_id": thought_id})
        
        # 删除思想元胞
        await db.execute(text("DELETE FROM thought_cells WHERE id = :thought_id"), {"thought_id": thought_id})
        
        await db.commit()
        
        # 更新用户的思想元胞计数
        await SquareService._update_user_thoughts_count(db, user_id, -1)
        
        return True
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    async def _check_is_liked(db: AsyncSession, thought_id: int, user_id: str) -> bool:
        """检查用户是否已点赞"""
        query_sql = "SELECT 1 FROM thought_likes WHERE thought_id = :thought_id AND user_id = :user_id"
        result = await db.execute(text(query_sql), {"thought_id": thought_id, "user_id": user_id})
        return result.fetchone() is not None

    @staticmethod
    async def _check_is_following(db: AsyncSession, follower_id: str, following_id: str) -> bool:
        """检查用户是否已关注"""
        query_sql = "SELECT 1 FROM user_follows WHERE follower_id = :follower_id AND following_id = :following_id"
        result = await db.execute(text(query_sql), {"follower_id": follower_id, "following_id": following_id})
        return result.fetchone() is not None

    @staticmethod
    async def _check_is_bookmarked(db: AsyncSession, thought_id: int, user_id: str) -> bool:
        """检查用户是否已收藏"""
        query_sql = "SELECT 1 FROM thought_bookmarks WHERE thought_id = :thought_id AND user_id = :user_id"
        result = await db.execute(text(query_sql), {"thought_id": thought_id, "user_id": user_id})
        return result.fetchone() is not None

    @staticmethod
    async def _update_user_thoughts_count(db: AsyncSession, user_id: str, delta: int):
        """更新用户的思想元胞计数"""
        # 确保用户资料存在
        await SquareService._ensure_user_profile(db, user_id)
        
        # 更新计数
        update_sql = """
        UPDATE user_profiles 
        SET thoughts_count = thoughts_count + :delta,
            updated_at = :updated_at
        WHERE user_id = :user_id
        """
        await db.execute(text(update_sql), {
            "delta": delta,
            "updated_at": datetime.now().isoformat(),
            "user_id": user_id
        })
        await db.commit()
    
    @staticmethod
    async def _ensure_user_profile(db: AsyncSession, user_id: str):
        """确保用户资料存在 (如果不存在则创建)"""
        check_sql = "SELECT 1 FROM user_profiles WHERE user_id = :user_id"
        result = await db.execute(text(check_sql), {"user_id": user_id})

        if not result.fetchone():
            # 创建默认用户资料
            insert_sql = """
            INSERT INTO user_profiles (user_id, created_at, updated_at)
            VALUES (:user_id, :created_at, :updated_at)
            """
            now = datetime.now().isoformat()
            await db.execute(text(insert_sql), {
                "user_id": user_id,
                "created_at": now,
                "updated_at": now
            })
            await db.commit()

    # ==================== 点赞相关方法 ====================

    @staticmethod
    async def toggle_like(db: AsyncSession, thought_id: int, user_id: str) -> Tuple[bool, int]:
        """切换点赞状态 (点赞/取消点赞)

        Returns:
            Tuple[bool, int]: (是否已点赞, 当前点赞数)
        """
        # 检查是否已点赞
        check_sql = "SELECT id FROM thought_likes WHERE thought_id = :thought_id AND user_id = :user_id"
        result = await db.execute(text(check_sql), {"thought_id": thought_id, "user_id": user_id})
        existing = result.fetchone()

        if existing:
            # 取消点赞
            await db.execute(text("DELETE FROM thought_likes WHERE id = :id"), {"id": existing.id})
            delta = -1
            is_liked = False
        else:
            # 添加点赞
            insert_sql = """
            INSERT INTO thought_likes (thought_id, user_id, created_at)
            VALUES (:thought_id, :user_id, :created_at)
            """
            await db.execute(text(insert_sql), {
                "thought_id": thought_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            })
            delta = 1
            is_liked = True

        # 更新思想元胞的点赞计数
        update_sql = """
        UPDATE thought_cells
        SET likes_count = likes_count + :delta,
            updated_at = :updated_at
        WHERE id = :thought_id
        """
        await db.execute(text(update_sql), {
            "delta": delta,
            "updated_at": datetime.now().isoformat(),
            "thought_id": thought_id
        })

        await db.commit()

        # 获取当前点赞数
        count_sql = "SELECT likes_count FROM thought_cells WHERE id = :thought_id"
        count_result = await db.execute(text(count_sql), {"thought_id": thought_id})
        likes_count = count_result.scalar() or 0

        return (is_liked, likes_count)

    # ==================== 评论相关方法 ====================

    @staticmethod
    async def create_comment(db: AsyncSession, thought_id: int, user_id: str, comment_data: CreateCommentRequest) -> CommentResponse:
        """创建评论"""
        # 插入评论数据
        insert_sql = """
        INSERT INTO thought_comments (thought_id, user_id, content, parent_id, created_at, updated_at)
        VALUES (:thought_id, :user_id, :content, :parent_id, :created_at, :updated_at)
        """

        now = datetime.now().isoformat()

        result = await db.execute(text(insert_sql), {
            "thought_id": thought_id,
            "user_id": user_id,
            "content": comment_data.content,
            "parent_id": comment_data.parent_id,
            "created_at": now,
            "updated_at": now
        })

        # 更新思想元胞的评论计数
        update_sql = """
        UPDATE thought_cells
        SET comments_count = comments_count + 1,
            updated_at = :updated_at
        WHERE id = :thought_id
        """
        await db.execute(text(update_sql), {
            "updated_at": now,
            "thought_id": thought_id
        })

        await db.commit()

        # 获取插入的评论ID
        comment_id = result.lastrowid

        # 返回创建的评论
        return await SquareService._get_comment_by_id(db, comment_id)

    @staticmethod
    async def get_comments(db: AsyncSession, thought_id: int) -> CommentListResponse:
        """获取思想元胞的评论列表 (包含嵌套回复)"""
        # 查询所有评论
        query_sql = """
        SELECT
            tc.id, tc.thought_id, tc.user_id, tc.content, tc.parent_id,
            tc.likes_count, tc.created_at, tc.updated_at,
            u.username,
            up.avatar_url
        FROM thought_comments tc
        LEFT JOIN users u ON tc.user_id = u.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        WHERE tc.thought_id = :thought_id
        ORDER BY tc.created_at ASC
        """

        result = await db.execute(text(query_sql), {"thought_id": thought_id})
        rows = result.fetchall()

        # 构建评论树
        comments_dict = {}
        root_comments = []

        for row in rows:
            comment = CommentResponse(
                id=row.id,
                thought_id=row.thought_id,
                user_id=row.user_id,
                username=row.username or "未知用户",
                avatar_url=row.avatar_url,
                content=row.content,
                parent_id=row.parent_id,
                likes_count=row.likes_count,
                created_at=row.created_at,
                updated_at=row.updated_at,
                replies=[]
            )
            comments_dict[row.id] = comment

            if row.parent_id is None:
                root_comments.append(comment)

        # 构建嵌套结构
        for comment in comments_dict.values():
            if comment.parent_id and comment.parent_id in comments_dict:
                comments_dict[comment.parent_id].replies.append(comment)

        return CommentListResponse(
            comments=root_comments,
            total=len(rows)
        )

    @staticmethod
    async def _get_comment_by_id(db: AsyncSession, comment_id: int) -> CommentResponse:
        """获取单个评论"""
        query_sql = """
        SELECT
            tc.id, tc.thought_id, tc.user_id, tc.content, tc.parent_id,
            tc.likes_count, tc.created_at, tc.updated_at,
            u.username,
            up.avatar_url
        FROM thought_comments tc
        LEFT JOIN users u ON tc.user_id = u.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        WHERE tc.id = :comment_id
        """

        result = await db.execute(text(query_sql), {"comment_id": comment_id})
        row = result.fetchone()

        return CommentResponse(
            id=row.id,
            thought_id=row.thought_id,
            user_id=row.user_id,
            username=row.username or "未知用户",
            avatar_url=row.avatar_url,
            content=row.content,
            parent_id=row.parent_id,
            likes_count=row.likes_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
            replies=[]
        )

    # ==================== 用户关注相关方法 ====================

    @staticmethod
    async def follow_user(db: AsyncSession, follower_id: str, following_id: str) -> bool:
        """关注用户"""
        if follower_id == following_id:
            return False  # 不能关注自己

        # 检查是否已关注
        check_sql = "SELECT 1 FROM user_follows WHERE follower_id = :follower_id AND following_id = :following_id"
        result = await db.execute(text(check_sql), {"follower_id": follower_id, "following_id": following_id})

        if result.fetchone():
            return False  # 已经关注了

        # 添加关注关系
        insert_sql = """
        INSERT INTO user_follows (follower_id, following_id, created_at)
        VALUES (:follower_id, :following_id, :created_at)
        """
        await db.execute(text(insert_sql), {
            "follower_id": follower_id,
            "following_id": following_id,
            "created_at": datetime.now().isoformat()
        })

        # 确保两个用户的资料都存在
        await SquareService._ensure_user_profile(db, follower_id)
        await SquareService._ensure_user_profile(db, following_id)

        # 更新关注者的关注数
        await db.execute(text("""
            UPDATE user_profiles
            SET following_count = following_count + 1,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """), {"updated_at": datetime.now().isoformat(), "user_id": follower_id})

        # 更新被关注者的粉丝数
        await db.execute(text("""
            UPDATE user_profiles
            SET followers_count = followers_count + 1,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """), {"updated_at": datetime.now().isoformat(), "user_id": following_id})

        await db.commit()
        return True

    @staticmethod
    async def unfollow_user(db: AsyncSession, follower_id: str, following_id: str) -> bool:
        """取消关注用户"""
        # 删除关注关系
        delete_sql = "DELETE FROM user_follows WHERE follower_id = :follower_id AND following_id = :following_id"
        result = await db.execute(text(delete_sql), {"follower_id": follower_id, "following_id": following_id})

        if result.rowcount == 0:
            return False  # 没有关注关系

        # 更新关注者的关注数
        await db.execute(text("""
            UPDATE user_profiles
            SET following_count = following_count - 1,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """), {"updated_at": datetime.now().isoformat(), "user_id": follower_id})

        # 更新被关注者的粉丝数
        await db.execute(text("""
            UPDATE user_profiles
            SET followers_count = followers_count - 1,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """), {"updated_at": datetime.now().isoformat(), "user_id": following_id})

        await db.commit()
        return True

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: str, current_user_id: Optional[str] = None) -> Optional[UserProfileResponse]:
        """获取用户资料"""
        # 确保用户资料存在
        await SquareService._ensure_user_profile(db, user_id)

        query_sql = """
        SELECT
            up.user_id, up.avatar_url, up.bio, up.location, up.website,
            up.followers_count, up.following_count, up.thoughts_count,
            up.created_at, up.updated_at,
            u.username
        FROM user_profiles up
        LEFT JOIN users u ON up.user_id = u.id
        WHERE up.user_id = :user_id
        """

        result = await db.execute(text(query_sql), {"user_id": user_id})
        row = result.fetchone()

        if not row:
            return None

        # 检查当前用户是否已关注
        is_following = False
        is_followed = False
        if current_user_id and current_user_id != user_id:
            # 检查是否关注了该用户
            check_sql = "SELECT 1 FROM user_follows WHERE follower_id = :follower_id AND following_id = :following_id"
            result = await db.execute(text(check_sql), {"follower_id": current_user_id, "following_id": user_id})
            is_following = result.fetchone() is not None

            # 检查该用户是否关注了当前用户
            result = await db.execute(text(check_sql), {"follower_id": user_id, "following_id": current_user_id})
            is_followed = result.fetchone() is not None

        return UserProfileResponse(
            user_id=row.user_id,
            username=row.username or "未知用户",
            avatar_url=row.avatar_url,
            bio=row.bio,
            location=row.location,
            website=row.website,
            followers_count=row.followers_count,
            following_count=row.following_count,
            thoughts_count=row.thoughts_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_following=is_following,
            is_followed=is_followed
        )

    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: str, profile_data: UpdateProfileRequest) -> UserProfileResponse:
        """更新用户资料"""
        # 确保用户资料存在
        await SquareService._ensure_user_profile(db, user_id)

        # 构建更新语句
        update_fields = []
        params = {"user_id": user_id, "updated_at": datetime.now().isoformat()}

        if profile_data.avatar_url is not None:
            update_fields.append("avatar_url = :avatar_url")
            params["avatar_url"] = profile_data.avatar_url

        if profile_data.bio is not None:
            update_fields.append("bio = :bio")
            params["bio"] = profile_data.bio

        if profile_data.location is not None:
            update_fields.append("location = :location")
            params["location"] = profile_data.location

        if profile_data.website is not None:
            update_fields.append("website = :website")
            params["website"] = profile_data.website

        if update_fields:
            update_sql = f"""
            UPDATE user_profiles
            SET {', '.join(update_fields)}, updated_at = :updated_at
            WHERE user_id = :user_id
            """
            await db.execute(text(update_sql), params)
            await db.commit()

        # 返回更新后的用户资料
        return await SquareService.get_user_profile(db, user_id)

    # ==================== 收藏相关方法 ====================

    @staticmethod
    async def toggle_bookmark(db: AsyncSession, user_id: str, thought_id: int) -> dict:
        """切换收藏状态（收藏/取消收藏）"""
        # 检查思想元胞是否存在
        check_thought_sql = "SELECT id FROM thought_cells WHERE id = :thought_id"
        result = await db.execute(text(check_thought_sql), {"thought_id": thought_id})
        thought = result.fetchone()

        if not thought:
            raise ValueError(f"思想元胞 {thought_id} 不存在")

        # 检查是否已收藏
        check_bookmark_sql = """
        SELECT id FROM thought_bookmarks
        WHERE thought_id = :thought_id AND user_id = :user_id
        """
        result = await db.execute(text(check_bookmark_sql), {
            "thought_id": thought_id,
            "user_id": user_id
        })
        existing_bookmark = result.fetchone()

        if existing_bookmark:
            # 已收藏，执行取消收藏
            delete_sql = """
            DELETE FROM thought_bookmarks
            WHERE thought_id = :thought_id AND user_id = :user_id
            """
            await db.execute(text(delete_sql), {
                "thought_id": thought_id,
                "user_id": user_id
            })
            await db.commit()

            return {
                "is_bookmarked": False,
                "message": "取消收藏成功"
            }
        else:
            # 未收藏，执行收藏
            insert_sql = """
            INSERT INTO thought_bookmarks (thought_id, user_id, created_at)
            VALUES (:thought_id, :user_id, :created_at)
            """
            now = datetime.now().isoformat()
            await db.execute(text(insert_sql), {
                "thought_id": thought_id,
                "user_id": user_id,
                "created_at": now
            })
            await db.commit()

            return {
                "is_bookmarked": True,
                "message": "收藏成功"
            }

    @staticmethod
    async def get_user_bookmarks(
        db: AsyncSession,
        user_id: str,
        current_user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> BookmarkListResponse:
        """获取用户的收藏列表"""
        offset = (page - 1) * page_size

        # 查询收藏的思想元胞（带收藏时间）
        query_sql = """
        SELECT
            tc.id,
            tc.user_id,
            tc.content,
            tc.images,
            tc.visibility,
            tc.likes_count,
            tc.comments_count,
            tc.shares_count,
            tc.tags,
            tc.location,
            tc.created_at,
            tc.updated_at,
            tb.created_at as bookmarked_at,
            COALESCE(u.username, tc.user_id) as username,
            up.avatar_url,
            up.bio,
            COALESCE(
                (SELECT 1 FROM thought_likes
                 WHERE thought_id = tc.id AND user_id = :current_user_id LIMIT 1),
                0
            ) as is_liked,
            COALESCE(
                (SELECT 1 FROM thought_bookmarks
                 WHERE thought_id = tc.id AND user_id = :current_user_id LIMIT 1),
                0
            ) as is_bookmarked
        FROM thought_bookmarks tb
        JOIN thought_cells tc ON tb.thought_id = tc.id
        LEFT JOIN user_profiles up ON tc.user_id = up.user_id
        LEFT JOIN users u ON tc.user_id = u.id
        WHERE tb.user_id = :user_id
        ORDER BY tb.created_at DESC
        LIMIT :limit OFFSET :offset
        """

        result = await db.execute(text(query_sql), {
            "user_id": user_id,
            "current_user_id": current_user_id or user_id,
            "limit": page_size,
            "offset": offset
        })
        rows = result.fetchall()

        # 查询总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM thought_bookmarks
        WHERE user_id = :user_id
        """
        count_result = await db.execute(text(count_sql), {"user_id": user_id})
        total = count_result.fetchone()[0]

        # 构建响应数据
        bookmarks = []
        for row in rows:
            # 解析 JSON 字段（处理空字符串和None）
            try:
                images = json.loads(row[3]) if row[3] and row[3].strip() else []
            except (json.JSONDecodeError, AttributeError):
                images = []

            try:
                tags = json.loads(row[8]) if row[8] and row[8].strip() else []
            except (json.JSONDecodeError, AttributeError):
                tags = []

            thought = ThoughtCellResponse(
                id=row[0],
                user_id=row[1],
                username=row[13],  # username
                content=row[2],
                images=images,
                visibility=row[4],
                likes_count=row[5],
                comments_count=row[6],
                shares_count=row[7],
                tags=tags,
                location=row[9],
                created_at=row[10],
                updated_at=row[11],
                avatar_url=row[14],
                bio=row[15],
                is_liked=bool(row[16]),
                is_bookmarked=bool(row[17])
            )

            bookmark = BookmarkThoughtCellResponse(
                thought=thought,
                bookmarked_at=row[12]  # bookmarked_at
            )
            bookmarks.append(bookmark)

        return BookmarkListResponse(
            bookmarks=bookmarks,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + len(bookmarks)) < total
        )

