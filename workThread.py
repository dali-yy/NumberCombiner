import math
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool, Manager
from utils import parseConditionFilename, getConditionsFromFile, batchCountCombination, mergeDict


class WorkThread(QThread):
    progress = pyqtSignal(int)  # 进度条的值

    def __init__(self, checkedFiles, resultDir, processCount):
        super().__init__()
        self.checkedFiles = checkedFiles  # 选中的条件文件
        self.resultDir = resultDir  # 结果保存的文件夹
        self.processCount = processCount  # 进程数

    def run(self):
        for checkedFile in self.checkedFiles:
            result = []  # 最终结果

            faultRange = parseConditionFilename(checkedFile['filename'])  # 容错范围
            conditions = getConditionsFromFile(checkedFile['filePath'])  # 获取文件中所有条件
            conditionCount = len(conditions)  # 条件数
            batchSize = math.ceil(conditionCount / (self.processCount + 1))  # 批次大小（每个进程计算的条件）,加1是因为主进程

            countList = Manager().list()  # 多进程共享变量
            with Pool(self.processCount) as pool: # 进程池
                # 前batchsize个条件留给主进程计算
                for i in range(batchSize, conditionCount, batchSize):
                    batchConditions = conditions[i: i + batchSize] if i + batchSize < conditionCount else conditions[i:]
                    pool.apply_async(batchCountCombination, args=(batchConditions, countList,))
                # 主进程计算
                # mainCombinationCount = {}
                # for idx, condition in enumerate(conditions):
                #     combinations = genCombinationsWithCondition(condition)
                #     for combination in combinations:
                #         mainCombinationCount[combination] = mainCombinationCount.get(combination, 0) + 1
                #     self.progress.emit(int((idx + 1) / batchSize * 100) - 1)
                # 等待所有进程运行完毕
                pool.close()
                pool.join()

            allCombinationCount = mergeDict(countList)  # 每个组合出现的次数
            # 获取文件对应的结果
            for key, value in allCombinationCount.items():
                if faultRange[0] <= conditionCount - value <= faultRange[1]:
                    result.append(key)
            print(result)
            self.progress.emit(100)
