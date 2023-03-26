from quantization.factor_validity_check.factor_validity_check import FactorValidityCheck


def test_cal_factors_ic():
    fvc = FactorValidityCheck(factors=['roe', 'basic_eps_yoy', 'pe_ttm'], sample_periods=6)
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
