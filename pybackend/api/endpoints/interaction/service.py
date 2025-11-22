"""
@Created on: 2025/01/18 10:00
@Author: DreamFly Team
@Des: 交互管理 - 业务逻辑
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

# 直接使用SQL操作，不依赖ORM模型
from core.exception import UnicornException
from .params import RecordInteractionParams, UpdateInteractionCountParams
from .schemas import InteractionRecordSchema, InteractionStatsSchema


class InteractionService:
    """交互管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_interaction(self, params: RecordInteractionParams) -> InteractionRecordSchema:
        """记录交互历史"""
        try:
            # 生成交互记录ID
            interaction_id = str(uuid.uuid4())
            current_time = datetime.now()

            # 插入交互记录到数据库
            await self.db.execute(
                text("""
                    INSERT INTO interaction_history
                    (id, user_id, mind_name, user_message, ai_response, tokens_used, created_at)
                    VALUES (:id, :user_id, :mind_name, :user_message, :ai_response, :tokens_used, :created_at)
                """),
                {
                    "id": interaction_id,
                    "user_id": params.user_id,
                    "mind_name": params.mind_name,
                    "user_message": params.user_message,
                    "ai_response": params.ai_response,
                    "tokens_used": params.tokens_used,
                    "created_at": current_time
                }
            )

            # 同时更新用户意识体资产的交互次数
            await self.update_interaction_count(UpdateInteractionCountParams(
                user_id=params.user_id,
                mind_name=params.mind_name,
                increment=1
            ))

            await self.db.commit()

            return InteractionRecordSchema(
                id=interaction_id,
                user_id=params.user_id,
                mind_name=params.mind_name,
                user_message=params.user_message,
                ai_response=params.ai_response,
                tokens_used=params.tokens_used,
                created_at=current_time
            )

        except Exception as e:
            await self.db.rollback()
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ 记录交互失败详细错误:")
            print(error_detail)
            raise UnicornException(code=500, errmsg=f"记录交互失败: {str(e)}")

    async def update_interaction_count(self, params: UpdateInteractionCountParams):
        """更新交互次数"""
        try:
            # 检查是否已存在记录
            check_query = text("""
                SELECT id, interactions_count FROM user_consciousness_assets
                WHERE user_id = :user_id AND name = :mind_name
            """)
            result = await self.db.execute(check_query, {
                "user_id": params.user_id,
                "mind_name": params.mind_name
            })
            existing = result.fetchone()

            if existing:
                # 更新现有记录的交互次数
                update_query = text("""
                    UPDATE user_consciousness_assets
                    SET interactions_count = interactions_count + :increment,
                        last_interaction_at = :now,
                        updated_at = :now
                    WHERE user_id = :user_id AND name = :mind_name
                """)
                await self.db.execute(update_query, {
                    "increment": params.increment,
                    "now": datetime.now(),
                    "user_id": params.user_id,
                    "mind_name": params.mind_name
                })
            else:
                # 创建新的意识体资产记录（id字段自动生成，不需要手动指定）
                insert_query = text("""
                    INSERT INTO user_consciousness_assets
                    (user_id, name, type, completeness, interactions_count, last_interaction_at, created_at, updated_at)
                    VALUES (:user_id, :name, :type, :completeness, :interactions_count, :now, :now, :now)
                """)
                await self.db.execute(insert_query, {
                    "user_id": params.user_id,
                    "name": params.mind_name,
                    "type": "MindCopy",
                    "completeness": 85,
                    "interactions_count": params.increment,
                    "now": datetime.now()
                })

            await self.db.flush()

        except Exception as e:
            raise UnicornException(code=500, errmsg=f"更新交互次数失败: {str(e)}")

    async def get_interaction_stats(self, user_id: str, mind_name: str) -> InteractionStatsSchema:
        """获取交互统计"""
        try:
            # 获取总交互次数
            count_result = await self.db.execute(
                text("SELECT COUNT(*) FROM interaction_history WHERE user_id = :user_id AND mind_name = :mind_name"),
                {"user_id": user_id, "mind_name": mind_name}
            )
            total_interactions = count_result.scalar() or 0
            
            # 获取总token使用量
            tokens_result = await self.db.execute(
                text("SELECT COALESCE(SUM(tokens_used), 0) FROM interaction_history WHERE user_id = :user_id AND mind_name = :mind_name"),
                {"user_id": user_id, "mind_name": mind_name}
            )
            total_tokens = tokens_result.scalar() or 0
            
            # 获取最后交互时间
            last_result = await self.db.execute(
                text("SELECT MAX(created_at) FROM interaction_history WHERE user_id = :user_id AND mind_name = :mind_name"),
                {"user_id": user_id, "mind_name": mind_name}
            )
            last_interaction = last_result.scalar()
            
            return InteractionStatsSchema(
                total_interactions=total_interactions,
                total_tokens=total_tokens,
                last_interaction=last_interaction
            )
            
        except Exception as e:
            raise UnicornException(code=500, errmsg=f"获取交互统计失败: {str(e)}")
