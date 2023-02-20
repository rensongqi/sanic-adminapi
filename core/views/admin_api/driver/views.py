"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
import traceback
from dataclasses import dataclass

# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import Driver, Department
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
# from tortoise.transactions import in_transaction
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


@dataclass
class QueryDriver:
    dept_id: int
    driver_name: str


class GetDrivers(HTTPMethodView):
    """
    车辆型号管理（查询）
    """
    @openapi.definition(
        summary="获取司机信息",
        description="获取司机信息",
        parameter=[
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        body=RequestBody(
            content={
                "application/json": QueryDriver,
            },
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": {
                        "departments": [
                            "永康市",
                            "伟明环保能源有限公司",
                            "城西新区管委会",
                        ]
                    }
                },
            },
            description='返回所有司机列表',
        ),
    )
    # @login_required
    @validate(json=QueryDriver)
    async def post(self, request, body):
        # 分页
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 20))
        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_dict = filter_empty_kvs(request.json)
        print(query_dict)
        try:
            drivers = await Driver.filter(
                **query_dict
            ).select_related("dept_id").limit(length).offset(page_num * length)

            return response_ok(dict(drivers=[driver.to_dict() for driver in drivers]), ECEnum.Success)

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="司机信息获取失败")


@dataclass
class DriverRecord:
    driver_no: str
    driver_name: str
    dept_id: int


@dataclass
class DriverInsertBody:
    new_record: DriverRecord


@dataclass
class DriverUpdateBody:
    old_record_id: int
    new_record: DriverRecord


class InsertDriver(HTTPMethodView):
    @openapi.definition(
        summary="系统设置-用户信息管理-查询",
        description="查找用户",
        body=RequestBody(
            content={
                "application/json": DriverInsertBody,
            },
            description="""
                user_id : 登录代号
                username : 真实姓名
                password : 用户密码
                dept_id : 单位id
                upload_state : 适用以下设施
                user_class : 用户级别
                menus : 用户菜单权限
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example":
                        {
                            "users": [{
                                "用户信息key": "value"
                            }]
                        }
                },
            },
            description='返回用户信息的列表',

        ),
    )
    @validate(json=DriverInsertBody)
    async def post(self, request, body):
        query_dict = request.json
        new_record = query_dict['new_record']

        try:
            new_record['dept_id'] = await Department.filter(id=new_record['dept_id']).first()

            async with in_transaction():
                driver = await Driver.create(
                    **new_record,
                    upload_state=2
                )
                return response_ok(dict(driver=driver.to_dict()), ECEnum.Success)
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="用户记录创建失败")


class UpdateDriver(HTTPMethodView):
    @openapi.definition(
        summary="系统设置-用户信息管理-查询",
        description="查找用户",
        parameter=[
            Parameter("action", str, "query", required=True, description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": DriverUpdateBody,
            },
            description="""
                user_id : 登录代号
                username : 真实姓名
                password : 用户密码
                dept_id : 单位id
                upload_state : 适用以下设施
                user_class : 用户级别
            """,
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example":
                        {
                            "users": [{
                                "用户信息key": "value"
                            }]
                        }
                },
            },
            description='返回用户信息的列表',

        ),
    )
    @validate(json=DriverUpdateBody)
    async def post(self, request, body):
        action = request.args.get("action", "update")
        query_dict = request.json
        old_record_id = query_dict['old_record_id']
        new_record = query_dict['new_record']

        try:
            driver_update_num = 0
            if action == "update":

                new_record['dept_id'] = await Department.filter(id=new_record['dept_id']).first()
                async with in_transaction():

                    driver_update_num = await Driver.select_for_update().filter(
                        id=old_record_id
                    ).update(
                        **new_record,
                    )

            elif action == "delete":

                async with in_transaction():

                    driver_update_num = await Driver.select_for_update().filter(
                        id=old_record_id
                    ).delete()

            return response_ok(dict(driver_update_num=driver_update_num), ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="操作人员记录更新失败")
