# -*- coding: utf-8 -*-
# @Time : 2022/12/24 9:03
# @Author : XXX
# @Site : 
# @File : result_frame.py
# @Software: PyCharm

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ResultFrame(QFrame):
    def __init__(self, title, importBtnName):
        super(ResultFrame, self).__init__()

        self.resultFileList = []  # 结果文件列表

        # 标题标签
        self.titleLabel = QLabel(title)
        self.titleLabel.setObjectName('title-label')
        # 已完成计数标签
        self.finishedLabel = QLabel('')
        self.finishedLabel.setObjectName('finished-label')
        # 外部结果文件全选框
        self.checkAllBox = QCheckBox('全选')
        self.checkAllBox.setObjectName('outer-result-check-all-label')
        self.checkAllBox.hide()
        self.checkAllBox.clicked.connect(self.onCheckAll)
        # 结果文件信息表格
        self.resultFileTable = QTableWidget()
        self.resultFileTable.setObjectName('file-tbale')
        self.resultFileTable.setShowGrid(False)
        self.resultFileTable.setColumnCount(2)
        self.resultFileTable.setHorizontalHeaderLabels(['结果文件名', ''])
        self.resultFileTable.setColumnWidth(0, 280)
        self.resultFileTable.setColumnWidth(1, 50)
        # 导入条件文件按钮
        self.importFilesBtn = QPushButton('文件导入')
        self.importFilesBtn.setObjectName('import-btn')
        self.importFilesBtn.setFixedSize(120, 30)
        self.importFilesBtn.setCursor(Qt.PointingHandCursor)
        self.importFilesBtn.clicked.connect(self.importResultFiles)
        # 导入条件文件夹按钮
        self.importDirBtn = QPushButton('文件夹导入')
        self.importDirBtn.setObjectName('import-btn')
        self.importDirBtn.setFixedSize(120, 30)
        self.importDirBtn.setCursor(Qt.PointingHandCursor)
        self.importDirBtn.clicked.connect(self.importResultDir)
        # 导入条件布局
        importLayout = QHBoxLayout()
        importLayout.addWidget(self.importFilesBtn)
        importLayout.addWidget(QLabel('/'))
        importLayout.addWidget(self.importDirBtn)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titleLabel, 0, 0, 2, 3)
        layout.addWidget(self.finishedLabel, 0, 3, 2, 2)
        layout.addWidget(self.checkAllBox, 0, 5, 2, 1, alignment=Qt.AlignRight)
        layout.addWidget(self.resultFileTable, 2, 0, 16, 6)
        layout.addLayout(importLayout, 18, 0, 1, 6, alignment=Qt.AlignCenter)
        # layout.addWidget(self.importBtn, 18, 0, 1, 6, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def onCheckAll(self):
        """
        全选按钮点击事件处理函数
        :return:
        """
        checked = self.checkAllBox.isChecked()
        for elem in self.resultFileList:
            elem['check'].setChecked(checked)

    def setTableItem(self, row, col, text):
        """
        设置表格元素
        """
        tableItem = QTableWidgetItem(text)
        tableItem.setTextAlignment(Qt.AlignCenter)
        self.resultFileTable.setItem(row, col, tableItem)

    def importResultDir(self):
        """
        导入结果文件夹
        :return:
        """
        resultDir = QFileDialog.getExistingDirectory(self)  # 选择条件文件夹
        if not resultDir:
            QMessageBox.warning(self, '提示', '外部结果未导入！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 选择了新的外部文件夹，则重置外部结果记录
        self.resultFileList = []
        # 外部结果文件中所有文件名
        resultFiles = os.listdir(resultDir)
        # 重置表格行数
        resultCnt = len(resultFiles)
        self.resultFileTable.setRowCount(resultCnt)
        # 导入的外部结果信息显示在表格中
        for idx, filename in enumerate(resultFiles):
            filePath = os.path.join(resultDir, filename)
            # 过滤文件夹
            if os.path.isdir(filePath):
                continue
            # 设置表格元素
            self.setTableItem(idx, 0, filename)
            checkBoxItem = QCheckBox()
            checkBoxItem.setChecked(True)
            self.resultFileTable.setCellWidget(idx, 1, checkBoxItem)

            resultFile = {
                'id': idx,
                'filename': filename,  # 结果文件名
                'filePath': os.path.join(resultDir, filename),
                'check': checkBoxItem  # 是否被选中
            }
            # 记录所有外部结果信息
            self.resultFileList.append(resultFile)

        # 显示全选外部结果复选框(默认全选)
        self.checkAllBox.setChecked(True)
        self.checkAllBox.show()

    def importResultFiles(self):
        """
        导入结果文件夹
        :return:
        """
        resultFiles, _ = QFileDialog.getOpenFileNames(self)  # 选择条件文件夹
        if not resultFiles:
            QMessageBox.warning(self, '提示', '未导入结果文件！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 选择了新的外部文件夹，则重置外部结果记录
        self.resultFileList = []
        # 重置表格行数
        resultCnt = len(resultFiles)
        self.resultFileTable.setRowCount(resultCnt)
        # 导入的外部结果信息显示在表格中
        for idx, file in enumerate(resultFiles):
            filename = os.path.basename(file)
            # 设置表格元素
            self.setTableItem(idx, 0, filename)
            checkBoxItem = QCheckBox()
            checkBoxItem.setChecked(True)
            self.resultFileTable.setCellWidget(idx, 1, checkBoxItem)

            resultFile = {
                'id': idx,
                'filename': filename,  # 结果文件名
                'filePath': file,
                'check': checkBoxItem  # 是否被选中
            }
            # 记录所有外部结果信息
            self.resultFileList.append(resultFile)

        # 显示全选外部结果复选框(默认全选)
        self.checkAllBox.setChecked(True)
        self.checkAllBox.show()

    def importResultDir(self):
        """
        导入结果文件夹
        :return:
        """
        resultDir = QFileDialog.getExistingDirectory(self)  # 选择条件文件夹
        if not resultDir:
            QMessageBox.warning(self, '提示', '未导入结果文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 选择了新的外部文件夹，则重置外部结果记录
        self.resultFileList = []
        # 外部结果文件中所有文件名
        resultFiles = os.listdir(resultDir)
        # 重置表格行数
        resultCnt = len(resultFiles)
        self.resultFileTable.setRowCount(resultCnt)
        # 导入的外部结果信息显示在表格中
        for idx, filename in enumerate(resultFiles):
            filePath = os.path.join(resultDir, filename)
            # 过滤文件夹
            if os.path.isdir(filePath):
                continue
            # 设置表格元素
            self.setTableItem(idx, 0, filename)
            checkBoxItem = QCheckBox()
            checkBoxItem.setChecked(True)
            self.resultFileTable.setCellWidget(idx, 1, checkBoxItem)

            resultFile = {
                'id': idx,
                'filename': filename,  # 结果文件名
                'filePath': os.path.join(resultDir, filename),
                'check': checkBoxItem  # 是否被选中
            }
            # 记录所有外部结果信息
            self.resultFileList.append(resultFile)

        # 显示全选外部结果复选框(默认全选)
        self.checkAllBox.setChecked(True)
        self.checkAllBox.show()

    def getCheckedResults(self):
        """
        获取选中的结果文件
        :return:
        """
        return [elem['filePath'] for elem in self.resultFileList if elem['check'].isChecked()]

    def setFinishedText(self, finished=0, total=0):
        """
        设置已完成文本
        :param finished: 已完成个数
        :param total: 总数
        :return:
        """
        self.finishedLabel.setText('' if total == 0 else f'已合并 {finished}/{total}')