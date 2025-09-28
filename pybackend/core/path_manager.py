"""
@Created on: 2025/09/28
@Author: DreamFly Team
@Des: 路径管理工具 - 统一管理所有文件路径
"""

import os
from pathlib import Path
from typing import Optional
from cfg.config import settings


class PathManager:
    """路径管理器 - 统一管理所有文件路径"""
    
    def __init__(self):
        """初始化路径管理器"""
        # 获取项目根目录
        self.project_root = self._get_project_root()
        
        # 初始化所有路径
        self._init_paths()
    
    def _get_project_root(self) -> Path:
        """获取项目根目录"""
        # 从当前文件向上查找项目根目录
        current_file = Path(__file__).resolve()
        # pybackend/core/path_manager.py -> 向上两级到pybackend -> 再向上一级到项目根
        return current_file.parent.parent.parent
    
    def _resolve_path(self, path_str: str) -> Path:
        """解析路径 - 支持相对路径和绝对路径"""
        if not path_str:
            return self.project_root
        
        path = Path(path_str)
        if path.is_absolute():
            return path
        else:
            # 相对路径相对于项目根目录
            return self.project_root / path
    
    def _init_paths(self):
        """初始化所有路径"""
        # 数据库相关路径
        self.database_dir = self._resolve_path(settings.DATABASE_DIR)
        self.minds_dir = self._resolve_path(settings.MINDS_DIR)
        
        # 上传相关路径
        self.upload_dir = self._resolve_path(settings.UPLOAD_DIR)
        self.upload_thought_dir = self.upload_dir / settings.UPLOAD_THOUGHT_DIR
        self.upload_voice_dir = self.upload_dir / settings.UPLOAD_VOICE_DIR
        self.upload_image_dir = self.upload_dir / settings.UPLOAD_IMAGE_DIR
        self.upload_document_dir = self.upload_dir / settings.UPLOAD_DOCUMENT_DIR
        
        # 日志路径
        self.log_dir = self._resolve_path(settings.LOG_DIR)
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.database_dir,
            self.minds_dir,
            self.upload_dir,
            self.upload_thought_dir,
            self.upload_voice_dir,
            self.upload_image_dir,
            self.upload_document_dir,
            self.log_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_upload_dir(self, upload_type: str) -> Path:
        """根据上传类型获取对应目录"""
        type_mapping = {
            'thought': self.upload_thought_dir,
            'voice': self.upload_voice_dir,
            'image': self.upload_image_dir,
            'documents': self.upload_document_dir,
            'document': self.upload_document_dir
        }
        
        return type_mapping.get(upload_type, self.upload_dir)
    
    def get_file_size_limit(self, upload_type: str) -> int:
        """根据上传类型获取文件大小限制"""
        size_mapping = {
            'thought': settings.MAX_THOUGHT_SIZE,
            'voice': settings.MAX_VOICE_SIZE,
            'image': settings.MAX_IMAGE_SIZE,
            'documents': settings.MAX_DOCUMENT_SIZE,
            'document': settings.MAX_DOCUMENT_SIZE
        }
        
        return size_mapping.get(upload_type, settings.MAX_FILE_SIZE)
    
    def get_allowed_types(self, upload_type: str) -> list:
        """根据上传类型获取允许的文件类型"""
        type_mapping = {
            'thought': settings.ALLOWED_THOUGHT_TYPES,
            'voice': settings.ALLOWED_VOICE_TYPES,
            'image': settings.ALLOWED_IMAGE_TYPES,
            'documents': settings.ALLOWED_DOCUMENT_TYPES,
            'document': settings.ALLOWED_DOCUMENT_TYPES
        }
        
        return type_mapping.get(upload_type, [])
    
    def get_relative_path(self, full_path: Path) -> str:
        """获取相对于项目根目录的相对路径"""
        try:
            return str(full_path.relative_to(self.project_root))
        except ValueError:
            # 如果不是项目根目录的子路径，返回绝对路径
            return str(full_path)
    
    def __str__(self) -> str:
        """返回路径信息的字符串表示"""
        return f"""PathManager:
  Project Root: {self.project_root}
  Database Dir: {self.database_dir}
  Minds Dir: {self.minds_dir}
  Upload Dir: {self.upload_dir}
  Log Dir: {self.log_dir}
  Upload Subdirs:
    - Thought: {self.upload_thought_dir}
    - Voice: {self.upload_voice_dir}
    - Image: {self.upload_image_dir}
    - Document: {self.upload_document_dir}
"""


# 创建全局路径管理器实例
path_manager = PathManager()

# 确保目录存在
path_manager.ensure_directories()


def get_path_manager() -> PathManager:
    """获取路径管理器实例"""
    return path_manager
