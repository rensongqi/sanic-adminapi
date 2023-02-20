# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : logger.py
Description:
"""
from __future__ import annotations
import logging
import os.path
from typing import Optional,Dict


def logging_type(types: Optional[str] = None):
    if types.lower() == 'critical':
        return logging.CRITICAL
    elif types.lower() == 'error':
        return logging.ERROR
    elif types.lower() == 'info':
        return logging.INFO
    elif types.lower() == 'debug':
        return logging.DEBUG
    elif types.lower() == 'notset':
        return logging.NOTSET
    else:
        return 0


def logger(file_log, settings: Dict = dict):
    '''
    打日志:
    param file_log: 日志文件名，类型string；
    '''
    log_formatter = "%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]-%(levelname)s-[日志信息]: %(message)s"
    log_init_msg = []

    if isinstance(settings,dict):
        log_level = ['logger_level','file_level','terminal_level']
        if 'log_formatter' not in settings:
            log_init_msg.append("配置文件未定义日志格式【{0}】，默认值:{1}".format('log_formatter'.upper(),log_formatter))
        else:
            log_formatter = settings['log_formatter']

        for level_t in log_level:
            if level_t not in settings:
                log_init_msg.append("配置文件未定义日志级别【{0}】，默认值:DEBUG".format(level_t.upper()))
                settings[level_t] = 'debug'
    else:
        log_init_msg.append('配置文件未定义日志，默认日志级别：【debug】')
        settings = {
            'logger_level': 'debug',
            'file_level': 'debug',
            'terminal_level': 'debug'
        }

    logger_level = logging_type(settings['logger_level'])
    file_level = logging_type(settings['file_level'])
    terminal_level = logging_type(settings['terminal_level'])

    # 创建一个loggger，并设置日志级别
    logger = logging.getLogger()
    logger.setLevel(logger_level)

    # 创建一个handler，用于写入日志文件，并设置日志级别，mode:a是追加写模式，w是覆盖写模式
    fh = logging.FileHandler(filename=file_log, encoding='utf-8', mode='a')
    fh.setLevel(file_level)

    # 创建一个handler，用于将日志输出到控制台，并设置日志级别
    ch = logging.StreamHandler()
    ch.setLevel(terminal_level)

    # 定义handler的输出格式
    formatter = logging.Formatter(log_formatter)
    # fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # 给logger添加handler, 是否打开日志写入文件
    # logger.addHandler(fh)
    logger.addHandler(ch)

    for log_msg in log_init_msg:
        logger.info(log_msg)

    return logger


# from pathlib import PurePath
#
#
# Cur_Dir: PurePath = PurePath(os.path.abspath(os.path.dirname(__file__)))
# print(Cur_Dir)
# ROOT_DIR = Cur_Dir.parent.parent
# print(ROOT_DIR)
# log_file = os.path.join(os.path.join(ROOT_DIR, 'log'), 'server.log')
# toml_file = os.path.join(os.path.join(ROOT_DIR, 'settings'), 'config.toml')
# logan = logger(log_file, {})


from typing import Optional, Any


class LoggerProxy:
    """logger代理"""

    __slots__ = ('_name', '_logger')

    def __init__(self, name: Optional[str] = None) -> None:
        self._name: Optional[str] = name
        self._logger: Optional['logging.Logger'] = None

    def _ensure_logger(self) -> None:
        """确保logger初始化"""
        if self._logger is None:
            self._logger = logging.getLogger(self._name)

    def __getattr__(self, item) -> Any:
        self._ensure_logger()
        return getattr(self._logger, item)





