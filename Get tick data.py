# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2018-2020 azai/Rgveda/GolemQuant base on QUANTAXIS/yutiansut
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json
import sys
import websocket
import easyquotation
import datetime
import time as timer
import numba as nb

try:
    import QUANTAXIS as QA
    from QUANTAXIS.QAUtil.QAParameter import ORDER_DIRECTION
    from QUANTAXIS.QAUtil.QASql import QA_util_sql_mongo_sort_ASCENDING
    from QUANTAXIS.QAUtil.QADate_trade import (
        QA_util_if_tradetime,
        QA_util_get_pre_trade_date,
        QA_util_get_real_date,
        trade_date_sse
    )
    from QUANTAXIS.QAData.QADataStruct import (
        QA_DataStruct_Index_min,
        QA_DataStruct_Index_day,
        QA_DataStruct_Stock_day,
        QA_DataStruct_Stock_min
    )
    from QUANTAXIS.QAIndicator.talib_numpy import *
    from QUANTAXIS.QAUtil.QADate_Adv import (
        QA_util_timestamp_to_str,
        QA_util_datetime_to_Unix_timestamp,
        QA_util_print_timestamp
    )
    from QUANTAXIS.QAUtil import (
        DATABASE,
        QASETTING,
        QA_util_log_info,
        QA_util_log_debug,
        QA_util_log_expection,
        QA_util_to_json_from_pandas
    )
    from QUANTAXIS.QASU.main import (
        QA_SU_save_etf_day,
        QA_SU_save_etf_min,
        QA_SU_save_financialfiles,
        QA_SU_save_index_day,
        QA_SU_save_index_min,
        QA_SU_save_stock_block,
        QA_SU_save_stock_day,
        QA_SU_save_stock_info,
        QA_SU_save_stock_info_tushare,
        QA_SU_save_stock_list,
        QA_SU_save_stock_min,
        QA_SU_save_stock_xdxr,
        QA_SU_save_future_day,
        QA_SU_save_future_day_all,
        QA_SU_save_future_min,
        QA_SU_save_future_min_all
    )
except:
    print('PLEASE run "pip install QUANTAXIS" to call these modules')
    pass


def formater_l1_tick(code:str, l1_tick:dict)->dict:
    """
    处理分发 Tick 数据，新浪和tdx l1 tick差异字段格式化处理
    """
    l1_tick['code'] = code
    l1_tick['servertime'] = l1_tick['time']
    l1_tick['datetime'] = '{} {}'.format(l1_tick['date'], l1_tick['time'])
    l1_tick['price'] = l1_tick['now']
    l1_tick['vol'] = l1_tick['volume']
    del l1_tick['date']
    del l1_tick['time']
    del l1_tick['now']
    del l1_tick['name']
    del l1_tick['volume']
    #print(l1_tick)
    return l1_tick


def formater_l1_ticks(l1_ticks:dict)->dict:
    """
    处理 l1 ticks 数据
    """
    l1_ticks_data = []
    for code, l1_tick_values in l1_ticks.items():
        #l1_tick = namedtuple('l1_tick', l1_ticks[code])
        #formater_l1_tick_jit(code, l1_tick)
        l1_tick = formater_l1_tick(code, l1_tick_values)
        l1_ticks_data.append(l1_tick)

    return l1_ticks_data


@nb.jit(nopython=True)
def formater_l1_ticks_jit(l1_ticks:dict)->dict:
    """
    我是阿财，我专门挖坑，所以这个函数我未调试完成
    处理分发 Tick 数据，新浪和tdx l1 tick差异字段格式化处理
    因为l1 tick数据必须2秒内处理完毕，尝试优化可能性，Cython或者JIT
    """
    l1_ticks_data = []
    for code in l1_ticks:
        l1_tick = namedtuple('l1_tick', l1_ticks[code])
        #formater_l1_tick_jit(code, l1_tick)
        #l1_tick = formater_l1_tick(code, l1_ticks[code])
        #l1_data = pd.DataFrame(l1_tick, index=['datetime'])
        #l1_data['code'] = code
        #l1_data = l1_data.rename({'time':'servertime', 'now':'price'})
        #l1_tick = namedtuple('l1_tick', l1_tick._fields+('code',))
        l1_tick['code'] = code
        l1_tick['servertime'] = l1_tick['time']
        l1_tick['datetime'] = '{} {}'.format(l1_tick['date'], l1_tick['time'])
        l1_tick['price'] = l1_tick['now']
        l1_tick['vol'] = l1_tick['volume']
        del l1_tick['date']
        del l1_tick['time']
        del l1_tick['now']
        del l1_tick['name']
        del l1_tick['volume']
        #del l1_tick['name']
        #print(l1_tick)
        #return l1_tick
        l1_ticks_data.append(l1_tick)

    return l1_ticks_data


