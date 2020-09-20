#!/usr/bin/env python3

"""
QUANTAXIS 版本的期货套利策略
"""

import datetime
from collections import deque

import pandas as pd

import QUANTAXIS as QA

from QAStrategy import QAStrategyCTABase

class Arbitrage(QAStrategyCTABase):
    """
    继承自 QAStrategyCTABase 这个基类，来实现自己的策略
    """

    def init(self):
        """
        定义初始化函数，进行预处理
        """
        #super().__init__()
        self.tick_info_A = deque(maxlen=120)
        self.tick_info_B = deque(maxlen=120)
        self.bar_info_A = deque(maxlen=10)
        self.bar_info_B = deque(maxlen=10)
        self.curr_date = str(datetime.date.today())[:10]
        #self.is_trade_time = is_trade_time
        #self.max_holding_vol = STG_PARAMS.max_holding_vol

    def on_tick(self, tick):
        print("llllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
        print(tick["symbol"])
        if tick["symbol"] == 'hc2005':
            # 保存分钟行情收盘价
            if tick["datetime"][17:19] == "00":
                self.bar_info_A.append(tick)
            self.tick_info_A.append(tick)
        elif tick["symbol"] == 'rb2005':
            if tick["datetime"][17:19] == "00":
                self.bar_info_B.append(tick)
            self.tick_info_B.append(tick)
        else:
            raise ValueError("fuck")

        try:
            print(self.tick_info_B.pop())
            print(self.tick_info_A.pop())
        except:
            pass


if __name__ == "__main__":
    Arbitrage = Arbitrage(
        code=["hc2005", 'rb2005'],
        frequence="tick",
        model="rust",
        strategy_id="rb_hc_arbitratege",
        # data_host='192.168.2.118',
        # trade_host='192.168.2.118',
        # mongo_ip='192.168.2.118'
        
        #init_cash=STG_PARAMS.init_cash,
    )
    Arbitrage.init()
    Arbitrage.run_sim()
