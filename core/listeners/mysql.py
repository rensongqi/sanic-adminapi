"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from .base import BaseListener
from sanic import Sanic
from asyncio.base_events import BaseEventLoop


class MysqlListener(BaseListener):
    async def after_server_start(self, app: Sanic, loop: BaseEventLoop) -> None:
        pass

    async def before_server_stop(self, app: Sanic, loop: BaseEventLoop) -> None:
        pass