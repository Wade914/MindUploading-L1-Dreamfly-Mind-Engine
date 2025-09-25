from fastapi import Body
from typing import List, Dict, Any
from pydantic import BaseModel
import copy


class QueryParams:

    def __init__(self, params=None):
        if params:
            self.page = params.page
            self.page_size = params.page_size
            self.v_order = params.v_order
            self.v_order_field = params.v_order_field

    def dict(self, exclude: list[str] = None) -> dict:
        result = copy.deepcopy(self.__dict__)
        if exclude:
            for item in exclude:
                try:
                    del result[item]
                except KeyError:
                    pass
        return result

    def to_count(self, exclude: list[str] = None) -> dict:
        params = self.dict(exclude=exclude)
        del params["page"]
        del params["page_size"]
        del params["v_order"]
        del params["v_order_field"]
        return params


class Paging(QueryParams):
    """
    列表分页
    """
    def __init__(self, page: int = 1, page_size: int = 10, v_order_field: str = None, v_order: str = None):
        super().__init__()
        self.page = page
        self.page_size = page_size
        self.v_order = v_order
        self.v_order_field = v_order_field


class IdList:
    """
    id 列表
    """
    def __init__(self, ids: list[str] = Body(..., title="ID 列表")):
        self.ids = ids

class PaginatedResponse(BaseModel):
    """分页响应模型
    
    Attributes:
        data: 分页数据列表
        total: 数据总条数
        page: 当前页码
        page_size: 每页数据条数
    """
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int

    @classmethod
    def create(cls, data: List[Dict[str, Any]], total: int, page: int, page_size: int):
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size
        )

