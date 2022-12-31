# -*- coding: utf-8 -*-
# @Time : 2022/12/25 13:14
# @Author : XXX
# @Site : 
# @File : spin_box.py
# @Software: PyCharm

from PyQt5.QtWidgets import *


class SpinBox(QSpinBox):
    """
    数字选择框
    """

    def __init__(self, initValue=0, minValue=0, maxValue=100000,):
        super(SpinBox, self).__init__()
        self.setValue(initValue)
        self.setMinimum(minValue)
        self.setMaximum(maxValue)

