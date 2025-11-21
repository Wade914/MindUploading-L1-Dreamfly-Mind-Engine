"""
@Created on: 2025/01/20
@Author: DreamFly Team
@Des: 向量化现有数据的迁移脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from cfg.config import settings
from api.endpoints.rag.service import get_rag_service


async def vectorize_documents(session: AsyncSession, rag_service):
    """向量化所有文档"""
    print("\n📄 开始向量化文档...")
    
    query = text("""
        SELECT id, user_id, filename, file_type, extracted_text 
        FROM user_documents 
        WHERE extracted_text IS NOT NULL AND extracted_text != ''
    """)
    
    result = await session.execute(query)
    documents = result.fetchall()
    
    success_count = 0
    for doc in documents:
        doc_id, user_id, filename, file_type, extracted_text = doc
        
        try:
            await rag_service.vectorize_and_store(
                collection_name="documents",
                doc_id=f"doc_{user_id}_{doc_id}",
                content=extracted_text,
                metadata={
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "filename": filename,
                    "file_type": file_type
                }
            )
            success_count += 1
            print(f"  ✅ 文档 {doc_id} ({filename}) 向量化成功")
        except Exception as e:
            print(f"  ❌ 文档 {doc_id} 向量化失败: {str(e)}")
    
    print(f"📄 文档向量化完成: {success_count}/{len(documents)}")
    return success_count


async def vectorize_memories(session: AsyncSession, rag_service):
    """向量化所有记忆片段"""
    print("\n🧠 开始向量化记忆片段...")
    
    query = text("""
        SELECT id, user_id, title, content, category, importance, time_period
        FROM memory_fragments
        WHERE content IS NOT NULL AND content != ''
    """)
    
    result = await session.execute(query)
    memories = result.fetchall()
    
    success_count = 0
    for mem in memories:
        mem_id, user_id, title, content, category, importance, time_period = mem
        
        try:
            await rag_service.vectorize_and_store(
                collection_name="memories",
                doc_id=f"mem_{user_id}_{mem_id}",
                content=content,
                metadata={
                    "user_id": user_id,
                    "memory_id": mem_id,
                    "title": title,
                    "category": category,
                    "importance": importance,
                    "time_period": time_period
                }
            )
            success_count += 1
            print(f"  ✅ 记忆片段 {mem_id} ({title}) 向量化成功")
        except Exception as e:
            print(f"  ❌ 记忆片段 {mem_id} 向量化失败: {str(e)}")
    
    print(f"🧠 记忆片段向量化完成: {success_count}/{len(memories)}")
    return success_count


async def vectorize_notes(session: AsyncSession, rag_service):
    """向量化所有笔记"""
    print("\n📝 开始向量化笔记...")
    
    query = text("""
        SELECT id, user_id, title, content, folder_id
        FROM notes
        WHERE content IS NOT NULL AND content != ''
    """)
    
    result = await session.execute(query)
    notes = result.fetchall()
    
    success_count = 0
    for note in notes:
        note_id, user_id, title, content, folder_id = note
        
        try:
            await rag_service.vectorize_and_store(
                collection_name="notes",
                doc_id=f"note_{user_id}_{note_id}",
                content=content,
                metadata={
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": title,
                    "folder_id": folder_id
                }
            )
            success_count += 1
            print(f"  ✅ 笔记 {note_id} ({title}) 向量化成功")
        except Exception as e:
            print(f"  ❌ 笔记 {note_id} 向量化失败: {str(e)}")
    
    print(f"📝 笔记向量化完成: {success_count}/{len(notes)}")
    return success_count


async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 DreamFly RAG数据迁移脚本")
    print("=" * 60)
    
    # 创建异步数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 初始化RAG服务
    print("\n🔧 初始化RAG服务...")
    rag_service = get_rag_service()
    print("✅ RAG服务初始化成功")
    
    async with async_session() as session:
        # 向量化各类数据
        doc_count = await vectorize_documents(session, rag_service)
        mem_count = await vectorize_memories(session, rag_service)
        note_count = await vectorize_notes(session, rag_service)
        
        total = doc_count + mem_count + note_count
        
        print("\n" + "=" * 60)
        print(f"✅ 数据迁移完成！共向量化 {total} 条数据")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

