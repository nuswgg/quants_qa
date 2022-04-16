import asyncio 
import time
from tqsdk import TqApi,TqAccount

#建立协程池
loop=asyncio.get_event_loop()

#将协程池传参给天勤,让天勤使用这个协程池,
api=TqApi( TqAccount("simnow","040123","123456") , auth="270829786@qq.com,24729220a",loop=loop)

#定义一个协程
async def 下单n秒不成功就撤单(订单id,n):
    await asyncio.sleep(n)
    订单=api.get_order(订单id)
    if 订单.volume_left>0:
        api.cancel_order(订单id)


#下面开启循环
n=0
while True:
    切片=api.get_quote("SHFE.rb2101")
    if n==0:
        n+=1
        订单=api.insert_order("SHFE.rb2101","BUY","OPEN",1,切片.lower_limit)
        #将协程任务加入 协程池子
        api.create_task(下单n秒不成功就撤单(订单.order_id,10))
    api.wait_update()
    