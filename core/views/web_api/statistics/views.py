"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8

from datetime import datetime
import decimal
from decimal import Decimal
import traceback
from dataclasses import dataclass
from sanic.views import HTTPMethodView
from sanic_ext import openapi
from sanic_ext import validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter
from tortoise.functions import Sum, Count
from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import Vehicle, VehicleType, Department, GarbageType, GarbageSource, Region, Driver, Card, Pound, \
    Dictionary, WeightRecord, Operator
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.sql_udfs import TruncDateTime
# from tortoise.transactions import in_transaction
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


class GetTransQueryDropItems(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-清运明细表查询-下拉栏",
        description="下拉栏数据",
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "pounds(地磅站名称/收货单位)": [
                            {
                                "id": 22,
                                "comp_name(收货单位)": "伟明环保能源有限公司"
                            }
                        ],
                        "depts(作业单位名称)": [
                            {
                                "id": 1,
                                "department_name(作业单位名称)": "北京创亿"
                            },
                        ],
                        "data_types(数据类型)": [
                            "1期",
                            "2期",
                        ],
                        "regions(区域)": [
                            {
                                "id": 2,
                                "region_name": "永康市五金城黎明建筑机械批发部"
                            },
                        ],
                        "garbage_sources(垃圾来源)": [
                            {
                                "id": 267,
                                "source_name": "浙江永康中国科技五金城会展有限公司"
                            },
                        ],
                        "garbage_types(统计类别)": [
                            {
                                "id": 41,
                                "garbage_type_name": "生活垃圾"
                            },
                        ],
                        "drivers(司机名)": [
                            {
                                "id": 27,
                                "driver_name": "童拥军"
                            },
                        ],
                        "pound_garbage_statistic_type 地磅清运统计表-类型下拉栏(司机名)": [
                            {
                                "id": 1,
                                "driver_name": "永康市卫生环卫管理处"
                            },
                            {
                                "id": 2,
                                "driver_name": "去除永康市环卫管理处"
                            },
                        ],
                    }
                },
            },
            description='返回所有区域列表',
        ),
    )
    # @login_required
    async def get(self, request):
        pounds = await Pound.all().values("id", "comp_name")
        depts = await Department.all().values("id", "department_name")
        data_types = await Dictionary.filter(data_type='DataType').values_list("data_value", flat=True)
        regions = await Region.all().values("id", "region_name")
        garbage_sources = await GarbageSource.all().values("id", "source_name")
        garbage_types = await GarbageType.all().values("id", "garbage_type_name")
        drivers = await Driver.all().values("id", "driver_name")
        pound_garbage_statistic_type = [
            {
                "id": 1,
                "driver_name": "永康市卫生环卫管理处"
            },
            {
                "id": 2,
                "driver_name": "去除永康市环卫管理处"
            }
        ]
        return response_ok(
            dict(
                pounds=pounds,
                depts=depts,
                data_types=data_types,
                regions=regions,
                garbage_sources=garbage_sources,
                garbage_types=garbage_types,
                drivers=drivers,
                pound_garbage_statistic_type=pound_garbage_statistic_type,
            ),
            ECEnum.Success
        )


@dataclass
class QueryTransInfo:
    pound_id: int  # 收货单位/地磅站名称对应的id
    vehicle_id__dept_id: int  # 作业单位名称对应id
    vehicle_id__vehicle_door_no__contains: str  # 车辆自编号
    vehicle_id__vehicle_no__contains: str  # 车牌号
    info: str  # 数据类型
    garbage_source_id__region_id: int  # 区域对应id
    garbage_source_id: int  # 垃圾来源对应id
    garbage_type_id: int  # 统计类别对应id
    start_time: str  #
    end_time: str  #
    driver_id: int  # 司机名对应id


# {
#   "pound_id": 0,
#   "vehicle_id__dept_id": 0,
#   "vehicle_id__vehicle_door_no__contains": "6",
#   "vehicle_id__vehicle_no__contains": "",
#   "info": "1期",
#   "garbage_source_id__region_id": 0,
#   "garbage_source_id": 0,
#   "garbage_type_id": 0,
#   "start_time": "2020-02-01 00:00:00",
#   "end_time": "2023-02-14 00:00:00",
#   "driver_id": 0
# }


