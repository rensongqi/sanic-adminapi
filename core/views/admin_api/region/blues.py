"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('region', url_prefix='/admin_api/region')

bp.add_route(GetAllRegion.as_view(), "/get_all_regions")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
bp.add_route(InsertRegion.as_view(), "/insert_region")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
bp.add_route(UpdateRegion.as_view(), "/delete_region")  # 登陆验证　/login/?auth=jwt# 登陆验证　/login/?auth=jwt
