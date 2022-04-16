# 子进程是一个一个的执行的，
# 函数func开始处用lock.acquire()锁定，执行完再用lock.release()释放锁，
# 一次只让一个子进程使用数据，虽然可以保证数据的安全，
# 但执行效率又大大降低了，失去了并行的意义，
# 为此，为保持高效率和数据安全，Python又引入了其他进程间通信的方式。

import time, os
from multiprocessing import Process, Lock


def func(a, b, y, lock, c=3, d=4):
    lock.acquire()
    print('开始执行子进程:', a)
    print('子进程' + a + '的id：{0},父进程的id:{1}'.format(os.getpid(), os.getppid()))
    global x
    x = y
    t0 = time.time()
    print('c+d:', c + d)
    print('子进程' + a + '的x:', x)
    time.sleep(b)
    print('子进程' + a + '执行结束,用时:', time.time() - t0)
    lock.release()


if __name__ == '__main__':
    lock = Lock()
    x = 60
    t0 = time.time()
    for j in range(1, 3):
        for i in 'abc':
            f = Process(target=func, name=i * j, args=(i * j, j, 10, lock), kwargs={'c': 5, 'd': 6})
            f.start()
            print('子进程f的名字:{0},pid:{1}'.format(f.name, f.pid))

    print('父进程的x:', x)
    print('父进程执行结束，用时:', time.time() - t0)