class GetTransInfo(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-清运明细表查询/称重数据明细表-查询",
        description="数据查询-清运明细表查询-查询",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度"),
        ],
        body=RequestBody(
            content={
                "application/json": QueryTransInfo,
            },
            required=True,
            description="""
                    pound_id: int   #   收货单位/地磅站名称对应的id
                    vehicle_id__dept_id: int    #   作业单位名称对应id
                    vehicle_id__vehicle_door_no__contains: str  #   车辆自编号
                    vehicle_id__vehicle_no__contains: str   #   车牌号
                    info: str   #   数据类型
                    garbage_source_id__region_id: int   #   区域对应id
                    garbage_source_id: int  #   垃圾来源对应id
                    garbage_type_id: int    #   统计类别对应id
                    start_time: str #   2022-02-01 00:00:00
                    end_time: str   #   
                    driver_id: int  #  司机名对应id
                """,
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "weight_records": [
                            {
                                "id_center()": 352856,
                                "vehicle_no(车牌号)": "浙GL2036",
                                "driver_name(司机名)": "吴洪胜一",
                                "vehicle_door_no(自编号)": "104",
                                "time_weight(进场称重时间)": "2022-02-01 03:49:03",
                                "weight_gross(毛重)": "17.60",
                                "time_leave(出场称重时间)": "2022-02-01 04:10:03",
                                "weight_tare(皮重)": "13.55",
                                "weight_net(净重)": "4.05",
                                "loading_rate(装载率)": "67.50%",
                                "pound_name(收货单位)": "伟明环保能源有限公司",
                                "dept_name(清运单位)": "永康市环境卫生管理处",
                                "weight_checker(计量员)": "null",
                                "garbage_source_name(垃圾来源)": "胜利街",
                                "garbage_type_name()": "生活垃圾",
                                "region_name(区域/发货单位)": "永康市环卫处",
                                "data_type(备注)": "自动读取",
                                "image_in()": "无图片",
                                "image_out()": "无图片",
                                "time_loading()": "null",
                                "load_meter_pos_id()": "null",
                                "info()": "2期",
                                "check_time()": "null"
                            },
                        ],
                        "record_count": 43,
                        "weight_gross_sum": "853.99",
                        "weight_tare_sum": "533.67",
                        "weight_net_sum": "320.32",
                    },

                },
            },
            description='返回所有区域列表',
        ),
    )
    # @login_required
    @validate(json=QueryTransInfo)
    async def post(self, request, body):
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 20))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = filter_empty_kvs(request.json)
        start_time = query_dict['start_time']
        end_time = query_dict['end_time']
        del query_dict['start_time']
        del query_dict['end_time']
        # 过滤
        filter_weight_records = WeightRecord.filter(
            **query_dict,
            time_weight__range=[start_time, end_time]
        )
        # 获取称重记录格个数
        weight_record_num = await filter_weight_records.count()

        # 统计毛重，皮重，净重
        total_gross_weight = await filter_weight_records.annotate(
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
        ).first()
        print(total_gross_weight)
        weight_gross_sum = 0.00
        weight_tare_sum = 0.00
        weight_net_sum = Decimal(0.00)

        if total_gross_weight.weight_gross_sum is not None and total_gross_weight.weight_tare_sum is not None:
            weight_gross_sum = total_gross_weight.weight_gross_sum
            weight_tare_sum = total_gross_weight.weight_tare_sum
            weight_net_sum = weight_gross_sum - weight_tare_sum

        # 分页
        weight_records = filter_weight_records.limit(length).offset(page_num * length)

        # 获取关联字段信息
        weight_records = await weight_records.select_related(
            "garbage_type_id",
            "driver_id",
            "user_id",
            "pound_id",
        ).prefetch_related(
            Prefetch(
                "vehicle_id",
                queryset=Vehicle.all().select_related("dept_id")
            ),
            Prefetch(
                "garbage_source_id",
                queryset=GarbageSource.all().select_related("region_id")
            ),
        )

        return response_ok(
            dict(
                weight_records=[weight_record.to_dict() for weight_record in weight_records],
                record_count=weight_record_num,
                weight_gross_sum=weight_gross_sum,
                weight_tare_sum=weight_tare_sum,
                weight_net_sum=weight_net_sum,
            ),
            ECEnum.Success
        )


