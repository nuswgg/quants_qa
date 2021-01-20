import datetime

import numpy as np
import pandas as pd
import prettytable as pt
import talib
from QAStrategy.qastockbase import QAStrategyStockBase
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import (GridSearchCV, cross_val_predict,
                                     cross_val_score, train_test_split)
from sklearn.preprocessing import MinMaxScaler, StandardScaler

import QUANTAXIS as QA
from QUANTAXIS.QAFetch import QAQuery


def get_year_report_date(now_date):
    if now_date.month < 4:
        return datetime.date(now_date.year-2, 12, 31)
    else:
        return datetime.date(now_date.year-1, 12, 31)


def get_all_stock_list_without_ST():
    stocklist = QA.QA_fetch_stock_list()
    stocklist = stocklist.loc[~stocklist['name'].str.contains('ST')]
    stocklist = stocklist['code'].to_list()
    return stocklist


def get_financialdata_and_stock_list(date):
    stocklist = get_all_stock_list_without_ST()
    financialdata = QA.QA_fetch_financial_report(
        stocklist, get_year_report_date(date).strftime('%Y-%m-%d'), ltype='CN')
    financialdata = financialdata.loc[financialdata.index[0][0]]
    financialdata = financialdata[['基本每股收益', '净资产收益率', '每股经营现金流量',
                                   '负债合计', '实收资本（或股本）', '营业收入', '营业利润', '息税折旧摊销前利润(EBITDA)']]
    financialdata = financialdata.query(
        '基本每股收益 >0 and 营业利润 >0 and 每股经营现金流量 >0')
    stocklist = financialdata.index.to_list()
    return financialdata, stocklist


def get_stock_thshy(stocklist):
    stock_block_data = QA.QA_fetch_stock_block(stocklist)
    tempdata = stock_block_data.loc[stock_block_data['type'] == 'thshy']
    tempdata = tempdata.drop_duplicates(subset='code', keep='first')
    return tempdata


def predicted_close_by_RandomForest(stockdata, Xlist, Yfieldname):
    RFR = RandomForestRegressor(n_estimators=100, min_samples_leaf=1)
    TX = stockdata[Xlist]
    vec = DictVectorizer(sparse=False)
    TX = vec.fit_transform(TX.to_dict(orient='record'))
    predicted = cross_val_predict(RFR, TX, stockdata[Yfieldname], cv=5)
    stockdata['predictedCapital'] = predicted
    stockdata['predictedclose'] = stockdata['predictedCapital'] / \
        stockdata['实收资本（或股本）']
    stockdata['predictedrate'] = stockdata['predictedclose'] / \
        stockdata['close']
    return stockdata['predictedrate']


def markettime_Boll(data):
    ind_BOLL = pd.DataFrame()
    ind_BOLL['UB'], ind_BOLL['BOLL'], ind_BOLL['LB'] = talib.BBANDS(
        data['close'], 30, 1, 1, 1)
    ind_BOLL['CLOSE'] = data['close']
    # 获取LBmin用于作图
    LBmin = ind_BOLL['LB'].min()
    # GOLDCROSS
    # CLOSE上穿LB
    ind_BOLL['CROSS_CLOSE_LB'] = QA.CROSS(
        ind_BOLL['CLOSE'], ind_BOLL['LB'])*LBmin
    # CLOSE上穿UB
    ind_BOLL['CROSS_CLOSE_UB'] = QA.CROSS(
        ind_BOLL['CLOSE'], ind_BOLL['UB'])*LBmin
    # DEADCROSS
    # CLOSE下穿UB
    ind_BOLL['CROSS_UP_CLOSE'] = - \
        QA.CROSS(ind_BOLL['UB'], ind_BOLL['CLOSE'])*LBmin
    # CLOSE下穿LB
    ind_BOLL['CROSS_LB_CLOSE'] = - \
        QA.CROSS(ind_BOLL['LB'], ind_BOLL['CLOSE'])*LBmin
    # CLOSE下穿BOLL
    ind_BOLL['CROSS_BOLL_CLOSE'] = - \
        QA.CROSS(ind_BOLL['BOLL'], ind_BOLL['CLOSE'])*LBmin
    # 将所有上穿下穿汇集到同一列中
    ind_BOLL['flag'] = ind_BOLL['CROSS_CLOSE_LB']+ind_BOLL['CROSS_UP_CLOSE'] + \
        ind_BOLL['CROSS_CLOSE_UB']+ind_BOLL['CROSS_LB_CLOSE'] + \
        ind_BOLL['CROSS_BOLL_CLOSE']
    ind_BOLL = ind_BOLL.dropna(axis='index')
    # 通过将0改为nan，fillna，实现在两次交叉之间的值均为前一次交叉的值
    ind_BOLL['flag'] = ind_BOLL['flag'].replace({0: np.nan})
    ind_BOLL = ind_BOLL.fillna(axis='index', method='ffill')
    # 把数据回到0-3000范围，作图好看
    #ind_BOLL['flag'] = ind_BOLL['flag'].replace({-LBmin: 0})
    ind_BOLL.loc[ind_BOLL['flag'] < 0, 'flag'] = False
    ind_BOLL.loc[ind_BOLL['flag'] > 0, 'flag'] = True
    return ind_BOLL


