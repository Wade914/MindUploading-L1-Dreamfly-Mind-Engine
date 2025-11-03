"""
@Created on: 2025/01/16
@Author: DreamFly Team
@Des: 添加 Square 广场功能的数据库表 (增量迁移脚本)
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# 直接使用相对于脚本的数据库路径
db_path = Path(__file__).parent.parent / "dreamfly.db"
DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"


async def add_square_tables(engine):
    """添加 Square 广场功能所需的数据库表"""
    
    print("🚀 开始添加 Square 广场数据库表...")
    
    # 1. 思想元胞表
    thought_cells_sql = """
    CREATE TABLE IF NOT EXISTS thought_cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        images TEXT,                                -- JSON数组,存储图片URL列表
        visibility VARCHAR(20) DEFAULT 'public',    -- public/friends/private
        likes_count INTEGER DEFAULT 0,
        comments_count INTEGER DEFAULT 0,
        shares_count INTEGER DEFAULT 0,
        tags TEXT,                                  -- JSON数组,存储标签列表
        location VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 2. 点赞表
    thought_likes_sql = """
    CREATE TABLE IF NOT EXISTS thought_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thought_id INTEGER NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(thought_id, user_id)                 -- 防止重复点赞
    );
    """
    
    # 3. 评论表
    thought_comments_sql = """
    CREATE TABLE IF NOT EXISTS thought_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thought_id INTEGER NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        parent_id INTEGER,                          -- 父评论ID,用于嵌套回复
        likes_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 4. 用户关注表
    user_follows_sql = """
    CREATE TABLE IF NOT EXISTS user_follows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        follower_id VARCHAR(50) NOT NULL,           -- 关注者ID
        following_id VARCHAR(50) NOT NULL,          -- 被关注者ID
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(follower_id, following_id)           -- 防止重复关注
    );
    """
    
    # 5. 用户公开资料表
    user_profiles_sql = """
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL UNIQUE,
        avatar_url VARCHAR(500),
        bio TEXT,
        location VARCHAR(200),
        website VARCHAR(500),
        followers_count INTEGER DEFAULT 0,
        following_count INTEGER DEFAULT 0,
        thoughts_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 6. 思想元胞收藏表
    thought_bookmarks_sql = """
    CREATE TABLE IF NOT EXISTS thought_bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thought_id INTEGER NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(thought_id, user_id)                 -- 防止重复收藏
    );
    """

    # 执行SQL语句
    async with engine.begin() as conn:
        print("  📝 创建 thought_cells 表...")
        await conn.execute(text(thought_cells_sql))

        print("  📝 创建 thought_likes 表...")
        await conn.execute(text(thought_likes_sql))

        print("  📝 创建 thought_comments 表...")
        await conn.execute(text(thought_comments_sql))

        print("  📝 创建 user_follows 表...")
        await conn.execute(text(user_follows_sql))

        print("  📝 创建 user_profiles 表...")
        await conn.execute(text(user_profiles_sql))

        print("  📝 创建 thought_bookmarks 表...")
        await conn.execute(text(thought_bookmarks_sql))

        print("✅ Square 广场数据库表创建成功！")


async def verify_tables(engine):
    """验证表是否创建成功"""
    print("\n🔍 验证表结构...")
    
    table_names = [
        'thought_cells',
        'thought_likes',
        'thought_comments',
        'user_follows',
        'user_profiles',
        'thought_bookmarks'
    ]
    
    async with engine.begin() as conn:
        for table_name in table_names:
            # 检查表是否存在
            check_sql = f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
            """
            result = await conn.execute(text(check_sql))
            exists = result.fetchone()
            
            if exists:
                # 获取表结构
                pragma_sql = f"PRAGMA table_info({table_name})"
                result = await conn.execute(text(pragma_sql))
                columns = result.fetchall()
                
                print(f"  ✅ {table_name} ({len(columns)} 列)")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
            else:
                print(f"  ❌ {table_name} 不存在！")
    
    print("\n✅ 表结构验证完成！")


async def main():
    """主函数"""
    print("=" * 60)
    print("🎯 Square 广场数据库表增量迁移脚本")
    print("=" * 60)
    print(f"📊 数据库: {DATABASE_URL}")
    print()
    
    # 创建数据库引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # 添加 Square 表
        await add_square_tables(engine)
        
        # 验证表结构
        await verify_tables(engine)
        
        print("\n" + "=" * 60)
        print("🎉 迁移完成！现有数据完全保留！")
        print("=" * 60)
        print("\n📌 下一步:")
        print("  1. 创建 Square API 模块 (pybackend/api/endpoints/square/)")
        print("  2. 在 main.py 中注册 Square 路由")
        print("  3. 测试 API 接口")
        print()
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

