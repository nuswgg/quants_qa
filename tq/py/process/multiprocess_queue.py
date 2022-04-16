# Queue（队列）实现多进程之间的数据传递，Queue是多进程安全的队列，不会出现多个进程竞争数据导致出现错误的情况。
# Queue()有个可选参数maxsize，表示队列中数据的最大数量，如果省略此参数则无大小限制。
# 用Queue()传递数据类似生产者和消费者模型，生产者向队列插入数据，消费者从队列取出数据。
# 队列的数据是先进先出的（FIFO，first-in，first-out），即先插入的数据先被取出。
# method as below
# put
# get
# get_nowait
# qsize
# empty
# full
# close
# cancel_join_thread
# join_thread

import time
import datetime
from multiprocessing import Process, Queue
def consumer(queue,n):   #消费者
    for i in range(3):
        time.sleep(1)
        v=queue.get()
        # v=queue.get_nowait() # it will report err as queue is empty
        print(n+'消耗了值：',v)
def producer(queue,n):  #生产者
    for i in range(6):
        time.sleep(1)
        print(n + ' start {0}'.format(datetime.datetime.now()))
        queue.put(i)
        print(n+'生产了值：',i)
if __name__ == '__main__':
    queue=Queue(2)
    c1=Process(target=consumer,args=(queue,'c1'))
    c2=Process(target=consumer,args=(queue,'c2'))
    p=Process(target=producer,args=(queue,'p'))
    c1.start()  #queue is empty
    c2.start() # queue is empty
    p.start()
    print('queue empty is {0}'.format(queue.empty()))