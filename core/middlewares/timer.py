# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : timer.py
Description:
"""
import time

from sanic import Request, HTTPResponse
from .base import BaseMiddleware
from core.libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


class TimerMiddleware(BaseMiddleware):
    """计时中间件"""

    threshold: float = 1.0

    async def before_request(self, request: Request) -> None:
        request.ctx.start_time = time.time()

    async def before_response(self, request: Request, response: HTTPResponse) -> None:
        diff = time.time() - request.ctx.start_time
        if diff > 1.0:
            logger.warning('%s, response timeout: %.6f' % (request.name, diff))
        # if diff > self.threshold:
        #     logger.warning('%s, response timeout: %.6f' % (request.name, diff))