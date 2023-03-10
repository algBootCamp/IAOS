from quotation.captures.tsdata_capturer import TuShareDataCapturer


def test_get_daily_basic():
    cc = TuShareDataCapturer()
    res = cc.get_daily_basic().head(2).to_dict()

    print(res.keys())
    ll = ['ts_code', 'trade_date', 'close', 'turnover_rate',
          'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb',
          'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share',
          'float_share', 'free_share', 'total_mv', 'circ_mv']
