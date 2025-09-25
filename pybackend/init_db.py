"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: 数据库初始化脚本
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database.models import Base
from database.session import DATABASE_URL


async def create_business_tables(engine):
    """创建前端功能所需的业务数据表"""

    # 1. 用户意识体资产表
    user_consciousness_assets_sql = """
    CREATE TABLE IF NOT EXISTS user_consciousness_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        type VARCHAR(50),
        completeness INTEGER DEFAULT 0,
        activity_score INTEGER DEFAULT 0,
        sync_status VARCHAR(20) DEFAULT 'pending',
        status VARCHAR(20) DEFAULT 'draft',
        tags TEXT, -- JSON格式存储标签数组
        interactions_count INTEGER DEFAULT 0,
        rating DECIMAL(3,2) DEFAULT 0.0,
        pricing_model TEXT, -- JSON格式存储定价模型
        avatar_url VARCHAR(500),
        last_sync_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 2. 用户文档表
    user_documents_sql = """
    CREATE TABLE IF NOT EXISTS user_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        filename VARCHAR(255) NOT NULL,
        file_type VARCHAR(20),
        file_size INTEGER,
        file_path VARCHAR(500),
        extracted_text TEXT,
        tags TEXT, -- JSON格式存储标签
        status VARCHAR(20) DEFAULT 'uploaded',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    );
    """

    # 3. 记忆片段表
    memory_fragments_sql = """
    CREATE TABLE IF NOT EXISTS memory_fragments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        title VARCHAR(200),
        content TEXT,
        time_period VARCHAR(100),
        category VARCHAR(50),
        importance INTEGER DEFAULT 5,
        tags TEXT, -- JSON格式存储标签
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 4. 测试结果表
    test_results_sql = """
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        test_type VARCHAR(50),
        results TEXT, -- JSON格式存储测试结果
        score INTEGER,
        answers TEXT, -- JSON格式存储用户答案
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 5. 交易记录表
    transactions_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id VARCHAR(50),
        seller_id VARCHAR(50),
        consciousness_id INTEGER,
        transaction_type VARCHAR(20), -- purchase, rent, sell
        amount DECIMAL(10,2),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    );
    """

    # 6. 用户统计数据表
    user_statistics_sql = """
    CREATE TABLE IF NOT EXISTS user_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        stat_type VARCHAR(50), -- consciousness_level, memory_count, interaction_count等
        stat_value VARCHAR(100),
        stat_date DATE DEFAULT CURRENT_DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 7. 笔记表
    notes_sql = """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(50) NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        folder_id VARCHAR(50),
        tags TEXT, -- JSON格式存储标签
        preview VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 8. 笔记文件夹表
    note_folders_sql = """
    CREATE TABLE IF NOT EXISTS note_folders (
        id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL,
        parent_id VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 9. 交互历史表
    interaction_history_sql = """
    CREATE TABLE IF NOT EXISTS interaction_history (
        id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50) NOT NULL,
        mind_name VARCHAR(100) NOT NULL,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        tokens_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # 执行SQL语句
    async with engine.begin() as conn:
        await conn.execute(text(user_consciousness_assets_sql))
        await conn.execute(text(user_documents_sql))
        await conn.execute(text(memory_fragments_sql))
        await conn.execute(text(test_results_sql))
        await conn.execute(text(transactions_sql))
        await conn.execute(text(user_statistics_sql))
        await conn.execute(text(notes_sql))
        await conn.execute(text(note_folders_sql))
        await conn.execute(text(interaction_history_sql))
        print("✅ 业务数据表创建成功！")


