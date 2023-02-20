# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : __init__.py.py
Description:
  - pip install toml
"""
from typing import Dict,Any

import toml
from sanic import Sanic, text
from sanic.config import Config


class TomlConfig(Config):
    def __init__(self, *args, path: str, config_type: str, **kwargs):
        super().__init__(*args, **kwargs)
        with open(path, "r") as f:
            try:
                config = toml.load(f)
                print('加载配置文件:', config)
                print('读取配置:', config_type)
                self.apply(config[config_type])
            except Exception as err:
                print("配置文件读取错误：{0}".format(path))
                print(err)

    def apply(self, config):
        self.update(self._to_uppercase(config))

    def _to_uppercase(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        retval: Dict[str, Any] = {}
        if isinstance(obj, str):
            return obj
        for key, value in obj.items():
            upper_key = key.upper()
            # print(isinstance(value, list))
            if isinstance(value, list):
                retval[upper_key] = [
                    self._to_uppercase(item) for item in value
                ]
            elif isinstance(value, dict):
                retval[upper_key] = self._to_uppercase(value)
            else:
                retval[upper_key] = value
        return retval


# toml_config = TomlConfig(path="config.toml",config_type='development')
# app = Sanic(toml_config.APP_NAME, config=toml_config)