# define your own process
# run() and start() are different,

import time, os
from multiprocessing import Process


def func(a, b, y, c=3, d=4):
    print('开始执行子进程:', a)
    print('子进程' + a + '的id：{0},父进程的id:{1}'.format(os.getpid(), os.getppid()))
    global x
    x = y
    t0 = time.time()
    print('c+d:', c + d)
    print('子进程' + a + '的x:', x)
    time.sleep(b)
    print('子进程' + a + '执行结束,用时:', time.time() - t0)


class MyProcess(Process):
    def __init__(self, target, args, kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.target(*self.args, **self.kwargs)


if __name__ == '__main__':
    x = 60
    f1 = MyProcess(target=func, args=('f1', 2, 10), kwargs={'c': 5, 'd': 6})
    f2 = MyProcess(target=func, args=('f2', 6, 100), kwargs={'c': 7, 'd': 8})
    t0 = time.time()
    f1.start()
    print('f1执行状态:', f1.is_alive())
    f1.join()
    # time.sleep(10)
    print('f1执行状态:', f1.is_alive())
    f2.start()
    # f2.run()
    print('f2执行状态:', f2.is_alive())
    f2.join(2)
    f2.terminate()
    f2.join()
    # time.sleep(10)
    print('f2执行状态:', f2.is_alive())
    print('子进程f1的名字:{0},pid:{1}'.format(f1.name, f1.pid))
    print('子进程f2的名字:{0},pid:{1}'.format(f2.name, f2.pid))
    print('父进程的x:', x)
    print('父进程执行结束，用时:', time.time() - t0)