import time

from quotation.cleaning.data_clean import BaseDataClean


def test_init_base_stock_infos():
    # bdc=BaseDataClean()
    BaseDataClean.init_base_stock_infos()


def test_init_tscode_set():
    assert False


def test_init_stocks_pool():
    assert False


def test_init_smb_industry_map():
    assert False


def test_get_data_percentile():
    assert False

def test_get_pretrade_date():
    BaseDataClean.get_pretrade_date()