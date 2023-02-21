# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging
import logging.config
import os
import sys
from importlib import reload
from cache.cache import BasicDataCache
from conf.globalcfg import GlobalCfg
from controller.blueprint import blue
from flask import Flask, jsonify
from controller.entity.jsonresp import JsonResponse

# 路径加载
reload(sys)
sys.path.append('./')
sys.path.append('../')
# print env
print('IAOS Server %s on %s' % (sys.version, sys.platform))

# get golbal_cfg
global_cfg = GlobalCfg()

# ----  log init ------ #
log_files = global_cfg.get_log_files()
# 确保log file path存在 python logging不提供创建日志文件路径
for file_list in log_files.values():
    log_filenames = file_list.split(',')
    for log_filename in log_filenames:
        # print(log_filename)
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
LOG_CFG = "conf/logging.cfg"
self_path = __file__
log_cfg_path = self_path.split("app.py", 1)[0] + LOG_CFG
logging.config.fileConfig(LOG_CFG)
# app,log_quantization,log_schedtask,log_blueprint,log_analysis
log = logging.getLogger("app")


# ----  log init ------ #


class IAOSFlask(Flask):

    def make_response(self, rv):
        """自定义响应内容 :
        视图函数可以直接返回: DataFrame,str,list、dict、tuple、None
        如果是DataFrame可以先转为dict"""
        if rv is None or isinstance(rv, (str, list, dict, tuple)):
            rv = JsonResponse.success(rv)
        # 如果是 DataFrame，转为 JsonResponse
        if isinstance(rv, JsonResponse):
            rv = jsonify(rv.to_dict())
        return super().make_response(rv)


def init():
    # 常用基础数据缓存 TODO
    BasicDataCache().refresh()
    log.debug("常用基础数据缓存完成。")


# start the app
# noinspection SpellCheckingInspection
def start():
    # init
    init()

    # start web server
    server_info = global_cfg.get_server_info()
    # flask app build
    app = IAOSFlask(__name__)
    # 蓝图  简单理解蓝图：就是将系统的代码模块化（组件化）
    app.register_blueprint(blue)
    app.config['DEBUG'] = False
    # app.config['SECRET_KEY'] = 'ABCDEFG'
    # 防止中文转换成ASCII编码
    app.config['JSON_AS_ASCII'] = False
    # 跨域的解决方案
    # CORS(app, supports_credentials=True)
    app.run(host=server_info['host'], port=int(server_info['port']))
    log.debug("IAOS Server Start!")


if __name__ == '__main__':
    start()
