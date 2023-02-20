from dataclasses import dataclass
from sanic.views import HTTPMethodView
from core.models import Card, Vehicle, CardPound, Pound
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.logger import LoggerProxy
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter
from core.libs.utils import filter_empty_kvs

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class GetSignedCardInfoData:
    vehicle_no: str       # 车牌号
    vehicle_door_no: int  # 自编号
    vehicle_type_id: int  # 车辆类型编号
    pound_id: int         # 该卡能进的地磅站id
    dept_id: int          # 所属部门


class GetSignedCardInfo(HTTPMethodView):
    """
    IC卡签发管理（查询）
    """

    @openapi.definition(
        summary="根据条件检索车辆",
        description="根据条件检索车辆",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        body=RequestBody(
            content={
                "application/json": GetSignedCardInfoData,
            },
            description="""
                vehicle_no : str        # 车牌号
                vehicle_door_no : int   # 自编号
                vehicle_type_id : int   # 车型
                pound_id : int          # 该卡能进的地磅站id
                dept_id : int           # 所属部门id
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": [
                        {
                            "vehicle_no": "鄂11.29472",
                            "vehicle_door_no": "0011",
                            "dept_name": "东城街道办事处",
                            "vehicle_type_name": "中型特殊结构货车",
                            "tare_weight": "7.00",
                            "max_net_weight": "5.00",
                            "modify_state": 0,
                            "modify_time": "2018-12-29 14:05:38",
                            "vehicle_info": "",
                            "card_no": "E2000016981001120440E731",
                            "card_start_time_t": "2018-09-01 00:00:00",
                            "card_expire_time_t": "2022-12-31 00:00:00",
                            "upload_state": 1,
                            "vehicle_use": "",
                            "driver": "一百零一",
                            "pound_name": "伟明环保能源有限公司",
                            "garbage_type_name": "生活垃圾",
                            "garbage_source_name": "东城街道办事处"
                        },
                    ]
                },
            },
            description='车辆信息列表',
        ),
    )
    # @login_required
    @validate(json=GetSignedCardInfoData)
    async def post(self, request, body):
        # 分页
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = request.json
        pound_id = query_dict["pound_id"]
        vehicle_no = query_dict["vehicle_no"]
        new_dict = dict(
            vehicle_door_no=query_dict["vehicle_door_no"],
            vehicle_type_id=query_dict["vehicle_type_id"],
            dept_id=query_dict["dept_id"]
        )

        empty_k_list = []
        for k in new_dict:
            if not new_dict[k]:
                empty_k_list.append(k)

        for k in empty_k_list:
            del new_dict[k]

        try:
            vehicle_num = await Vehicle.filter(
                **new_dict,
                vehicle_no__icontains=vehicle_no
            ).prefetch_related(
                "card_id",
                "dept_id",
                "vehicle_type_id",
                "garbage_type_id",
                "garbage_source_id"
            ).count()

            vehicles = await Vehicle.filter(
                **new_dict,
                vehicle_no__icontains=vehicle_no
            ).prefetch_related(
                "card_id",
                "dept_id",
                "vehicle_type_id",
                "garbage_type_id",
                "garbage_source_id"
            ).limit(length).offset(page_num * length)

            vs = []
            for v in vehicles:
                if pound_id == 0:
                    card_pounds = await CardPound.filter(
                        card_id=v.card_id
                    ).prefetch_related("pound_id").all()
                else:
                    card_pounds = await CardPound.filter(
                        card_id=v.card_id,
                        pound_id__id=pound_id
                    ).prefetch_related("pound_id").all()
                if v.card_id is None:
                    vs.append(v.card_to_dict(""))
                for card_pound in card_pounds:
                    vs.append(v.card_to_dict(card_pound.pound_id.comp_name))
            return response_ok(
                dict(
                    vehicles=vs,
                    vehicle_num=vehicle_num,
                ),
                ECEnum.Success
            )
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="车辆信息获取失败")


@dataclass
class SignedIcCardData:
    id: int         # 车牌号
    card_start_time: str    # 自编号
    card_expire_time: str    # 车辆类型编号
    pound_id: int            # 部门id


class SignedIcCard(HTTPMethodView):
    # 签发ic卡片
    @openapi.definition(
        summary="签发ic_card",
        description="签发ic_card",
        body=RequestBody(
            content={
                "application/json": SignedIcCardData,
            },
            description="""
    id : int                     # id
    card_start_time : datetime   # IC卡有效期（开始时间）
    card_expire_time : datetime  # IC卡有效期（终止时间）
    pound_id : int               # 地磅站id
            """,
            required=False
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "签发ic卡成功",
                        "msg": "成功"
                      },
                },
            },
            description='签发ic卡',
        ),
    )
    # @login_required
    @validate(json=SignedIcCardData)
    async def post(self, request, body):
        body_json = request.json
        id = body_json["id"]
        start_time = body_json["card_start_time"]
        expire_time = body_json["card_expire_time"]
        pound_id = body_json["pound_id"]

        try:
            # 更新card table 信息
            await Card.select_for_update().filter(id=id).update(
                card_start_time=start_time,
                card_expire_time=expire_time
            )
            # 更新card_pound关系表信息
            exist = await CardPound.exists(card_id=id)
            pound = await Pound.filter(id=pound_id).first()
            card = await Card.filter(id=id).first()
            # 如果表中存在则更新数据，否则创建新数据
            if exist:
                await CardPound.select_for_update().filter(card_id=id).update(pound_id=pound)
            else:
                await CardPound.create(card_id=card, pound_id=pound, upload_state=1)

            return response_ok("签发ic卡成功", ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="签发ic卡失败")
