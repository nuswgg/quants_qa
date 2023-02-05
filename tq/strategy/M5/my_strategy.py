# !/usr/bin/env python
#  -*- coding: utf-8 -*-
import sys
from tqsdk.ta import MA, EMA
from tqsdk.tafunc import ma, ema, abs, std, hhv, llv, count, time_to_datetime, barlast
from numpy.lib.stride_tricks import as_strided as stride
from my_func import *
import pandas as pd
import numpy as np

# sys.path.append('D:\\BaiduNetdiskDownload\\Quants\\tq\\strategy\\M5')
multiZF = 8  # 均线靠拢的放到系数 [1,30] %10 - 300%
inc_body1_4 = 4  # ma_kl1_4 4均线靠拢 增量参数  base 10 5就是增加50%
inc_body1_3 = 4  # ma_kl1_3 3均线靠拢 增量参数  base 10 5就是增加50%
s_para = 13 # para for short
m_para = 33 # para for medium
l_para = 71 # para for large

def get_short_trend(kline):
    pass


def get_direction(kline):
    return 1 if kline.close >= kline.open else -1


def get_cdl_body_h(kline):  # decide open/close for predction
    return kline.open if kline.open >= kline.predict_c else kline.predict_c


def get_cdl_body_l(kline):
    return kline.open if kline.open < kline.predict_c else kline.predict_c


def get_up_only(klines, n):
    if n is null:
        n = 20
    t = klines[-n:]
    temp = t[t > 0]
    if len(temp) == 0:
        return 0
    else:
        return ema(temp, len(temp))[-1:]

def not_trend(kline):
    pass

def get_non_trend(kline):
    """
    对震荡阶段进行 进一步的分类
    临界:均线聚合 & 价格聚合
    超买:
        均线聚合
            空头趋势
            多头趋势
        均线没有集合
            空头趋势
            多头趋势
    超卖:
        均线聚合
            空头趋势
            多头趋势
        均线没有集合
            空头趋势
            多头趋势
    :param kline:
    :return:
    """
    # if (kline.ma_band1_3 <= kline.non_trend_unit) :
    if kline.non_trend_flag:
        return 'nt'
    # elif ():
    #     return 'nt_over_buy'
    # elif ():
    #     return 'nt_over_sell'
    else:
        return 'other'

def get_exit_signal(kline):
    pass

def get_stop_loss(kline):
    if kline.stage == 'ktqd':
        return 0
    elif kline.stage == 'dtqd':
        return 0
    elif kline.stage == 'ktjs':
        return 0
    elif kline.stage == 'dtjs':
        return 0
    elif kline.stage == 'dtbc':
        return 0
    elif kline.stage == 'ktbc':
        return 0
    elif kline.stage == 'dthc':
        return 0
    elif kline.stage == 'ktfc':
        return 0
    elif kline.stage == 'dtht':
        return 0
    elif kline.stage == 'ktft':
        return 0
    else:
        return 0

##
def stop_loss_final(kline):
    pass

def get_critical_point(kline):
    # if (kline.mv1 > kline.mv3) & (kline.vol_s1>=2):
    if (kline.vol_s1 >= 2) & (kline.bsp_ratio == 2):
        return 2
    # elif (kline.mv1 < kline.mv3) & (kline.vol_s1>2):
    elif (kline.vol_s1 >= 2) & (kline.bsp_ratio == 1):
        return 1
    else:
        return 0

