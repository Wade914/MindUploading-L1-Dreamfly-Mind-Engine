"""
数据库迁移脚本：为 user_consciousness_assets 表添加缺失的字段

缺失字段：
1. name - 意识体名称（必需）
2. last_interaction_at - 最后交互时间（可选）

执行方式：
python pybackend/migrations/add_missing_columns_to_user_consciousness_assets.py
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def migrate():
    """执行数据库迁移"""
    db_path = project_root / 'pybackend' / 'dreamfly.db'
    
    print(f"📊 连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查当前表结构
        cursor.execute('PRAGMA table_info(user_consciousness_assets)')
        columns = {col[1] for col in cursor.fetchall()}
        
        print(f"✅ 当前表有 {len(columns)} 个字段")
        
        # 添加 name 字段（如果不存在）
        if 'name' not in columns:
            print("📝 添加字段: name VARCHAR(100) NOT NULL")
            cursor.execute('''
                ALTER TABLE user_consciousness_assets 
                ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''
            ''')
            print("✅ name 字段添加成功")
        else:
            print("⏭️  name 字段已存在，跳过")
        
        # 添加 last_interaction_at 字段（如果不存在）
        if 'last_interaction_at' not in columns:
            print("📝 添加字段: last_interaction_at TIMESTAMP")
            cursor.execute('''
                ALTER TABLE user_consciousness_assets 
                ADD COLUMN last_interaction_at TIMESTAMP
            ''')
            print("✅ last_interaction_at 字段添加成功")
        else:
            print("⏭️  last_interaction_at 字段已存在，跳过")
        
        # 提交更改
        conn.commit()
        
        # 验证结果
        cursor.execute('PRAGMA table_info(user_consciousness_assets)')
        new_columns = {col[1] for col in cursor.fetchall()}
        
        print(f"\n🎉 迁移完成！表现在有 {len(new_columns)} 个字段")
        print("\n新增字段验证:")
        print(f"  - name: {'✅' if 'name' in new_columns else '❌'}")
        print(f"  - last_interaction_at: {'✅' if 'last_interaction_at' in new_columns else '❌'}")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 数据库迁移：添加缺失字段到 user_consciousness_assets")
    print("=" * 60)
    print()
    
    migrate()
    
    print()
    print("=" * 60)
    print("✅ 迁移脚本执行完成")
    print("=" * 60)

