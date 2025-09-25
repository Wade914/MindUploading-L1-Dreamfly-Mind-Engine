"""
@Created on: 2025/09/14
@Author: DreamFly Team
@Des: 文档管理 - 业务逻辑
"""

import json
import os
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .models import UserDocument, UpdateDocumentRequest, Transaction, CreateTransactionRequest, MarketConsciousnessItem


class DocumentService:
    """文档服务"""
    
    @staticmethod
    async def create_document_record(
        db: AsyncSession, 
        user_id: str, 
        filename: str, 
        file_type: str, 
        file_size: int, 
        file_path: str
    ) -> UserDocument:
        """创建文档记录"""
        query = text("""
            INSERT INTO user_documents 
            (user_id, filename, file_type, file_size, file_path, status, uploaded_at)
            VALUES (:user_id, :filename, :file_type, :file_size, :file_path, 'uploaded', datetime('now'))
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "user_id": user_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "file_path": file_path
        })
        
        doc_id = result.scalar()
        await db.commit()
        
        return await DocumentService.get_document_by_id(db, doc_id)
    
    @staticmethod
    async def get_document_by_id(db: AsyncSession, doc_id: int) -> Optional[UserDocument]:
        """根据ID获取文档"""
        query = text("""
            SELECT id, user_id, filename, file_type, file_size, file_path, extracted_text, 
                   tags, status, uploaded_at, processed_at
            FROM user_documents 
            WHERE id = :doc_id
        """)
        
        result = await db.execute(query, {"doc_id": doc_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        tags = json.loads(row.tags) if row.tags else []
        
        return UserDocument(
            id=row.id,
            user_id=row.user_id,
            filename=row.filename,
            file_type=row.file_type,
            file_size=row.file_size,
            file_path=row.file_path,
            extracted_text=row.extracted_text,
            tags=tags,
            status=row.status,
            uploaded_at=row.uploaded_at,
            processed_at=row.processed_at
        )
    
    @staticmethod
    async def get_user_documents(db: AsyncSession, user_id: str) -> List[UserDocument]:
        """获取用户的文档列表"""
        query = text("""
            SELECT id, user_id, filename, file_type, file_size, file_path, extracted_text, 
                   tags, status, uploaded_at, processed_at
            FROM user_documents 
            WHERE user_id = :user_id 
            ORDER BY uploaded_at DESC
        """)
        
        result = await db.execute(query, {"user_id": user_id})
        rows = result.fetchall()
        
        documents = []
        for row in rows:
            tags = json.loads(row.tags) if row.tags else []
            
            document = UserDocument(
                id=row.id,
                user_id=row.user_id,
                filename=row.filename,
                file_type=row.file_type,
                file_size=row.file_size,
                file_path=row.file_path,
                extracted_text=row.extracted_text,
                tags=tags,
                status=row.status,
                uploaded_at=row.uploaded_at,
                processed_at=row.processed_at
            )
            documents.append(document)
        
        return documents
    
    @staticmethod
    async def update_document(db: AsyncSession, doc_id: int, user_id: str, update_data: UpdateDocumentRequest) -> Optional[UserDocument]:
        """更新文档"""
        update_fields = []
        params = {"doc_id": doc_id, "user_id": user_id}
        
        if update_data.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = json.dumps(update_data.tags, ensure_ascii=False)
        
        if update_data.extracted_text is not None:
            update_fields.append("extracted_text = :extracted_text")
            params["extracted_text"] = update_data.extracted_text
            update_fields.append("status = 'processed'")
            update_fields.append("processed_at = datetime('now')")
        
        if not update_fields:
            return await DocumentService.get_document_by_id(db, doc_id)
        
        query = text(f"""
            UPDATE user_documents 
            SET {', '.join(update_fields)}
            WHERE id = :doc_id AND user_id = :user_id
        """)
        
        await db.execute(query, params)
        await db.commit()
        
        return await DocumentService.get_document_by_id(db, doc_id)
    
    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: int, user_id: str) -> bool:
        """删除文档"""
        # 先获取文档信息以删除文件
        document = await DocumentService.get_document_by_id(db, doc_id)
        if document and document.user_id == user_id and document.file_path:
            try:
                if os.path.exists(document.file_path):
                    os.remove(document.file_path)
            except Exception:
                pass  # 文件删除失败不影响数据库记录删除
        
        query = text("""
            DELETE FROM user_documents 
            WHERE id = :doc_id AND user_id = :user_id
        """)
        
        result = await db.execute(query, {"doc_id": doc_id, "user_id": user_id})
        await db.commit()
        
        return result.rowcount > 0


class TransactionService:
    """交易服务"""
    
    @staticmethod
    async def create_transaction(db: AsyncSession, buyer_id: str, transaction_data: CreateTransactionRequest) -> Transaction:
        """创建交易记录"""
        query = text("""
            INSERT INTO transactions 
            (buyer_id, seller_id, consciousness_id, transaction_type, amount, status, created_at)
            VALUES (:buyer_id, :seller_id, :consciousness_id, :transaction_type, :amount, 'pending', datetime('now'))
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "buyer_id": buyer_id,
            "seller_id": transaction_data.seller_id,
            "consciousness_id": transaction_data.consciousness_id,
            "transaction_type": transaction_data.transaction_type,
            "amount": transaction_data.amount
        })
        
        transaction_id = result.scalar()
        await db.commit()
        
        return await TransactionService.get_transaction_by_id(db, transaction_id)
    
    @staticmethod
    async def get_transaction_by_id(db: AsyncSession, transaction_id: int) -> Optional[Transaction]:
        """根据ID获取交易记录"""
        query = text("""
            SELECT id, buyer_id, seller_id, consciousness_id, transaction_type, amount, status, created_at, completed_at
            FROM transactions 
            WHERE id = :transaction_id
        """)
        
        result = await db.execute(query, {"transaction_id": transaction_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return Transaction(
            id=row.id,
            buyer_id=row.buyer_id,
            seller_id=row.seller_id,
            consciousness_id=row.consciousness_id,
            transaction_type=row.transaction_type,
            amount=float(row.amount),
            status=row.status,
            created_at=row.created_at,
            completed_at=row.completed_at
        )
    
    @staticmethod
    async def get_user_transactions(db: AsyncSession, user_id: str) -> List[Transaction]:
        """获取用户的交易记录"""
        query = text("""
            SELECT id, buyer_id, seller_id, consciousness_id, transaction_type, amount, status, created_at, completed_at
            FROM transactions 
            WHERE buyer_id = :user_id OR seller_id = :user_id
            ORDER BY created_at DESC
        """)
        
        result = await db.execute(query, {"user_id": user_id})
        rows = result.fetchall()
        
        transactions = []
        for row in rows:
            transaction = Transaction(
                id=row.id,
                buyer_id=row.buyer_id,
                seller_id=row.seller_id,
                consciousness_id=row.consciousness_id,
                transaction_type=row.transaction_type,
                amount=float(row.amount),
                status=row.status,
                created_at=row.created_at,
                completed_at=row.completed_at
            )
            transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    async def get_market_consciousness_items(db: AsyncSession, limit: int = 20) -> List[MarketConsciousnessItem]:
        """获取市场上的意识体商品"""
        query = text("""
            SELECT id, user_id, name, description, type, rating, interactions_count, pricing_model, avatar_url, tags
            FROM user_consciousness_assets 
            WHERE status = 'active' AND pricing_model IS NOT NULL
            ORDER BY rating DESC, interactions_count DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"limit": limit})
        rows = result.fetchall()
        
        items = []
        for row in rows:
            tags = json.loads(row.tags) if row.tags else []
            pricing_model = json.loads(row.pricing_model) if row.pricing_model else {}
            
            item = MarketConsciousnessItem(
                id=row.id,
                name=row.name,
                description=row.description,
                type=row.type,
                seller_id=row.user_id,
                rating=float(row.rating),
                interactions_count=row.interactions_count,
                pricing_model=pricing_model,
                avatar_url=row.avatar_url,
                tags=tags
            )
            items.append(item)
        
        return items
