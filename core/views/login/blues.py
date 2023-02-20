"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""

from sanic import Blueprint

from .views import *

bp: Blueprint = Blueprint('login', url_prefix='/login')

bp.add_route(IndexLogin.as_view(), "/")  # 登陆验证　
bp.add_route(Verify_codes.as_view(), "/get_captcha")  # 获取验证码
bp.add_route(Test_verify_captcha.as_view(), "/verify_captcha")  # 核查验证码
bp.add_route(CheckInfo.as_view(), "/info")  # 检验是否登录，或会话是否过期
