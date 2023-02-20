# IC卡年检
from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('ic_card_check', url_prefix='/admin_api/ic_card')

bp.add_route(AnnualCheckCard.as_view(), "/check_card")
