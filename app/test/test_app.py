from unittest import TestCase
import time


class Test(TestCase):
    def test_init(self):
        # xx=['000488.SZ', '600470.SH', '000501.SZ', '000410.SZ', '600262.SH', '600422.SH', '002044.SZ', '000715.SZ', '600021.SH', '600207.SH', '600419.SH', '000637.SZ', '000868.SZ', '002135.SZ', '002015.SZ', '600100.SH', '600010.SH', '000679.SZ', '600652.SH', '000629.SZ', '000976.SZ', '000756.SZ', '002105.SZ', '600480.SH', '600710.SH', '000985.SZ', '600075.SH', '600778.SH', '002126.SZ', '000421.SZ', '000569.SZ', '000554.SZ', '600814.SH', '002014.SZ', '000049.SZ', '000510.SZ', '600493.SH', '600395.SH', '000550.SZ', '600056.SH', '600211.SH', '000531.SZ', '600522.SH', '600483.SH', '600688.SH', '600071.SH', '600029.SH', '002170.SZ', '600070.SH', '000977.SZ', '600863.SH', '600295.SH', '000912.SZ', '600858.SH', '000909.SZ', '000564.SZ', '600157.SH', '000062.SZ', '600389.SH', '000713.SZ', '000533.SZ', '000926.SZ', '600793.SH', '002084.SZ', '000833.SZ', '600805.SH', '600966.SH', '600511.SH', '600115.SH', '000816.SZ', '600741.SH', '600826.SH', '600390.SH', '600348.SH', '000419.SZ', '000920.SZ', '000676.SZ', '600769.SH', '002068.SZ', '000635.SZ', '600495.SH', '600859.SH', '600871.SH', '600128.SH', '600607.SH', '002160.SZ', '002163.SZ', '600726.SH', '600573.SH', '600679.SH', '600609.SH', '000522.SZ', '600351.SH', '600882.SH', '600857.SH', '000819.SZ', '600560.SH', '000661.SZ', '600179.SH', '000806.SZ']
        # symbol = ","
        # t=symbol.join(xx)
        # print(t)
        import pandas as pd

        data1 = [[10], [12], [13]]

        df1 = pd.DataFrame(data1, columns=['close'], dtype=float)

        print(df1)
        data2 = [[11], [12], [11]]

        df2 = pd.DataFrame(data2, columns=['close'], dtype=float)

        print(df2)

        data3 = [[100], [1200], [1100]]
        df3 = pd.DataFrame(data3, columns=['cmv'], dtype=float)
        x1 = df2['close'] / df1['close'] - 1
        x2 = df3['cmv']
        x3 = x1 * x2
        xx = x3.sum() / x2.sum()
        # weighted_m_return = ((close2['close'].ix[0, :] / close1['close'].ix[0, :] - 1) * CMV).sum() / (
        #     CMV.ix[port].sum())
        now_time = time.localtime(time.time())
        this_year = now_time.tm_year
        this_month =now_time.tm_mon
        print("---------------")
        d={"port1":[0.2,0.3,-0.2,2.3],"port2":[0.1,0.4,-0.1,2.3]}
        monthly_return=pd.DataFrame(d)
        total_return=(monthly_return + 1).cumprod().iloc[-1,:]-1
        annual_return = (total_return + 1) ** (1. / 6) - 1
        # xxxx=(d + 1).T.cumprod().iloc[-1, :] - 1