from quantization.backtest.securitypick_backtest.stk_pick_backtest import SecurityPickBackTest


def test_init_stk_pick_strategy():
    spbt = SecurityPickBackTest(stk_pick_strategy_weights_args={'roe': 34, 'basic_eps_yoy': 33, 'pe_ttm': 33})
    spbt.init_stk_pick_strategy()
    spbt.cal_shift_period_return()
