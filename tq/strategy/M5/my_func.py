# !/usr/bin/env python
#  -*- coding: utf-8 -*-

import pandas as pd
import time
from tqsdk.ta import MA,EMA
from tqsdk.tafunc import ma,ema,abs,std, hhv, llv, time_to_datetime

def get_index_line(klines):
    '''计算指标线'''
    high = klines.high.iloc[-2]  # 前一日的最高价
    low = klines.low.iloc[-2]  # 前一日的最低价
    close = klines.close.iloc[-2]  # 前一日的收盘价
    pivot = (high + low + close) / 3  # 枢轴点
    bBreak = high + 2 * (pivot - low)  # 突破买入价
    sSetup = pivot + (high - low)  # 观察卖出价
    sEnter = 2 * pivot - low  # 反转卖出价
    bEnter = 2 * pivot - high  # 反转买入价
    bSetup = pivot - (high - low)  # 观察买入价
    sBreak = low - 2 * (high - pivot)  # 突破卖出价
    print("已计算新标志线, 枢轴点: %f, 突破买入价: %f, 观察卖出价: %f, 反转卖出价: %f, 反转买入价: %f, 观察买入价: %f, 突破卖出价: %f"
                % (pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak))
    return pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak


def get_margin(api,symbol):
    margin_list = pd.read_csv('D:/BaiduNetdiskDownload/Quants/tq/margin.csv')
    quote = api.get_quote(symbol)
    prod = quote.product_id
    margin = margin_list[margin_list.code==prod]
    return margin.cust

def trace_stop_loss(klines):
    pass

# def price_stop_loss(basedata,STOP_LOSS_PRICE):
#     '''
#
#     :param basedata:
#     :param STOP_LOSS_PRICE:
#     :return: STOP_LOSS_PRICE
#     '''
#     # Temp_STOP_LOSS = basedata.close.iloc[-2] - basedata.maBody.iloc[-2] - base_data.std_cdl_f.iloc[-2] * 2
#     # if Temp_STOP_LOSS > STOP_LOSS_PRICE:
#     #     STOP_LOSS_PRICE = Temp_STOP_LOSS
#     # 放巨量 和 大量 止损幅度小
#     if basedata.dl.iloc[-2] or basedata.jl.iloc[-2]:
#         Temp_STOP_LOSS = basedata.close.iloc[-2] - base_data.std_cdl_f.iloc[-2]
#         return STOP_LOSS_PRICE if STOP_LOSS_PRICE>Temp_STOP_LOSS else Temp_STOP_LOSS
#     elif basedata.zdStrengh>1:
#         Temp_STOP_LOSS = basedata.close.iloc[-2] - basedata.maBody.iloc[-2] - base_data.std_cdl_f.iloc[-2] * 2
#         return STOP_LOSS_PRICE if STOP_LOSS_PRICE>Temp_STOP_LOSS else Temp_STOP_LOSS
#     elif basedata.jl.iloc[-2] and basedata.:
#         Temp_STOP_LOSS = basedata.close.iloc[-2] + basedata.cdlUs.iloc[-2]
#     else:
#         Temp_STOP_LOSS = basedata.close.iloc[-2] - basedata.maBody.iloc[-2] - base_data.std_cdl_f.iloc[-2] * 2
#         return STOP_LOSS_PRICE if STOP_LOSS_PRICE > Temp_STOP_LOSS else Temp_STOP_LOSS
#     return get_stop_loss

