from dataclasses import dataclass
from sanic.views import HTTPMethodView
from core.models import CardChanged, Card
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.logger import LoggerProxy
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class QueryIcCardChangeRecords:
    vehicle_no: str         # 车牌号
    start_time: str         # 开始时间
    end_time: str           # 结束时间
    page: int               # 页数
    length: int             # 页面长度


class GetChangeInfo(HTTPMethodView):
    # 换卡记录查询
    @openapi.definition(
        summary="换卡记录查询",
        description="换卡记录查询",
        parameter=[
            Parameter("vehicle_no", str, "query", required=False, description="车牌号"),
            Parameter("start_time", str, "query", required=False, description="开始时间"),
            Parameter("end_time", str, "query", required=False, description="结束时间"),
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "ic_card_chane_records": {
                            "id": 85,
                            "ic_card_no_old": "yongkangtest111",
                            "ic_card_no_new": "20220718f6e5d4c3b2a1a019",
                            "change_card_time": "2023-02-13 00:00:00",
                            "change_reason": "丢失",
                            "operator": "rsq",
                            "remarks": "磁卡丢失",
                            "vehicle_no": "浙GA2dg7",
                            "vehicle_door_no": "647",
                            "department": "永康市环境卫生管理处",
                            "upload_state": 0
                        }
                    },
                },
            },
            description='换卡记录查询',
        ),
    )
    # @login_required
    # @validate(json=QueryIcCardChangeRecords)
    async def get(self, request):
        vehicle_no = request.args.get("vehicle_no", "")
        start_time = request.args.get("start_time", "")
        end_time = request.args.get("end_time", "")
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))
        print(vehicle_no, start_time, end_time, page_num, length)

        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        try:
            # TODO，防止SQL注入
            record_count = await CardChanged.filter(
                vehicle_no__contains=vehicle_no,
                change_card_time__range=[start_time, end_time],
            ).prefetch_related("card_id", "new_card_id", "dept_id").count()
            records = await CardChanged.filter(
                vehicle_no__contains=vehicle_no,
                change_card_time__range=[start_time, end_time],
            ).prefetch_related("card_id", "new_card_id", "dept_id").limit(length).offset(page_num * length)

            if len(records) > 300:
                return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")
            return response_ok(
                dict(
                    ic_card=[record.to_dict() for record in records],
                    record_count=record_count,
                ),
                ECEnum.Success
            )

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="换卡记录查询失败")


@dataclass
class ChangeRecords:
    card_id: int
    card_start_time: str
    card_expire_time: str
    change_card_time: str
    change_reason: int
    operator: str
    info: str
    vehicle_no: str
    vehicle_door_no: int
    dept_id: int
    new_card_id: int


class ChangeCard(HTTPMethodView):
    # IC卡换卡
    @openapi.definition(
        summary="IC卡换卡",
        description="IC卡换卡",
        body=RequestBody(
            content={
                "application/json": ChangeRecords,
            },
            description="""
                "card_id": int          # 旧的IC卡id
                "card_start_time": str  # IC卡有效期（开始时间）
                "card_expire_time": str # IC卡有效期（终止时间）
                "change_card_time": str # IC卡更换时间
                "change_reason": int    # 换卡原因, 1: 正常损坏；2:人为损坏 ; 3:丢失 
                "operator": str         # 操作员
                "info": str             # 备注
                "vehicle_no": str       # IC卡卡号
                "vehicle_door_no": int  # 是否临时卡, true=1, false=0
                "dept_id": int          # 部门id
                "new_card_id": int      # 新卡id
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "IC卡换卡成功",
                        "msg": "成功"
                    },
                },
            },
            description='IC卡换卡',
        ),
    )
    # @login_required
    @validate(json=ChangeRecords)
    async def post(self, request, body):
        body_json = request.json
        old_car_id = body_json["card_id"]
        start_time = body_json["card_start_time"]
        expire_time = body_json["card_expire_time"]
        change_card_time = body_json["change_card_time"]
        change_reason = body_json["change_reason"]
        operator = body_json["operator"]
        info = body_json["info"]
        vehicle_no = body_json["vehicle_no"]
        vehicle_door_no = body_json["vehicle_door_no"]
        dept_id = body_json["dept_id"]
        new_card_id = body_json["new_card_id"]

        try:
            # 更新card table 信息
            await Card.select_for_update().filter(id=old_car_id).update(
                card_start_time=start_time,
                card_expire_time=expire_time
            )
            # 如果card_changed表中存在则更新数据，否则创建新数据
            exist = await CardChanged.exists(card_id=old_car_id)
            if exist:
                await CardChanged.select_for_update().filter(card_id=old_car_id).update(
                    change_card_time=change_card_time,
                    change_reason=change_reason,
                    user_id=operator,
                    info=info,
                    vehicle_no=vehicle_no,
                    vehicle_door_no=vehicle_door_no,
                    dept_id=dept_id,
                    new_card_id=new_card_id,
                    upload_state=0
                )
            else:
                await CardChanged.create(
                    card_id=old_car_id,
                    change_card_time=change_card_time,
                    change_reason=change_reason,
                    user_id=operator,
                    info=info,
                    vehicle_no=vehicle_no,
                    vehicle_door_no=vehicle_door_no,
                    dept_id=dept_id,
                    new_card_id=new_card_id,
                    upload_state=0
                )
            return response_ok("IC卡换卡成功", ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="IC卡换卡失败")
