from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget, QDialog, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout
from setting_pages import GeneralPage, FilterPage, SpeedPage
from setting_msg_box import SettingMessage
import json


class SettingWindow(QDialog):

    columnTree = None
    buttonBox = None

    mainLayout = None
    leftLayout = None
    rightLayout = None

    geneSet = None
    ipFilter = None

    genePage = None
    filterPage = None

    def __init__(self):
        super(SettingWindow, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Settings')
        self.setFixedSize(800, 350)

        self.genePage = GeneralPage()
        self.filterPage = FilterPage()
        self.initSetting()
        self.initUi()

    def initUi(self):
        self.initColumnTree()
        self.initButtons()

        self.leftLayout = QVBoxLayout()
        self.leftLayout.addWidget(self.columnTree)
        self.leftLayout.addWidget(self.buttonBox)

        self.rightLayout = self.genePage

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)
        self.mainLayout.setStretchFactor(self.leftLayout, 1)
        self.mainLayout.setStretchFactor(self.rightLayout, 2)

        self.setLayout(self.mainLayout)

    def initColumnTree(self):
        self.columnTree = QTreeWidget()
        self.columnTree.setHeaderHidden(True)
        self.columnTree.setColumnCount(1)

        self.geneSet = QTreeWidgetItem()
        self.geneSet.setText(0, 'General settings')
        self.columnTree.addTopLevelItem(self.geneSet)

        self.ipFilter = QTreeWidgetItem()
        self.ipFilter.setText(0, 'IP Filter')
        self.columnTree.addTopLevelItem(self.ipFilter)

        self.columnTree.itemClicked.connect(self.itemClickedTriggered)

    def itemClickedTriggered(self):
        self.mainLayout.removeItem(self.rightLayout)

        if self.rightLayout.pro == 1:
            self.rightLayout.connectionBox.close()
            self.rightLayout.timeoutBox.close()
        elif self.rightLayout.pro == 2:
            self.rightLayout.labelAllowed.close()
            self.rightLayout.editAllowed.close()
            self.rightLayout.labelBanned.close()
            self.rightLayout.editBanned.close()
        elif self.rightLayout.pro == 3:
            self.rightLayout.downloadBox.close()
            self.rightLayout.uploadBox.close()
            self.rightLayout.downloadSpeedWidget.close()
            self.rightLayout.uploadSpeedWidget.close()
        else:
            pass

        if self.geneSet.isSelected():
            self.rightLayout = self.genePage
            self.rightLayout.connectionBox.show()
            self.rightLayout.timeoutBox.show()
        elif self.ipFilter.isSelected():
            self.rightLayout = self.filterPage
            self.rightLayout.labelAllowed.show()
            self.rightLayout.editAllowed.show()
            self.rightLayout.labelBanned.show()
            self.rightLayout.editBanned.show()
        else:
            pass

        self.mainLayout.addLayout(self.rightLayout)
        self.mainLayout.setStretchFactor(self.leftLayout, 1)
        self.mainLayout.setStretchFactor(self.rightLayout, 2)

    def initButtons(self):
        self.buttonBox = QGroupBox()

        buttonOK = QPushButton('OK')
        buttonCancel = QPushButton('Cancel')

        buttonOK.clicked.connect(self.okTriggered)
        buttonCancel.clicked.connect(self.cancelTriggered)

        subLayout = QVBoxLayout()
        subLayout.addWidget(buttonOK)
        subLayout.addWidget(buttonCancel)

        self.buttonBox.setLayout(subLayout)

    def okTriggered(self):
        self.updateSetting()

        msg = SettingMessage()
        msg.exec()

        self.close()

    def cancelTriggered(self):
        self.close()

    def initSetting(self):
        with open('./setting.json', 'r') as load_f:
            load_j = json.load(load_f)

        self.genePage.edit1.setText(str(load_j['Port']))

        self.genePage.edit2.setText(str(load_j['MaxConnectionCount']))

        allowedList = load_j['IPAllowed']
        for item in allowedList:
            self.filterPage.editAllowed.append(item)

        bannedList = load_j['IPBanned']
        for item in bannedList:
            self.filterPage.editBanned.append(item)


    def updateSetting(self):
        with open('./setting.json', 'r+') as lw_f:
            lw_j = json.load(lw_f)
            lw_f.seek(0)
            lw_f.truncate()

            lw_j['Port'] = int(self.genePage.edit1.text())

            lw_j['MaxConnectionCount'] = int(self.genePage.edit2.text())

            allowedList = self.filterPage.editAllowed.toPlainText().split('\n')
            allowedJsonList = []
            for item in allowedList:
                allowedJsonList.append(item)
            lw_j['IPAllowed'] = allowedJsonList

            bannedList = self.filterPage.editBanned.toPlainText().split('\n')
            bannedJsonList = []
            for item in bannedList:
                bannedJsonList.append(item)
            lw_j['IPBanned'] = bannedJsonList

            json.dump(lw_j, lw_f)