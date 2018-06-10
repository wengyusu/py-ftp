from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QGridLayout, QLabel, QAbstractItemView, QMainWindow, QAction, qApp ,QTextEdit, QVBoxLayout, QWidget, QTableWidget,QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *   
import about_msg_box
import setting_window
import user_window
import main
import json
import sys
import asyncio
import os
import logging
import server


# class WorkThread(QThread):
    
#     def __init__(self, parent = None):  
#         super(WorkThread, self).__init__(parent)
#     trigger = pyqtSignal()
#     def run(self):
#         try:
#             print("starting...")
#             with open("setting.json", 'r') as f:
#                 config = json.load(f)
#                 port = config['Port']
#                 print(port)
#             # self.ftpserver = main.FTP()
#             global ftpserver
#             ftpserver = FTPServer(port = port)
#             self.trigger.emit()
#             ftpserver.start()
#         except Exception as e:
#             print(e)

class EmittingStream(QObject):  
        textWritten = pyqtSignal(str)  
        def write(self, text):  
            self.textWritten.emit(str(text))
            
class ServerMainWindow(QMainWindow):

    menubar = None
    toolbar = None
    statusbar = None

    fileMenu = None
    editMenu = None
    aboutMenu = None

    startAct = None
    stopAct = None
    quitAct = None
    settingAct = None
    userAct = None
    aboutAct = None

    msgWidget = None
    connectList = None
    flowWidget = None

    mainLayout = None
    bottomLayout = None

    centralWidget = None
    bottomWidget =None

    startMessage = None
    stopMessage = None
    setMessage = None
    userMessage = None
    aboutMessage = None

    def __init__(self):
        # self.ftpserver = None
        super(ServerMainWindow, self).__init__()
        self.server = None
        self.thread = QThread()
        # self.thread.trigger.connect(self.on_start)
        self.thread.start()
        self.initUI()
        self.uploadflow = 0
        self.downloadflow = 0
        sys.stdout = EmittingStream(textWritten=self.msgAppendText)

    def initUI(self):
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('PyFTP Server')

        self.statusBar().showMessage('Ready')

        self.initWidgets()
        self.initAction()
        self.initMenu()
        self.initToolBar()

        self.initCentralWidget()

        self.show()
    def initWidgets(self):
        self.setMessage = setting_window.SettingWindow()
        self.userMessage = user_window.UserWindow()

    def initAction(self):
        self.startAct = QAction(QIcon('resource/start.png'), 'Start server', self)
        self.startAct.setStatusTip('Starts PyFTP Server')
        self.startAct.triggered.connect(self.startTriggered)
        self.startAct.setEnabled(True)

        self.stopAct = QAction(QIcon('resource/stop.png'), 'Stop server', self)
        self.stopAct.setStatusTip('Stops the server')
        self.stopAct.triggered.connect(self.stopTriggered)
        self.stopAct.setEnabled(False)

        self.quitAct = QAction(QIcon('resource/quit.png'), 'Quit', self)
        self.quitAct.setStatusTip('Quits FTP Server')
        self.quitAct.triggered.connect(qApp.quit)

        self.settingAct = QAction(QIcon('resource/set.png'), 'Settings', self)
        self.settingAct.setStatusTip('Displays the options dialog')
        self.settingAct.triggered.connect(self.setTriggered)

        self.userAct = QAction(QIcon('resource/user.png'), 'Users', self)
        self.userAct.setStatusTip('Opens the users dialog')
        self.userAct.triggered.connect(self.userTriggered)

        self.aboutAct = QAction(QIcon('resource/about.png'), 'About PyFTP Server', self)
        self.aboutAct.setStatusTip('Displays the about dialog with useful information about PyFTP Server')
        self.aboutAct.triggered.connect(self.aboutTriggered)

    def initMenu(self):
        self.menubar = self.menuBar()

        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(self.startAct)
        self.fileMenu.addAction(self.stopAct)
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menubar.addMenu('Edit')
        self.editMenu.addAction(self.settingAct)
        self.editMenu.addAction(self.userAct)

        self.aboutMenu = self.menubar.addMenu('About')
        self.aboutMenu.addAction(self.aboutAct)

    def initToolBar(self):
        self.toolbar = self.addToolBar('ToolBar')

        self.toolbar.addAction(self.startAct)
        self.toolbar.addAction(self.stopAct)
        self.toolbar.addAction(self.settingAct)
        self.toolbar.addAction(self.userAct)
        self.toolbar.addAction(self.aboutAct)

    def initCentralWidget(self):
        self.msgWidget = QTextEdit()
        self.msgWidget.setReadOnly(True)
        self.msgWidget.append('PyFTP Server 0.1 beta')
        self.msgWidget.append('Test by wzc')

        self.connectList = QTableWidget()
        self.connectList.setColumnCount(2)
        self.connectList.setRowCount(0)
        self.connectList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.connectList.setHorizontalHeaderLabels(('Account', 'IP'))
        self.connectList.verticalHeader().setHidden(True)
        self.connectList.setShowGrid(False)

        self.flowWidget = FlowWidget()

        self.bottomWidget = QWidget()

        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addWidget(self.connectList)
        self.bottomLayout.addWidget(self.flowWidget)
        self.bottomWidget.setLayout(self.bottomLayout)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.msgWidget)
        self.mainLayout.addWidget(self.bottomWidget)
        self.centralWidget.setLayout(self.mainLayout)

    def startTriggered(self):

        self.startAct.setEnabled(False)
        self.stopAct.setEnabled(True)

        # print("starting....")
        if self.server is None:
            whitelist = []
            blacklist = []
            with open("setting.json", 'r') as f:
                config = json.load(f)
                port = config['Port']
                username_info = config['Users']
                whitelist = config['IPAllowed']
                blacklist = config['IPBanned']
                maxcon = config['MaxConnectionCount']

            self.server = server.FTPServer(port=port,whitelist=whitelist,blacklist=blacklist,username_info = username_info,timeout=60.0,maxcon=maxcon)
            self.server.moveToThread(self.thread)
            self.server.begin.connect(self.server.start)
            self.server.onconnect.connect(self.addConnectionItem)
            self.server.upload.connect(self.updateUploadFlow)
            self.server.download.connect(self.updateDownloadFlow)
            self.server.disconnect.connect(self.removeConnectionItem)
            self.server.stop.connect(self.removeAllConnectionItem)
            self.server.begin.emit()
            self.msgWidget.append("Start successfully.")

        # 槽函数
        # 判断是否启动成功。若启动成功，显示成功信息，否则显示失败信息
        # 信息添加到self.msgWidget中，self.msgWidget是一个QTextEdit
        # self.msgWidget.append(需要添加的文本))

    def on_start(self):
        ftpserver.addr = EmittingStream(textWritten=self.msgAppendText)
        print("onstart")
        

    def stopTriggered(self):
        self.startAct.setEnabled(True)
        self.stopAct.setEnabled(False)
        print("stopping....")
        try:
            if self.server is not None:
                self.server.stop.connect(self.server.close)
                self.server.stop.emit()
                self.msgWidget.append("Close successfully.")
                self.server = None
        except Exception as e:
            self.msgWidget.append(e)

        # 槽函数
        # 判断是否停止成功。若停止成功，显示成功信息，否则显示失败信息
        # 信息添加到self.msgWidget中，self.msgWidget是一个QTextEdit
        # self.msgWidget.append(需要添加的文本))

        

    def setTriggered(self):
        self.setMessage.exec()

    def userTriggered(self):
        self.userMessage.exec()

    def aboutTriggered(self):
        self.aboutMessage = about_msg_box.AboutMessage()
        self.aboutMessage.exec()

    def msgAppendText(self,text):
        self.msgWidget.append(text)
        # 用于向self.msgWidget添加其它文本，具体怎么实现我不是很清楚，
        # 你可以不用这个函数，根据你的需要实现一个或多个
        # self.msgWidget.append(需要添加的文本)


    def addConnectionItem(self,name,addr):
        item1 = QTableWidgetItem(name)
        item2 = QTableWidgetItem(addr)
        self.connectList.setRowCount(self.connectList.rowCount() + 1)
        self.connectList.setItem(self.connectList.rowCount() - 1, 0, item1)
        self.connectList.setItem(self.connectList.rowCount() - 1, 1, item2)
        # 用于向self.connectList添加连接信息，包括用户名和远程主机IP
        # self.connectList是一个QTableWidget，我记得每条连接信息貌似需要由两个QTableWidgetItem组成，
        # 一个单元格是一个item，我将connectList设为不可编辑，也就是双击item不能更改条目内容，
        # 初始化时connectList的行数为0，在添加一条信息前，需要将它的行数加1
        # self.connectList.setRowCount(self.connectList.rowCount() + 1)


    def removeConnectionItem(self, username, ip):
        for index in range(self.connectList.rowCount()):
            if self.connectList.item(index, 0).text() == username:
                if self.connectList.item(index, 1).text() == ip:
                    self.connectList.removeRow(index)

    def removeAllConnectionItem(self):
        for index in range(self.connectList.rowCount()):
            self.connectList.removeRow(index)

    def updateUploadFlow(self, size):
        self.uploadflow = self.uploadflow + int(size)
        self.flowWidget.label22.setText(str(self.uploadflow))
        # 用于更新上传及下载流量，我觉得这两个可以一起定时更新，所以用一个函数应该没问题
        # 更新下载流量的方法是，self.flowWidget.label12.setText(需要添加的文本)
        # 更新上传流量的方法是，self.flowWidget.label22.setText(需要添加的文本)
        # 单位是bytes

    def updateDownloadFlow(self, size):
        self.downloadflow = self.downloadflow +int(size)
        self.flowWidget.label12.setText(str(self.downloadflow))


class FlowWidget(QWidget):

    layout = None
    label11 = None
    label12 = None
    label13 = None
    label21 = None
    label22 = None
    label23 = None

    def __init__(self):
        super(FlowWidget, self).__init__()
        self.initLabels()
        self.initLayout()


    def initLabels(self):
        self.label11 = QLabel('Received Data:')
        self.label12 = QLabel('0')
        self.label13 = QLabel('bytes')
        self.label21 = QLabel('Sent Data:')
        self.label22 = QLabel('0')
        self.label23 = QLabel('bytes')

    def initLayout(self):
        layout = QGridLayout()
        layout.addWidget(self.label11, 0, 0)
        layout.addWidget(self.label12, 0, 1)
        layout.addWidget(self.label13, 0, 2)
        layout.addWidget(self.label21, 1, 0)
        layout.addWidget(self.label22, 1, 1)
        layout.addWidget(self.label23, 1, 2)

        layout.setColumnMinimumWidth(0, 120)
        layout.setColumnMinimumWidth(1, 30)
        layout.setColumnMinimumWidth(2, 30)

        self.setLayout(layout)