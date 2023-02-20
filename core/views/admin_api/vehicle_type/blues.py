"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('vehicle_type', url_prefix='/admin_api/vehicle_type')

bp.add_route(GetVehicleTypes.as_view(), "/get_vehicle_type")  #
bp.add_route(InsertVehicleTypes.as_view(), "/insert_vehicle_type")  #
bp.add_route(UpdateVehicleTypes.as_view(), "/update_vehicle_type")  #
