import itertools

TOTAL_COUNT = 33  # 总的数字个数
SELECTED_COUNT = 6  # 选择的数字个数
ALL_NUMBERS = [('0' if idx < 9 else '') + str(idx + 1) for idx in range(TOTAL_COUNT)]  # 所有数字
ALL_COMBINATIONS = list(itertools.combinations(ALL_NUMBERS, 6))  # 所有可能的组合
ALL_COUNT = len(ALL_COMBINATIONS)
DEFAULT_PREFIX = 'hqdm_0_0_hqdm_0_1_0_'  # 固定前缀
STATUS = {
  'UNCAL': '未计算',
  'WAITING': '等待中',
  'RUNNING': '运行中',
  'FINISHED': '已完成',
  'NOTEXIST': '文件不存在',
  'FAILED': '失败'
}