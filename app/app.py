# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging.config
import os
import sys
import threading
from importlib import reload

from flask import Flask, jsonify

from conf.globalcfg import GlobalCfg
from entity.jsonresp import JsonResponse
# 路径加载 [后续用作lib加载，便于部署]
from scheduledtask.iaos_scheduler import IAOSTask

reload(sys)
sys.path.append('./')
sys.path.append('../')
# print env
print('IAOS Server %s on %s' % (sys.version, sys.platform))

# get golbal_cfg
global_cfg = GlobalCfg()


# noinspection PyMethodMayBeStatic
class IAOSFlask(Flask):

    def __init__(self, *args, **kwargs):
        super(IAOSFlask, self).__init__(*args, **kwargs)
        self._iaos_cfg()
        self._iaos_init_log()
        self._iaos_init()

    def _iaos_cfg(self):
        self.config['DEBUG'] = False
        self.config['SECRET_KEY'] = 'ABCDEFG'
        # 防止中文转换成ASCII编码
        self.config['JSON_AS_ASCII'] = False
        # 跨域的解决方案
        # CORS(app, supports_credentials=True)

    def _iaos_init_log(self):
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
        log_cfg = "conf/logging.cfg"
        self_path = __file__
        log_cfg_path = self_path.split("app.py", 1)[0] + log_cfg
        logging.config.fileConfig(log_cfg_path)
        # ----------------------- global log init ----------------------- #
        self.log = logging.getLogger("app")
        self.log_err = logging.getLogger("log_err")

    def _iaos_init(self):
        def init():
            # TODO
            """常用基础数据缓存"""
            from quotation.cache.cache import RemoteBasicDataCache, LocalBasicDataCache
            RemoteBasicDataCache.refresh()
            # 保证RemoteBasicDataCache.refresh执行结束，再进行LocalBasicDataCache.refresh
            LocalBasicDataCache.refresh()

        t1 = threading.Thread(target=init)
        t1.start()

        # 蓝图  简单理解蓝图：就是将系统的代码模块化（组件化）
        from web.controller.blueprint import iaos_blue
        self.register_blueprint(iaos_blue)
        """定时任务开始"""
        IAOSTask(app=self).start_task()
        self.log.info("IAOS Server will Start!")

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


# flask app build
# __name__是当前 Python 模块的名称,应用知道在哪里设置路径。
# instance_relative_config=True相当与告诉应用配置文件相当与实例文件夹(instance folder)的相对地址,实例文件夹放置本地的配置文件
# instance_path实例化目录所在地址
app = IAOSFlask(__name__, instance_relative_config=True, instance_path=os.getcwd())


# start the app 仅仅使用 python 启动时
# noinspection SpellCheckingInspection
# @app.cli.command("start-iaos")
# @click.argument("env")
def start():
    try:
        # start web web
        server_info = global_cfg.get_server_info()
        app.run(host=server_info['host'], port=int(server_info['port']))
    except Exception as e:
        app.log_err.error("IAOS Server Failed! {}".format(e))
        raise Exception("IAOS Server Failed! %s" % e)


if __name__ == '__main__':
    start()
