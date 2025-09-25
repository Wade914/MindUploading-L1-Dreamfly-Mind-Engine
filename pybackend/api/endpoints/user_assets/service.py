"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 用户资产管理 - 业务逻辑
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, insert, update, delete
from .models import ConsciousnessAsset, CreateAssetRequest, UpdateAssetRequest, DashboardStats


class UserAssetsService:
    """用户资产服务"""
    
    @staticmethod
    async def get_user_consciousness_assets(db: AsyncSession, user_id: str) -> List[ConsciousnessAsset]:
        """获取用户的意识体资产列表"""
        query = text("""
            SELECT id, user_id, name, description, type, completeness, activity_score, 
                   sync_status, status, tags, interactions_count, rating, pricing_model, 
                   avatar_url, last_sync_at, created_at, updated_at
            FROM user_consciousness_assets 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = await db.execute(query, {"user_id": user_id})
        rows = result.fetchall()
        
        assets = []
        for row in rows:
            # 解析JSON字段
            tags = json.loads(row.tags) if row.tags else []
            pricing_model = json.loads(row.pricing_model) if row.pricing_model else None
            
            asset = ConsciousnessAsset(
                id=row.id,
                user_id=row.user_id,
                name=row.name,
                description=row.description,
                type=row.type,
                completeness=row.completeness,
                activity_score=row.activity_score,
                sync_status=row.sync_status,
                status=row.status,
                tags=tags,
                interactions_count=row.interactions_count,
                rating=float(row.rating) if row.rating else 0.0,
                pricing_model=pricing_model,
                avatar_url=row.avatar_url,
                last_sync_at=row.last_sync_at,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            assets.append(asset)
        
        return assets
    
    @staticmethod
    async def create_consciousness_asset(db: AsyncSession, user_id: str, asset_data: CreateAssetRequest) -> ConsciousnessAsset:
        """创建新的意识体资产"""
        # 准备数据
        tags_json = json.dumps(asset_data.tags, ensure_ascii=False)
        pricing_model_json = json.dumps(asset_data.pricing_model.model_dump(), ensure_ascii=False) if asset_data.pricing_model else None
        
        query = text("""
            INSERT INTO user_consciousness_assets 
            (user_id, name, description, type, tags, pricing_model, created_at, updated_at)
            VALUES (:user_id, :name, :description, :type, :tags, :pricing_model, 
                    datetime('now'), datetime('now'))
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "name": asset_data.name,
            "description": asset_data.description,
            "type": asset_data.type,
            "tags": tags_json,
            "pricing_model": pricing_model_json
        })
        
        asset_id = result.scalar()
        await db.commit()
        
        # 返回创建的资产
        return await UserAssetsService.get_consciousness_asset_by_id(db, asset_id)
    
    @staticmethod
    async def get_consciousness_asset_by_id(db: AsyncSession, asset_id: int) -> Optional[ConsciousnessAsset]:
        """根据ID获取意识体资产"""
        query = text("""
            SELECT id, user_id, name, description, type, completeness, activity_score, 
                   sync_status, status, tags, interactions_count, rating, pricing_model, 
                   avatar_url, last_sync_at, created_at, updated_at
            FROM user_consciousness_assets 
            WHERE id = :asset_id
        """)
        
        result = await db.execute(query, {"asset_id": asset_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # 解析JSON字段
        tags = json.loads(row.tags) if row.tags else []
        pricing_model = json.loads(row.pricing_model) if row.pricing_model else None
        
        return ConsciousnessAsset(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            description=row.description,
            type=row.type,
            completeness=row.completeness,
            activity_score=row.activity_score,
            sync_status=row.sync_status,
            status=row.status,
            tags=tags,
            interactions_count=row.interactions_count,
            rating=float(row.rating) if row.rating else 0.0,
            pricing_model=pricing_model,
            avatar_url=row.avatar_url,
            last_sync_at=row.last_sync_at,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    @staticmethod
    async def update_consciousness_asset(db: AsyncSession, asset_id: int, user_id: str, asset_data: UpdateAssetRequest) -> Optional[ConsciousnessAsset]:
        """更新意识体资产"""
        # 构建更新字段
        update_fields = []
        params = {"asset_id": asset_id, "user_id": user_id}
        
        if asset_data.name is not None:
            update_fields.append("name = :name")
            params["name"] = asset_data.name
        
        if asset_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = asset_data.description
        
        if asset_data.type is not None:
            update_fields.append("type = :type")
            params["type"] = asset_data.type
        
        if asset_data.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = json.dumps(asset_data.tags, ensure_ascii=False)
        
        if asset_data.pricing_model is not None:
            update_fields.append("pricing_model = :pricing_model")
            params["pricing_model"] = json.dumps(asset_data.pricing_model.model_dump(), ensure_ascii=False)
        
        if asset_data.status is not None:
            update_fields.append("status = :status")
            params["status"] = asset_data.status
        
        if not update_fields:
            return await UserAssetsService.get_consciousness_asset_by_id(db, asset_id)
        
        update_fields.append("updated_at = datetime('now')")
        
        query = text(f"""
            UPDATE user_consciousness_assets 
            SET {', '.join(update_fields)}
            WHERE id = :asset_id AND user_id = :user_id
        """)
        
        await db.execute(query, params)
        await db.commit()
        
        return await UserAssetsService.get_consciousness_asset_by_id(db, asset_id)
    
    @staticmethod
    async def delete_consciousness_asset(db: AsyncSession, asset_id: int, user_id: str) -> bool:
        """删除意识体资产"""
        query = text("""
            DELETE FROM user_consciousness_assets 
            WHERE id = :asset_id AND user_id = :user_id
        """)
        
        result = await db.execute(query, {"asset_id": asset_id, "user_id": user_id})
        await db.commit()
        
        return result.rowcount > 0
    
    @staticmethod
    async def get_user_dashboard_stats(db: AsyncSession, user_id: str) -> DashboardStats:
        """获取用户仪表板统计数据 - 从实际数据动态计算"""
        try:
            # 1. 统计用户的意识体资产数量
            assets_result = await db.execute(
                text("SELECT COUNT(*) FROM user_consciousness_assets WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            assets_count = assets_result.scalar() or 0

            # 2. 统计用户的记忆片段数量
            memory_result = await db.execute(
                text("SELECT COUNT(*) FROM memory_fragments WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            memory_count = memory_result.scalar() or 0

            # 3. 统计用户的总交互次数（从意识体资产的interactions_count求和）
            interaction_result = await db.execute(
                text("SELECT COALESCE(SUM(interactions_count), 0) FROM user_consciousness_assets WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            interaction_count = interaction_result.scalar() or 0

            # 4. 统计用户的总收入（从transactions表）
            revenue_result = await db.execute(
                text("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE seller_id = :user_id AND status = 'completed'"),
                {"user_id": user_id}
            )
            total_revenue = revenue_result.scalar() or 0

            # 5. 统计本月收入
            monthly_revenue_result = await db.execute(
                text("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE seller_id = :user_id
                    AND status = 'completed'
                    AND strftime('%Y-%m', completed_at) = strftime('%Y-%m', 'now')
                """),
                {"user_id": user_id}
            )
            monthly_revenue = monthly_revenue_result.scalar() or 0

            # 6. 计算意识协合度（基于TTFD测试结果）
            # 查询用户最新的TTFD测试结果
            ttfd_result = await db.execute(
                text("""
                    SELECT score FROM test_results
                    WHERE user_id = :user_id AND test_type = 'ttfd'
                    ORDER BY completed_at DESC
                    LIMIT 1
                """),
                {"user_id": user_id}
            )
            latest_ttfd_score = ttfd_result.scalar()

            if latest_ttfd_score is not None:
                # 如果有TTFD测试结果，直接使用TTFD得分作为意识协合度
                consciousness_level = int(latest_ttfd_score)
            else:
                # 如果没有TTFD测试结果，使用默认算法（鼓励用户进行测试）
                consciousness_level = min(50, max(0, (assets_count * 5) + (interaction_count // 200)))
                # 最高只能到50分，鼓励用户完成TTFD测试获得更高分数

            # 7. 计算知识点数（基于记忆片段数量和资产完整度）
            completeness_result = await db.execute(
                text("SELECT COALESCE(AVG(completeness), 0) FROM user_consciousness_assets WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            avg_completeness = completeness_result.scalar() or 0
            knowledge_points = min(100, max(0, (memory_count * 2) + (avg_completeness // 2)))

            return DashboardStats(
                consciousness_level=int(consciousness_level),
                memory_count=int(memory_count),
                interaction_count=int(interaction_count),
                knowledge_points=int(knowledge_points),
                assets_count=int(assets_count),
                total_revenue=int(total_revenue),
                monthly_revenue=int(monthly_revenue)
            )
        except Exception as e:
            print(f"获取仪表板统计失败: {e}")
            # 返回默认值
            return DashboardStats(
                consciousness_level=0,
                memory_count=0,
                interaction_count=0,
                knowledge_points=0,
                assets_count=0,
                total_revenue=0,
                monthly_revenue=0
            )