async def insert_demo_data(engine):
    """插入演示数据"""
    demo_user_id = "demo_user_001"
    test_user_id = "c3a45caf-92ad-43d8-b242-f6ac8fcdee51"  # 新注册的测试用户

    # 示例意识体资产数据
    consciousness_assets_data = [
        (demo_user_id, '技术专家意识体', '专注于软件架构设计和系统优化的技术专家意识体，具备丰富的项目经验和问题解决能力。',
         '专业技能', 95, 88, '已同步', 'active', '["技术架构", "系统设计", "性能优化", "AI开发"]',
         1280, 4.9, '{"preview": {"enabled": true, "duration": 30}, "rent": {"enabled": true, "price": 1200}, "buy": {"enabled": true, "price": 25000}}',
         '/static/avatar.jpg'),
        (demo_user_id, '创意设计意识体', '融合艺术创作与设计思维的创意意识体，善于视觉设计和用户体验优化。',
         '创意艺术', 92, 85, '同步中', 'syncing', '["UI设计", "UX设计", "创意思维", "艺术创作"]',
         960, 4.8, '{"preview": {"enabled": true, "duration": 15}, "rent": {"enabled": true, "price": 800}, "buy": {"enabled": false, "price": 0}}',
         '/static/avatar.jpg'),

        # 为新测试用户添加数据
        (test_user_id, 'testuser2的个人意识体', 'testuser2的第一个数字意识体，包含个人思维模式和兴趣爱好。',
         '个人助手', 88, 82, '已同步', 'active', '["编程", "游戏", "学习", "生活"]',
         520, 4.5, '{"preview": {"enabled": true, "duration": 30}, "rent": {"enabled": true, "price": 300}, "buy": {"enabled": true, "price": 8000}}',
         '/static/avatar.jpg'),
        (test_user_id, '学习助手意识体', '专门用于学习和知识管理的AI助手，帮助提高学习效率。',
         '教育学习', 90, 85, '同步中', 'syncing', '["学习方法", "知识管理", "编程教学", "数学"]',
         380, 4.7, '{"preview": {"enabled": true, "duration": 15}, "rent": {"enabled": true, "price": 200}, "buy": {"enabled": false, "price": 0}}',
         '/static/avatar.jpg')
    ]

    # 示例记忆片段数据
    memory_fragments_data = [
        (demo_user_id, '大学时光', '在南京大学的那段时光，是我人生中最重要的成长阶段。从初入校园的青涩懵懂，到逐渐适应大学生活，再到最后的成熟自信，这四年的经历塑造了现在的我。', '2020-2024', 'education', 9, '["大学", "学习", "成长", "青春"]'),
        (demo_user_id, '第一份工作', '毕业后的第一份工作让我学会了很多。从技术小白到能够独当一面，从不敢发言到主动承担责任，职场的历练让我快速成长。', '2024', 'career', 8, '["工作", "职场", "经验", "成长"]'),
        (demo_user_id, '学习编程', '记得第一次接触编程时的兴奋和困惑。从Hello World到复杂的系统架构，每一行代码都是成长的足迹。', '2019-2024', 'skill', 9, '["编程", "技术", "学习", "代码"]'),

        # 为新测试用户添加记忆片段
        (test_user_id, '初学编程', '刚开始学习编程时的那种兴奋感，每解决一个问题都让我感到成就感满满。', '2023', 'skill', 8, '["编程", "学习", "成长", "技术"]'),
        (test_user_id, '游戏时光', '和朋友一起玩游戏的快乐时光，不仅是娱乐，也是友谊的见证。', '2024', 'entertainment', 7, '["游戏", "友谊", "娱乐", "快乐"]')
    ]

    # 示例统计数据
    statistics_data = [
        (demo_user_id, 'consciousness_level', '85', '2024-09-14'),
        (demo_user_id, 'memory_count', '156', '2024-09-14'),
        (demo_user_id, 'interaction_count', '2340', '2024-09-14'),
        (demo_user_id, 'knowledge_points', '89', '2024-09-14'),
        (demo_user_id, 'assets_count', '2', '2024-09-14'),
        (demo_user_id, 'total_revenue', '15800', '2024-09-14'),
        (demo_user_id, 'monthly_revenue', '2800', '2024-09-14'),

        # 为新测试用户添加统计数据
        (test_user_id, 'consciousness_level', '65', '2025-09-15'),
        (test_user_id, 'memory_count', '2', '2025-09-15'),
        (test_user_id, 'interaction_count', '5', '2025-09-15'),
        (test_user_id, 'knowledge_points', '45', '2025-09-15'),
        (test_user_id, 'assets_count', '2', '2025-09-15'),
        (test_user_id, 'total_revenue', '0', '2025-09-15'),
        (test_user_id, 'monthly_revenue', '0', '2025-09-15')
    ]

    async with engine.begin() as conn:
        # 插入意识体资产数据
        for user_id, name, description, type_, completeness, activity, sync_status, status, tags, interactions, rating, pricing_model, avatar_url in consciousness_assets_data:
            sql = text("""
                INSERT OR IGNORE INTO user_consciousness_assets
                (user_id, name, description, type, completeness, activity_score, sync_status, status, tags, interactions_count, rating, pricing_model, avatar_url)
                VALUES (:user_id, :name, :description, :type, :completeness, :activity_score, :sync_status, :status, :tags, :interactions_count, :rating, :pricing_model, :avatar_url)
            """)
            await conn.execute(sql, {
                'user_id': user_id, 'name': name, 'description': description, 'type': type_,
                'completeness': completeness, 'activity_score': activity, 'sync_status': sync_status,
                'status': status, 'tags': tags, 'interactions_count': interactions,
                'rating': rating, 'pricing_model': pricing_model, 'avatar_url': avatar_url
            })

        # 插入记忆片段数据
        for user_id, title, content, time_period, category, importance, tags in memory_fragments_data:
            sql = text("""
                INSERT OR IGNORE INTO memory_fragments
                (user_id, title, content, time_period, category, importance, tags, created_at, updated_at)
                VALUES (:user_id, :title, :content, :time_period, :category, :importance, :tags, datetime('now'), datetime('now'))
            """)
            await conn.execute(sql, {
                'user_id': user_id, 'title': title, 'content': content,
                'time_period': time_period, 'category': category, 'importance': importance, 'tags': tags
            })

        # 插入统计数据
        for user_id, stat_type, stat_value, stat_date in statistics_data:
            sql = text("""
                INSERT OR IGNORE INTO user_statistics
                (user_id, stat_type, stat_value, stat_date)
                VALUES (:user_id, :stat_type, :stat_value, :stat_date)
            """)
            await conn.execute(sql, {
                'user_id': user_id, 'stat_type': stat_type, 'stat_value': stat_value, 'stat_date': stat_date
            })

        print("✅ 演示数据插入成功！")


async def init_database():
    """初始化数据库表"""
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 创建原有的模型表
        await conn.run_sync(Base.metadata.create_all)

    # 创建业务数据表
    await create_business_tables(engine)

    # 插入演示数据
    await insert_demo_data(engine)

    await engine.dispose()
    print("🎉 数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_database())