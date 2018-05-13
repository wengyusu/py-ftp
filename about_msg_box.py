from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap


class AboutMessage(QMessageBox):

    def __init__(self):
        super(AboutMessage, self).__init__(QMessageBox.NoIcon, 'About PyFTP Server', 'PyFTP Server 0.1 beta\nCopyright(C) 2018\nWritten by: Wangzichen')
        self.setIconPixmap(QPixmap('resource/python.png'))