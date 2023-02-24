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
    db_flag = 'db.info'
    redis_flag = 'redis.info'
    log_files_flag = 'log.files'
    cfg_path = 'cfg.ini'

    def __init__(self) -> object:
        # flask配置信息
        self.__server_info = dict()
        # tushare配置信息
        self.__ts_info = dict()
        self.__dlophin_info = dict()
        # 数据库连接池配置信息
        self.__db_info = dict()
        # redis配置信息
        self.__redis_info = dict()
        # 日志配置信息
        self.__log_files = dict()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    # noinspection PyRedundantParentheses
    def get_ts_info(self) -> dict:
        if (0 == len(self.__ts_info)):
            self.initcfg()
            self.__ts_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.ts_flag)
        return self.__ts_info

    # noinspection PyRedundantParentheses
    def get_server_info(self) -> dict:
        if (0 == len(self.__server_info)):
            self.initcfg()
            self.__server_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.server_flag)
        return self.__server_info

    # noinspection PyRedundantParentheses
    def get_dlophin_info(self) -> dict:
        if (0 == len(self.__dlophin_info)):
            self.initcfg()
            self.__dlophin_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.dolphin_flag)
        return self.__dlophin_info

    # noinspection PyRedundantParentheses
    def get_db_info(self) -> dict:
        if (0 == len(self.__db_info)):
            self.initcfg()
            self.__db_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.db_flag)
        return self.__db_info

    # noinspection PyRedundantParentheses
    def get_redis_info(self) -> dict:
        if (0 == len(self.__redis_info)):
            self.initcfg()
            self.__redis_info = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.redis_flag)
        return self.__redis_info

    # noinspection PyRedundantParentheses
    def get_log_files(self) -> dict:
        if (0 == len(self.__log_files)):
            self.initcfg()
            self.__log_files = ConfigHelper.get_cfg_info(self.cfg_path, GlobalCfg.log_files_flag)
        return self.__log_files

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
