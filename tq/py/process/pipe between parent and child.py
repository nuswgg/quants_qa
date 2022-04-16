# Pipe的读写效率要高于Queue。
# 进程间的Pipe基于fork机制建立。
# 当主进程创建Pipe的时候，Pipe的两个Connections连接的的都是主进程。
# 当主进程创建子进程后，Connections也被拷贝了一份。此时有了4个Connections。
# 此后，关闭主进程的一个Out Connection，关闭一个子进程的一个In Connection。那么就建立好了一个输入在主进程，输出在子进程的管道。

# 示例代码
# coding=utf-8
from multiprocessing import Pipe, Process

def son_process(x, pipe):
    _out_pipe, _in_pipe = pipe

    # 关闭fork过来的输入端
    _in_pipe.close()
    while True:
        try:
            msg = _out_pipe.recv()
            print(msg)
        except EOFError:
            # 当out_pipe接受不到输出的时候且输入被关闭的时候，会抛出EORFError，可以捕获并且退出子进程
            break

if __name__ == '__main__':
    out_pipe, in_pipe = Pipe(True)
    son_p = Process(target=son_process, args=(100, (out_pipe, in_pipe)))
    son_p.start()

    # 等 pipe 被 fork 后，关闭主进程的输出端
    # 这样，创建的Pipe一端连接着主进程的输入，一端连接着子进程的输出口
    out_pipe.close()
    for x in range(10):
        in_pipe.send(x)
    in_pipe.close()
    son_p.join()
    print("主进程也结束了")

