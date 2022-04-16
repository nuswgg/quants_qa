import asyncio
from time import time
from datetime import datetime


# 异步开平仓函数
async def OpenClose(api, quote={}, position={}, kaiping='', lot=0, price=None, advanced=None, che_time=0, block=False):
    '''
    api=TqApi(TqAccount('H期货公司','账号','密码'),auth=TqAuth("天勤账号", "密码"))
    quote=api.get_quote('SHFE.rb2105') #品种行情
    position=api.get_position('SHFE.rb2105') #品种持仓
    kaiping='pingduo' or 'pingkong'  or 'kaiduo' or 'kaikong'#下单方向，平多或者平空，开多或者开空
    lot=1 #下单手数
    price=None #下单价格，默认对手价，可设为停板价，买以涨停价，卖以跌停价
    advanced=None #指令模式，FAK为报单手数若部分成交剩下的撤单，有些策略需要在满足条件时下单，循环判断条件再下单，FAK可保证所有的持仓都满足条件
    che_time=0 #撤单等待时间，需为大于等于0的数值，表示委托单等待che_time秒还不成交则撤单，在advanced=None时有效，且block=True，建议advanced=None时设置撤单时间，在程序化中可以根据行情随时下单，提前挂单意义不大
    block=False，是否挂单，在advanced=None时有效，即当日有效单，False无需等待委托单是否完成,True则等待委托单完成,委托单完成包括成交完成或撤单
    '''
    symbol = quote.instrument_id  # 品种代码
    print(datetime.now(), '已经触发下单,品种:', symbol, '方向:', kaiping)
    if not price or price == '对手价':
        price_buy = quote.ask_price1
        price_sell = quote.bid_price1
    elif price == '停板价':
        price_buy = quote.upper_limit
        price_sell = quote.lower_limit
    elif price == price:
        price_buy = price_sell = price  # 其他限定价
    shoushu = 0  # 已成交手数
    junjia = 0.0  # 成交均价
    che_count = 0  # 主动撤单次数
    if kaiping == 'pingduo':  # 交易方向为平多
        if 0 < lot <= position.pos_long_today:  # 小于等于今仓，平今
            ping_jin = api.insert_order(symbol=symbol, direction='SELL', offset='CLOSETODAY', volume=lot,
                                        limit_price=price_sell, advanced=advanced)
        elif 0 < position.pos_long_today < lot <= position.pos_long:
            ping_zuo = api.insert_order(symbol=symbol, direction='SELL', offset='CLOSE',
                                        volume=lot - position.pos_long_today, limit_price=price_sell,
                                        advanced=advanced)  # 先平昨再平今
            ping_jin = api.insert_order(symbol=symbol, direction='SELL', offset='CLOSETODAY',
                                        volume=position.pos_long_today, limit_price=price_sell, advanced=advanced)
        elif 0 == position.pos_long_today < lot <= position.pos_long:
            ping_zuo = api.insert_order(symbol=symbol, direction='SELL', offset='CLOSE', volume=lot,
                                        limit_price=price_sell, advanced=advanced)
    elif kaiping == 'pingkong':  # 交易方向为平空
        if 0 < lot <= position.pos_short_today:  # 小于等于今仓，平今
            ping_jin = api.insert_order(symbol=symbol, direction='BUY', offset='CLOSETODAY', volume=lot,
                                        limit_price=price_buy, advanced=advanced)
        elif 0 < position.pos_short_today < lot <= position.pos_short:
            ping_zuo = api.insert_order(symbol=symbol, direction='BUY', offset='CLOSE',
                                        volume=lot - position.pos_short_today, limit_price=price_buy, advanced=advanced)
            ping_jin = api.insert_order(symbol=symbol, direction='BUY', offset='CLOSETODAY',
                                        volume=position.pos_short_today, limit_price=price_buy, advanced=advanced)
        elif 0 == position.pos_short_today < lot <= position.pos_short:
            ping_zuo = api.insert_order(symbol=symbol, direction='BUY', offset='CLOSE', volume=lot,
                                        limit_price=price_buy, advanced=advanced)

    elif kaiping == 'kaiduo':  # 交易方向为开多
        order = api.insert_order(symbol=symbol, direction='BUY', offset='OPEN', volume=lot, limit_price=price_buy,
                                 advanced=advanced)
    elif kaiping == 'kaikong':  # 交易方向为开空
        order = api.insert_order(symbol=symbol, direction='SELL', offset='OPEN', volume=lot, limit_price=price_sell,
                                 advanced=advanced)
    # 判断下单是否执行完，避免在某些代码中先前平仓开仓未执行完又重复下单
    try:
        t = time()  # 时间起点
            while ping_zuo.status != "FINISHED":  # 平昨单是否完成
            # if time() - t >= 1: break  #等待1秒还无法完成，网络可能断线无法返回订单信息，但订单可能已经成交，退出状态检查，但若未获取成交手数后续可能重复平仓
            if not advanced and not block: break  # 当日有效单，且无需等待是否完成
            if che_time and not advanced and time() - t >= che_time:
                api.cancel_order(ping_zuo)  # 等待che_time秒还不成交撤单，适用于advanced=None的情况
            await asyncio.sleep(0.1)  # 等待时间不应低于0.1秒，过快的查询可能出错
        if ping_zuo.volume_orign - ping_zuo.volume_left > 0:  # 有成交
            shoushu += ping_zuo.volume_orign - ping_zuo.volume_left  # 计算已成交手数
            junjia += ping_zuo.trade_price * (ping_zuo.volume_orign - ping_zuo.volume_left)
        elif ping_zuo.status == "FINISHED" and not advanced:
            che_count += 1  # 撤单次数增加
    except NameError as e:
        print("捕捉到名称错误异常：", e)
    except Exception as ex:
        print("捕捉到了异常:", ex)
    try:
        t = time()
        while ping_jin.status != "FINISHED":  # 平今单是否完成
            # if time() - t >= 1: break
            if not advanced and not block: break
            if che_time and not advanced and time() - t >= che_time:
                api.cancel_order(ping_jin)
            await asyncio.sleep(0.1)
        if ping_jin.volume_orign - ping_jin.volume_left > 0:
            shoushu += ping_jin.volume_orign - ping_jin.volume_left
            junjia += ping_jin.trade_price * (ping_jin.volume_orign - ping_jin.volume_left)
        elif ping_jin.status == "FINISHED" and not advanced:
            che_count += 1  # 撤单次数增加
    except NameError as e:
        print("捕捉到名称错误异常：", e)
    except Exception as ex:
        print("捕捉到了异常:", ex)
    try:
        t = time()
        while order.status != "FINISHED":  # 开仓是否完成
            # if time() - t >= 1: break  #等待1秒还无法完成，网络可能断线无法返回订单信息，但订单可能已经成交，退出状态检查，但若未获取成交手数后续可能重复平仓
            if not advanced and not block: break
            if che_time and not advanced and time() - t >= che_time:
                api.cancel_order(order)
            await asyncio.sleep(0.1)  # 等待时间不应低于0.1秒
        if order.volume_orign - order.volume_left > 0:
            shoushu += order.volume_orign - order.volume_left  # 计算已成交手数
            junjia = order.trade_price * shoushu
        elif order.status == "FINISHED" and not advanced:
            che_count += 1  # 撤单次数增加
    except NameError as e:
        print("捕捉到名称错误异常：", e)
    except Exception as ex:
        print("捕捉到了异常:", ex)
    if shoushu:
        junjia = junjia / shoushu  # 计算成交均价
    else:
        junjia = float('nan')
    print(datetime.now(), '已经成交手数:', shoushu, '成交均价:', junjia, '品种:', symbol, '方向:', kaiping)
    return shoushu, junjia, che_count, symbol, kaiping  # 返回成交手数、成交均价,和主动撤单次数，若无成交则均价为nan值