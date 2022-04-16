# Pipe（管道）类似队列的变种，管道更形象的体现了进程间的通信，一个进程向另一个进程发数据，管道就像传输数据的通道，管道两端连接着收发数据的进程。

# 方法Pipe([duplex])返回一个元组(conn1, conn2)，代表管道的两端，
# 参数duplex为True(默认值)，表示管道是全双工模式，即conn1和conn2均可收发；
# duplex为False，表示管道是单工模式，即conn1只负责接收数据，conn2只负责发送数据。

# 单工(Simplex)：duplex=False 单工数据传输只支持数据在一个方向上传输，例如：电视、广播发送消息，观众接收消息。
# 半双工(Half Duplex)：半双工数据传输允许数据在两个方向上传输，但在某一时刻只允许数据在一个方向上传输，
#     它实际上是一种切换方向的单工通信；在同一时间只可以有一方接受或发送信息，例如：对讲机，同一时间只能有一方讲话。
# 全双工(Full Duplex)：duplex=True 全双工数据通信允许数据同时在两个方向上传输，因此，全双工通信是两个单工通信方式的结合，
#   它要求发送设备和接收设备都有独立的接收和发送能力；在同一时间可以同时接收和发送信息，实现双向通信，例如：电话通信，双方可同时说话。

import os
import time,datetime
from multiprocessing import Process,Pipe
def func1(conn,sendv,n1):
    for i in sendv:
        conn.send(i)
        print('{2} 子进程{0}发送了数据{1}'.format(os.getpid(),i,n1))
    print('func1 send {0}'.format(datetime.datetime.now()))
    while conn.poll(3):
        rc=conn.recv()
        print('{2} 子进程{0}收到了数据{1}'.format(os.getpid(),rc,n1))
    print('func1 rec {0}'.format(datetime.datetime.now()))
def func2(conn,sendv,n1):
    for i in sendv:
        time.sleep(1)
        conn.send(i)
        print('{2} 子进程{0}发送了数据{1}'.format(os.getpid(),i,n1))
    print('func2 send {0}'.format(datetime.datetime.now()))
    while conn.poll(3):
        rc=conn.recv()
        print('{2} 子进程{0}收到了数据{1}'.format(os.getpid(),rc,n1))
    print('func2 rec {0}'.format(datetime.datetime.now()))

if __name__ == '__main__':
    conn1,conn2=Pipe()
    sendv1='abcde'
    sendv2=[1,2,3,4,5]
    sendv3 = 'ABCDE'
    f1=Process(target=func1,args=(conn1,sendv1,'f1'))
    f2=Process(target=func2,args=(conn2,sendv2, 'f2'))
    f3 = Process(target=func1, args=(conn2, sendv3, 'f3'))
    f1.start()
    f2.start()
    # f3.start()
    f1.join()
    f2.join()
    # f3.join()
    conn1.close()
    conn2.close() #del conn1,conn2