""""
Function: 爬取结算参数（数据来源：天勤、SHFE、DCE、CZCE）和CFMMC账单并存盘，计算生成风控参数
Author: 虎歌
Date: 2020-08-02
Environment:  python3.8
"""

import time
import os
import requests
import json
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay


datapath = 'D:\\交易修炼\\交易分析\\交易参数\\'


def calendar(periods=200, end = time.strftime("%Y%m%d", time.localtime(time.time()-(15*60*60+15*60)))):
    # 读取holiday文件内容自动生成交易日历，每年需维护一次'holiday.txt'，追加法定假日定义
    # print('开始获取交易日历...')
    with open(r'D:\交易修炼\交易量化\PycharmProjects\HugeTrader\holiday.txt', 'r') as f:
        freq = CustomBusinessDay(holidays=f.read().split('\n'))
    c=pd.bdate_range(end=end, periods=periods, freq=freq)
    # print('交易日历已获取')
    return c


def pth(exchange_id, date):
    """
    功能：根据交易所及交易日期生成带路径的json存储文件名
    :param exchange_id: 'DCE' 或 'SHFE' 或 'CZCE' 或 'MarginRate' 或 'TQ' 或 '品种参数'
    :param date: 交易日期（'YYMMDD'格式），exchange_id为 'TQ' 或 '品种参数' 时忽略
    :return: 带路径的json存储文件名
    """
    a = datapath
    if exchange_id in ['TQ','品种参数']:
        c = a + exchange_id + '.json'
        return c
    b = a+date[0:4]
    if not os.path.exists(b):
        os.mkdir(b)
    b = b + '\\' + exchange_id
    if not os.path.exists(b):
        os.mkdir(b)
    c = b + '\\' + exchange_id + date + '.json'
    return c


def dce_trade_para(dt=time.strftime("%Y%m%d", time.localtime())):
    filename = pth('DCE', dt)
    if os.path.exists(filename):
        with open(filename, 'r',encoding='utf-8') as f:
            para = json.load(f)
        return para
    url = 'http://www.dce.com.cn/publicweb/businessguidelines/exportFutAndOptSettle.html'
    formdata = {
        'variety': 'all',
        'trade_type': '0',
        'year': dt[:4],
        'month': str(int(dt[4:6]) - 1),
        'day': dt[6:],
        'exportFlag': 'txt'
    }
    res = requests.post(url, data=formdata)
    if res.status_code == 200:
        a = res.content.decode().replace('\t\t', '\t').split('\r\n')
        colname = a[2].split('\t')
        n = len(colname) - 1
        # print(colname)
        tadict = {}
        for i in range(3, len(a) - 1):
            b = a[i].split('\t')
            rowdict = {}
            for j in range(n):
                rowdict[colname[j]] = b[j]
            tadict[b[1]] = rowdict
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tadict, f, ensure_ascii=False)
            print('DCE', dt, '交易参数 已转存', filename)
        return tadict
    else:
        print(f'{res.status_code} DCE {dt} 交易参数爬取失败')
        return None


def shfe_trade_para(dt=time.strftime("%Y%m%d", time.localtime())):
    filename = pth('SHFE', dt)
    if os.path.exists(filename):
        with open(filename, 'r',encoding='utf-8') as f:
            para = json.load(f)
        return para
    url = 'http://www.shfe.com.cn/data/instrument/Settlement' + dt + '.dat'
    header = {
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    res = requests.get(url, headers=header)
    if res.status_code == 200:
        talist = res.json()['Settlement']
        tadict = {v['INSTRUMENTID']:v for v in talist}
        with open(filename,'w',encoding='utf-8') as f:
            json.dump(tadict,f,ensure_ascii=False)
            print('SHFE', dt, '交易参数 已转存',filename)
        return tadict
    else:
        print(f'{res.status_code} SHFE {dt} 交易参数爬取失败')
        return None


def czce_trade_para(dt=time.strftime("%Y%m%d", time.localtime())):
    filename = pth('CZCE', dt)
    if os.path.exists(filename):
        with open(filename, 'r',encoding='utf-8') as f:
            para = json.load(f)
        return para
    url = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/' + dt[:4] + '/' + dt + '/FutureDataClearParams.txt'
    res = requests.get(url)
    code = 'ANSI' if dt<'20171228' else 'utf-8'
    if res.status_code == 404:
        print(f'{res.status_code} CZCE {dt} 交易参数爬取失败')
        return None
    else:
        a = res.content.decode(encoding=code).replace(' ', '').split('\r\n')
        colname = a[1].split('|')
        n = len(colname)
        tadict = {}
        for i in range(2, len(a) - 1):
            b = a[i].split('|')
            rowdict = {}
            for j in range(n):
                rowdict[colname[j]] = b[j]
            tadict[b[0]] = rowdict
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tadict, f, ensure_ascii=False)
            print('CZCE', dt, '交易参数 已转存', filename)
        return tadict


def margin_rate(dt=time.strftime("%Y%m%d", time.localtime())):
    exchange_id = 'MarginRate'
    filename = pth(exchange_id, dt)
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            mr = json.load(f)
        return mr

    mr = {}
    if os.path.exists(pth('CZCE', dt)):
        with open(pth('CZCE', dt), 'r', encoding='utf-8') as f:
            ta_czce = json.load(f)
    else:
        ta_czce = czce_trade_para(dt)
    mr_field = '买交易保证金率(%)' if dt <= '20190830' else '交易保证金率(%)'
    mr.update({k: float(ta_czce[k][mr_field]) / 100 for k in sorted(ta_czce.keys())})

    if os.path.exists(pth('DCE',dt)):
        with open(pth('DCE',dt),'r',encoding='utf-8') as f:
            ta_dce = json.load(f)
    else:
        ta_dce = dce_trade_para(dt)
    mr.update({k:float(int(ta_dce[k]["投机买保证金率"][:-1])/100) for k in sorted(ta_dce.keys())})

    if os.path.exists(pth('SHFE',dt)):
        with open(pth('SHFE',dt),'r') as f:
            ta_shfe = json.load(f)
    else:
        ta_shfe = shfe_trade_para(dt)
    mr.update({k:float(ta_shfe[k]["LONGMARGINRATIO"]) for k in sorted(ta_shfe.keys())})

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(mr, f, ensure_ascii=False)
        print(exchange_id, dt, '已转存', filename)
    return mr

if __name__ == '__main__':
    t0 = time.time()
    cal = calendar()
    # print(cal)
    print(f"当前交易日{cal[-1].strftime('%Y-%m-%d')}")
    mr = margin_rate()
    print(mr)

    mr = margin_rate('20201204')
    print(mr)


    print(f"总耗时 {time.time() - t0:.3f} 秒")