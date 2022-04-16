# 前面进程间的通信都是子进程间进行的，11.1.1节里我们也知道主进程和子进程的命名空间是独立的，子进程无法访问主进程的全局变量，
# Manager则可以用来共享全局变量，Manager支持的类型有
# list、dict、Namespace、Lock、RLock、Semaphore、BoundedSemaphore、Condition、Event、Queue、Value和Array。


import multiprocessing, time


def func(mydict, mylist):
    mydict["x"] = 0  # 子进程改变dict,主进程跟着改变
    mydict["a"] = 11
    mydict["b"] = 22
    mylist.append(11)  # 子进程改变List,主进程跟着改变
    mylist.append(22)
    mylist.append(33)
    mylist[0]['y'] = 4  # 直接修改嵌套数据
    m = mylist[1]
    m['z'] = 5  # 通过中间变量m修改嵌套数据
    mylist[1] = m


if __name__ == "__main__":
    with multiprocessing.Manager() as MG:  # 重命名
        mydict = MG.dict({'x': 1})  # 主进程与子进程共享这个字典
        mylist = MG.list([{'y': 2}, {'z': 3}])  # 主进程与子进程共享这个List

        p = multiprocessing.Process(target=func, args=(mydict, mylist))
        p.start()

        while True:
            print(f"{time.strftime('%X')}")
            print(mydict)
            print(mylist)
            time.sleep(1)
