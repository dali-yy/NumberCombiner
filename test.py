import os
import time
import multiprocessing


def work(count, lock):
    lock.acquire()  # 加锁，只允许一个进程运行
    count.append(5)
    print(count, os.getpid())
    time.sleep(2)  # 阻塞5s
    lock.release()  # 解锁
    return 'result is %s, pid is %s' % (count, os.getpid())


if __name__ == '__main__':
    pool = multiprocessing.Pool(5)  # 创建具有5个进程的进程池
    manager = multiprocessing.Manager()
    lock = manager.RLock()
    count = manager.list()

    results = []
    for i in range(5):
        result = pool.apply_async(func=work, args=(count, lock))
    pool.close()
    pool.join()
