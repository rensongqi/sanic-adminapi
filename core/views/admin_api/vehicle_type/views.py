"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
from dataclasses import dataclass
from datetime import datetime

# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import VehicleType
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
                "vehicle_types": [
                    {
                        "id(主键)": 9,
                        "vehicle_type_no(车辆型号序号)": 11,
                        "vehicle_type_name(车辆型号名称)": "中型特殊结构货车",
                        "modify_state()": 0,
                        "modify_time()": "2018-09-13 15:56:44",
                        "vehicle_type_info(备注)": "",
                        "upload_state()": 1
                    },
                ]
            }
        },
    },
    description='返回车辆型号列表',
)


class GetVehicleTypes(HTTPMethodView):
    """
    车辆型号管理（查询）
    """

    @openapi.definition(
        summary="数据维护-车辆型号",
        description="获取车辆型号",
        response=response_example,
    )
    # @login_required
    async def get(self, request):

        try:
            vehicle_type_names = await VehicleType.filter(modify_state=0)
            return response_ok(dict(vehicle_types=[vehicle_type.to_dict() for vehicle_type in vehicle_type_names]),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆型号信息获取失败")


@dataclass
class VehicleTypeRecord:
    vehicle_type_name: str  # 车辆型号名称
    vehicle_type_info: str  # 备注


@dataclass
class VehicleTypeInsertBody:
    new_record: VehicleTypeRecord


@dataclass
class VehicleTypeUpdateBody:
    old_record_id: int
    new_record: VehicleTypeRecord


class InsertVehicleTypes(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-车辆型号-新建",
        description="新建车辆型号",
        body=RequestBody(
            content={
                "application/json": VehicleTypeInsertBody,
            },
            description="""
                new_record: {
                    vehicle_type_name: str  # 车辆型号名称
                    vehicle_type_info: str  # 备注
                }
                
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=VehicleTypeInsertBody)
    async def post(self, request, body: VehicleTypeInsertBody):
        query_json = request.json
        new_record = query_json['new_record']
        print(new_record)
        try:
            async with in_transaction():
                vehicle_type = await VehicleType.create(
                    **new_record,
                    vehicle_type_no=0,
                    modify_state=0,
                    modify_time=str(datetime.strftime(
                        datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    upload_state=1,
                )
            return response_ok(dict(vehicle_type=vehicle_type.to_dict()),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆型号信息创建失败")


class UpdateVehicleTypes(HTTPMethodView):

    @openapi.definition(
        summary="车辆信息管理-车辆型号管理-编辑",
        description="新建车辆型号",
        parameter=[
            Parameter("action", str, "query", required=True,
                      description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": VehicleTypeUpdateBody,
            },
            description="""
                old_record_id: int          # 旧记录id
                new_record: {
                    vehicle_type_name: str  # 车辆型号名称
                    vehicle_type_info: str  # 备注
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=VehicleTypeUpdateBody)
    async def post(self, request, body):
        query_json = request.json
        old_record_id = query_json['old_record_id']
        new_record = query_json['new_record']
        action = request.args.get("action", 'update')
        modify_state = 0
        print(action)
        if action == 'delete':
            modify_state = 2
        try:
            async with in_transaction():
                vehicle_type_update_num = await VehicleType \
                    .select_for_update() \
                    .filter(id=old_record_id) \
                    .update(
                        **new_record,
                        modify_state=modify_state,
                        modify_time=str(datetime.strftime(
                            datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    )

            return response_ok(dict(vehicle_type_update_num=vehicle_type_update_num),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆型号信息更新失败")
