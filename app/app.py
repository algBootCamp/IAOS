# -*- coding: utf-8 -*-
__author__ = 'carl'

from flask import Flask

from cache.cache import BasicDataCache
from conf.globalcfg import GlobalCfg
from controller.blueprint import blue

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'ABCDEFG'

# 蓝图  简单理解蓝图：就是将系统的代码模块化（组件化）
app.register_blueprint(blue)


def init():
    # 常用基础数据缓存
    BasicDataCache().refresh()


# start the app
# noinspection SpellCheckingInspection
def start():
    # init
    cfg = GlobalCfg()
    init()
    # start web server
    server_info = cfg.get_server_info()
    app.run(host=server_info['host'], port=int(server_info['port']), debug=True)


if __name__ == '__main__':
    start()
