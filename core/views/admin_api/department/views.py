"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
import json
import traceback
from dataclasses import dataclass
from datetime import datetime
# coding: utf-8
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response, RequestBody
from sanic_ext import openapi, validate
from tortoise.transactions import in_transaction

from core.libs.utils import filter_empty_kvs
from core.models import Department
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
                "departments": [
                    {
                        "id": 1399,
                        "department_code": "DefaultNo",
                        "department_name": "浙江酷移机器人有限公司",
                        "department_info": "",
                        "used": 1,
                        "unit_kind": 2,
                        "stat": 3
                    },
                ],
                "deparment_relations_dict": {
                    "北京创亿": [
                        "永康市",
                        "永康市行政执法局"
                    ],
                    "浙江嘉顺门业": [
                        "海呈再生资源有限公司"
                    ],
                    "永康市公安局": [
                        "永康市公安局龙山派出所"
                    ],
                    "伟明餐厨": [
                        "伟明餐厨污泥"
                    ]
                }
            }
        },
    },
    description="""
        "departments": [
            {
                "id": 1399,                                     id
                "department_code": "DefaultNo",                 单位编号
                "department_name": "浙江酷移机器人有限公司",        单位名称
                "department_info": "",                          单位说明
                "used": 1,                                      使用状态 (使用/暂停, 1/0)
                "unit_kind": 2,                                 单位属性 (设施/清运单位/其他单位, 1/2/3)
                "stat": 3                                       单位统计类别 (环卫中心/街乡/其他单位, 1/2/3)
            },
        ],
    """,
)


class GetAllDept(HTTPMethodView):
    """
    车辆型号管理（查询）
    """

    @openapi.definition(
        summary="系统设置-单位设置",
        description="任何单位下拉栏也可调用此接口",
        response=response_example
    )
    # @login_required
    async def get(self, request):

        try:
            departments = await Department.all()
            deparment_relations = await Department.all().select_related(
                "parent_dept_id"
            ).values(
                "department_name",
                "parent_dept_id__department_name",
                "id"
            )
            dept_relations_list= []

            def add_children(root_dict: dict, ori_d: list):
                name_list = [e['name'] for e in ori_d]
                for i, v in enumerate(root_dict['children']):
                    if v['name'] in name_list:
                        v['children'] = ori_d[name_list.index(v['name'])]['children']
                        v = add_children(v, ori_d)
                return v

            for d in deparment_relations:
                parent_dept_name = d['parent_dept_id__department_name']
                if parent_dept_name is None:
                    dept_relations_list.append(dict(
                        name=d['department_name'],
                        children=[],
                        id=d['id']
                    ))
                else:
                    dept_name_list = [e['name'] for e in dept_relations_list]
                    if parent_dept_name not in dept_name_list:
                        d1 = dict(
                            name=parent_dept_name,
                            children=[],
                            id=d['id']
                        )
                        dept_relations_list.append(d1)
                    dept_name_list = [e['name'] for e in dept_relations_list]
                    dept_relations_list[dept_name_list.index(parent_dept_name)]['children'].append(dict(
                        name=d['department_name'],
                        children=[],
                        id=d['id']
                    ))

            deparment_relations_list = list(dept_relations_list)
            print(deparment_relations_list)
            print(dept_relations_list)
            dept_relations_list[0] = add_children(dept_relations_list[0], dept_relations_list)
            print(deparment_relations_list)
            print(dept_relations_list)
            return response_ok(
                dict(
                    # departments=[department.to_dict() for department in departments],
                    dept_relations=deparment_relations_list[0],
                ),
                ECEnum.Success
            )

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="单位信息获取失败")


@dataclass
class DepartmentRecord:
    department_name: str
    department_info: str
    used: int
    unit_kind: int
    stat: int


@dataclass
class DepartmentInsertBody:
    old_record_id: int
    new_record: DepartmentRecord


@dataclass
class DepartmentUpdateBody:
    old_record_id: int
    new_record: DepartmentRecord


class InsertDepartment(HTTPMethodView):
    @openapi.definition(
        summary="系统设置-单位设置-添加",
        description="查找用户",
        body=RequestBody(
            content={
                "application/json": DepartmentInsertBody,
            },
            description="""
                department_name: 单位名称 
                department_info: 单位说明
                used: 使用状态 (使用/暂停, 1/0)
                unit_kind: 单位属性 (设施/清运单位/其他单位, 1/2/3)
                stat:   单位统计类别 (环卫中心/街乡/其他单位, 1/2/3)
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
    @validate(json=DepartmentInsertBody)
    async def post(self, request, body):
        query_dict = request.json
        new_record = query_dict['new_record']
        old_record_id = query_dict['old_record_id']

        try:
            async with in_transaction():
                new_record['parent_dept_id'] = await Department.filter(id=old_record_id).first()

                # related_garbage_source = await GarbageSource.filter(source_name=new_record['garbage_source'])
                # if len(related_garbage_source) != 1:
                #     return response_ok(dict(), ECEnum.Fail, msg="对应垃圾来源数据有误")
                # new_record['garbage_source'] = related_garbage_source[0]
                department = await Department.create(
                    **new_record,
                    department_code="DefaultNo",
                    create_time=str(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
                    upload_state=1,
                    type=0,
                    sheshi_type=0,
                )
                return response_ok(dict(department=department.to_dict()), ECEnum.Success)
        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="用户记录创建失败")


class UpdateDepartment(HTTPMethodView):
    @openapi.definition(
        summary="系统设置-用户信息管理-查询",
        description="查找用户",
        parameter=[
            Parameter("action", str, "query", required=True, description="update/delete"),
        ],
        body=RequestBody(
            content={
                "application/json": DepartmentUpdateBody,
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
    @validate(json=DepartmentUpdateBody)
    async def post(self, request, body):
        action = request.args.get("action", "update")
        query_dict = request.json
        old_record_id = query_dict['old_record_id']
        new_record = query_dict['new_record']

        try:
            department_update_num = 0
            if action == "update":

                async with in_transaction():

                    department_update_num = await Department.select_for_update().filter(
                        id=old_record_id
                    ).update(
                        **new_record,
                    )

            elif action == "delete":

                async with in_transaction():

                    department_update_num = await Department.select_for_update().filter(
                        id=old_record_id
                    ).delete()

            return response_ok(dict(department_update_num=department_update_num), ECEnum.Success)

        except Exception as e:
            traceback.print_exc()
            logger.error(e.with_traceback(None))
            return response_ok(dict(error=str(e.with_traceback(None))), ECEnum.Fail, msg="操作人员记录更新失败")
