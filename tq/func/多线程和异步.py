#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from tqsdk import TqApi, TqAuth, TqAccount #, TargetPosTask
import asyncio
import threading

#多线程类
class WorkerThread(threading.Thread):
    '''
    1，主要用于依赖某个业务更新动态启动多品种策略的情况，比如随着账户持仓的变化启动各持仓品种的风控
    2，多品种策略不需要依赖自身业务更新时，推荐使用异步协程
    '''
    def __init__(self, api,data=[],func1=[],func2=[],**job):
        threading.Thread.__init__(self)
        self.api = api #传入天勤实例副本
        self.data = data #需要更新的业务数据，如行情、账户，可传入列表
        self.func1 = func1 #随着业务更新需要执行的函数列表
        self.func2 = func2 #自带业务更新的异步协程函数列表
        self.job = job   #func函数需要的参数，不定关键字参数
    async def execute(self): #业务更新函数，为了保持线程代码块简洁性和自由性，业务更新采用了注册Tqchan方式
        async with self.api.register_update_notify(self.data) as update_chan: #业务注册到channel
            async for _ in update_chan:#
                e = 0
                for f in self.func1:
                    e += f(api=self.api,**self.job) #返回值True保持业务更新，重复调用函数，全部返回值False退出业务更新，全部函数返回值必须一致
                #也可以self.func1[index](api=self.api,**self.job)逐一调用
                if not e : break
    def run(self):
        task1 = self.api.create_task(self.execute()) #
        task2 = []
        for f in self.func2: #线程中创建异步协程
            task2.append(self.api.create_task(f(api=self.api,data=self.data,**self.job))) #func2为协程，直接创建协程任务
        #也可以self.api.create_task(self.func2[index](api=self.api,data=self.data,**self.job))逐一调用
        while True :
            if task1.done() and all([t.done() for t in task2]) :break
            self.api.wait_update()

#策略协程
#async def CTA(api,data,**job):
async def CTA(quote):
    async with api.register_update_notify(quote) as update_chan:  # 当 quote 有更新时会发送通知到 update_chan 上
        async for _ in update_chan:  # 当从 update_chan 上收到业务更新通知时执行策略
            if quote.last_price > 1000:
                print(quote.instrument_id)
#策略函数
def cat1(api,**job):
    if job['p1'].pos_long > 0: #有多单
        print(job['quote1'].ask_price1)
    if job['p1'].pos_short > 0: #有空单
        print(job['quote1'].bid_price1,job['quote1'].instrument_id,'有空单')
    if job['p1'].pos_long + job['p1'].pos_short == 0: #没有持仓
        print('没有持仓',job['quote1'].instrument_id)
        return False
    elif job['p1'].pos_long + job['p1'].pos_short > 0:return True
def cat2(api,**job):
    if job['p2'].pos_long > 0: #有多单
        print(job['quote2'].ask_price1)
    if job['p2'].pos_short > 0: #有空单
        print(job['quote2'].bid_price1,job['quote2'].instrument_id,'有空单')
    if job['p2'].pos_long + job['p2'].pos_short == 0: #没有持仓
        print('没有持仓',job['quote2'].instrument_id)
        return False
    elif job['p2'].pos_long + job['p2'].pos_short > 0:return True

#天勤账户主实例
api = TqApi(TqAccount('H期货公司','账号','密码'),auth=TqAuth("天勤账号", "密码"))
quote1 = api.get_quote('CZCE.SR105') #品种行情
position1 = api.get_position('CZCE.SR105') #品种持仓
quote2 = api.get_quote('SHFE.rb2105')
position2 = api.get_position('SHFE.rb2105')

#创建多线程
#thread1 = WorkerThread(api.copy(),[quote1,position1],[cat1,cat2],quote1=quote1,p1=position1,quote2=quote2,p2=position2)
thread1 = WorkerThread(api.copy(),[quote1,position1],[cat1],quote1=quote1,p1=position1)#创建线程实例
thread2 = WorkerThread(api.copy(),[quote2,position2],[cat2],quote2=quote2,p2=position2)
#thread1 = WorkerThread(api.copy(),[quote1,position1],func2=[CTA],quote1=quote1,p1=position1)#线程+协程
thread1.start() #启动线程
thread2.start()

#创建协程任务
api.create_task(CTA(quote=quote1))
api.create_task(CTA(quote=quote2))
while True:
    api.wait_update()