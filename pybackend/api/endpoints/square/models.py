"""
@Created on: 2025/01/16
@Author: DreamFly Team
@Des: Square 广场 - 数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 思想元胞相关模型 ====================

class CreateThoughtRequest(BaseModel):
    """创建思想元胞请求模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="思想元胞内容")
    images: Optional[List[str]] = Field(default=[], description="图片URL列表")
    visibility: Optional[str] = Field(default="public", description="可见性: public/friends/private")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    location: Optional[str] = Field(default=None, max_length=200, description="地理位置")


class UpdateThoughtRequest(BaseModel):
    """更新思想元胞请求模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="思想元胞内容")
    images: Optional[List[str]] = Field(None, description="图片URL列表")
    visibility: Optional[str] = Field(None, description="可见性: public/friends/private")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    location: Optional[str] = Field(None, max_length=200, description="地理位置")


class ThoughtCellResponse(BaseModel):
    """思想元胞响应模型"""
    id: int
    user_id: str
    username: str  # 从 users 表 JOIN 获取
    avatar_url: Optional[str] = None  # 从 user_profiles 表 JOIN 获取
    user_birth: Optional[str] = None  # 从 users 表 JOIN 获取用户出生日期
    content: str
    images: List[str] = []
    visibility: str
    likes_count: int
    comments_count: int
    shares_count: int
    tags: List[str] = []
    location: Optional[str] = None
    created_at: str
    updated_at: str
    is_liked: bool = False  # 当前用户是否已点赞
    is_following: bool = False  # 当前用户是否已关注该作者
    is_bookmarked: bool = False  # 当前用户是否已收藏

    class Config:
        from_attributes = True


# ==================== 评论相关模型 ====================

class CreateCommentRequest(BaseModel):
    """创建评论请求模型"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(default=None, description="父评论ID (用于嵌套回复)")


class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    thought_id: int
    user_id: str
    username: str  # 从 users 表 JOIN 获取
    avatar_url: Optional[str] = None  # 从 user_profiles 表 JOIN 获取
    content: str
    parent_id: Optional[int] = None
    likes_count: int
    created_at: str
    updated_at: str
    replies: List['CommentResponse'] = []  # 子评论列表
    
    class Config:
        from_attributes = True


# ==================== 用户关系相关模型 ====================

class FollowRequest(BaseModel):
    """关注用户请求模型"""
    following_id: str = Field(..., description="要关注的用户ID")


class UserProfileResponse(BaseModel):
    """用户资料响应模型"""
    user_id: str
    username: str  # 从 users 表 JOIN 获取
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    followers_count: int
    following_count: int
    thoughts_count: int
    created_at: str
    updated_at: str
    is_following: bool = False  # 当前用户是否已关注
    is_followed: bool = False  # 是否关注了当前用户
    
    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """更新用户资料请求模型"""
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    location: Optional[str] = Field(None, max_length=200, description="地理位置")
    website: Optional[str] = Field(None, max_length=500, description="个人网站")


# ==================== 列表响应模型 ====================

class ThoughtListResponse(BaseModel):
    """思想元胞列表响应模型"""
    thoughts: List[ThoughtCellResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class CommentListResponse(BaseModel):
    """评论列表响应模型"""
    comments: List[CommentResponse]
    total: int


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserProfileResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ==================== 收藏相关模型 ====================

class BookmarkThoughtCellResponse(BaseModel):
    """收藏的思想元胞响应模型（包含收藏时间）"""
    thought: ThoughtCellResponse
    bookmarked_at: str  # 收藏时间

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """收藏列表响应模型"""
    bookmarks: List[BookmarkThoughtCellResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# 解决 CommentResponse 的前向引用问题
CommentResponse.model_rebuild()

