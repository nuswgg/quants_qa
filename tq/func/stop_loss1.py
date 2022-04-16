#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = "Xiaoli"
# https://zhuanlan.zhihu.com/p/243165040

###################
# 示例1水平通道止损
###################


"""
策略思路：
1.最高价突破前期5周期均线与60周期均线金叉k线最高点，平空做多。
2.最低价突破前期5周期均线与60周期均线死叉k线最低点，平多做空。
"""

from tqsdk import TqApi, TargetPosTask
from tqsdk.ta import MA
from tqsdk.tafunc import crossup, crossdown

# 设置合约代码
SYMBOL = "DCE.m2105"
api = TqApi(auth=TqAuth("nuswgg", "541278"))
quote = api.get_quote(SYMBOL)
klines = api.get_kline_serial(SYMBOL, 60 * 60)
target_pos = TargetPosTask(api, SYMBOL)


while True:
    api.wait_update()
    if api.is_changing(quote):
        df = klines.copy()
        df["crossup"] = crossup(MA(df, 5)["ma"], MA(df, 60)["ma"]) #定位所有均线金叉
        df["crossdown"] = crossdown(MA(df, 5)["ma"], MA(df, 60)["ma"]) #定位所有均线死叉
        try:
            top = df[df["crossup"]==1].iloc[-1]["high"] #找最近一个金叉的K线位置
        except IndexError:
            top = float("nan")
        try:
            bottom = df[df["crossdown"]==1].iloc[-1]["low"] #找最近一个死叉的K线位置
        except IndexError:
            bottom = float("nan")
        #float("nan")与任何数值进行判断均为False
        if quote["last_price"] > top:
            target_pos.set_target_volume(1)
        elif quote["last_price"] < bottom:
            target_pos.set_target_volume(-1)