def get_kline_time(kline_datetime):
    """获取k线的时间(不包含日期)"""
    # kline_time = datetime.fromtimestamp(kline_datetime // 1000000000).time()  # 每根k线的时间
    kline_time = datetime.fromtimestamp(kline_datetime // 1000000000).strftime('%Y-%m-%d %H:%M')  # 每根k线的时间
    return kline_time

def trading_start_end(quote):
    # calc day trade start/end in sec from 00:00:00
    # calc night trade start/end in sec from 00:00:00
    DAY_TRADING_PERIOD = quote.trading_time.day
    NIGHT_TRADING_PERIOD = quote.trading_time.night

    DAY_TRADE_START = DAY_TRADING_PERIOD[0][0]
    DAY_TRADE_END = DAY_TRADING_PERIOD[-1][-1]

    if len(NIGHT_TRADING_PERIOD) == 0:  # 检查是否为空,为空则没有夜盘
        NITE_TRADE_START = '00:00:00'
        NITE_TRADE_END = '00:00:00'
    else:
        NITE_TRADE_START = NIGHT_TRADING_PERIOD[0][0]
        NITE_TRADE_END = NIGHT_TRADING_PERIOD[-1][-1]

    DAY_TRADE_START_HR, DAY_TRADE_START_MIN, DAY_TRADE_START_SEC = DAY_TRADE_START.split(':')
    DAY_TRADE_END_HR, DAY_TRADE_END_MIN, DAY_TRADE_END_SEC = DAY_TRADE_END.split(':')
    NITE_TRADE_START_HR, NITE_TRADE_START_MIN, NITE_TRADE_START_SEC = NITE_TRADE_START.split(':')
    NITE_TRADE_END_HR, NITE_TRADE_END_MIN, NITE_TRADE_END_SEC = NITE_TRADE_END.split(':')

    DAY_START = int(DAY_TRADE_START_HR)*3600 + int(DAY_TRADE_START_MIN)*60 + int(DAY_TRADE_START_SEC)
    DAY_END = int(DAY_TRADE_END_HR) * 3600 + int(DAY_TRADE_END_MIN) * 60 + int(DAY_TRADE_END_SEC)
    NITE_START = int(NITE_TRADE_START_HR)*3600 + int(NITE_TRADE_START_MIN)*60 + int(NITE_TRADE_START_SEC)
    NITE_END = int(NITE_TRADE_END_HR) * 3600 + int(NITE_TRADE_END_MIN) * 60 + int(NITE_TRADE_END_SEC)

    return DAY_START, DAY_END, NITE_START, NITE_END

def get_time_now():
    cur_time = time.localtime()
    HR, MIN, SEC = cur_time.tm_hour, cur_time.tm_min, cur_time.tm_sec
    early_morning = 3*3600
    time_now = int(HR)*3600 + int(MIN)*60 + int(SEC)
    if time_now < early_morning:
        time_now += 24*3600
    return time_now

def trading_period(quote):
    #####获取期货品质的交易时间#######
    DAY_START, DAY_END, NITE_START, NITE_END = trading_start_end(quote)
    time_now = get_time_now()

    DAY_IN_TRADING = (time_now >= DAY_START) & (time_now < DAY_END)
    NITE_IN_TRADING = (time_now >= NITE_START) & (time_now < NITE_END)

    if NITE_START == 0:  # 检查是否有夜盘
        return DAY_IN_TRADING
    else:
        return (DAY_IN_TRADING | NITE_IN_TRADING)
    #####获取期货品质的交易时间#######

def last_kline(kline,quote):
    DAY_START, DAY_END, NITE_START, NITE_END = trading_start_end(quote)
    time_now = get_time_now()
    if DAY_START < time_now < DAY_END:
        return ((DAY_END - time_now) < kline.duration.iloc[-2])
    else:
        if NITE_END != 0:
            return ((NITE_END - time_now) < kline.duration.iloc[-2])
        else:
            return False

def second_kline(kline,quote):
    DAY_START, DAY_END, NITE_START, NITE_END = trading_start_end(quote)
    time_now = get_time_now()
    if DAY_START < time_now < DAY_END:
        return (kline.duration.iloc[-2] < (time_now - DAY_START )) & ((time_now - DAY_START ) <= kline.duration.iloc[-2] * 2)
    else:
        if NITE_END != 0:
            return (kline.duration.iloc[-2] < (time_now - NITE_START )) & ((time_now - NITE_START ) <= kline.duration.iloc[-2] * 2)
        else:
            return False

def first_kline(kline):
    global quote
    DAY_START, DAY_END, NITE_START, NITE_END = trading_start_end(quote)
    ts = time_to_datetime(kline.datetime/1e+9)
    kline_time = ts.hour*3600 + ts.minute*60 + ts.second
    if DAY_START == (kline_time - kline.duration):
        return True
    else:
        return False

def classify_mas(basedata):
    pass

