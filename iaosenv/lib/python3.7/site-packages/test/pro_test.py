# -*- coding:utf-8 -*- 
'''
Created on 2018年7月29日
@author: JM
'''

from tushare.pro.data_pro import pro_api

if __name__ == '__main__':
    pro = pro_api('')
    print(pro.daily(ts_code='', trade_date='20180724'))