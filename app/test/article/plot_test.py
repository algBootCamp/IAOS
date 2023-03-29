# -*- coding: utf-8 -*-
__author__ = 'carl'

import matplotlib.gridspec as gridspec  # 调用网格
import matplotlib.pyplot as plt
import numpy as np

"""
to see:https://zhuanlan.zhihu.com/p/139052035
"""


def test1():
    fig = plt.figure(num=1, figsize=(4, 4))
    # 221
    # 里面前两个代表的是画布划分的行数和列数，
    # 公共分为4个子图，最后一个1是代表，现在选中第一个子图
    ax1 = fig.add_subplot(221)  ###可从图中看到，我们的画布是分为2x2的区域
    ax1.plot([1, 2, 3, 4], [1, 2, 3, 4])
    ax2 = fig.add_subplot(222)
    ax2.plot([1, 2, 3, 4], [2, 2, 3, 4])
    ax3 = fig.add_subplot(223)
    ax3.plot([1, 2, 3, 4], [1, 2, 2, 4])
    ax4 = fig.add_subplot(224)
    ax4.plot([1, 2, 3, 4], [1, 2, 3, 3])

    plt.show()


def test2():
    fig = plt.figure(num=1, figsize=(4, 6))  # 创建画布
    gs = gridspec.GridSpec(3, 3)  # 设定网格

    ax1 = fig.add_subplot(gs[0, :])  # 选定网格
    ax1.plot([1, 2, 3, 4], [1, 2, 3, 4])

    ax2 = fig.add_subplot(gs[1, :-1])
    ax2.plot([1, 2, 3, 4], [1, 2, 3, 4])

    ax3 = fig.add_subplot(gs[1:, -1])
    ax3.plot([1, 2, 3, 4], [1, 2, 3, 4])

    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot([1, 2, 3, 4], [1, 2, 3, 4])

    ax5 = fig.add_subplot(gs[2, 1])
    ax5.plot([1, 2, 3, 4], [1, 2, 3, 4])

    plt.show()


def test3():
    app = [78, 80, 79, 81, 91, 95, 96]
    x = np.arange(1, 8)
    fig = plt.figure(num=1, figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.plot(x, app)
    plt.show()


def test4():
    app = [78, 80, 79, 81, 91, 95, 96]
    x = np.arange(1, 8)
    plt.rcParams["font.family"] = "SimHei"
    # plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 用来正常显示中文标签
    fig = plt.figure(num=1, figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.plot(x, app)
    ax.set_xlim([1, 7.1])
    ax.set_ylim([40, 100])
    ax.set_xticks(np.linspace(1, 7, 7))
    ax.set_yticks(np.linspace(50, 100, 6))  # 可调控字体大小，样式，
    ax.set_xticklabels(["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"], fontproperties="SimHei",
                       fontsize=12, rotation=10)
    # 参数rotation=10，可以使得类标旋转值为10的角度
    ax.set_yticklabels(["50kg", "60kg", "70kg", "80kg", "90kg", "100kg"])

    # ax.plot(x, app, label="apple")
    ax.plot(x, app, "r-.d", label="apple")  # 在原来的基础上添加“r-.d”

    ban = [70, 80, 81, 82, 75, 90, 89]
    ax.plot(x, ban, "c-d", label="ban")
    ax.legend(loc=3, labelspacing=2, handlelength=3, fontsize=14, shadow=True)
    plt.show()

def test5():
    pass
