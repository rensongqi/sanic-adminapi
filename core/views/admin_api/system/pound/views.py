from dataclasses import dataclass
from sanic.views import HTTPMethodView
from core.models import Pound
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from core.libs.logger import LoggerProxy
from sanic_ext import openapi, validate
# from tortoise.query_utils import Prefetch
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class CreatePoundsData:
    pound_no: str           # 地磅站编号
    comp_name: str          # 地磅站名称
    dept_id: int            # 所属部门id
    comments: str           # 备注


class CreatePounds(HTTPMethodView):
    # 新增地磅站信息
    @openapi.definition(
        summary="新增地磅站信息",
        description="新增地磅站信息",
        body=RequestBody(
            content={
                "application/json": CreatePoundsData,
            },
            description="""
    pound_no: str           # 地磅站编号
    comp_name: str          # 地磅站名称
    dept_id: int            # 所属部门id
    comments: str           # 备注
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "新增地磅站信息成功",
                        "msg": "成功"
                      },
                },
            },
            description='新增地磅站信息',
        ),
    )
    # @login_required
    @validate(json=CreatePoundsData)
    async def post(self, request, body):
        body_json = request.json
        print(body_json)
        try:
            # 新增地磅站信息
            await Pound.create(
                pound_no=body_json["pound_no"],
                comp_name=body_json["comp_name"],
                comments=body_json["comments"],
                upload_state=1,
                modify_state=0,
                dept_id_id=body_json["dept_id"]
            )
            return response_ok("新增地磅站信息成功", ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="新增地磅站信息失败")


class GetPounds(HTTPMethodView):
    # 查询地磅站信息
    @openapi.definition(
        summary="查询地磅站信息",
        description="查询地磅站信息",
        parameter=[
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
                            "pounds": [
                                {
                                    "id": 22,
                                    "comp_name": "伟明环保能源有限公司",
                                    "pound_no": "1100100101",
                                    "comments": "",
                                    "department_name": "伟明环保能源有限公司",
                                    "modify_time": "2016-04-10 22:34:55"
                                }
                            ],
                            "pounds_count": 1
                        },
                        "msg": "成功"
                    },
                },
            },
            description='查询地磅站信息',
        ),
    )
    # @login_required
    # @validate(json=QueryIcCard)
    async def get(self, request):
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))

        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        try:
            # TODO，防止SQL注入
            pounds = await Pound.all().prefetch_related("dept_id")
            pounds_count = await Pound.all().prefetch_related("dept_id").count()
            pounds_num = await Pound.all().prefetch_related("dept_id").limit(length).offset(page_num * length)
            if len(pounds_num) > 300:
                return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")
            return response_ok(
                dict(
                    pounds=[pound.to_dict() for pound in pounds],
                    pounds_count=pounds_count,
                ),
                ECEnum.Success
            )

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="操作日志信息获取失败")


@dataclass
class UpdatePoundsData:
    id: int                 # id
    pound_no: str           # 地磅站编号
    comp_name: str          # 地磅站名称
    dept_id: int            # 所属部门id
    comments: str           # 备注


class UpdatePounds(HTTPMethodView):
    # 更新地磅站信息
    @openapi.definition(
        summary="更新地磅站信息",
        description="更新地磅站信息",
        body=RequestBody(
            content={
                "application/json": UpdatePoundsData,
            },
            description="请求体",
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "更新地磅站信息成功",
                        "msg": "成功"
                    },
                },
            },
            description='更新地磅站信息',
        ),
    )
    # @login_required
    @validate(json=UpdatePoundsData)
    async def post(self, request, body):
        body_json = request.json
        id = body_json["id"]
        try:
            await Pound.filter(id=id).update(
                pound_no=body_json["pound_no"],
                comp_name=body_json["comp_name"],
                comments=body_json["comments"],
                dept_id_id=body_json["dept_id"]
            )
            return response_ok("更新地磅站信息成功", ECEnum.Success)
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="更新地磅站信息失败")


@dataclass
class DeletePoundsData:
    id: int           # 地磅站编号


class DeletePounds(HTTPMethodView):
    # 删除地磅站信息
    @openapi.definition(
        summary="删除地磅站信息",
        description="删除地磅站信息",
        body=RequestBody(
            content={
                "application/json": DeletePoundsData,
            },
            description="请求体",
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "code": "0",
                        "data": "删除地磅站信息成功",
                        "msg": "成功"
                    },
                },
            },
            description='删除地磅站信息',
        ),
    )
    # @login_required
    @validate(json=DeletePoundsData)
    async def delete(self, request, body):
        body_json = request.json
        id = body_json["id"]
        try:
            await Pound.filter(id=id).delete()
            return response_ok("删除地磅站信息成功", ECEnum.Success)
        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="删除地磅站信息失败")
