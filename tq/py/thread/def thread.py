# 可以通过继承Thread类自定义线程类以实现个性化功能，自定义类需要在初始化函数里用super().__init__()先执行Thread类的初始化，
# 并重写run()方法，我们把上例改写，用自定义线程类创建子线程

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
    return c+d
class MyThread(threading.Thread):
    def __init__(self,target,args,kwargs):
        super().__init__()
        self.target=target
        self.args=args
        self.kwargs=kwargs
    def run(self):
        self.res=self.target(*self.args,**self.kwargs)
x=60
f1=MyThread(target=func,args=('f1',2,10),kwargs={'c':5,'d':6})
f2=MyThread(target=func,args=('f2',6,100),kwargs={'c':7,'d':8})
f3=MyThread(target=func,args=('f3',10,200),kwargs={'c':9,'d':10})
t0=time.time()
f1.setName('kk')
f1.start()
print('f1执行状态:',f1.is_alive())
f1.join()
print('f1执行状态:',f1.is_alive())
#f3.daemon=True
f2.start()
f3.start()
print('当前的线程变量:',threading.current_thread())
print('正在执行的线程列表:',threading.enumerate())
print('正在执行的线程数量',threading.active_count())
print('f2执行状态:',f2.is_alive())
f2.join(2)
print('f2执行状态:',f2.is_alive())
print('子线程f1的名字:{0},即:{1}'.format(f1.name,f1.getName()))
print('子线程f2的名字:{0},即:{1}'.format(f2.name,f2.getName()))
print('子线程f3的名字:{0},即:{1}'.format(f3.name,f3.getName()))
f2.join()
f3.join()
print('主线程的x:',x)
print('主线程执行结束，用时:',time.time()-t0)
print(f1.res,f2.res,f3.res)
