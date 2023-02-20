"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
import traceback
from dataclasses import dataclass
from types import TracebackType

# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction
from tortoise.functions import Count, Sum

from core.libs.utils import filter_empty_kvs
from core.models import \
    WeightRecord, GarbageSource, Region, Vehicle, Department, GarbageType, VehicleType, Driver
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.sql_udfs import TruncDateTime
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)

response_example = Response(
    status=200,
    content={
        "application/json": {
            "example": {
                "weight_records": [{
                    "time_weightingT": "2019-01-01 15:31:40",
                    "vehicle_no": "浙GG7592",
                    "vehicle_door_no": "130",
                    "driver": "肖团结",
                    "vehicle_type": "重型特殊结构货车",
                    "weight_gross": 18.07,
                    "weight_tare": 13.32,
                    "weight_net": 4.75,
                    "trans_dept": "永康市环境卫生管理处",
                    "garbage_type": "生活垃圾",
                    "garbage_source": "方岩",
                    "region_name": "方岩镇"
                }, ]
            }
        },
    },
    description='返回称重信息',
)


# {
#   "vehicle_no__contains": "",
#   "vehicle_door_no__contains": "",
#   "vehicle_type": "",
#   "trans_dept": "",
#   "garbage_type": "",
#   "garbage_source": "",
#   "garbage_source__region__region_name__contains": "方岩镇",
#   "driver": "",
#   "time_filtered": true,
#   "start_time": "2019-01-01 15:00:00",
#   "end_time": "2023-01-01 17:00:00"
# }


class GetDropItems(HTTPMethodView):
    @openapi.definition(
        summary="称重信息管理-称重数据查询-查看详细-下拉栏",
        description="称重数据查询",
    )
    # @login_required
    async def get(self, request):
        vehicle_types = await VehicleType.all().values_list("vehicle_type_name", flat=True)
        depts = await Department.all().values_list("department_name", flat=True)
        garbage_types = await GarbageType.all().values_list("garbage_type_name", flat=True)
        garbage_sources = await GarbageSource.all().values_list("source_name", flat=True)
        region = await Region.all().values_list("region_name", flat=True)
        drivers = await Driver.all().values_list("driver_name", flat=True)

        return response_ok(
            dict(
                vehicle_types=vehicle_types,
                depts=depts,
                garbage_types=garbage_types,
                garbage_sources=garbage_sources,
                region=region,
                drivers=drivers,
            ),
            ECEnum.Success
        )


class GetFullWeightRecord(HTTPMethodView):
    @openapi.definition(
        summary="称重信息管理-称重数据查询-查看详细",
        description="称重数据查询",
        parameter=[
            Parameter("id", int, "query", required=True, description="记录id"),
        ],
        response=response_example,
    )
    # @login_required
    async def post(self, request):
        weight_record_id = request.args.get('id', None)
        weight_record = await WeightRecord \
            .filter(id=weight_record_id) \
            .first().prefetch_related(
            Prefetch(
                "garbage_source",
                queryset=GarbageSource.all().select_related("region"),
                to_attr="to_attr_source"
            )
        )
        weight_record_dict = weight_record.to_full_dict()
        # if not weight_record_dict:
        #     return response_ok(dict(), ECEnum.Fail, "无法获取对应垃圾来源和区域信息")

        return response_ok(dict(weight_record=weight_record_dict), ECEnum.Success)


@dataclass
class QueryWeightRecord:
    vehicle_no__contains: str
    vehicle_door_no__contains: str
    vehicle_type: str
    trans_dept: str
    garbage_type: str
    garbage_source: str
    garbage_source__region__region_name__contains: str
    driver: str
    time_filtered: bool
    start_time: str
    end_time: str


class GetWeightRecord(HTTPMethodView):
    """
    称重数据查询（查询）
    """

    @openapi.definition(
        summary="称重数据查询",
        description="称重信息管理-称重数据查询-查询",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度"),
        ],
        body=RequestBody(
            content={
                "application/json": QueryWeightRecord,
            },
            description="称重信息",
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=QueryWeightRecord)
    async def post(self, request, body):

        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 50))
        query_dict = request.json
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        print(query_dict)
        time_filtered = query_dict['time_filtered']
        query_dict = filter_empty_kvs(query_dict)
        print(query_dict)
        try:
            if time_filtered:
                start_time = query_dict['start_time']
                end_time = query_dict['end_time']
                del query_dict['start_time']
                del query_dict['end_time']
                del query_dict['time_filtered']
                weight_records = WeightRecord \
                    .filter(time_weightingT__range=[start_time, end_time]) \
                    .filter(**query_dict) \
                    # .limit(length).offset(page_num * length)

            else:
                weight_records = WeightRecord \
                    .filter(**query_dict) \
                    # .limit(length).offset(page_num * length)

            # 与source，region表关联查询获取每条记录region名
            # recs = await weight_records.all()
            # print([rec.to_dict() for rec in recs])
            # print("first:", (await WeightRecord.first()).to_dict())
            record_count = await weight_records.count()
            if record_count > 0:
                weight_records = await weight_records\
                    .limit(length).offset(page_num * length)\
                    .prefetch_related(
                        Prefetch(
                            "garbage_source",
                            queryset=GarbageSource.all().select_related("region"),
                            to_attr="to_attr_source"
                        )
                    )
            else:
                weight_records = []
            # print(a[0].fetch_related(""))
            # print(a[0].garbage_source, type(a[0].garbage_source))
            # print(a[0].to_attr_source.region.region_name, type(a[0].to_attr_source))
            # print((await a[0].garbage_source.related_model.first()).region_id)
            return response_ok(
                dict(weight_records=[weight_record.to_dict() for weight_record in weight_records], record_count=record_count),
                ECEnum.Success
            )
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="称重记录获取失败")


