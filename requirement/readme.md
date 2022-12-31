# 数字组合软件

## 开发环境
python 3.7.4

## python库

- 多进程库：multiprocessing (python内置库)
- UI界面库：PyQt5    `pip install PyQt5`

## 程序文件介绍
- app.py：主应用程序文件，用于构建UI，以及相关事件
- utils.py：工具文件，定义用于计算组合、解析文件、存储数据的方法
- workThread.py：工作线程，根据文件计算组合数
- constant.py: 常量文件，定义程序中使用的常量

## 程序运行
pycharm 中运行 app.py 文件 或者 cmd窗口中执行`python app.py`

## 程序打包成exe
依赖于 pyinstaller 包
```
//打包命令
pyinstaller -w -F app.py
```
