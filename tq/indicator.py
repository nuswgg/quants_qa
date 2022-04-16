from datetime import date
from tqsdk import TqApi, TqAuth, TqBacktest, TargetPosTask
from tqsdk.ta import MA
from tqsdk.ta import MACD

# 在创建 api 实例时传入 TqBacktest 就会进入回测模式,设置web_gui=True开启图形化界面
api = TqApi(web_gui="http://192.168.1.4:9878", auth=TqAuth("nuswgg", "541278"))
# 获得 SHFE.cu2105 5分钟K线的引用
# klines = api.get_kline_serial("SHFE.cu2105", 5 * 60, data_length=15)
# 创建 cu2105 的目标持仓 task，该 task 负责调整 cu2105 的仓位到指定的目标仓位
# klines = api.get_kline_serial("SHFE.rb2105", 60)
#
# # 画一次指标线
# ma1 = MA(klines, 10)  # 使用 tqsdk 自带指标函数计算均线
# ma2 = MA(klines, 20)
# ma3 = MA(klines, 40)
#
# klines["ma10"] = ma1.ma  # 在主图中画一根默认颜色（红色）的 ma 指标线
# klines["ma20"] = ma2.ma
# klines["ma40"] = ma3.ma
#
# # 示例1: 在主图中最后一根K线上画射线以标注需要的信号
# api.draw_line(klines, -1, klines.iloc[-1].close, -1, klines.iloc[-1].high, line_type="SEG", color=0xFFFF9900, width=3)
#
# # 示例2: 绘制字符串
# api.draw_text(klines, "信号1", x=-1, y=klines.iloc[-1].high + 5, color=0xFFFF3333)
#
# # 示例3: 给主图最后5根K线加一个方框
# api.draw_box(klines, x1=-5, y1=klines.iloc[-5]["high"], x2=-1, y2=klines.iloc[-1]["low"], width=1, color=0xFF0000FF,
#              bg_color=0x7000FF00)
#
# # 由于需要在浏览器中查看绘图结果，因此程序不能退出
# while True:
#     api.wait_update()
#     # 当最后 1 根柱子最大最小值价差大于 0.05 时，在主图绘制信号
#     high = klines.iloc[-1].high
#     low = klines.iloc[-1].low
#     if high - low > 0.05:
#         # 绘制直线, 每一个 id 对应同一条直线
#         api.draw_line(klines, -1, high, -1, low, id="box%.0f" % (klines.iloc[-1].id), color=0xaa662244, width=4)
#         # 绘制字符串
#         api.draw_text(klines, "信号1", x=-1, y=low, id="text%.0f" % (klines.iloc[-1].id), color=0xFFFF3333)

############################################################
# t95 - 附图中画K线、线段和方框
############################################################
# klines = api.get_kline_serial("CFFEX.IC2104", 60)
# klines2 = api.get_kline_serial("CFFEX.IH2104", 60)
#
# # 示例1 : 在附图画出 T2012 的K线: 需要将open、high、log、close的数据都设置正确
# klines["T2012.open"] = klines2["open"]
# klines["T2012.high"] = klines2["high"]
# klines["T2012.low"] = klines2["low"]
# klines["T2012.close"] = klines2["close"]
# klines["T2012.board"] = "B2"
# ma = MA(klines, 30)
# klines["ma_MAIN"] = ma.ma
#
# # 示例2: 在附图中画线段(默认为红色)
# api.draw_line(klines, -10, klines2.iloc[-10].low, -3, klines2.iloc[-3].high, id="my_line", board="B2", line_type="SEG",
#               color=0xFFFF00FF, width=3)
#
# # 示例3: 在附图K线上画黄色的方框: 需要设置画在附图时, 将board参数选择到对应的图板即可
# api.draw_box(klines, x1=-5, y1=klines2.iloc[-5]["high"], x2=-1, y2=klines2.iloc[-1]["low"], id="my_box", board="B2",
#              width=1, color=0xFF0000FF, bg_color=0x70FFFF00)
#
# # 由于需要在浏览器中查看绘图结果，因此程序不能退出
# while True:
#     api.wait_update()


##############################################################
# t96 - 附图中画MACD
##############################################################

def calc_macd_klines(klines):
    # 计算 macd 指标
    macd = MACD(klines, 12, 26, 9)
    # 用 K 线图模拟 MACD 指标柱状图
    klines["MACD.open"] = 0.0
    klines["MACD.close"] = macd["bar"]
    klines["MACD.high"] = klines["MACD.close"].where(klines["MACD.close"] > 0, 0)
    klines["MACD.low"] = klines["MACD.close"].where(klines["MACD.close"] < 0, 0)
    klines["MACD.board"] = "MACD"
    # 在 board=MACD 上添加 diff、dea 线
    klines["diff"] = macd["diff"]
    klines["diff.board"] = "MACD"
    klines["diff.color"] = "gray"
    klines["dea"] = macd["dea"]
    klines["dea.board"] = "MACD"
    klines["dea.color"] = "rgb(255,128,0)"


klines = api.get_kline_serial("SHFE.rb2105", 5*60, 200)
while True:
    calc_macd_klines(klines)
    api.wait_update()