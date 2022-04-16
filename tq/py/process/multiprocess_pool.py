# Pool（进程池）用来控制一次同时执行的进程数量。
# 进程池的大小不要超过CPU的数量，调用方法Pool()返回一个进程池对象，调用如下：
# pool = Pool(2)

import time,os
from multiprocessing import Pool
def func1(a,b,c=3,d=4):
    print('f1开始执行,子进程id:{0}，传入参数：{1}'.format(os.getpid(),a))
    time.sleep(b)
    a*=2
    c*=2
    d*=2
    print('f1执行结束,子进程id:{0}，传入参数执行结果：{1}'.format(os.getpid(),a))
    return a,c,d
def func2(x):
    print('f2开始执行,子进程id:{0}，传入参数：{1}'.format(os.getpid(),x))
    time.sleep(3)
    x*=2
    print('f2执行结束,子进程id:{0}，传入参数执行结果：{1}'.format(os.getpid(),x))
    return x
if __name__ == '__main__':
    pool1=Pool(2)
    pool2=Pool(2)
    pool3=Pool(2)
    x='abcdef'
    y=[1,2,3,4,5,6]
    z='jklmn'
    r1=[]
    t0=time.time()
    for i in y:
        r=pool1.apply_async(func=func1,args=(i,3),kwds={'c':5,'d':6})
        r1.append(r)
    r2=pool2.map_async(func2,x)
    r3=pool3.map(func2,z)
    while True:
        if time.time()-t0>=5:
            pool1.close()
            pool2.terminate()
            pool3.close()
            pool1.join()
            pool2.join()
            pool3.join()
            print('pool1进程返回值：',[r.get() for r in r1])
            print('pool2进程返回值：', r2.get())
            print('pool3进程返回值：',r3)
            break
    print('父进程执行结束，用时:',time.time()-t0)
