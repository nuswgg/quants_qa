# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# https://zhuanlan.zhihu.com/p/180116971

from tqsdk import TqApi, TqBacktest, TargetPosTask, ta, TqSim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import warnings
from datetime import date

api = TqApi(account=TqSim(init_balance=20000), backtest=TqBacktest(start_dt=date(2020, 5, 1), end_dt=date(2020, 8, 10)),
            web_gui=True)
symbol = "SHFE.rb2010"
klines = api.get_kline_serial(symbol, 3600)
quote = api.get_quote(symbol)
position = api.get_position(symbol)
targetpos = TargetPosTask(api, symbol)


def get_pv_df(klines: pd.DataFrame, distance=10):
    xxx = np.arange(len(klines))
    yyy = np.array(klines["close"])

    warnings.filterwarnings("error")
    for i in range(1, 100):
        try:
            z1 = np.polyfit(xxx, yyy, i)
        except Warning:
            z1 = np.polyfit(xxx, yyy, i - 1)
            warnings.filterwarnings("ignore")
            break
    p1 = np.poly1d(z1)
    yvals = p1(xxx)

    '''
    plt.plot(xxx, yyy, '.',label='original values')
    plt.plot(xxx, yvals, 'r',label='polyfit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.legend(loc=4)
    plt.title('polyfitting')
    plt.show()
    '''

    num_peak = signal.find_peaks(yvals, distance=distance)
    num_valley = signal.find_peaks(-yvals, distance=distance)

    '''
    num_peak = signal.find_peaks_cwt(yyy, np.arange(1,100), signal.ricker)#小波变换后找峰效果似乎不是很好
    num_valley = signal.find_peaks_cwt(yyy, np.arange(1,100), signal.ricker) #小波变换后找峰效果似乎不是很好
    '''

    '''
    plt.plot(xxx, yyy, '.',label='original values')
    plt.plot(xxx, yvals, 'r',label='polyfit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.legend(loc=4)
    plt.title('polyfitting')
    for ii in range(len(num_peak[0])):
        plt.plot(num_peak[0][ii], yvals[num_peak[0][ii]],'*',markersize=10)
    for ii in range(len(num_valley[0])):
        plt.plot(num_valley[0][ii], yvals[num_valley[0][ii]],'*',markersize=10)
    plt.show()
    '''

    klines_copy = klines.copy()
    # 2为非峰非谷
    klines_copy["pv"] = [2] * len(klines_copy)

    # 1为峰
    for i in num_peak[0]:
        klines_copy.iloc[i, -1] = 1
    # 0为谷
    for i in num_valley[0]:
        klines_copy.iloc[i, -1] = 0

    # 峰谷定位
    df = klines_copy[klines_copy["pv"] != 2].copy()
    df["hv"] = df["close"].diff()
    return df


df = get_pv_df(klines)
pv = list(df.iloc[-3:]["pv"])
price1 = df.iloc[-3]["close"]
price2 = df.iloc[-2]["close"]
price3 = df.iloc[-1]["close"]
atr = ta.ATR(klines, 14).iloc[-1]["atr"]

while True:
    api.wait_update()
    if api.is_changing(klines.iloc[-1], "datetime"):
        df = get_pv_df(klines)
        pv = list(df.iloc[-3:]["pv"])
        price1 = df.iloc[-3]["close"]
        price2 = df.iloc[-2]["close"]
        price3 = df.iloc[-1]["close"]
        atr = ta.ATR(klines, 14).iloc[-1]["atr"]
    if api.is_changing(quote):
        if position.pos_long == 0:
            if pv == [0, 1, 0] and price1 > price3:
                if quote.last_price > price2:
                    targetpos.set_target_volume(1)
                    myhigh = quote.last_price
        elif position.pos_short == 0:
            if pv == [1, 0, 1] and price1 < price3:
                if quote.last_price < price2:
                    targetpos.set_target_volume(-1)
                    mylow = quote.last_price
        if position.pos_long > 0:
            myhigh = max(myhigh, quote.last_price)
            if myhigh - quote.last_price > 2 * atr:
                targetpos.set_target_volume(0)
        elif position.pos_short > 0:
            mylow = min(mylow, quote.last_price)
            if quote.last_price - mylow > 2 * atr:
                targetpos.set_target_volume(0)

