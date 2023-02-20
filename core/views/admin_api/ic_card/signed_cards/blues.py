from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('ic_card_signed', url_prefix='/admin_api/ic_card')

bp.add_route(GetSignedCardInfo.as_view(), "/signed/get_cards")
bp.add_route(SignedIcCard.as_view(), "/signed/signed_card")