@dataclass
class QueryRegionGarbageInfo:
    pound_id: int  #
    vehicle_id__dept_id: int  #
    garbage_source_id__region_id: int  #
    garbage_source_id: int  #
    garbage_type_id: int  #
    start_time: str  #
    end_time: str  #


class GetWeightInfo(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-运输区域垃圾量汇总表-查询",
        description="数据查询-运输区域垃圾量汇总表-查询",
        body=RequestBody(
            content={
                "application/json": QueryRegionGarbageInfo,
            },
            required=True,
            description="""
                pound_id: int   #   收货单位/地磅站名称对应的id
                vehicle_id__dept_id: int    #   作业单位名称对应id
                vehicle_id__vehicle_door_no__contains: str  #   车辆自编号
                vehicle_id__vehicle_no__contains: str   #   车牌号
                info: str   #   数据类型
                garbage_source_id__region_id: int   #   区域对应id
                garbage_source_id: int  #   垃圾来源对应id
                garbage_type_id: int    #   统计类别对应id
                start_time: str #   2022-02-01 00:00:00
                end_time: str   #   
                driver_id: int  #  司机名对应id
            """,
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "group_weight_records": [
                            {
                                "garbage_source_id__region_id__region_name(运输区域)": "永康市环卫处",
                                "vehicle_id__dept_id__department_name(运输单位)": "永康市环境卫生管理处",
                                "vehicle_num(车数)": 102,
                                "weight_gross_sum": "1716",
                                "weight_tare_sum": "1310.22",
                                "weight_net_sum(净重)": "405.78"
                            },
                        ],
                        "vehicle_num_total(合计-车数)": "232",
                        "weight_net_total(合计-净重)": "1449.69",
                        "sanitation_total_vehicle_num(环卫处汇总量-车数)": "127",
                        "sanitation_total_garbage_weight(环卫处汇总量-净重)": "541.59",
                        "towns_total_vehicle_num(各乡镇汇总量-车数)": "105",
                        "towns_total_garbage_weight(各乡镇汇总量-净重)": "908.10"

                    },

                },
            },
            description="""
                "garbage_source_id__region_id__region_name(运输区域)": "永康市环卫处",
                "vehicle_id__dept_id__department_name(运输单位)": "永康市环境卫生管理处",
                "vehicle_num(车数)": 102,
                "weight_gross_sum": "1716",
                "weight_tare_sum": "1310.22",
                "weight_net_sum(净重)": "405.78"
            """,
        ),
    )
    # @login_required
    @validate(json=QueryRegionGarbageInfo)
    async def post(self, request, body: QueryRegionGarbageInfo):
        query_dict = filter_empty_kvs(request.json)

        start_time = query_dict['start_time']
        end_time = query_dict['end_time']
        del query_dict['start_time']
        del query_dict['end_time']
        group_weight_records = await WeightRecord.filter(
            **query_dict,
            time_weight__range=[start_time, end_time]
        ).annotate(
            vehicle_num=Count("id_center"),
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
        ).group_by(
            "garbage_source_id__region_id__region_name",
            "vehicle_id__dept_id__department_name"
        ).values(
            "garbage_source_id__region_id__region_name",
            "vehicle_id__dept_id__department_name",
            "vehicle_num",
            "weight_gross_sum",
            "weight_tare_sum",
        )

        sanitation_dept_names = await Department.filter(id=349).values_list("department_name", flat=True)
        sanitation_dept_name = sanitation_dept_names[0]
        print(sanitation_dept_name)
        # TODO，剩余合计和按乡镇，环卫处分类
        vehicle_num_total = Decimal(0)
        weight_net_total = Decimal(0.00)
        sanitation_total_vehicle_num = Decimal(0)
        sanitation_total_garbage_weight = Decimal(0.00)
        towns_total_vehicle_num = Decimal(0)
        towns_total_garbage_weight = Decimal(0.00)
        for d in group_weight_records:
            d['weight_net_sum'] = d['weight_gross_sum'] - d['weight_tare_sum']
            vehicle_num_total += d['vehicle_num']
            weight_net_total += d['weight_net_sum']
            if d['vehicle_id__dept_id__department_name'] == sanitation_dept_name:
                sanitation_total_vehicle_num += d['vehicle_num']
                sanitation_total_garbage_weight += d['weight_net_sum']
            else:
                towns_total_vehicle_num += d['vehicle_num']
                towns_total_garbage_weight += d['weight_net_sum']

        return response_ok(
            dict(
                group_weight_records=group_weight_records,
                vehicle_num_total=vehicle_num_total,
                weight_net_total=weight_net_total,
                sanitation_total_vehicle_num=sanitation_total_vehicle_num,
                sanitation_total_garbage_weight=sanitation_total_garbage_weight,
                towns_total_vehicle_num=towns_total_vehicle_num,
                towns_total_garbage_weight=towns_total_garbage_weight,
            ),
            ECEnum.Success
        )


