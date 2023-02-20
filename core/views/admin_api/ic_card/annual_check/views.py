from dataclasses import dataclass
from sanic.views import HTTPMethodView
from core.models import Card
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.logger import LoggerProxy
from sanic_ext import openapi, validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response

from core.models import Vehicle

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class AnnualCheckData:
    id: int                     # IC卡ID
    card_start_time: str        # IC卡有效期（开始时间）
    card_expire_time: str       # IC卡有效期（终止时间）


class AnnualCheckCard(HTTPMethodView):
    # IC卡年检
    @openapi.definition(
        summary="IC卡年检",
        description="IC卡年检",
        body=RequestBody(
            content={
                "application/json": AnnualCheckData,
            },
            description="""
    id : str                     # id
    card_start_time : datetime   # IC卡有效期（开始时间）
    card_expire_time : datetime  # IC卡有效期（终止时间）
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "IC卡年检成功",
                        "msg": "成功"
                      },
                },
            },
            description='IC卡年检',
        ),
    )
    # @login_required
    @validate(json=AnnualCheckData)
    async def post(self, request, body):
        body_json = request.json
        id = body_json["id"]
        start_time = body_json["card_start_time"]
        expire_time = body_json["card_expire_time"]

        try:
            # 更新card table 信息
            await Card.select_for_update().filter(id=id).update(
                card_start_time=start_time,
                card_expire_time=expire_time
            )
            return response_ok("IC卡年检成功", ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="IC卡年检失败")
