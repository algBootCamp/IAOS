import pandas as pd

from quantization.securitypick.condition.conditionstockpick01 import ConditonStockPick01


def test_get_target_data():
    csp1 = ConditonStockPick01()
    if csp1.base_stock_infos is None:
        # data = pd.read_csv("./testdata/base_stock_infos.csv", dtype={'symbol': str})
        data = pd.read_csv("./testdata/base_stock_infos.csv", dtype=object)
        csp1.base_stock_infos = data
    condtions = {
        'name': "平安银行"
        # 'ps': [5, 10],
        # 'pb': [1, 3],
        # 'pe_ttm': [5, 10]
    }
    csp1.get_target_stock_pool(**condtions)
