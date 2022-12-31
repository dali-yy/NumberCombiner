import os
import math
from typing import List
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool, Manager
from constant import STATUS, CAL_TYPE
from utils import genCombinations, parseCondFilename, getCondFromFile, \
    genRangeLine, genRandomLine, mergeDict, resultToFile


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


def byLineService(conditions: List[dict], start: int, size: int, lineCnt: int,
                  faultRange: list, filename: str, resultDir: str):
    """
    逐行计算进程服务程序
    :param filename:
    :param faultRange:
    :param lineCnt:
    :param conditions:
    :param start: 
    :param size: 区间大小
    :param resultDir: 
    :return: 
    """
    for idx in range(start, start + size):
        genRangeLine(conditions, idx, lineCnt, faultRange, filename, resultDir)


def randomLineService(conditions: List[dict], randomCnt: int, lineCnt: int, faultRange: list,
                      filename: str, resultDir: str):
    """
    随机行计算进程服务程序
    :param filename:
    :param faultRange:
    :param lineCnt:
    :param conditions:
    :param randomCnt: 随机的次数
    :param resultDir:
    :return:
    """
    for idx in range(randomCnt):
        genRandomLine(conditions, lineCnt, faultRange, filename, resultDir)


class CalThread(QThread):
    progress = pyqtSignal(int)  # 进度条的值
    finishedCnt = pyqtSignal(int)  # 完成的文件个数
    fileStatus = pyqtSignal(tuple)  # 文件状态

    def __init__(self, condFiles, resultDir, processCnt, calType=0, lineCnt=0, randomCnt=0):
        super().__init__()
        self.condFiles = condFiles  # 选中的条件文件
        self.resultDir = resultDir  # 结果保存的文件夹
        self.processCnt = processCnt  # 进程数
        self.calType = calType  # 计算类型（0：）
        self.lineCnt = lineCnt  # 逐行计算或随即行计算的行数
        self.randomCnt = randomCnt  # 随机行计算次数
        self.pool = None  # 初始化进程池为空

    def run(self):
        if self.calType == CAL_TYPE['BY_FILE']:
            self.calByFile()
        elif self.calType == CAL_TYPE['BY_LINE']:
            self.calByLine()
        else:
            self.calRandomLine()

    def calByFile(self):
        """
        逐文件计算
        :return:
        """
        for fileIndex, condFile in enumerate(self.condFiles):
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['RUNNING']))
            # 容错范围
            faultRange = parseCondFilename(condFile['filename'])  # 容错范围
            # 文件名不规范
            if faultRange is None:
                self.fileStatus.emit((condFile['id'], STATUS['FAILED']))
                continue
            # 解析条件文件，获取文件中所有条件
            conditions = getCondFromFile(condFile['filePath'])
            condCnt = len(conditions)  # 条件数
            # 判断文件是否为空
            if condCnt == 0:
                self.fileStatus.emit((condFile['id'], STATUS['EMPTY']))
                continue
            # 每个进程计算的条件个数
            batchSize = math.ceil(condCnt / self.processCnt)
            # 如果只有一个条件不启用多进程
            if condCnt == 1:
                combinationCnt = {}
                combinations = genCombinations(conditions[0])
                for idx, combination in enumerate(combinations):
                    combinationCnt[combination] = combinationCnt.get(combination, 0) + 1
                    self.progress.emit(int((idx + 1) / len(combinations) * 100) - 1)
            else:
                manager = Manager()  # 共享管理
                countList = manager.list()  # 多进程共享变量
                lock = manager.RLock()  # 共享锁

                self.pool = Pool(condCnt // batchSize)  # 进程池
                # 添加进程，每个进程运行batchSize个条件
                for i in range(batchSize, condCnt, batchSize):
                    batchConditions = conditions[i: i + batchSize] \
                        if i + batchSize < condCnt else conditions[i:]
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
                combinationCnt = mergeDict(countList)
            result = []  # 最终结果
            for key, value in combinationCnt.items():
                if faultRange[0] <= condCnt - value <= faultRange[1]:
                    result.append(key)
            # 将结果写入写入文件
            prefix, suffix = os.path.splitext(condFile['filename'])
            resultFileName = prefix + '结果' + suffix  # 结果文件名
            resultFilePath = os.path.join(self.resultDir, resultFileName)  # 结果文件路径
            # 对结果进行排序
            result.sort()
            # 将结果写入文件
            resultToFile(result, resultFilePath)
            # 进程条100%
            self.progress.emit(100)
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['FINISHED']))
            # 文件完成计算个数加1
            self.finishedCnt.emit(fileIndex + 1)
        # 进程池置空
        self.pool = None

    def calByLine(self):
        """
        逐行计算
        :return:
        """
        for fileIndex, condFile in enumerate(self.condFiles):
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['RUNNING']))
            # 容错范围
            faultRange = parseCondFilename(condFile['filename'])  # 容错范围
            # 文件名不规范
            if faultRange is None:
                self.fileStatus.emit((condFile['id'], STATUS['FAILED']))
                continue
            # 解析条件文件，获取文件中所有条件
            conditions = getCondFromFile(condFile['filePath'])
            condCnt = len(conditions)  # 条件数
            # 判断文件是否为空
            if condCnt == 0:
                self.fileStatus.emit((condFile['id'], STATUS['EMPTY']))
                continue
            # 条件数小于设定行数
            if condCnt < self.lineCnt:
                self.fileStatus.emit((condFile['id'], STATUS['LINE_CNT_LARGER']))
                continue
            # 逐行计算的次数
            calCnt = condCnt - self.lineCnt + 1
            # 每个进程计算的次数
            batchSize = math.ceil(calCnt / self.processCnt)
            # 如果只计算一次不启用多进程
            if calCnt == 1:
                genRangeLine(conditions, 0, len(conditions), faultRange, condFile['filename'], self.resultDir)
            else:
                self.pool = Pool(calCnt // batchSize)  # 进程池
                # 添加进程，每个进程运行batchSize个条件
                for i in range(batchSize, calCnt, batchSize):
                    size = batchSize if i + batchSize < calCnt else calCnt - i
                    self.pool.apply_async(byLineService,
                                          args=(conditions, i, size, self.lineCnt, faultRange, condFile['filename'], self.resultDir,))
                # 关闭进程池，不能再加入新的进程
                self.pool.close()
                # 主进程运行，主要是为了监控进度
                for idx in range(batchSize):
                    genRangeLine(conditions, idx, self.lineCnt, faultRange, condFile['filename'], self.resultDir)
                    self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
                # 主线程等待进程池所有进程退出
                self.pool.join()
            # 进程条100%
            self.progress.emit(100)
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['FINISHED']))
            # 文件完成计算个数加1
            self.finishedCnt.emit(fileIndex + 1)
        # 进程池置空
        self.pool = None

    def calRandomLine(self):
        """
        随机行计算
        :return:
        """
        for fileIndex, condFile in enumerate(self.condFiles):
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['RUNNING']))
            # 容错范围
            faultRange = parseCondFilename(condFile['filename'])  # 容错范围
            # 文件名不规范
            if faultRange is None:
                self.fileStatus.emit((condFile['id'], STATUS['FAILED']))
                continue
            # 解析条件文件，获取文件中所有条件
            conditions = getCondFromFile(condFile['filePath'])
            condCnt = len(conditions)  # 条件数
            # 判断文件是否为空
            if condCnt == 0:
                self.fileStatus.emit((condFile['id'], STATUS['EMPTY']))
                continue
            # 条件数小于设定行数
            if condCnt < self.lineCnt:
                self.fileStatus.emit((condFile['id'], STATUS['LINE_CNT_LARGER']))
                continue
            # 逐行计算次数小于进程数
            if self.randomCnt < self.processCnt:
                self.processCnt = self.randomCnt  # 进程数等于随机次数
            # 每个进程计算的次数
            batchSize = math.ceil(self.randomCnt / self.processCnt)
            # 如果只计算一次不启用多进程
            if self.randomCnt == 1:
                genRandomLine(conditions, self.lineCnt, faultRange, condFile['filename'], self.resultDir)
            else:
                self.pool = Pool(self.randomCnt // batchSize)  # 进程池
                # 添加进程，每个进程运行batchSize个条件
                for i in range(batchSize, self.randomCnt, batchSize):
                    cnt = batchSize if i + batchSize < self.randomCnt else self.randomCnt - i
                    self.pool.apply_async(randomLineService,
                                          args=(conditions, cnt,
                                                self.lineCnt, faultRange, condFile['filename'], self.resultDir,))
                # 关闭进程池，不能再加入新的进程
                self.pool.close()
                # 主进程运行，主要是为了监控进度
                for idx in range(batchSize):
                    genRandomLine(conditions, self.lineCnt, faultRange, condFile['filename'], self.resultDir)
                    self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
                # 主线程等待进程池所有进程退出
                self.pool.join()
            # 进程条100%
            self.progress.emit(100)
            # 修改文件状态为已完成
            self.fileStatus.emit((condFile['id'], STATUS['FINISHED']))
            # 文件完成计算个数加1
            self.finishedCnt.emit(fileIndex + 1)
        # 进程池置空
        self.pool = None
