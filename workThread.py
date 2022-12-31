import math
import os
from typing import List

from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool, Manager
from constant import STATUS
from utils import genCombinations, parseCondFilename, getCondFromFile, mergeDict, resultToFile


def countCombinations(conditions: List[dict], countList: List[dict], lock):
    """
    统计条件下生成的组合数出现次数
    """
    combinationCnt = {}
    for condition in conditions:
        combinations = genCombinations(condition)
        for combination in combinations:
            combinationCnt[combination] = combinationCnt.get(combination, 0) + 1
    lock.acquire()
    countList.append(combinationCnt)
    lock.release()


class WorkThread(QThread):
    progress = pyqtSignal(int)  # 进度条的值
    finishedCount = pyqtSignal(int)  # 完成的文件个数
    fileStatus = pyqtSignal(tuple)  # 文件状态
    resultPath = pyqtSignal(tuple)  # 结果保存路径

    def __init__(self, checkedFiles, resultDir, processCount):
        super().__init__()
        self.checkedFiles = checkedFiles  # 选中的条件文件
        self.resultDir = resultDir  # 结果保存的文件夹
        self.processCount = processCount  # 进程数

    def run(self):
        for fileIndex, checkedFile in enumerate(self.checkedFiles):
            # 修改文件状态为已完成
            self.fileStatus.emit((checkedFile['id'], STATUS['RUNNING']))

            result = []  # 最终结果
            faultRange = parseCondFilename(checkedFile['filename'])  # 容错范围
            # 文件名不规范
            if faultRange is None:
                self.fileStatus.emit((checkedFile['id'], STATUS['FAILED']))
                continue
            conditions = getCondFromFile(checkedFile['filePath'])  # 获取文件中所有条件
            conditionCount = len(conditions)  # 条件数

            manager = Manager()  # 共享管理
            countList = manager.list()  # 多进程共享变量
            lock = manager.RLock()  # 共享锁

            batchSize = conditionCount // self.processCount  # 批量大小
            # 批量大小不能小于等于0
            if batchSize <= 0:
                return
            self.pool = Pool(self.processCount)  # 进程池
            # 添加进程，每个进程运行batchSize个条件
            for i in range(batchSize, conditionCount, batchSize):
                batchConditions = conditions[i: i + batchSize] if i + batchSize < conditionCount else conditions[i:]
                self.pool.apply_async(countCombinations, args=(batchConditions, countList, lock,))
            # 关闭进程池，不能再加入新的进程
            self.pool.close()
            # 主进程运行，主要是为了监控进度
            mainCount = {}
            for idx, condition in enumerate(conditions[:batchSize]):
                combinations = genCombinations(condition)
                for combination in combinations:
                    mainCount[combination] = mainCount.get(combination, 0) + 1
                self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
            countList.append(mainCount)
            # 主线程等待进程池所有进程退出
            self.pool.join()

            # 计算结果（判断次数是否在重复数范围内）
            combinationCount = mergeDict(countList)
            for key, value in combinationCount.items():
                if faultRange[0] <= conditionCount - value <= faultRange[1]:
                    result.append(key)
            # 将结果写入写入文件
            prefix, suffix = os.path.splitext(checkedFile['filename'])
            resultFileName = prefix + '结果' + suffix  # 结果文件名
            resultFilePath = os.path.join(self.resultDir, resultFileName)  # 结果文件路径
            # 对结果进行排序
            result.sort()
            # 将结果写入文件
            resultToFile(result, resultFilePath)
            # 进程条100%
            self.progress.emit(100)
            # 结果文件路径
            self.resultPath.emit((checkedFile['id'], resultFilePath))
            # 修改文件状态为已完成
            self.fileStatus.emit((checkedFile['id'], STATUS['FINISHED']))
            # 文件完成计算个数加1
            self.finishedCount.emit(fileIndex + 1)
