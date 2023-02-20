"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
import datetime
import traceback
from dataclasses import dataclass

# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import GarbageType, GarbageSource, Region
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
# from tortoise.transactions import in_transaction
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)

response_example = Response(
    status=200,
    content={
        "application/json": {
            "example": {
                "garbage_sources": [
                    {
                        "id()": 267,
                        "source_name(来源地名称)": "浙江永康中国科技五金城会展有限公司",
                        "source_flag(来源地类型)": 1,
                        "info(虚拟来源)": "",
                        "upload_state()": 1,
                        "source_id()": 267,
                        "code()": 0,
                        "region_name()": "浙江永康中国科技五金城会展有限公司",
                        "virtual_source()": ""
                    },
                ]
            }
        },
    },
    description='返回垃圾来源地列表',
)


@dataclass
class GarbageSourceRecord:
    source_flag: int  # 来源地类型  行政区/设施, 1/2
    source_name: str  # 来源地名称
    virtual_source: str  # 虚拟来源
    region_id: int  # 区域
    info: str  # 备注


@dataclass
class GarbageSourceInsertBody:
    new_record: GarbageSourceRecord


@dataclass
class GarbageSourceUpdateBody:
    old_record_id: int
    new_record: GarbageSourceRecord


class GetGarbageSource(HTTPMethodView):
    """
    垃圾来源管理（查询）
    """

    @openapi.definition(
        summary="数据维护-垃圾来源",
        description="获取垃圾来源",
        response=response_example,
    )
    # @login_required
    async def get(self, request):
        try:
            garbage_sources = await GarbageSource.all().prefetch_related("region_id")
            return response_ok(dict(garbage_sources=[garbage_source.to_dict() for garbage_source in garbage_sources]), ECEnum.Success)
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="垃圾来源地信息获取失败")


class InsertGarbageSource(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-垃圾来源-新建",
        description="新建垃圾来源",
        body=RequestBody(
            content={
                "application/json": GarbageSourceInsertBody,
            },
            description="""
                new_record:{
                    source_flag: int  # 来源地类型 行政区/设施, 1/2
                    source_name: str  # 来源地名称
                    virtual_source: str  # 虚拟来源
                    region_id: int  # 区域
                    info: str  # 备注
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=GarbageSourceInsertBody)
    async def post(self, request, body):
        query_json = request.json
        new_record = query_json['new_record']
        print(new_record)
        try:
            async with in_transaction():
                region = await Region.filter(id=new_record['region_id']).first()
                new_record['region_id'] = region
                garbage_source = await GarbageSource.create(
                    **new_record,
                    upload_state=1,
                    source_id=0,
                    code=0,
                )
                return response_ok(dict(garbage_source=garbage_source.to_dict()),
                                   ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="垃圾来源信息创建失败")


class UpdateGarbageSource(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-垃圾来源-编辑/删除",
        description="新建垃圾来源",
        parameter=[
            Parameter("action", str, "query", required=True,
                      description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": GarbageSourceUpdateBody,
            },
            description="""
                old_record_id: int # 旧记录id
                new_record:{
                    source_flag: int  # 来源地类型 行政区/设施, 1/2
                    source_name: str  # 来源地名称
                    virtual_source: str  # 虚拟来源
                    region_id: int  # 区域
                    info: str  # 备注
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=GarbageSourceUpdateBody)
    async def post(self, request, body):
        query_json = request.json
        old_record_id = query_json['old_record_id']
        new_record = query_json['new_record']
        action = request.args.get('action', 'update')
        try:
            region = await Region.filter(id=new_record['region_id']).first()
            new_record['region_id'] = region
            vehicle_type_update_num = 0
            async with in_transaction():
                if action == 'update':
                    vehicle_type_update_num = await GarbageSource\
                        .select_for_update()\
                        .filter(id=old_record_id)\
                        .update(**new_record)

                elif action == 'delete':
                    vehicle_type_update_num = await GarbageSource \
                        .filter(id=old_record_id) \
                        .delete()

                return response_ok(dict(vehicle_type_update_num=vehicle_type_update_num),
                                   ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="垃圾来源数据更新失败")
