# coding: utf-8
"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""

import time
import types
from datetime import timedelta
from sanic.views import HTTPMethodView
from sanic_ext.extensions.openapi.definitions import Parameter, Response

from core.libs.verify_login_codes import *
from core.libs.error_code import *
from core.libs.response import *
from core.models import *
from functools import wraps
from sanic_ext import openapi
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


class Verify_codes(HTTPMethodView):
    # @openapi.summary("This is a summary")
    @openapi.description("获取图形验证码")
    @openapi.definition(
        parameter=Parameter("", str, "query"),
        response=Response(dict(), 200, "")
    )
    async def get(self, request):
        new_captcha = CaptchaTool()
        img, code = new_captcha.get_verify_code()

        request.ctx.session['code'] = code
        print(request.cookies)

        print(request.ctx.session['code'], request.ctx.session)
        response1 = response_ok(dict(img=img), ECEnum.Success)
        return response1


class Test_verify_captcha(HTTPMethodView):

    async def post(self, request):
        print("body:{}".format(request.json))
        print("param:{}".format(request.args))
        print("host:{}".format(request.host))
        print("version:{}".format(request.version))
        print("name:{}".format(request.name))
        print("ip:{}".format(request.ip))
        print("cookies:{}".format(request.cookies))
        print("server_path:{}".format(request.server_path))
        print("server_port:{}".format(request.server_port))
        print("url:{}".format(request.url))
        print("token:{}".format(request.token))
        print("uri_template:{}".format(request.uri_template))
        obj = {}
        code = obj.get('code', None)

        s_code = request.ctx.session.get("code", None)
        if (not all([code, s_code])) or (code != s_code):
            return response_ok(dict(code=code), ECEnum.VerificationCodeError)

        return response_ok(dict(img=''), ECEnum.Success)


class IndexLogin(HTTPMethodView):

    async def post(self, request):
        obj = request.json

        # 图形验证码
        code = obj.get("code", None)
        cookies = request.cookies
        print(cookies)
        print(request.ctx.session)
        s_code = request.ctx.session.get("code", None)
        print(code, s_code)

        if (not all([code, s_code])) or (code != s_code):
            return response_ok(dict(code=code), ECEnum.VerificationCodeError)

        login_account = obj.get("username")
        passwd = obj.get("password")

        if not login_account or not passwd:
            return response_ok(dict(login_account=login_account, passwd=passwd), ECEnum.InvalidParameter)

        # 根据用户id查找用户
        users = await Users.filter(login_account=login_account)

        if len(users) > 1:
            return response_ok(dict(users=[user.to_dict() for user in users]), ECEnum.AccountOrPassWordErr,
                               msg="存在重复用户id")
        if len(users) < 1:
            return response_ok(dict(login_account=login_account, passwd=passwd), ECEnum.AccountOrPassWordErr)

        user = users[0]
        if passwd != user.password:
            return response_ok(dict(login_account=login_account, passwd=passwd), ECEnum.AccountOrPassWordErr)

        # TODO, 检查时间戳地区
        exp_time_seconds = datetime.timestamp(datetime.now() + timedelta(hours=24))
        # 设置session内容
        request.ctx.session['exp_time'] = exp_time_seconds
        request.ctx.session['login_account'] = login_account
        # request.ctx.session['password'] = passwd
        # data = {
        #     "username": login_account,
        #     "exp_time": exp_time_seconds
        #
        # }

        return response_ok({}, ECEnum.Success, msg="登录成功")


class CheckInfo(HTTPMethodView):
    """
    验证是否登录，或是否过期
    """

    async def get(self, request):
        if 'login_account' not in request.ctx.session:
            return response_ok(dict(), ECEnum.InvalidParameter, msg="用户id丢失")

        login_account = request.ctx.session['login_account']

        if not login_account:
            return response_ok(dict(login_account=login_account), ECEnum.InvalidParameter, msg="用户id错误")

        # 根据用户id查找用户
        users = await Users.filter(login_account=login_account)
        if len(users) > 1:
            return response_ok(dict(users=[user.to_dict() for user in users]), ECEnum.AccountOrPassWordErr,
                               msg="存在重复用户id")
        if len(users) < 1:
            return response_ok(dict(login_account=login_account), ECEnum.AccountOrPassWordErr)

        # 验证session是否过期，未过期则刷新过期时间
        cur_time = datetime.now()
        exp_time = request.ctx.session['exp_time']
        if datetime.timestamp(cur_time) > exp_time:
            return response_ok(dict(exp_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp_time))),
                               ECEnum.SessionExpired)
        else:
            request.ctx.session['exp_time'] = datetime.timestamp(cur_time + timedelta(hours=24))

        exp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.ctx.session['exp_time']))
        return response_ok(dict(login_account=login_account, exp_time=exp_time), ECEnum.Success)

def login_required(wrapped):

    def wapper_auth(func):
        @wraps(func)
        async def check_login(self, request, *args, **kwargs):
            login_account = request.ctx.session['login_account']

            if not login_account:
                return response_ok(dict(login_account=login_account), ECEnum.InvalidParameter)

            # 根据用户id查找用户
            users = await Users.filter(login_account=login_account)
            if len(users) > 1:
                return response_ok(dict(users=[user.to_dict() for user in users]), ECEnum.AccountOrPassWordErr,
                                   msg="存在重复用户id")
            if len(users) < 1:
                return response_ok(dict(login_account=login_account), ECEnum.AccountOrPassWordErr)

            # 验证session是否过期，未过期则刷新过期时间
            cur_time = datetime.now()
            exp_time = request.ctx.session['exp_time']
            if datetime.timestamp(cur_time) > exp_time:
                return response_ok(dict(exp_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp_time))),
                                   ECEnum.SessionExpired)
            else:
                request.ctx.session['exp_time'] = datetime.timestamp(cur_time + timedelta(hours=24))

            return await func(self, request, *args, **kwargs)

        return check_login

    return wapper_auth(wrapped)
