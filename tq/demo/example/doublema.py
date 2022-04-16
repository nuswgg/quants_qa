#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

'''
双均线策略
注: 该示例策略仅用于功能示范, 实盘时请根据自己的策略/经验进行修改
'''
from tqsdk import TqApi, TqAuth, TargetPosTask,TqBacktest, TqSim
from tqsdk.tafunc import ma
from datetime import date

SHORT = 30  # 短周期
LONG = 60  # 长周期
SYMBOL = "SHFE.bu2105"  # 合约代码

# api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://192.168.1.4:9876", auth=TqAuth("nuswgg", "541278"))
# api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://172.16.83.232:9876", auth=TqAuth("nuswgg", "541278"))
# api = TqApi(TqSim(init_balance=100000), auth=TqAuth("天勤123", "tianqin123"))
# api = TqApi(TqSim(init_balance=100000), auth=TqAuth("nuswgg", "541278"))
api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 10)),web_gui="http://192.168.1.4:9876", auth=TqAuth("天勤123", "tianqin123"))
print("策略开始运行")

data_length = LONG + 2  # k线数据长度
# "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
klines = api.get_kline_serial(SYMBOL, duration_seconds=60, data_length=data_length)
target_pos = TargetPosTask(api, SYMBOL)

while True:
    api.wait_update()

    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA
        short_avg = ma(klines["close"], SHORT)  # 短周期
        long_avg = ma(klines["close"], LONG)  # 长周期

        # 均线下穿，做空
        if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] > short_avg.iloc[-1]:
            target_pos.set_target_volume(-3)
            print("均线下穿，做空")

        # 均线上穿，做多
        if short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] > long_avg.iloc[-1]:
            target_pos.set_target_volume(3)
            print("均线上穿，做多")
