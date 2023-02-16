# -*- coding: utf-8 -*-
__author__ = 'carl'
'''
全局配置 当为单例
'''
from util.configreader import ConfigHelper


# noinspection PyTypeChecker
class GlobalCfg(object):
    instance = None
    server_flag = 'flask.server'
    ts_flag = 'tushare.info'
    dolphin_flag = 'dolphindb.info'
    cfg_path = 'cfg.ini'

    def __init__(self) -> object:
        self.server_info = dict()
        self.ts_info = dict()
        self.dlophin_info = dict()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    # noinspection PyRedundantParentheses
    def get_ts_info(self) -> dict:
        if (0 == len(self.ts_info)):
            self.initcfg()
            self.ts_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.ts_flag)
        return self.ts_info

    # noinspection PyRedundantParentheses
    def get_server_info(self) -> dict:
        if (0 == len(self.server_info)):
            self.initcfg()
            self.server_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.server_flag)
        return self.server_info

    # noinspection PyRedundantParentheses
    def get_dlophin_info(self) -> dict:
        if (0 == len(self.dlophin_info)):
            self.initcfg()
            self.dlophin_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.dolphin_flag)
        return self.dlophin_info

    # noinspection PyRedundantParentheses,SpellCheckingInspection
    def initcfg(self):
        self.cfg_path = __file__
        self.cfg_path = self.cfg_path.split("globalcfg.py", 1)[0] + GlobalCfg.cfg_path

# test
# x = GlobalCfg()
# y = GlobalCfg()
# print(x.get_server_info())
# print(x.get_server_info())
# print(x.get_server_info())
# print(y.get_ts_cfg())
# print(x)
# print(y)
