# https://zhuanlan.zhihu.com/p/340809344


#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import multiprocessing
from datetime import datetime, time
from time import sleep
from tqsdk import TqApi, TqAuth, TqAccount

# 交易时段
day_start = time(8, 45)  # 上午
day_end = time(15, 15)  # 下午
night_start = time(20, 45)  # 夜盘
night_end = time(2, 30)  # 凌晨


# 交易时段函数
def Trading_time():
    now = datetime.now()  # 当前日期时间
    trading = False
    # 白盘夜盘周一至周五，凌晨周二至周六
    if (day_start <= now.time() <= day_end or night_start <= now.time()) and now.weekday() <= 4 \
            or (now.time() <= night_end and 0 < now.weekday() <= 5):
        trading = True
    return trading


# 策略子进程
def Cta():
    api = TqApi(TqAccount('H期货公司', '账号', '密码'), auth=TqAuth("天勤账号", "密码"))
    quote1 = api.get_quote('CZCE.SR105')  # 品种行情
    quote2 = api.get_quote('SHFE.rb2105')

    # 循环判断是否处于交易时间，非交易时间关闭api
    while True:
        print(quote1.last_price, quote1.instrument_id)
        print(quote2.last_price, quote2.instrument_id)
        trading = Trading_time()
        print(datetime.now(), '子进程')  # 策略子进程当前日期时间
        if not trading:  # 非交易时间关闭api
            api.close()
            print("关闭子进程")
            break  # 退出循环结束进程
        api.wait_update()


def Main():
    child_process = None
    while True:
        trading = Trading_time()
        print(datetime.now(), '父进程')  # 父进程当前日期时间
        # 交易时段启动策略
        # 子进程崩溃也可用下句条件重启
        # if trading and (child_process == None or isinstance(child_process,multiprocessing.Process) and not child_process.is_alive()):
        if trading and child_process == None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=Cta)
            child_process.start()
            print("子进程启动成功")
        # 非交易时段退出子进程
        if not trading and child_process != None:
            if not child_process.is_alive():  # 子进程已结束
                child_process = None
                print("子进程关闭成功")
            elif child_process.is_alive():
                child_process.terminate()  # 子进程被阻塞，强制关闭进程，api未关闭不会报错
                child_process = None
                print("子进程强制关闭")

        sleep(300)  # 5分钟检查一次


if __name__ == "__main__":
    Main()