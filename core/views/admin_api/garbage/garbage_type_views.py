"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from datetime import datetime
from dataclasses import dataclass

# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.transactions import in_transaction

from core.models import GarbageType, GarbageSource, GarbageType
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
                "garbage_types": [
                    {
                        "id()": 41,
                        "garbage_type_no(载质类型编号)": "AO",
                        "garbage_type_name(载质类型名称)": "生活垃圾",
                        "garbage_price(垃圾单价)": "1.00",
                        "modify_state()": 0,
                        "modify_time()": "2015-04-27 14:49:27",
                        "garbage_type_info(备注)": "",
                        "upload_state()": 1
                    },
                ]
            }
        },
    },
    description='返回垃圾类型信息列表',
)


@dataclass
class GarbageTypeRecord:
    garbage_type_name: str  # 载质类型名称
    garbage_price: str  # 垃圾单价
    garbage_type_info: str  # 备注


@dataclass
class GarbageTypeInsertBody:
    new_record: GarbageTypeRecord


@dataclass
class GarbageTypeUpdateBody:
    old_record_id: int
    new_record: GarbageTypeRecord


class GetGarbageType(HTTPMethodView):
    """
    载质类型管理（查询）
    """

    @openapi.definition(
        summary="数据维护-载质类型",
        description="获取垃圾类型信息",
        response=response_example,
    )
    # @login_required
    async def get(self, request):
        try:
            garbage_types = await GarbageType.filter(modify_state=0)
            return response_ok(dict(garbage_types=[garbage_type.to_dict() for garbage_type in garbage_types]),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="垃圾类型信息获取失败")


class InsertGarbageType(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-载质类型-新建",
        description="新建载质类型",
        body=RequestBody(
            content={
                "application/json": GarbageTypeInsertBody,
            },
            description="""
                new_record:{
                    garbage_type_name: str  # 载质类型名称
                    garbage_price: str  # 垃圾单价, 传入str
                    garbage_type_info: str  # 备注
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=GarbageTypeInsertBody)
    async def post(self, request, body):
        query_json = request.json
        new_record = query_json['new_record']
        print(query_json)
        try:
            async with in_transaction():
                garbage_type = await GarbageType.create(
                    **new_record,
                    garbage_type_no="NO",
                    modify_state=0,
                    modify_time=str(datetime.strftime(
                        datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    upload_state=1,
                )
                return response_ok(dict(garbage_type=garbage_type.to_dict()),
                                   ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="载质类型信息创建失败")


class UpdateGarbageType(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-载质类型-编辑/删除",
        description="新建载质类型",
        parameter=[
            Parameter("action", str, "query", required=True,
                      description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": GarbageTypeUpdateBody,
            },
            description="""
                old_record_id: int 
                new_record:{
                    garbage_type_name: str  # 载质类型名称
                    garbage_price: str  # 垃圾单价, 传入str
                    garbage_type_info: str  # 备注
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=GarbageTypeUpdateBody)
    async def post(self, request, body):
        query_json = request.json
        old_record_id = query_json['old_record_id']
        new_record = query_json['new_record']
        action = request.args.get('action', 'update')
        modify_state = 0
        if action == 'update':
            modify_state = 0
        elif action == 'delete':
            modify_state = 2
        try:
            async with in_transaction():
                garbage_type_update_num = await GarbageType\
                    .select_for_update() \
                    .filter(id=old_record_id) \
                    .update(
                        **new_record,
                        modify_state=modify_state,
                        modify_time=str(datetime.strftime(
                            datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    )

                return response_ok(dict(garbage_type_update_num=garbage_type_update_num),
                                   ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="载质类型信息更新失败")
