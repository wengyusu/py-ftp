from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QDialog, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout
from user_pages import UserPage, FirstPage
from PyQt5.QtGui import QPixmap
import json


class UserWindow(QDialog):

    columnLabel = None
    columnTable = None
    userButtons = None
    windowButtons = None

    userButtonBox = None
    windowButtonBox = None

    mainLayout = None
    leftLayout = None
    rightLayout = None
    initLayout = None

    userGeneral = None
    userFolders = None

    userPage = None

    addUserDialog = None

    buttonAdd = None
    buttonRemove = None

    def __init__(self):
        super(UserWindow, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Settings')

        self.userPage = UserPage()
        self.initLayout = FirstPage()

        self.initUi()
        self.initSetting()

    def initUi(self):
        self.initColumnLabel()
        self.initColumnTable()
        self.initUserButtons()
        self.initWindowButtons()

        self.leftLayout = QVBoxLayout()
        self.leftLayout.addStretch()
        self.leftLayout.addWidget(self.columnLabel)
        self.leftLayout.addWidget(self.columnTable)
        self.leftLayout.addWidget(self.userButtonBox)
        self.leftLayout.addWidget(self.windowButtonBox)

        self.rightLayout = self.initLayout

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)

        self.setLayout(self.mainLayout)

    def initColumnLabel(self):
        self.columnLabel = QLabel('Users:')

    def initColumnTable(self):
        self.columnTable = QTableWidget()
        self.columnTable.setColumnCount(1)
        self.columnTable.setRowCount(0)
        self.columnTable.verticalHeader().setHidden(True)
        self.columnTable.horizontalHeader().setHidden(True)
        self.columnTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.columnTable.setSelectionMode(QAbstractItemView.SingleSelection)

        self.columnTable.itemClicked.connect(self.itemClickedTriggered)

    def itemClickedTriggered(self):
        self.mainLayout.removeItem(self.rightLayout)

        self.rightLayout.accountSettingBox.close()
        self.rightLayout.sharedFolderBox.close()

        for index in range(self.columnTable.rowCount()):
            item = self.columnTable.item(index, 0)
            if item.isSelected():
                self.rightLayout = item.page
                break

        self.mainLayout.addLayout(self.rightLayout)
        self.rightLayout.accountSettingBox.show()
        self.rightLayout.sharedFolderBox.show()

    def initUserButtons(self):
        self.userButtonBox = QGroupBox()

        self.buttonAdd = QPushButton('Add')
        self.buttonRemove = QPushButton('Remove')
        self.buttonRemove.setEnabled(False)

        self.buttonAdd.clicked.connect(self.addTriggered)
        self.buttonRemove.clicked.connect(self.removeTriggered)

        subLayout = QHBoxLayout()
        subLayout.addWidget(self.buttonAdd)
        subLayout.addWidget(self.buttonRemove)

        self.userButtonBox.setLayout(subLayout)

    def addTriggered(self):
        self.addUserDialog = addDialog()
        self.addUserDialog.userOKButton.clicked.connect(self.addOKTriggered)
        self.addUserDialog.userCancelButton.clicked.connect(self.addCancelTriggered)
        self.addUserDialog.exec()

        name = self.addUserDialog.userNameEdit

    def addOKTriggered(self):
        name = self.addUserDialog.userNameEdit.text()

        if name == '':
            box1 = QMessageBox()
            box1.setText('Please enter a name.')
            box1.setIconPixmap(QPixmap('resource/fail.png'))
            box1.exec()
            return

        for index in range(self.columnTable.rowCount()):
            item = self.columnTable.item(index, 0)
            if name == item.text():
                box2 = QMessageBox()
                box2.setText('User %s has existed.' % name)
                box2.setIconPixmap(QPixmap('resource/fail.png'))
                box2.exec()
                return

        nameItem = NewTypeItem()
        nameItem.setText(name)
        nameItem.page.sharedFolderEdit.setText('/%s' % name)

        self.columnTable.setRowCount(self.columnTable.rowCount() + 1)
        self.columnTable.setItem(self.columnTable.rowCount() - 1, 0, nameItem)

        self.addUserDialog.close()

        self.buttonRemove.setEnabled(True)

    def addCancelTriggered(self):
        self.addUserDialog.close()

    def removeTriggered(self):
        for index in range(self.columnTable.rowCount()):
            item = self.columnTable.item(index, 0)
            if item.isSelected():
                self.columnTable.removeRow(index)
                if self.columnTable.rowCount() == 0:
                    self.buttonRemove.setEnabled(False)
                    break

        self.mainLayout.removeItem(self.rightLayout)
        self.rightLayout.accountSettingBox.close()
        self.rightLayout.sharedFolderBox.close()

        self.rightLayout = self.initLayout
        self.mainLayout.addLayout(self.rightLayout)
        self.rightLayout.accountSettingBox.show()
        self.rightLayout.sharedFolderBox.show()

    def initWindowButtons(self):
        self.windowButtonBox = QGroupBox()

        buttonOK = QPushButton('OK')
        buttonCancel = QPushButton('Cancel')

        buttonOK.clicked.connect(self.okTriggered)
        buttonCancel.clicked.connect(self.cancelTriggered)

        subLayout = QVBoxLayout()
        subLayout.addWidget(buttonOK)
        subLayout.addWidget(buttonCancel)

        self.windowButtonBox.setLayout(subLayout)

    def okTriggered(self):
        self.updateSetting()
        self.close()

    def cancelTriggered(self):
        self.close()

    def initSetting(self):
        with open('./setting.json', 'r') as load_f:
            load_j = json.load(load_f)

        userList = load_j['Users']
        for user in userList:
            userItem = NewTypeItem()
            userItem.setText(user['Name'])
            userItem.page = UserPage()

            if user['UsePassword']:
                userItem.page.passwordCheckBox.setChecked(True)
            else:
                userItem.page.passwordCheckBox.setChecked(False)

            userItem.page.passwordEdit.setText(user['Password'])
            userItem.page.sharedFolderEdit.setText(user['SharedFolder'])

            self.columnTable.setRowCount(self.columnTable.rowCount() + 1)
            self.columnTable.setItem(self.columnTable.rowCount() - 1, 0, userItem)

        if self.columnTable.rowCount() != 0:
            self.buttonRemove.setEnabled(True)

        pass

    def updateSetting(self):
        with open('./setting.json', 'r+') as lw_f:
            lw_j = json.load(lw_f)
            lw_f.seek(0)
            lw_f.truncate()

            itemJsonList = []
            for index in range(self.columnTable.rowCount()):
                item = self.columnTable.item(index, 0)
                if item.page.passwordCheckBox.isChecked() == True:
                    itemJsonList.append({"Name": item.text(), "UsePassword": 1, "Password": item.page.passwordEdit.text(),
                                         "SharedFolder": item.page.sharedFolderEdit.text()})
                else:
                    itemJsonList.append({"Name": item.text(), "UsePassword": 0, "Password": item.page.passwordEdit.text(),
                                         "SharedFolder": item.page.sharedFolderEdit.text()})
            lw_j['Users'] = itemJsonList
            json.dump(lw_j, lw_f)
        pass

class addDialog(QDialog):

    userNameLabel = None
    userNameEdit = None
    userOKButton = None
    userCancelButton = None

    addDialogLayout = None


    def __init__(self):
        super(addDialog, self).__init__()

        self.initLabel()
        self.initEdit()
        self.initButton()
        self.initLayout()

    def initLabel(self):
        self.userNameLabel = QLabel('Please enter the name of the user account that should be added:')

    def initEdit(self):
        self.userNameEdit = QLineEdit()

    def initButton(self):
        self.userOKButton = QPushButton('OK')
        self.userCancelButton = QPushButton('Cancel')

    def initLayout(self):
        childLayout = QHBoxLayout()
        childLayout.addWidget(self.userOKButton)
        childLayout.addWidget(self.userCancelButton)

        self.addDialogLayout = QVBoxLayout()
        self.addDialogLayout.addWidget(self.userNameLabel)
        self.addDialogLayout.addWidget(self.userNameEdit)
        self.addDialogLayout.addLayout(childLayout)

        self.setLayout(self.addDialogLayout)

class NewTypeItem(QTableWidgetItem):

    page = None

    def __init__(self):
        super(NewTypeItem, self).__init__()
        self.page = UserPage()
