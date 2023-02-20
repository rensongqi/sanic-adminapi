"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from sanic import Blueprint

from .garbage_source_views import *
from .garbage_type_views import *

bp: Blueprint = Blueprint('garbage', url_prefix='/admin_api/garbage')

bp.add_route(GetGarbageType.as_view(), "/get_garbage_type")  #
bp.add_route(InsertGarbageType.as_view(), "/insert_garbage_type")  #
bp.add_route(UpdateGarbageType.as_view(), "/update_garbage_type")  #
bp.add_route(GetGarbageSource.as_view(), "/get_garbage_source")  #
bp.add_route(InsertGarbageSource.as_view(), "/insert_garbage_source")  #
bp.add_route(UpdateGarbageSource.as_view(), "/update_garbage_source")  #
