# -*- coding: utf-8 -*-
__author__ = 'carl'

from datetime import datetime, timedelta
from typing import List, Union

import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid

from quotation.captures.tsdata_capturer import TuShareDataCapturer

"""
对股价的Heikin Ashi蜡烛图进行可视化

HA蜡烛图

1-普通K线图中往往存在很多噪声，这些噪声容易掩盖市场真实趋势的随机波动，包括价格和成交量波动。
比如，对市场影响持续性较短的新闻事件，以及对技术指标和市场趋势解读等，都可能造成无意义的短期价格和交易量波动，
这样的噪声会对交易者分析市场产生干扰和误导。
2-为了减少普通K线图产生的噪声，HA蜡烛图应运而生。
HA中的四个价格中，HA开盘价和HA收盘价都是经过平均计算得来，平
均化的处理相当于噪声消除处理，在一定程度上消除了市场的噪声，可以更加明确地反映市场价格的走势。其计算方法具体如下∶
HA收盘价ha_close=(开盘价open+收盘价close+最高价high+最低价low)/4
HA开盘价ha_open =(上一交易日HA开盘价+上一交易日HA收盘价)/2
HA最高价ha_high =MAX（最高价high,HA开盘价ha_open,HA收盘价ha_close)
HA最低价ha_low  =MIN（最低价low,HA开盘价ha_open,HA收盘价ha_close)

pyecharts to see：https://pyecharts.org/#/zh-cn/intro
"""

tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
index = {'上证综指': '000001.SH', '深证成指': '399001.SZ',
         '沪深300': '000300.SH', '创业板指': '399006.SZ',
         '上证50': '000016.SH', '中证500': '000905.SH',
         '中小板指': '399005.SZ', '上证180': '000010.SH'}


def get_ts_code(name):
    """
    获取当前交易的股票代码和名称
    """
    df = tsdatacapture.get_stock_list()
    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    stocks = dict(stock, **index)
    return stocks[name]


# 默认设定时间周期为当前时间往前推120个交易日
def get_data(ts_code, n=300):
    t = datetime.now()
    t0 = t - timedelta(n)
    start = t0.strftime('%Y%m%d')
    end = t.strftime('%Y%m%d')
    # 如果代码在字典index里，则取的是指数数据
    if ts_code in index.values():
        df = tsdatacapture.get_index_daily(ts_code=ts_code, start_date=start, end_date=end)
    # 否则取的是个股数据
    else:
        df = tsdatacapture.get_pro_bar(ts_code=ts_code, start_date=start, end_date=end, adj='qfq')
    # 将交易日期设置为索引值
    # df.index = pd.to_datetime(df.trade_date)
    df = df.sort_values(by='trade_date')
    # 计算收益率
    return df


def cal_hadata(name):
    """
    计算Heikin Ashi蜡烛线
    """
    ts_code = get_ts_code(name)
    df = get_data(ts_code)
    # 计算修正版K线
    df['ha_close'] = (df.close + df.open + df.high + df.low) / 4.0
    ha_open = np.zeros(df.shape[0])
    ha_open[0] = df.open[0]
    for i in range(1, df.shape[0]):
        ha_open[i] = (ha_open[i - 1] + df['ha_close'][i - 1]) / 2
    df.insert(1, 'ha_open', ha_open)
    df['ha_high'] = df[['high', 'ha_open', 'ha_close']].max(axis=1)
    df['ha_low'] = df[['low', 'ha_open', 'ha_close']].min(axis=1)
    df['v_flag'] = np.where((df['open'] > df['close']), int(1), int(-1))
    df = df.iloc[1:]
    return df


def split_data(df, ktype=0):
    category_data = df.trade_date.tolist()
    if ktype == 0:
        k_values = df[['open', 'close', 'low', 'high']].values
    else:
        k_values = df[['ha_open', 'ha_close', 'ha_low', 'ha_high']].values
    k_values = [v.tolist() for v in k_values]
    volumes = [v.tolist() for v in df[['vol', 'v_flag']].values]
    for i, v in enumerate(volumes):
        v.insert(0, i)
        v[2] = int(v[2])
    d = {"categoryData": category_data, "values": k_values, "volumes": volumes}
    return d


def calculate_ma(day_count: int, data):
    result: List[Union[float, str]] = []
    for i in range(len(data["values"])):
        if i < day_count:
            result.append("-")
            continue
        sum_total = 0.0
        for j in range(day_count):
            sum_total += float(data["values"][i - j][1])
        result.append(abs(float("%.3f" % (sum_total / day_count))))
    return result


def kline_plot(name, ktype=0):
    df = cal_hadata(name)
    chart_data = split_data(df=df)
    kline_data = chart_data["values"]
    kline = (
        Kline()
            .add_xaxis(xaxis_data=chart_data["categoryData"])
            .add_yaxis(
            series_name="Dow-Jones index",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
            legend_opts=opts.LegendOpts(
                is_show=False, pos_bottom=10, pos_left="center"
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1],
                    range_start=98,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="85%",
                    range_start=98,
                    range_end=100,
                ),
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": "#00da3c"},
                    {"value": -1, "color": "#ec0000"},
                ],
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX",
            ),
        )
    )

    line = (
        Line()
            .add_xaxis(xaxis_data=chart_data["categoryData"])
            .add_yaxis(
            series_name="MA5",
            y_axis=calculate_ma(day_count=5, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True),
        )
            .add_yaxis(
            series_name="MA10",
            y_axis=calculate_ma(day_count=10, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True),
        )
            .add_yaxis(
            series_name="MA20",
            y_axis=calculate_ma(day_count=20, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True),
        )
            .add_yaxis(
            series_name="MA30",
            y_axis=calculate_ma(day_count=30, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True),
        )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )

    bar = (
        Bar()
            .add_xaxis(xaxis_data=chart_data["categoryData"])
            .add_yaxis(
            series_name="Volume",
            y_axis=chart_data["volumes"],
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                grid_index=1,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                is_scale=True,
                split_number=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    # Kline And Line
    overlap_kline_line = kline.overlap(line)

    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="63%", height="16%"
        ),
    )
    grid_chart.render("./render_html/m_kline_plot.html")


kline_plot('沪深300')
