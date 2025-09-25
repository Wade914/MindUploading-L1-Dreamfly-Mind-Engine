"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 记忆片段管理 - 业务逻辑
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .models import MemoryFragment, CreateMemoryRequest, UpdateMemoryRequest, TestResult, CreateTestResultRequest


class MemoryService:
    """记忆片段服务"""
    
    @staticmethod
    async def get_user_memory_fragments(db: AsyncSession, user_id: str, category: Optional[str] = None) -> List[MemoryFragment]:
        """获取用户的记忆片段列表"""
        base_query = """
            SELECT id, user_id, title, content, time_period, category, importance, tags, created_at, updated_at
            FROM memory_fragments 
            WHERE user_id = :user_id
        """
        
        params = {"user_id": user_id}
        
        if category:
            base_query += " AND category = :category"
            params["category"] = category
        
        base_query += " ORDER BY importance DESC, created_at DESC"
        
        result = await db.execute(text(base_query), params)
        rows = result.fetchall()
        
        fragments = []
        for row in rows:
            tags = json.loads(row.tags) if row.tags else []
            
            fragment = MemoryFragment(
                id=row.id,
                user_id=row.user_id,
                title=row.title,
                content=row.content,
                time_period=row.time_period,
                category=row.category,
                importance=row.importance,
                tags=tags,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            fragments.append(fragment)
        
        return fragments
    
    @staticmethod
    async def create_memory_fragment(db: AsyncSession, user_id: str, memory_data: CreateMemoryRequest) -> MemoryFragment:
        """创建新的记忆片段"""
        tags_json = json.dumps(memory_data.tags, ensure_ascii=False)
        
        query = text("""
            INSERT INTO memory_fragments 
            (user_id, title, content, time_period, category, importance, tags, created_at, updated_at)
            VALUES (:user_id, :title, :content, :time_period, :category, :importance, :tags, 
                    datetime('now'), datetime('now'))
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "title": memory_data.title,
            "content": memory_data.content,
            "time_period": memory_data.time_period,
            "category": memory_data.category,
            "importance": memory_data.importance,
            "tags": tags_json
        })
        
        fragment_id = result.scalar()
        await db.commit()
        
        return await MemoryService.get_memory_fragment_by_id(db, fragment_id)
    
    @staticmethod
    async def get_memory_fragment_by_id(db: AsyncSession, fragment_id: int) -> Optional[MemoryFragment]:
        """根据ID获取记忆片段"""
        query = text("""
            SELECT id, user_id, title, content, time_period, category, importance, tags, created_at, updated_at
            FROM memory_fragments 
            WHERE id = :fragment_id
        """)
        
        result = await db.execute(query, {"fragment_id": fragment_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        tags = json.loads(row.tags) if row.tags else []
        
        return MemoryFragment(
            id=row.id,
            user_id=row.user_id,
            title=row.title,
            content=row.content,
            time_period=row.time_period,
            category=row.category,
            importance=row.importance,
            tags=tags,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    @staticmethod
    async def update_memory_fragment(db: AsyncSession, fragment_id: int, user_id: str, memory_data: UpdateMemoryRequest) -> Optional[MemoryFragment]:
        """更新记忆片段"""
        update_fields = []
        params = {"fragment_id": fragment_id, "user_id": user_id}
        
        if memory_data.title is not None:
            update_fields.append("title = :title")
            params["title"] = memory_data.title
        
        if memory_data.content is not None:
            update_fields.append("content = :content")
            params["content"] = memory_data.content
        
        if memory_data.time_period is not None:
            update_fields.append("time_period = :time_period")
            params["time_period"] = memory_data.time_period
        
        if memory_data.category is not None:
            update_fields.append("category = :category")
            params["category"] = memory_data.category
        
        if memory_data.importance is not None:
            update_fields.append("importance = :importance")
            params["importance"] = memory_data.importance
        
        if memory_data.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = json.dumps(memory_data.tags, ensure_ascii=False)
        
        if not update_fields:
            return await MemoryService.get_memory_fragment_by_id(db, fragment_id)
        
        update_fields.append("updated_at = datetime('now')")
        
        query = text(f"""
            UPDATE memory_fragments 
            SET {', '.join(update_fields)}
            WHERE id = :fragment_id AND user_id = :user_id
        """)
        
        await db.execute(query, params)
        await db.commit()
        
        return await MemoryService.get_memory_fragment_by_id(db, fragment_id)
    
    @staticmethod
    async def delete_memory_fragment(db: AsyncSession, fragment_id: int, user_id: str) -> bool:
        """删除记忆片段"""
        query = text("""
            DELETE FROM memory_fragments 
            WHERE id = :fragment_id AND user_id = :user_id
        """)
        
        result = await db.execute(query, {"fragment_id": fragment_id, "user_id": user_id})
        await db.commit()
        
        return result.rowcount > 0


class TestResultService:
    """测试结果服务"""
    
    @staticmethod
    async def create_test_result(db: AsyncSession, user_id: str, test_data: CreateTestResultRequest) -> TestResult:
        """创建测试结果"""
        results_json = json.dumps(test_data.results, ensure_ascii=False)
        answers_json = json.dumps(test_data.answers, ensure_ascii=False) if test_data.answers else None
        
        query = text("""
            INSERT INTO test_results 
            (user_id, test_type, results, score, answers, completed_at)
            VALUES (:user_id, :test_type, :results, :score, :answers, datetime('now'))
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "test_type": test_data.test_type,
            "results": results_json,
            "score": test_data.score,
            "answers": answers_json
        })
        
        test_id = result.scalar()
        await db.commit()
        
        return await TestResultService.get_test_result_by_id(db, test_id)
    
    @staticmethod
    async def get_test_result_by_id(db: AsyncSession, test_id: int) -> Optional[TestResult]:
        """根据ID获取测试结果"""
        query = text("""
            SELECT id, user_id, test_type, results, score, answers, completed_at
            FROM test_results 
            WHERE id = :test_id
        """)
        
        result = await db.execute(query, {"test_id": test_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        results = json.loads(row.results) if row.results else {}
        answers = json.loads(row.answers) if row.answers else {}
        
        return TestResult(
            id=row.id,
            user_id=row.user_id,
            test_type=row.test_type,
            results=results,
            score=row.score,
            answers=answers,
            completed_at=row.completed_at
        )
    
    @staticmethod
    async def get_user_test_results(db: AsyncSession, user_id: str, test_type: Optional[str] = None) -> List[TestResult]:
        """获取用户的测试结果列表"""
        base_query = """
            SELECT id, user_id, test_type, results, score, answers, completed_at
            FROM test_results 
            WHERE user_id = :user_id
        """
        
        params = {"user_id": user_id}
        
        if test_type:
            base_query += " AND test_type = :test_type"
            params["test_type"] = test_type
        
        base_query += " ORDER BY completed_at DESC"
        
        result = await db.execute(text(base_query), params)
        rows = result.fetchall()
        
        test_results = []
        for row in rows:
            results = json.loads(row.results) if row.results else {}
            answers = json.loads(row.answers) if row.answers else {}
            
            test_result = TestResult(
                id=row.id,
                user_id=row.user_id,
                test_type=row.test_type,
                results=results,
                score=row.score,
                answers=answers,
                completed_at=row.completed_at
            )
            test_results.append(test_result)
        
        return test_results
