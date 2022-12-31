import collections
import os
import random
import re
import itertools
from copy import copy
from typing import List

from constant import SELECTED_COUNT, ALL_NUMBERS, DEFAULT_PREFIX


def parseCondFilename(filename: str) -> list:
    """
    解析条件文件名，获取容错范围
    """
    pattern = r'[(（][0-9]+-[0-9]+[）)]'
    prefix = os.path.splitext(filename)[0].strip()
    result = re.search(pattern, prefix)
    return [int(i) for i in result.group()[1: -1].split('-')] if result else None


def parseCondText(conditionText: str) -> dict:
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


def getCondFromFile(filePath: str) -> List[dict]:
    """
    从 txt 文件中获取所有条件
    """
    conditions = []  # 记录文件中的所有条件

    # 打开文件
    with open(filePath, mode='r', encoding='utf8') as rf:
        for line in rf.readlines():
            # 以默认前缀开头，说明是条件文本
            if line.startswith(DEFAULT_PREFIX):
                conditions.append(parseCondText(line.strip().strip('\n')))
    return conditions


def genCombinations(condition: dict) -> set:
    """
    生成数字组合（单个条件）
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


def genAndMergeCombinations(conditions: List[dict], faultRange: list):
    """
    多条件生成组合数，根据容错范围合并
    :param conditions: 条件
    :param faultRange: 容错范围
    :return:
    """
    combinationCnt = {}
    for condition in conditions:
        combinations = genCombinations(condition)
        for combination in combinations:
            combinationCnt[combination] = combinationCnt.get(combination, 0) + 1
    result = []  # 最终结果
    for key, value in combinationCnt.items():
        if faultRange[0] <= len(conditions) - value <= faultRange[1]:
            result.append(key)
    # 对结果进行排序
    result.sort()
    return result


def genRangeLine(conditions: List[dict], start: int, lineCnt: int, faultRange: list, filename: str, resultDir: str):
    """
    范围行计算
    :param filename:
    :param lineCnt:
    :param resultDir:
    :param conditions:
    :param start:
    :param faultRange:
    :return:
    """
    end = start + lineCnt
    result = genAndMergeCombinations(conditions[start: end], faultRange)
    prefix, suffix = os.path.splitext(filename)
    resultFilename = f'{prefix}结果（{start + 1}-{end}）行={len(result)}{suffix}'
    resultPath = os.path.join(resultDir, resultFilename)
    resultToFile(result, resultPath)


def genRandomLine(conditions: List[dict], lineCnt: int, faultRange: list, filename: str, resultDir: str):
    """
    随机行计算
    :param filename:
    :param lineCnt:
    :param resultDir:
    :param conditions:
    :param faultRange:
    :return:
    """
    index = random.sample(range(len(conditions)), lineCnt)
    index.sort()
    result = genAndMergeCombinations([conditions[i] for i in index], faultRange)
    prefix, suffix = os.path.splitext(filename)
    resultFilename = f'{prefix}结果（{".".join([str(i+1) for i in index])}）行={len(result)}{suffix}'
    resultPath = os.path.join(resultDir, resultFilename)
    resultToFile(result, resultPath)


def getResultsFromFile(filePath: str):
    """
    从文件中获取结果
    :param filePath: 结果文件
    :return:
    """
    # 文件不存在，返回空列表
    if not os.path.exists(filePath):
        return []
    with open(filePath, mode='r', encoding='utf8') as rf:
        # 判断文件格式是否能被解析
        combinations = [tuple(line.split(' ')) for line in rf.read().strip('\n').split('\n')]
    return combinations


def resultToFile(result: list, savaPath: str) -> None:
    """
    将结果写入文件
    """
    with open(savaPath, mode='w', encoding='utf8') as wf:
        wf.write('\n'.join(' '.join(item) for item in result))


def mergeDict(dicts):
    """
    合并字典，相同key的键值相加
    """
    resultCounter = collections.Counter({})
    dictCounters = [collections.Counter(d) for d in dicts]
    for dictCounter in dictCounters:
        resultCounter += dictCounter
    return dict(resultCounter)


if __name__ == '__main__':
    conditions = getCondFromFile('./data/conditions/验证2（0-3）.txt')
    print(len(conditions))