def sub_l1_from_sina():
    """
    从新浪获取L1数据，3秒更新一次，建议mongodb数据库存放在企业级SSD上面
    （我用Intel DC P3600 800GB SSD，锐龙 3900X，每个tick 保存时间 < 0.6s）
    """
    def collections_of_today():
        database = DATABASE.get_collection('realtime_{}'.format(datetime.date.today()))
        database.create_index([('code', QA_util_sql_mongo_sort_ASCENDING)])
        database.create_index([('datetime', QA_util_sql_mongo_sort_ASCENDING)])
        database.create_index(
            [
                ("code",
                    QA_util_sql_mongo_sort_ASCENDING),
                ("datetime",
                    QA_util_sql_mongo_sort_ASCENDING)
            ],
            #unique=True,
        )
        return database

    def save_X_func():
        """
        QUANTAXIS的save X，建议每天下午四~五点收盘后执行
        """

        pass

    quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']

    sleep_time = 2.0
    sleep = int(sleep_time)
    _time1 = datetime.datetime.now()
    database = collections_of_today()
    get_once = True
    # 开盘/收盘时间
    end_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+' 16:30', '%Y-%m-%d %H:%M')
    start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 09:15', '%Y-%m-%d %H:%M')
    day_changed_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 01:00', '%Y-%m-%d %H:%M')
    while (datetime.datetime.now() < end_time):
        # 开盘/收盘时间
        end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 16:30', '%Y-%m-%d %H:%M')
        start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 09:15', '%Y-%m-%d %H:%M')
        day_changed_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 01:00', '%Y-%m-%d %H:%M')
        _time = datetime.datetime.now()

        if (datetime.datetime.now() < day_changed_time):
            # 日期变更，写入表也会相应变更，这是为了防止用户永不退出一直执行
            print(u'当前日期更新~！ {} '.format(datetime.date.today()))
            database = collections_of_today()

        if QA_util_if_tradetime(_time) or \
            (get_once):  # 如果在交易时间
            l1_ticks = quotation.market_snapshot(prefix=False)
            l1_ticks_data = formater_l1_ticks(l1_ticks)

            if (datetime.datetime.now() < start_time):
                print(u'Not Trading time 现在是中国A股收盘时间 {}'.format(_time))
                timer.sleep(sleep)
                continue

            # 查询是否新 tick
            query_id = {
                "code": [l1_tick['code'] for l1_tick in l1_ticks_data],
                "datetime": {
                    '$in': [l1_tick['datetime'] for l1_tick in l1_ticks_data]
                }
            }
            refcount = database.count_documents(query_id)
            if refcount > 0:
                if (len(l1_ticks_data) > 1):
                    # 删掉重复数据
                    database.delete_many(query_id)
                    database.insert_many(l1_ticks_data)
                else:
                    # 持续更新模式，更新单条记录
                    database.replace_one(query_id, l1_ticks_data[0])
            else:
                # 新 tick，插入记录
                database.insert_many(l1_ticks_data)
            if (get_once != True):
                print(u'Trading time now 现在是中国A股交易时间 {}\nProcessing ticks data cost:{:.3f}s'.format(datetime.datetime.now(),
                    (datetime.datetime.now() - _time).total_seconds()))
            timer.sleep(sleep)
            print('Program Last Time {:.3f}s'.format(
                (datetime.datetime.now() - _time1).total_seconds()))
            get_once = False
        else:
            print(u'Not Trading time 现在是中国A股收盘时间 {}'.format(_time))
            timer.sleep(sleep)

    # 每天下午5点，代码就会执行到这里，如有必要，再次执行收盘行情下载，也就是 QUANTAXIS/save X
    save_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 17:00', '%Y-%m-%d %H:%M')
    if (datetime.datetime.now() > end_time) and \
        (datetime.datetime.now() < save_time):
        # 收盘时间 下午16:00到17:00 更新收盘数据
        QA_SU_save_stock_day('tdx')
        QA_SU_save_stock_xdxr('tdx')
        QA_SU_save_stock_min('tdx')
        QA_SU_save_index_day('tdx')
        QA_SU_save_index_min('tdx')
        QA_SU_save_etf_list('tdx')
        QA_SU_save_etf_day('tdx')
        QA_SU_save_etf_min('tdx')
        QA_SU_save_stock_list('tdx')
        QA_SU_save_index_list('tdx')
        QA_SU_save_stock_block('tdx')
        QA_SU_save_future_list('tdx')

    # While循环每天下午5点自动结束，在此等待13小时，大概早上六点结束程序自动重启
    print(u'While循环每天下午5点自动结束，在此等待13小时，大概早上六点结束程序自动重启，这样只要窗口不关，永远每天自动收取 tick')
    timer.sleep(30000)


