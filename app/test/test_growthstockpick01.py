import pandas as pd

from quantization.securitypick.growth.growthstockpick01 import GrowthStockPick01

def test_gsp01():
    # dropna(axis,how,subset)方法会删除有空值的行或列，
    # axis为0是行，axis为1是列,
    # how为any时该行或列只要有一个空值就会删除，all是全都是空值才删除
    # subset是一个列表，指定某些列
    data = pd.read_csv("./testdata/base_stock_infos.csv", dtype={"roe":float,"basic_eps_yoy":float,"pe_ttm":float})
    gsp01 = GrowthStockPick01(stocksinfos=data)