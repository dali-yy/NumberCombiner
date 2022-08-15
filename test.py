import time
from multiprocessing import Pool, Manager

from tqdm import tqdm


def count(countList):
    for i in tqdm(range(100000)):
        countList[(1, 2, 3)] = countList.get((1, 2, 3), 0) + 1


if __name__ == '__main__':

    countList = Manager().dict() # 多进程共享变量

    pool = Pool(10)
    for i in range(0, 4):
        pool.apply_async(count, args=(countList,))
    countList['a'] = 1
    pool.close()
    pool.join()
    print(countList)
