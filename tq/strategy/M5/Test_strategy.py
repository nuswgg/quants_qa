#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'susir'

from contextlib import closing
from tqsdk import TqApi, TqAuth, TqSim

class Test_strategy:
    def __init__(self,
                 api,
                 symbolList,
                 ):
        self._api = api
        self._symbolList = symbolList
        self._tick = {}
        self._tickTask = {}
        for symbol in self._symbolList:
            self._tick[symbol] = self._api.get_tick_serial(symbol)
            self._tickTask[symbol] = self._api.register_update_notify(self._tick[symbol])

    async def _runOpen(self, symbol):
        async for _ in self._tickTask[symbol]:
            if self._api.is_changing(self._tick[symbol]):
                tick = self._tick[symbol].iloc[-1].copy()
                print("symbol: %s , ask_price1: %s" % (symbol, tick.ask_price1))
                # todo 想干啥就干啥。

    # def runStrategy(self):
    #     while True:
    #         for symbol in self._symbolList:
    #             self._api.create_task(self._runOpen(symbol))
    #         while True:
    #             self._api.wait_update()


    def runStrategy(self):
        while True:
            self._api.wait_update()
            for symbol in self._symbolList:
                self._api.create_task(self._runOpen(symbol))


if __name__ == '__main__':
    symbolList01 = ['SHFE.ni2106', 'SHFE.ni2107']
    api01 = TqApi(TqSim(init_balance=100000), auth=TqAuth("nuswgg", "541278"))
    test_strategy01 = Test_strategy(api=api01, symbolList=symbolList01)
    with closing(test_strategy01._api):
        test_strategy01.runStrategy()