def get_signal(kline):
        """
        仓位管理
        空头启动
            short 初始仓位 半仓, 设止损，不设止盈
        空头加速
            addShort 加仓 50% 则为全仓, 设止损，不设止盈
        ['strategy_name', 'direction', 'cang_wei', 'stop_loss', 'stop_win', 'style']
        style:
            zd
            long
            short
            fantan
            huicai
        bsp_ratio
            如果在趋势市场 bias0<0.4 bsp_ratio>2.1 不需要平仓

        bias 止盈
            qsjs 趋势加速 bias0>1.5% bsp_ratio>2.1 立刻平仓

        """
        ##################################################### 多头趋势类交易 #####################################################
        ##########################
        ######  dtqd 多头启动 ######
        ##########################
        ## 强势上涨回调后 重度bsp  回调近ma0 开重仓long信号 通常为空头转多头，多头大阳袭击， 空头反击无力 博弈点
        if (kline.stage.iloc[-1] == 'dtqd') & (kline.bsp_class.iloc[-1] == 2) & (-1 <= kline.bias0.iloc[-1]) & (kline.bias0.iloc[-1] <= 2) & \
                (kline.slp0.iloc[-1] > 999.90) & (kline.df_01.iloc[-1] > kline.df_12.iloc[-1]) & (kline.zdStrength.iloc[-2] < 0) & \
                (kline.vol_momt.iloc[-1] == 2) & (kline.vol_cp_20d.iloc[-1] >= 1):
            return 'dtqd_byd2', 'BUY', kline.close, 1, kline.close - kline.ma_body - (kline.ma_Us + kline.Ls) / 2, 0, 0

        ##########################
        ######  dtjs 多头加速 ######
        ##########################

        ##################################################### 空头趋势类交易 #####################################################
        ###########################
        ######  ktqd 空头启动 ######
        ###########################
        # 强势下跌反弹后 重度滞涨 靠近ma0 开重仓short信号 通常为多头转空头，空头突袭大阴，多头反攻无力
        elif (kline.stage.iloc[-1] == 'ktqd') & (kline.bsp_class.iloc[-1] == 2) & (-2 <= kline.bias0.iloc[-1]) & (kline.bias0.iloc[-1] <= 1) \
                & (kline.slp0.iloc[-1] < 1000.1) & (kline.df_01.iloc[-1] < kline.df_12.iloc[-1]) & (kline.zdStrength.iloc[-2] < -1) & \
                (kline.vol_momt.iloc[-1] == 2) & (kline.vol_cp_20d.iloc[-1] >= 1):
            return 'ktqd_byd2', 'SELL', kline.close, 1, kline.close + kline.ma_body + (kline.ma_Us + kline.Ls) / 2, 0, 0

        # ## 中度卖压 开半仓信号, 中等滞涨 靠近ma0  以价格设止损 需要跟踪 update stop_loss，不设止盈
        elif (kline.stage.iloc[-1] == 'ktqd') & (kline.bsp_class.iloc[-1] == 1) & (-2 < kline.bias0.iloc[-1]) & (kline.bias0.iloc[-1] <= 1) & \
                (kline.slp0.iloc[-1] <= 1000) & (kline.df_01.iloc[-1] < kline.df_12.iloc[-1]) & (kline.zdStrength.iloc[-2] > 1) & \
                (kline.vol_momt.iloc[-1] == 2) & (kline.vol_cp_20d.iloc[-1] >= 1):
            # & ((kline.zdStrength < kline.zdStrength_prev) | (kline.volume > kline.vol_prev)):
            return 'ktqd_byd1', 'SELL', kline.close, 0.5, kline.close + kline.ma_body + (kline.ma_Us + kline.Ls) / 2, 0, 0

        # #########################
        # ######  ktjs 空头加速 ######
        # #########################
        ## 震荡超卖 重度买压 15/1000=0.015, 1.5% over sell, cang_wei = 0, mean close short, 趋势加速有时效性
        elif ((kline.stage.iloc[-1] == 'ktjs') & (kline.bsp_class.iloc[-1] == 2) & (kline.bias1.iloc[-1] >= -6) & (kline.bias0.iloc[-1] <= -4) \
              & (kline.zdStrength.iloc[-1] < -1.5) & (kline.df_01.iloc[-1] < kline.df_12.iloc[-1]) & (kline.vol_momt.iloc[-1] == 2)):
            return 'ktjs_byd2', 'SELL', kline.close, 1, kline.ma0 * 0.004, kline.ma0 * 0.004, 3
        # # 重度卖压 开重仓信号 加仓 或 全仓信号, <0.7 :  以ma0设止损，不设止盈
        elif (kline.stage.iloc[-1] == 'ktjs') & (kline.bsp_class.iloc[-1] == -1) & (kline.bias1.iloc[-1] >= -4) & (kline.bias1.iloc[-1] <= -9) & \
                (kline.zdStrength.iloc[-1] < -1) & (kline.zdStrength.iloc[-2] < 1) & (-kline.zdStrength.iloc[-1] > kline.zdStrength.iloc[-2]) & \
                (kline.df_01.iloc[-1] < kline.df_12.iloc[-1]) & (kline.slp0.iloc[-1] < kline.slp1.iloc[-1]) \
                & (kline.high.iloc[-1] >= kline.ma0.iloc[-1]) & (kline.vol_momt.iloc[-1] == 2):
            return 'ktqd_s3', 'SELL', kline.close, 1, kline.ma0 + kline.ma_body + kline.ma_Us, 0, 3

        ##################################################### 超卖类交易 #####################################################
        # #震荡超卖 重度买压 15/1000=0.015, 1.5% over sell, cang_wei = 0, mean close short, 趋势加速有时效性
        elif ((kline.stage.iloc[-1] == 'ktqd') & (kline.bsp_class.iloc[-1] == 2) & (kline.bias1.iloc[-1] <= -6) & \
        (kline.zdStrength.iloc[-1] > 0) & (kline.cdlUs.iloc[-1] / kline.ma_Us.iloc[-1] >= 2)):
            temp = kline.close - kline.ma_body - (kline.ma_Us + kline.ma_Ls) / 2
            stop_loss = min(temp, kline.ma0 * 0.003)
            return 'ktjs_os_byd2', 'BUY', kline.close, 0.5, stop_loss, kline.ma0 * 0.004, 3

        # ## 空头加速超卖 重度买卖压，反向开仓 超跌 止跌  此信号 需要确保stop_loss未到跌停
        elif ((kline.stage.iloc[-1] == 'ktjs') & (kline.bsp_class.iloc[-1] == 2) & (kline.bias0.iloc[-1] < -15) & (kline.zdStrength.iloc[-2] <= -3)):
            temp = kline.close - kline.ma_body - (kline.ma_Us + kline.ma_Ls) / 2
            stop_loss = min(temp, kline.ma0 * 0.003)
            return 'ktjs_b1', 'BUY', kline.close, 0.5, kline.close - kline.ma_body - (
                        kline.ma_Us + kline.ma_Ls) / 2, kline.close * 0.006, 0

        ##################################################### 超买类交易 #####################################################
        # elif (kline.stage.iloc[-1] == 'jmkt') & (kline.bsp_class.iloc[-1] == 2) & (kline.net_strength_1_s.iloc[-1]>0) & (kline.pct_chg.iloc[-1] > 2)

        ##################################################### 震荡类做多 #####################################################

        ##################################################### 震荡类做空 #####################################################

        ##################################################### 平仓类交易 #####################################################
        # ## 绝对止盈 空头加速 急速下跌 大幅偏离 立即止盈 不开反手
        elif (kline.stage.iloc[-1] == 'ktjs') & (kline.bias0.iloc[-1] < -15) & (kline.vol_cp.iloc[-1] == 2):
            return 'ktjs_b2', 'BUY', kline.close, 0, 0, 0, 0

        # ## 空头加速 急速下跌 未到超卖 出现重度买卖压 之需要调低止损 而不需要平仓
        # ## 急速下跌 止损0.5% 快速下跌 止损 0.4% 慢速下跌 0.3%
        # elif (kline.stage == 'ktjs') & (kline.ma_slp0 < 998)  & (kline.bsp_class == 2):
        #     return 'ktjs_kp','noAction', 0, 0, kline.close*1.005, 0, 0
        # ## 空头加速 重度卖压
        # elif (kline.stage == 'ktjs') & (kline.bsp_class == 2) & (-2< kline.bias0) & (kline.bias0 < 1):
        #     return 'ktjs_s1', 'SELL', kline.close, 1, kline.close + kline.ma_body + (kline.ma_Us + kline.ma_Ls)/2, 0, 0
        # ## 空头加速 中度卖压
        # elif (kline.stage == 'ktjs') & (kline.bsp_class == 1) & (-2< kline.bias0) & (kline.bias0 < 1):
        #     return 'ktjs_s2','SELL', kline.close, 0.5, 0, 0, 0
        # # 空头加速 急速下跌  快速反弹， 做空 止损 0.5% 止盈 1.1%
        # elif (kline.stage == 'ktjs') & (kline.ma_slp0 < 998) :
        #     return 'ktjs_s3', 'SELL', kline.predict_ma0, 0.5, kline.predict_ma0*1.005, kline.predict_ma0*0.989, 0
        # #########################
        # ######  dtjs 多头加速 ######
        # #########################
        # elif (kline.stage == 'dtjs') & kline.jl & (kline.bsp_class == 2) & (kline.bias0 <= 5) & (kline.)
        #     return 'jmklzd','noAction',0, 0, 0, 0, 0

        # ###############################
        # ######  dtbc 多头保持（减弱）######
        # ###############################
        # ## 多头保持，大周期是反弹
        # elif (kline.stage == 'dtbc') & kline.dl & (kline.bsp_class == 2) & (kline.ma_slp0 <= kline.ma_slp1) & (kline.cdlUs > kline.ma_Us * 2) \
        #         & (kline.bias0 < 3):
        #     return 'dtbc_s1', 'SELL', kline.close*1.0008, 0.5, kline.close*1.0008 + kline.ma_body + (kline.ma_Us + kline.ma_Ls)/2, 0

        # ###########################
        # ######  jmkl 紧密靠拢 ######
        # ###########################
        # #紧密靠拢 重度买卖压 超卖 LH_SIGNAL: JMKL_OS
        # elif kline.jmkl & (kline.slp1 >= 999) & (kline.bias1 <= -4) & (kline.bsp_class == 2) & kline.last_k_fl:
        #     return 'jmkl_os', 'BUY', kline.close, 0.5, kline.close*0.997, kline.close*1.004, 0

        # # 紧密靠拢 重度买卖压 超买 LH_SIGNAL: JMKL_OB
        # elif kline.jmkl & (kline.slp1 <=1001) & (kline.bias1 >=4) & (kline.bsp_class == 2) \
        #         & kline.last_k_fl & (kline.zdStrength <= 1) & (kline.mv1 <= kline.mv3*1.1) & (kline.dl_5d < 2):
        #     return 'jmkl_ob', 'SELL', kline.close, 0.5, kline.close*1.003, kline.close*0.996

        # #####################
        # ######  jmklzd ######
        # #####################
        # # # 放量
        # elif (kline.stage == 'jmklzd') & (kline.jltj >= 1) & (kline.dltj >= 2) & (kline.mv1 > kline.mv3):
        #     return 'jmklzd','noAction',0, 0, 0, 0, 0

        # #####################
        # ######  ssklpd ######
        # #####################
        # ## 松散多头偏多 准备突破
        # elif (kline.stage == 'ssklpd') & (kline.slp3 >= 1000) & (kline.slp2 >= 1000) & (kline.bsp_class == 1):
        #     return 'ssklpd_brk','BUY',  kline.close, 0.5, kline.close - kline.ma_body - (kline.ma_Us + kline.ma_Ls)/2, 0
        # ## 松散靠拢多头 回踩ma3 ma4为参考 多头回调
        # elif (kline.stage == 'ssklpd') & (kline.slp3 >= 1000) & (kline.slp2 >= 1000) & (-1 <= kline.bias3) & (kline.bias3 < 1) \
        #         & (kline.df_23 < kline.df_34) & (kline.df_23 > kline.ma3*0.005):
        #     return 'ssklpd_ht','BUY',kline.close, 1, kline.close - kline.ma_body - (kline.ma_Us + kline.ma_Ls)/2, 0
        # #####################
        # ######  ssklpk ######
        # #####################
        # # elif :
        else:
            return 'noStage', np.nan, 0, 0, 0, 0, 0


def long_(kline):
    if (kline.bias0 <= 1):
        return ['s', 0.5, kline.close + kline.ma_body + kline.ma_Us]
    else:
        return 'n', 0, 0, 0


def stop_loss_style(kline):
    # 和信号同时产生的 stop_loss, 进行调整后的stop_loss_filled
    # 绝对止盈
    #
    pass

def get_bsp_class(kline):
    ##重度买卖压
    if kline.bsp_ratio >= 2.1:
        return 2
    ##中度买卖压
    elif kline.bsp_ratio >= 1.4:
        return 1
    ## 强买压或强卖压
    elif (kline.bsp_ratio <= 0.7) & ((kline.zdStrength > 1.5) | (kline.zdStrength < -1.5)):
        return -1
    else:
        return 0

def get_top1_net_strength(klines):
    temp = klines.sort_values()
    top1 = temp.iloc[-1] + temp.iloc[0]
    return top1


def get_top2_net_strength(klines):
    temp = klines.sort_values()
    top1 = temp.iloc[-1] + temp.iloc[0]
    top2 = top1 + temp.iloc[-2] + temp.iloc[1]
    return top2

def get_top3_net_strength(klines):
    temp = klines.sort_values()
    top1 = temp.iloc[-1] + temp.iloc[0]
    top2 = top1 + temp.iloc[-2] + temp.iloc[1]
    top3 = top2 + temp.iloc[-3] + temp.iloc[2]
    return top3

def get_top1_long_strength(klines):
    temp = klines.sort_values()
    return temp.iloc[-1]

def get_top1_short_strength(klines):
    temp = klines.sort_values()
    return temp.iloc[0]

def get_top_long(klines):
    temp = klines.sort_values()
    return temp.iloc[-1]

def get_top_short(klines):
    temp = klines.sort_values()
    return temp.iloc[0]


# if ((kline.vol_s3 <= 1) & (kline.vol_s3>=0.7)) |\
#         ((kline.mv13_r > 1.4) & (kline.vol_s3<=0.7)) |\
#         ((kline.mv23_r > 1.2) & (kline.vol_s3<=0.7)):
#     return 1


def get_vol_momt(kline):
    # if (kline.vol_s1 >= 2) | (kline.vol_s3>1.6) | \
    if ((kline.mv13_r >= 1) & (kline.mv13_r <= 1.3) & (kline.vol_s3 >= 1.3)) | \
            ((kline.mv13_r >= 1.3) & (kline.vol_s3 >= 1)) | \
            ((kline.mv23_r >= 1) & (kline.mv23_r <= 1.2) & (kline.vol_s3 >= 1.2)) | \
            ((kline.mv23_r >= 1.2) & (kline.vol_s3 >= 1)) | \
            (kline.vol_s3 >= 1.6):
        return 2
    elif ((kline.mv13_r < 1) & (kline.mv13_r >= 0.7) & (kline.vol_s3 > 1)) | \
            ((kline.mv13_r > 1) & (kline.mv13_r < 1.3) & (kline.vol_s3 > 0.7)) | \
            ((kline.mv23_r <= 1) & (kline.mv23_r >= 0.8) & (kline.vol_s2 > 1)) | \
            ((kline.mv23_r >= 1) & (kline.mv23_r <= 1.2) & (kline.vol_s2 > 0.8)) | \
            ((kline.mv13_r >= 1.3) & (kline.vol_s3 <= 1)) | \
            ((kline.mv23_r >= 1.2) & (kline.vol_s3 <= 1)) | \
            (kline.vol_s3 >= 1):
        return 1
    else:
        return 0

