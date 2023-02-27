import time

from quotation.cleaning.data_clean import BaseDataClean
import pandas as pd

def test_init_base_stock_infos():
    # bdc=BaseDataClean()
    BaseDataClean.init_base_stock_infos()
    # left = pd.DataFrame({'sno': [11, 12, 13, 14],
    #                      'name': ['name_a', 'name_b', 'name_c', 'name_d']
    #                      })
    # right = pd.DataFrame({'sno': [11, 12, 13, 14,15],
    #                       'age': ['21', '22', '23', '24','22']
    #                       })
    # df = pd.merge(left, right, on='sno')
    # print("******************left*******************")
    # print(left)
    # print("******************right*******************")
    # print(right)
    # print("******************df*******************")
    # print(df)

    # trade_date
    # d = {'code': {0: '873527'}, 'name': {0: '夜光明'}, 'changepercent': {0: -0.481}, 'trade': {0: 8.28}, 'open': {0: 8.6},
    #      'high': {0: 8.6}, 'low': {0: 8.24}, 'settlement': {0: 8.32}, 'volume': {0: 60733},
    #      'turnoverratio': {0: 0.25921}, 'amount': {0: 504705}, 'per': {0: 11.662}, 'pb': {0: 2.038},
    #      'mktcap': {0: 49715.3556}, 'nmc': {0: 19399.75848}}
    # print(d.keys())
    # ['code', 'name', 'changepercent', 'trade', 'open', 'high', 'low', 'settlement', 'volume', 'turnoverratio','amount', 'per', 'pb', 'mktcap', 'nmc']
    # f_index = {'ts_code': {0: '002315.SZ'}, 'ann_date': {0: '20230228'}, 'end_date': {0: '20221231'}, 'eps': {0: 0.98},
    #            'dt_eps': {0: 0.98}, 'total_revenue_ps': {0: 4.7446}, 'revenue_ps': {0: 4.7071},
    #            'capital_rese_ps': {0: 3.6813}, 'surplus_rese_ps': {0: 0.5}, 'undist_profit_ps': {0: 1.8577},
    #            'extra_item': {0: 21419985.19}, 'profit_dedt': {0: 278979020.85}, 'gross_margin': {0: 1173881502.89},
    #            'current_ratio': {0: 2.0432}, 'quick_ratio': {0: 2.0318}, 'cash_ratio': {0: 1.9193},
    #            'ar_turn': {0: 46.4208}, 'ca_turn': {0: 0.6743}, 'fa_turn': {0: 3.0625}, 'assets_turn': {0: 0.4238},
    #            'op_income': {0: 304590195.53}, 'ebit': {0: 297558792.99}, 'ebitda': {0: 378867314.06},
    #            'fcff': {0: 292754040.89}, 'fcfe': {0: 292754040.89}, 'current_exint': {0: 1093963388.23},
    #            'noncurrent_exint': {0: 155488507.84}, 'interestdebt': {0: 41153579.88}, 'netdebt': {0: -1909282504.57},
    #            'tangible_asset': {0: 2140803231.48}, 'working_capital': {0: 1161983049.86},
    #            'networking_capital': {0: -768576978.6}, 'invest_capital': {0: 2308078710.47},
    #            'retained_earnings': {0: 732909859.0}, 'diluted2_eps': {0: 0.9664}, 'bps': {0: 7.2348},
    #            'ocfps': {0: 1.56}, 'retainedps': {0: 2.3577}, 'cfps': {0: 2.1617}, 'ebit_ps': {0: 0.9572},
    #            'fcff_ps': {0: 0.9418}, 'fcfe_ps': {0: 0.9418}, 'netprofit_margin': {0: 20.515},
    #            'grossprofit_margin': {0: 80.226}, 'cogs_of_sales': {0: 19.774}, 'expense_of_sales': {0: 58.7972},
    #            'profit_to_gr': {0: 20.3531}, 'saleexp_to_gr': {0: 37.7394}, 'adminexp_of_gr': {0: 22.677},
    #            'finaexp_of_gr': {0: -2.0831}, 'impai_ttm': {0: -0.1537}, 'gc_of_gr': {0: 79.3478},
    #            'op_of_gr': {0: 22.4122}, 'ebit_of_gr': {0: 20.1755}, 'roe': {0: 13.8333}, 'roe_waa': {0: None},
    #            'roe_dt': {0: 12.8469}, 'roa': {0: 8.5495}, 'npta': {0: 8.6248}, 'roic': {0: 12.1508},
    #            'roe_yearly': {0: 13.8333}, 'roa2_yearly': {0: 8.5495}, 'debt_to_assets': {0: 36.2781},
    #            'assets_to_eqt': {0: 1.5693}, 'dp_assets_to_eqt': {0: 1.6027}, 'ca_to_assets': {0: 63.972},
    #            'nca_to_assets': {0: 36.028}, 'tbassets_to_totalassets': {0: 60.1767}, 'int_to_talcap': {0: 1.783},
    #            'eqt_to_talcapital': {0: 97.4389}, 'currentdebt_to_debt': {0: 86.3036}, 'longdeb_to_debt': {0: 13.6964},
    #            'ocf_to_shortdebt': {0: 0.4354}, 'debt_to_eqt': {0: 0.5693}, 'eqt_to_debt': {0: 1.7426},
    #            'eqt_to_interestdebt': {0: 54.6481}, 'tangibleasset_to_debt': {0: 1.6588},
    #            'tangasset_to_intdebt': {0: 52.0199}, 'tangibleasset_to_netdebt': {0: None}, 'ocf_to_debt': {0: 0.3757},
    #            'turn_days': {0: 29.2796}, 'roa_yearly': {0: 8.6248}, 'roa_dp': {0: 8.6311},
    #            'fixed_assets': {0: 485493014.78}, 'profit_to_op': {0: 22.3212}, 'q_saleexp_to_gr': {0: 40.295},
    #            'q_gc_to_gr': {0: 82.4055}, 'q_roe': {0: 2.8184}, 'q_dt_roe': {0: 2.4508}, 'q_npta': {0: 1.8897},
    #            'q_ocf_to_sales': {0: 95.2991}, 'basic_eps_yoy': {0: 22.5}, 'dt_eps_yoy': {0: 22.5},
    #            'cfps_yoy': {0: -7.5391}, 'op_yoy': {0: 20.3803}, 'ebt_yoy': {0: 20.0555}, 'netprofit_yoy': {0: 22.5989},
    #            'dt_netprofit_yoy': {0: 37.44}, 'ocf_yoy': {0: -6.0865}, 'roe_yoy': {0: 14.1608}, 'bps_yoy': {0: 5.7302},
    #            'assets_yoy': {0: 4.531}, 'eqt_yoy': {0: 7.3914}, 'tr_yoy': {0: 0.0005}, 'or_yoy': {0: 0.6229},
    #            'q_sales_yoy': {0: -6.2623}, 'q_op_qoq': {0: -29.0853}, 'equity_yoy': {0: 7.3914},
    #            'update_flag': {0: '0'}}
    # print(f_index.keys())


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