@dataclass
class InsertParams:
    vehicle_no: str
    vehicle_door_no: str
    driver: str
    vehicle_type: str
    weight_gross: float
    weight_tare: float
    weight_net: float
    weight_deduction: float
    trans_dept: str
    garbage_type: str
    garbage_source: str


@dataclass
class InsertRecord:
    # old_record: InsertParams
    new_record: InsertParams
    # def to_dict(self):
    #     return dict(
    #         vehicle_no=self.vehicle_no,
    #         vehicle_door_no=self.vehicle_door_no,
    #         driver=self.driver,
    #         vehicle_type=self.vehicle_type,
    #         weight_gross=self.weight_gross,
    #         weight_tare=self.weight_tare,
    #         weight_net=self.weight_net,
    #         trans_dept=self.trans_dept,
    #         garbage_type=self.garbage_type,
    #         garbage_source=self.garbage_source,
    #     )


@dataclass
class UpdateRecord:
    old_record: InsertParams
    new_record: InsertParams


@dataclass
class DeleteRecord:
    old_record: InsertParams


class InsertWeightRecord(HTTPMethodView):
    """
    称重数据查询页面（新增）
    """

    @openapi.definition(
        summary="称重信息管理-称重数据查询-新增",
        description="插入称重数据",
        body=RequestBody(
            content={
                "application/json": InsertRecord,
            },
            description="称重信息",
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=InsertRecord)
    async def post(self, request, body: InsertRecord):
        query_dict = request.json
        if not query_dict['new_record']:
            return response_ok(dict(), ECEnum.InvalidParameter)
        # TODO, 插入具体逻辑需与前段讨论，哪些字段可以为空，哪些字段需要下拉栏选择. 目前只对垃圾来源进行了校验
        new_record = filter_empty_kvs(query_dict['new_record'])
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

        try:
            async with in_transaction():
                related_garbage_source = await GarbageSource.filter(source_name=new_record['garbage_source'])
                if len(related_garbage_source) != 1:
                    return response_ok(dict(), ECEnum.Fail, msg="对应垃圾来源数据有误")

                new_record['garbage_source'] = related_garbage_source[0]
                weight_record = await WeightRecord.create(**new_record)
                return response_ok(
                    dict(weight_records=[weight_record.to_dict()]),
                    ECEnum.Success
                )
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="称重记录创建失败")


class UpdateWeightRecord(HTTPMethodView):
    """
    称重数据查询页面（新增）
    """

    @openapi.definition(
        summary="更新称重数据",
        description="更新称重数据",
        body=RequestBody(
            content={
                "application/json": UpdateRecord,
            },
            description="称重信息",
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=UpdateRecord)
    async def post(self, request, body: UpdateRecord):
        # TODO, 插入具体逻辑需与前段讨论，哪些字段可以为空，哪些字段需要下拉栏选择
        query_dict = request.json
        if not query_dict['new_record'] or not query_dict['old_record']:
            return response_ok(dict(), ECEnum.InvalidParameter)

        old_record = filter_empty_kvs(query_dict['old_record'])
        new_record = filter_empty_kvs(query_dict['new_record'])

        try:
            async with in_transaction():
                udpate_num = await WeightRecord.filter(**old_record).update(**new_record)
                return response_ok(
                    dict(udpate_num=udpate_num),
                    ECEnum.Success
                )
        except Exception as e:
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="称重记录更新失败")


