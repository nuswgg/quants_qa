# 子进程把返回值放入队列，再从队列中获取返回值，我们还可以用管道Pipe获取返回值

import time,os
from multiprocessing import Process, Pipe
def func1(a,b,conn,c=3,d=4):
    print('f1开始执行,子进程id:{0}，传入参数：{1}'.format(os.getpid(),a))
    time.sleep(b)
    a*=2
    c*=2
    d*=2
    print('f1执行结束,子进程id:{0}，传入参数执行结果：{1}'.format(os.getpid(),a))
    conn.send((a,c,d))
if __name__ == '__main__':
    conn1,conn2=Pipe()
    f1=Process(target=func1,args=(10,2,conn2),kwargs={'c':5,'d':6})
    f1.start()
    f1.join()
    print('子进程返回值是：',conn1.recv())
    conn1.close()
    conn2.close()

