# !/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'eric'

'''
一个品种 每天多少撤单以下 不被监管
商品 500
股指 400
交易所代码
 * CFFEX: 中金所
 * SHFE: 上期所
 * DCE: 大商所
 * CZCE: 郑商所
 * INE: 能源交易所(原油)
 * SSE: 上交所
 * SZSE: 深交所
'''
# simnow 服务器
# "交易服务器": "tcp://180.168.146.187:10201",
# "行情服务器": "tcp://180.168.146.187:10211"
# 注册账号: 15828033765
# user: nuswgg
# investorid: 187180
# brokerid: 9999
# 挂靠会员: 海通期货

from datetime import datetime, date
from tqsdk import TqApi, TargetPosTask,TqBacktest,TqAuth,TqSim
from tqsdk.algorithm.twap import Twap
from tqsdk.ta import MA,EMA
from tqsdk.tafunc import ma,ema,abs,std, hhv, llv, time_to_datetime
import pandas as pd
import talib as ta
import time
from functools import wraps

from my_func import *
from my_strategy import *

# class time_stop_loss(t1):
#     pass

class trade_count():
    def __init__(self, func):
        self.func = func
        self.count = 0
    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args,**kwargs)

def new_kline(kline):
    global temp_min
    # cur_min = time.localtime(basedata.datetime.iloc[-2:-1]/1e+9).tm_min
    cur_min = time_to_datetime(kline.datetime.iloc[-2]).minute
    if cur_min == temp_min:
        return False
    else:
        temp_min = cur_min
        return True

def time_stop_loss():
    pass
    # trade_list

# def cnt_cancl(func):
#     @wraps(func)
#     def wraper(*arg,**kwargs):

## control para
CONST_SYMBOL = "KQ.m@SHFE.rb"  # 合约代码
# SYMBOL = "SHFE.rb2110"  ## 合约代码
CLOSE_HOUR, CLOSE_MINUTE = 14, 50  # 平仓时间 最后一根k线  全部平仓
STOP_LOSS_PRICE = 10  # 止损点(价格)
multiZF = 8  # 均线靠拢的放到系数 [1,30] %10 - 300%
inc_body1_4 = 4 # ma_kl1_4 4均线靠拢 增量参数  base 10 5就是增加50%
inc_body1_3 = 4 # ma_kl1_3 3均线靠拢 增量参数  base 10 5就是增加50%
data_len = 200

# api = TqApi(TqSim(init_balance=100000), backtest=TqBacktest(start_dt=date(2021, 3, 27), end_dt=date(2021, 4, 2)),web_gui="http://192.168.1.4:9876", auth=TqAuth("天勤123", "tianqin123"))
# api = TqApi(TqSim(init_balance=100000),backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://172.16.83.232:9876", auth=TqAuth("nuswgg", "541278"))
    # api = TqApi(TqSim(init_balance=100000),backtest=TqBacktest(start_dt=date(2021, 3, 24), end_dt=date(2021, 3, 24)), auth=TqAuth("nuswgg", "541278"))
# api = TqApi(TqSim(init_balance=100000), auth=TqAuth("nuswgg", "541278"))
api = TqApi(TqSim(init_balance=100000), auth=TqAuth("天勤123", "tianqin123"))

margin = get_margin(api,CONST_SYMBOL)
quote = api.get_quote(CONST_SYMBOL)
SYMBOL = quote.underlying_symbol

acct = api.get_account()
position = api.get_position(SYMBOL)
risk = api.get_risk_management_data(SYMBOL)
cancel_cnt = risk.frequent_cancellation.cancel_order_count

#获取多个周期数据
klines_d = api.get_kline_serial(SYMBOL, 60*60*24, data_len)  # 86400: 使用日线
klines_m1 = api.get_kline_serial(SYMBOL, 60, data_len) #1分K线 获取2 小时
klines_m5 = api.get_kline_serial(SYMBOL, 60*5, data_len) #5分K线 获取大概2天  一天是69
klines_m15 = api.get_kline_serial(SYMBOL, 60*15, data_len) #15分K线 获取3.5天
tick_data =  api.get_tick_serial(SYMBOL,1200)

