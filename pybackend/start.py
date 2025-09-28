#!/usr/bin/env python3
"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 项目启动脚本
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from init_db import init_database
from core.path_manager import get_path_manager


def run_server():
    """启动服务器"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )


def setup_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    asyncio.run(init_database())
    print("数据库初始化完成！")


def create_directories():
    """创建必要的目录"""
    path_manager = get_path_manager()
    path_manager.ensure_directories()
    print("✅ 所有必要目录已创建")


def main():
    """主函数"""
    print("🚀 DreamFly API 启动中...")
    
    # 创建必要目录
    create_directories()
    
    # 初始化数据库
    setup_database()
    
    # 启动服务器
    print("🌟 启动服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔄 ReDoc文档: http://localhost:8000/redoc")
    run_server()


if __name__ == "__main__":
    main()