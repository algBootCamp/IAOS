condtions_col = ['ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date', 'exchange',
                 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'total_mv', 'circ_mv',
                 'dv_ratio', 'dv_ttm', 'changepercent', 'trade', 'volume', 'turnoverratio', 'amount',
                 'ann_date', 'end_date', 'eps', 'current_ratio', 'quick_ratio', 'bps',
                 'netprofit_margin', 'grossprofit_margin', 'profit_to_gr', 'op_of_gr', 'roe',
                 'roa', 'npta', 'roic', 'roe_yearly', 'roa2_yearly', 'debt_to_assets', 'op_yoy',
                 'ebt_yoy', 'tr_yoy', 'or_yoy', 'equity_yoy', 'update_flag'
                 ]

dic = {'ts_code': '222', 'npta': [30, 80]}

for k in dic:
    if condtions_col.__contains__(k):
        print(dic[k])
