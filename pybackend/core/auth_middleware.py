"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: JWT认证中间件
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Optional
from .jwt_auth import jwt_manager


class JWTBearer(HTTPBearer):
    """JWT Bearer认证"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                print(f"❌ JWT认证失败: 无效的认证方案 {credentials.scheme}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )

            if not self.verify_jwt(credentials.credentials):
                print(f"❌ JWT认证失败: token验证失败")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )

            print(f"✅ JWT认证成功")
            return credentials.credentials
        else:
            print(f"❌ JWT认证失败: 缺少Authorization header")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )
    
    def verify_jwt(self, token: str) -> bool:
        """验证JWT token"""
        payload = jwt_manager.verify_token(token)
        return payload is not None


# 创建JWT Bearer实例
jwt_bearer = JWTBearer()


def get_current_user_id(token: str = Depends(jwt_bearer)) -> str:
    """
    从JWT token中获取当前用户ID
    
    Args:
        token: JWT token
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 如果token无效或无法获取用户ID
    """
    user_id = jwt_manager.get_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user_id_optional(request: Request) -> Optional[str]:
    """
    可选的用户ID获取（不强制要求认证）
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        用户ID或None
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        return jwt_manager.get_user_id_from_token(token)
    except Exception:
        return None
