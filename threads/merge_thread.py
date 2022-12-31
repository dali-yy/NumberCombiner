# -*- coding: utf-8 -*-
# @Time : 2022/12/27 12:44
# @Author : XXX
# @Site : 
# @File : merge_thread.py
# @Software: PyCharm
import math
import os
import random

from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool, Manager
from constant import MERGE_TYPE
from utils import getResultsFromFile, resultToFile
import itertools


def mergeResultFiles(resultFiles, faultRange, saveDir):
    """
    合并结果文件
    :param resultFiles:
    :param faultRange:
    :param saveDir:
    :return:
    """
    combinationCount = {}
    fileCnt = len(resultFiles)  # 基础结果文件个数
    # 读取结果文件内容
    for idx, filePath in enumerate(resultFiles):
        for combination in getResultsFromFile(filePath):
            combinationCount[combination] = combinationCount.get(combination, 0) + 1
    # 合并的结果
    mergeResult = []
    faultLeft, faultRight = faultRange
    for key, value in combinationCount.items():
        if faultLeft <= fileCnt - value <= faultRight:
            mergeResult.append(key)
    mergeResult.sort()  # 结果排序
    # 保存结果
    filePath = '+'.join([os.path.splitext(os.path.basename(file))[0] for file in resultFiles]) \
               + f'（{faultLeft}-{faultRight}）结果={len(mergeResult)}.txt'
    resultToFile(mergeResult, os.path.join(saveDir, filePath))


def allMergeService(basicFile, otherGroups, faultRange, saveDir):
    """
    合并所有进程服务程序
    :param basicFile:
    :param otherGroups:
    :param faultRange:
    :param saveDir:
    :return:
    """
    for idx, group in enumerate(otherGroups):
        mergeResultFiles([basicFile] + list(group), faultRange, saveDir)


def randomMergeService(basicFile, otherResultFiles, otherCnt, batchSize, faultRange, saveDir):
    """
    随机合并进程服务程序
    :param basicFile:
    :param otherResultFiles:
    :param otherCnt:
    :param batchSize:
    :param faultRange:
    :param saveDir:
    :return:
    """
    for i in range(batchSize):
        resultFiles = [basicFile] + random.sample(otherResultFiles, otherCnt)
        mergeResultFiles(resultFiles, faultRange, saveDir)


class MergeThread(QThread):
    progress = pyqtSignal(int)  # 进度条的值
    finishedCnt = pyqtSignal(int)  # 完成的文件个数

    def __init__(self, basicResultFiles, otherResultFiles, saveDir, faultRange, processCnt, mergeType=0, otherCnt=0,
                 randomCnt=0):
        super().__init__()
        self.basicResultFiles = basicResultFiles  # 基础结果文件
        self.otherResultFiles = otherResultFiles  # 其他结果文件
        self.saveDir = saveDir  # 合并后结果的保存文件夹
        self.faultRange = faultRange  # 容错范围
        self.processCnt = processCnt  # 进程数
        self.mergeType = mergeType  # 合并类型
        self.otherCnt = otherCnt  # 其他结果文件合并个数
        self.randomCnt = randomCnt  # 随机行计算次数
        self.pool = None  # 初始化进程池为空

    def run(self):
        if self.mergeType == MERGE_TYPE['BASIC']:
            self.basicMerge()
        elif self.mergeType == MERGE_TYPE['ALL']:
            self.allMerge()
        else:
            self.randomMerge()

    def basicMerge(self):
        """
        基础合并
        :return:
        """
        mergeResultFiles(self.basicResultFiles, self.faultRange, self.saveDir)
        self.finishedCnt.emit(len(self.basicResultFiles))
        self.progress.emit(100)

    def allMerge(self):
        """
        全部穷举合并
        :return:
        """
        # 其他结果文件穷举组合
        otherGroups = list(itertools.combinations(self.otherResultFiles, self.otherCnt))
        # 其他文件穷举组合个数
        otherGroupCnt = len(otherGroups)
        for fileIndex, basicFile in enumerate(self.basicResultFiles):
            # 如果条件数小于进程数
            if otherGroupCnt < self.processCnt:
                self.processCnt = otherGroupCnt  # 进程数等于条件数
            # 每个进程计算的条件个数
            batchSize = math.ceil(otherGroupCnt / self.processCnt)
            # 如果只有一个条件不启用多进程
            if otherGroupCnt == 1:
                self.mergeResultFiles([basicFile] + self.otherResultFiles)
            else:
                self.pool = Pool(otherGroupCnt // batchSize)  # 进程池
                # 添加进程，每个进程运行batchSize个条件
                for i in range(batchSize, otherGroupCnt, batchSize):
                    batchGroups = otherGroups[i: i + batchSize if i + batchSize < otherGroupCnt else otherGroupCnt]
                    self.pool.apply_async(allMergeService, args=(basicFile, batchGroups, self.faultRange, self.saveDir))
                # 关闭进程池，不能再加入新的进程
                self.pool.close()
                # 主进程运行，主要是为了监控进度
                for idx, group in enumerate(otherGroups[0: batchSize]):
                    mergeResultFiles([basicFile] + list(group), self.faultRange, self.saveDir)
                    self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
                # 主线程等待进程池所有进程退出
                self.pool.join()
            # 进程条100%
            self.progress.emit(100)
            # 文件完成计算个数加1
            self.finishedCnt.emit(fileIndex + 1)
        # 进程池置空
        self.pool = None

    def randomMerge(self):
        """
        随机组合合并
        :return:
        """
        for fileIndex, basicFile in enumerate(self.basicResultFiles):
            # 如果条件数小于进程数
            if self.randomCnt < self.processCnt:
                self.processCnt = self.randomCnt  # 进程数等于随机组合次数
            # 每个进程计算的条件个数
            batchSize = math.ceil(self.randomCnt / self.processCnt)
            # 如果只有一个条件不启用多进程
            if self.randomCnt == 1:
                self.mergeResultFiles([basicFile] + random.sample(self.otherResultFiles, self.otherCnt))
            else:
                self.pool = Pool(self.randomCnt // batchSize)  # 进程池
                # 添加进程，每个进程运行batchSize个条件
                for i in range(batchSize, self.randomCnt, batchSize):
                    size = batchSize if i + batchSize < self.randomCnt else self.randomCnt - i
                    self.pool.apply_async(randomMergeService, args=(basicFile, self.otherResultFiles,
                                                                    self.otherCnt, size,
                                                                    self.faultRange, self.saveDir,))
                # 关闭进程池，不能再加入新的进程
                self.pool.close()
                # 主进程运行，主要是为了监控进度
                for idx in range(batchSize):
                    resultFiles = [basicFile] + random.sample(self.otherResultFiles, self.otherCnt)
                    mergeResultFiles(resultFiles, self.faultRange, self.saveDir)
                    self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
                # 主线程等待进程池所有进程退出
                self.pool.join()
            # 进程条100%
            self.progress.emit(100)
            # 文件完成计算个数加1
            self.finishedCnt.emit(fileIndex + 1)
        # 进程池置空
        self.pool = None
