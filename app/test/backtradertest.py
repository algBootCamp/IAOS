# -*- coding: utf-8 -*-
__author__ = 'carl'

import backtrader as bt
import pandas as pd
import warnings
from quotation.captures.tsdata_capturer import TuShareDataCapturer

warnings.filterwarnings("ignore")

# noinspection SpellCheckingInspection
'''
backtrader test
'''


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('exitbars', 5), ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

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

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        '''The strategy next method will be called on each bar of the system clock (self.datas[0]).
         This is true until other things come into play like indicators,
         which need some bars to start producing an output. More on that later.'''
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    df = TuShareDataCapturer().get_pro_bar(ts_code='000001.SZ', freq='D', start_date='20220101', end_date='20220818')
    df = df.loc[:].rename(columns={'vol': 'volume'})
    df.index = pd.to_datetime(df.trade_date)
    # df['openinterest']=0
    # volume 成交量 openinterest 持仓量
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df[::-1]
    # print(df)
    feed = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    # Add the Data Feed to Cerebro
    cerebro.adddata(feed)
    # Add a strategy
    cerebro.addstrategy(TestStrategy)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result 需要保证 matplotlib==3.2.2 不要用matplotlib最新版
    cerebro.plot()
