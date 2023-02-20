"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint
from .views import *

bp: Blueprint = Blueprint('vehicle', url_prefix='/admin_api/vehicle')

bp.add_route(GetQueryDropItems.as_view(), "/get_query_drop_items")  #
bp.add_route(GetInsertDropItems.as_view(), "/get_insert_drop_items")  #
bp.add_route(GetScrappedVehicles.as_view(), "/get_scrapped_vehicles")  #
bp.add_route(GetVehicles.as_view(), "/get_vehicles")  #
bp.add_route(GetVehicleInfo.as_view(), "/get_vehicle_info")  #
bp.add_route(InsertVehicle.as_view(), "/insert_vehicle")  #
bp.add_route(UpdateVehicle.as_view(), "/update_vehicle")  #
# bp.add_route(GetDept.as_view(), "/get_department")  #
# bp.add_route(GetDeptSTA.as_view(), "/get_department_sta")  #
