
from dataclasses import asdict, is_dataclass
from typing import List, Type, TypeVar, Generic
from pydantic import BaseModel
import importlib
import logging

# -*- coding:utf-8 -*-
"""
@Created on: 2025/02/16 10:32
@Author: Alan
@Des: 工具函数
"""

import hashlib
import uuid


def random_str():
    """
    唯一随机字符串
    :return: str
    """
    only = hashlib.md5(str(uuid.uuid1()).encode(encoding='UTF-8')).hexdigest()
    return str(only)


T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)

def transform_objects(source_list: List[object], target_class: Type[U]) -> List[U]:
    """
    实体类对象列表转换为值对象列表
    :param source_list: 实体类对象列表
    :param target_class: 值对象类的类型
    :return: 值对象列表
    """
    target_list = []
    if not source_list:
        return target_list

    # 自动获取实体类的类型
    entity_class = type(source_list[0])

    for entity in source_list:
        if not isinstance(entity, entity_class):
            raise ValueError(f"Expected instance of {entity_class.__name__}, got {type(entity).__name__}")
        fields_to_include = [field for field in dir(entity) if not field.startswith("__") and not callable(getattr(entity, field))]
        target_data = {field: getattr(entity, field) for field in fields_to_include}
        target = target_class(**target_data)
        target_list.append(target)
    return target_list

def import_modules(modules: list, desc: str, **kwargs):
    """
    动态导入模块
    :param modules: 模块列表
    :param desc: 描述
    :param kwargs: 参数
    :return:
    """
    for module in modules:
        if not module:
            continue
        try:
            module_pag = importlib.import_module(module[0:module.rindex(".")])
            getattr(module_pag, module[module.rindex(".") + 1:])(**kwargs)
        except ModuleNotFoundError:
            logging.error(f"AttributeError：导入{desc}失败，未找到该模块：{module}")
        except AttributeError:
            logging.error(f"ModuleNotFoundError：导入{desc}失败，未找到该模块下的方法：{module}")    

file_type_mapping = {
    'document': ['txt', 'md', 'markdown', 'pdf', 'html', 'xlsx', 'xls', 'docx', 'csv', 'eml', 'msg', 'pptx', 'ppt', 'xml', 'epub'],
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    'audio': ['mp3', 'm4a', 'wav', 'webm', 'amr'],
    'video': ['mp4', 'mov', 'mpeg', 'mpga']
}

def get_file_category(file_extension):
   
    for category, extensions in file_type_mapping.items():
        for ext in extensions:
            if ext in file_extension:
                return category

    return 'custom'           



