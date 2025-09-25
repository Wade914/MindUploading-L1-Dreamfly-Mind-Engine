"""
@Created on: 2025/09/15
@Author: DreamFly Team
@Des: 通用装饰器 - 减少重复代码
"""

from functools import wraps
from typing import Callable, Any, Dict, List
from core.response import success, fail


def api_error_handler(success_msg: str = "操作成功", error_msg: str = "操作失败"):
    """
    API错误处理装饰器
    自动处理异常并返回统一格式的响应
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                if isinstance(result, dict) and 'data' in result:
                    return success(data=result['data'], msg=success_msg)
                else:
                    return success(data=result, msg=success_msg)
            except Exception as e:
                return fail(msg=f"{error_msg}: {str(e)}")
        return wrapper
    return decorator


def format_list_response(items: List[Any], key: str) -> Dict[str, Any]:
    """
    格式化列表响应
    统一处理模型列表的序列化
    """
    if hasattr(items[0], 'model_dump') if items else False:
        # Pydantic v2
        return {key: [item.model_dump() for item in items]}
    elif hasattr(items[0], 'dict') if items else False:
        # Pydantic v1 或 SQLAlchemy 模型
        return {key: [item.model_dump() if hasattr(item, 'model_dump') else item.dict() for item in items]}
    else:
        # 普通字典或其他类型
        return {key: items}


def format_single_response(item: Any, key: str) -> Dict[str, Any]:
    """
    格式化单个对象响应
    统一处理模型对象的序列化
    """
    if hasattr(item, 'model_dump'):
        # Pydantic v2
        return {key: item.model_dump()}
    elif hasattr(item, 'dict'):
        # Pydantic v1 或 SQLAlchemy 模型
        return {key: item.model_dump() if hasattr(item, 'model_dump') else item.dict()}
    else:
        # 普通字典或其他类型
        return {key: item}


def validate_user_access(user_id: str, resource_user_id: str) -> bool:
    """
    验证用户访问权限
    确保用户只能访问自己的资源
    """
    return user_id == resource_user_id


class APIResponseHelper:
    """API响应助手类"""
    
    @staticmethod
    def list_response(items: List[Any], key: str, msg: str = "获取成功") -> Dict[str, Any]:
        """返回列表响应"""
        data = format_list_response(items, key)
        return success(data=data, msg=msg)
    
    @staticmethod
    def single_response(item: Any, key: str, msg: str = "操作成功") -> Dict[str, Any]:
        """返回单个对象响应"""
        data = format_single_response(item, key)
        return success(data=data, msg=msg)
    
    @staticmethod
    def empty_response(msg: str = "操作成功") -> Dict[str, Any]:
        """返回空响应"""
        return success(msg=msg)
    
    @staticmethod
    def error_response(msg: str, code: int = 400) -> Dict[str, Any]:
        """返回错误响应"""
        return fail(msg=msg, code=code)
