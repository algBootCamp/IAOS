# -*- coding: utf-8 -*-
__author__ = 'carl'

from datetime import datetime
import backtrader as bt

from quotation.tsdata_capturer import TuShareDataCapturer

'''
均线策略：当收盘价上涨突破15日均线买入（做多），当收盘价下跌跌穿15日均线卖出（做空）
'''


class MAStrategy(bt.Strategy):
    # 全局参数，可选：更改交易策略中变量/参数的值，可用于参数调优。
    params = (
        ('maperiod', 15),
    )

    # 日志，可选：记录策略的执行日志，可以打印出该函数提供的日期时间和txt变量。
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 用于初始化交易策略
    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show

        # 指数移动平均
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # 加权移动平均
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,subplot=True)
        # 慢速随机指标
        # bt.indicators.StochasticSlow(self.datas[0])
        # 异同移动平均线
        bt.indicators.MACDHisto(self.datas[0])
        # 相对强弱指数
        # rsi = bt.indicators.RSI(self.datas[0])
        # SMA是指简单移动平均线 计算方法为一组数字相加，除以该组数据的组成个数，其中每一给定时限在计算平均值时的权重均相等
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # 均幅指标:是取一定时间周期内的股价波动幅度的移动平均值
        # bt.indicators.ATR(self.datas[0], plot=False)

    # 可选：跟踪交易指令（order）的状态。order具有提交，接受，买入/卖出执行和价格，已取消/拒绝等状态。
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    # 可选：跟踪交易的状态，任何已平仓的交易都将报告毛利和净利润。
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS【毛利】： %.2f, NET【净利】： %.2f \n' %
                 (trade.pnl, trade.pnlcomm))

    # 必选：制定交易策略的函数，策略模块最核心的部分。
    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('收盘价：%.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market  检查是否持仓
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                # self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(size=500)

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=500)
