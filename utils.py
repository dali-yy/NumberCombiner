import collections
import datetime
import os
import itertools
import re
from copy import copy
from typing import List
from multiprocessing import Pool, Manager
import math
from tqdm import tqdm

from constant import SELECTED_COUNT, ALL_NUMBERS, DEFAULT_PREFIX


def parseConditionFilename(filename: str) -> list:
    """
    解析条件文件名
    """
    pattern = r'[(（][0-9]+-[0-9]+[）)]'
    prefix = os.path.splitext(filename)[0].strip()
    result = re.search(pattern, prefix)
    return [int(i) for i in result.group()[1: -1].split('-')] if result else None


def parseConditionText(conditionText: str) -> dict:
    """
    解析单个条件文本
    """
    condition = {}  # 条件字典
    # 根据 - 分割条件中的A部分数字与选择的个数(并去去除默认前缀)
    numsA, count = conditionText.replace(DEFAULT_PREFIX, '').split('-')
    # A 部分数字
    condition['A'] = numsA.split(',')
    # 剩余数字则为B部分
    numsB = copy(ALL_NUMBERS)
    for num in condition['A']:
        numsB.remove(num)
    condition['B'] = numsB
    # 从A部分选择的数字个数
    condition['countA'] = [int(item) for item in count.split(',')]

    return condition


def getConditionsFromFile(filePath: str) -> List[dict]:
    """
    从 txt 文件中获取所有条件
    """
    conditions = []  # 记录文件中的所有条件

    # 打开文件
    with open(filePath, mode='r', encoding='utf8') as rf:
        for line in rf.readlines():
            # 以默认前缀开头，说明是条件文本
            if line.startswith(DEFAULT_PREFIX):
                conditions.append(parseConditionText(line.strip().strip('\n')))
    return conditions


def genCombinationsWithCondition(condition: dict) -> set:
    """
    单个条件限制下生成数字组合
    """
    combinations = set()  # 满足该条件的所有数字组合

    # 遍历 A 部分选择的数字个数
    for countA in condition['countA']:
        countB = SELECTED_COUNT - countA  # B部分选择的数字个数
        combinationsAB = []
        combinationsB = list(itertools.combinations(condition['B'], countB))
        # 合并A、B部分的数字组合
        for combinationA in itertools.combinations(condition['A'], countA):
            for combinationB in combinationsB:
                combinationsAB.append(tuple(sorted(combinationA + combinationB)))  # 排序，防止因顺序不同导致错误
        combinations |= set(combinationsAB)  # 求并集
    return combinations


def getResultDifference(results: List[set]) -> set:
    """
  获取结果的差集
  """
    allCombinations = itertools.combinations(ALL_NUMBERS, SELECTED_COUNT)  # 所有可能的组合
    differentSet = set(allCombinations)  # 转换成集合
    # 去除所有满足条件的组合数
    for result in results:
        differentSet -= result
    return differentSet


def batchCountCombination(conditions: List[dict], countList: List[dict], lock):
    """
    多进程批量统计组合数出现次数
    """
    combinationCount = {}
    for condition in tqdm(conditions):
        combinations = genCombinationsWithCondition(condition)
        for combination in combinations:
            combinationCount[combination] = combinationCount.get(combination, 0) + 1
    lock.acquire()
    countList.append(combinationCount)
    lock.release()

def mergeDict(dicts):
    """
    合并字典，相同key的键值相加
    """
    resultCounter = collections.Counter({})
    dictCounters = [collections.Counter(d) for d in dicts]
    for dictCounter in dictCounters:
        resultCounter += dictCounter
    return dict(resultCounter)


def genCombinationsByFile(filePath: str, processCount: int) -> list:
    """
    计算单个文件的结果
    """
    result = []  # 最终结果

    faultRange = parseConditionFilename(os.path.basename(filePath))  # 容错范围
    conditions = getConditionsFromFile(filePath)  # 获取文件中所有条件
    conditionCount = len(conditions)  # 条件数
    countList = Manager().list()  # 多进程共享变量

    batchSize = math.ceil(conditionCount / processCount)  # 批量大小
    pool = Pool(processCount)
    for i in range(0, conditionCount, batchSize):
        batchConditions = conditions[i: i + batchSize] if i + batchSize < conditionCount else conditions[i:]
        pool.apply_async(batchCountCombination, args=(batchConditions, countList))
    pool.close()
    pool.join()

    combinationCount = mergeDict(countList)  # 每个组合出现的次数

    for key, value in combinationCount.items():
        if faultRange[0] <= conditionCount - value <= faultRange[1]:
            result.append(key)
    return result

def _genCombinationsByFile(filePath: str, processCount: int) -> list:
    """
    计算单个文件的结果
    """
    result = []  # 最终结果

    faultRange = parseConditionFilename(os.path.basename(filePath))  # 容错范围
    conditions = getConditionsFromFile(filePath)  # 获取文件中所有条件
    conditionCount = len(conditions)  # 条件数

    manager = Manager()  # 共享管理
    countList = manager.list()  # 多进程共享变量
    lock = manager.RLock()  # 共享锁

    batchSize = math.ceil(conditionCount / (processCount + 1))  # 批量大小
    pool = Pool(processCount)
    for i in range(batchSize, conditionCount, batchSize):
        batchConditions = conditions[i: i + batchSize] if i + batchSize < conditionCount else conditions[i:]
        pool.apply_async(batchCountCombination, args=(batchConditions, countList, lock,))
    pool.close()
    mainCount = {}
    for condition in tqdm(conditions[:batchSize]):
        combinations = genCombinationsWithCondition(condition)
        for combination in combinations:
            mainCount[combination] = mainCount.get(combination, 0) + 1
    countList.append(mainCount)
    pool.join()

    combinationCount = mergeDict(countList)  # 每个组合出现的次数

    for key, value in combinationCount.items():
        if faultRange[0] <= conditionCount - value <= faultRange[1]:
            result.append(key)
    return result


def resultToFile(result: list, savaPath: str) -> None:
    """
    将结果写入文件
    """
    with open(savaPath, mode='w', encoding='utf8') as wf:
        wf.write('\n'.join(' '.join(item) for item in result))


if __name__ == '__main__':
    # conditionText = 'hqdm_0_0_hqdm_0_1_0_01,02,03-2'
    # conditionText = 'hqdm_0_0_hqdm_0_1_0_23,24,25-0,2'
    # condition = parseConditionText(conditionText)
    # combinations = genCombinationsWithSingle(condition)
    # print(list(combinations)[0])
    # print(len(combinations))
    # conditions = getConditionsFromFile('data\conditions\TEST002 (0-0）.txt')
    # print('条件计算')
    # combinationsList = _genCombinationsWithMultiple(conditions)
    # print('合并结果')
    # results = genCombinationsWithFault(combinationsList, 0, 5)
    print(datetime.datetime.now())
    result = _genCombinationsByFile('data/conditions/验证2（0-3）.txt', 10)
    print(datetime.datetime.now())
    resultToFile(result, 'data/result/验证2（0-3）结果.txt')
    print(datetime.datetime.now())