def get_markettime(date, index):
    datestr = date.strftime('%Y-%m-%d')
    # 数据取到400天之前的，保证周线数据计算
    startdate = date-datetime.timedelta(days=900)
    startdatestr = startdate.strftime('%Y-%m-%d')
    data = QA.QA_fetch_index_day_adv(index, startdatestr, datestr)
    # 制作周线数据
    weekdata = data.week
    # 由于在markettime_BOLL中使用TALIB计算，所以传入数据为DataFrame
    daydata = data.data
    markettime_day = markettime_Boll(daydata)
    markettime_week = markettime_Boll(weekdata)
    # 周线与日线均为True才开仓
    if markettime_week['flag'][-1]:
        if markettime_day['flag'][-1]:
            return True
    return False


def data_prepared(date):
    datestr = date.strftime('%Y-%m-%d')
    financialdata, stocklist = get_financialdata_and_stock_list(date)
    data = QA.QA_fetch_stock_day_adv(stocklist, datestr, datestr)
    data = data.to_qfq()
    data = data.data.loc[data.index[0][0], :]
    mergeddata = pd.merge(left=data, right=financialdata,
                          left_index=True, right_index=True)
    mergeddata['总市值'] = mergeddata['close'] * \
        mergeddata['实收资本（或股本）']
    blockdata = get_stock_thshy(stocklist)
    mergeddata = mergeddata.merge(
        blockdata[['blockname']], left_index=True, right_index=True)
    return mergeddata

#['EPS', 'ROE', 'operatingCashFlowPerShare', 'totalShare', 'operatingRevenue', 'blockname']


def select_stock(date, Xlist, Yfieldname, target_stock_number):
    mergeddata = data_prepared(date)
    mergeddata['predictedrate'] = predicted_close_by_RandomForest(
        mergeddata, Xlist, Yfieldname)
    mergeddata = mergeddata.sort_values(
        by='predictedrate', ascending=False)
    target_stock_list = mergeddata.index.to_list()[:target_stock_number]
    return target_stock_list


