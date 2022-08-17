import multiprocessing
import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils import resultToFile
from constant import STATUS
from workThread import WorkThread


def setTableItem(tableWidget, row, col, text):
    """
    设置表格元素
    """
    tableItem = QTableWidgetItem(text)
    tableItem.setTextAlignment(Qt.AlignCenter)
    tableWidget.setItem(row, col, tableItem)


def modifyTableItem(tableWidget, row, col, text):
    """
    修改表格元素内容
    """
    tableItem = tableWidget.item(row, col)
    tableItem.setText(text)


class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resultDir = ''  # 结果保存的文件夹
        self.conditionFileList = []  # 导入的条件文件列表
        self.outerResultList = []  # 导入的外部结果列表

        self.finalResult = []  # 最终结果（即导入excel文件的结果）

        self.setWindowTitle('数字组合工具')  # 标题
        self.setWindowIcon(QIcon('./favicon.ico'))  # 图标
        self.resize(1200, 800)  # 窗口大小
        # 设置背景颜色
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))  # 设置背景颜色
        self.setPalette(palette)

        # 有效截止时间
        validDeadline = datetime.strptime('2022_08_20', '%Y_%m_%d')
        # 超过截止时间不显示
        if datetime.now() > validDeadline:
            return
            
        # 初始化布局
        self.initUi()

    def initUi(self):
        """
    初始化界面UI
    """
        # 设置窗口的中心部件
        self.centerWidget = QWidget()
        self.setCentralWidget(self.centerWidget)

        # 模块1部件
        self.module1Widget = QWidget()
        # 模块2部件
        self.module2Widget = QWidget()

        # 设置中心部件布局
        centerLayout = QGridLayout()
        centerLayout.addWidget(self.module1Widget, 0, 0, 0, 0)
        centerLayout.addWidget(self.module2Widget, 0, 0, 0, 0)
        self.centerWidget.setLayout(centerLayout)

        # 模块2部件初始不可见
        self.module2Widget.hide()

        # *************************** 模块1界面布局 *****************************
        # 设置结果文件夹按钮
        self.resultDirSetBtn = QPushButton('设置结果文件夹')
        self.resultDirSetBtn.setObjectName('result-dir-set-btn')
        self.resultDirSetBtn.setFixedSize(180, 50)
        self.resultDirSetBtn.setCursor(Qt.PointingHandCursor)
        self.resultDirSetBtn.clicked.connect(self.selectSaveDir)
        # 显示设置的文件夹路径
        self.resultDirPathLabel = QLabel('')
        self.resultDirPathLabel.setObjectName('result-dir-path-label')

        # 模块1内容区
        self.module1ContentFrame = QFrame()
        self.module1ContentFrame.setObjectName('module1-content-frame')
        # 条件文件表格标签
        self.conditionFileLabel = QLabel('条件文件')
        self.conditionFileLabel.setObjectName('file-label')
        # 已完成计数标签
        self.finishedLabel = QLabel('')
        self.finishedLabel.setObjectName('finished-label')
        # 条件文件全选框
        self.conditionCheckAllBox = QCheckBox('全选')
        self.conditionCheckAllBox.setObjectName('condition-check-all-box')
        self.conditionCheckAllBox.hide()
        self.conditionCheckAllBox.clicked.connect(self.selectAllConditionFiles)
        # 外部结果文件标签
        self.outerResultFileLabel = QLabel('外部结果文件')
        self.outerResultFileLabel.setObjectName('file-label')
        # 外部结果文件全选框
        self.outerResultCheckAllBox = QCheckBox('全选')
        self.outerResultCheckAllBox.setObjectName('outer-result-check-all-label')
        self.outerResultCheckAllBox.hide()
        self.outerResultCheckAllBox.clicked.connect(self.selectAllOuterResults)

        # 条件文件信息表格
        self.conditionFileTable = QTableWidget()
        self.conditionFileTable.setObjectName('condition-file-table')
        self.conditionFileTable.setShowGrid(False)
        self.conditionFileTable.setColumnCount(4)
        self.conditionFileTable.setHorizontalHeaderLabels(['条件文件名', '对应结果文件名', '状态', ''])
        self.conditionFileTable.setColumnWidth(0, 220)
        self.conditionFileTable.setColumnWidth(1, 220)
        self.conditionFileTable.setColumnWidth(2, 120)
        self.conditionFileTable.setColumnWidth(3, 50)
        # 外部结果文件信息表格
        self.outerResultFileTable = QTableWidget()
        self.outerResultFileTable.setObjectName('outer-result-file-tbale')
        self.outerResultFileTable.setShowGrid(False)
        self.outerResultFileTable.setColumnCount(2)
        self.outerResultFileTable.setHorizontalHeaderLabels(['外部结果文件名', ''])
        self.outerResultFileTable.setColumnWidth(0, 340)
        self.outerResultFileTable.setColumnWidth(1, 50)

        # 根据条件文件计算数字组合进度条
        self.calProgressBar = QProgressBar()
        self.calProgressBar.setMinimum(0)
        self.calProgressBar.setMaximum(100)
        self.calProgressBar.setValue(0)
        # 合并结果文件进度条
        self.mergeProgressBar = QProgressBar()
        self.mergeProgressBar.setMinimum(0)
        self.mergeProgressBar.setMaximum(100)
        self.mergeProgressBar.setValue(0)

        # 导入条件文件按钮
        self.importConditionFileBtn = QPushButton('导入条件文件夹')
        self.importConditionFileBtn.setObjectName('import-btn')
        self.importConditionFileBtn.setFixedSize(200, 30)
        self.importConditionFileBtn.setCursor(Qt.PointingHandCursor)
        self.importConditionFileBtn.clicked.connect(self.importCondition)
        # 导入外部结果按钮
        self.importOuterResultBtn = QPushButton('导入外部结果')
        self.importOuterResultBtn.setObjectName('import-btn')
        self.importOuterResultBtn.setFixedSize(200, 30)
        self.importOuterResultBtn.setCursor(Qt.PointingHandCursor)
        self.importOuterResultBtn.clicked.connect(self.importOuterResult)

        # 模块1内容区布局
        module1ContentLayout = QGridLayout()
        module1ContentLayout.addWidget(self.conditionFileLabel, 0, 0, 2, 6)
        module1ContentLayout.addWidget(self.finishedLabel, 0, 6, 2, 7)
        module1ContentLayout.addWidget(self.conditionCheckAllBox, 0, 13, 2, 1)
        module1ContentLayout.addWidget(self.outerResultFileLabel, 0, 15, 2, 8)
        module1ContentLayout.addWidget(self.outerResultCheckAllBox, 0, 23, 2, 1)
        module1ContentLayout.addWidget(self.conditionFileTable, 2, 0, 16, 14)
        module1ContentLayout.addWidget(self.outerResultFileTable, 2, 15, 16, 9)
        module1ContentLayout.addWidget(self.calProgressBar, 18, 0, 1, 14)
        module1ContentLayout.addWidget(self.mergeProgressBar, 18, 15, 1, 9)
        module1ContentLayout.addWidget(self.importConditionFileBtn, 19, 0, 1, 14, alignment=Qt.AlignCenter)
        module1ContentLayout.addWidget(self.importOuterResultBtn, 19, 14, 1, 10, alignment=Qt.AlignCenter)
        self.module1ContentFrame.setLayout(module1ContentLayout)

        # 开始按钮
        self.startBtn = QPushButton('开 始')
        self.startBtn.setObjectName('start-btn')
        self.startBtn.setFixedSize(150, 40)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.clicked.connect(self.onStart)
        # 暂停按钮
        # self.suspendBtn = QPushButton('暂 停')
        # self.suspendBtn.setObjectName('suspend-btn')
        # self.suspendBtn.setFixedSize(150, 40)
        # self.suspendBtn.setCursor(Qt.PointingHandCursor)
        # self.suspendBtn.clicked.connect(self.onSuspend)
        # 结束按钮
        self.endBtn = QPushButton('结 束')
        self.endBtn.setObjectName('end-btn')
        self.endBtn.setFixedSize(150, 40)
        self.endBtn.setCursor(Qt.PointingHandCursor)
        self.endBtn.hide()  # 初始不显示结束按钮，等开始就算才显示
        self.endBtn.clicked.connect(self.onEnd)
        # 进程数
        self.processLabel = QLabel('进程数：')
        self.processLabel.setObjectName('process-label')
        # 进程数选择
        self.processSpin = QSpinBox()
        self.processSpin.setObjectName('process-spin')
        self.processSpin.setMaximum(100)
        self.processSpin.setMinimum(1)
        self.processSpin.setValue(10)

        # 容错标签
        self.faultLabel = QLabel('容错')
        self.faultLabel.setObjectName('fault-label')
        # 容错左边界
        self.faultLeftSpin = QSpinBox()
        self.faultLeftSpin.setObjectName('fault-spin')
        # 容错右边界
        self.faultRightSpin = QSpinBox()
        self.faultRightSpin.setObjectName('fault-spin')
        # 合并结果按钮
        self.mergeResultBtn = QPushButton('合并结果')
        self.mergeResultBtn.setObjectName('result-btn')
        self.mergeResultBtn.setFixedSize(150, 40)
        self.mergeResultBtn.setCursor(Qt.PointingHandCursor)
        self.mergeResultBtn.clicked.connect(self.mergeResult)
        # 导出结果按钮
        self.exportResultBtn = QPushButton('导出结果')
        self.exportResultBtn.setObjectName('result-btn')
        self.exportResultBtn.setFixedSize(150, 40)
        self.exportResultBtn.setCursor(Qt.PointingHandCursor)
        self.exportResultBtn.clicked.connect(self.exportResult)

        # 设置模块1总体布局
        module1Layout = QGridLayout()
        module1Layout.addWidget(self.resultDirSetBtn, 0, 0, 2, 4)
        module1Layout.addWidget(self.resultDirPathLabel, 0, 5, 2, 19)
        module1Layout.addWidget(self.module1ContentFrame, 2, 0, 20, 24)
        module1Layout.addWidget(self.startBtn, 22, 0, 2, 4, alignment=Qt.AlignLeft)
        module1Layout.addWidget(self.endBtn, 22, 4, 2, 4, alignment=Qt.AlignLeft)
        module1Layout.addWidget(self.processLabel, 22, 10, 2, 2, alignment=Qt.AlignRight)
        module1Layout.addWidget(self.processSpin, 22, 12, 2, 2, alignment=Qt.AlignLeft)
        module1Layout.addWidget(self.faultLabel, 22, 15, 2, 1)
        module1Layout.addWidget(self.faultLeftSpin, 22, 16, 2, 1)
        module1Layout.addWidget(self.faultRightSpin, 22, 17, 2, 1)
        module1Layout.addWidget(self.mergeResultBtn, 22, 18, 2, 3, alignment=Qt.AlignRight)
        module1Layout.addWidget(self.exportResultBtn, 22, 21, 2, 3, alignment=Qt.AlignRight)
        self.module1Widget.setLayout(module1Layout)

        self.module1Widget.setStyleSheet("""
        QLabel {
            font-size: 20px;
            font-family: '微软雅黑'
        }

        QLabel#file-label {
            font-size: 24px;
            font-family: '微软雅黑';
            font-weight: 400
        }

        QLabel#finished-label {
            color: #00BFFF;
            font-weight: 400
        }

        QFrame#module1-content-frame {
            border: 1px solid #D3D3D3;
            border-radius: 5px;
        }

        QPushButton {
            border: 1px solid #d3d7d4;
            color: #1c1e21;
            font-size: 22px;
            font-family: '黑体';
            font-weight: 400;
            border-radius: 5px;
        }

        QPushButton:hover {
            border: 1px solid #69c0ff;
            color: #69c0ff;
        }

        QPushButton#import-btn {
            font-size: 20px;
            border: None;
        }

        QPushButton#result-btn
        {
            border: None;
            background: #40a9ff;
            color: #fff
        }

        QPushButton#result-btn:hover {
            background: #69c0ff;
        }
        """)
    
    def modifyConditionFileList(self, id, key, value):
        """
        修改条件文件信息
        """
        self.conditionFileList[id][key] = value

    def selectSaveDir(self):
        """
        选择保存结果的文件夹
        """
        dirPath = QFileDialog.getExistingDirectory(self)
        self.resultDir = dirPath  # 记录选择的结果保存文件夹
        self.resultDirPathLabel.setText(dirPath)  # 显示选择的结果文件夹

    def selectAllConditionFiles(self):
        """
      全选条件文件
      """
        checked = self.conditionCheckAllBox.isChecked()
        for elem in self.conditionFileList:
            elem['check'].setChecked(checked)

    def selectAllOuterResults(self):
        """
      全选外部结果
      """
        checked = self.outerResultCheckAllBox.isChecked()
        for elem in self.outerResultList:
            elem['check'].setChecked(checked)

    def importCondition(self):
        """
        导入条件文件
        """
        conditionDir = QFileDialog.getExistingDirectory(self)  # 选择条件文件夹
        if not conditionDir:
            QMessageBox.warning(self, '提示', '未选择条件文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 如果选择了新的条件文件夹，清空记录的条件文件夹
        self.conditionFileList = []
        # 文件夹中所有文件
        conditionFiles = os.listdir(conditionDir)
        # 设置表格行数
        self.conditionFileTable.setRowCount(len(conditionFiles))
        # 将条件文件信息显示在表格中
        for idx, filename in enumerate(conditionFiles):
            # 过滤文件夹
            if os.path.isdir(os.path.join(conditionDir, filename)):
                continue
            # 设置表格元素
            setTableItem(self.conditionFileTable, idx, 0, filename)
            setTableItem(self.conditionFileTable, idx, 1, '无')
            setTableItem(self.conditionFileTable, idx, 2, STATUS['UNCAL'])
            checkBoxItem = QCheckBox()
            self.conditionFileTable.setCellWidget(idx, 3, checkBoxItem)

            # 记录所有条件信息
            self.conditionFileList.append({
                'id': idx,
                'filename': filename,  # 条件文件名
                'filePath': os.path.join(conditionDir, filename),  # 条件文件路径
                'resultFilename': '无',  # 对应结果文件名，初始化为无（因为未计算）
                'resultFilePath': '',  # 结果文件路径
                'status': STATUS['UNCAL'],  # 条件状态
                'check': checkBoxItem,  # 是否被选中
            })

        # 显示全选条件文件复选框
        self.conditionCheckAllBox.show()

    def importOuterResult(self):
        """
        导入外部结果
        """
        outerResultDir = QFileDialog.getExistingDirectory(self)  # 选择条件文件夹
        if not outerResultDir:
            QMessageBox.warning(self, '提示', '外部结果未导入！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 选择了新的外部文件夹，则重置外部结果记录
        self.outerResultList = []
        # 外部结果文件中所有文件名
        outerResultFiles = os.listdir(outerResultDir)
        # 重置表格行数
        resultCount = len(outerResultFiles)
        self.outerResultFileTable.setRowCount(resultCount)
        # 导入的外部结果信息显示在表格中
        for idx, filename in enumerate(outerResultFiles):
            filePath = os.path.join(outerResultDir, filename)
            # 过滤文件夹
            if os.path.isdir(filePath):
                continue
            # 设置表格元素
            setTableItem(self.outerResultFileTable, idx, 0, filename)
            checkBoxItem = QCheckBox()
            self.outerResultFileTable.setCellWidget(idx, 1, checkBoxItem)

            outerResult = {
                'id': idx,
                'filename': filename,  # 结果文件名
                'filePath': os.path.join(outerResultDir, filename),
                'check': checkBoxItem  # 是否被选中
            }
            # 记录所有外部结果信息
            self.outerResultList.append(outerResult)

        # 显示全选外部结果复选框
        self.outerResultCheckAllBox.show()

    def onStart(self):
        """
      开始按钮点击函数
      """
        self.calProgressBar.setValue(0)  # 进度条清空
        checkedConditionFiles = []  # 选中的条件
        # 遍历查找被选中的条件
        for elem in self.conditionFileList:
            if elem['check'].isChecked() and elem['status'] != STATUS['FINISHED']:
                # 判断当前文件是否被误删
                if not os.path.exists(elem['filePath']):
                    elem['status'] = STATUS['NOTEXIST']  # 修改状态为文件不存在
                else:
                    # 修改要进行计算的状态为等待中
                    elem['status'] = STATUS['WAITING']
                    checkedConditionFiles.append(elem)
                # 修改对应表格中的状态
                modifyTableItem(self.conditionFileTable, elem['id'], 2, elem['status'])

        # 如果没有选中文件
        if not checkedConditionFiles:
            QMessageBox.warning(self, '提示', '未选择进行计算的条件文件！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 判断是否设置了结果文件夹
        if not self.resultDir:
            QMessageBox.warning(self, '提示', '未选择结果保存文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 判断设置的结果文件夹是否仍然存在
        if not os.path.exists(self.resultDir):
            QMessageBox.warning(self, '提示', '结果文件夹已不存在（被误删）！', QMessageBox.Yes, QMessageBox.Yes)
            return
        
        # 显示结束按钮
        self.endBtn.show()  

        # 进程数
        processCount = self.processSpin.value()
        # 选中的文件数
        self.checkedCount = len(checkedConditionFiles)
        self.finishedLabel.setText('已完成 {:d}/{:d}'.format(0, self.checkedCount))
        # 开启子线程计算条件
        self.workThread = WorkThread(checkedConditionFiles, self.resultDir, processCount)
        self.workThread.progress.connect(self.onProgressChanged)
        self.workThread.fileStatus.connect(self.onFileStatusChanged)
        self.workThread.finishedCount.connect(self.onFinishedCountChanged)
        self.workThread.start()

    def onProgressChanged(self, status):
        """
        进度条值发生改变
        """
        self.calProgressBar.setValue(status)

    def onFinishedCountChanged(self, status):
        """
        完成的文件个数发生改变
        """
        # 记录完成的个数
        self.finishedLabel.setText('已完成 {:d}/{:d}'.format(status, self.checkedCount))
        # 如果所有文件完成，则提示
        if status == self.checkedCount:
            QMessageBox.information(self, '提示', '全部文件已计算完成！', QMessageBox.Yes, QMessageBox.Yes)

    def onFileStatusChanged(self, status):
        """
        文件状态改变时
        """
        modifyTableItem(self.conditionFileTable, status[0], 2, status[1])
        self.modifyConditionFileList(status[0], 'status', status[1])

    def onResultPathChanged(self, status):
        """
        文件状态改变时
        """
        filename = os.path.basename(status[1])
        modifyTableItem(self.conditionFileTable, status[0], 1, filename)
        self.modifyConditionFileList(status[0], 'resultFilename', filename)
        self.modifyConditionFileList(status[0], 'resultFilePath', status[1])

    def onEnd(self):
        """
        结束按钮点击函数
        """
        self.workThread.pool.terminate()  # 终止进程
        self.workThread.terminate()  # 终止线程
        self.calProgressBar.setValue(0)  # 进度条清空

        # 修改未计算文件状态
        for item in self.conditionFileList:
            if item['status'] in [STATUS['WAITING'], STATUS['RUNNING']]:
                item['status'] = STATUS['UNCAL']
                modifyTableItem(self.conditionFileTable, item['id'], 2, STATUS['UNCAL'])

        QMessageBox.information(self, '提示', '计算已终止！！！', QMessageBox.Yes, QMessageBox.Yes)


    def mergeResult(self):
        """
      合并结果
      """
        self.mergeProgressBar.setValue(0)  # 清空合并进度条

        checkedResultFiles = []  # 选中的要合并的结果
        # 依据条件计算出的结果
        for elem in self.conditionFileList:
            if elem['check'].isChecked() and elem['status'] == STATUS['FINISHED']:
                checkedResultFiles.append(elem['resultFilePath'])
        # 外部导入的结果
        for elem in self.outerResultList:
            if elem['check'].isChecked():
                checkedResultFiles.append(elem['filePath'])
        # 判断是否选中了可合并的结果
        if not checkedResultFiles:
            QMessageBox.warning(self, '提示', '未选中可合并的结果！', QMessageBox.Yes, QMessageBox.Yes)
            return

        faultLeft = self.faultLeftSpin.value()  # 容错左边界
        faultRight = self.faultRightSpin.value()  # 容错右边界
        # 容错范围正确性检验
        if faultLeft > faultRight:
            QMessageBox.warning(self, '提示', '容错范围错误，左边界大于右边界！', QMessageBox.Yes, QMessageBox.Yes)
            return

        checkCount = len(checkedResultFiles)  # 选中的结果个数
        if faultRight > checkCount:
            QMessageBox.warning(self, '提示', '容错范围右边界不能大于选中的合并结果个数！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 读取结果文件内容
        combinationCount = {}
        for idx, filePath in enumerate(checkedResultFiles):
            with open(filePath, mode='r', encoding='utf8') as rf:
                for combination in [tuple(line.strip('\n').split(' ')) for line in rf.readlines()]:
                    combinationCount[combination] = combinationCount.get(combination, 0) + 1
            self.mergeProgressBar.setValue(int((idx + 1) / checkCount * 100) - 1)
            QApplication.processEvents()  # 读取完文件后刷新屏幕，防止卡频

        # 合并的结果
        mergeResult = []
        for key, value in combinationCount.items():
            if faultLeft <= checkCount - value <= faultRight:
                mergeResult.append(key)

        # 记录合并结果
        self.finalResult = mergeResult
        # 进度条结束
        self.mergeProgressBar.setValue(100)
        QMessageBox.information(self, '提示', '合并成功！', QMessageBox.Yes, QMessageBox.Yes)

    def exportResult(self):
        """
      导出结果
      """
        # 判断有无可导出的结果
        if not self.finalResult:
            QMessageBox.warning(self, '提示', '未合并可导出的结果！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 判断是否设置了导出的文件夹
        if not self.resultDir:
            QMessageBox.warning(self, '提示', '未设置结果文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return

        # 保存合并结果文件名
        resultFilename = '合并结果-{}.txt'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
        # 结果文件保存路径
        resultSavePath = os.path.join(self.resultDir, resultFilename)
        # 将结果写入文件
        resultToFile(self.finalResult, resultSavePath)

        QMessageBox.information(self, '提示', '结果导出成功！\n已保存在文件{}中'.format(resultSavePath), QMessageBox.Yes,
                                QMessageBox.Yes)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)  # 创建应用程序
    gui = MainUi()  # 新建窗口
    gui.show()  # 显示窗口
    sys.exit(app.exec_())  # 调用系统方法保证程序能够退出
