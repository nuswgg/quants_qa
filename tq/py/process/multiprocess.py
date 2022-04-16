import time,os
from multiprocessing import Process
def func(a,b,y,c=3,d=4):
    print('开始执行子进程:',a)
    print('子进程'+a+'的id：{0},父进程的id:{1}'.format(os.getpid(),os.getppid()))
    global x
    x=y
    t0=time.time()
    print('c+d:',c+d)
    print('子进程'+a+'的x:',x)
    time.sleep(b)
    print('子进程'+a+'执行结束,用时:',time.time()-t0)

if __name__ == '__main__':
    x=60
    f1=Process(target=func,args=('f1',3,10),kwargs={'c':5,'d':6})
    f2=Process(target=func,name='mm',args=('f2',5,100),kwargs={'c':7,'d':8})
    t0=time.time()
    f1.start()
    f2.start()
    print('子进程f1的名字:{0},pid:{1}'.format(f1.name,f1.pid))
    print('子进程f2的名字:{0},pid:{1}'.format(f2.name,f2.pid))
    print('父进程的x:',x)
    print('父进程执行结束，用时:',time.time()-t0)

    # 子进程的pid即可以用属性pid获取也可以用os.getpid()
    # 获取，父进程的pid可用os.getppid()
    # 获取