class Strategy(QAStrategyStockBase):
    def user_init(self):
        self.Xlist = ['基本每股收益', '净资产收益率', '每股经营现金流量',
                      '实收资本（或股本）', '营业收入', '息税折旧摊销前利润(EBITDA)',
                      'blockname']
        self.target_stock_number = 5
        self.days_to_change = 3
        self.hold_days = 0
        self.init_cash = 100000
        self.stock_positions = pretty_stock_positions()
        return super().user_init()

    def order_to_target_volume(self, code, volume):
        if self.frequence == 'day':
            currentprice = QA.QA_fetch_stock_day(
                code, self.datestr, self.datestr, format='pd')['close'][-1]
        elif self.frequence == '1min':
            currentprice = QA.QA_fetch_stock_min(
                code, self.datetimestr, self.datetimestr, format='pd')['close'][-1]
        if volume > 0:
            if code in self.stock_positions.codelist():
                hold_stock_amount = self.acc.positions[code].volume_long
                print("{0}\t{1}".format(code, hold_stock_amount))
                if volume > hold_stock_amount:
                    self.send_order('BUY', 'OPEN', code,
                                    currentprice, volume - hold_stock_amount)
                    print("调仓\t买入了{0}\t{1}股\t单价为{2}".format(
                        code, volume-hold_stock_amount, currentprice))
                elif volume < hold_stock_amount:
                    self.send_order('SELL', 'CLOSE', code,
                                    currentprice, hold_stock_amount - volume)
                    print("调仓\t卖出了{0}\t{1}股".format(
                        code, hold_stock_amount-volume))
                else:
                    print('已经持有目标数量的{0}股票,不必调仓'.format(code))
            else:
                self.send_order('BUY', 'OPEN', code, currentprice, volume)
                self.stock_positions.codelist().append(code)
                print("开仓\t买入了{0}\t{1}股\t单价为{2}".format(
                    code, volume, currentprice))
        else:
            if code in self.stock_positions.codelist():
                hold_stock_amount = self.acc.positions[code].volume_long
                if hold_stock_amount > 0:
                    self.send_order('SELL', 'CLOSE', code,
                                    currentprice, hold_stock_amount)
                    print("调仓\t卖出了{0}\t{1}股\t单价为{2}".format(
                        code, hold_stock_amount, currentprice))
                self.stock_positions.codelist().remove(code)
            else:
                print("{0}本就不在持仓中，不必清仓".format(code))

    def on_bar(self, bar):
        self.date = bar.name[0]
        self.datestr = self.date.strftime('%Y-%m-%d')
        if self.datestr == self.start:
            self.acc.reload()
        self.datetimestr = self.date.strftime('%Y-%m-%d %H-%M-%S')
        markettime = get_markettime(self.date, '399333')
        print("{0}的全市场择时结果为{1}".format(self.datestr, markettime))
        self.ajust_postion(markettime)

    def ajust_postion(self, markettime):
        # 择时结果为True则进行交易
        if markettime:
            # 持仓天数为0就调仓
            print("当前可用资金{0}".format(self.get_cash()))
            if self.hold_days == 0:
                target_stock_list = select_stock(
                    self.date, self.Xlist, 'close', self.target_stock_number)
                print("目标股列表{0}".format((target_stock_list)))
                # 先把不在目标列表里的股票卖掉
                for stockcode in self.stock_positions.codelist():
                    # print("{0}has amount of {1}".format(
                    #     stockcode, self.acc.positions[stockcode].volume_long))
                    if not stockcode in target_stock_list:
                        self.order_to_target_volume(stockcode, 0)
                # 算算有多少钱
                total_cash = self.get_cash()
                target_cash = total_cash*0.98 / \
                    (self.target_stock_number-len(self.stock_positions.codelist()))
                for stockcode in target_stock_list:
                    # print("开始处理股票{0}".format(stockcode))

                    if self.frequence == 'day':
                        stock_price = QA.QA_fetch_stock_day(
                            stockcode, self.datestr, self.datestr, format='pd')['close'][-1]

                    else:
                        stock_price = QA.QA_fetch_stock_min(
                            stockcode, self.datetimestr, self.datetimestr, format='pd')['close'][-1]
                    # print("目标股价{0}".format(stock_price))
                    target_volume = target_cash / stock_price // 100 * 100
                    print("{0}的目标持仓量{1}".format(stockcode,target_volume))
                    if stockcode in self.stock_positions.codelist():
                        # if target_volume == self.acc.positions[stockcode].volume_long:
                        print("{0}已经在持仓中，不需要调仓".format(stockcode))
                        # else:
                        #     self.order_to_target_volume(stockcode,target_volume)
                    else:
                        self.order_to_target_volume(stockcode, target_volume)
            # 持仓天数加1
            self.hold_days = self.hold_days + 1
            # 如果持仓天数等于2（0天开始持仓，相当于持仓三天），则等于零，后一天为调仓日
            if self.hold_days == self.days_to_change-1:
                self.hold_days = 0
        else:
            if len(self.stock_positions.codelist()) > 0:
                print("清仓")
                for stockcode in self.stock_positions.codelist():
                    self.order_to_target_volume(stockcode, 0)
            # 如果hold_days小于0，用于三只乌鸦等应急清仓，清仓后的等待不开仓天数。其他时候，如果市场本身就是空仓的，就等于0
            if self.hold_days < 0:
                self.hold_days = self.hold_days + 1
            else:
                self.hold_days = 0
        self.stock_positions.update(self.date)


class pretty_stock_positions(Strategy):
    def __init__(self):
        self.stock_positions = pd.DataFrame()

    def append(self, code, amount, price, buydate):
        pass

    def print(self):
        if len(self.stock_positions) > 0:
            tb = pt.PrettyTable()
            for columnsname in self.stock_positions.columns:
                tb.add_column(columnsname, self.stock_positions[columnsname])
            print(tb)
        else:
            pass

    def update(self, date):
        self.stock_positions = pd.DataFrame()
        stocklist = s.acc.positions.keys()
        for stockcode in stocklist:
            tempdf = pd.Series(s.acc.get_position(stockcode).__dict__)
            tempdf = tempdf[['code', 'volume_long_his', 'volume_long_today',
                             'open_price_long', 'position_price_long', 'position_cost_long', 'last_price']]
            self.stock_positions = self.stock_positions.append(
                tempdf, ignore_index=True)
        if len(self.stock_positions) > 0:
            self.stock_positions = self.stock_positions.loc[(
                self.stock_positions['volume_long_his'] > 0) | (self.stock_positions['volume_long_today'] > 0)]
            self.stock_positions['float_profit'] = (self.stock_positions['last_price'] - self.stock_positions['position_price_long']) * (
                self.stock_positions['volume_long_his']+self.stock_positions['volume_long_today'])
        self.stock_positions.reset_index(inplace=True)
        self.print()

    def codelist(self):
        if len(self.stock_positions) > 0:
            return self.stock_positions['code'].to_list()
        else:
            return []

    def __repr__(self):
        return self.stock_positions


s = Strategy(code='000001', frequence='day',
             start='2019-03-01', end='2019-03-31', strategy_id='布林择时3日调仓')
s.run_backtest()
