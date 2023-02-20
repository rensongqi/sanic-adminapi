from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('ic_card_change', url_prefix='/admin_api/ic_card')

bp.add_route(GetChangeInfo.as_view(), "/get_change_info")       # 查询IC卡换卡信息
bp.add_route(ChangeCard.as_view(), "/change_card")              # IC卡换卡
