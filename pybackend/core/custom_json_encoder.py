from json import JSONEncoder
from datetime import datetime
from api.endpoints.alarm.schemas import AlarmPerceptionPullVO


"""
@Created on: 2025/05/06 16:39
@Author: Soren
@Des: JSON格式化工具, 可通过类型判断后续添加格式化信息
"""

class JSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, AlarmPerceptionPullVO):
           return obj.model_dump() if hasattr(obj, 'model_dump') else (obj.dict() if hasattr(obj, 'dict') else obj.__dict__)
        return super().default(obj)
    