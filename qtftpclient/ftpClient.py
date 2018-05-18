from PyQt5.QtWidgets import QPushButton, QApplication, QMainWindow, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, \
    QVBoxLayout, QWidget, QTreeView, QTreeWidget, QSplitter, QTextEdit, QTreeWidgetItem, QDialog, QListWidget, \
    QListWidgetItem, QMessageBox, QCheckBox, QMenu
from PyQt5.QtGui import QIntValidator,QCursor
from ChangedQDirModel import *
from MyDelegate import *
from myFtp import myFtp
import sys, os, time, json, socket, ftplib


class client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.localPath = '/'
        self.serverPath= '/'
        self.linkData = []
        self.logText='日志\nwelcome\n'
        self.connectionNow={'hostname':'','username':'','passwd':'','port':21}
        self.FTP=None
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1100, 600)
        self.setMinimumWidth(650)
        self.setWindowTitle('ftpClient')
        self.initMenuBar()
        self.initCenterWidget()
        self.show()

    def initMenuBar(self):
        linkManage = QAction('管理连接(&L)', self)
        linkManage.setShortcut('Ctrl+M')
        linkManage.setStatusTip('管理所有连接')
        linkManage.triggered.connect(self.startLinkManageDialog)

        exitAct = QAction('退出(&E)', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('退出程序')
        exitAct.triggered.connect(qApp.quit)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('文件(&F)')
        fileMenu.addAction(linkManage)
        fileMenu.addAction(exitAct)

    def initCenterWidget(self):
        centerWidget = QWidget()

        self.centerBox = QVBoxLayout()
        self.centerBox.setAlignment(Qt.AlignTop)
        self.initQuickLink()

        localWidget = QWidget()
        serverWidget = QWidget()

        localWidgetLayout = QVBoxLayout()
        serverWidgetLayout = QVBoxLayout()

        localLabelLayout = QHBoxLayout()
        serverLabelLayout = QHBoxLayout()

        self.localPathLineEdit = QLineEdit()
        self.serverPathLineEdit = QLineEdit()

        self.localPathLineEdit.setFocusPolicy(Qt.NoFocus)
        self.serverPathLineEdit.setFocusPolicy(Qt.NoFocus)

        self.initLocalFileBox()
        self.initServerFileBox()

        localLabelLayout.addWidget(QLabel('本地文件:'))
        localLabelLayout.addWidget(self.localPathLineEdit)

        serverLabelLayout.addWidget(QLabel('服务器文件:'))
        serverLabelLayout.addWidget(self.serverPathLineEdit)

        localWidgetLayout.addLayout(localLabelLayout)
        localWidgetLayout.addWidget(self.localFileTreeView)
        localWidgetLayout.setContentsMargins(0, 0, 0, 0)

        serverWidgetLayout.addLayout(serverLabelLayout)
        serverWidgetLayout.addWidget(self.serverFileTree)
        serverWidgetLayout.setContentsMargins(0, 0, 0, 0)

        localWidget.setLayout(localWidgetLayout)
        localWidget.setContentsMargins(0, 0, 0, 0)
        serverWidget.setLayout(serverWidgetLayout)
        serverWidget.setContentsMargins(0, 0, 0, 0)

        self.logTextWindow = QTextEdit()

        self.logTextWindow.setText(self.logText)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter2 = QSplitter(Qt.Vertical)
        splitter3 = QSplitter(Qt.Vertical)
        splitter4 = QSplitter(Qt.Vertical)

        splitter2.addWidget(localWidget)
        splitter2.addWidget(self.localFileTreeWidget)
        splitter3.addWidget(serverWidget)
        splitter3.addWidget(self.serverFileTable)
        splitter1.addWidget(splitter2)
        splitter1.addWidget(splitter3)
        splitter4.addWidget(splitter1)
        splitter4.addWidget(self.logTextWindow)

        self.centerBox.addWidget(splitter4)

        centerWidget.setLayout(self.centerBox)
        self.setCentralWidget(centerWidget)

    def initQuickLink(self):
        self.hostInput = QLineEdit(self)
        self.userNameInput = QLineEdit(self)
        self.passwdInput = QLineEdit(self)
        self.portInput = QLineEdit('21', self)
        self.quickLoginButton = QPushButton('快速连接', self)
        self.anonymousLoginCheckBox = QCheckBox('匿名连接')

        self.passwdInput.setEchoMode(QLineEdit.Password)
        self.portInput.setValidator(QIntValidator(0, 65535))
        self.portInput.setMaximumWidth(40)

        quickLinkBox = QHBoxLayout()
        quickLinkBox.addWidget(QLabel('  主机:', self))
        quickLinkBox.addWidget(self.hostInput)
        quickLinkBox.addWidget(QLabel(' 用户名:', self))
        quickLinkBox.addWidget(self.userNameInput)
        quickLinkBox.addWidget(QLabel(' 密码:', self))
        quickLinkBox.addWidget(self.passwdInput)
        quickLinkBox.addWidget(QLabel(' 端口:', self))
        quickLinkBox.addWidget(self.portInput)
        quickLinkBox.addWidget(self.quickLoginButton)
        quickLinkBox.addWidget(self.anonymousLoginCheckBox)
        quickLinkBox.addStretch(1)
        self.centerBox.addLayout(quickLinkBox)

        self.quickLoginButton.clicked.connect(self.connectFromQuickLink)
        self.anonymousLoginCheckBox.stateChanged.connect(self.quickLinkCheckBoxChanged)

    def initLocalFileBox(self):
        self.localFileTreeView = QTreeView()
        self.localFileTreeWidget = QTreeWidget()

        self.localDirModel = ChangedQDirModel()
        self.localFileTreeView.setModel(self.localDirModel)
        self.localFileTreeView.setColumnWidth(0,240)
        self.localFileTreeView.setColumnWidth(2,60)

        self.localFileTreeView.clicked.connect(self.localTreeClicked)

        self.localFileTreeWidget.setColumnCount(4)
        self.localFileTreeWidget.setHeaderLabels(['文件名', '文件大小', '文件类型', '修改时间'])
        self.localFileTreeWidget.setColumnWidth(0,240)
        self.localFileTreeWidget.setColumnWidth(2,60)
        self.localFileTreeWidget.setItemDelegate(MyDelegate())

        self.localFileTable = []

        self.localFileRefesh()

        self.localFileTreeWidget.doubleClicked.connect(self.localTableDoubleClicked)
        self.localFileTreeWidget.itemPressed.connect(self.localTableRightClicked)

    def initServerFileBox(self):
        self.serverFileTree = QTreeWidget()
        self.serverFileTable = QTreeWidget()

        self.serverFileTree.setHeaderLabels(['目录结构'])

        self.serverFileTable.setColumnCount(5)
        self.serverFileTable.setHeaderLabels(['文件名', '文件类型', '文件大小', '权限', '修改时间'])
        self.serverFileTable.setColumnWidth(0,240)
        self.serverFileTable.setColumnWidth(1,60)
        self.serverFileTable.setColumnWidth(2,60)
        self.serverFileTable.setColumnWidth(3,70)
        self.serverFileTable.setItemDelegate(MyDelegate())

        self.serverFileTable.doubleClicked.connect(self.serverTableDoubleClicked)
        self.serverFileTable.itemPressed.connect(self.serverTableRightClicked)

    def connectFromQuickLink(self):
        hostName = self.hostInput.text()
        userName = self.userNameInput.text()
        passwd = self.passwdInput.text()
        port = int(self.portInput.text())
        with open('linkdata.json','r') as f:
            self.linkData=json.load(f)
        data={'hostname':hostName,'username':userName,'passwd':passwd,'port':port,'remark':'来自快速连接'}
        self.linkData[userName+'@'+hostName+':'+str(port)+' '+'来自快速连接']=data
        with open('linkdata.json','w') as f:
            json.dump(self.linkData,f)

        try:
            self.aNewConnection(hostName, userName, passwd, port)
        except socket.gaierror:
            QMessageBox.information(self,'主机名错误','主机名错误，请输入正确的主机名',QMessageBox.Ok,QMessageBox.Ok)
            return
        except ConnectionRefusedError:
            QMessageBox.information(self, '连接出错', '连接失败，请检查是否输入了正确的主机名或端口', QMessageBox.Ok, QMessageBox.Ok)
            return
        except ftplib.error_perm:
            QMessageBox.information(self, '登陆出错', '登陆失败，请检查是否输入了正确的用户名或密码', QMessageBox.Ok, QMessageBox.Ok)
            return

    def localFileRefesh(self):
        self.localFileTable.clear()
        self.localFileTreeWidget.clear()

        if self.localPath!='/':
            node = QTreeWidgetItem(self.localFileTreeWidget)
            node.setText(0, '..')
            self.localFileTable.append(node)

        for i in os.listdir(self.localPath):
            node = QTreeWidgetItem(self.localFileTreeWidget)
            node.setText(0, i)
            tempPath = os.path.join(self.localPath, i)
            if os.path.isfile(tempPath):
                node.setText(1, str(os.path.getsize(tempPath)))
                node.setText(2, 'File')
            elif os.path.isdir(tempPath):
                node.setText(1, '')
                node.setText(2, 'Folder')
            elif os.path.islink(tempPath):
                node.setText(1, '')
                node.setText(2, 'Shortcut')
            elif os.path.ismount(tempPath):
                node.setText(1, '')
                node.setText(2, 'Mount')
            try:
                node.setText(3, TimeStampToTime(os.path.getmtime(tempPath)))
            except FileNotFoundError:
                pass
            except PermissionError:
                pass
            self.localFileTable.append(node)

        self.localPathLineEdit.setText(self.localPath)

        for i in self.localFileTable:
            self.localFileTreeWidget.addTopLevelItem(i)

    def serverFileRefresh(self):
        try:
            fileinfo = self.FTP.getdirinfo(self.serverPath)
        except ftplib.error_temp:
            self.reconnect()
            fileinfo = self.FTP.getdirinfo(self.serverPath)

        for i in fileinfo:
            node = QTreeWidgetItem(self.serverFileTable)
            node.setText(0, i[0])
            node.setText(1, i[1])
            node.setText(2, i[2])
            node.setText(3, i[3])
            node.setText(4, i[4])
            self.serverFileInfo.append(node)

        self.serverPathLineEdit.setText(self.serverPath)

        for i in self.serverFileInfo:
            self.serverFileTable.addTopLevelItem(i)

    def serverTableDoubleClicked(self,index):
        if qApp.mouseButtons()==Qt.RightButton:
            return

        if self.serverFileInfo[index.row()].text(1)=='File':
            return

        if index.row()==0:
            if self.serverPath=='/':
                self.localPath=self.serverPath+self.serverFileInfo[0].text(0)
            else:
                tempPath=self.serverPath.split('/')[:-1]
                self.serverPath=''
                for i in tempPath:
                    self.serverPath=self.serverPath+'/'+i
                if self.serverPath!='/':
                    self.serverPath=self.serverPath[1:]
        else:
            self.serverPath=os.path.join(self.serverPath,self.serverFileInfo[index.row()].text(0))

        self.serverFileTable.clear()
        self.serverFileInfo.clear()

        if self.serverPath!='/':
            node = QTreeWidgetItem(self.serverFileTable)
            node.setText(0,'..')
            self.serverFileInfo.append(node)

        self.serverFileRefresh()

    def serverTableRightClicked(self,item,int_p):
        if item.text(0)=='..':
            return
        if qApp.mouseButtons()==Qt.RightButton:
            localMenu=QMenu()
            downLoadFile=QAction('download')
            localMenu.addAction(downLoadFile)

            downLoadFile.triggered.connect(self.downloadFile)
            localMenu.exec_(QCursor.pos())

    def downloadFile(self):
        filename=self.serverFileTable.selectedItems()[0].text(0)
        if ' ' in filename:
            localName=filename.replace(' ','_')
        else:
            localName=filename
        pid = os.fork()
        if pid == 0:
            with open(self.localPath +'/' + localName, 'wb') as fp:
                self.FTP.retrbinary('RETR ' + self.serverPath + '/' + filename, fp.write, 1024)
                self.FTP.set_debuglevel(0)
                os._exit(0)
        else:
            pass

    def localTreeClicked(self, index):
        if self.localDirModel.fileInfo(index).isDir():
            self.localPath = self.localDirModel.filePath(index)
        else:
            self.localPath = self.localDirModel.filePath(index)
            tempPath = self.localPath.split('/')[:-1]
            self.localPath = ''
            for i in tempPath:
                self.localPath = self.localPath + '/' + i
            if self.localPath != '/':
                self.localPath = self.localPath[1:]

        self.localFileRefesh()

    def localTableDoubleClicked(self, index):
        if qApp.mouseButtons()==Qt.RightButton:
            return

        if os.path.isdir(os.path.join(self.localPath, self.localFileTable[index.row()].text(0))) == False:
            return

        if index.row() == 0:
            if self.localPath=='/':
                self.localPath = self.localPath + self.localFileTable[0].text(0)
            else:
                tempPath = self.localPath.split('/')[:-1]
                self.localPath = ''
                for i in tempPath:
                    self.localPath = self.localPath + '/' + i
                if self.localPath!='/':
                    self.localPath=self.localPath[1:]
        else:
            self.localPath = os.path.join(self.localPath, self.localFileTable[index.row()].text(0))

        self.localFileRefesh()

    def localTableRightClicked(self,item,int_p):
        if item.text(0)=='..':
            return
        if qApp.mouseButtons()==Qt.RightButton:
            localMenu=QMenu()
            upLoadFile=QAction('upload')
            localMenu.addAction(upLoadFile)

            upLoadFile.triggered.connect(self.uploadFile)
            localMenu.exec_(QCursor.pos())

    def uploadFile(self):
        filename = self.localFileTreeWidget.selectedItems()[0].text(0)
        pid = os.fork()
        if pid == 0:
            with open(self.localPath + '/' + filename, 'rb') as fp:
                self.FTP.storbinary('STOR ' + self.serverPath + '/' + filename, fp, 1024)
                self.FTP.set_debuglevel(0)
                os._exit(0)
        else:
            pass

    def startLinkManageDialog(self):
        with open('linkdata.json','r') as f:
            self.linkData=json.load(f)
        self.linkManageDialog = QDialog()
        self.linkManageDialog.setModal(True)
        linkManageLayout = QVBoxLayout()
        self.linkManageDialog.setLayout(linkManageLayout)
        self.linkManageDialog.setWindowTitle('连接管理')

        linkDisplayLayout = QHBoxLayout()
        bottomButtomGroupLayout = QHBoxLayout()

        connectButtom = QPushButton('连接')
        confirmButtom = QPushButton('确定')
        cancleButtom = QPushButton('取消')


        bottomButtomGroupLayout.addStretch(1)
        bottomButtomGroupLayout.addWidget(connectButtom)
        bottomButtomGroupLayout.addWidget(confirmButtom)
        bottomButtomGroupLayout.addWidget(cancleButtom)

        linkManageLayout.addLayout(linkDisplayLayout)
        linkManageLayout.addLayout(bottomButtomGroupLayout)

        linkListLayout = QVBoxLayout()
        linkEditLayout = QVBoxLayout()

        linkDisplayLayout.addLayout(linkListLayout)
        linkDisplayLayout.addLayout(linkEditLayout)

        self.linkList = QListWidget()
        addLinkButton = QPushButton('新建')
        removeLinkButton = QPushButton('删除')
        linkManageButtonGroupLayout = QHBoxLayout()
        linkManageButtonGroupLayout.addWidget(addLinkButton)
        linkManageButtonGroupLayout.addWidget(removeLinkButton)

        linkListLayout.addWidget(QLabel('连接列表：'), 0, Qt.AlignTop)
        linkListLayout.addWidget(self.linkList)
        linkListLayout.addLayout(linkManageButtonGroupLayout)

        hBox1 = QHBoxLayout()
        hBox2 = QHBoxLayout()
        hBox3 = QHBoxLayout()
        hBox4 = QHBoxLayout()
        hBox5 = QHBoxLayout()
        hBox6=QHBoxLayout()

        self.host = QLineEdit()
        self.userName = QLineEdit()
        self.passwd = QLineEdit()
        self.port = QLineEdit()
        self.remark=QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        self.port.setValidator(QIntValidator(0,65535))
        self.anonymousLogin = QCheckBox('匿名登录')
        confirmEdit=QPushButton('确定修改')
        confirmEdit.setFixedWidth(80)

        self.anonymousLogin.stateChanged.connect(self.linkManageCheckBoxChanged)

        hBox1.addWidget(QLabel('主机：   '))
        hBox1.addWidget(self.host)
        hBox2.addWidget(QLabel('用户名：'))
        hBox2.addWidget(self.userName)
        hBox3.addWidget(QLabel('密码：   '))
        hBox3.addWidget(self.passwd)
        hBox4.addWidget(QLabel('端口：   '))
        hBox4.addWidget(self.port)
        hBox6.addWidget(QLabel('备注：   '))
        hBox6.addWidget(self.remark)
        hBox5.addWidget(self.anonymousLogin)
        hBox5.addWidget(confirmEdit,Qt.AlignRight)

        linkEditLayout.addLayout(hBox1)
        linkEditLayout.addLayout(hBox2)
        linkEditLayout.addLayout(hBox3)
        linkEditLayout.addLayout(hBox4)
        linkEditLayout.addLayout(hBox6)
        linkEditLayout.addLayout(hBox5)

        for key in self.linkData:
            item = QListWidgetItem(self.linkList)
            item.setText(key)

        self.linkList.setCurrentRow(0)
        if len(self.linkData)!=0:
            tempdata=self.linkData[self.linkList.currentItem().text()]

            self.host.setText(tempdata['hostname'])
            self.port.setText(str(tempdata['port']))
            self.remark.setText(tempdata['remark'])
            if tempdata['username']=='anonymous':
                self.anonymousLogin.setCheckState(Qt.Checked)
            else:
                self.userName.setText(tempdata['username'])
                self.passwd.setText(tempdata['passwd'])

        cancleButtom.clicked.connect(self.linkManageDialog.close)
        self.linkList.itemClicked.connect(self.listItemClicked)
        addLinkButton.clicked.connect(self.addNewLink)
        confirmEdit.clicked.connect(self.confirmEditLink)
        confirmButtom.clicked.connect(self.saveData)
        removeLinkButton.clicked.connect(self.removeLink)
        connectButtom.clicked.connect(self.connectFromDialog)

        self.linkManageDialog.show()

    def connectFromDialog(self):
        hostName = self.host.text()
        userName = self.userName.text()
        passwd = self.passwd.text()
        port = int(self.port.text())

        try:
            self.aNewConnection(hostName, userName, passwd, port)
        except socket.gaierror:
            QMessageBox.information(self,'主机名错误','主机名错误，请输入正确的主机名',QMessageBox.Ok,QMessageBox.Ok)
            return
        except ConnectionRefusedError:
            QMessageBox.information(self, '连接出错', '连接失败，请检查是否输入了正确的主机名或端口', QMessageBox.Ok, QMessageBox.Ok)
            return
        except ftplib.error_perm:
            QMessageBox.information(self, '登陆出错', '登陆失败，请检查是否输入了正确的用户名或密码', QMessageBox.Ok, QMessageBox.Ok)
            return
        self.saveData()

    def removeLink(self):
        if len(self.linkData)==0:
            return

        rowNow=self.linkList.currentRow()
        itemNow=self.linkList.currentItem()

        self.linkData.pop(itemNow.text())
        self.linkList.removeItemWidget(itemNow)

        self.linkList.clear()

        for key in self.linkData:
            item = QListWidgetItem(self.linkList)
            item.setText(key)

        if len(self.linkData)==0:
            self.host.setText('')
            self.port.setText('')
            self.anonymousLogin.setCheckState(Qt.Unchecked)
            self.userName.setText('')
            self.passwd.setText('')
            self.remark.setText('')
            return
        elif len(self.linkData)<rowNow+1:
            rowNow=len(self.linkData)-1
            self.linkList.setCurrentRow(len(self.linkData)-1)
        else:
            self.linkList.setCurrentRow(rowNow)

        self.listItemClicked(self.linkList.currentItem())

    def saveData(self):
        self.confirmEditLink()
        with open('linkdata.json','w') as f:
            json.dump(self.linkData,f)
        self.linkManageDialog.close()

    def confirmEditLink(self):
        hostName = self.host.text()
        userName = self.userName.text()
        passwd = self.passwd.text()
        port = int(self.port.text())
        remark=self.remark.text()

        data = {'hostname': hostName, 'username': userName, 'passwd': passwd, 'port': port, "remark":remark}

        self.linkData.pop(self.linkList.currentItem().text())
        self.linkData[userName + '@' + hostName + ':' + str(port) +' '+remark] = data

        self.linkList.clear()

        for key in self.linkData:
            item = QListWidgetItem(self.linkList)
            item.setText(key)

        self.linkList.setCurrentRow(len(self.linkList)-1)

    def addNewLink(self):
        if '新连接' in self.linkData:
            return
        self.linkData['新连接']={'hostname':'','username':'','passwd':'','port':'','remark':''}
        item = QListWidgetItem(self.linkList)
        item.setText('新连接')
        self.linkList.setCurrentRow(len(self.linkList) - 1)

        self.host.setText('')
        self.port.setText('21')
        self.anonymousLogin.setCheckState(Qt.Unchecked)
        self.userName.setText('')
        self.passwd.setText('')
        self.remark.setText('')

    def listItemClicked(self,item):
        tempdata = self.linkData[item.text()]

        self.host.setText(tempdata['hostname'])
        self.port.setText(str(tempdata['port']))
        self.remark.setText(tempdata['remark'])
        if tempdata['username'] == 'anonymous':
            self.anonymousLogin.setCheckState(Qt.Checked)
        else:
            self.anonymousLogin.setCheckState(Qt.Unchecked)
            self.userName.setText(tempdata['username'])
            self.passwd.setText(tempdata['passwd'])

    def quickLinkCheckBoxChanged(self):
        if self.anonymousLoginCheckBox.checkState() == Qt.Checked:
            self.userNameInput.setText('anonymous')
            self.passwdInput.setText('')
            self.userNameInput.setEnabled(False)
            self.passwdInput.setEnabled(False)
        elif self.anonymousLoginCheckBox.checkState() == Qt.Unchecked:
            self.userNameInput.setText('')
            self.passwdInput.setText('')
            self.userNameInput.setEnabled(True)
            self.passwdInput.setEnabled(True)

    def linkManageCheckBoxChanged(self):
        if self.anonymousLogin.checkState() == Qt.Checked:
            self.userName.setText('anonymous')
            self.passwd.setText('')
            self.userName.setEnabled(False)
            self.passwd.setEnabled(False)
        elif self.anonymousLogin.checkState() == Qt.Unchecked:
            self.userName.setText('')
            self.passwd.setText('')
            self.userName.setEnabled(True)
            self.passwd.setEnabled(True)

    def log(self,message):
        self.logText=self.logText+message
        self.logTextWindow.setText(self.logText)

    def aNewConnection(self,host,username,passwd,port):
        if self.FTP!=None:
            try:
                self.FTP.quit()
            except AttributeError:
                pass
        self.FTP=myFtp()
        self.FTP.set_pasv(True)
        self.connectionNow['hostname']=host
        self.connectionNow['username']=username
        self.connectionNow['passwd']=passwd
        self.connectionNow['port']=port
        self.FTP.connect(host,port)
        self.FTP.login(username,passwd)

        self.serverFileInfo = []
        self.serverPath='/'
        self.serverFileTable.clear()

        self.serverFileRefresh()

    def reconnect(self):
        self.FTP.connect(self.connectionNow['hostname'], self.connectionNow['port'])
        self.FTP.login(self.connectionNow['username'], self.connectionNow['passwd'])


def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cli = client()
    sys.exit(app.exec_())