def classify_ma13_df(kline):
    if (kline.ma_band1_3 <= kline.ma3*0.001):
        return 'ma13_df_1'
    elif (kline.ma_band1_3 <= kline.ma3*0.002):
        return 'ma13_df_2'
    elif (kline.ma_band1_3 <= kline.ma3*0.004):
        return 'ma13_df_4'
    else:
        return 'ma13_df_inf'

def classify_ma02_df(kline):
    if (kline.ma_band0_2 <= kline.ma2*0.001):
        return 'ma02_df_1'
    elif (kline.ma_band0_2 <= kline.ma2*0.002):
        return 'ma02_df_2'
    elif (kline.ma_band0_2 <= kline.ma2*0.004):
        return 'ma02_df_4'
    else:
        return 'ma02_df_inf'

def classify_ma24_df(kline):
    if (kline.ma_band2_4 <= kline.ma4*0.001):
        return 'ma02_df_1'
    elif (kline.ma_band0_2 <= kline.ma2*0.002):
        return 'ma02_df_2'
    elif (kline.ma_band0_2 <= kline.ma2*0.004):
        return 'ma02_df_4'
    else:
        return 'ma02_df_inf'

def get_stage(kline):
    if (kline.dtxt & (kline.ma_2_slp0 >= 1000) & (kline.bias1 >= 1)):
        return 'dtjg'  # 多头进攻
    elif kline.dtxt & (kline.ma_2_slp0 < 1000) & (kline.bias1 > 1):
        return 'dttz'  # 多头调整
    elif kline.dtxt & (kline.bias4 >= -0.5) & (kline.bias4 <= 1):
        return 'cai_ma4'  # 踩ma4
    elif kline.dtxt & (kline.bias3 >= -0.5) & (kline.bias3 <= 1):
        return 'cai_ma3'  # 踩ma3
    elif kline.dtxt & (kline.bias2 >= -0.5) & (kline.bias2 <= 1):
        return 'cai_ma2'  # 踩ma2
    elif kline.dtxt & (kline.bias1 >= -0.5) & (kline.bias1 <= 1):
        return 'cai_ma1'  # 踩ma1
    elif kline.dtxt & (kline.bias3 <= -0.5) & (kline.bias4 >= 1):
        return 'dzj34'  # 多中继34
    elif kline.dtxt & (kline.bias2 <= -0.5) & (kline.bias3 >= 1):
        return 'dzj23'  # 多中继23
    elif kline.dtxt & (kline.bias1 <= -0.5) & (kline.bias2 >= 1):
        return 'dzj12'  # 多中继12
    elif kline.dtxt & (kline.bias4 <= -0.5):
        return 'oversell'
    elif kline.ktxt & (kline.ma_2_slp0 <= 1000) & (kline.bias1 < -1):
        return 'ktjg'  # 空头进攻
    elif kline.ktxt & (kline.ma_2_slp0 > 1000) & (kline.bias1 < -1):
        return 'kttz'  # 空头调整
    elif kline.ktxt & (kline.bias4 <= 0.5) & (kline.bias4 >= -1):
        return 'chou_ma4'  # 抽ma4
    elif kline.ktxt & (kline.bias3 <= 0.5) & (kline.bias3 >= -1):
        return 'chou_ma3'  # 抽ma3
    elif kline.ktxt & (kline.bias2 <= 0.5) & (kline.bias2 >= -1):
        return 'chou_ma2'  # 抽ma2
    elif kline.ktxt & (kline.bias1 <= 0.5) & (kline.bias1 >= -1):
        return 'chou_ma1'  # 抽ma1
    elif kline.ktxt & (kline.bias3 >= 0.5) & (kline.bias4 <= -1):
        return 'kzj34'  # 空中继34
    elif kline.ktxt & (kline.bias2 >= 0.5) & (kline.bias3 <= -1):
        return 'kzj23'  # 空中继23
    elif kline.ktxt & (kline.bias1 >= 0.5) & (kline.bias2 <= -1):
        return 'kzj12'  # 空中继12
    elif kline.ktxt & (kline.bias4 >= 0.5):
        return 'overbuy'
    else:
        return 'others'

    # elif kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 >= 0):
    #     return 'jin_dtjg'  # 紧 多头进攻
    # elif kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 <= 0):
    #     return 'jin_dtht'  # 紧 多头回调
    # elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 <= 0):
    #     return 'jin_ktjg'  # 紧 空头进攻
    # elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 >= 0):
    #     return 'jin_ktht'  # 紧 空头回调
    # elif kline.jmkl & (kline.bias4 >= -0.5) & (kline.bias4 <= 0.5):
    #     return 'jin_tiema4' #贴ma4
    # elif kline.jmkl & (kline.bias3 >= -0.5) & (kline.bias3 <=0.5):
    #     return 'jin_tiema3'
    # elif kline.jmkl & (kline.bias2 >= -0.5) & (kline.bias2 <= 0.5):
    #     return 'jin_tiema2'
    # elif kline.jmkl & (kline.bias1 >= -0.5) & (kline.bias1 <= 0.5):
    #     return 'jin_tiema1'
    # elif kline.jmkl & (((kline.bias3 < -0.5) & (kline.bias4 > 0.5) & (kline.ma3 > kline.ma4)) | ((kline.bias3 > 0.5) & (kline.bias4 < -0.5) & (kline.ma3 < kline.ma4))):
    #     return 'jin_zj34'
    # elif kline.jmkl & (((kline.bias2 < -0.5) & (kline.bias3 > 0.5) & (kline.ma2 > kline.ma3)) | ((kline.bias2 > 0.5) & (kline.bias3 < -0.5) & (kline.ma2 < kline.ma3))):
    #     return 'jin_zj23'
    # elif kline.jmkl & (((kline.bias1 < -0.5) & (kline.bias2 > 0.5) & (kline.ma1 > kline.ma2)) | ((kline.bias1 > 0.5) & (kline.bias2 < -0.5) & (kline.ma1 < kline.ma2))):
    #     return 'jin_zj23'
    # elif kline.jmkl & (kline.max_bias < -0.5):
    #     return 'jin_dzk' #紧密 多转空
    # elif kline.jmkl & (kline.max_bias > 0.5):
    #     return 'jin_kzd' #紧密 空转多
    # else:
    #     return 'others'

def roll(df,w,**kwargs):
    v = df.values
    d0, d1 = v.shape
    s0, s1 = v.strides
    a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))
    rolled_df = pd.concat({
        row:pd.DataFrame(values, columns=df.columns)
        for row, values in zip(df.index, a)
    })
    return rolled_df.groupby(level=0,**kwargs)

def get_dt_stage(kline):
    if kline.dtxt & (kline.ma_2_slp0 >= 1000) & (kline.close >= kline.ma1) :
        return 'dtjg'  # 多头进攻
    elif kline.dtxt & (kline.ma_2_slp0 < 1000) & (kline.bias1 > 1):
        return 'dttz'  #多头调整
    elif kline.dtxt & (kline.bias4 >= -0.5) & (kline.bias4 <= 1):
        return 'cai_ma4' #踩ma4
    elif kline.dtxt & (kline.bias3 >= -0.5) & (kline.bias3 <= 1):
        return 'cai_ma3' #踩ma3
    elif kline.dtxt & (kline.bias2 >= -0.5) & (kline.bias2 <= 1):
        return 'cai_ma2' #踩ma2
    elif kline.dtxt & (kline.bias1 >= -0.5) & (kline.bias1 <= 1):
        return 'cai_ma1' #踩ma1
    elif kline.dtxt & (kline.bias3 <= -0.5) & (kline.bias4 >= 1):
        return 'dzj34' #多中继34
    elif kline.dtxt & (kline.bias2 <= -0.5) & (kline.bias3 >= 1):
        return 'dzj23' #多中继23
    elif kline.dtxt & (kline.bias1 <= -0.5) & (kline.bias2 >= 1):
        return 'dzj12'  # 多中继12
    elif kline.dtxt & (kline.bias4 <= -0.5):
        return 'oversell'
    elif kline.jmkl:
        return 'jmkl'
    else:
        return 'ktxt'

def get_kt_stage(kline):
    if kline.ktxt & (kline.ma_2_slp0 <= 1000) & (kline.close <= kline.ma1):
        return 'ktjg'  # 空头进攻
    elif kline.ktxt & (kline.ma_2_slp0 > 1000) & (kline.bias1 < -1):
        return 'kttz'  # 空头调整
    elif kline.ktxt & (kline.bias4 <= 0.5) & (kline.bias4 >= -1):
        return 'chou_ma4'  # 抽ma4
    elif kline.ktxt & (kline.bias3 <= 0.5) & (kline.bias3 >= -1):
        return 'chou_ma3'  # 抽ma3
    elif kline.ktxt & (kline.bias2 <= 0.5) & (kline.bias2 >= -1):
        return 'chou_ma2'  # 抽ma2
    elif kline.ktxt & (kline.bias1 <= 0.5) & (kline.bias1 >= -1):
        return 'chou_ma1'  # 抽ma1
    elif kline.ktxt & (kline.bias3 >= 0.5) & (kline.bias4 <= -1):
        return 'kzj34'  # 空中继34
    elif kline.ktxt & (kline.bias2 >= 0.5) & (kline.bias3 <= -1):
        return 'kzj23'  # 空中继23
    elif kline.ktxt & (kline.bias1 >= 0.5) & (kline.bias2 <= -1):
        return 'kzj12'  # 空中继12
    elif kline.ktxt & (kline.bias4 >= 0.5):
        return 'overbuy'
    elif kline.jmkl:
        return 'jmkl'
    # else kline.dtxt:
    #     return 'dtxt'

