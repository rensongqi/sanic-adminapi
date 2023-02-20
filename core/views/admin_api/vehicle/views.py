"""
Author: rensongqi
Email: rensongqi1024@gmail.com
"""
# coding: utf-8

from datetime import datetime
import traceback
from dataclasses import dataclass


from sanic.views import HTTPMethodView
from sanic_ext import openapi
from sanic_ext import validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter
from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import Vehicle, VehicleType, Department, GarbageType, GarbageSource, Region, Driver, Card
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
# from tortoise.transactions import in_transaction
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)
response_example = Response(
    status=200,
    content={
        "application/json": {
            "example": [
                {
                    "id()": 583,
                    "vehicle_no(车牌号)": "浙07.76175",  
                    "vehicle_door_no(自编号)": "0026",
                    "department_name(所属单位)": "东城街道办事处",
                    "vehicle_type_name(车辆型号)": "中型特殊结构货车",
                    "tare_weight(皮重， 车辆自重)": "3.45",
                    "max_net_weight(核定载重)": "5.00",
                    "modify_state()": 2,
                    "modify_time()": "2018-10-07 17:20:17",
                    "vehicle_info(备注)": "",
                    "card_no(ic卡号)": "",
                    "upload_state()": 1,
                    "vehicle_use()": "",
                    "driver(司机名)": "江南街道办事处",
                    "buy_cost()": "0.00",
                    "garbage_type_name(垃圾类型、载质类型)": "生活垃圾",
                    "garbage_source_name(垃圾来源)": "东城街道办事处"
                },
            ]
        },
    },
    description='车辆信息列表',
)


class GetQueryDropItems(HTTPMethodView):
    @openapi.definition(
        summary="数据维护-车辆信息-下拉栏",
        description="下拉栏数据",
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "vehicle_types": [
                            {
                                "id": 9,
                                "vehicle_type_name(车辆类型)": "中型特殊结构货车"
                            },
                        ],
                        "depts": [
                            {
                                "id": 51,
                                "department_name(单位名称)": "永康市"
                            },
                        ],
                        "sources": [
                            {
                                "id": 267,
                                "source_name(垃圾来源名)": "浙江永康中国科技五金城会展有限公司",
                                "region_id__region_name(区域名)": "浙江永康中国科技五金城会展有限公司"
                            },
                        ],
                        "drivers": [
                            {
                                "id": 27,
                                "driver_name(司机名)": "童拥军"
                            },
                        ]
                    }


                },
            },
        )
    )
    # @login_required
    async def get(self, request):
        # vehicle_nums = await Vehicle.all().values_list("vehicle_no", flat=True)
        vehicle_types = await VehicleType.filter(modify_state=0).values_list("vehicle_type_name", flat=True)
        depts = await Department.filter(id__not=1).values_list("department_name", flat=True)
        drivers = await Driver.all().values_list("driver_name", flat=True)

        return response_ok(
            dict(
                depts=depts,
                vehicle_types=vehicle_types,
                drivers=drivers,
            ),
            ECEnum.Success
        )


@dataclass
class ScrappedVehicleQuery:
    vehicle_no__contains: str  # 车牌号
    vehicle_door_no__contains: str  # 自编号
    vehicle_type_id__vehicle_type_name: str  # 车型
    dept_id__department_name: str  # 所属单位


@dataclass
class VehicleQuery:
    vehicle_no__contains: str  # 车牌号
    vehicle_door_no__contains: str  # 自编号
    vehicle_type_id__vehicle_type_name: str  # 车型
    dept_id__department_name: str  # 所属单位
    driver: str  # 司机


# {
#             "vehicle_no__contains": "",
#             "vehicle_door_no__contains": 0,
#             "vehicle_type": "",
#             "max_net_weight__contains": 0.0,
#             "tare_weight__contains": 0.0,
#             "ic_card_no__contains": "",
#             "department": "",
#             "source__contains": "",
#             "department_sta": ""
#         }


