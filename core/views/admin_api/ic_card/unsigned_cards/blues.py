from sanic import Blueprint
from .views import *


bp: Blueprint = Blueprint('ic_card_unsigned', url_prefix='/admin_api/ic_card')

# bp.add_route(GetIcCard.as_view(), "/unsigned/get_cards")
# bp.add_route(SignedIcCard.as_view(), "/unsigned/signed_card")