def get_kl_stage(kline):
    if kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 >= 0) :
        return 'jin_dtjg' #紧 多头进攻
    elif kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 <= 0) :
        return 'jin_dtht' #紧 多头回调
    elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 <= 0) :
        return 'jin_ktjg' #紧 空头进攻
    elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 >= 0) :
        return 'jin_ktht' #紧 空头回调
    elif kline.jmkl & (kline.bias4 >= -0.5) & (kline.bias4 <= 0.5):
        return 'jin_tiema4' #贴ma4
    elif kline.jmkl & (kline.bias3 >= -0.5) & (kline.bias3 <=0.5):
        return 'jin_tiema3'
    elif kline.jmkl & (kline.bias2 >= -0.5) & (kline.bias2 <= 0.5):
        return 'jin_tiema2'
    elif kline.jmkl & (kline.bias1 >= -0.5) & (kline.bias1 <= 0.5):
        return 'jin_tiema1'
    elif kline.jmkl & (((kline.bias3 < -0.5) & (kline.bias4 > 0.5) & (kline.ma3 > kline.ma4)) | ((kline.bias3 > 0.5) & (kline.bias4 < -0.5) & (kline.ma3 < kline.ma4))):
        return 'jin_zj34'
    elif kline.jmkl & (((kline.bias2 < -0.5) & (kline.bias3 > 0.5) & (kline.ma2 > kline.ma3)) | ((kline.bias2 > 0.5) & (kline.bias3 < -0.5) & (kline.ma2 < kline.ma3))):
        return 'jin_zj23'
    elif kline.jmkl & (((kline.bias1 < -0.5) & (kline.bias2 > 0.5) & (kline.ma1 > kline.ma2)) | ((kline.bias1 > 0.5) & (kline.bias2 < -0.5) & (kline.ma1 < kline.ma2))):
        return 'jin_zj23'
    elif kline.jmkl & (kline.max_bias < -0.5):
        return 'jin_dzk' #紧密 多转空
    elif kline.jmkl & (kline.max_bias > 0.5):
        return 'jin_kzd' #紧密 空转多
    else:
        return 'other'

def vol_stage(klines):
    if (klines.mv23_r > 1.2) | (klines.mv12_r > 1.3):
        return 'fangliang'
    elif (klines.mv23_r < 0.8) | (klines.mv12_r < 0.7):
        return 'suoliang'
    else:
        return 'normal'