@dataclass
class QueryGarbageSourceTransInfo:
    pound_id: int
    vehicle_id__dept_id: int
    garbage_source_id__region_id: int
    garbage_source_id: int
    garbage_type_id: int
    month: str


class GetGarbageSourceTransInfo(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-垃圾来源清运统计表-查询",
        description="数据查询-清运明细表查询-查询",
        body=RequestBody(
            content={
                "application/json": QueryGarbageSourceTransInfo,
            },
            required=True,
            description="""
                pound_id: int   #   收货单位/地磅站名称对应的id
                vehicle_id__dept_id: int    #   作业单位名称对应id
                vehicle_id__vehicle_door_no__contains: str  #   车辆自编号
                vehicle_id__vehicle_no__contains: str   #   车牌号
                info: str   #   数据类型
                garbage_source_id__region_id: int   #   区域对应id
                garbage_source_id: int  #   垃圾来源对应id
                garbage_type_id: int    #   统计类别对应id
                start_time: str #   2022-02-01 00:00:00
                end_time: str   #   
                driver_id: int  #  司机名对应id
            """,
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "group_weight_records": [
                            {
                                "garbage_source_id__source_name(中转站名称)": "胜利街",
                                "date(日期)": "01",
                                "vehicle_num(车数)": 5
                            },
                        ],
                        "vehicle_num_groupBy_date": [
                            {
                                "date": "15",
                                "vehicle_num": 13322
                            },
                        ],
                        "vehicle_num_groupBy_garbage_source": [
                            {
                                "garbage_source_id__source_name": "null",
                                "vehicle_num": 159033
                            },
                        ]
                    },

                },
            },
        )
    )
    # @login_required
    @validate(json=QueryGarbageSourceTransInfo)
    async def post(self, request, body: QueryRegionGarbageInfo):
        query_dict = filter_empty_kvs(request.json)

        month = query_dict['month']
        del query_dict['month']
        group_weight_records = await WeightRecord.filter(
            **query_dict,
            month=month,
        ).annotate(
            vehicle_num=Count("id_center"),
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
            month=TruncDateTime('time_weight', '%Y-%m'),
            date=TruncDateTime('time_weight', '%d'),
        ).group_by(
            "garbage_source_id__source_name",
            "date"
        ).values(
            "garbage_source_id__source_name",
            "date",
            "vehicle_num",
        )

        vehicle_num_groupBy_date = await WeightRecord.filter(
            **query_dict,
        ).annotate(
            vehicle_num=Count("id_center"),
            date=TruncDateTime('time_weight', '%d'),
        ).group_by(
            "date"
        ).values(
            "date",
            "vehicle_num",
        )

        vehicle_num_groupBy_garbage_source = await WeightRecord.filter(
            **query_dict,
        ).annotate(
            vehicle_num=Count("id_center"),
        ).group_by(
            "garbage_source_id__source_name"
        ).values(
            "garbage_source_id__source_name",
            "vehicle_num",
        )

        return response_ok(
            dict(
                group_weight_records=group_weight_records,
                vehicle_num_groupBy_date=vehicle_num_groupBy_date,
                vehicle_num_groupBy_garbage_source=vehicle_num_groupBy_garbage_source,
            ),
            ECEnum.Success
        )


