from dataclasses import dataclass
from sanic.views import HTTPMethodView
from tortoise.query_utils import Prefetch

from core.models import Card
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.logger import LoggerProxy
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter

from core.models import Vehicle

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class CreateIcCardData:
    card_no: str            # IC卡卡号
    num_card_invalid: int   # # 是否临时卡, true=1, false=0


class CreateIcCard(HTTPMethodView):
    # 新增ic_card信息
    @openapi.definition(
        summary="新增ic_card信息",
        description="新增ic_card信息",
        body=RequestBody(
            content={
                "application/json": CreateIcCardData,
            },
            description="""
    "card_no": str            # IC卡卡号
    "num_card_invalid": int   # 是否临时卡, true=1, false=0
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "创建ic卡信息成功",
                        "msg": "成功"
                      },
                },
            },
            description='查询ic_card信息',
        ),
    )
    # @login_required
    @validate(json=CreateIcCardData)
    async def post(self, request, body):
        body_json = request.json

        try:
            # 新增ic卡信息
            await Card.create(
                **body_json,
                change_reason="",
                card_print_no=body_json["card_no"],
                upload_state=1,
                modify_state=0
            )
            return response_ok("新增ic卡信息成功", ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="新增ic卡信息失败")


class GetIcCard(HTTPMethodView):
    # 查询ic_card 信息
    @openapi.definition(
        summary="查询ic_card信息",
        description="查询ic_card信息",
        parameter=[
            Parameter("vehicle_no", str, "query", required=False, description="车牌号"),
            Parameter("vehicle_door_no", str, "query", required=False, description="自编号"),
            Parameter("ic_card_no", str, "query", required=False, description="IC卡卡号"),
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": {
                            "ic_card": [
                                {
                                    "id": 1,
                                    "card_no": "E004000003C17306",
                                    "card_start_time": "2016-04-11 00:00:00",
                                    "card_expire_time": "2018-04-11 00:00:00",
                                    "num_card_invalid": 0,
                                    "upload_state": 1,
                                    "modify_state": 0,
                                    "change_reason": "",
                                    "card_print_no": "E004000003C17306",
                                    "vehicle_no": "",
                                    "vehicle_door_no": ""
                                }
                            ],
                            "record_count": 859,
                            "test": "ok"
                        },
                        "msg": "成功"
                    },
                },
            },
            description='查询ic_card信息',
        ),
    )
    # @login_required
    # @validate(json=QueryIcCard)
    async def get(self, request):
        vehicle_no = request.args.get("vehicle_no", "")
        vehicle_door_no = request.args.get("vehicle_door_no", "")
        ic_card_no = request.args.get("ic_card_no", "")
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))

        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        try:
            record_count = await Card.filter(card_no__contains=ic_card_no).prefetch_related(
                Prefetch(
                    "vehicles", queryset=Vehicle.filter(
                        vehicle_no__contains=vehicle_no,
                        vehicle_door_no__contains=vehicle_door_no
                    )
                )
            ).count()

            ic_cards = await Card.filter(card_no__contains=ic_card_no).prefetch_related(
                Prefetch(
                    "vehicles", queryset=Vehicle.filter(
                        vehicle_no__contains=vehicle_no,
                        vehicle_door_no__contains=vehicle_door_no
                    )
                )
            ).limit(length).offset(page_num * length)
            if len(ic_cards) > 300:
                return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")

            # for i, ic in enumerate(ic_cards):
            #     # print(i)
            #     for vehicle in ic.vehicles:
            #         print(type(vehicle), vehicle.vehicle_no, vehicle.vehicle_door_no)
            return response_ok(
                dict(
                    ic_card=[card.vehicle_to_dict() for card in ic_cards],
                    record_count=record_count,
                    test="ok"
                ),
                ECEnum.Success
            )

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="操作日志信息获取失败")


@dataclass
class UpdateIcCardData:
    id: int                 # IC卡ID
    card_no: str            # IC卡卡号
    num_card_invalid: int   # 是否临时卡, true=1, false=0


class UpdateIcCard(HTTPMethodView):
    # 更新ic_card信息
    @openapi.definition(
        summary="更新ic_card信息",
        description="更新ic_card信息",
        body=RequestBody(
            content={
                "application/json": UpdateIcCardData,
            },
            description="""
    "id": int,               # IC卡ID
    "card_no": str,          # IC卡卡号
    "num_card_invalid": int  # 是否临时卡, true=1, false=0
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "更新ic卡信息成功",
                        "msg": "成功"
                      },
                },
            },
            description='更新ic_card信息',
        ),
    )
    # @login_required
    @validate(json=UpdateIcCardData)
    async def post(self, request, body):
        body_json = request.json
        id = body_json["id"]
        card_no = body_json["card_no"]
        num_card_invalid = body_json["num_card_invalid"]
        try:
            await Card.select_for_update().filter(id=id).update(
                card_no=card_no,
                num_card_invalid=num_card_invalid,
                card_print_no=card_no
            )
            return response_ok("更新ic卡信息成功", ECEnum.Success)
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="更新ic卡信息失败")


@dataclass
class DeleteIcCardData:
    id: int         # IC卡ID


class DeleteIcCard(HTTPMethodView):
    # 报废ic_card
    @openapi.definition(
        summary="报废ic_card",
        description="报废ic_card",
        body=RequestBody(
            content={
                "application/json": DeleteIcCardData,
            },
            description="""
    "id": int   # IC卡ID
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "删除ic卡信息成功",
                        "msg": "成功"
                    },
                },
            },
            description='报废ic_card',
        ),
    )
    # @login_required
    @validate(json=DeleteIcCardData)
    async def delete(self, request, body):
        body_json = request.json
        id = body_json["id"]
        try:
            await Card.filter(id=id).delete()
            return response_ok("删除ic卡信息成功", ECEnum.Success)
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="删除ic卡信息失败")
