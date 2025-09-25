"""
@Created on: 2025/09/16
@Author: DreamFly Team
@Des: 社交网络 - 业务逻辑服务
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from datetime import datetime
import uuid

from database.models import User
from core.exception import UnicornException
from .models import AddUserRequest, UserPermission, UpdatePermissionRequest, SocialStats, UserSearchResult


class UserPermissionModel:
    """用户权限数据库模型（临时，后续可移到database/models.py）"""
    def __init__(self):
        self.id = None
        self.user_id = None
        self.owner_id = None
        self.account_id = None
        self.name = None
        self.avatar = "👤"
        self.space = None
        self.is_inheritor = False
        self.tags = []
        self.created_at = None
        self.updated_at = None


class SocialService:
    """社交网络服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # 临时使用内存存储，后续需要创建数据库表
        self._permissions = []

    async def search_user_by_account_id(self, account_id: str) -> Optional[UserSearchResult]:
        """根据账号ID搜索用户"""
        # 这里可以根据用户名或邮箱搜索
        query = select(User).where(
            or_(
                User.username == account_id,
                User.email == account_id,
                User.id == account_id
            )
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return UserSearchResult(
                user_id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at
            )
        return None

    async def add_user_permission(self, owner_id: str, request: AddUserRequest) -> UserPermission:
        """添加用户权限"""
        # 验证用户是否存在
        user_info = await self.search_user_by_account_id(request.account_id)
        if not user_info:
            raise UnicornException(code=404, errmsg="用户不存在")
        
        # 检查是否已经添加过该用户
        existing = next((p for p in self._permissions 
                        if p.get('owner_id') == owner_id and p.get('user_id') == user_info.user_id), None)
        if existing:
            raise UnicornException(code=400, errmsg="该用户已经被添加")
        
        # 创建权限记录
        permission_id = str(uuid.uuid4())
        tags = []
        if request.is_inheritor and request.space == 'family':
            tags.append('继承人')
        
        permission_data = {
            'id': permission_id,
            'user_id': user_info.user_id,
            'owner_id': owner_id,
            'account_id': request.account_id,
            'name': user_info.username,
            'avatar': '👤',
            'space': request.space,
            'is_inheritor': request.is_inheritor if request.space == 'family' else False,
            'tags': tags,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._permissions.append(permission_data)
        
        return UserPermission(**permission_data)

    async def get_user_permissions(self, owner_id: str, space: Optional[str] = None) -> List[UserPermission]:
        """获取用户权限列表"""
        permissions = [p for p in self._permissions if p.get('owner_id') == owner_id]
        
        if space:
            permissions = [p for p in permissions if p.get('space') == space]
        
        return [UserPermission(**p) for p in permissions]

    async def update_user_permission(self, owner_id: str, permission_id: str, request: UpdatePermissionRequest) -> UserPermission:
        """更新用户权限"""
        permission = next((p for p in self._permissions 
                          if p.get('id') == permission_id and p.get('owner_id') == owner_id), None)
        
        if not permission:
            raise UnicornException(code=404, errmsg="权限记录不存在")
        
        # 更新权限
        if request.space is not None:
            permission['space'] = request.space
        
        if request.is_inheritor is not None:
            permission['is_inheritor'] = request.is_inheritor if permission['space'] == 'family' else False
            
            # 更新标签
            tags = [tag for tag in permission['tags'] if tag != '继承人']
            if permission['is_inheritor']:
                tags.append('继承人')
            permission['tags'] = tags
        
        permission['updated_at'] = datetime.now()
        
        return UserPermission(**permission)

    async def remove_user_permission(self, owner_id: str, permission_id: str) -> bool:
        """移除用户权限"""
        permission_index = next((i for i, p in enumerate(self._permissions) 
                               if p.get('id') == permission_id and p.get('owner_id') == owner_id), None)
        
        if permission_index is None:
            raise UnicornException(code=404, errmsg="权限记录不存在")
        
        self._permissions.pop(permission_index)
        return True

    async def get_social_stats(self, owner_id: str) -> SocialStats:
        """获取社交统计数据"""
        permissions = [p for p in self._permissions if p.get('owner_id') == owner_id]
        
        total_connections = len(permissions)
        inheritors_count = len([p for p in permissions if p.get('is_inheritor')])
        personal_space_users = len([p for p in permissions if p.get('space') == 'personal'])
        family_space_users = len([p for p in permissions if p.get('space') == 'family'])
        public_space_users = len([p for p in permissions if p.get('space') == 'public'])
        
        return SocialStats(
            total_connections=total_connections,
            inheritors_count=inheritors_count,
            personal_space_users=personal_space_users,
            family_space_users=family_space_users,
            public_space_users=public_space_users
        )
