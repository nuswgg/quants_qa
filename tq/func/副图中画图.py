__author__ = 'limin'
from datetime import datetime
from tqsdk import TqApi, TqAuth
from tqsdk.ta import MA
api = TqApi(auth=TqAuth("信易账号", "密码"),web_gui=True)
kline = api.get_kline_serial("SHFE.rb2105", 60,data_length=100)
# 通过浏览器访问TqSdk指定的地址，需保持程序运行
while True:
    # 计算收盘价的10日简单均线
    ma = MA(kline,10)
    # 为K线增加一列ma_B2，把均线值赋值给此列
    kline["ma_B2"] = ma.ma
    # 添加一列“.board”，用来设置副图，列的值为任意字符串，相同字符串表示同一个副图
    kline["ma_B2.board"] = "B2"
    # 添加一列“.color”，用来设置颜色
    kline["ma_B2.color"] = "green"  # 设置为绿色. 以下设置颜色方式都可行: "green", "#00FF00", "rgb(0,255,0)", "rgba(0,125,0,0.5)"
    # 在另一个附图画一根比ma小4的宽度为4的紫色指标线
    kline["ma_4"] = ma.ma - 4
    kline["ma_4.board"] = "MA4"  # 设置为另一个附图
    kline["ma_4.color"] = 0xFF9933CC  # 设置为紫色, 或者 "#9933FF"
    kline["ma_4.width"] = 4  # 设置宽度为4，默认为1
    api.wait_update()
api.close()