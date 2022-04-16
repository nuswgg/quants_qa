#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = "Xiaoli"
# https://zhuanlan.zhihu.com/p/243165040

#####################
#示例2分段追踪止损
#####################

"""
策略思路：
开仓思路（多头为例）
以最新价和当根K线的结算价比较结果判断入场时机，最高价突破入场以来最高点再次入场。
平仓思路（多头为例）
分段追踪止损+尾盘平仓
1、浮盈为负，以指定LoseBit步长限价止损
2、浮盈为正
A段：最新价在开仓均价以上B段基线以下，以RC2步长设置追踪+回调止赢
B段：最新价在B段基线以上，C段以下，以RC1步长设置追踪+回调止赢
C段：最新价在C段基线以上，以WinM步长止赢
"""

from tqsdk import TqApi, TargetPosTask, tafunc
from tqsdk.tafunc import crossup

Step = 10
LoseBit = 10
WinBit = 10
RC1 = 2
RC2 = 3
WinM = 25

# 设置合约代码
SYMBOL = "DCE.m2105"
api = TqApi(auth=TqAuth("nuswgg", "541278"))
ticks = api.get_tick_serial(SYMBOL)
klines = api.get_kline_serial(SYMBOL, 60 * 60)
position = api.get_position(SYMBOL)
target_pos = TargetPosTask(api, SYMBOL)
myhigh = float("nan")

while True:
    api.wait_update()
    if api.is_changing(ticks.iloc[-1], "datetime"):
        df = ticks.copy()
        df["crossup"] = crossup(ticks["last_price"], ticks["average"])
        myhigh = max(df.iloc[-1]["last_price"], myhigh)
        df["myhigh"] = myhigh
        df["crossup2"] = crossup(ticks["last_price"], df["myhigh"])
        now = tafunc.time_to_datetime(ticks.iloc[-1]["datetime"])
        if time(14, 59) < now.time() <= time(15):
            target_pos.set_target_volume(0)
        else:
            if position.pos_long == 0:
                if df.iloc[-1]["crossup"] == 1:
                    target_pos.set_target_volume(1)
                    myhigh = df.iloc[-1]["last_price"]
            else:
                if position.pos_long == 1:
                    df.iloc[-1]["crossup2"] == 1:
                    target_pos.set_target_volume(2)
                    myhigh = df.iloc[-1]["last_price"]
                if df.iloc[-1]["last_price"] < position.open_price_long - LoseBit:
                    target_pos.set_target_volume(0)
                elif myhigh >= position.open_price_long + WinBit:
                    if df.iloc[-1]["last_price"] < myhigh - RC1:
                        target_pos.set_target_volume(0)
                elif myhigh >= position.open_price_long + WinBit + Step:
                    if df.iloc[-1]["last_price"] < myhigh - RC2:
                        target_pos.set_target_volume(0)
                elif df.iloc[-1] >= position.open_price_long + WinM:
                    target_pos.set_target_volume(0)




