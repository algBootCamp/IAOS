# -*- coding: utf-8 -*-
__author__ = 'carl'

from cache.cache import BasicDataCache
from conf.globalcfg import GlobalCfg
from controller.blueprint import blue
from flask import Flask, jsonify
from controller.entity.jsonresp import JsonResponse


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


# start the app
# noinspection SpellCheckingInspection
def start():
    # get config
    cfg = GlobalCfg()
    # init
    init()

    # start web server
    server_info = cfg.get_server_info()
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


if __name__ == '__main__':
    start()