target_pos = TargetPosTask(api, SYMBOL)
target_pos_value = position.pos_long - position.pos_short  # 净目标净持仓数
open_position_price = position.open_price_long if target_pos_value > 0 else position.open_price_short  # 开仓价
base_data = calc_base_data(klines_m5)
temp_min = 61
volume_multiple = quote.volume_multiple

print("策略开始运行")
while True:
    api.wait_update()
    price = quote.last_price
    print(price)
    # print(trading_period(quote))
    orders = api.get_order(account='TqSim')

    # # structTime = time.localtime(base_data.datetime.iloc[-2] / 1e+9)
    # structTime = time_to_datetime(base_data.datetime.iloc[-2])
    # # M5_STAMP = datetime(*structTime[:6]).strftime('%Y-%m-%d %H:%M')

    # # # 产生新k线,则重新计算指标线 or 其他数据
    if api.is_changing(klines_m5.iloc[-1], "datetime") & api.is_serial_ready(klines_m5):
        # print(time_to_datetime(klines_m5.datetime.iloc[-1]))
        base_data = calc_base_data(klines_m5)
        base_data['action_filled'] = base_data.direction.bfill()
        base_data['stop_loss_filled'] = base_data.stop_loss.bfill()
        base_data['stop_loss_final'] = base_data.apply(stop_loss_final,axis=1)
        # structTime = time.localtime(base_data.datetime.iloc[-1] / 1e+9)
        structTime = time_to_datetime(klines_m5.datetime.iloc[-1] / 1e+9)
        if (structTime.hour == 14) & (structTime.minute == 55):
            base_data['time'] = base_data.datetime.apply(lambda x:get_kline_time(x))
            base_data.to_csv('D:/BaiduNetdiskDownload/Quants/tq/data/base_data_%d_%d.csv' %(structTime.tm_mon, structTime.tm_mday))

        # # #开多仓条件
        # # # 交易时间 & 没有冻结资金 - 没有仓位  应该可以没有 (position.pos_long == 0)
        ## 没有未成交单, 没有仓位
    if (base_data.direction.iloc[-2] != 'noAction') & (acct.frozen_margin == 0) & (acct.risk_ratio == 0) & (last_kline(klines_m5,quote)==False):
        pass
        # open_pos(base_data)

        #有仓位 有新的开仓信号
    elif (acct.risk_ratio != 0) & (base_data.direction.iloc[-2] != 'noAction'):
        pass
        # ## 最后根K线，不可以交易
        # if (base_data.direction.iloc[-2] == 'SELL') & (acct.frozen_margin == 0) & (last_kline(klines_m5,quote)==False):
        #     vol_avail = round(acct.available * volume_multiple / (margin * price))  # 用定制的margin来计算 可开仓
        #     structTime = time.localtime(base_data.datetime.iloc[-1]/1e+9)
        #     # print(datetime(*structTime[:6]).strftime('%Y-%m-%d %H:%M:%S'))
        #     BUY_PRICE = base_data.close.iloc[-2] - base_data.std_cdl_b.iloc[-2]
        #     orders = api.insert_order(SYMBOL,direction="BUY",offset = "OPEN", volume=vol_avail,limit_price=BUY_PRICE)
        #     # orders2 = api.insert_order(SYMBOL, direction="BUY", offset="OPEN", volume=1, limit_price ='BEST' )  ##仅中金所支持 BEST / FIVELEVEL
        #     # orders3 = api.insert_order(SYMBOL, direction="BUY", offset="OPEN", volume=1)  ## 中金所、上期所、原油交易所、上交所、深交所不支持市价单
        #     # orders4 = api.insert_order(SYMBOL, direction="BUY", offset="OPEN", volume=1,advanced = 'FAK')
        #     # orders5 = api.insert_order(SYMBOL, direction="BUY", offset="OPEN", volume=1,limit_price = 5530)  # 限价埋单，当日有效
        #       close1 = api.insert_order(SYMBOL, direction="SELL", offset="CLOSETODAY", volume=1,limit_price = 5530)
        #     # 平仓
        #     # api.insert_order(SYMBOL, direction="SELL", offset="CLOSETODAY", volume=1, limit_price=5050)  上期所和原油分平今/平昨, 平今用"CLOSETODAY", 平昨用"CLOSE";
        #
        #     # detail refer to https://doc.shinnytech.com/tqsdk2/latest/advanced/order.html?highlight=insert_order
        #         # orders.order
        #     # target_pos.set_target_volume(vol_avail)
        #     STOP_LOSS_PRICE = BUY_PRICE - base_data.maBody.iloc[-2] - base_data.std_cdl_f.iloc[-2] * 2
        #     print(datetime(*structTime[:6]).strftime('%Y-%m-%d %H:%M:%S') + ' Buy %d, 止损 %d' %(BUY_PRICE, STOP_LOSS_PRICE) )
        #     api.cancel_orde()

    # 有未成交单
    if acct.frozen_margin != 0:
        print('got position')
        # 任何tick都计算 STOP_LOSS_PRICE 满足条件就平仓
        # STOP_LOSS_PRICE = price_stop_loss(base_data, STOP_LOSS_PRICE)

    # # 平多仓条件 价格止损
    # if api.is_changing(quote, "last_price") & (position.pos_long > 0) & (quote.last_price<= STOP_LOSS_PRICE):
    #     closeTime = quote.datetime[:19]
    #     print('close pos @ %s @ price %d' %(closeTime, STOP_LOSS_PRICE))
    #     target_pos.set_target_volume(0)
    # # 平多条件 时间止损
    # if (in_trade_period == False) & (position.pos_long > 0)\
    #         & :
    #     target_pos.set_target_volume(0)


