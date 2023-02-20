# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   :2022-11
File   :__init__.py.py
Description:
"""
import json
import os
from sanic import Sanic
from sanic_session import Session, RedisSessionInterface
from settings import TomlConfig
from core.listeners import LISTENER_TUPLE, BaseListener
from core.middlewares import MIDDLEWARE_TUPLE, BaseMiddleware
from core.views.blues import BLUE_TUPLE
from core.libs.logger import logger
from sanic_session import InMemorySessionInterface
# from core.libs.sanic_log import LOGGING_CONFIG_DEFAULTS
from .models import *
from tortoise.contrib.sanic import register_tortoise
from sanic_session import Session


def create_app() -> Sanic:
    """
    服务配置与应用注册
    :return:
    """
    # 项目根路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = os.path.join(os.path.join(BASE_DIR, 'log'), 'server.log')
    toml_file = os.path.join(os.path.join(BASE_DIR, 'settings'), 'config.toml')
    toml_config = TomlConfig(path=toml_file, config_type='development')
    toml_config['BASE_PATH'] = BASE_DIR
    toml_config['STATIC_PATH'] = os.path.join(BASE_DIR, 'static')
    app: Sanic = Sanic(toml_config.APP_NAME)
    # app: Sanic = Sanic(toml_config.APP_NAME, log_config=LOGGING_CONFIG_DEFAULTS)

    # 服务配置初始化
    app.config.update_config(toml_config)
    app.config['CORS_SUPPORTS_CREDENTIALS'] = True

    # 静态资源加载
    app: Sanic = configure_static_resources(app, toml_config)

    logger(log_file, toml_config)

    # 注册监听
    register_listener(app, toml_config)

    # 注册中间件
    register_middleware(app)

    # 创建session

    Session(app, interface=InMemorySessionInterface(httponly=False))

    # 注册蓝图
    app: Sanic = register_blueprint(app)

    # 注册创建数据库引擎

    mysql_host = toml_config['MYSQL']['HOST']
    mysql_db = toml_config['MYSQL']['DB']
    mysql_port = toml_config['MYSQL']['PORT']
    mysql_user = toml_config['MYSQL']['USER']
    mysql_password = toml_config['MYSQL']['PASSWORD']
    # mysql_config = toml_config['MYSQL']['CONFIG']
    register_tortoise(
        app, db_url=f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}",
        modules={"models": ["core.models"]}, generate_schemas=True
    )

    return app


def configure_static_resources(app: Sanic, settings) -> Sanic:
    """
    注册静态文件路径
    :param app:
    :param settings:
    :return:
    """
    app.static('/static', settings.STATIC_PATH)
    return app


def register_blueprint(app: Sanic) -> Sanic:
    """注册蓝图"""
    for blueprint in BLUE_TUPLE:
        app.blueprint(blueprint)
    return app


def register_listener(app: Sanic, settings) -> None:
    """１注册监听"""
    for listener_cls in LISTENER_TUPLE:
        listener: BaseListener = listener_cls(settings)
        for event in ('after_server_start', 'before_server_stop'):
            if hasattr(listener, event):
                app.register_listener(getattr(listener, event), event)


def register_middleware(app: Sanic) -> None:
    """２注册中间件"""
    for middle_cls in MIDDLEWARE_TUPLE:
        middle: BaseMiddleware = middle_cls()
        if hasattr(middle, 'before_request'):
            app.register_middleware(middle.before_request, attach_to='request')
        if hasattr(middle, 'before_response'):
            app.register_middleware(middle.before_response, attach_to='response')
