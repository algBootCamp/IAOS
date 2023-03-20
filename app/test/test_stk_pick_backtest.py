from quantization.backtest.securitypick_backtest.stk_pick_backtest import SecurityPickBackTest


def test_init_stk_pick_strategy():
    spbt = SecurityPickBackTest()
    spbt.init_stk_pick_strategy()