def calc_base_data(klines):
    klinesC = klines.copy()

    ########################### 基础数据 ###########################
    klinesC['vol_prev'] = klinesC.volume.shift(1)
    klinesC['c_prev'] = klinesC.close.shift(1)
    # klinesC['first_k'] =klinesC.apply(first_kline, axis=1)

    # ma series
    klinesC['ma0'] = EMA(klines, 8)  # 多头/空头 加速或进行时  需要用到
    klinesC['ma1'] = EMA(klines, 20)
    klinesC['ma2'] = EMA(klines, 40)
    klinesC['ma3'] = EMA(klines, 60)
    klinesC['ma4'] = EMA(klines, 120)

    # get vol stats
    klinesC['mv1'] = ma(klinesC.volume, 10)
    klinesC['mv2'] = ma(klinesC.volume, 40)
    klinesC['mv3'] = ma(klinesC.volume, 120)

    # 计算斜率
    klinesC['slp0'] = round(klinesC.ma0 / klinesC.ma0.shift(1) * 1000, 2)
    klinesC['slp1'] = round(klinesC.ma1 / klinesC.ma1.shift(1) * 1000, 2)
    klinesC['slp2'] = round(klinesC.ma2 / klinesC.ma2.shift(1) * 1000, 2)
    klinesC['slp3'] = round(klinesC.ma3 / klinesC.ma3.shift(1) * 1000, 2)
    klinesC['slp4'] = round(klinesC.ma4 / klinesC.ma4.shift(1) * 1000, 2)

    # 偏离与位移 计算价格与ma的位置 均线之间的距离
    klinesC['bias0'] = round((klinesC.close / klinesC.ma0 - 1) * 1000, 2)
    klinesC['bias1'] = round((klinesC.close / klinesC.ma1 - 1) * 1000, 2)
    klinesC['bias2'] = round((klinesC.close / klinesC.ma2 - 1) * 1000, 2)
    klinesC['bias3'] = round((klinesC.close / klinesC.ma3 - 1) * 1000, 2)
    klinesC['bias4'] = round((klinesC.close / klinesC.ma4 - 1) * 1000, 2)
    klinesC['df_01'] = klinesC.ma0 - klinesC.ma1
    klinesC['df_12'] = klinesC.ma1 - klinesC.ma2
    klinesC['df_23'] = klinesC.ma2 - klinesC.ma3
    klinesC['df_34'] = klinesC.ma3 - klinesC.ma4

    # 计算K线的特征
    klinesC['pct_chg'] = round(klinesC.close.pct_change() * 1000,2)
    klinesC['zdf'] = klinesC.close - klinesC.close.shift(1)
    klinesC['abs_zdf'] = abs(klinesC.zdf)
    klinesC['cdlBody'] = klinesC.close - klinesC.open
    klinesC['abs_body'] = abs(klinesC.cdlBody)
    klinesC['top_body'] = max(klinesC.close, klinesC.open)
    klinesC['button_body'] = min(klinesC.close, klinesC.open)
    klinesC['pct_body'] = round(klinesC.abs_body / klinesC.c_prev * 1000, 2) #k线实体的振幅
    klinesC['cdlHL'] = klinesC.high - klinesC.low  # k线的 full length = H - L
    klinesC['pct_HL'] = klinesC.cdlHL / klinesC.c_prev * 1000  # K线的振幅
    klinesC['cdlHO'] = klinesC.high - klinesC.open  # 可以作为 多头
    klinesC['cdlHC'] = klinesC.high - klinesC.close  # 可以作为空头
    klinesC['cdlUs'] = klinesC[['cdlHC', 'cdlHO']].min(axis=1)  # 上影线upper shadow
    klinesC['pct_Us'] = klinesC.cdlUs / klinesC.close * 1000  #上影线振幅
    klinesC['cdlLO'] = klinesC.open - klinesC.low  # 可以作为 空头
    klinesC['cdlLC'] = klinesC.close - klinesC.low  #
    klinesC['cdlLs'] = klinesC[['cdlLO', 'cdlLC']].min(axis=1)  # 下影线 lower shadow
    klinesC['pct_Ls'] = klinesC.cdlLs / klinesC.close * 1000 #下影线振幅

    ###############################################################
    # klinesC['body_rng'] = klinesC.bodyU - klinesC.bodyD  # K线 波动range refer to abs_zdf

    # 通过斜率判断空头时：下跌或止跌， 多头: 上涨或滞涨
    # 在空头 slp_r_01<1 则表示加速下跌  slp_r_01>1 则表示 下跌减速 或者反弹
    # 在多头slp_r_01 > 1 则表示上涨加速 在多头slp_r_01<1 则表示 上涨减速 或 下跌
    # klinesC['slp_r_01'] = klinesC.slp0/klinesC.slp1
    # klinesC['slp_r_12'] = klinesC.slp1/klinesC.slp2
    # klinesC['slp_r_23'] = klinesC.slp2/klinesC.slp3

    # Get ma data
    klinesC['ma_Us'] = ma(klinesC.cdlUs, 20) # 获取upper shadow 均值
    klinesC['ma_Ls'] = ma(klinesC.cdlLs, 20) # 获取lower shadow 均值
    klinesC['ma_slp0'] = ma(klinesC.slp0, 4)
    klinesC['ma_slp1'] = ma(klinesC.slp1, 4)
    klinesC['ma_slp2'] = ma(klinesC.slp2, 4)
    klinesC['ma_slp3'] = ma(klinesC.slp3, 4)
    klinesC['ma_2_slp0'] = ma(klinesC.slp0, 2) # 用于判断回调
    klinesC['ma_body'] = ma(abs(klinesC.cdlBody), 20)
    klinesC['ma_bias1'] = ma(abs(klinesC.bias1), 20)  # 获取20日绝对bias1的平均
    klinesC['ma_bias2'] = ma(abs(klinesC.bias2), 20)  # 获取20日绝对bias2的平均

    # 衍生数据
    klinesC['zdStrength'] = klinesC.cdlBody / klinesC.ma_body  # 涨跌力度
    klinesC['longUShadow'] = klinesC.cdlUs / klinesC.ma_body  # 上影
    klinesC['longLShadow'] = klinesC.cdlLs / klinesC.ma_body # 下影

    # 描述交易量
    # 交易量分类 vol strength
    klinesC['vol_s1'] = klinesC.volume / klinesC.mv1.shift(1)
    klinesC['vol_s2'] = klinesC.volume / klinesC.mv2.shift(1)
    klinesC['vol_s3'] = klinesC.volume / klinesC.mv3.shift(1)
    klinesC['mv13_r'] = klinesC.mv1 / klinesC.mv3
    klinesC['mv12_r'] = klinesC.mv1 / klinesC.mv2
    klinesC['mv23_r'] = klinesC.mv2 / klinesC.mv3

    # 巨量
    klinesC['jl_1'] = (klinesC.vol_s3 >= 3)
    klinesC['jltj'] = count(klinesC.jl_1, 20)  # 巨量统计
    klinesC['jl_2'] = klinesC.jl_1 & klinesC.jl_1.shift(1)  # 连续2天放量
    klinesC['jl_3'] = klinesC.jl_2 & klinesC.jl_2.shift(1)  # 连续3天放量

    #定位巨量位置
    klinesC['jl_1_days'] = barlast(klinesC.jl_1 == True)
    klinesC['jl_2_days'] = barlast(klinesC.jl_2 == True)
    klinesC['jl_3_days'] = barlast(klinesC.jl_3 == True)

    # 大量
    klinesC['dl_1'] = ((klinesC.vol_s3 >= 1.8) & (klinesC.vol_s3 < 3))
    klinesC['dltj'] = count(klinesC.dl_1, 20)  # 大量统计
    klinesC['dl_2'] = klinesC.dl_1 & klinesC.dl_1.shift(1)
    klinesC['dl_3'] = klinesC.dl_2 & klinesC.dl_2.shift(1)  # 连续3天放量

    # 定位大量
    klinesC['dl_1_days'] = barlast(klinesC.dl_1 == True)
    klinesC['dl_2_days'] = barlast(klinesC.dl_2 == True)
    klinesC['dl_3_days'] = barlast(klinesC.dl_3 == True)

    # 放量统计
    klinesC['fl_1'] = (klinesC.vol_s3 > 1.2)
    klinesC['fltj'] = count(klinesC.fl_1, 20)
    klinesC['fl_2'] = klinesC.dl_1 & klinesC.fl_1.shift(1)
    klinesC['fl_3'] = klinesC.dl_2 & klinesC.fl_2.shift(1)  # 连续3天放量

    # 定位放量
    klinesC['fl_1_days'] = barlast(klinesC.fl_1 == True)
    klinesC['fl_2_days'] = barlast(klinesC.fl_2 == True)
    klinesC['fl_3_days'] = barlast(klinesC.fl_3 == True)

    # 阶段放量
    # 多转空时 klinesC.jltj >= 2 & klinesC.dltj >= 3
    # 空头保持时  klinesC.jltj >= 1 & klinesC.dltj >= 2
    klinesC['jdfl'] = (klinesC.mv1 > klinesC.mv2) & (klinesC.mv1 > klinesC.mv3) & (
                (klinesC.jltj >= 2) | (klinesC.dltj >= 3))

    # 反攻放量
    klinesC['fgfl'] = (klinesC.mv1 < klinesC.mv3) & (klinesC.volume / klinesC.vol_prev > 2)
    klinesC['dltj'] = count(klinesC.volume / klinesC.mv3 > 1.5, 20)  # 大量统计
    klinesC['fltj'] = count(klinesC.volume / klinesC.mv3 > 1, 20)  # 放量统计
    klinesC['lxfl'] = (klinesC.mv1 > klinesC.mv2) & (klinesC.mv2 > klinesC.mv3) & (
                klinesC.mv1 / klinesC.mv3 > 1.3)  # 连续放量

    ## 获取特征
    # 找到价格均线位置起始
    klinesC['c_gt_ma0_pos'] = barlast(klinesC.bias0 < 0)
    klinesC['c_lt_ma0_pos'] = barlast(klinesC.bias0 > 0)
    klinesC['c_gt_ma1_pos'] = barlast(klinesC.bias1 < 0)
    klinesC['c_lt_ma1_pos'] = barlast(klinesC.bias1 > 0)
    klinesC['c_gt_ma2_pos'] = barlast(klinesC.bias2 < 0)
    klinesC['c_lt_ma2_pos'] = barlast(klinesC.bias2 > 0)
    klinesC['c_gt_ma3_pos'] = barlast(klinesC.bias3 < 0)
    klinesC['c_lt_ma3_pos'] = barlast(klinesC.bias3 > 0)
    klinesC['c_gt_ma4_pos'] = barlast(klinesC.bias4 < 0)
    klinesC['c_lt_ma4_pos'] = barlast(klinesC.bias4 > 0)

    # 计算阳性/阴线的百分比
    klinesC['up_cdl_pct_s'] = count(klinesC.pct_body > 0, s_para) / s_para * 100
    klinesC['dw_cdl_pct_s'] = count(klinesC.pct_body < 0, s_para) / s_para * 100
    klinesC['up_cdl_pct_m'] = count(klinesC.pct_body > 0, m_para) / m_para * 100
    klinesC['dw_cdl_pct_m'] = count(klinesC.pct_body < 0, m_para) / m_para * 100
    klinesC['up_cdl_pct_l'] = count(klinesC.pct_body > 0, l_para) / l_para * 100
    klinesC['dw_cdl_pct_l'] = count(klinesC.pct_body < 0, l_para) / l_para * 100

    # 统计vol与ma的关系
    klinesC['vol_lt_mv1_1'] = count(klinesC.volume < klinesC.mv1, 7)
    klinesC['vol_lt_mv1_2'] = count(klinesC.volume < klinesC.mv1, 13)
    klinesC['vol_lt_mv1_3'] = count(klinesC.volume < klinesC.mv1, 21)
    klinesC['vol_lt_mv2_1'] = count(klinesC.volume < klinesC.mv2, 7)
    klinesC['vol_lt_mv2_2'] = count(klinesC.volume < klinesC.mv2, 13)
    klinesC['vol_lt_mv2_3'] = count(klinesC.volume < klinesC.mv2, 21)
    klinesC['vol_lt_mv3_1'] = count(klinesC.volume < klinesC.mv3, 7)
    klinesC['vol_lt_mv3_2'] = count(klinesC.volume < klinesC.mv3, 13)
    klinesC['vol_lt_mv3_3'] = count(klinesC.volume < klinesC.mv3, 21)

    # ## 获取区间最大量能  参考
    # klinesC['llv_vol_1'] = hhv(klinesC.volume, 7)
    # klinesC['llv_vol_2'] = hhv(klinesC.volume, 13)
    # klinesC['llv_vol_3'] = hhv(klinesC.volume, 21)
    # klinesC['llv_vol_4'] = hhv(klinesC.volume, 34)
    # klinesC['llv_vol_5'] = hhv(klinesC.volume, 55)
    # klinesC['llv_vol_6'] = hhv(klinesC.volume, 89)

    # 计算统计数据
    klinesC['std_bias1'] = std(klinesC.bias1, 20)  # 标准差
    klinesC['std_bias2'] = std(klinesC.bias2, 20)  # 标准差
    klinesC['std_cdl_b'] = std(klinesC.cdlBody, 20)  # K线实体的标准差
    klinesC['std_cdl_f'] = std(klinesC.cdlHL, 20)  # k线长度的标准差
    klinesC['stdCdlB'] = std(klinesC.cdlBody, 20)  # K线实体的标准差
    klinesC['stdCdlF'] = std(klinesC.cdlHL, 20)  # k线长度的标准差

    ## 形态
    ## 计算突破/破位
    klinesC['rng3D'] = hhv(klinesC.close, 3) - llv(klinesC.close, 3)  # 3日K线实体波动
    klinesC['rng5D'] = hhv(klinesC.close, 5) - llv(klinesC.close, 5)  # 5日K线实体波动
    klinesC['rng7D'] = hhv(klinesC.close, 7) - llv(klinesC.close, 7)  # 7日K线实体波动
    klinesC['rng9D'] = hhv(klinesC.close, 9) - llv(klinesC.close, 9)  # 9日K线实体波动
    klinesC['rng17D'] = hhv(klinesC.close, 17) - llv(klinesC.close, 17)  # 17日K线实体波动

    # klinesC['bRng'] = klinesC['bodyU'] - klinesC['bodyD']  # K线实体range
    klinesC['bRng'] = klinesC[['abs_body', 'abs_zdf']].max(axis=1)

    # 计算买卖压力
    klinesC['abs_body'] = abs(klinesC.cdlBody)
    klinesC['ma_body_off'] = klinesC.ma_body * 0.7
    klinesC['revise_body'] = klinesC[['abs_body', 'ma_body_off']].max(axis=1)
    klinesC['bsp'] = klinesC.volume / klinesC.revise_body
    klinesC['ma_bsp'] = ma(klinesC.bsp, 40)
    klinesC['bsp_ratio'] = klinesC.bsp / klinesC.ma_bsp  # 可以进行分级，然后可以作为开仓或者关仓的信号

    # 获取前一K线数据
    klinesC['zdStrength_prev'] = klinesC.zdStrength.shift(1)

    # get klines pattern
    # 阳包阴
    klinesC['yby'] = (klinesC.zdStrength > 1) & (klinesC.zdStrength.shift(1) < -1) & (
                klinesC.close >= klinesC.open.shift(1)) & \
                     ((klinesC.volume > klinesC.mv2) | (klinesC.volume > klinesC.mv1))
    # 穿头破脚
    klinesC['ctpj'] = (klinesC.zdStrength > 1) & (klinesC.zdStrength.shift(1) < -1) & (
                klinesC.close < klinesC.open.shift(1)) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume > klinesC.mv1))
    # 阴包阳
    klinesC['ybyD'] = (klinesC.zdStrength <= -1) & (klinesC.zdStrength.shift(1) >= 1) & (
                klinesC.close <= klinesC.open.shift(1))
    # 乌云盖顶
    klinesC['wygd'] = (klinesC.zdStrength <= -1) & (klinesC.zdStrength.shift(1) >= 1) & (
                klinesC.close > klinesC.open.shift(1))
    # 突破N天，N为3，5，7
    klinesC['tp3D'] = (klinesC.bRng >= klinesC.rng3D) & (abs(klinesC.zdStrength) > 1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.shift(1) > 1.6) & (
                                  klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp3D==True]
    klinesC['tp5D'] = (klinesC.bRng >= klinesC.rng5D) & (abs(klinesC.zdStrength) > 1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.shift(1) > 1.6) & (
                                  klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp5D==True]
    klinesC['tp7D'] = (klinesC.bRng >= klinesC.rng7D) & (abs(klinesC.zdStrength) > 1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.shift(1) > 1.6) & (
                                  klinesC.volume > klinesC.mv1))
    klinesC['tp17D'] = (klinesC.bRng >= klinesC.rng17D.shift(1)) & (abs(klinesC.zdStrength) > 1.5) & \
                       ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.shift(1) > 1.6) & (
                                   klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp7D == True]
    #  predict close: 用来判断趋势是否加速 (需要配合量能来分析)
    klinesC['predict_ma0'] = klinesC.ma0.shift(1) * klinesC.slp0.shift(1) / 1000
    klinesC['predict_c'] = (klinesC.predict_ma0 - klinesC.ma0.shift(1) * 7 / 9) * 9 / 2

    # 定义多头 / 空头的spacer
    # klinesC['dk_spacer'] = klinesC.ma_body
    klinesC['non_trend_unit'] = klinesC.ma3 * 0.002

    #获取最大或最小
    # ma0-ma2
    klinesC['min_ma0_2'] = klinesC[['ma0', 'ma1', 'ma2']].min(axis=1)
    klinesC['max_ma0_2'] = klinesC[['ma0', 'ma1', 'ma2']].max(axis=1)
    klinesC['ma_band0_2'] = klinesC.max_ma0_2 - klinesC.min_ma0_2
    # ma1-ma3
    klinesC['min_ma1_3'] = klinesC[['ma1', 'ma2', 'ma3']].min(axis=1)  # 3均线
    klinesC['max_ma1_3'] = klinesC[['ma1', 'ma2', 'ma3']].max(axis=1)  # 3均线
    klinesC['ma_band1_3'] = klinesC.max_ma1_3 - klinesC.min_ma1_3
    # ma2-ma4
    klinesC['min_ma2_4'] = klinesC[['ma2', 'ma3', 'ma4']].min(axis=1)  # 3均线
    klinesC['max_ma2_4'] = klinesC[['ma2', 'ma3', 'ma4']].max(axis=1)  # 3均线
    klinesC['ma_band2_4'] = klinesC.max_ma2_4 - klinesC.min_ma2_4

    klinesC['max_bias'] = klinesC[['bias1','bias2','bias3','bias4']].max(axis=1)
    klinesC['min_bias'] = klinesC[['bias1','bias2','bias3','bias4']].min(axis=1)

    # klinesC['kl_base_ref'] = klinesC.ma2 * 0.0001 # 此指标避免极端窄幅波动
    # klinesC['kl1_3_thresh'] = klinesC[['ma_body','kl_base_ref']].max(axis=1) * (10 + inc_body1_3) / 10 # 4均线靠拢的阈值
    # klinesC['non_trend'] = klinesC.ma_band1_3 <= klinesC.non_trend_unit  # 3 均线
    # klinesC['ma_min1_4'] = klinesC[['ma1', 'ma2', 'ma3', 'ma4']].min(axis=1)  # 4均线
    # klinesC['ma_max1_4'] = klinesC[['ma1', 'ma2', 'ma3', 'ma4']].max(axis=1)  # 4均线
    # klinesC['ma_band1_4'] = klinesC['ma_max1_4'] - klinesC['ma_min1_4']  # 4均线
    # klinesC['kl1_4_thresh'] = klinesC[['ma_body','kl_base_ref']].max(axis=1) * (10 + inc_body1_4) / 10  # 4均线靠拢的阈值
    # klinesC['ma_kl1_4'] = klinesC.ma_band1_4 <= klinesC.kl1_4_thresh  # 4均线

    ## 获取区间最大量能
    klinesC['llv_vol_1'] = hhv(klinesC.volume, 7)
    klinesC['llv_vol_2'] = hhv(klinesC.volume, 13)
    klinesC['llv_vol_3'] = hhv(klinesC.volume, 21)
    klinesC['llv_vol_4'] = hhv(klinesC.volume, 34)
    klinesC['llv_vol_5'] = hhv(klinesC.volume, 55)
    klinesC['llv_vol_6'] = hhv(klinesC.volume, 89)

    # 定位最大量能位置
    klinesC['llv_vol_1_days'] = barlast(klinesC.volume == klinesC.llv_vol_1.iloc[-2])
    klinesC['llv_vol_2_days'] = barlast(klinesC.volume == klinesC.llv_vol_2.iloc[-2])
    klinesC['llv_vol_3_days'] = barlast(klinesC.volume == klinesC.llv_vol_3.iloc[-2])
    klinesC['llv_vol_4_days'] = barlast(klinesC.volume == klinesC.llv_vol_4.iloc[-2])
    klinesC['llv_vol_5_days'] = barlast(klinesC.volume == klinesC.llv_vol_5.iloc[-2])
    klinesC['llv_vol_6_days'] = barlast(klinesC.volume == klinesC.llv_vol_6.iloc[-2])

    # 区间多空对比: 获取多空最强力度
    klinesC['llv_pct_body_s'] = llv(klinesC.pct_body, s_para)
    klinesC['llv_pct_body_m'] = llv(klinesC.pct_body, m_para)
    klinesC['llv_pct_body_l'] = llv(klinesC.pct_body, l_para)
    klinesC['hhv_pct_body_s'] = hhv(klinesC.pct_body, s_para)
    klinesC['hhv_pct_body_m'] = hhv(klinesC.pct_body, m_para)
    klinesC['hhv_pct_body_l'] = hhv(klinesC.pct_body, l_para)

    # 定位最大多空K线
    # klinesC['llv_pct_body_days_s'] = barlast(klinesC.pct_body == klinesC.llv_pct_body_s.iloc[-2:-1]) ##not working

    klinesC['llv_pct_body_days_s'] = barlast(klinesC.pct_body == klinesC.llv_pct_body_s.iloc[-2])
    klinesC['llv_pct_body_days_m'] = barlast(klinesC.pct_body == klinesC.llv_pct_body_m.iloc[-2])
    klinesC['llv_pct_body_days_l'] = barlast(klinesC.pct_body == klinesC.llv_pct_body_l.iloc[-2])
    klinesC['hhv_pct_body_days_s'] = barlast(klinesC.pct_body == klinesC.hhv_pct_body_s.iloc[-2])
    klinesC['hhv_pct_body_days_m'] = barlast(klinesC.pct_body == klinesC.hhv_pct_body_m.iloc[-2])
    klinesC['hhv_pct_body_days_l'] = barlast(klinesC.pct_body == klinesC.hhv_pct_body_l.iloc[-2])

    ## 急速区间多空力度
    klinesC['net_strength_1_s'] = klinesC.hhv_pct_body_s - klinesC.llv_pct_body_s
    klinesC['net_strength_1_m'] = klinesC.hhv_pct_body_m - klinesC.llv_pct_body_m
    klinesC['net_strength_1_l'] = klinesC.hhv_pct_body_l - klinesC.llv_pct_body_l
    klinesC['net_strength_2_s'] = klinesC.pct_body.rolling(s_para, 4).apply(get_top2_net_strength)
    klinesC['net_strength_2_m'] = klinesC.pct_body.rolling(m_para, 4).apply(get_top2_net_strength)
    klinesC['net_strength_2_l'] = klinesC.pct_body.rolling(l_para, 4).apply(get_top2_net_strength)

    ## 均线形态
    klinesC['ktpl'] = ((klinesC.ma1 <= klinesC.ma2) & (klinesC.ma2 <= klinesC.ma3))  # 空头排列 ma1,2,3
    klinesC['dtpl'] = ((klinesC.ma1 >= klinesC.ma2) & (klinesC.ma2 >= klinesC.ma3))  # 多头排列 ma1,2,3
    klinesC['ktpl_s'] = ((klinesC.ma0 <= klinesC.ma1) & (klinesC.ma1 <= klinesC.ma2)) # 空头排列 ma0,1,2
    klinesC['dtpl_s'] = ((klinesC.ma0 >= klinesC.ma1) & (klinesC.ma1 >= klinesC.ma2)) # 多头排列 ma0,1,2
    klinesC['ktpl_l'] = ((klinesC.ma2 <= klinesC.ma3) & (klinesC.ma3 <= klinesC.ma4)) # 空头排列 ma2,3,4
    klinesC['dtpl_l'] = ((klinesC.ma2 >= klinesC.ma3) & (klinesC.ma3 >= klinesC.ma4)) # 多头排列 ma2,3,4
    klinesC['ktpl_days'] = barlast(klinesC.ktpl == False)
    klinesC['dtpl_days'] = barlast(klinesC.dtpl == False)
    klinesC['ktpl_days_s'] = barlast(klinesC.ktpl_s == False)
    klinesC['dtpl_days_s'] = barlast(klinesC.dtpl_s == False)
    klinesC['ktpl_days_l'] = barlast(klinesC.ktpl_l == False)
    klinesC['dtpl_days_l'] = barlast(klinesC.dtpl_l == False)

    # 定义均线排列类型
    klinesC['ktxt'] = (klinesC.ktpl & (klinesC.ma_band1_3 >= klinesC.ma3 * 0.002))  # 空头形态
    klinesC['dtxt'] = (klinesC.dtpl & (klinesC.ma_band1_3 >= klinesC.ma3 * 0.002))  # 多头形态
    klinesC['jmkl'] = (klinesC.ma_band1_3 <= klinesC.ma3 * 0.002)  # 均线 紧密靠拢
    klinesC['sskl'] = (klinesC.ma3 * 0.002 <= klinesC.ma_band1_3) & (klinesC.ma_band1_3 <= klinesC.ma3 * 0.004)  # 松散靠拢
    klinesC['long_tran_short'] = (klinesC.dtpl==False) & (klinesC.ktpl==False) & (klinesC.df_34 > 0)
    klinesC['short_tran_long'] = (klinesC.dtpl==False) & (klinesC.ktpl==False) & (klinesC.df_34 < 0)

    # 计算价格大于均线的 百分比
    klinesC['gt_ma0_pct_s'] = count(klinesC.bias0 > 0, s_para) / s_para * 100
    klinesC['gt_ma1_pct_s'] = count(klinesC.bias1 > 0, s_para) / s_para * 100
    klinesC['gt_ma2_pct_s'] = count(klinesC.bias2 > 0, s_para) / s_para * 100
    klinesC['gt_ma3_pct_s'] = count(klinesC.bias3 > 0, s_para) / s_para * 100
    klinesC['gt_ma4_pct_s'] = count(klinesC.bias4 > 0, s_para) / s_para * 100

    klinesC['gt_ma0_pct_m'] = count(klinesC.bias0 > 0, m_para) / m_para * 100
    klinesC['gt_ma1_pct_m'] = count(klinesC.bias1 > 0, m_para) / m_para * 100
    klinesC['gt_ma2_pct_m'] = count(klinesC.bias2 > 0, m_para) / m_para * 100
    klinesC['gt_ma3_pct_m'] = count(klinesC.bias3 > 0, m_para) / m_para * 100
    klinesC['gt_ma4_pct_m'] = count(klinesC.bias4 > 0, m_para) / m_para * 100

    klinesC['gt_ma0_pct_l'] = count(klinesC.bias0 > 0, l_para) / l_para * 100
    klinesC['gt_ma1_pct_l'] = count(klinesC.bias1 > 0, l_para) / l_para * 100
    klinesC['gt_ma2_pct_l'] = count(klinesC.bias2 > 0, l_para) / l_para * 100
    klinesC['gt_ma3_pct_l'] = count(klinesC.bias3 > 0, l_para) / l_para * 100
    klinesC['gt_ma4_pct_l'] = count(klinesC.bias4 > 0, l_para) / l_para * 100

    ## clean data
    klinesC.fillna(method='bfill', inplace=True)

    # 量能获取人气
    klinesC['vol_momt'] = klinesC.apply(get_vol_momt, axis=1)
    klinesC['vol_stage'] = klinesC.apply(vol_stage, axis=1)
    klinesC['vol_cp'] = klinesC.apply(get_critical_point, axis=1)
    klinesC['vol_cp_20d'] = count(klinesC.vol_cp == 2, 20)
    klinesC['vol_cp_30d'] = count(klinesC.vol_cp == 2, 30)

    # 统计
    klinesC['v20_2_pct'] = count(klinesC.vol_momt == 2, 20)*5
    klinesC['v20_1_pct'] = count(klinesC.vol_momt == 1, 20)*5
    klinesC['v20_0_pct'] = count(klinesC.vol_momt == 0, 20)*5
    klinesC['last_v_2'] = barlast(klinesC.vol_momt == 2)
    klinesC['last_v_1'] = barlast(klinesC.vol_momt == 1)

    ##对买卖压进行分类
    klinesC['bsp_class'] = klinesC.apply(get_bsp_class, axis=1)
    klinesC['dl_5d'] = count(klinesC.vol_s3 > 1.8, 5)

    ## get trend stage
    klinesC['ma02_df'] = klinesC.apply(classify_ma02_df, axis=1)
    klinesC['ma13_df'] = klinesC.apply(classify_ma13_df, axis=1)
    klinesC['stage'] = klinesC.apply(get_stage, axis=1)

    ## get non-trend stage
    # klinesC['non_trend_stage'] = klinesC.apply(get_non_trend, axis=1)

    # 准备前K数据
    klinesC['last_stage'] = klinesC.stage.shift(1)
    klinesC['last_momt'] = klinesC.vol_momt.shift(1)
    ## get signal
    # abs_stop_win 无条件止盈
    # rolling cannot be used in multiple columns
    # base[['strategy_name', 'direction', 'limit_price', 'cang_wei', 'stop_loss', 'stop_win_1', 'time_limit']]  = klinesC.rolling(2).apply(get_signal, axis=1,result_type="expand")
   # has to use user defined func
    # roll(basedata, 3).apply(get_signal)
    # klinesC[['strategy_name', 'direction', 'limit_price', 'cang_wei', 'stop_loss', 'stop_win_1', 'time_limit']] = klinesC.apply(get_signal, axis=1,result_type="expand")
    # base[['strategy_name', 'direction', 'limit_price', 'cang_wei', 'stop_loss', 'stop_win_1', 'time_limit']]  = basedata.apply(get_signal, axis=1,result_type="expand")
    # base[['strategy_name', 'direction', 'limit_price', 'cang_wei', 'stop_loss', 'stop_win_1', 'time_limit']]  = basedata.rolling(2).apply(get_signal, axis=1,result_type="expand")
    ## 定义Strategy
    # klinesC['s001'] = (klinesC.yby == True) & (klinesC.ma_kl1_3 == True)

    return klinesC


    # klinesC['top_1_short_s'] = llv(klinesC.pct_body, s_para)
    # klinesC['top_1_short_m'] = llv(klinesC.pct_body, m_para)
    # klinesC['top_1_short_l'] = llv(klinesC.pct_body, l_para)
    # klinesC['top_1_long_s'] = hhv(klinesC.pct_body, s_para)
    # klinesC['top_1_long_m'] = hhv(klinesC.pct_body, m_para)
    # klinesC['top_1_long_l'] = hhv(klinesC.pct_body, l_para)

    # klinesC['net_strength_2_s'] = klinesC.cdlBody.rolling(12, 4).apply(get_top2_net_strength)
    # klinesC['net_strength_2_m'] = klinesC.cdlBody.rolling(33, 4).apply(get_top2_net_strength)
    # klinesC['net_strength_2_l'] = klinesC.cdlBody.rolling(60, 4).apply(get_top2_net_strength)
    # klinesC['top_1_l_s'] = klinesC.pct_chg.rolling(12, 4).apply(get_top1_long_strength)
    # klinesC['top_1_s_s'] = klinesC.pct_chg.rolling(12, 4).apply(get_top1_short_strength)
    # klinesC['top_1_l_m'] = klinesC.pct_chg.rolling(33, 4).apply(get_top1_long_strength)
    # klinesC['top_1_s_m'] = klinesC.pct_chg.rolling(33, 4).apply(get_top1_short_strength)
    # predict hlc
    # klinesC['direction'] = klinesC.apply(lambda row: get_direction(row),axis = 1)
    # klinesC['predict_c'] = klinesC.close.shift(1) + (klinesC.ma_body.shift(1) + abs(klinesC.cdlBody.shift(1)))*klinesC.direction.shift(1)/2
    # klinesC['predict_body_h'] = klinesC.apply(lambda row:get_cdl_body_h(row),axis=1)
    # klinesC['predict_body_l'] = klinesC.apply(lambda row:get_cdl_body_l(row),axis=1)
    # klinesC['predict_h'] = klinesC.predict_body_h + (klinesC.cdlU s.shift(1) + klinesC.ma_Us.shift(1))/2
    # klinesC['predict_l'] = klinesC.predict_body_l - (klinesC.cdlLs.shift(1) + klinesC.ma_Ls.shift(1))/2


