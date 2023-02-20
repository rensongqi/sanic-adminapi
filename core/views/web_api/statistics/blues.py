"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint
from .views import *

bp: Blueprint = Blueprint('statistics', url_prefix='/web_api/statistics')

bp.add_route(GetTransQueryDropItems.as_view(), "/get_trans_query_drop_items")  #
bp.add_route(GetTransInfo.as_view(), "/get_trans_info")  #
bp.add_route(GetWeightInfo.as_view(), "/get_region_weight_info")  #
bp.add_route(GetGarbageSourceTransInfo.as_view(), "/get_garbage_source_trans_info")  #
bp.add_route(GetPoundGarbageInfo.as_view(), "/get_pound_garbage_info")  #
bp.add_route(GetTransGroupByDateInfo.as_view(), "/get_trans_group_by_date_info")  #
# bp.add_route(GetDept.as_view(), "/get_department")  #
# bp.add_route(GetDeptSTA.as_view(), "/get_department_sta")  #