class GetScrappedVehicles(HTTPMethodView):
    """
    车辆信息管理(查询)
    """

    @openapi.definition(
        summary="数据维护-报废车辆查询",
        description="根据条件检索车辆",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        body=RequestBody(
            content={
                "application/json": ScrappedVehicleQuery,
            },
            required=True,
            description="""
                vehicle_no__contains: str  # 车牌号
                vehicle_door_no__contains: str  # 自编号
                vehicle_type_id__vehicle_type_name: str  # 车型
                dept_id__department_name: str  # 所属单位
            """

        ),
        response=response_example,

    )
    # @login_required
    @validate(json=ScrappedVehicleQuery)
    async def post(self, request, body: ScrappedVehicleQuery):
        # 分页
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = filter_empty_kvs(request.json)
        print(query_dict)

        try:
            vehicles = Vehicle.filter(modify_state=2, **query_dict).prefetch_related(
                "dept_id",
                "vehicle_type_id",
                "card_id",
                "garbage_type_id",
                "garbage_source_id",
            )
            vehicle_num = await vehicles.count()
            # if vehicle_num > 100:
            #     return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")
            vehicles = await vehicles.limit(length).offset(page_num * length)
            return response_ok(dict(scrapped_vehicles=[vehicle.to_dict() for vehicle in vehicles], record_count=vehicle_num),
                               ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆信息获取失败")


class GetVehicles(HTTPMethodView):
    """
    车辆信息管理(查询)
    """

    @openapi.definition(
        summary="数据维护-车辆信息-查询",
        description="根据条件检索车辆",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        body=RequestBody(
            content={
                "application/json": VehicleQuery,
            },
            required=True,
            description="""
                vehicle_no__contains  车牌号
                vehicle_door_no__contains   自编号
                vehicle_type_id__vehicle_type_name      车辆型号
                dept_id__department_name    所属单位
                driver  司机名
            """

        ),
        response=response_example,
    )
    # @login_required
    @validate(json=VehicleQuery)
    async def post(self, request, body):
        # 分页
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 20))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = filter_empty_kvs(request.json)
        print(query_dict)

        try:
            vehicles = Vehicle.filter(modify_state=0, **query_dict).prefetch_related(
                "dept_id",
                "vehicle_type_id",
                "card_id",
                "garbage_type_id",
                "garbage_source_id",
            )
            vehicle_num = await vehicles.count()
            # if vehicle_num > 100:
            #     return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")
            vehicles = await vehicles.limit(length).offset(page_num * length)
            return response_ok(dict(vehicles=[vehicle.to_dict() for vehicle in vehicles], record_count=vehicle_num),
                               ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆信息获取失败")


class GetVehicleInfo(HTTPMethodView):
    """
    车辆信息管理(查询)
    """

    @openapi.definition(
        summary="数据维护-车辆信息-查看",
        description="查看某一车辆完整信息",
        parameter=[
            Parameter("id", int, "query", required=True, description="车辆信息记录主键id"),
        ],
        response=response_example,
    )
    # @login_required
    async def post(self, request):
        # 分页
        vehicle_id = request.args.get("id")

        try:
            vehicle = await Vehicle.filter(id=vehicle_id).prefetch_related(
                "dept_id",
                "vehicle_type_id",
                "card_id",
                "garbage_type_id",
                "garbage_source_id",
            )

            if len(vehicle) != 1:
                return response_ok(dict(), ECEnum.Fail, msg="数据库中车辆信息有误")

            vehicle = vehicle[0]
            if vehicle.dept_id is None or \
                    vehicle.vehicle_type_id is None or \
                    vehicle.card_id is None or \
                    vehicle.garbage_type_id is None or \
                    vehicle.garbage_source_id is None:
                return response_ok(dict(vehicle=vehicle.to_dict()), ECEnum.Fail, msg="此车辆部分信息缺失")

            return response_ok(dict(vehicle=vehicle.to_dict()), ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆信息获取失败")


@dataclass
class VehicleRecord:
    vehicle_no: str # 车牌号
    vehicle_door_no: str    #   自编号
    dept_id: int    #   单位id
    vehicle_type_id: int    #  车辆型号id
    garbage_source_id: int  #   垃圾来源id
    garbage_type_id: int    #   垃圾类型、载质类型id
    tare_weight: str    #   车辆自重
    max_net_weight: str #   车辆核定载重
    vehicle_info: str   #   备注
    driver: str #   司机名    


# new_record = {
#                 "vehicle_no": "string",
#                 "vehicle_door_no": "string",
#                 "driver": "string",
#                 "vehicle_type": "string",
#                 "weight_gross": 0.0,
#                 "weight_tare": 0.0,
#                 "weight_net": 0.0,
#                 "weight_deduction": 0.0,
#                 "trans_dept": "string",
#                 "garbage_type": "string",
#                 "garbage_source": "收集车/浙GG0610",
#               }


@dataclass
class VehicleInsertBody:
    new_record: VehicleRecord


@dataclass
class VehicleUpdateBody:
    old_record_id: int
    new_record: VehicleRecord


class GetInsertDropItems(HTTPMethodView):
    @openapi.definition(
        summary="数据维护-车辆信息-编辑/添加-下拉栏",
        description="下拉栏数据，包含关联信息，对应表id等",
    )
    # @login_required
    async def get(self, request):
        vehicle_types = await VehicleType.filter(modify_state=0).values("id", "vehicle_type_name")
        depts = await Department.filter(id__not=1).values("id", "department_name")
        source_names = await GarbageSource.all() \
            .prefetch_related("region_id") \
            .values("id", "source_name", "region_id__region_name")
        garbage_type_names = await GarbageType.filter(modify_state=0).values("id", "garbage_type_name")
        region_names = await Region.all().values("id", "region_name")
        drivers = await Driver.all().values("id", "driver_name")

        return response_ok(
            dict(
                vehicle_types=vehicle_types,
                depts=depts,
                sources=source_names,
                garbage_types=garbage_type_names,
                drivers=drivers,
            ),
            ECEnum.Success
        )


# {
#   "new_record": {
#     "vehicle_no": "string",
#     "vehicle_door_no": "string",
#     "dept_id": 338,
#     "vehicle_type_id": 9,
#     "garbage_source_id": 267,
#     "garbage_type_id": 74,
#     "tare_weight": "0.00",
#     "max_net_weight": "0.00",
#     "vehicle_info": "string",
#     "driver": "string"
#   }
# }

class InsertVehicle(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-车辆信息-添加",
        description="添加车辆数据",
        body=RequestBody(
            content={
                "application/json": VehicleInsertBody,
            },
            description="""
                除了vehicle_info(备注)字段外, 都是必填, 后续所有的备注字段都是选填
                new_record: {
                    vehicle_no: str             # 车牌号
                    vehicle_door_no: str        #   自编号
                    dept_id: int                #   单位id
                    vehicle_type_id: int        #  车辆型号id
                    garbage_source_id: int      #   垃圾来源id
                    garbage_type_id: int        #   垃圾类型、载质类型id
                    tare_weight: str            #   车辆自重
                    max_net_weight: str         #   车辆核定载重
                    vehicle_info: str           #   备注
                    driver: str                 #   司机名  
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=VehicleInsertBody)
    async def post(self, request, body: VehicleInsertBody):
        query_dict = request.json
        new_record = query_dict['new_record']

        try:
            dept_id = await Department.filter(id=new_record['dept_id']).first()
            vehicle_type_id = await VehicleType.filter(id=new_record['vehicle_type_id']).first()
            garbage_type_id = await GarbageType.filter(id=new_record['garbage_type_id']).first()
            garbage_source_id = await GarbageSource.filter(id=new_record['garbage_source_id']).first()
            new_record['dept_id'] = dept_id
            new_record['vehicle_type_id'] = vehicle_type_id
            new_record['garbage_type_id'] = garbage_type_id
            new_record['garbage_source_id'] = garbage_source_id

            async with in_transaction():
                # related_garbage_source = await GarbageSource.filter(source_name=new_record['garbage_source'])
                # if len(related_garbage_source) != 1:
                #     return response_ok(dict(), ECEnum.Fail, msg="对应垃圾来源数据有误")
                # new_record['garbage_source'] = related_garbage_source[0]
                vehicle = await Vehicle.create(
                    **new_record,
                    modify_state=0,
                    card_id=0,
                    modify_time=str(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    buy_cost="0.00",
                    upload_state=1,
                )
                return response_ok(dict(vehicle=vehicle.to_dict()), ECEnum.Success)
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="车辆信息记录创建失败")


# {
#   "old_record": {
#     "vehicle_no": "浙GG9671",
#     "vehicle_door_no": "",
#     "department": "永康市环境卫生管理处",
#     "vehicle_type": "",
#     "source": "",
#     "region_name": "",
#     "garbage_type": "",
#     "tare_weight": "",
#     "max_net_weight": "5",
#     "memo": "",
#     "driver": ""
#   },
#   "new_record": {
#     "vehicle_no": "浙GG9671",
#     "vehicle_door_no": "",
#     "department": "永康市环境卫生管理处",
#     "vehicle_type": "",
#     "source": "",
#     "region_name": "",
#     "garbage_type": "",
#     "tare_weight": "",
#     "max_net_weight": "4",
#     "memo": "",
#     "driver": ""
#   }
# }


class UpdateVehicle(HTTPMethodView):
    """
    称重数据查询页面(新增)
    """

    @openapi.definition(
        summary="数据维护-车辆信息-编辑/报废",
        description="更新车辆信息",
        parameter=[
            Parameter("action", str, "query", required=True, description="update/scrap(报废)"),
        ],
        body=RequestBody(
            content={
                "application/json": VehicleUpdateBody,
            },
            description="""
                old_record_id: int              #   旧记录id
                new_record: {
                    vehicle_no: str             #   车牌号
                    vehicle_door_no: str        #   自编号
                    dept_id: int                #   单位id
                    vehicle_type_id: int        #   车辆型号id
                    garbage_source_id: int      #   垃圾来源id
                    garbage_type_id: int        #   垃圾类型、载质类型id
                    tare_weight: str            #   车辆自重
                    max_net_weight: str         #   车辆核定载重
                    vehicle_info: str           #   备注
                    driver: str                 #   司机名  
                }
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=VehicleUpdateBody)
    async def post(self, request, body: VehicleUpdateBody):
        query_dict = request.json
        old_record_id = query_dict['old_record_id']
        new_record: dict = query_dict['new_record']
        action = request.args.get("action", "update")

        try:
            modify_state = '0'
            if action == 'scrap':
                modify_state = '2'
                async with in_transaction():
                    vehicle_update_num = await Vehicle.select_for_update().filter(
                        id=old_record_id
                    ).update(
                        modify_state=modify_state,
                        modify_time=str(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    )
                    return response_ok(
                        dict(vehicle_update_num=vehicle_update_num),
                        ECEnum.Success
                    )
            elif action == 'update':
                dept_id = await Department.filter(id=new_record['dept_id']).first()
                vehicle_type_id = await VehicleType.filter(id=new_record['vehicle_type_id']).first()
                garbage_type_id = await GarbageType.filter(id=new_record['garbage_type_id']).first()
                garbage_source_id = await GarbageSource.filter(id=new_record['garbage_source_id']).first()
                new_record['dept_id'] = dept_id
                new_record['vehicle_type_id'] = vehicle_type_id
                new_record['garbage_type_id'] = garbage_type_id
                new_record['garbage_source_id'] = garbage_source_id
                async with in_transaction():
                    # related_garbage_source = await GarbageSource.filter(source_name=new_record['garbage_source'])
                    # if len(related_garbage_source) != 1:
                    #     return response_ok(dict(), ECEnum.Fail, msg="对应垃圾来源数据有误")
                    # new_record['garbage_source'] = related_garbage_source[0]

                    vehicle_update_num = await Vehicle.select_for_update().filter(
                        id=old_record_id
                    ).update(
                        **new_record,
                        modify_state=modify_state,
                        modify_time=str(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    )
                    return response_ok(
                        dict(vehicle_update_num=vehicle_update_num),
                        ECEnum.Success
                    )
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="车辆信息记录更新失败")
