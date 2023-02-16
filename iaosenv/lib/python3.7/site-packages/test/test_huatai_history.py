# coding: utf8

def get_app():
    from tushare import ht_subs
    return ht_subs('MDIL1TUSHARE01', 'De3y9.j+_9Jk')  # level1
    # return ht_subs('MDCTest2434', 'Jn.V+_V7fcySk')  # level2


# 引入tushare-sdk中的华泰客户端
from tushare import ht_subs


def demo():
    # 对应华泰的账号
    app = ht_subs('account', 'password')

    @app.register_playback_func(datatype='1MIN', codes=["000001.SZ"])
    def print_subscribe_message(ts_record: dict, ht_record: dict, *args, **kwargs):
        pass

    @app.register_playback_func(datatype='TICK', codes=["000001.SZ"])
    def print_subscribe_message(ts_record: dict, ht_record: dict, *args, **kwargs):
        pass


    # 程序启动后等待， 输入stop后推出
    app.run()


if __name__ == '__main__':
    demo()
