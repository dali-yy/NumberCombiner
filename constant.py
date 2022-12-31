import itertools

TOTAL_COUNT = 33  # 总的数字个数
SELECTED_COUNT = 6  # 选择的数字个数
ALL_NUMBERS = [('0' if idx < 9 else '') + str(idx + 1) for idx in range(TOTAL_COUNT)]  # 所有数字
ALL_COMBINATIONS = list(itertools.combinations(ALL_NUMBERS, 6))  # 所有可能的组合
ALL_COUNT = len(ALL_COMBINATIONS)
DEFAULT_PREFIX = 'hqdm_0_0_hqdm_0_1_0_'  # 固定前缀
# 文件状态
STATUS = {
  'UNCAL': '未计算',
  'WAITING': '等待中',
  'RUNNING': '运行中',
  'FINISHED': '已完成',
  'NOTEXIST': '文件不存在',
  'EMPTY': '文件为空',
  'LINE_CNT_LARGER': '条件数小于行数',
  'FAILED': '失败'
}
# 计算类型
CAL_TYPE = {
  'BY_FILE': 0,  # 逐文件计算
  'BY_LINE': 1,  # 每个文件逐行计算
  'RANDOM_LINE': 2  # 每个文件随即行计算
}

# 合并类型
MERGE_TYPE = {
  'BASIC': 0,  # 基础合并
  'ALL': 1,  # 一对多全部合并
  'RANDOM': 2  # 一对多随机合并
}