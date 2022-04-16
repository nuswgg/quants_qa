import asyncio 
import time
from tqsdk import TqApi,TqAccount

#建立协程池
loop=asyncio.get_event_loop()

#将协程池传参给天勤,让天勤使用这个协程池,
api=TqApi(  auth="270829786@qq.com,24729220a",loop=loop)

#定义一个协程,每间隔10秒,打印一下时间戳
async def myprint(n):
    while True:
        print(time.time(),n)
        await asyncio.sleep(10)
#将协程任务加入 协程池子
api.create_task(myprint(1))

api.create_task(myprint(2))
#下面开启循环
while True:
    api.wait_update()
    