@dataclass
class QueryPoundGarbageInfo:
    pound_id: int
    type: int
    month: str


class GetPoundGarbageInfo(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-地磅清运统计汇总表-查询",
        description="数据查询-地磅清运统计汇总表-查询",
        body=RequestBody(
            content={
                "application/json": QueryPoundGarbageInfo,
            },
            required=True,
            description="""
                pound_id: int    收货单位
                type: int        0:全部， 1:永康市卫生环卫管理处, 2: 去除永康市环卫管理处
                month: str
            """
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "weight_records_group_by_date": [
                            {
                                "date(日期)": "01",
                                "vehicle_num(车数)": 192,
                                "weight_gross_sum(毛重)": "3176.07",
                                "weight_tare_sum(皮重)": "2181.75",
                                "weight_net_sum(净重)": "994.32"
                            },
                        ],
                        "vehicle_num_total": 4765,
                        "weight_net_total": "26332.46"
                    },

                },
            },
        )
    )
    # @login_required
    @validate(json=QueryPoundGarbageInfo)
    async def post(self, request, body: QueryRegionGarbageInfo):

        query_dict = request.json
        data_type = query_dict['type']
        month = query_dict['month']
        del query_dict['month']
        del query_dict['type']
        query_dict = filter_empty_kvs(query_dict)
        weight_records_group_by_date = WeightRecord.filter(
            **query_dict,
            month=month,
        ).annotate(
            vehicle_num=Count("id_center"),
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
            month=TruncDateTime('time_weight', '%Y-%m'),
            date=TruncDateTime('time_weight', '%d'),
        ).group_by(
            "date"
        ).values(
            "date",
            "vehicle_num",
            "weight_gross_sum",
            "weight_tare_sum",
        )
        if data_type == 1:
            weight_records_group_by_date = weight_records_group_by_date.filter(vehicle_id__dept_id=51)
        elif data_type == 2:
            weight_records_group_by_date = weight_records_group_by_date.filter(vehicle_id__dept_id__not=51)

        weight_records_group_by_date = await weight_records_group_by_date

        weight_records_group_by_month = await WeightRecord.filter(
            **query_dict,
            month=month,
        ).annotate(
            month=TruncDateTime('time_weight', '%Y-%m'),
            vehicle_num=Count("id_center"),
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
        )

        for record in weight_records_group_by_date:
            record['weight_net_sum'] = record['weight_gross_sum'] - record['weight_tare_sum']

        vehicle_num_total = 0
        weight_net_total = 0.00
        weight_gross_total = 0.00
        weight_tare_total = 0.00
        if weight_records_group_by_month[0].id_center is not None:
            vehicle_num_total = weight_records_group_by_month[0].vehicle_num
            weight_net_total = weight_records_group_by_month[0].weight_gross_sum - weight_records_group_by_month[0].weight_tare_sum
            weight_gross_total = weight_records_group_by_month[0].weight_gross_sum
            weight_tare_total = weight_records_group_by_month[0].weight_tare_sum
        return response_ok(
            dict(
                weight_records_group_by_date=weight_records_group_by_date,
                vehicle_num_total=vehicle_num_total,
                weight_net_total=weight_net_total,
                weight_gross_total=weight_gross_total,
                weight_tare_total=weight_tare_total,
            ),
            ECEnum.Success
        )


@dataclass
class QueryTransInfo:
    pound_id: int
    garbage_source_id__region_id: int
    garbage_type_id: int
    info: str
    start_time: str
    end_time: str


