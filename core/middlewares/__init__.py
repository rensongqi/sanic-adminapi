# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : __init__.py.py
Description:
"""
from __future__ import annotations
from typing import Tuple,Type
from .base import BaseMiddleware
from .timer import TimerMiddleware
from .cors import CorsMiddleware

MIDDLEWARE_TUPLE: Tuple[Type[BaseMiddleware], ...] = (
    TimerMiddleware,
    CorsMiddleware,
)