from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.render import make_snapshot
# 使用 snapshot-selenium 渲染图片
from snapshot_selenium import snapshot
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType

def test1():
    bar = Bar()
    bar.add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
    bar.add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    # 也可以传入路径参数，如 bar.render("mycharts.html")
    bar.render("./render_html/test1.html")


def test2():
    """pyecharts 所有方法均支持链式调用"""
    bar = (
        Bar().
            add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]).
            add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    )
    bar.render("./render_html/test2.html")


def test3():
    """使用 options 配置项，在 pyecharts 中，一切皆 Options"""
    # V1 版本开始支持链式调用
    # 你所看到的格式其实是 `black` 格式化以后的效果
    # 可以执行 `pip install black` 下载使用
    bar = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
            .set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    bar.render("./render_html/test3.html")
    # 不习惯链式调用的开发者依旧可以单独调用方法
    # bar = Bar()
    # bar.add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
    # bar.add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    # bar.set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
    # bar.render("./render_html/test3.html")

def test4():
    """
    使用 snapshot-selenium 渲染图片
    """
    bar = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    )
    make_snapshot(snapshot, bar.render(), "./render_html/bar.png")

def test5():
    """
    pyecharts 提供了 10+ 种内置主题，
    开发者也可以定制自己喜欢的主题，进阶话题-定制主题 有相关介绍。
    """
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
            .add_yaxis("商家B", [15, 6, 45, 20, 35, 66])
            .set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
    )
    bar.render("./render_html/test5.html")