def max_volume_time(symbol: str, time_period: int):
    kline = api.get_kline_serial(symbol=symbol, duration_seconds=60, data_length=time_period)
    kline_previous_volume = kline[-time_period:]["volume"]
    kline_id = kline_previous_volume.idxmax()
    kline_max_datetime = kline.iloc[kline_id]["datetime"]

    return time_to_datetime(kline_max_datetime)


## old version
# def get_stage(kline):
#     """
#     对多头/空头进行分类
#     多头
#         多头启动
#             ma3*0.002< ma_band1_3 < ma3*0.004
#         多头加速
#             ma_band1_3 >= ma3*0.004 & ma_band1_2 <= ma3*0.004 & ma_band2_3 <= ma3*0.004
#         多头保持
#         多头回踩
#         多头回调
#     空头
#         空头启动
#         空头加速
#         空头保持
#         空头反抽
#         空头反弹
#     紧密靠拢
#         偏多
#         偏空
#         震荡
#     松散靠拢
#         偏多
#         偏空
#         震荡
#     :param kline:
#     :return:
#     """
#     # 多头启动  ((kline.mv1 > kline.mv3) | (kline.mv2 > kline.mv3)) & (kline.jltj >= 2) & (kline.dltj >= 3))  replaced by (kline.vol_momt == 2)
#     ## 量能在博弈区
#     if (kline.dtpl & kline.sskl & (kline.vol_momt >= 1) & (kline.close >= kline.ma1) & (kline.df_12 >= kline.df_23)) \
#             & ((-kline.llv_pct_body_s < kline.hhv_pct_body_s) | (-kline.llv_pct_body_m < kline.hhv_pct_body_m) | (
#             -kline.llv_pct_body_l < kline.hhv_pct_body_l)):
#         return 'dtqd'
#     # 空头启动  (kline.jltj >= 1) & (kline.dltj >= 2)
#     elif (kline.ktpl & kline.sskl & (kline.vol_momt >= 1) & (kline.close <= kline.ma1) & (kline.df_12 <= kline.df_23)) \
#             & ((-kline.llv_pct_body_s > kline.hhv_pct_body_s) | (-kline.llv_pct_body_m > kline.hhv_pct_body_m) | (
#             -kline.llv_pct_body_l > kline.hhv_pct_body_l)):
#         return 'ktqd'
#     # elif kline.dtpl & kline.sskl & :
#
#     # ## 多头中继
#     # elif (kline.ma_band0_2 <= kline.ma3 * 0.004) & (kline.c_gt_ma4_pos >= kline.dtpl_days) & (kline.dtpl_days > 5) & \
#     #         (kline.ma_slp3 >= 1000) & (kline.df_12 < kline.df_23):
#     #     return 'dtzj'
#     # ## 空头中继
#     # elif (kline.ma_band0_2 <= kline.ma3 * 0.004) & (kline.c_lt_ma4_pos >= kline.ktpl_days) & (kline.ktpl_days > 5) & \
#     #         (kline.ma_slp3 <= 1000) & (kline.df_12 > kline.df_23):
#     #     return 'ktzj'
#     # # 多头加速
#     # elif (kline.dtxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 >= kline.slp2) & (kline.slp2 >= 1000)):
#     #     return 'dtjs'
#     # # 空头加速
#     # elif (kline.ktxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 <= kline.slp2) & (kline.slp2 <= 1000)):
#     #     return 'ktjs'
#     # # 多头保持/减弱
#     # elif (kline.dtxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 <= kline.slp2) & (kline.slp1 >= 1000)):
#     #     return 'dtbc'
#     # 空头保持/减弱
#     elif (kline.ktxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 >= kline.slp2) & (kline.slp1 <= 1000)):
#         return 'ktbc'
#     # 多头回踩
#     elif (kline.dtxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 <= 1000)):
#         return 'dthc'
#     # 空头反抽
#     elif (kline.ktxt & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.slp1 >= 1000)):
#         return 'ktfc'
#     # 空头反弹
#     elif ((kline.ma2 < kline.ma3) & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.ma1 >= kline.ma2)):
#         return 'ktft'
#     # 多头回调
#     elif ((kline.ma2 > kline.ma3) & (kline.ma_band1_3 >= kline.ma3 * 0.004) & (kline.ma1 <= kline.ma2)):
#         return 'dtht'
#     # 紧密靠拢偏多
#     # elif (kline.jmkl & kline.dtpl):
#     elif kline.jmkl & (kline.dtpl_days >= 8):
#         return 'jmdt'
#     # 紧密靠拢偏空
#     elif kline.jmkl & (kline.ktpl_days >= 8):
#         return 'jmkt'
#     # 紧密靠拢震荡偏空
#     elif kline.jmkl & (kline.ktpl_days < 8) & kline.ktpl:
#         return 'jmzdpk'
#     # 紧密靠拢震荡偏多
#     elif kline.jmkl & (kline.dtpl_days < 8) & kline.dtpl:
#         return 'jmzdpd'
#     # 松散靠拢偏多
#     elif kline.sskl & (kline.dtpl_days >= 12):
#         return 'ssdt'
#     # 松散 靠拢偏空
#     elif kline.sskl & (kline.ktpl_days >= 12):
#         return 'sskt'
#     # 松散靠拢震荡偏空
#     elif kline.sskl & (kline.ktpl_days < 12) & kline.ktpl:
#         return 'sszdpk'
#     # 松散靠拢震荡偏多
#     elif kline.sskl & (kline.dtpl_days < 12) & kline.dtpl:
#         return 'sszdpd'
#     # 松散靠拢 过渡区间
#     elif kline.sskl:
#         return 'sszd'
#     # 紧密靠拢 过渡区间
#     elif kline.jmkl:
#         return 'sszd'
#     else:
#         return 'other'

