# -*- coding: utf-8 -*-
__author__ = 'carl'

import configparser

'''global config util'''


class ConfigHelper(object):

    # get your need config info
    @staticmethod
    def get_cfg_info(cfg_path, cfg_flag) -> object:
        config = configparser.ConfigParser()
        config.read(cfg_path)
        info = dict()
        if cfg_flag in config:
            for key in config[cfg_flag]:
                info[key] = config[cfg_flag][key].strip()
        return info
