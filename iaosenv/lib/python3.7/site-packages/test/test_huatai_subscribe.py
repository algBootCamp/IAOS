# coding: utf8

def get_app():
    from tushare import ht_subs
    # return ht_subs('MDIL1TUSHARE01', 'De3y9.j+_9Jk')  # level2
    return ht_subs('MDCTest2434', 'Jn.V+_V7fcySk')  # level1


# 引入tushare-sdk中的华泰客户端
from tushare import ht_subs


def demo():
    # 对应华泰的账号
    # app = ht_subs('account', 'password')
    app = get_app()     # 这里隐藏了账密，实际情况下，用上面方法获取app

    @app.register_subscribe_func(datatypes=['1MIN'], codes=["000001.SZ"])
    def print_subscribe_message(ts_record: dict, ht_record: dict, *args, **kwargs):
        """
        订阅数据类型datatypes，并指定codes列表，
            datatype:  TICK, TRANSACTION, ORDER, 1MIN, 5MIN, 15MIN, 30MIN, 60MIN, 1DAY, 15SECOND
        :param
            ts_record:
                数据类型：字典
                字段说明参考 tushare.subs.model.min 和 tushare.subs.model.tick
            ht_record
                数据类型：字典
                字段说明参考华泰的数据格式
        :return:
        """
        print('展示订阅到的数据内容========================')
        print(f'tushare-data: {ts_record}')
        print(f'huatai-data: {ht_record}')

    # 程序启动后等待， 输入stop后推出
    app.run()


if __name__ == '__main__':
    demo()
