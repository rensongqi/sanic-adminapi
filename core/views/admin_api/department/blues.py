"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('department', url_prefix='/admin_api/department')

bp.add_route(GetAllDept.as_view(), "/get_all_depts")
bp.add_route(InsertDepartment.as_view(), "/insert_dept")
bp.add_route(UpdateDepartment.as_view(), "/update_dept")
# bp.add_route(GetAllDept.as_view(), "/get_all_depts")
# bp.add_route(GetAllDept.as_view(), "/get_all_depts")
