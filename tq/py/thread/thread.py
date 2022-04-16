# 线程由threading模块的Thread类创建
# Thread类的属性和方法有：
#
# start():启动线程，它安排run() 方法在一个独立的控制进程中被调用，以执行子线程函数。
# run()：实际执行线程函数
# is_alive():判断线程是否存活状态，存活状态返还True，否则返回False。
# setName(str):设置线程名。
# getName():返回线程名，也可用name属性获取或者修改。
# join(timeout=None)：阻塞主线程，等待子线程执行结束。若给定timeout值，为超时时间，超过timeout不再阻塞。必须用start()启动线程才能使用join()方法。


import time
import threading
def func(a,b,y,c=3,d=4):
    print('开始执行子线程:',a,'c+d:',c+d)
    t0=time.time()
    global x
    x=y
    time.sleep(b)
    print('子线程'+a+'的x:',x)
    print('子线程'+a+'执行结束,用时:',time.time()-t0)
x=60
f1=threading.Thread(target=func,args=('f1',2,10),kwargs={'c':5,'d':6})
f2=threading.Thread(target=func,name='mm',args=('f2',6,100),kwargs={'c':7,'d':8})
f3=threading.Thread(target=func,name='nn',args=('f3',10,200),kwargs={'c':9,'d':10})
t0=time.time()
f1.setName('kk')
f1.start()
print('f1执行状态:',f1.is_alive())
f1.join()  # wait for f1 finish
print('f1执行状态:',f1.is_alive())
#f3.daemon=True
f2.start()
f3.start()
print('当前的线程变量:',threading.current_thread())
print('正在执行的线程列表:',threading.enumerate())
print('正在执行的线程数量',threading.active_count())
print('f2执行状态:',f2.is_alive())
f2.join(2)  # wait for 2 sec
print('f2执行状态:',f2.is_alive())
print('子线程f1的名字:{0},即:{1}'.format(f1.name,f1.getName()))
print('子线程f2的名字:{0},即:{1}'.format(f2.name,f2.getName()))
print('子线程f3的名字:{0},即:{1}'.format(f3.name,f3.getName()))
print('主线程的x:',x)
print('主线程执行结束，用时:',time.time()-t0)
