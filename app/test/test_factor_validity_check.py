from quantization.factor_validity_check.factor_validity_check import FactorValidityCheck


def test_cal_factors_ic():
    fvc = FactorValidityCheck(sample_periods=7)
    # fvc.check_factor_validity(fac='roe_yearly')
    fvc.get_validity_all_factors(refresh=False)


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


def test_get_validity_factors():
    assert False
