from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from typing import Optional, Type, Dict, Any, List, Tuple, Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import functools
import inspect
from contextlib import contextmanager
# 简化版本，不使用 ContextManager

ERROR_MESSAGES = {
    "string_too_short": "长度不能小于{min_length}个字符",
    "string_too_long": "长度不能大于{max_length}个字符",
    "string_pattern_mismatch": "格式不符合要求",
    "string_type": "必须是字符串类型",
    "int_type": "必须是整数类型",
    "float_type": "必须是浮点数类型",
    "number_not_gt": "必须大于{limit_value}",
    "number_not_ge": "必须大于或等于{limit_value}",
    "number_not_lt": "必须小于{limit_value}",
    "number_not_le": "必须小于或等于{limit_value}",
    "missing": "缺少必要字段",
    "none_not_allowed": "不能为空",
    "enum_mismatch": "必须是以下值之一: {permitted_values}",
    "date_type": "必须是日期格式",
    "time_type": "必须是时间格式",
    "datetime_type": "必须是日期时间格式",
    "list_type": "必须是列表类型",
    "dict_type": "必须是字典类型",
    "empty_string": "不能为空",
}

FIELD_DESCRIPTIONS: Dict[str, Dict[str, str]] = {}

def register_model(model_class: Type[BaseModel]) -> Type[BaseModel]:
    """注册模型及其字段描述"""
    model_name = model_class.__name__
    FIELD_DESCRIPTIONS[model_name] = {}
    
    for field_name, field in model_class.model_fields.items():
        description = field.description or field_name.replace("_", " ")
        FIELD_DESCRIPTIONS[model_name][field_name] = description
    
    return model_class

def get_field_description(model_name: str, field_path: List[str]) -> str:
    """递归获取字段的友好描述"""
    if not field_path:
        return ""
    
    current_field = field_path[0]
    
    if model_name in FIELD_DESCRIPTIONS:
        if current_field in FIELD_DESCRIPTIONS[model_name]:
            description = FIELD_DESCRIPTIONS[model_name][current_field]
        else:
            description = current_field
    else:
        description = current_field
    
    if len(field_path) > 1:
        nested_model_name = f"{model_name}_{current_field}"
        nested_description = get_field_description(nested_model_name, field_path[1:])
        
        if nested_description:
            return f"{description}({nested_description})"
    
    return description

def translate_error(error: dict) -> dict:
    """将Pydantic验证错误转换为中文"""
    error_type = error["type"]
    msg_template = ERROR_MESSAGES.get(error_type, error["msg"])
    
    ctx = error.get("ctx", {})
    for key, value in ctx.items():
        if key == "permitted_values":
            value = ", ".join([str(v) for v in value])
        msg_template = msg_template.replace(f"{{{key}}}", str(value))
    
    loc = list(error["loc"])
    
    model_name = "UnknownModel"  # 简化版本，使用默认模型名
    
    if loc and loc[0] == "body":
        field_path = loc[1:]
    else:
        field_path = loc
    
    field_description = get_field_description(model_name, field_path)
    
    return {
        "field": loc[1],
        "message": f"{field_description}{msg_template}"
    }