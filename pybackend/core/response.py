# -*- coding:utf-8 -*-
"""
@Created on: 2025/02/16 10:45 
@Author: Alan
@Des: 常用返回类型封装
"""
from typing import List


def stream_response(msg, data=None):
    """支持流式输出 返回的格式"""
    if data is None:
        data = []
    result = {
        "message": msg,
        "data": data
    }
    return result


def base_response(code, msg, data=None):
    """基础返回格式"""
    if data is None:
        data = []
    result = {
        "code": code,
        "message": msg,
        "data": data
    }
    return result


def success(data=None, msg='sucess'):
    """成功返回格式"""
    return base_response(200, msg, data)


def fail(code=-1, msg='', data=None):
    """失败返回格式"""
    return base_response(code, msg, data)