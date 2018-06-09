from PyQt5.QtWidgets import QWidget, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QButtonGroup, QRadioButton


class GeneralPage(QVBoxLayout):

    pro = 1

    connectionBox = None
    timeoutBox = None

    edit1 = None
    edit2 = None
    edit3 = None

    def __init__(self):
        super(GeneralPage, self).__init__()

        self.initConnectionBox()
        self.initTimeoutBox()

        self.addWidget(self.connectionBox)
        self.addWidget(self.timeoutBox)

    def initConnectionBox(self):
        self.connectionBox = QGroupBox('Connection settings')

        connectBoxLayout = QGridLayout()

        label11 = QLabel('Listen on these ports:')
        self.edit1 = QLineEdit('21')
        label12 = QLabel('List of ports between 1 and 65535.')

        label21 = QLabel('Max connection count:')
        self.edit2 = QLineEdit('0')
        label22 = QLabel('(0 for unlimited connections)')

        connectBoxLayout.addWidget(label11, 0, 0)
        connectBoxLayout.addWidget(self.edit1, 0, 1)
        connectBoxLayout.addWidget(label12, 0, 2)

        connectBoxLayout.addWidget(label21, 1, 0)
        connectBoxLayout.addWidget(self.edit2, 1, 1)
        connectBoxLayout.addWidget(label22, 1, 2)

        self.connectionBox.setLayout(connectBoxLayout)

    def initTimeoutBox(self):
        self.timeoutBox = QGroupBox('Timeout settings')

        timeoutLayout = QHBoxLayout()
        label1 = QLabel('Connection timeout:')
        timeoutLayout.addWidget(label1)
        self.edit3 = QLineEdit('300')
        timeoutLayout.addWidget(self.edit3)
        label2 = QLabel('in seconds(1-9999, 0 for no timeout).')
        timeoutLayout.addWidget(label2)

        self.timeoutBox.setLayout(timeoutLayout)


class FilterPage(QVBoxLayout):

    pro = 2

    labelAllowed = None
    editAllowed = None
    labelBanned = None
    editBanned = None

    def __init__(self):
        super(FilterPage, self).__init__()

        self.initWidget()

        self.addWidget(self.labelAllowed)
        self.addWidget(self.editAllowed)
        self.addWidget(self.labelBanned)
        self.addWidget(self.editBanned)

    def initWidget(self):
        self.labelAllowed = QLabel('The following IP address are allowed to connect to the server:')
        self.editAllowed = QTextEdit()

        self.labelBanned = QLabel('The following IP address are not allowed to connect to the server:')
        self.editBanned = QTextEdit()


class SpeedPage(QVBoxLayout):

    pro = 3

    downloadBox = None
    uploadBox = None

    downloadSpeedWidget = None
    uploadSpeedWidget = None

    noLimitButton1 = None
    limitButton1 = None

    noLimitButton2 = None
    limitButton2 = None

    def __init__(self):
        super(SpeedPage, self).__init__()

        self.initDownloadBox()
        self.initUploadBox()

        self.addWidget(self.downloadBox)
        self.addWidget(self.uploadBox)

    def initDownloadBox(self):
        self.downloadBox = QGroupBox('Download Speed Limit')
        downloadLayout = QVBoxLayout()

        self.noLimitButton1 = QRadioButton('No Limit')
        self.noLimitButton1.setChecked(True)
        self.noLimitButton1.clicked.connect(self.downloadNoLimitTriggered)
        self.limitButton1 = QRadioButton('Constant Speed Limit of')
        self.limitButton1.clicked.connect(self.downloadLimitTriggered)

        downloadGroup = QButtonGroup()
        downloadGroup.addButton(self.noLimitButton1)
        downloadGroup.addButton(self.limitButton1)

        self.downloadSpeedWidget = SpeedWidget()
        self.downloadSpeedWidget.edit.setEnabled(False)

        downloadLayout.addWidget(self.noLimitButton1)
        downloadLayout.addWidget(self.limitButton1)
        downloadLayout.addWidget(self.downloadSpeedWidget)
        self.downloadBox.setLayout(downloadLayout)

    def initUploadBox(self):
        self.uploadBox = QGroupBox('Upload Speed Limit')
        uploadLayout = QVBoxLayout()

        self.noLimitButton2 = QRadioButton('No Limit')
        self.noLimitButton2.setChecked(True)
        self.noLimitButton2.clicked.connect(self.uploadNoLimitTriggered)
        self.limitButton2 = QRadioButton('Constant Speed Limit of')
        self.limitButton2.clicked.connect(self.uploadLimitTriggered)


        uploadGroup = QButtonGroup()
        uploadGroup.addButton(self.noLimitButton2)
        uploadGroup.addButton(self.limitButton2)

        self.uploadSpeedWidget = SpeedWidget()
        self.uploadSpeedWidget.edit.setEnabled(False)

        uploadLayout.addWidget(self.noLimitButton2)
        uploadLayout.addWidget(self.limitButton2)
        uploadLayout.addWidget(self.uploadSpeedWidget)
        self.uploadBox.setLayout(uploadLayout)

    def downloadNoLimitTriggered(self):
        self.downloadSpeedWidget.edit.setEnabled(False)

    def downloadLimitTriggered(self):
        self.downloadSpeedWidget.edit.setEnabled(True)

    def uploadNoLimitTriggered(self):
        self.uploadSpeedWidget.edit.setEnabled(False)

    def uploadLimitTriggered(self):
        self.uploadSpeedWidget.edit.setEnabled(True)


class SpeedWidget(QWidget):

    edit = None
    label = None

    def __init__(self):
        super(SpeedWidget, self).__init__()

        self.edit = QLineEdit('10')
        self.label = QLabel('kB/s')

        self.initLayout()

    def initLayout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.label)

        self.setLayout(layout)