# {
#   "pound_id": 0,
#   "vehicle_id__dept_id": 0,
#   "vehicle_id__vehicle_door_no__contains": "6",
#   "vehicle_id__vehicle_no__contains": "",
#   "info": "1期",
#   "garbage_source_id__region_id": 0,
#   "garbage_source_id": 0,
#   "garbage_type_id": 0,
#   "start_time": "2020-02-01 00:00:00",
#   "end_time": "2023-02-14 00:00:00",
#   "driver_id": 0
# }


class GetTransGroupByDateInfo(HTTPMethodView):
    @openapi.definition(
        summary="数据查询-清运量报表（按日统计）-查询",
        description="数据查询-清运明细表查询-查询",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度"),
        ],
        body=RequestBody(
            content={
                "application/json": QueryTransInfo,
            },
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "weight_records_group_by_date_source": [
                            {
                                "garbage_source_id__source_name(区域)": "胜利街",
                                "date": "2022-02-01",
                                "weight_gross_sum": "87.52",
                                "weight_tare_sum": "67.05",
                                "weight_net_sum": "20.47"
                            },
                        ],
                        "weight_records_group_by_date": [
                            {
                                "date": "2022-02-01",
                                "weight_gross_sum": "853.99",
                                "weight_tare_sum": "533.67",
                                "weight_net_sum": "320.32"
                            },
                        ],
                        "weight_records_group_by_source": [
                            {
                                "garbage_source_id__source_name(区域)": "胜利街",
                                "weight_gross_sum": "326.24",
                                "weight_tare_sum": "254.98",
                                "weight_net_sum": "71.26"
                            },
                        ],
                    },

                },
            },
        )
    )
    # @login_required
    @validate(json=QueryTransInfo)
    async def post(self, request, body):
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 20))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = filter_empty_kvs(request.json)

        start_time = query_dict['start_time']
        end_time = query_dict['end_time']
        del query_dict['start_time']
        del query_dict['end_time']
        # 按日期和垃圾来源统计
        weight_records_group_by_date_source = await WeightRecord.filter(
            **query_dict,
            time_weight__range=[start_time, end_time]
        ).select_related(
            "garbage_source_id"
        ).annotate(
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
            date=TruncDateTime('time_weight', '%Y-%m-%d'),
        ).group_by(
            "date",
            "garbage_source_id__source_name"
        ).values(
            "date",
            "weight_gross_sum",
            "weight_tare_sum",
            "garbage_source_id__source_name",
        )
        for record in weight_records_group_by_date_source:
            record['weight_net_sum'] = record['weight_gross_sum'] - record['weight_tare_sum']

        # 按日期统计
        weight_records_group_by_date = await WeightRecord.filter(
            **query_dict,
            time_weight__range=[start_time, end_time]
        ).annotate(
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
            date=TruncDateTime('time_weight', '%Y-%m-%d'),
        ).group_by(
            "date",
        ).values(
            "date",
            "weight_gross_sum",
            "weight_tare_sum",
        )
        for record in weight_records_group_by_date:
            record['weight_net_sum'] = record['weight_gross_sum'] - record['weight_tare_sum']

        # 按部门统计
        weight_records_group_by_source = await WeightRecord.filter(
            **query_dict,
            time_weight__range=[start_time, end_time]
        ).select_related(
            "garbage_source_id"
        ).annotate(
            weight_gross_sum=Sum("weight_gross"),
            weight_tare_sum=Sum("weight_tare"),
        ).group_by(
            "garbage_source_id__source_name"
        ).values(
            "weight_gross_sum",
            "weight_tare_sum",
            "garbage_source_id__source_name",
        )

        for record in weight_records_group_by_source:
            record['weight_net_sum'] = record['weight_gross_sum'] - record['weight_tare_sum']

        return response_ok(
            dict(
                weight_records_group_by_date_source=weight_records_group_by_date_source,
                weight_records_group_by_date=weight_records_group_by_date,
                weight_records_group_by_source=weight_records_group_by_source,
            ),
            ECEnum.Success
        )
