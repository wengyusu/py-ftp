from PyQt5.QtWidgets import QFileDialog, QPushButton, QCheckBox, QLineEdit, QVBoxLayout, QHBoxLayout, QGroupBox


class UserPage(QVBoxLayout):

    accountSettingBox = None
    sharedFolderBox = None

    passwordCheckBox = None
    passwordEdit = None
    sharedFolderEdit = None
    chooseButton = None

    folderPath = None

    def __init__(self):
        super(UserPage, self).__init__()

        self.initAccountSettingBox()
        self.initSharedFolderBox()

        self.addWidget(self.accountSettingBox)
        self.addWidget(self.sharedFolderBox)

    def initAccountSettingBox(self):
        self.accountSettingBox = QGroupBox('Account settings')

        self.passwordCheckBox = QCheckBox('Password:')
        self.passwordCheckBox.setChecked(False)

        self.passwordEdit = QLineEdit()

        accountSettingLayout = QHBoxLayout()
        accountSettingLayout.addWidget(self.passwordCheckBox)
        accountSettingLayout.addWidget(self.passwordEdit)
        self.accountSettingBox.setLayout(accountSettingLayout)

    def initSharedFolderBox(self):
        self.sharedFolderBox = QGroupBox('Shared folder')

        self.sharedFolderEdit = QLineEdit()

        self.chooseButton = QPushButton('Choose...')
        self.chooseButton.clicked.connect(self.chooseButtonClicked)

        sharedFolderLayout = QVBoxLayout()
        sharedFolderLayout.addWidget(self.sharedFolderEdit)
        sharedFolderLayout.addWidget(self.chooseButton)
        self.sharedFolderBox.setLayout(sharedFolderLayout)

    def chooseButtonClicked(self):
        self.folderPath = QFileDialog.getExistingDirectory(self.sharedFolderEdit, 'Choose a folder.')
        self.sharedFolderEdit.setText(self.folderPath)

class FirstPage(UserPage):
    def __init__(self):
        super(FirstPage, self).__init__()
        self.accountSettingBox.setEnabled(False)
        self.sharedFolderBox.setEnabled(False)
