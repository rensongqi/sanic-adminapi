"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('driver_management', url_prefix='/admin_api/region')

bp.add_route(GetDrivers.as_view(), "/get_all_drivers")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
bp.add_route(InsertDriver.as_view(), "/insert_driver")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
bp.add_route(UpdateDriver.as_view(), "/update_driver")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
# bp.add_route(GetDept.as_view(), "/get_depts")  #
