-*- coding: utf-8 -*-

from tqsdk import TqApi, TqAuth,TqKq
# api = TqApi(auth=TqAuth("nuswgg", "541278"))

# 创建api实例，设置web_gui=True生成图形化界面
api = TqApi(web_gui=True, auth=TqAuth("nuswgg", "541278"))
# mock
api = TqApi(TqKq(), auth=TqAuth("nuswgg", "541278"))
quote = api.get_quote("SHFE.ni2106")
# 打印行情
while True:
    api.wait_update()
    print (quote.datetime, quote.last_price)

#######################
# t30 - 使用K线/Tick数据
#######################

# 获得 ni2106 10秒K线的引用
klines = api.get_kline_serial("SHFE.ni2106", 10)
#获得上一K线的时间
while True:
    api.wait_update()
    # 判断整个tick序列是否有变化
    if api.is_changing(ticks):
        # ticks.iloc[-1]返回序列中最后一个tick
        print("tick变化", ticks.iloc[-1])
    # 判断最后一根K线的时间是否有变化，如果发生变化则表示新产生了一根K线
    if api.is_changing(klines.iloc[-1], "datetime"):
        # datetime: 自unix epoch(1970-01-01 00:00:00 GMT)以来的纳秒数
        print("新K线", datetime.datetime.fromtimestamp(klines.iloc[-1]["datetime"] / 1e9))
    # 判断最后一根K线的收盘价是否有变化
    if api.is_changing(klines.iloc[-1], "close"):
        # klines.close返回收盘价序列
        print("K线变化", datetime.datetime.fromtimestamp(klines.iloc[-1]["datetime"] / 1e9), klines.close.iloc[-1])

################
# 一个典型程序的结构
################
klines = api.get_kline_serial("SHFE.rb1901", 60)
target_pos = TargetPosTask(api, "SHFE.rb1901")

while True:                                                 #判断开仓条件的主循环
    api.wait_update()                                       #等待业务数据更新
    if 开仓条件:
        target_pos.set_target_volume(1)                     #如果触发了，则通过 target_pos 将 SHFE.rb1901 的目标持仓设置为多头 1 手，具体的调仓工作则由 target_pos 在后台完成
        break                                               #跳出开仓循环，进入下面的平仓循环

while True:                                                 #判断平仓条件的主循环
    api.wait_update()
    if 平仓条件:
        target_pos.set_target_volume(0)                     ##如果触发了，则通过 target_pos 将 SHFE.rb1901 的目标持仓设置为0手(即空仓)
        break

api.close()                                                 #注意：程序结束运行前需调用此函数以关闭天勤接口实例并释放相应资源，同时此函数会包含发送最后一次wait_update信息传输
#至此就完成一次完整的开平仓流程，如果平仓后还需再判断开仓条件可以把开仓循环和平仓循环再套到一个大循环中。

##########################
#下载数据
##########################

from datetime import datetime, date
from contextlib import closing
from tqsdk import TqApi, TqSim,TqAuth
from tqsdk.tools import DataDownloader

# api = TqApi(TqSim())
api = TqApi(auth=TqAuth("nuswgg", "541278"))
download_tasks = {}
download_tasks["cu_min"] = DataDownloader(api, symbol_list=["SHFE.rb2106"], dur_sec=5,
                    start_dt=datetime(2019, 5, 10, 6, 0 ,0), end_dt=datetime(2019, 12, 11, 16, 0, 0), csv_file_name="2SHFE.rb2106.csv")

with closing(api):
    while not all([v.is_finished() for v in download_tasks.values()]):
        api.wait_update()
        print("progress: ", { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() })