"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('weight_record', url_prefix='/admin_api/weight_record')

bp.add_route(GetDropItems.as_view(), "/get_drop_items")
bp.add_route(GetFullWeightRecord.as_view(), "/read_full_weight_record")
bp.add_route(GetWeightRecord.as_view(), "/read_weight_record")
bp.add_route(InsertWeightRecord.as_view(), "/insert_weight_record")
# bp.add_route(UpdateWeightRecord.as_view(), "/update_weight_record")
# bp.add_route(DeleteWeightRecord.as_view(), "/delete_weight_record")
bp.add_route(ClassifyWeightRecord.as_view(), "/classify_weight_record")
# bp.add_route(WeightRecordGroupByValues.as_view(), "/weight_record_groupby_garbage")
# bp.add_route(WeightOperation.as_view(), "/weight_operation")

# {
#   "vehicle_type": "",
#   "trans_dept": "",
#   "garbage_type": "",
#   "garbage_source": "",
#   "garbage_source__region__region_name": "方岩镇",
#   "year": "2021",
#   "month": "",
#   "date": "",
#   "start_hour": "",
#   "end_hour": ""
# }