# ###########高级委托指令##########################
# limit_price	    advanced	memo
# 指定价格	None	限价指令，即时成交，当日有效
# 指定价格	FAK	    限价指令，即时成交剩余撤销
# 指定价格	FOK	    限价指令，即时全部成交或撤销
# None	    None	市价指令，即时成交剩余撤销
# None	    FAK	    市价指令，即时成交剩余撤销
# None	    FOK	    市价指令，即时全部成交或撤销
# BEST	    None	最优一档即时成交剩余撤销指令
# BEST	    FAK 	最优一档即时成交剩余撤销指令
# FIVELEVEL	None	最优五档即时成交剩余撤销指令
# FIVELEVEL	FAK	    最优五档即时成交剩余撤销指令
#############################################



##########################################################################
# order attribute
    # {'order_id': 'PYSDK_insert_195e7750968fd307e9c9232b3d1ebfe9',
    #  'exchange_order_id': '',
    #  'exchange_id': 'SHFE',
    #  'instrument_id': 'rb2110',
    #  'direction': 'BUY',
    #  'offset': 'OPEN',
    #  'volume_orign': 1,
    #  'volume_left': 1,
    #  'limit_price': 4100.0,
    #  'price_type': 'LIMIT',
    #  'volume_condition': 'ANY',
    #  'time_condition': 'GFD',
    #  'insert_date_time': 0,
    #  'last_msg': '',
    #  'status': 'ALIVE'}

# position
# {'exchange_id': 'SHFE',
# 'instrument_id': 'rb2105',
# 'pos_long_his': 0,
# 'pos_long_today': 6,
# 'pos_short_his': 0,
# 'pos_short_today': 0,
# 'volume_long_today': 6,
# 'volume_long_his': 0,
# 'volume_long': 6,
# 'volume_long_frozen_today': 0,
# 'volume_long_frozen_his': 0,
# 'volume_long_frozen': 0,
# 'volume_short_today': 0,
# 'volume_short_his': 0,
# 'volume_short': 0,
# 'volume_short_frozen_today': 0,
# 'volume_short_frozen_his': 0,
# 'volume_short_frozen': 0,
# 'open_price_long': 4227.0,
# 'open_price_short': nan,
# 'open_cost_long': 253620.0,
# 'open_cost_short':nan,
# 'position_price_long': 4227.0,
# 'position_price_short': nan,
# 'position_cost_long': 253620.0,
# 'position_cost_short': nan,
# 'float_profit_long': 0.0,
# 'float_profit_short': nan,
# 'float_profit': 0.0,
# 'position_profit_long': 0.0,
# 'position_profit_short': nan,
# 'position_profit': 0.0,
# 'margin_long': 25620.0,
# 'margin_short': nan,
# 'margin': 25620.0,
# 'market_value_long': nan,
# 'market_value_short': nan,
# 'market_value': nan,
# 'user_id': '',
# 'volume_long_yd': 0,
# 'volume_short_yd': 0,
# 'last_price': 4227.0}

