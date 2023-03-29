from quantization.factor_validity_check.factor_validity_check import FactorValidityCheck


def test_cal_factors_ic():
    fvc = FactorValidityCheck(factors=['turnover_rate', 'turnover_rate_f', 'volume_ratio',
                                       'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share',
                                       'total_mv', 'circ_mv', 'dv_ratio', 'dv_ttm', 'changepercent', 'trade',
                                       'volume', 'amount', 'eps', 'current_ratio', 'quick_ratio', 'bps',
                                       'netprofit_margin', 'grossprofit_margin', 'profit_to_gr', 'op_of_gr',
                                       'roe', 'basic_eps_yoy', 'roa', 'npta', 'roic', 'roe_yearly',
                                       'roa2_yearly', 'debt_to_assets', 'op_yoy', 'ebt_yoy', 'tr_yoy', 'or_yoy',
                                       'equity_yoy'], sample_periods=7)
    fvc.get_validity_factors()
    fvc.draw_return_picture()


def test_draw():
    import numpy as np
    import matplotlib.pyplot as plt

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.xticks(size=12, rotation=50)  # 设置字体大小和字体倾斜度

    data = np.random.normal(5, 1, 100)
    fig = plt.figure()
    plt.plot(data)
    plt.show()


def test_draw_return_picture():
    assert False
