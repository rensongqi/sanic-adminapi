from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('pound', url_prefix='/admin_api/pound')

bp.add_route(GetPounds.as_view(), "/get")
bp.add_route(CreatePounds.as_view(), "/create")
bp.add_route(UpdatePounds.as_view(), "/update")
bp.add_route(DeletePounds.as_view(), "/delete")
