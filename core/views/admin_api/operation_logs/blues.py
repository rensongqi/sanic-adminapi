"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8

from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('operation_logs', url_prefix='/admin_api/operation_logs')

# bp.add_route(BulkWrite.as_view(), "/write")
# bp.add_route(BulkDelete.as_view(), "/delete")
# bp.add_route(BulkUpdate.as_view(), "/update")     # 测试事务和update接口
bp.add_route(GetLogs.as_view(), "/get_logs")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt

# bp.add_route(SingleUpdate.as_view(), "/SingleUpdate")                    # 获取验证码 /api/v1/login/GetCaptcha/
