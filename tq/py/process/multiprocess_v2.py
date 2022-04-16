# use join

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
    f1=Process(target=func,args=('f1',2,10),kwargs={'c':5,'d':6})
    f2=Process(target=func,name='mm',args=('f2',6,100),kwargs={'c':7,'d':8})
    f3=Process(target=func,name='nn',args=('f3',10,200),kwargs={'c':9,'d':10},daemon=True)
    t0=time.time()
    f1.start()
    print('f1执行状态:',f1.is_alive())
    f1.join()  #let f1 finish
    #time.sleep(10)
    print('f1执行状态:',f1.is_alive())
    #f3.daemon=True
    f2.start()
    f3.start()
    print('f2执行状态:',f2.is_alive())
    f2.join(2)  #wait for 2 sec
    f2.terminate()
    f2.join()
    #time.sleep(10)
    print('f2执行状态:',f2.is_alive())
    print('子进程f1的名字:{0},pid:{1}'.format(f1.name,f1.pid))
    print('子进程f2的名字:{0},pid:{1}'.format(f2.name,f2.pid))
    print('子进程f3的名字:{0},pid:{1}'.format(f3.name,f3.pid))
    print('父进程的x:',x)
    print('父进程执行结束，用时:',time.time()-t0)

# f1执行状态: True
# 开始执行子进程: f1
# 子进程f1的id：22784,父进程的id:21820
# c+d: 11
# 子进程f1的x: 10
# 子进程f1执行结束,用时: 2.000809907913208
# f1执行状态: False
# f2执行状态: True
# 开始执行子进程: f2
# 子进程f2的id：21208,父进程的id:21820
# c+d: 15
# 子进程f2的x: 100
# 开始执行子进程: f3
# 子进程f3的id：23544,父进程的id:21820
# c+d: 19
# 子进程f3的x: 200
# f2执行状态: False
# 子进程f1的名字:Process-1,pid:22784
# 子进程f2的名字:mm,pid:21208
# 子进程f3的名字:nn,pid:23544
# 父进程的x: 60
# 父进程执行结束，用时: 4.316863298416138