# 把市场分为多头，空头，靠拢
def get_stage(kline):
    if kline.dtxt & (kline.ma_2_slp0 >= 1000) & (kline.close >= kline.ma1):
        return 'dtjg'  # 多头进攻
    elif kline.dtxt & (kline.ma_2_slp0 < 1000) & (kline.bias1 > 1):
        return 'dttz'  # 多头调整
    elif kline.dtxt & (kline.bias4 >= -0.5) & (kline.bias4 <= 1):
        return 'cai_ma4'  # 踩ma4
    elif kline.dtxt & (kline.bias3 >= -0.5) & (kline.bias3 <= 1):
        return 'cai_ma3'  # 踩ma3
    elif kline.dtxt & (kline.bias2 >= -0.5) & (kline.bias2 <= 1):
        return 'cai_ma2'  # 踩ma2
    elif kline.dtxt & (kline.bias1 >= -0.5) & (kline.bias1 <= 1):
        return 'cai_ma1'  # 踩ma1
    elif kline.dtxt & (kline.bias3 <= -0.5) & (kline.bias4 >= 1):
        return 'dzj34'  # 多中继34
    elif kline.dtxt & (kline.bias2 <= -0.5) & (kline.bias3 >= 1):
        return 'dzj23'  # 多中继23
    elif kline.dtxt & (kline.bias1 <= -0.5) & (kline.bias2 >= 1):
        return 'dzj12'  # 多中继12
    elif kline.dtxt & (kline.bias4 <= -0.5):
        return 'oversell'
    elif kline.ktxt & (kline.ma_2_slp0 <= 1000) & (kline.close <= kline.ma1):
        return 'ktjg'  # 空头进攻
    elif kline.ktxt & (kline.ma_2_slp0 > 1000) & (kline.bias1 < -1):
        return 'kttz'  # 空头调整
    elif kline.ktxt & (kline.bias4 <= 0.5) & (kline.bias4 >= -1):
        return 'chou_ma4'  # 抽ma4
    elif kline.ktxt & (kline.bias3 <= 0.5) & (kline.bias3 >= -1):
        return 'chou_ma3'  # 抽ma3
    elif kline.ktxt & (kline.bias2 <= 0.5) & (kline.bias2 >= -1):
        return 'chou_ma2'  # 抽ma2
    elif kline.ktxt & (kline.bias1 <= 0.5) & (kline.bias1 >= -1):
        return 'chou_ma1'  # 抽ma1
    elif kline.ktxt & (kline.bias3 >= 0.5) & (kline.bias4 <= -1):
        return 'kzj34'  # 空中继34
    elif kline.ktxt & (kline.bias2 >= 0.5) & (kline.bias3 <= -1):
        return 'kzj23'  # 空中继23
    elif kline.ktxt & (kline.bias1 >= 0.5) & (kline.bias2 <= -1):
        return 'kzj12'  # 空中继12
    elif kline.ktxt & (kline.bias4 >= 0.5):
        return 'overbuy'
    elif kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 >= 0):
        return 'jin_dtjg'  # 紧 多头进攻
    elif kline.jmkl & kline.dtpl & (kline.bias1 >= 0.5) & (kline.ma_2_slp0 <= 0):
        return 'jin_dtht'  # 紧 多头回调
    elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 <= 0):
        return 'jin_ktjg'  # 紧 空头进攻
    elif kline.jmkl & kline.ktpl & (kline.bias1 <= -0.5) & (kline.ma_2_slp0 >= 0):
        return 'jin_ktht'  # 紧 空头回调
    elif kline.jmkl & (kline.bias4 >= -0.5) & (kline.bias4 <= 0.5):
        return 'jin_tiema4' #贴ma4
    elif kline.jmkl & (kline.bias3 >= -0.5) & (kline.bias3 <=0.5):
        return 'jin_tiema3'
    elif kline.jmkl & (kline.bias2 >= -0.5) & (kline.bias2 <= 0.5):
        return 'jin_tiema2'
    elif kline.jmkl & (kline.bias1 >= -0.5) & (kline.bias1 <= 0.5):
        return 'jin_tiema1'
    elif kline.jmkl & (((kline.bias3 < -0.5) & (kline.bias4 > 0.5) & (kline.ma3 > kline.ma4)) | ((kline.bias3 > 0.5) & (kline.bias4 < -0.5) & (kline.ma3 < kline.ma4))):
        return 'jin_zj34'
    elif kline.jmkl & (((kline.bias2 < -0.5) & (kline.bias3 > 0.5) & (kline.ma2 > kline.ma3)) | ((kline.bias2 > 0.5) & (kline.bias3 < -0.5) & (kline.ma2 < kline.ma3))):
        return 'jin_zj23'
    elif kline.jmkl & (((kline.bias1 < -0.5) & (kline.bias2 > 0.5) & (kline.ma1 > kline.ma2)) | ((kline.bias1 > 0.5) & (kline.bias2 < -0.5) & (kline.ma1 < kline.ma2))):
        return 'jin_zj23'
    elif kline.jmkl & (kline.max_bias < -0.5):
        return 'jin_dzk' #紧密 多转空
    elif kline.jmkl & (kline.max_bias > 0.5):
        return 'jin_kzd' #紧密 空转多
    else:
        return 'others'
