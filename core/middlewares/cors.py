"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
from .base import BaseMiddleware
from sanic import Request, HTTPResponse


class CorsMiddleware(BaseMiddleware):
    """允许跨域"""

    async def before_request(self, request: Request) -> None:
        pass

    async def before_response(self, request: Request, response: HTTPResponse) -> None:
        # if 'X-Error-Code' not in dict(response.headers):
        #     response.headers['X-Error-Code'] = 0

        response.headers["Access-Control-Allow-Origin"] = "http://localhost:7003"
        response.headers["Access-Control-Allow-Headers"] = "X-Custom-Header,Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # response.headers["Access-Control-Allow-Methods"] = "POST, GET"
