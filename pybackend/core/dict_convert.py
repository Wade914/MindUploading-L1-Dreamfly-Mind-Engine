from typing import Dict, Tuple
from database.session import redis_client
from functools import wraps
from fastapi import FastAPI
from database.session import db_session
from sqlalchemy import text
from database.session import redis_client


def dict_converter(dict_fields: Dict[str, Tuple[str, str]]):
    def decorator(cls):
        class Config:
            from_attributes = True
        cls.model_config = Config
        
        original_serializer = getattr(cls, "model_dump", None)
        
        @wraps(cls.model_dump)
        def new_serializer(self, *args, **kwargs):
            data = original_serializer(self, *args, **kwargs) if original_serializer else super(cls, self).model_dump(*args, **kwargs)
            for field_name, (target_field, dict_type) in dict_fields.items():
                if field_name in data and data[field_name] is not None:
                    converted_value = redis_client.hget(dict_type, data[field_name])
                    data[target_field] = converted_value
            return data
        
        cls.model_dump = new_serializer
        return cls
    return decorator        


def register_dic_data(app: FastAPI):
     @app.on_event("startup")
     async def startup_event():
       async for session in db_session():
        try:
            results = await session.execute(text("select code_item_id,code_id,code_name from jxudp_dictionary"))
            rows = results.fetchall()
            for row in rows:
                code_item_id = row[0]
                code_id = row[1]
                code_name = row[2]
                redis_client.hset(code_item_id, code_id, code_name)
        except Exception as e:
            raise RuntimeError("查询出错")
        finally:
            await session.close()

DICS = [
    #"core.dict_convert.register_dic_data"
]              