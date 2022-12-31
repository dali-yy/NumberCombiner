# -*- coding: utf-8 -*-
# @Time : 2022/12/24 9:06
# @Author : XXX
# @Site : 
# @File : condition_frame.py
# @Software: PyCharm
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from constant import STATUS


class ConditionFrame(QFrame):
    def __init__(self, title):
        super(ConditionFrame, self).__init__()

        self.condFileList = []  # 条件文件列表

        # 标题标签
        self.titleLabel = QLabel(title)
        self.titleLabel.setObjectName('title-label')
        # 已完成计数标签
        self.finishedLabel = QLabel('')
        self.finishedLabel.setObjectName('finished-label')
        # 重置按钮
        self.resetBtn = QPushButton('重置')
        self.resetBtn.setFixedSize(50, 30)
        self.resetBtn.setCursor(Qt.PointingHandCursor)
        self.resetBtn.clicked.connect(self.reset)
        # 条件文件全选框
        self.checkAllBox = QCheckBox('全选')
        self.checkAllBox.setObjectName('condition-check-all-box')
        self.checkAllBox.hide()
        self.checkAllBox.clicked.connect(self.onCheckAll)
        # 条件文件信息表格
        self.condFileTable = QTableWidget()
        self.condFileTable.setObjectName('condition-file-table')
        self.condFileTable.setShowGrid(False)
        self.condFileTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.condFileTable.setColumnCount(3)
        self.condFileTable.setHorizontalHeaderLabels(['条件文件名', '状态', ''])
        self.condFileTable.setColumnWidth(0, 500)
        self.condFileTable.setColumnWidth(1, 250)
        self.condFileTable.setColumnWidth(2, 50)
        # 导入条件文件按钮
        self.importFilesBtn = QPushButton('文件导入')
        self.importFilesBtn.setObjectName('import-btn')
        self.importFilesBtn.setFixedSize(150, 30)
        self.importFilesBtn.setCursor(Qt.PointingHandCursor)
        self.importFilesBtn.clicked.connect(self.importConditionFiles)
        # 导入条件文件夹按钮
        self.importDirBtn = QPushButton('文件夹导入')
        self.importDirBtn.setObjectName('import-btn')
        self.importDirBtn.setFixedSize(150, 30)
        self.importDirBtn.setCursor(Qt.PointingHandCursor)
        self.importDirBtn.clicked.connect(self.importConditionDir)
        # 导入条件布局
        importLayout = QHBoxLayout()
        importLayout.addWidget(self.importFilesBtn)
        importLayout.addWidget(QLabel('/'))
        importLayout.addWidget(self.importDirBtn)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titleLabel, 0, 0, 2, 2)
        layout.addWidget(self.finishedLabel, 0, 4, 2, 2, alignment=Qt.AlignCenter)
        layout.addWidget(self.resetBtn, 0, 8, 2, 2, alignment=Qt.AlignCenter)
        layout.addWidget(self.checkAllBox, 0, 10, 2, 2, alignment=Qt.AlignRight)
        layout.addWidget(self.condFileTable, 2, 0, 16, 12)
        layout.addLayout(importLayout, 18, 0, 1, 12, alignment=Qt.AlignCenter)
        # layout.addWidget(self.importFilesBtn, 18, 0, 1, 6, alignment=Qt.AlignCenter)
        # layout.addWidget(self.importDirBtn, 18, 6, 1, 6, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def setTableItem(self, row, col, text):
        """
        设置表格元素
        """
        tableItem = QTableWidgetItem(text)
        tableItem.setTextAlignment(Qt.AlignCenter)
        self.condFileTable.setItem(row, col, tableItem)

    def modifyTableItem(self, row, col, text):
        """
        修改表格元素内容
        """
        tableItem = self.condFileTable.item(row, col)
        tableItem.setText(text)

    def modifyCondFile(self, id, key, value):
        """
        修改条件文件信息
        """
        self.condFileList[id][key] = value

    def setFinishedText(self, finished=0, total=0):
        """
        设置已完成文本
        :param finished: 已完成个数
        :param total: 总数
        :return:
        """
        self.finishedLabel.setText('' if total == 0 else f'已完成 {finished}/{total}')

    def onCheckAll(self):
        """
        全选按钮点击事件处理函数
        :return:
        """
        checked = self.checkAllBox.isChecked()
        for elem in self.condFileList:
            elem['check'].setChecked(checked)

    def importConditionDir(self):
        """
        导入条件文件夹
        :return:
        """
        condDir = QFileDialog.getExistingDirectory(self)  # 选择条件文件夹
        if not condDir:
            QMessageBox.warning(self, '提示', '未选择条件文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 如果选择了新的条件文件夹，清空记录的条件文件夹
        self.condFileList = []
        # 文件夹中所有文件
        condFiles = os.listdir(condDir)
        # 设置表格行数
        self.condFileTable.setRowCount(len(condFiles))
        # 将条件文件信息显示在表格中
        for idx, filename in enumerate(condFiles):
            # 过滤文件夹
            if os.path.isdir(os.path.join(condDir, filename)):
                continue
            # 设置表格元素
            self.setTableItem(idx, 0, filename)
            self.setTableItem(idx, 1, STATUS['UNCAL'])
            checkBoxItem = QCheckBox()
            self.condFileTable.setCellWidget(idx, 2, checkBoxItem)

            # 记录所有条件信息
            self.condFileList.append({
                'id': idx,
                'filename': filename,  # 条件文件名
                'filePath': os.path.join(condDir, filename),  # 条件文件路径
                'status': STATUS['UNCAL'],  # 条件状态
                'check': checkBoxItem,  # 是否被选中
            })

        # 显示全选条件文件复选框
        self.checkAllBox.show()

    def importConditionFiles(self):
        """
        导入条件文件
        :return:
        """
        condFiles, _ = QFileDialog.getOpenFileNames(self)  # 选择条件文件夹
        if not condFiles:
            QMessageBox.warning(self, '提示', '未选择条件文件！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 如果选择了新的条件文件夹，清空记录的条件文件夹
        self.condFileList = []
        # 设置表格行数
        self.condFileTable.setRowCount(len(condFiles))
        # 将条件文件信息显示在表格中
        for idx, file in enumerate(condFiles):
            filename = os.path.basename(file)
            # 设置表格元素
            self.setTableItem(idx, 0, filename)
            self.setTableItem(idx, 1, STATUS['UNCAL'])
            checkBoxItem = QCheckBox()
            self.condFileTable.setCellWidget(idx, 2, checkBoxItem)

            # 记录所有条件信息
            self.condFileList.append({
                'id': idx,
                'filename': filename,  # 条件文件名
                'filePath': file,  # 条件文件路径
                'status': STATUS['UNCAL'],  # 条件状态
                'check': checkBoxItem,  # 是否被选中
            })

        # 显示全选条件文件复选框
        self.checkAllBox.show()

    def getCheckedCondFiles(self):
        """
        获取选中的条件文件
        :return:
        """
        checkedCondFileList = []  # 选中的条件文件
        # 遍历查找被选中的条件
        for elem in self.condFileList:
            if elem['check'].isChecked() and elem['status'] != STATUS['FINISHED']:
                # 判断当前文件是否被误删
                if not os.path.exists(elem['filePath']):
                    elem['status'] = STATUS['NOTEXIST']  # 修改状态为文件不存在
                    continue
                checkedCondFileList.append(elem)

        return checkedCondFileList

    def getCheckedResults(self):
        """
        获取选中的已完成计算的条件文件对应的结果文件
        :return:
        """
        return [elem['resultFilePath'] for elem in self.condFileList
                if elem['check'].isChecked() and elem['status'] == STATUS['FINISHED']]

    def reset(self):
        """
        重置文件状态
        :return:
        """
        for elem in self.condFileList:
            elem['status'] = STATUS['UNCAL']
            self.modifyTableItem(elem['id'], 1, STATUS['UNCAL'])
        self.setFinishedText(0, 0)