class DeleteWeightRecord(HTTPMethodView):
    """
    称重数据查询页面（新增）
    """

    @openapi.definition(
        summary="称重信息管理-称重数据查询-删除",
        description="删除称重数据",
        body=RequestBody(
            content={
                "application/json": DeleteRecord,
            },
            description="称重信息",
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=DeleteRecord)
    async def post(self, request, body: DeleteRecord):
        query_dict = request.json
        # if not query_dict['old_record']:
        #     return response_ok(dict(), ECEnum.InvalidParameter)

        old_record = filter_empty_kvs(query_dict['old_record'])

        try:
            async with in_transaction():
                delete_num = await WeightRecord.filter(**old_record).delete()
                return response_ok(
                    dict(
                        delete_num=delete_num,
                        old_record=old_record,
                     ),
                    ECEnum.Success
                )
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="称重记录删除失败")


@dataclass
class WeightRecordClassifyInfo:
    vehicle_type: str
    trans_dept: str
    garbage_type: str
    garbage_source__source_name: str
    garbage_source__region__region_name: str
    time_filtered: bool
    start_time: str
    end_time: str


class ClassifyWeightRecord(HTTPMethodView):
    """
        称重分类查询
    """

    @openapi.definition(
        summary="称重分类查询-统计",
        description="称重分类查询-统计",
        body=RequestBody(
            content={
                "application/json": WeightRecordClassifyInfo,
            },
            description="称重信息",
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=WeightRecordClassifyInfo)
    async def post(self, request, body: WeightRecordClassifyInfo):
        query_dict = request.json
        print(query_dict)
        query_dict = filter_empty_kvs(query_dict)
        print(query_dict)
        try:
            # 按时间过滤
            start_time = query_dict['start_time']
            end_time = query_dict['end_time']
            del query_dict['start_time']
            del query_dict['end_time']

            weight_records = WeightRecord \
                .filter(time_weightingT__range=[start_time, end_time])

            if len(list(query_dict.keys())) != 1:
                return response_ok(dict(query_dict=query_dict), ECEnum.InvalidParameter, msg="过滤字段格式有误")

            # 分类统计并按分类项过滤
            classification = list(query_dict.keys())[0]
            if query_dict[classification] != 'all':
                weight_records = weight_records.filter(**query_dict)

            weight_records = await (
                weight_records
                .group_by(classification)
                .annotate(
                    classified_name=classification,
                    weight_gross_sum=Sum("weight_gross"),
                    weight_tare_sum=Sum("weight_tare"),
                    weight_net_sum=Sum("weight_net"),
                    vehicle_no_count=Count("vehicle_no"),
                )
                .values(
                    classification,
                    "weight_gross_sum",
                    "weight_tare_sum",
                    "weight_net_sum",
                    "vehicle_no_count",
                )
            )

            return response_ok(
                dict(weight_records=weight_records),
                ECEnum.Success
            )
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="称重记录获取失败")


@dataclass
class WeightInputInfo:
    weight: str
    weight_gross: float
    weight_tare: float
    weight_net: float
    weight_deduction: float
    vehicle_no: str
    vehicle_door_no: str
    driver: str
    garbage_source: str
    weighting_time: str
    weight_checker: str


class WeightOperation(HTTPMethodView):
    @openapi.definition(
        summary="称重操作数据获取",
        description="称重操作数据获取",
        # body=RequestBody(
        #     content={
        #         "application/json": WeightInputInfo,
        #     },
        #     description="称重信息",
        #     required=True
        # ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {

                    }
                },
            },
            description='返回处理后称重数据',
        ),
    )
    # @login_required
    # @validate(json=WeightInputInfo)
    async def get(self, request):
        # TODO. 每个字段分别是 前端传入，后端计算还是硬件这边通过socketio传输过来
        # TODO.从socket流获取数据
        data = {
            "weight": "",
            "weight_gross": 0,
            "weight_tare": 0,
            "weight_net": 0,
            "vehicle_no": "",
            "vehicle_door_no": "",
            "driver": "",
            "garbage_source": "",
            "weighting_time": "",
            "weight_checker": "",
        }
        # 查询车辆对应装载量，ic卡号等信息

        vehicle_no = data["vehicle_no"]
        filter_dict = dict(
            vehicle_no=vehicle_no,
        )
        vehicle = await Vehicle.filter(**filter_dict).first()
        # if len(vehicles) > 1:
        #     return response_ok(dict(), ECEnum.Fail, msg="车辆")
        return response_ok(
            dict(
                weight=data["weight"],
                weight_gross=vehicle.weight_gross,
                weight_tare=vehicle.weight_tare,
                weight_net=vehicle.weight_net,
                ic_card_no=vehicle.ic_card_no,
                vehicle_no=vehicle.vehicle_no,
                vehicle_door_no=vehicle.vehicle_door_no,
                load_rate=data["weight_net"] / data["weight_net"],
                driver=vehicle.driver,
                garbage_source=vehicle.garbage_type,
                weighting_time=vehicle,
                weight_checker=vehicle.weight_checker,
            )
        )
