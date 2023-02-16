# -*- coding: utf-8 -*-
__author__ = 'carl'

import dolphindb as ddb
from conf.globalcfg import GlobalCfg

cfg = GlobalCfg()
dolphin_info = cfg.get_dlophin_info()

s = ddb.session()
# print(dolphin_info)
s.connect(dolphin_info['host'], int(dolphin_info['port1']), dolphin_info['userid'], dolphin_info['password'])
