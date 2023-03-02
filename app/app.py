# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging.config
import os
import sys
from importlib import reload
from cache.cache import BasicDataCache
from conf.globalcfg import GlobalCfg
from flask import Flask, jsonify
from entity.jsonresp import JsonResponse

# 路径加载 [后续用作lib加载，便于部署]
reload(sys)
sys.path.append('./')
sys.path.append('../')
# print env
print('IAOS Server %s on %s' % (sys.version, sys.platform))

# get golbal_cfg
global_cfg = GlobalCfg()

# ----------------------- global log init ----------------------- #
"""
全局日志文件key 列表
其余模块使用：仅需logging.getLogger(key) 即可

app：                主日志，包括flask服务、数据获取、cache、db等
log_quantization：   量化逻辑日志
log_schedtask：      定时任务日志
log_blueprint：      外部功能提供接口日志（controller）
log_analysis：       因子验证评价逻辑日志
log_err：            错误日志
"""
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
logging.config.fileConfig(log_cfg_path)
# ----------------------- global log init ----------------------- #

log = logging.getLogger("app")
log_err = logging.getLogger("log_err")


class IAOSFlask(Flask):

    def make_response(self, rv):
        """
        自定义响应内容 :
        视图函数可以直接返回: DataFrame,str,list、dict、tuple、None
        如果是DataFrame可以先转为dict
        """
        if rv is None or isinstance(rv, (str, list, dict, tuple)):
            rv = JsonResponse.success(rv)
        # 如果是 DataFrame，转为 JsonResponse
        if isinstance(rv, JsonResponse):
            rv = jsonify(rv.to_dict())
        return super().make_response(rv)


def init():
    # TODO
    """常用基础数据缓存"""
    BasicDataCache().refresh()


# start the app
# noinspection SpellCheckingInspection
def start():
    try:
        # init
        init()
        # start web server
        server_info = global_cfg.get_server_info()
        # flask app build
        app = IAOSFlask(__name__)
        # 蓝图  简单理解蓝图：就是将系统的代码模块化（组件化）
        from controller.blueprint import blue
        app.register_blueprint(blue)
        app.config['DEBUG'] = False
        # app.config['SECRET_KEY'] = 'ABCDEFG'
        # 防止中文转换成ASCII编码
        app.config['JSON_AS_ASCII'] = False
        # 跨域的解决方案
        # CORS(app, supports_credentials=True)
        log.info("IAOS Server will Start!")
        app.run(host=server_info['host'], port=int(server_info['port']))
    except Exception as e:
        log_err.error("IAOS Server Failed! ", e)
        raise Exception("IAOS Server Failed! %s" % e)


if __name__ == '__main__':
    start()
