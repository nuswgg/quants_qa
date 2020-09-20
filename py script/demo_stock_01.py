#!/usr/bin/env python3

import numpy as np
import pandas as pd
import QUANTAXIS as QA

from QAStrategy.qastockbase import QAStrategyStockBase


class strategy(QAStrategyStockBase):
    def init(self):
        """
        初始化工作
        """
        # 复权因子表, 复权处理
        self.df_adj = pd.read_csv("20190101_20191201_adj.csv", index_col="date")
        self.df_adj.index = pd.to_datetime(self.df_adj.index)
        # 获取前置数据, 便于技术指标的计算
        start = QA.QA_util_get_pre_trade_date(self.start, n=40)
        end = QA.QA_util_get_pre_trade_date(self.start, n=1)
        self.hist_data = QA.QA_fetch_stock_day_adv(
            code=self.code, start=start, end=end
        ).data.unstack()
        # 对前置数据进行复权处理
        self.hist_data.loc[:, ["open", "high", "low", "close"]] = (
            self.hist_data[["open", "high", "low", "close"]]
            * self.df_adj.loc[self.hist_data.index, self.hist_data["open"].columns]
        )
        self.hist_data.loc[:, ["volume"]] = (
            self.hist_data[["volume"]]
            / self.df_adj.loc[self.hist_data.index, self.hist_data["volume"].columns]
        )
        self.hist_data = self.hist_data.stack()

        # 每日数据, 换日时自动更新
        self.daily_open = dict()
        self.daily_high = dict()
        self.daily_low = dict()
        self.daily_close = dict()
        self.daily_volume = dict()
        self.daily_amount = dict()
        self.cursor_date = pd.Timestamp(QA.QA_util_get_real_date(self.start, towards=1))
        self.daily_adj = self.df_adj.loc[self.cursor_date, self.code]

        # 信号过滤器
        self.jc_count = dict()  # 为了防止假信号, 默认连续 5 次出现信号买入
        self.sc_count = dict()  # 为了防止假信号, 默认连续 5 次出现信号买入

        # 标的过滤器
        # 说明: 盘中买入的股票, 如果策略是非 T0 的, 可以直接过滤, 因为 A 股是 T+1
        self.longed_stocks = []

        # 开仓标记
        # self.long_sig = dict()

        # 平仓标记
        self.close_sig = dict()

    def on_bar(self, data):
        """
        按 bar 更新数据
        """
        # print(self.hist_data)
        # print(data)
        # self.hist_data = self.hist_data.loc[(self.hist_data.index.levels[0][1:], slice(None)), :] # 加速运算, 换日时丢弃最早的一根日线 bar
        idx_date = str(data.name[0])[:10]
        idx_code = data.name[1]
        if idx_code in self.longed_stocks:
            return
        # 换日重置
        if pd.Timestamp(idx_date) > self.cursor_date:
            print("#####################################################")
            self.cursor_date = pd.Timestamp(idx_date)
            self.daily_adj = self.df_adj.loc[self.cursor_date]
            self.daily_open = dict()
            self.daily_high = dict()
            self.daily_low = dict()
            self.daily_close = dict()
            self.daily_volume = dict()
            self.daily_amount = dict()
            self.jc_count = dict()
            self.longed_stocks = []

        # 每个分钟 bar 自动更新日线 bar
        if self.daily_open.get(idx_date, {}).get(idx_code, None) is None:
            self.daily_open[idx_date] = {idx_code: data["open"]}
            self.daily_high[idx_date] = {idx_code: data["high"]}
            self.daily_low[idx_date] = {idx_code: data["low"]}
            self.daily_close[idx_date] = {idx_code: data["close"]}
            self.daily_volume[idx_date] = {idx_code: data["volume"]}
            self.daily_amount[idx_date] = {idx_code: data["amount"]}
        else:
            self.daily_high[idx_date][idx_code] = max(
                self.daily_high.get(idx_date).get(idx_code), data.high
            )
            self.daily_low[idx_date][idx_code] = min(
                self.daily_low.get(idx_date).get(idx_code), data.low
            )
            self.daily_close[idx_date][idx_code] = data["close"]
            self.daily_volume[idx_date][idx_code] += data["volume"]
            self.daily_amount[idx_date][idx_code] += data["amount"]
        daily_bar = pd.Series(
            name=(pd.Timestamp(idx_date), idx_code),
            data=[
                self.daily_open.get(idx_date).get(idx_code),
                self.daily_high.get(idx_date).get(idx_code),
                self.daily_low.get(idx_date).get(idx_code),
                self.daily_close.get(idx_date).get(idx_code),
                self.daily_volume.get(idx_date).get(idx_code),
                self.daily_amount.get(idx_date).get(idx_code),
            ],
            index=["open", "high", "low", "close", "volume", "amount"],
        )
        daily_bar.loc[["open", "high", "low", "close"]] *= self.daily_adj.loc[idx_code]
        daily_bar.loc[["volume"]] /= self.daily_adj.loc[idx_code]

        # 加入到统一的 dataframe
        self.hist_data = self.hist_data.append(daily_bar)

        # 信号计算
        try:
            kdj = QA.QAIndicator.QA_indicator_KDJ(
                self.hist_data.xs(idx_code, level="code")
            )
        except:
            return
        # jc_signal = QA.QAIndicator.CROSS(kdj["KDJ_K"], kdj["KDJ_D"])
        jc_signal = (kdj["KDJ_K"].iloc[-2] < kdj["KDJ_D"].iloc[-2]) & (
            kdj["KDJ_K"].iloc[-1] > kdj["KDJ_D"].iloc[-1]
        )
        sc_signal = (kdj["KDJ_K"].iloc[-2] > kdj["KDJ_D"].iloc[-2]) & (
            kdj["KDJ_K"].iloc[-1] < kdj["KDJ_D"].iloc[-1]
        )
        # 信号过滤, 盘中连续五根分钟 bar 触发 KDJ 金叉, 买入
        if jc_signal:
            if self.jc_count.get(idx_code, None) is None:
                self.jc_count[idx_code] = 1
            else:
                self.jc_count[idx_code] += 1
        if sc_signal:
            if self.sc_count.get(idx_code, None) is None:
                self.sc_count[idx_code] = 1
            else:
                self.sc_count[idx_code] += 1
        if (idx_code in self.jc_count) and (self.jc_count[idx_code] >= 5):
            # if self.long_sig.get(idx_code, None) is None:
            #     self.long_sig[idx_code] = True
            # elif self.long_sig.get(idx_code):
            self.send_order(
                direction="BUY",
                offset="OPEN",
                code=idx_code,
                price=data["close"],
                volume=10,
                order_id="",
            )
        if (idx_code in self.sc_count) and (self.sc_count[idx_code] >= 5):
            positions = self.acc.positions.get(idx_code, None)
            if positions:
                his_long_vol = positions.volume_long_his
                if his_long_vol > 0:
                    self.send_order(
                        direction="SELL",
                        offset="CLOSE",
                        code=idx_code,
                        price=data["close"],
                        volume=10,
                        order_id="",
                    )


if __name__ == "__main__":
    s = strategy(
        code=["000001", "000002", "600000"],
        init_cash=10000000.0,
        frequence="1min",
        strategy_id="QA_STRATEGY_DEMO",
        risk_check_gap=1,
        portfolio="QA_DEMO",
        start="2019-07-02 09:30:00",
        end="2019-07-05 15:00:00",
    )
    s.run_backtest()
