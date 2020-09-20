# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/20 下午5:15
"""

import uuid
import pandas as pd
import os
import datetime
from QAStrategy import QAStrategyCTABase
import QUANTAXIS as QA
from QUANTAXIS.QAUtil import QA_util_cache
from userfunc import QA_DataStruct_Future_min_wier
from userfunc import checkTimeInsideForBuy2, checkTimeInsideForSell2
from userfunc import checkTimeInsideTail
#单边空。连c>o + vol1<vol2.s天（23456）。损（）
a0 = 10
S0 = 2
n0 = 1
c0 = [9999998]
o0 = [0]
v0 = [0]
# k0数列作为保存前一个留下来的完整K线数列
FLAG0 = {'s': 0, "h": 0.0, "l": 9999999.0, 'dt': 0}
timestamp0 = pd.Timestamp(0)
# 买入到卖出时间限制
OPENDT0 = {'SELL': timestamp0, 'BUY': timestamp0}


class WierStrategy(QAStrategyCTABase):
    """BUY_OPEN 期货 多开
    BUY_CLOSE 期货 空平(多头平旧仓)
    SELL_OPEN 期货 空开
    SELL_CLOSE 期货 多平(空头平旧仓)
    """

    def user_init(self):
        # self.flag保存{s H L}列表
        self.flag = [FLAG0]
        self._cache = QA_util_cache()
        self._opendt = OPENDT0.copy()

    def on_bar(self, data):
        # 计算
        s, h, l = self._getSHL()
        timestamp_1min = data.name[0]
        code = data.name[1]
        if s >=S0 and self._getPositionVolume(code) <= 1 :
            # 计算并缓存1min多开、空开信号
            self._getBuyOrSell(data, '1min')
        if self.acc.get_position(code).volume_short == 0:
            # 空头未开仓
            # 判断是否要开仓
            if s >= S0 and checkTimeInsideForBuy2(timestamp_1min):
                op = self._getBuyOrSell(data, '1min')
                if op['SELL_OPEN']:
                    # 空开
                    self.send_order('SELL', 'OPEN', code=code, price=self.roundPrice(data), volume=1)
                    self._opendt['SELL'] = timestamp_1min
                    # 有多开或空开仓位时：S=0, H1、L1保持上一个五分钟值
                    self._flagAfterVolumeChange(timestamp_1min)
                    self._showStaticMessage(code)
        elif self.acc.get_position(code).volume_short == 1:
            # 空平判断
            op = self._getBuyOrSell(data, '5min')
            if op['BUY_CLOSE'] or checkTimeInsideForSell2(timestamp_1min):
                # if self._getBuyOrSellTimeLimit(data)['BUY']:
                if self._getBuyOrSellTimeLimit(data)['SELL']:
                    # 空平
                    self.send_order('BUY', 'CLOSE', code=code, price=self.roundPrice(data), volume=1)
                    if self.acc.get_position(code).volume_long == 0:
                        self._flagUpdate(FLAG0, timestamp_1min)
                    self._showStaticMessage(code)

        if self.acc.get_position(code).volume_long == 0:
            # 未开仓
            # 判断是否要开仓
            if s >= S0 and checkTimeInsideForBuy2(timestamp_1min):
                op = self._getBuyOrSell(data, '1min')
                if op is None:
                    op = self.wier1minOpen(data)
                if op['BUY_OPEN']:
                    # 多开
                    self.send_order('BUY', 'OPEN', code=code, price=self.roundPrice(data), volume=1)
                    self._opendt['BUY'] = timestamp_1min
                    self._flagAfterVolumeChange(timestamp_1min)
                    self._showStaticMessage(code)
        elif self.acc.get_position(code).volume_long == 1:
            # 多平判断_getBuyOrSellTimeLimit
            op = self._getBuyOrSell(data, '5min')
            if op['SELL_CLOSE'] or checkTimeInsideForSell2(timestamp_1min):
                # if self._getBuyOrSellTimeLimit(data)['SELL']:
                if self._getBuyOrSellTimeLimit(data)['BUY']:
                    # 多平
                    self.send_order('SELL', 'CLOSE', code=code, price=self.roundPrice(data), volume=1)
                    if self.acc.get_position(code).volume_short == 0:
                        self._flagUpdate(FLAG0, timestamp_1min)
                    self._showStaticMessage(code)

        # 计算五分钟s, h, l
        self.wier5min(data)
        self._cache.clear()

    def _flagAfterVolumeChange(self, timestamp_1min):
        flag = self.flag[-1].copy()
        flag['s'] = 0
        self._flagUpdate(flag, timestamp_1min)

    def roundPrice(self, data, ndigits=0):
        """成交价格
        四舍五入道ndigits位小数
        """
        return round(data['close'], ndigits)

    def _getBuyOrSell(self, data, freq='1min'):
        """缓存买卖条件
        """
        # key = freq + timestamp
        key = freq + str(data.name[0])
        op = self._cache.get(key)
        if op is None:
            if freq == '1min':
                op = self.wier1minOpen(data)
            elif freq == '5min':
                op = self.wier5minClose(data)
            self._cache.set(key, op, age=100)
        return op

    def _getBuyOrSellTimeLimit(self, data):
        """买入时间和卖出时间间隔限制
        """
        timestamp_1min = data.name[0]
        result = {}
        for item in self._opendt:
            # 当前分钟数比上次买入时间大于299秒
            result[item] = (timestamp_1min - self._opendt[item]).seconds > 299
        return result

    def _flagUpdteDatetime(self, timestamp_min, flag):
        """更新flag时间戳
        """
        _flag = flag.copy()
        _flag.update({'dt': timestamp_min})
        return _flag

    def _showStaticMessage(self, code, debug=True):
        if debug:
            pos = self.acc.get_position(code)
            print("持仓信息：", pos.static_message)
            print("volume_long:{}, volume_short:{}".format(self.acc.get_position(code).volume_long,
                                                           self.acc.get_position(code).volume_short))
            print("--------------------------------------------")

    def wier(self, data):
        """计算s, h , l策略
        data: ('open', 12980.0) ('high', 13030.0009765625) ('low', 12980.0) ('close', 13005.0009765625) ('volume', 3374.0) ('position', 221960.0) ('price', 0.0) ('tradetime', '2020-01-02 09:01') ('type', '1min')
        """
        s, h, l = self._getSHL()
        s, h, l, timestamp_1min = self.wier5min(data)

        return self.flag[-1]

    def wier1minOpen(self, data):
        """多开 空开条件判断
        """
        # 连续缩量
        # 一分钟数据
        s, h, l = self._getSHL()
        timestamp_1min = data.name[0]
        # print("连续缩量：{} {}".format(s, timestamp_1min))
        op = {'BUY_OPEN': False, 'SELL_OPEN': False}
        if self._getPositionVolume(data.name[1]) == 0:
            # 仓位不为零;
            if data.close < 0 and checkTimeInsideForBuy2(timestamp_1min):
                # 买多信号
                print("--多开信号：S={} {}".format(s, timestamp_1min))
                op['BUY_OPEN'] = True

            if data.close < l and checkTimeInsideForBuy2(timestamp_1min):
                # 买空信号
                print("--空开信号：S={} {}".format(s, timestamp_1min))
                op['SELL_OPEN'] = True

        # if self._getPositionVolume(data.name[1]) > 0:
        #     # 仓位不为零; 当同时产生信号时，为True
        #     # a = op['BUY_OPEN'] and op['SELL_OPEN']
        #     for item in op:
        #         op[item] = False

        return op

    def wier5minClose(self, data):
        """平多、平空条件判断
        逐个5min-high和5min-low和时间标签:
        若是买多，当5min-low>H1+4*(H1-L1)或5min-high<L1或时间标签位于（14:30~15:00）就平仓，并s，H1,L1=0。
        若是买空，当5min-high<L1-4*(H1-L1)或5min-low>H1或时间标签位于（14:30~15:00）就平仓，并s，H1,L1=0。
        """
        # 连续缩量
        # 一分钟数据
        op = {'BUY_CLOSE': False, 'SELL_CLOSE': False}
        timestamp_1min = data.name[0]
        if self._ifdivby5min(str(timestamp_1min)):
            s, h, l = self._getSHL()
            code = data.name[1]
            # print("连续缩量：{} {}".format(s, timestamp_1min))
            # 时间为5分钟的整倍数
            data = self._get5minLast(code)
            high, low, close, open = data.high[0], data.low[0], data.close[0], data.open[0]
            if close < h or close > h + n0*(h - l):
                # 平多信号
                print("--多平信号：S={} {} | {}".format(s, timestamp_1min, "5min-low>H1+4*(H1-L1) 或 5min-high<L1"))
                print(" {} > {} or {} < {}".format(low, h + 4 * (h - l), high, l))
                op['SELL_CLOSE'] = True
            if close > h or close < l - n0*(h - l):
                # 平空信号
                print("--空平信号：S={} {} | {}".format(s, timestamp_1min, "5min-high<L1-4*(H1-L1) 或 5min-low>H1"))
                print(" {} < {} or {} > {}".format(high, l - 4 * (h - l), low, h))
                op['BUY_CLOSE'] = True

        return op

    def wier5min(self, data):
        """计算五分钟s, h, l
        当5min-vol<6000时，S=S+1.
            当5min-high>=H1，H1=5min-high
            当5min-low<=L1，L1=5min-low
        当5min-vol>6000时，
            空仓时: S，H1，都为0， L1=99999999
            非空仓（有多开或空开仓位）时：S=0, H1、L1保持上一个五分钟值;
        """
        s, h, l = self._getSHL()
        timestamp_1min = data.name[0]
        code = data.name[1]
        # if self._ifdivby5min(str(timestamp_1min)) and checkTimeInsideForBuy2(str(timestamp_1min)):
        if self._ifdivby5min(str(timestamp_1min)):
            # 时间为5分钟的整倍数
            if self._getPositionVolume(code) == 0:
                # 持仓时计算flag
                d5 = self._get5minLast(code)
                c0.append(d5.close[0])
                o0.append(d5.open[0])
                v0.append(d5.volume[0])
                if d5.close.values[0] > d5.open.values[0] and v0[-2] < d5.volume.values[0]:
                    if checkTimeInsideTail(timestamp_1min) and self._getPositionVolume(code) == 0:
                        s, h, l = self._getSHL(index=0)
                    else:
                        s += 1
                        h = h if h > d5.high.values[0] else d5.high.values[0]
                        l = l if l < d5.low.values[0] else d5.low.values[0]
                else:
                    s = 0
                    if (self._getPositionVolume(code)) == 0:
                        # 没有开仓
                        # 当5min-vol>6000时，
                        #   空仓时: S，H1，都为0， L1=99999999
                        #   非空仓（有多开或空开仓位）时：S=0, H1、L1保持上一个五分钟值;
                        h, l = FLAG0['h'], FLAG0['l']
                    # h = flag['h']
                    # l = flag['l']

            flag = {'s': s, "h": h, "l": l}
            self._flagUpdate(flag, timestamp_1min)
        return s, h, l, timestamp_1min

    def wier5min02(self, data):
        """计算五分钟s, h, l
        当5min-vol>6000时，s=0,h,l继续当5min-high>=H1，H1=5min-high
    当5min-low<=L1，L1=5min-low
        """
        s, h, l = self._getSHL()
        timestamp_1min = data.name[0]
        code = data.name[1]
        # if self._ifdivby5min(str(timestamp_1min)) and checkTimeInsideForBuy2(str(timestamp_1min)):
        if self._ifdivby5min(str(timestamp_1min)):
            # 时间为5分钟的整倍数
            d5 = self._get5minLast(code)
            if d5.close.values[0] > d5.open.values[0]:
                s += 1
            else:
                s = 0
            h = h if h > d5.high.values[0] else d5.high.values[0]
            l = l if l < d5.low.values[0] else d5.low.values[0]
            flag = {'s': s, "h": h, "l": l}
            self._flagUpdate(flag, timestamp_1min)
        return s, h, l, timestamp_1min

    def wier5min01(self, data):
        """计算五分钟s, h, l
        当5min-vol>6000时，s=0,h =0, l=0
        """
        s, h, l = self._getSHL()
        timestamp_1min = data.name[0]
        code = data.name[1]
        # if self._ifdivby5min(str(timestamp_1min)) and checkTimeInsideForBuy2(str(timestamp_1min)):
        if self._ifdivby5min(str(timestamp_1min)):
            # 时间为5分钟的整倍数
            d5 = self._get5minLast(code)
            if d5.close.values[0] > d5.open.values[0]:
                s += 1
                h = h if h > d5.high.values[0] else d5.high.values[0]
                l = l if l < d5.low.values[0] else d5.low.values[0]
                flag = {'s': s, "h": h, "l": l}
            else:
                flag = FLAG0
                # h = flag['h']
                # l = flag['l']
            self._flagUpdate(flag, timestamp_1min)
        return s, h, l, timestamp_1min

    def _getPositionVolume(self, code):
        """总仓位数量
        """
        return self.acc.get_position(code).volume_short + self.acc.get_position(code).volume_long

    def _flagUpdate(self, flag, timestamp_1min):
        """更新self.flag
        """
        flag = self._flagUpdteDatetime(timestamp_1min, flag)
        if flag != self.flag[-1] and flag['dt'] != self.flag[-1]['dt']:
            # flag和上一个不同，并且时间也不相同，则插入flag
            self.flag.append(flag)

    def _getSHL(self, index=-1):
        """返回index对应的flag
        默认index=-1,返回最后一个flag
        """
        flag = self.flag[index]
        s, h, l = flag['s'], flag['h'], flag['l']
        return s, h, l

    def _get5minLast(self, code):
        """转换成五分钟数据,返回最后一个五分钟数据
        """
        # 非正好五分钟时间点处理
        count = 15
        data5 = self._get5min(code, count)
        d5 = data5.tail(1)
        return d5

    def _get5min(self, code, count=999999):
        """转换成五分钟数据
        """
        md = self.get_code_marketdata(code)[-count:]
        d1 = QA_DataStruct_Future_min_wier(md)
        # data5 = data5.min5()
        data5 = d1.resample('5min')
        return data5

    def _ifdivby5min(self, datestr: str, inlist=["5", "0"]):
        """是否五分钟的整倍数
        五分钟的分钟数最后一位是："5", "0"
        可调整inlist适应10分钟、15分钟的整倍数
        """
        return str(datestr)[-4] in inlist

    def saveResult(self):
        """保存策略结果到excel
        """
        from openpyxl import load_workbook, Workbook

        def _insertWorksheet(dataFrame, path, sheet_name):
            if os.path.exists(path):
                writer = pd.ExcelWriter(path, engine='openpyxl')
                writer.book = load_workbook(path)
                writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)

                dataFrame.to_excel(writer, sheet_name=sheet_name)
                writer.save()
            else:
                dataFrame.to_excel(path, sheet_name=sheet_name)

        def _save_market_data():

            md = pd.concat(self._market_data, axis=1, sort=False).T
            md.to_excel(path, sheet_name="1min")

            d1 = QA_DataStruct_Future_min_wier(md)
            data5 = d1.resample('5min')
            _insertWorksheet(data5, path, '5min')

        # save flag
        path = os.path.join("./", '{}.xlsx'.format("market_data"))
        _save_market_data()
        data = pd.DataFrame(self.flag, columns=['dt', 's', 'h', 'l'])
        _insertWorksheet(data, path, 'Flag')
        # save acc.history_table
        data = self.acc.history_table
        _insertWorksheet(data, path, 'Trade')
        data = data[
            ['datetime', 'code', 'price', 'amount', 'cash', 'commission', 'tax', 'message', 'frozen', 'direction',
             'total_frozen'
             ]]
        #_insertWorksheet(data, path, 'Trade')
