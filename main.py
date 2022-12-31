import multiprocessing
import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from constant import STATUS, CAL_TYPE, MERGE_TYPE
from threads.cal_thread import CalThread
from threads.merge_thread import MergeThread
from components.condition_frame import ConditionFrame
from components.result_frame import ResultFrame
from components.spin_box import SpinBox


class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resultDir = ''  # 结果保存的文件夹
        self.finalResult = []  # 最终结果（即导入excel文件的结果）

        self.calThread = None  # 计算结果子线程
        self.mergeThread = None  # 合并结果子线程

        self.setWindowTitle('数字组合工具')  # 标题
        self.setWindowIcon(QIcon('./favicon.ico'))  # 图标
        self.resize(1800, 1000)  # 窗口大小
        # 设置背景颜色
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))  # 设置背景颜色
        self.setPalette(palette)
        if datetime.now() < datetime.strptime('2023_01_07', '%Y_%m_%d'):
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

        # 设置中心部件布局
        centerLayout = QGridLayout()
        centerLayout.addWidget(self.module1Widget, 0, 0, 0, 0)
        self.centerWidget.setLayout(centerLayout)

        # *************************** 模块1界面布局 *****************************
        # 头部区域
        self.headFrame = QFrame()
        self.headFrame.setObjectName('head-frame')
        # 设置结果文件夹按钮
        self.resultDirSetBtn = QPushButton('设置结果文件夹')
        self.resultDirSetBtn.setObjectName('result-dir-set-btn')
        self.resultDirSetBtn.setFixedSize(180, 50)
        self.resultDirSetBtn.setCursor(Qt.PointingHandCursor)
        self.resultDirSetBtn.clicked.connect(self.selectSaveDir)
        # 显示设置的文件夹路径
        self.resultDirPathLabel = QLabel('')
        self.resultDirPathLabel.setObjectName('result-dir-path-label')
        # # 导出结果按钮
        # self.exportResultBtn = QPushButton('导出结果')
        # self.exportResultBtn.setObjectName('primary-btn')
        # self.exportResultBtn.setFixedSize(150, 50)
        # self.exportResultBtn.setCursor(Qt.PointingHandCursor)
        # self.exportResultBtn.clicked.connect(self.exportResult)
        # 头部布局
        headLayout = QGridLayout()
        headLayout.addWidget(self.resultDirSetBtn, 0, 0, 2, 3)
        headLayout.addWidget(self.resultDirPathLabel, 0, 3, 2, 21)
        # headLayout.addWidget(self.exportResultBtn, 0, 20, 2, 4, alignment=Qt.AlignRight)
        self.headFrame.setLayout(headLayout)

        # 左边框布局
        self.leftFrame = QFrame()
        # 条件框
        self.condFrame = ConditionFrame('条件文件')
        # 根据条件文件计算数字组合进度条
        self.calProgressBar = QProgressBar()
        self.calProgressBar.setMinimum(0)
        self.calProgressBar.setMaximum(100)
        self.calProgressBar.setValue(0)
        # 进程数
        self.processLabel = QLabel('进程数：')
        self.processLabel.setObjectName('process-label')
        # 进程数选择
        self.processSpin = SpinBox(10, 1, 100)
        self.processSpin.setObjectName('process-spin')
        # 逐行选择
        self.byLineCheckBox = QCheckBox('逐  ')
        self.byLineCheckBox.clicked.connect(self.onByLineClick)
        self.byLineSpin = SpinBox()
        byLineLayout = QHBoxLayout()
        byLineLayout.addWidget(self.byLineCheckBox)
        byLineLayout.addWidget(self.byLineSpin)
        byLineLayout.addWidget(QLabel('行'))
        # 随机次选择
        self.randomLineCheckBox = QCheckBox('随机')
        self.randomLineCheckBox.clicked.connect(self.onRandomLineClick)
        self.randomLineSpin = SpinBox()  # 随机选多少行
        self.randomCntSpin = SpinBox()  # 随机多少次
        randomLineLayout = QHBoxLayout()
        randomLineLayout.addWidget(self.randomLineCheckBox)
        randomLineLayout.addWidget(self.randomLineSpin)
        randomLineLayout.addWidget(QLabel('行'))
        randomLineLayout.addWidget(self.randomCntSpin)
        randomLineLayout.addWidget(QLabel('次'))
        # 开始按钮
        self.startBtn = QPushButton('开 始')
        self.startBtn.setObjectName('primary-btn')
        self.startBtn.setFixedSize(100, 40)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.clicked.connect(self.onStart)
        # 结束按钮
        self.endBtn = QPushButton('结 束')
        self.endBtn.setObjectName('end-btn')
        self.endBtn.setFixedSize(100, 40)
        self.endBtn.setCursor(Qt.PointingHandCursor)
        # self.endBtn.hide()  # 初始不显示结束按钮，等开始就算才显示
        self.endBtn.clicked.connect(self.onEnd)
        # 左边框布局
        leftLayout = QGridLayout()
        leftLayout.addWidget(self.condFrame, 0, 0, 19, 12)
        leftLayout.addWidget(self.calProgressBar, 19, 0, 1, 12)
        leftLayout.addWidget(self.processLabel, 20, 0, 2, 1)
        leftLayout.addWidget(self.processSpin, 20, 1, 2, 1, alignment=Qt.AlignLeft)
        leftLayout.addLayout(byLineLayout, 20, 3, 1, 3)
        leftLayout.addLayout(randomLineLayout, 21, 3, 1, 4)
        leftLayout.addWidget(self.startBtn, 20, 10, 1, 2, alignment=Qt.AlignRight)
        leftLayout.addWidget(self.endBtn, 21, 10, 1, 2, alignment=Qt.AlignRight)
        self.leftFrame.setLayout(leftLayout)

        # 右边框
        self.rightFrame = QFrame()
        # 基础结果框
        self.basiceRsultFrame = ResultFrame('基础结果文件', '导入基础结果')
        # 其他结果框
        self.otherRresultFrame = ResultFrame('其他结果文件', '导入其他结果')
        # 合并结果文件进度条
        self.mergeProgressBar = QProgressBar()
        self.mergeProgressBar.setMinimum(0)
        self.mergeProgressBar.setMaximum(100)
        self.mergeProgressBar.setValue(0)
        # 容错标签
        self.faultLabel = QLabel('容错：')
        self.faultLabel.setObjectName('fault-label')
        # 容错左边界
        self.faultLeftSpin = SpinBox(0, 0, 10000)
        self.faultLeftSpin.setObjectName('fault-spin')
        # 容错右边界
        self.faultRightSpin = SpinBox(0, 0, 10000)
        self.faultRightSpin.setObjectName('fault-spin')
        # 随机组合选择
        self.randomMergeCheckBox = QCheckBox('随机')
        self.randomMergeCheckBox.clicked.connect(self.onRandomMergeClick)
        self.randomMergeCntSpin = SpinBox(1, 1)  # 随机组合次数
        randomMergeLayout = QHBoxLayout()
        randomMergeLayout.addWidget(self.randomMergeCheckBox, alignment=Qt.AlignLeft)
        randomMergeLayout.addWidget(self.randomMergeCntSpin, alignment=Qt.AlignLeft)
        randomMergeLayout.addWidget(QLabel('次'), alignment=Qt.AlignLeft)
        # 全部组合选择
        self.allMergeCheckBox = QCheckBox('全部组合')
        self.allMergeCheckBox.clicked.connect(self.onAllMergeClick)
        # 组合个数布局
        self.otherCntSpin = SpinBox(1, 1)
        otherCntLayout = QHBoxLayout()
        otherCntLayout.addWidget(self.otherCntSpin)
        otherCntLayout.addWidget(QLabel('个'))
        # 合并结果按钮
        self.mergeResultBtn = QPushButton('合并结果')
        self.mergeResultBtn.setObjectName('primary-btn')
        self.mergeResultBtn.setFixedSize(120, 40)
        self.mergeResultBtn.setCursor(Qt.PointingHandCursor)
        self.mergeResultBtn.clicked.connect(self.mergeResult)
        # 合并结果按钮
        self.stopMergeBtn = QPushButton('终止合并')
        self.stopMergeBtn.setFixedSize(120, 40)
        self.stopMergeBtn.setCursor(Qt.PointingHandCursor)
        self.stopMergeBtn.clicked.connect(self.onStopMerge)
        # 右边框布局
        rightLayout = QGridLayout()
        rightLayout.addWidget(self.basiceRsultFrame, 0, 0, 19, 6)
        rightLayout.addWidget(self.otherRresultFrame, 0, 6, 19, 6)
        rightLayout.addWidget(self.mergeProgressBar, 19, 0, 1, 12)
        rightLayout.addWidget(self.faultLabel, 20, 0, 2, 1)
        rightLayout.addWidget(self.faultLeftSpin, 20, 1, 2, 1)
        rightLayout.addWidget(self.faultRightSpin, 20, 2, 2, 1)
        rightLayout.addLayout(randomMergeLayout, 20, 4, 1, 3)
        rightLayout.addWidget(self.allMergeCheckBox, 21, 4, 1, 3)
        rightLayout.addLayout(otherCntLayout, 20, 7, 2, 2, alignment=Qt.AlignLeft)
        rightLayout.addWidget(self.mergeResultBtn, 20, 9, 1, 3, alignment=Qt.AlignRight)
        rightLayout.addWidget(self.stopMergeBtn, 21, 9, 1, 3, alignment=Qt.AlignRight)
        self.rightFrame.setLayout(rightLayout)

        # 设置模块1总体布局
        module1Layout = QGridLayout()
        module1Layout.addWidget(self.headFrame, 0, 0, 2, 24)
        module1Layout.addWidget(self.leftFrame, 2, 0, 22, 12)
        module1Layout.addWidget(self.rightFrame, 2, 12, 22, 12)
        self.module1Widget.setLayout(module1Layout)

        self.module1Widget.setStyleSheet("""
        QLabel#result-dir-path-label {
            border: 1px solid #DCDCDC;
            border-radius: 5px;
        }
        QLabel {
            font-size: 20px;
            font-family: '微软雅黑'
        }

        QLabel#title-label {
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

        QPushButton#primary-btn
        {
            border: None;
            background: #40a9ff;
            color: #fff
        }

        QPushButton#primary-btn:hover {
            background: #69c0ff;
        }
        """)

    def onByLineClick(self):
        """
        逐行运算选中框点击事件处理函数
        :return:
        """
        if self.byLineCheckBox.isChecked():
            self.randomLineCheckBox.setChecked(False)

    def onRandomLineClick(self):
        """
        随机行运算选中框点击事件处理函数
        :return:
        """
        if self.randomLineCheckBox.isChecked():
            self.byLineCheckBox.setChecked(False)

    def onAllMergeClick(self):
        """
        全部组合选中框点击事件处理函数
        :return:
        """
        if self.allMergeCheckBox.isChecked():
            self.randomMergeCheckBox.setChecked(False)

    def onRandomMergeClick(self):
        """
        随机组合框点击事件处理函数
        :return:
        """
        if self.randomMergeCheckBox.isChecked():
            self.allMergeCheckBox.setChecked(False)

    def selectSaveDir(self):
        """
        选择保存结果的文件夹
        """
        dirPath = QFileDialog.getExistingDirectory(self)
        self.resultDir = dirPath  # 记录选择的结果保存文件夹
        self.resultDirPathLabel.setText(dirPath)  # 显示选择的结果文件夹

    def onStart(self):
        """
        开始按钮点击函数
        """
        self.calProgressBar.setValue(0)  # 进度条清空
        # 获取选中的条件文件
        checkedCondFiles = self.condFrame.getCheckedCondFiles()
        # 判断是否设置了结果文件夹
        if not self.resultDir:
            QMessageBox.warning(self, '提示', '未选择结果保存文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 判断设置的结果文件夹是否仍然存在
        if not os.path.exists(self.resultDir):
            QMessageBox.warning(self, '提示', '结果文件夹已不存在（被误删）！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 如果没有选中文件
        if not checkedCondFiles:
            QMessageBox.warning(self, '提示', '未选择进行计算的条件文件！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 修改选中文件信息
        for elem in checkedCondFiles:
            # 修改要进行计算的状态为等待中
            elem['status'] = STATUS['WAITING']
            # 修改对应表格中的状态
            self.condFrame.modifyTableItem(elem['id'], 1, elem['status'])
        # 选中的文件数
        self.checkedCondCnt = len(checkedCondFiles)
        self.condFrame.setFinishedText(0, self.checkedCondCnt)
        # 显示结束按钮
        self.endBtn.show()
        # 进程数
        processCnt = self.processSpin.value()
        lineCnt = 0  # 行数
        randomCnt = 0  # 随机计算次数
        # 计算方式
        if self.byLineCheckBox.isChecked():
            calType = CAL_TYPE['BY_LINE']
            lineCnt = self.byLineSpin.value()
        elif self.randomLineCheckBox.isChecked():
            calType = CAL_TYPE['RANDOM_LINE']
            lineCnt = self.randomLineSpin.value()
            randomCnt = self.randomCntSpin.value()
        else:
            calType = CAL_TYPE['BY_FILE']
        # 进度条设置为1，标识开始计算
        self.calProgressBar.setValue(1)
        # 禁用开始按钮、合并按钮
        self.mergeResultBtn.setDisabled(True)
        self.startBtn.setDisabled(True)
        # 开启子线程计算条件
        self.calThread = CalThread(checkedCondFiles, self.resultDir, processCnt, calType, lineCnt, randomCnt)
        self.calThread.progress.connect(self.onCalProgressChanged)
        self.calThread.fileStatus.connect(self.onCalFileStatusChanged)
        self.calThread.finishedCnt.connect(self.onCalFinishedCntChanged)
        self.calThread.start()

    def onCalProgressChanged(self, status):
        """
        进度条值发生改变
        """
        self.calProgressBar.setValue(status)

    def onCalFinishedCntChanged(self, status):
        """
        完成的文件个数发生改变
        """
        # 记录完成的个数
        self.condFrame.setFinishedText(status, self.checkedCondCnt)
        # 如果所有文件完成，则提示
        if status == self.checkedCondCnt:
            # 启用开始按钮、合并按钮
            self.mergeResultBtn.setDisabled(False)
            self.startBtn.setDisabled(False)
            QMessageBox.information(self, '提示', '全部文件已计算完成！', QMessageBox.Yes, QMessageBox.Yes)

    def onCalFileStatusChanged(self, status):
        """
        文件状态改变时
        """
        self.condFrame.modifyTableItem(status[0], 1, status[1])
        self.condFrame.modifyCondFile(status[0], 'status', status[1])

    def onEnd(self):
        """
        结束按钮点击函数
        """
        # 未开启子线程
        if self.calThread is None:
            return
        # 未开启进程池
        if self.calThread.pool is None:
            return
        self.calThread.pool.terminate()  # 终止进程
        self.calThread.terminate()  # 终止线程
        self.calProgressBar.setValue(0)  # 进度条清空
        # 修改未计算文件状态
        for item in self.condFrame.condFileList:
            if item['status'] in [STATUS['WAITING'], STATUS['RUNNING']]:
                item['status'] = STATUS['UNCAL']
                self.condFrame.modifyTableItem(item['id'], 1, STATUS['UNCAL'])
        # 启用开始按钮、合并按钮
        self.mergeResultBtn.setDisabled(False)
        self.startBtn.setDisabled(False)
        self.condFrame.setFinishedText(0, 0)

        QMessageBox.information(self, '提示', '计算已终止！！！', QMessageBox.Yes, QMessageBox.Yes)

    def mergeResult(self):
        """
      合并结果
      """
        self.mergeProgressBar.setValue(0)  # 清空进度条
        # 判断是否设置了结果文件夹
        if not self.resultDir:
            QMessageBox.warning(self, '提示', '未选择结果保存文件夹！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 判断设置的结果文件夹是否仍然存在
        if not os.path.exists(self.resultDir):
            QMessageBox.warning(self, '提示', '结果文件夹已不存在（被误删）！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 基础结果文件
        basicResultFiles = self.basiceRsultFrame.getCheckedResults()
        self.basicCnt = len(basicResultFiles)
        # 判断是否选中基础结果
        if not basicResultFiles:
            QMessageBox.warning(self, '提示', '未选中基础结果文件！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # 其他结果文件
        otherResultFiles = self.otherRresultFrame.getCheckedResults()
        # 获取合并类型
        if self.allMergeCheckBox.isChecked():
            mergeType = MERGE_TYPE['ALL']
        elif self.randomMergeCheckBox.isChecked():
            mergeType = MERGE_TYPE['RANDOM']
        else:
            mergeType = MERGE_TYPE['BASIC']
        randomMergeCnt = self.randomMergeCntSpin.value()  # 随机合并次数
        otherCnt = self.otherCntSpin.value()  # 其他结果文件组合个数
        # 判断是否选择其他结果
        if mergeType in [MERGE_TYPE['ALL'], MERGE_TYPE['RANDOM']]:
            if not otherResultFiles:
                QMessageBox.warning(self, '提示', '未选中其他结果文件！', QMessageBox.Yes, QMessageBox.Yes)
                return
            # 组合个数大于选中的其他文件总数
            if otherCnt > len(otherResultFiles):
                QMessageBox.warning(self, '提示', '组合个数大于选中的其他文件总数！', QMessageBox.Yes, QMessageBox.Yes)
                return
        faultLeft = self.faultLeftSpin.value()  # 容错左边界
        faultRight = self.faultRightSpin.value()  # 容错右边界
        # 容错范围正确性检验
        if faultLeft > faultRight:
            QMessageBox.warning(self, '提示', '容错范围错误，左边界大于右边界！', QMessageBox.Yes, QMessageBox.Yes)
            return
        # if faultRight > len(basicResultFiles) and mergeType == MERGE_TYPE['BASIC'] \
        #         or faultRight > otherCnt + 1 and mergeType in [MERGE_TYPE['ALL'], MERGE_TYPE['RANDOM']]:
        #     QMessageBox.warning(self, '提示', '容错范围右边界过大！', QMessageBox.Yes, QMessageBox.Yes)
        #     return
        processCnt = self.processSpin.value()
        self.mergeResultBtn.setDisabled(True)
        self.startBtn.setDisabled(True)
        self.mergeProgressBar.setValue(1)
        self.basiceRsultFrame.setFinishedText(0, self.basicCnt)
        self.mergeThread = MergeThread(basicResultFiles, otherResultFiles, self.resultDir,
                                       [faultLeft, faultRight], processCnt, mergeType,
                                       otherCnt, randomMergeCnt)
        self.mergeThread.progress.connect(self.onMergeProgressChanged)
        self.mergeThread.finishedCnt.connect(self.onMergeFinishedCntChanged)
        self.mergeThread.start()

    def onStopMerge(self):
        """
        结束按钮点击函数
        """
        # 未开启子线程
        if self.mergeThread is None:
            return
        # 未开启进程池
        if self.mergeThread.pool is None:
            return
        self.mergeThread.pool.terminate()  # 终止进程
        self.mergeThread.terminate()  # 终止线程
        self.mergeProgressBar.setValue(0)  # 进度条清空
        # 启用开始按钮、合并按钮
        self.mergeResultBtn.setDisabled(False)
        self.startBtn.setDisabled(False)
        # 清空完成计数
        self.basiceRsultFrame.setFinishedText(0, 0)
        QMessageBox.information(self, '提示', '合并已终止！！！', QMessageBox.Yes, QMessageBox.Yes)

    def onMergeProgressChanged(self, status):
        """
        结果合并进度条值发生改变
        """
        self.mergeProgressBar.setValue(status)

    def onMergeFinishedCntChanged(self, status):
        """
        结果合并完成个数
        :param status:
        :return:
        """
        # 记录完成的个数
        self.basiceRsultFrame.setFinishedText(status, self.basicCnt)
        if status == self.basicCnt:
            # 启用开始按钮、合并按钮
            self.mergeResultBtn.setDisabled(False)
            self.startBtn.setDisabled(False)
            QMessageBox.information(self, '提示', '结果合并完毕！', QMessageBox.Yes, QMessageBox.Yes)

    # def exportResult(self):
    #     """
    #   导出结果
    #   """
    #     # 判断有无可导出的结果
    #     if not self.finalResult:
    #         QMessageBox.warning(self, '提示', '未合并可导出的结果！', QMessageBox.Yes, QMessageBox.Yes)
    #         return
    #     # 判断是否设置了导出的文件夹
    #     if not self.resultDir:
    #         QMessageBox.warning(self, '提示', '未设置结果文件夹！', QMessageBox.Yes, QMessageBox.Yes)
    #         return
    #
    #     # 保存合并结果文件名
    #     resultFilename = '合并结果-{}.txt'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
    #     # 结果文件保存路径
    #     resultSavePath = os.path.join(self.resultDir, resultFilename)
    #     # 将结果写入文件
    #     resultToFile(self.finalResult, resultSavePath)
    #
    #     QMessageBox.information(self, '提示', '结果导出成功！\n已保存在文件{}中'.format(resultSavePath), QMessageBox.Yes,
    #                             QMessageBox.Yes)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)  # 创建应用程序
    gui = MainUi()  # 新建窗口
    gui.show()  # 显示窗口
    sys.exit(app.exec_())  # 调用系统方法保证程序能够退出
