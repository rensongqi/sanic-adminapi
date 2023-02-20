from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('ic_card_create', url_prefix='/admin_api/ic_card')

bp.add_route(GetIcCard.as_view(), "/create/get_ic_card")
bp.add_route(UpdateIcCard.as_view(), "/create/update_ic_card")
bp.add_route(DeleteIcCard.as_view(), "/create/delete_ic_card")
bp.add_route(CreateIcCard.as_view(), "/create/create_ic_card")