def sub_1min_from_tencent_lru():
    """
    我是阿财，我专门挖坑，所以这个函数我未调试完成
    从腾讯获得当天交易日分钟K线数据
    """
    blocks = ['MSCI中国',
              '沪深300',
              '上证380',
              '深证300',
              '上证50',
              '上证电信',
              '电信等权',
              '上证100',
              '上证150',
              '沪深300',
              '中证100',
              '中证500',
              '全指消费',
              '中小板指',
              '创业板指',
              '综企指数',
              '1000可选',
              '国证食品',
              '深证可选',
              '深证消费',
              '深成消费',
              '中证酒',
              '中证白酒']
    all_stock_blocks = QA.QA_fetch_stock_block_adv()
    for blockname in blocks:
        if (blockname in all_stock_blocks.block_name):
            codelist_300 = all_stock_blocks.get_block(blockname).code
            print(u'QA预定义板块“{}”成分数据'.format(blockname))
            print(codelist_300)
        else:
            print(u'QA默认无板块“{}”成分数据'.format(blockname))

    quotation = easyquotation.use("timekline")
    data = quotation.real([codelist], prefix=False)
    while (True):
        l1_tick = quotation.market_snapshot(prefix=False)
        print(l1_tick)

    return True


if __name__ == '__main__':
    # 从新浪财经获取tick数据，自动启停，
    # 无限轮询的任何程序都可能会断线，我没有处理异常，所以断线就会抛出异常退出，
    # 我认为这样最好，可以释放意外占用的TCP/IP半连接，避免无人值守的服务器耗尽
    # 端口资源。建议使用我的土味无限循环脚本，等于3秒后自动重试：
    """
    举个例子，例如这个sub.py脚本保存在 D:\代码\QUANTAXIS\QUANTAXIS\cli 
    目录下面，并且创建一个空的 __init__.py，对同级2个文件__init__.py， 
    还有这个文件保存成 __main__.py，没有你就新建一个。
    创建一个PowerShell：sub_l1.ps1
        D:
        CD D:\代码\QUANTAXIS\

        $n = 1
        while($n -lt 6)
        {
	        python -m QUANTAXIS.cli
	        Start-Sleep -Seconds 3
        }

    创建一个Cmd/Batch：sub_l1.cmd
        D:
        CD D:\代码\QUANTAXIS\

        :start
        python -m QUANTAXIS.cli

        @ping 127.0.0.1 -n 3 >nul

        goto start

        pause

    Linux Bash脚本我不会，你们能用linux肯定会自己编写。
    """

    sub_l1_from_sina()
    # sub_1min_from_tencent_lru()
    pass
``` 标记代码块



# 读取 l1行情，转换K线数据——参考我的旧帖子：http://www.yutiansut.com:3000/topic/5ee1905c5778f910c1ba6c03