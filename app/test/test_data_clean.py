import time

from quotation.cleaning.data_clean import BaseDataClean
import pandas as pd

def test_init_base_stock_infos():
    # bdc=BaseDataClean()
    BaseDataClean.init_base_stock_infos()


def test_init_tscode_set():
    col = ['name', 'outstanding', 'pe', 'pb', 'esp',
           'reservedPerShare', 'rev', 'profit', 'gpr', 'npr']
    newcol = ['简称', '流通股', '市盈率', '市净率', '每股收益', '每股公积',
              '收入同比', '利润同比', '毛利率', '净利率']
    d = dict(zip(col, newcol))
    print(d)


def test_init_stocks_pool():
    assert False


def test_init_smb_industry_map():
    assert False


def test_get_data_percentile():
    assert False


def test_get_pretrade_date():
    BaseDataClean.get_pretrade_date()
