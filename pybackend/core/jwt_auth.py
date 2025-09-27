"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: JWT认证工具类
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from cfg.config import settings


class JWTManager:
    """JWT管理器"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY or "dreamfly_secret_key_2025"
        self.algorithm = settings.ALGORITHM or "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES or 1440
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT token字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌

        Args:
            token: JWT token字符串

        Returns:
            解码后的数据，如果验证失败返回None
        """
        try:
            print(f"🔍 JWT验证开始: secret_key={self.secret_key[:10]}..., algorithm={self.algorithm}")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            print(f"✅ JWT验证成功: user_id={payload.get('user_id')}")
            return payload
        except JWTError as e:
            print(f"❌ JWT验证失败: {e}")
            print(f"🔍 使用的密钥: {self.secret_key[:10]}...")
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        从token中获取用户ID
        
        Args:
            token: JWT token字符串
            
        Returns:
            用户ID，如果获取失败返回None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        检查token是否过期
        
        Args:
            token: JWT token字符串
            
        Returns:
            True表示已过期，False表示未过期
        """
        payload = self.verify_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.utcnow() > datetime.fromtimestamp(exp)


# 全局JWT管理器实例
jwt_manager = JWTManager()
