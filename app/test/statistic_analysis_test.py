# -*- coding: utf-8 -*-
__author__ = 'carl'

# https://mp.weixin.qq.com/s/7b_uPuWLpkF52lrYQiumvQ
# https://mp.weixin.qq.com/s/f0uQ4JxWyCmYXBKA-hQktQ
import pandas as pd
from pandas import DataFrame

from quotation.tsdata_capturer import TuShareDataCapturer
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns  # 画图用的
from matplotlib import font_manager

# 正常显示画图时出现的中文
# from pylab import mpl
import warnings

warnings.filterwarnings('ignore')
'''
Python 获取股票数据，并进行简单的统计分析和可视化 test
'''
# 正常显示画图时出现的中文
# for font in font_manager.fontManager.ttflist:
#     # 查看字体名以及对应的字体文件名
#     print(font.name, '-', font.fname)
# print(matplotlib.get_cachedir())

# mpl.rcParams['font.sans-serif'] = ['SimHei']
# # 画图时显示负号
# mpl.rcParams['axes.unicode_minus'] = False


tscapture = TuShareDataCapturer()
df = tscapture.get_index_daily(ts_code='000001.SH', start_date='19901219')
# print(len(df))
print(df.head(5))

# 将数据列表中的第0列'date'设置为索引
df.index = pd.to_datetime(df.trade_date)
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签     使用微软雅黑字体
plt.rcParams['figure.figsize'] = (20.0, 18.0)  # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'
plt.grid()


# 画出上证指数收盘价的走势
def close_analy():
    # 画出上证指数收盘价的走势
    # df['close'].plot(figsize=(20, 10))

    plt.plot(df.close)
    plt.title('上证指数1990-2022年走势图')
    plt.xlabel('日期')
    plt.ylabel('指数')
    plt.show()


# -----------------------------------------
# 描述性统计
def des_analy():
    # pandas的describe()函数提供了数据的描述性统计
    # count:数据样本，mean:均值，std:标准差
    ds = df.describe().round(2)
    print(ds)


# -----------------------------------------
# 成交量
def volume_analy():
    df.loc["2007-01-01":]["vol"].plot(figsize=(12, 6))
    plt.title('上证指数2007-2022年日成交量图')
    plt.xlabel('日期')
    plt.show()


# -----------------------------------------
# 均线分析
def ma_analy():
    # 这里的平均线是通过自定义函数，手动设置20,52,252日均线
    # 移动平均线：
    ma_day = [20, 52, 252]
    for ma in ma_day:
        column_name = "%s日均线" % (str(ma))
        df[column_name] = df["close"].rolling(ma).mean()
    # df.tail(3)
    # 画出2010年以来收盘价和均线图
    df.loc['2010-10-8':][["close", "20日均线", "52日均线", "252日均线"]].plot(figsize=(12, 6))
    plt.title('2010-2022上证指数走势图')
    plt.xlabel('日期')
    plt.show()



# ma_analy()
# volume_analy()
