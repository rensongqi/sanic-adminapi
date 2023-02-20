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
from core.models import Region
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
                "regions": [
                    {
                        "id": 2,
                        "region_name(区域名称)": "永康市五金城黎明建筑机械批发部",
                        "upload_state": 0,
                        "order_no": "12.0"
                    },
                ]
            }
        },
    },
    description='返回所有区域列表',
)


class GetAllRegion(HTTPMethodView):
    """
    区域管理（查询）
    """

    @openapi.definition(
        summary="数据维护-区域设置",
        description="获取区域信息",
        response=response_example,
    )
    # @login_required
    async def get(self, request):
        try:
            regions = await Region.all()
            return response_ok(dict(regions=[region.to_dict() for region in regions]), ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="区域信息获取失败")


@dataclass
class RegionRecord:
    region_name: str # 区域名称


@dataclass
class RegionInsertBody:
    new_record: RegionRecord


@dataclass
class RegionUpdateBody:
    old_record_id: int
    new_record: RegionRecord


class InsertRegion(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-区域设置-新建",
        description="新建区域",
        body=RequestBody(
            content={
                "application/json": RegionInsertBody,
            },
            description="""
                region_name: str # 区域名称
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=RegionInsertBody)
    async def post(self, request, body: RegionInsertBody):
        query_json = request.json
        new_record = query_json['new_record']
        print(new_record)
        try:
            async with in_transaction():
                region = await Region.create(
                    **new_record,
                    upload_state=0,
                )
            return response_ok(dict(region=region.to_dict()),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="区域信息创建失败")


class UpdateRegion(HTTPMethodView):

    @openapi.definition(
        summary="数据维护-区域设置-编辑/删除",
        description="区域",
        parameter=[
            Parameter("action", str, "query", required=True,
                      description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": RegionUpdateBody,
            },
            description="""
                region_name: str # 区域名称
            """,
            required=True
        ),
        response=response_example,
    )
    # @login_required
    @validate(json=RegionUpdateBody)
    async def post(self, request, body):
        query_json = request.json
        old_record_id = query_json['old_record_id']
        new_record = query_json['new_record']
        action = request.args.get("action", 'update')
        print(action)
        try:
            async with in_transaction():
                if action == 'update':
                    region_update_num = await Region.select_for_update().filter(id=old_record_id) \
                        .update(**new_record)

                elif action == 'delete':
                    region_update_num = await Region.select_for_update().filter(id=old_record_id).delete()

            return response_ok(dict(region_update_num=region_update_num),
                               ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="区域信息更新失败")
