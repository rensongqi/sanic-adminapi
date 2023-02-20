"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
import time
from dataclasses import dataclass

from sanic.views import HTTPMethodView
from tortoise.expressions import Q

from core.models import OperationLog
from core.libs.response import response_ok
from core.libs.error_code import ECEnum
from tortoise.transactions import in_transaction
from core.libs.logger import LoggerProxy
from sanic_ext import openapi
from sanic_ext import validate
from sanic_ext.extensions.openapi.definitions import RequestBody, Response, Parameter

logger: LoggerProxy = LoggerProxy(__name__)

@dataclass
class QueryOpsLog:

    log_start_time: str
    log_end_time: str
    data_start_time: str
    data_end_time: str


class GetLogs(HTTPMethodView):

    @openapi.definition(
        summary="系统设置-操作日志查询-查询按钮",
        description="获取操作日志",
        parameter=[
            Parameter("query_str", str, "query", required=False, description="任意字符串"),
            Parameter("page", int, "query", required=True, description="页数"),
            Parameter("length", int, "query", required=True, description="页面长度")
        ],
        body=RequestBody(
            content={
                "application/json": QueryOpsLog,
            },
            description="时间过滤信息",
            required=True
        ),
        response=Response(
            status=200,
            content={
                "application/json": {
                    "example": [{
                        "id": 244,
                        "log_time": "2018-03-17 16:36:27",
                        "data_time": "2018-03-17 16:36:27",
                        "account": "yhq",
                        "username": "杨汉青",
                        "log_type": "用户登陆",
                        "log_info": "登陆成功\r"
                      }],
                },
            },
            description='返回操作日志列表',
        ),
    )
    # @login_required
    @validate(json=QueryOpsLog)
    async def post(self, request, body):
        query_str = request.args.get("query_str", "")
        page_num = int(request.args.get("page", 0))
        length = int(request.args.get("length", 0))

        if length > 100 or length == 0:
            return response_ok(dict(length=length), ECEnum.Fail, msg="请将页面长度设置为大于0小于100")

        query_json = request.json
        for k in query_json:
            try:
                time.strptime(query_json[k], "%Y-%m-%d %H:%M:%S")
            except Exception:
                return response_ok(query_json, ECEnum.Fail, f"{k}传入时间格式错误")
        # {
        #     "log_start_time": "2018-03-06 06:02:37",
        #     "log_end_time": "2018-05-01 06:02:37",
        #     "data_start_time": "2018-03-06 06:02:37",
        #     "data_end_time": "2018-05-01 06:02:37"
        # }
        try:
            # TODO，防止SQL注入
            operation_logs = OperationLog.filter(
                Q(account__contains=query_str)
                | Q(username__contains=query_str)
                | Q(log_type__contains=query_str)
                | Q(log_info__contains=query_str),
                log_time__range=[query_json["log_start_time"],query_json["log_end_time"]],
                data_time__range=[query_json["data_start_time"],query_json["data_end_time"]],
                )
            record_count = await operation_logs.count()
            operation_logs = await operation_logs.limit(length).offset(page_num * length)

            if len(operation_logs) > 300:
                return response_ok(dict(length=length), ECEnum.Fail, msg="结果数目过多")

            return response_ok(
                dict(
                    operation_logs=[operation_log.to_dict() for operation_log in operation_logs],
                    record_count=record_count,
                ),
                ECEnum.Success
            )

        except Exception as e:
            logger.error(e)
            return response_ok(dict(error=str(e)), ECEnum.Fail, msg="操作日志信息获取失败")
