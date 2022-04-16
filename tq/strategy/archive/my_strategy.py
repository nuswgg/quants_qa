# !/usr/bin/env python
#  -*- coding: utf-8 -*-

from tqsdk.ta import MA,EMA
from tqsdk.tafunc import ma,ema,abs,std, hhv, llv, time_to_datetime

def calc_base_data(klines):
    klinesC = klines.copy()

    # Get ma data
    klinesC['ma0'] = EMA(klines,8)
    # klinesC['ma1'] = MA(klines, 20).ma
    klinesC['ma1'] = EMA(klines, 20)
    klinesC['ma2'] = EMA(klines, 40)
    klinesC['ma3'] = EMA(klines, 60)
    klinesC['ma4'] = EMA(klines, 120)
    klinesC['slp1'] = klinesC.ma1 / klinesC.ma1.shift(1)
    klinesC['slp2'] = klinesC.ma2 / klinesC.ma2.shift(1)
    klinesC['slp3'] = klinesC.ma3 / klinesC.ma3.shift(1)
    klinesC['slp4'] = klinesC.ma4 / klinesC.ma4.shift(1)
    klinesC['cToMa1'] = klinesC.close - klinesC.ma1 # close 到 ma1 距离
    klinesC['cToMa2'] = klinesC.close - klinesC.ma2 # close 到 ma2 距离
    klinesC['std_cToMa1'] = std(klinesC.cToMa1, 20) # 标准差
    klinesC['std_cToMa2'] = std(klinesC.cToMa1, 20)  # 标准差
    klinesC['cdlBody'] = klinesC.close - klinesC.open
    klinesC['cdlHl'] = klinesC.high - klinesC.low # k线的full length = H - L
    klinesC['std_cdl_b'] = std(klinesC.cdlBody, 20) # K线实体的标准差
    klinesC['std_cdl_f'] = std(klinesC.cdlHl, 20) # k线长度的标准差
    klinesC['ma_body'] = ma(abs(klinesC.cdlBody),20)
    klinesC['ma_cToMa1'] = ma(abs(klinesC.cToMa1),20) # 获取20日绝对cToMa1的平均
    klinesC['ma_cToMa2'] = ma(abs(klinesC.cToMa2),20) # 获取20日绝对cToMa2的平均
    klinesC['ma_min1_3'] = klinesC[['ma1', 'ma2', 'ma3']].min(axis=1)  # 3均线
    klinesC['ma_max1_3'] = klinesC[['ma1', 'ma2', 'ma3']].max(axis=1)  # 3均线
    klinesC['ma_band1_3'] = klinesC.ma_max1_3 - klinesC.ma_min1_3
    klinesC['kl_base_ref'] = klinesC.ma2 * 0.0001 # 此指标避免极端窄幅波动
    klinesC['kl1_3_thresh'] = klinesC[['ma_body','kl_base_ref']].max(axis=1) * (10 + inc_body1_3) / 10 # 4均线靠拢的阈值
    klinesC['ma_kl1_3'] = klinesC.ma_band1_3 <= klinesC.kl1_3_thresh  # 3 均线
    klinesC['ma_min1_4'] = klinesC[['ma1', 'ma2', 'ma3', 'ma4']].min(axis=1)  # 4均线
    klinesC['ma_max1_4'] = klinesC[['ma1', 'ma2', 'ma3', 'ma4']].max(axis=1) # 4均线
    klinesC['ma_band1_4'] = klinesC['ma_max1_4'] - klinesC['ma_min1_4'] # 4均线
    klinesC['kl1_4_thresh'] = klinesC[['ma_body','kl_base_ref']].max(axis=1) * (10 + inc_body1_4) / 10  # 4均线靠拢的阈值
    klinesC['ma_kl1_4'] = klinesC.ma_band1_4 <= klinesC.kl1_4_thresh  # 4均线
    klinesC['df_12'] = klinesC.ma1 - klinesC.ma2
    klinesC['df_23'] = klinesC.ma2 - klinesC.ma3
    klinesC['df_34'] = klinesC.ma3 - klinesC.ma4

    # get vol stats
    klinesC['mv1'] = ma(klinesC.volume, 8)
    klinesC['mv2'] = ma(klinesC.volume, 40)
    # vol strend
    klinesC['vols'] = klinesC.volume/klinesC.mv2
    # 巨量
    klinesC['jl'] = klinesC.vols > 3
    # 大量
    klinesC['dl'] = ((klinesC.vols > 2) & (klinesC.vols < 3))
    # 阶段放量
    klinesC['jdfl'] = (klinesC.mv1 > klinesC.mv2) & (klinesC.volume/klinesC.mv1 > 1.3)
    # 反攻放量
    klinesC['fgfl'] = (klinesC.mv1 < klinesC.mv2) & (klinesC.volume/klinesC.mv1 > 1.5)

    # get kline stats
    # klinesC['cdlBody'] = klinesC.close - klinesC.open
    # klinesC['cdlHl'] = klinesC.high - klinesC.low # k线的full length = H - L
    klinesC['zf'] = klinesC.close.pct_change()*1000
    klinesC['bodyU'] = klinesC[['close', 'open']].max(axis=1)
    klinesC['bodyD'] = klinesC[['close', 'open']].min(axis=1)
    klinesC['bdr'] = klinesC.bodyU - klinesC.bodyD # K线 波动range
    klinesC['upperShadow'] = klinesC.high - klinesC.bodyU
    klinesC['lowerShadow'] = klinesC.bodyD - klinesC.low

    # get kline statistics
    klinesC['stdCdlB'] = std(klinesC.cdlBody, 20) # K线实体的标准差
    klinesC['stdCdlF'] = std(klinesC.cdlHl, 20) # k线长度的标准差
    klinesC['maBody'] = ma(abs(klinesC.cdlBody),30)  # 平均绝对body长度
    klinesC['zdStrengh'] = klinesC.cdlBody/klinesC.maBody # 涨跌力度
    klinesC['longUShadow'] = klinesC.upperShadow/klinesC.maBody
    klinesC['longLShadow'] = klinesC.lowerShadow/klinesC.maBody
    klinesC['rng3D'] = hhv(klinesC.close,3) - llv(klinesC.close,3)    # 3日K线实体波动
    klinesC['rng5D'] = hhv(klinesC.close,5) - llv(klinesC.close,5)     # 5日K线实体波动
    klinesC['rng7D'] = hhv(klinesC.close,7) - llv(klinesC.close,7)  # 7日K线实体波动
    klinesC['rng9D'] = hhv(klinesC.close,9) - llv(klinesC.close,9)  # 9日K线实体波动
    klinesC['bRng'] = klinesC['bodyU']  - klinesC['bodyD']  # K线实体range

    # get klines pattern
    klinesC['yby'] =  (klinesC.zdStrengh > 1) & (klinesC.zdStrengh.shift(1) < -1) & (klinesC.close >= klinesC.open.shift(1)) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume > klinesC.mv1))  # 阳包阴
    klinesC['ctpj'] = (klinesC.zdStrengh > 1) & (klinesC.zdStrengh.shift(1) < -1) & (klinesC.close < klinesC.open.shift(1)) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume > klinesC.mv1)) # 穿头破脚
    klinesC['ybyD'] = (klinesC.zdStrengh <= -1) & (klinesC.zdStrengh.shift(1) >= 1) & (klinesC.close <= klinesC.open.iloc[-2])   # 阴包阳
    klinesC['wygd'] = (klinesC.zdStrengh <= -1) & (klinesC.zdStrengh.shift(1) >= 1) & (klinesC.close > klinesC.open.iloc[-2])  # 乌云盖顶
    klinesC['tp3D'] = (klinesC.bRng >= klinesC.rng3D) & (abs(klinesC.zdStrengh)>1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.iloc[-2] > 1.5) & (klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp3D==True]
    klinesC['tp5D'] = (klinesC.bRng >= klinesC.rng5D) & (abs(klinesC.zdStrengh)>1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.iloc[-2] > 1.5) & (klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp5D==True]
    klinesC['tp7D'] = (klinesC.bRng >= klinesC.rng7D) & (abs(klinesC.zdStrengh)>1.5) & \
                      ((klinesC.volume > klinesC.mv2) | (klinesC.volume / klinesC.volume.iloc[-2] > 1.5) & (klinesC.volume > klinesC.mv1))
    # klinesC[klinesC.tp7D == True]
    ## 定义Strategy
    klinesC['s001'] = (klinesC.yby == True) & (klinesC.ma_kl1_3 == True)
    return klinesC

