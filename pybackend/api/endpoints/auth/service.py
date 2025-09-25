"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 用户认证 - 业务逻辑服务
"""

import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from core.exception import UnicornException

from .models import User
from .params import RegisterParams, LoginParams
from .schemas import LoginResponseSchema, RegisterResponseSchema


class AuthService:
    """用户认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_salt() -> str:
        """生成密码盐值"""
        return secrets.token_hex(16)

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """密码哈希"""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    async def check_user_exists(self, username: str = None, email: str = None) -> bool:
        """检查用户是否存在"""
        query = select(User)
        conditions = []
        
        if username:
            conditions.append(User.username == username)
        if email:
            conditions.append(User.email == email)
            
        if conditions:
            # 使用 OR 条件
            from sqlalchemy import or_
            query = query.where(or_(*conditions))
            
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user is not None

    async def register_user(self, params: RegisterParams) -> RegisterResponseSchema:
        """用户注册"""
        # 检查用户名或邮箱是否已存在
        if await self.check_user_exists(username=params.username, email=params.email):
            raise UnicornException(code=400, errmsg="用户名或邮箱已存在")

        # 生成密码哈希
        salt = self.generate_salt()
        password_hash = self.hash_password(params.password, salt)

        # 创建用户
        user = User(
            username=params.username,
            email=params.email,
            birth=params.birth,
            password_hash=password_hash,
            password_salt=salt
        )

        self.db.add(user)
        await self.db.flush()  # 获取生成的ID
        await self.db.refresh(user)

        return RegisterResponseSchema(
            user_id=user.id,
            username=user.username,
            email=user.email,
            birth=user.birth,
            register_time=user.created_at
        )

    async def login_user(self, params: LoginParams) -> LoginResponseSchema:
        """用户登录"""
        print(f"🔍 登录尝试: {params.email}")

        # 查找用户
        query = select(User).where(User.email == params.email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ 用户不存在: {params.email}")
            raise UnicornException(code=404, errmsg="用户不存在")

        print(f"✅ 找到用户: {user.username}")
        print(f"🔑 密码盐存在: {bool(user.password_salt)}")
        print(f"🔑 密码哈希存在: {bool(user.password_hash)}")

        # 检查密码哈希是否存在
        if not user.password_hash or not user.password_salt:
            print(f"❌ 用户 {user.username} 缺少密码哈希或盐值")
            raise UnicornException(code=500, errmsg="用户密码数据异常，请联系管理员")

        # 验证密码
        password_hash = self.hash_password(params.password, user.password_salt)
        if password_hash != user.password_hash:
            print(f"❌ 密码验证失败: {user.username}")
            raise UnicornException(code=401, errmsg="密码错误")

        print(f"✅ 登录成功: {user.username}")
        return LoginResponseSchema(
            user_id=user.id,
            username=user.username,
            email=user.email,
            birth=user.birth,
            register_time=user.created_at
        )