# account的信息：
# {'currency': 'CNY',
# 'pre_balance': 11063866.3,
# 'static_balance': 11063866.3,
# 'balance': 11063302.733000001,
# 'available': 11028999.633000001,
# 'ctp_balance': 11063302.733000001,
# 'ctp_available': 11028999.633000001,
# 'float_profit': -220.0,
# 'position_profit': -220.0,
# 'close_profit': -280.0,
# 'frozen_margin': 4270.0,
# 'margin': 30029.0,
# 'frozen_commission': 4.1000000000000005,
# 'commission': 63.56700000000001,
# 'frozen_premium': 0.0,
# 'premium': 0.0,
# 'deposit': 0.0,
# 'withdraw': 0.0,
# 'risk_ratio': 0.0027142889175786958,
# 'market_value': 0.0,
# 'user_id': ''}

    # # 尾盘清仓
    # if api.is_changing(quote, "datetime"):
    #     now = datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f")
    #     if now.hour == CLOSE_HOUR and now.minute >= CLOSE_MINUTE:  # 到达平仓时间: 平仓
    #         print("临近本交易日收盘: 平仓")
    #         target_pos_value = 0  # 平仓
    #         # target_pos.set_target_volume(0)
    #         pivot = bBreak = sSetup = sEnter = bEnter = bSetup = sBreak = float("nan")  # 修改各指标线的值, 避免平仓后再次触发
    #
    # '''交易规则'''
    # if api.is_changing(quote, "last_price"):
    #     print("最新价: %f" % quote.last_price)
    #
    #     # 止损: 开仓价与当前行情价之差大于止损点则止损
    #     if (target_pos_value > 0 and open_position_price - quote.last_price >= STOP_LOSS_PRICE) or \
    #             (target_pos_value < 0 and quote.last_price - open_position_price >= STOP_LOSS_PRICE):
    #         target_pos_value = 0  # 平仓
    #         # target_pos.set_target_volume(0)
    #
    #     # 反转:
    #     if target_pos_value > 0:  # 多头持仓
    #         if quote.highest > sSetup and quote.last_price < sEnter:
    #             # 多头持仓,当日内最高价超过观察卖出价后，
    #             # 盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，
    #             # 采取反转策略，即在该点位反手做空
    #             print("多头持仓,当日内最高价超过观察卖出价后跌破反转卖出价: 反手做空")
    #             target_pos_value = -3  # 做空
    #             # target_pos.set_target_volume(-3)
    #             open_position_price = quote.last_price
    #     elif target_pos_value < 0:  # 空头持仓
    #         if quote.lowest < bSetup and quote.last_price > bEnter:
    #             # 空头持仓，当日内最低价低于观察买入价后，
    #             # 盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，
    #             # 采取反转策略，即在该点位反手做多
    #             print("空头持仓,当日最低价低于观察买入价后超过反转买入价: 反手做多")
    #             target_pos_value = 3  # 做多
    #             # target_pos.set_target_volume(3)
    #             open_position_price = quote.last_price
    #
    #     # 突破:
    #     elif target_pos_value == 0:  # 空仓条件
    #         if quote.last_price > bBreak:
    #             # 在空仓的情况下，如果盘中价格超过突破买入价，
    #             # 则采取趋势策略，即在该点位开仓做多
    #             print("空仓,盘中价格超过突破买入价: 开仓做多")
    #             target_pos_value = 3  # 做多
    #             # target_pos.set_target_volume(3)
    #             open_position_price = quote.last_price
    #         elif quote.last_price < sBreak:
    #             # 在空仓的情况下，如果盘中价格跌破突破卖出价，
    #             # 则采取趋势策略，即在该点位开仓做空
    #             print("空仓,盘中价格跌破突破卖出价: 开仓做空")
    #             target_pos_value = -3  # 做空
    #             # target_pos.set_target_volume(-3)
    #             open_position_price = quote.last_price
    #
    #             api.query_quotes()