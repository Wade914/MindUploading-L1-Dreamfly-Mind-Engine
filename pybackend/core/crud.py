"""
@Created on: 2025/05/06 16:39
@Author: Soren
@Des: CRUD基础工具类
"""

import datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, delete, update, BinaryExpression, ScalarResult, select, false, insert
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from starlette import status
from sqlalchemy.sql.selectable import Select as SelectType
from typing import Any, Union
from sqlmodel import text
from core.query import PaginatedResponse


class DalBase:
    ORDER_FIELD = ["desc", "descending"]

    OPERATOR_MAPPING = {
        'like': lambda col, val: f"{col} LIKE :{col}",
        '=': lambda col, val: f"{col} = :{col}",
        '!=': lambda col, val: f"{col} != :{col}",
        '>': lambda col, val: f"{col} > :{col}",
        '<': lambda col, val: f"{col} < :{col}",
        '>=': lambda col, val: f"{col} >= :{col}",
        '<=': lambda col, val: f"{col} <= :{col}"
    }

    def __init__(self, db: AsyncSession = None, model: Any = None, schema: Any = None):
        self.db = db
        self.model = model
        self.schema = schema

    async def get_data(
            self,
            data_id: str = None,
            v_start_sql: SelectType = None,
            v_select_from: list[Any] = None,
            v_join: list[Any] = None,
            v_outer_join: list[Any] = None,
            v_options: list[_AbstractLoad] = None,
            v_where: list[BinaryExpression] = None,
            v_order: str = None,
            v_order_field: str = None,
            v_return_none: bool = False,
            v_schema: Any = None,
            v_expire_all: bool = False,
            **kwargs
    ) -> Any:
        """
        获取单个数据，默认使用 ID 查询，否则使用关键词查询
        :param data_id: 数据 ID
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_return_none: 是否返回空 None，否认 抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化对象
        :param v_expire_all: 使当前会话（Session）中所有已加载的对象过期，确保您获取的是数据库中的最新数据，但可能会有性能损耗。
        :param kwargs: 查询参数
        :return: 默认返回 ORM 对象，如果存在 v_schema 则会返回 v_schema 结果
        """
        if v_expire_all:
            self.db.expire_all()

        if not isinstance(v_start_sql, SelectType):
            v_start_sql = select(self.model)

        if data_id is not None:
            v_start_sql = v_start_sql.where(self.model.id == data_id)

        queryset: ScalarResult = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_where=v_where,
            v_order=v_order,
            v_order_field=v_order_field,
            v_return_sql=False,
            **kwargs
        )

        if v_options:
            data = queryset.unique().first()
        else:
            data = queryset.first()

        if not data and v_return_none:
            return None

        if data and v_schema:
            return v_schema.model_validate(data).model_dump()

        if data:
            return data

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到此数据")

    async def get_datas(
            self,
            page: int = 1,
            page_size: int = 10,
            v_start_sql: SelectType = None,
            v_select_from: list[Any] = None,
            v_join: list[Any] = None,
            v_outer_join: list[Any] = None,
            v_options: list[_AbstractLoad] = None,
            v_where: list[BinaryExpression] = None,
            v_order: str = None,
            v_order_field: str = None,
            v_return_count: bool = False,
            v_return_scalars: bool = False,
            v_return_objs: bool = False,
            v_schema: Any = None,
            v_distinct: bool = False,
            v_expire_all: bool = False,
            **kwargs
    ) -> Union[list[Any], ScalarResult, tuple]:
        """
        获取数据列表
        :param page: 页码
        :param page_size: 当前页数据量
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_return_count: 默认为 False，是否返回 count 过滤后的数据总数，不会影响其他返回结果，会一起返回为一个数组
        :param v_return_scalars: 返回scalars后的结果
        :param v_return_objs: 是否返回对象
        :param v_schema: 指定使用的序列化对象
        :param v_distinct: 是否结果去重
        :param v_expire_all: 使当前会话（Session）中所有已加载的对象过期，确保您获取的是数据库中的最新数据，但可能会有性能损耗
        :param kwargs: 查询参数，使用的是自定义表达式
        :return: 返回值优先级：v_return_scalars > v_return_objs > v_schema
        """
        if v_expire_all:
            self.db.expire_all()

        sql: SelectType = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_where=v_where,
            v_order=v_order,
            v_order_field=v_order_field,
            v_return_sql=True,
            **kwargs
        )

        if v_distinct:
            sql = sql.distinct()

        count = 0
        if v_return_count:
            count_sql = select(func.count()).select_from(sql.alias())
            count_queryset = await self.db.execute(count_sql)
            count = count_queryset.one()[0]

        if page_size != 0:
            sql = sql.offset((page - 1) * page_size).limit(page_size)

        queryset = await self.db.scalars(sql)

        if v_return_scalars:
            if v_return_count:
                return queryset, count
            return queryset

        if v_options:
            result = queryset.unique().all()
        else:
            result = queryset.all()

        if v_return_objs:
            if v_return_count:
                return list(result), count
            return list(result)

        if v_schema is None: 
           v_schema = self.schema
           
        datas = [await self.out_dict(i, v_schema=v_schema) for i in result]
        if v_return_count:
            return PaginatedResponse.create(datas, count, page, page_size)
        return datas

    async def get_count(
            self,
            v_select_from: list[Any] = None,
            v_join: list[Any] = None,
            v_outer_join: list[Any] = None,
            v_where: list[BinaryExpression] = None,
            **kwargs
    ) -> int:
        """
        获取数据总数
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_where: 当前表查询条件，原始表达式
        :param kwargs: 查询参数
        """
        v_start_sql = select(func.count(self.model.id))
        sql = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_where=v_where,
            v_return_sql=True,
            **kwargs
        )
        queryset = await self.db.execute(sql)
        return queryset.one()[0]

    async def create_data(
            self,
            data,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        创建单个数据
        :param data: 创建数据
        :param v_options: 指示应使用select在预加载中加载给定的属性。
        :param v_schema: ，指定使用的序列化对象
        :param v_return_obj: ，是否返回对象
        """
        obj = ""
        if isinstance(data, dict):
            obj = self.model(**data)
        else:
            obj = self.model(**data.model_dump())
        await self.flush(obj)
        return await self.out_dict(obj, v_options, v_return_obj, v_schema)
  

    async def create_datas(self, datas: list[dict]) -> None:
        """
        批量创建数据
        :param datas: 字典数据列表
        """
        await self.db.execute(insert(self.model), datas)
        await self.db.commit()
        await self.db.flush()

    async def put_data(
            self,
            data_id: str,
            data: Any,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        更新单个数据
        :param data_id: 修改行数据的 ID
        :param data: 数据内容
        :param v_options: 指示应使用select在预加载中加载给定的属性。
        :param v_return_obj: ，是否返回对象
        :param v_schema: ，指定使用的序列化对象
        """
        obj = await self.get_data(data_id, v_options=v_options)
        obj_dict = jsonable_encoder(data)
        for key, value in obj_dict.items():
            setattr(obj, key, value)
        await self.flush(obj)
        return await self.out_dict(obj, None, v_return_obj, v_schema)
    
    async def put_datas(
            self,
            data_list: list[dict], 
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> list[Any]:
        """
        批量更新数据
        :param data_list: 包含多个数据的字典列表，每个字典需包含 'id' 字段
        :param v_options: 指示应使用select在预加载中加载给定的属性。
        :param v_return_obj: 是否返回对象
        :param v_schema: 指定使用的序列化对象
        :return: 批量更新后的数据列表
        """
        updated_objects = []
        ids = [data['id'] for data in data_list if 'id' in data]
        if not ids:
            return updated_objects

        # 批量查询要更新的对象
        queryset = await self.get_datas(
            v_where=[self.model.id.in_(ids)],
            v_options=v_options,
            v_return_objs=True
        )
        obj_dict = {obj.id: obj for obj in queryset}

        # 获取 BaseAttr 模型的所有字段
        model_fields = set(self.model.__fields__.keys())

        for data in data_list:
            data_id = data.get('id')
            if data_id in obj_dict:
                obj = obj_dict[data_id]
                for key, value in data.items():
                    if key != 'id'and key in model_fields:
                       setattr(obj, key, value)
                updated_objects.append(obj)


        for obj in updated_objects:
            await self.flush(obj)

    

    async def delete_datas(self, ids: list[str], v_soft: bool = False, **kwargs) -> None:
        """
        删除多条数据
        :param ids: 数据集
        :param v_soft: 是否执行软删除
        :param kwargs: 其他更新字段
        """
        if v_soft:
            await self.db.execute(
                update(self.model).where(self.model.id.in_(ids)).values(
                    delete_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    **kwargs
                )
            )
        else:
            await self.db.execute(delete(self.model).where(self.model.id.in_(ids)))
        await self.flush()

    async def flush(self, obj: Any = None) -> Any:
        """
        刷新到数据库
        :param obj:
        :return:
        """
        if obj:
            self.db.add(obj)
        await self.db.commit()
        if obj:
            await self.db.refresh(obj)
        return obj

    async def out_dict(
            self,
            obj: Any,
            v_options: list[_AbstractLoad] = None,
            v_return_obj: bool = False,
            v_schema: Any = None
    ) -> Any:
        """
        序列化
        :param obj:
        :param v_options: 指示应使用select在预加载中加载给定的属性。
        :param v_return_obj: ，是否返回对象
        :param v_schema: ，指定使用的序列化对象
        :return:
        """
        if v_options:
            obj = await self.get_data(obj.id, v_options=v_options)
        if v_return_obj:
            return obj
        if v_schema:
            return v_schema.model_validate(obj).model_dump()
        return self.schema.model_validate(obj).model_dump()

    async def filter_core(
            self,
            v_start_sql: SelectType = None,
            v_select_from: list[Any] = None,
            v_join: list[Any] = None,
            v_outer_join: list[Any] = None,
            v_options: list[_AbstractLoad] = None,
            v_where: list[BinaryExpression] = None,
            v_order: str = None,
            v_order_field: str = None,
            v_return_sql: bool = False,
            **kwargs
    ) -> Union[ScalarResult, SelectType]:
        """
        数据过滤核心功能
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_return_sql: 是否直接返回 sql
        :return: 返回过滤后的总数居 或 sql
        """
        if not isinstance(v_start_sql, SelectType):
            v_start_sql = select(self.model)

        sql = self.add_relation(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options
        )

        if v_where:
            sql = sql.where(*v_where)

        sql = self.add_filter_condition(sql, **kwargs)

        if v_order_field and (v_order in self.ORDER_FIELD):
            sql = sql.order_by(getattr(self.model, v_order_field).desc(), self.model.id.desc())
        elif v_order_field:
            sql = sql.order_by(getattr(self.model, v_order_field), self.model.id)
        elif v_order in self.ORDER_FIELD:
            sql = sql.order_by(self.model.id.desc())

        if v_return_sql:
            return sql

        queryset = await self.db.scalars(sql)

        return queryset

    def add_relation(
            self,
            v_start_sql: SelectType,
            v_select_from: list[Any] = None,
            v_join: list[Any] = None,
            v_outer_join: list[Any] = None,
            v_options: list[_AbstractLoad] = None,
    ) -> SelectType:
        """
        关系查询，关系加载
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        """
        if v_select_from:
            v_start_sql = v_start_sql.select_from(*v_select_from)

        if v_join:
            for relation in v_join:
                table = relation[0]
                if isinstance(table, str):
                    table = getattr(self.model, table)
                if len(relation) == 2:
                    v_start_sql = v_start_sql.join(table, relation[1])
                else:
                    v_start_sql = v_start_sql.join(table)

        if v_outer_join:
            for relation in v_outer_join:
                table = relation[0]
                if isinstance(table, str):
                    table = getattr(self.model, table)
                if len(relation) == 2:
                    v_start_sql = v_start_sql.outerjoin(table, relation[1])
                else:
                    v_start_sql = v_start_sql.outerjoin(table)

        if v_options:
            v_start_sql = v_start_sql.options(*v_options)

        return v_start_sql

    def add_filter_condition(self, sql: SelectType, **kwargs) -> SelectType:
        """
        添加过滤条件
        :param sql:
        :param kwargs: 关键词参数
        """
        conditions = self.__dict_filter(**kwargs)
        if conditions:
            sql = sql.where(*conditions)
        return sql

    def __dict_filter(self, **kwargs) -> list[BinaryExpression]:
        """
        字典过滤
        :param model:
        :param kwargs:
        """
        conditions = []
        for field, value in kwargs.items():
            if value is not None and value != "":
                attr = getattr(self.model, field)
                if isinstance(value, tuple):
                    if len(value) == 1:
                        if value[0] == "None":
                            conditions.append(attr.is_(None))
                        elif value[0] == "not None":
                            conditions.append(attr.isnot(None))
                        else:
                            raise RuntimeError("语法错误")
                    elif len(value) == 2 and value[1] not in [None, [], ""]:
                        if value[0] == "date":
                            conditions.append(func.date_format(attr, "%Y-%m-%d") == value[1])
                        elif value[0] == "like":
                            conditions.append(attr.like(f"%{value[1]}%"))
                        elif value[0] == "in":
                            conditions.append(attr.in_(value[1]))
                        elif value[0] == "between" and len(value[1]) == 2:
                            conditions.append(attr.between(value[1][0], value[1][1]))
                        elif value[0] == "month":
                            conditions.append(func.date_format(attr, "%Y-%m") == value[1])
                        elif value[0] == "!=":
                            conditions.append(attr != value[1])
                        elif value[0] == ">":
                            conditions.append(attr > value[1])
                        elif value[0] == ">=":
                            conditions.append(attr >= value[1])
                        elif value[0] == "<=":
                            conditions.append(attr <= value[1])
                        else:
                            raise RuntimeError("语法错误")
                else:
                    conditions.append(attr == value)
        return conditions

    def __condition_filter(self, **kwargs) -> tuple[list[str], dict]:
        """
        字典过滤，将输入的关键字参数转换为 SQL 查询条件和参数。

        :param kwargs: 关键字参数，支持特定的操作符格式。
        :return: 包含 SQL 条件字符串的列表和对应的参数字典。
        """

        conditions = []
        sql_params = {}

        def process_condition(field, operator, val):
            if operator not in self.OPERATOR_MAPPING:
                raise RuntimeError(f"不支持的操作符: {operator}")
            condition_func = self.OPERATOR_MAPPING[operator]
            condition = condition_func(field, val)
            conditions.append(condition)
            if operator == 'like':
                sql_params[field] = f"%{val}%"
            else:
                sql_params[field] = val

        for field, value in kwargs.items():
            if isinstance(value, (tuple, list)) and len(value) == 2 and value[1] not in [None, [], ""]:
                operator, val = value
                process_condition(field, operator, val)

        return conditions, sql_params


    async def execute_query(self, sql: str, params: dict, schema: any = None):
        """
        执行 SQL 查询并返回结果，若传入 schema 则返回指定模式的对象
        :param sql: 查询的 SQL 语句
        :param params: 查询参数
        :param schema: 可选，用于序列化结果的模式
        :return: 若传入 schema 则返回序列化后的对象或 None，未传入则返回原始查询结果或 None
        """
        statement = text(sql)
        result = await self.db.execute(statement, params)
        row = result.fetchone()
        if row:
            if schema:
                row_dict = dict(zip(result.keys(), row))
                return schema(**row_dict)
            return row
        return None


    async def execute_query_all(self, sql: str, params: dict, schema: any):
        """
        执行 SQL 查询并返回所有结果，以指定模式的对象列表形式返回
        :param sql: 查询的 SQL 语句
        :param params: 查询参数
        :param schema: 用于序列化结果的模式
        :return: 序列化后的对象列表
        """
        statement = text(sql)
        result = await self.db.execute(statement, params)
        rows = result.fetchall()
        datas = []
        for row in rows:
            row_dict = dict(zip(result.keys(), row))
            datas.append(schema(**row_dict))
        return datas    

    def _generate_paginated_sql(self, sql: str, page: int, page_size: int):
        """
        生成用于分页查询的 SQL 语句和计数 SQL 语句
        :param sql: 原始查询 SQL 语句
        :param page: 页码
        :param page: 当前页数据量
        :return: 分页 SQL 语句和计数 SQL 语句
        """
        count_sql = f"SELECT COUNT(*) FROM ({sql}) AS subquery"
        offset = (page - 1) * page_size
        limit_sql = f" LIMIT {page_size} OFFSET {offset}"
        full_sql = sql + limit_sql
        return full_sql, count_sql

    async def execute_paginated_query(
        self,
        sql: str,
        params: any,
        schema: any,
        table_alias: str = "t"
    ):
        """
        执行分页查询并返回分页结果
        :param sql: 查询的 SQL 语句
        :param params: 分页参数，需包含 page 和 page_size 属性
        :param schema: 用于序列化结果的模式
        :return: 分页响应对象
        """
    
        conditions, sql_params = self.__condition_filter(**params)
        exec_sql = None
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            exec_sql = sql + where_clause
        else:
            exec_sql = sql

        order_field = params.get('v_order_field')
        order_rule = params.get('v_order') 
        if order_field is None:
            order_field = table_alias + '.create_time'
        if order_rule is None:
            order_rule = 'desc'  

        exec_sql += f" ORDER BY {order_field} {order_rule}"
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        full_sql, count_sql = self._generate_paginated_sql(exec_sql, page, page_size)    

        count_result = await self.db.execute(text(count_sql),sql_params)
        count = count_result.scalar()

        result = await self.db.execute(text(full_sql),sql_params)
        rows = result.fetchall()

        datas = []
        for row in rows:
            row_dict = dict(zip(result.keys(), row))
            model_instance = schema(**row_dict)
            datas.append(model_instance.model_dump())

        return PaginatedResponse.create(datas, count, page, page_size)


    async def execute_unconditional_paginated_query(
        self,
        sql: str,
        params: any,
        schema: any,
        table_alias: str = "t"
    ):
        """
        执行分页查询并返回分页结果
        :param sql: 查询的 SQL 语句
        :param params: 分页参数，需包含 page 和 page_size 属性
        :param schema: 用于序列化结果的模式
        :return: 分页响应对象
        """
        order_field = params.get('v_order_field')
        order_rule = params.get('v_order') 
        if order_field is None:
            order_field = table_alias + '.create_time'
        if order_rule is None:
            order_rule = 'desc'  

        sql += f" ORDER BY {order_field} {order_rule}"
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        full_sql, count_sql = self._generate_paginated_sql(sql, page, page_size)    

        count_result = await self.db.execute(text(count_sql),params)
        count = count_result.scalar()

        result = await self.db.execute(text(full_sql),params)
        rows = result.fetchall()

        datas = []
        for row in rows:
            row_dict = dict(zip(result.keys(), row))
            model_instance = schema(**row_dict)
            datas.append(model_instance.model_dump())

        return PaginatedResponse.create(datas, count, page, page_size)
