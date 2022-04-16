# Event（事件）的机制为：
# 全局定义一个“事件”，如果“事件”值为 False，那么当进程执行wait()方法时就会阻塞，
# 如果“事件”值为True，那么执行wait()方法时便不再阻塞，即wait()是否阻塞依赖于“事件”的值，
# 阻塞时需等待“事件”值变为True而“放行”，因此，进程中可以通过设置“事件”值来决定另一进程对同一数据的访问。
# 下面的例子 event 是绿灯

import time,random
from multiprocessing import Process, Event
def light(event):
    while True:  # 循环检查红绿灯
        if event.is_set():  # True代表绿灯,False代表红灯
            print('是绿灯，放行，3秒后转为红灯')
            time.sleep(3)  # 所以在这让灯等5秒钟，这段时间让车过
            event.clear()  # 把事件状态设置为False
        else:
            print('是红灯，禁行，6秒后转为绿灯')
            time.sleep(6)
            event.set()  # 将事件状态设置为True
def car(event,number):
    event.wait()
    print('是绿灯，车牌号{0}放行'.format(number))
if __name__ == '__main__':
    event=Event() #实例化事件类
    bright=Process(target=light,args=(event,)) #红绿灯进程
    bright.start()
    for i in 'abcde':
        time.sleep(random.randint(1,2))  # 车辆在2秒内随机出现
        c=Process(target=car,args=(event,i))
        c.start()

