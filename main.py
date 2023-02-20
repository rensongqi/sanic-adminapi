# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : main1.py
Description:
"""
from sanic import Sanic
from core import create_app
# from sanic.response import text

app: Sanic = create_app()

if __name__ == "__main__":
    """
    test running: python3.8 true
    test running: python3.10 false
    socketio 可拆分单独启动
    - auto_reload: 修改代码后，自动重载
    - workers：启动进程数量，默认１
    - debug：调试启用
    - access_log：记录日志启用
    - fast: True 自动以系统最大的核心数量来创建工作线程
    """
    app.run(host="0.0.0.0", port=8012, workers=1, auto_reload=True, debug=False, access_log=False)